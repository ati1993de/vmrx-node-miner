"""VMRX Node & Miner v0.1.2-dev — local-only desktop controller.

Requires only Python 3.12 + Tkinter at runtime. No seed phrase or wallet keys.
"""
from __future__ import annotations

import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from node_process import find_bundled_daemon, launch_node
from rpc_client import RpcError, VMRXRpc, valid_mining_address

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
BG, SURFACE, SURFACE2 = "#0c1420", "#172332", "#1d2d3d"
TEXT, MUTED, CYAN, GREEN, AMBER = "#e8f2fa", "#a2b5c6", "#2ed7dc", "#63dab5", "#ffcb79"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VMRX · Node & Miner v0.1.2-dev")
        self.geometry("920x680")
        self.minsize(820, 590)
        self.configure(bg=BG)
        self.work_queue: queue.Queue = queue.Queue()
        self.child: subprocess.Popen | None = None
        self.poll_pending = False
        self.rpc_port = tk.StringVar(value="29781")
        self.p2p_port = tk.StringVar(value="29780")
        self.peer = tk.StringVar(value="31.70.81.5:29780")
        self.node_exe = tk.StringVar(value=find_bundled_daemon())
        self.node_dir = tk.StringVar(value=str(Path.home() / ".vmrx-node"))
        self.address = tk.StringVar(value="")
        self.threads = tk.IntVar(value=1)
        self.background_mining = tk.BooleanVar(value=False)
        self.fields = {key: tk.StringVar(value="—") for key in
                       ("height", "difficulty", "peers", "sync", "mining", "speed", "hash", "node")}
        self.status = tk.StringVar(value="Waiting for a local VMRX node · use Node Control to select the daemon")
        self._style()
        self._build()
        self.after(150, self._drain)
        self.after(300, self._refresh_tick)
        self.protocol("WM_DELETE_WINDOW", self._close)

    def _style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TNotebook", background=BG, borderwidth=0)
        s.configure("TNotebook.Tab", background=SURFACE, foreground=MUTED,
                    padding=(24, 11), font=("Segoe UI", 10, "bold"))
        s.map("TNotebook.Tab", background=[("selected", SURFACE2)], foreground=[("selected", CYAN)])
        s.configure("TFrame", background=BG)
        s.configure("Surface.TFrame", background=SURFACE)
        s.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        s.configure("Muted.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 10))
        s.configure("Header.TLabel", background=BG, foreground=TEXT, font=("Segoe UI Semibold", 22))
        s.configure("Subheader.TLabel", background=BG, foreground=CYAN, font=("Segoe UI", 11, "bold"))
        s.configure("TEntry", padding=6, foreground="#102232", fieldbackground="#eef7fb")
        s.configure("TButton", padding=(14, 9), font=("Segoe UI", 10))
        s.configure("TCheckbutton", background=BG, foreground=TEXT)
        s.map("TCheckbutton", foreground=[("disabled", MUTED)])

    def _build(self):
        bar = tk.Frame(self, bg=BG)
        bar.pack(fill="x", padx=28, pady=(21, 15))
        try:
            self.app_icon = tk.PhotoImage(file=str(ROOT / "assets" / "vmrx-logo.png"))
            self.brand_icon = self.app_icon.subsample(
                max(1, (self.app_icon.width() + 51) // 52),
                max(1, (self.app_icon.height() + 51) // 52),
            )
            tk.Label(bar, image=self.brand_icon, bg=BG).pack(side="left", padx=(0, 14))
            self.iconphoto(True, self.app_icon)
        except tk.TclError:
            tk.Label(bar, text="◆", fg=CYAN, bg=BG, font=("Segoe UI", 30, "bold")).pack(side="left", padx=(0, 14))
        titles = tk.Frame(bar, bg=BG)
        titles.pack(side="left")
        tk.Label(titles, text="VMRX", fg=TEXT, bg=BG, font=("Segoe UI", 23, "bold")).pack(anchor="w")
        tk.Label(titles, text="VARGAMESH RX  /  RANDOMX MAINNET", fg=CYAN, bg=BG,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(bar, text="v0.1.2-dev  •  LOCAL RPC", bg=SURFACE, fg=CYAN,
                 font=("Segoe UI", 9, "bold"), padx=13, pady=8).pack(side="right")
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=24)
        dashboard = ttk.Frame(self.tabs)
        mining = ttk.Frame(self.tabs)
        node = ttk.Frame(self.tabs)
        about = ttk.Frame(self.tabs)
        self.tabs.add(dashboard, text="Dashboard")
        self.tabs.add(mining, text="CPU Mining")
        self.tabs.add(node, text="Node Control")
        self.tabs.add(about, text="About & Safety")
        self._dashboard(dashboard)
        self._mining(mining)
        self._node(node)
        self._about(about)
        bottom = tk.Frame(self, bg=BG)
        bottom.pack(fill="x", padx=30, pady=12)
        tk.Label(bottom, textvariable=self.status, bg=BG, fg=MUTED,
                 wraplength=700, anchor="w", justify="left",
                 font=("Segoe UI", 9)).pack(side="left", fill="x", expand=True)
        ttk.Button(bottom, text="Refresh now", command=self.refresh).pack(side="right")

    def _heading(self, parent, title, text):
        tk.Label(parent, text=title, bg=BG, fg=TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=14, pady=(23, 5))
        tk.Label(parent, text=text, bg=BG, fg=MUTED,
                 font=("Segoe UI", 10), wraplength=760, justify="left").pack(anchor="w", padx=14)

    def _card(self, parent, title, variable, color=TEXT):
        frame = tk.Frame(parent, bg=SURFACE, padx=20, pady=18)
        tk.Label(frame, text=title.upper(), bg=SURFACE, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(frame, textvariable=variable, bg=SURFACE, fg=color,
                 font=("Segoe UI", 21, "bold"), wraplength=310).pack(anchor="w", pady=(9, 0))
        return frame

    def _dashboard(self, frame):
        self._heading(frame, "Network overview", "Local VMRX daemon status · Offline? Open Node Control to choose and start the real VMRX Core binary.")
        cards = tk.Frame(frame, bg=BG)
        cards.pack(fill="both", expand=False, padx=14, pady=22)
        for i, (label, value, color) in enumerate([
            ("Blockchain height", self.fields["height"], TEXT),
            ("Peer connections", self.fields["peers"], CYAN),
            ("Network difficulty", self.fields["difficulty"], TEXT),
            ("Synchronization", self.fields["sync"], GREEN),
            ("RandomX mining", self.fields["mining"], TEXT),
            ("Current hashrate", self.fields["speed"], CYAN),
        ]):
            card = self._card(cards, label, value, color)
            card.grid(row=i // 3, column=i % 3, sticky="nsew", padx=7, pady=7)
        for c in range(3):
            cards.grid_columnconfigure(c, weight=1)
        tk.Label(frame, text="CHAIN TIP", fg=MUTED, bg=BG,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=23)
        tk.Label(frame, textvariable=self.fields["hash"], fg=CYAN, bg=BG,
                 font=("Consolas", 10), wraplength=760).pack(anchor="w", padx=23, pady=8)

    def _field(self, parent, row, text, variable, browse=None):
        tk.Label(parent, text=text, bg=BG, fg=MUTED, font=("Segoe UI", 10)).grid(
            row=row, column=0, sticky="w", pady=10)
        entry = ttk.Entry(parent, textvariable=variable, width=60)
        entry.grid(row=row, column=1, sticky="ew", padx=(16, 8), pady=10)
        if browse is not None:
            ttk.Button(parent, text="Browse", command=browse).grid(row=row, column=2, padx=5)
        parent.columnconfigure(1, weight=1)

    def _mining(self, frame):
        self._heading(frame, "CPU mining", "Start or stop RandomX mining on an already-synchronized local VMRX daemon. Never mine to an unknown address.")
        form = tk.Frame(frame, bg=BG)
        form.pack(fill="x", padx=18, pady=22)
        self._field(form, 0, "VMRX mining address", self.address)
        tk.Label(form, text="CPU threads", bg=BG, fg=MUTED).grid(row=1, column=0, sticky="w", pady=12)
        spin = ttk.Spinbox(form, from_=1, to=min(os.cpu_count() or 1, 64), width=8, textvariable=self.threads)
        spin.grid(row=1, column=1, sticky="w", padx=16, pady=10)
        ttk.Checkbutton(form, text="Use daemon background mining mode", variable=self.background_mining).grid(
            row=2, column=1, sticky="w", padx=16, pady=10)
        buttons = tk.Frame(frame, bg=BG)
        buttons.pack(anchor="w", padx=18)
        ttk.Button(buttons, text="▶ Start mining", command=self.start_mining).pack(side="left", padx=(0, 12))
        ttk.Button(buttons, text="■ Stop mining", command=self.stop_mining).pack(side="left")
        tk.Label(frame, text="Mining runs in the daemon, not the GUI. Stopping affects all mining on the attached daemon.\n"
                 "The node may return BUSY until it is synchronized. CPU load and power use can be significant.",
                 bg=BG, fg=AMBER, justify="left", wraplength=760).pack(anchor="w", padx=18, pady=24)

    def _node(self, frame):
        self._heading(frame, "Local node", "Connect to a local VMRX daemon. A packaged Core is detected automatically, if present; otherwise choose an executable.")
        form = tk.Frame(frame, bg=BG)
        form.pack(fill="x", padx=18, pady=(14, 6))
        self._field(form, 0, "RPC port (localhost)", self.rpc_port)
        self._field(form, 1, "Daemon binary", self.node_exe,
                    browse=lambda: self._browse_file(self.node_exe))
        self._field(form, 2, "Blockchain data directory", self.node_dir,
                    browse=lambda: self._browse_dir(self.node_dir))
        self._field(form, 3, "P2P port (localhost)", self.p2p_port)
        self._field(form, 4, "Verified VMRX peer (optional)", self.peer)
        actions = tk.Frame(frame, bg=BG)
        actions.pack(anchor="w", padx=18, pady=14)
        ttk.Button(actions, text="▶ Start local node", command=self.start_node).pack(side="left", padx=(0, 12))
        ttk.Button(actions, text="■ Stop node I launched", command=self.stop_node).pack(side="left")
        tk.Label(frame, text="VMRX mainnet preferred peers: 31.70.81.5:29780 and 217.154.93.20:29780 (availability not guaranteed).\n"
                 "A filled peer uses non-exclusive priority connections and VMRX-only discovery.\nLeave empty for isolation. Local RPC/P2P bind to localhost; no Monero seeds.",
                 bg=BG, fg=AMBER, justify="left", wraplength=800).pack(anchor="w", padx=18, pady=(10, 0))

    def _about(self, frame):
        self._heading(frame, "About VMRX", "VargaMesh RX is a separate Monero-derived RandomX blockchain, NOT the SHA-256d VMESH mainnet.")
        body = (
            "VMRX mainnet — observed parameters (operator logs, 2026-10-24)\n\n"
            "Consensus: RandomX / HF16  •  target: 120 seconds\n"
            "Mainnet P2P: 29780  •  mainnet RPC: 29781 (localhost only)\n"
            "Genesis: 405baab8805904ffb7d3643a5004c43b45fc3f5f4c97e712ba4c078a384139d4\n"
            "Founder allocation: 200,000 VMRX in block 1 (PREMINE; mandatory disclosure)\n"
            "Tail emission: 0.6 VMRX per target block; NO strict supply cap\n\n"
            "This software is NOT independently audited and is not a wallet or exchange integration.\n"
            "Actual spend and recovery tests, public source/build checks, seed infrastructure, and licensing\n"
            "review are outstanding. Do not disclose wallet seeds, passwords or key files.\n\n"
            "The GUI only controls local daemon RPC; it does not manage private keys or payments."
        )
        tk.Label(frame, text=body, justify="left", anchor="nw", bg=SURFACE, fg=TEXT,
                 padx=20, pady=20, wraplength=800, font=("Consolas", 10)).pack(fill="both", expand=True, padx=14, pady=18)

    def _browse_file(self, var):
        value = filedialog.askopenfilename(title="Choose VMRX daemon (vmrxd/monerod)")
        if value:
            var.set(value)

    def _browse_dir(self, var):
        value = filedialog.askdirectory(title="Choose VMRX blockchain data directory")
        if value:
            var.set(value)

    def _task(self, name, func):
        def wrapped():
            try:
                self.work_queue.put((name, True, func()))
            except Exception as exc:
                self.work_queue.put((name, False, str(exc)))
        threading.Thread(target=wrapped, daemon=True).start()

    def _refresh_tick(self):
        self.refresh()
        self.after(5000, self._refresh_tick)

    def refresh(self):
        if self.poll_pending:
            return
        try:
            port = int(self.rpc_port.get())
            client = VMRXRpc(port)
        except ValueError as exc:
            self.status.set(f"Invalid RPC port: {exc}")
            return
        self.poll_pending = True
        def read():
            info = client.info()
            try:
                mining = client.mining_status()
            except RpcError:
                mining = {}
            return info, mining
        self._task("poll", read)

    def _drain(self):
        try:
            while True:
                task, ok, data = self.work_queue.get_nowait()
                if task == "poll":
                    self.poll_pending = False
                    if ok:
                        info, mining = data
                        self.fields["height"].set(str(info.get("height", "—")))
                        self.fields["peers"].set(str(info.get("incoming_connections_count", 0) + info.get("outgoing_connections_count", 0)))
                        self.fields["difficulty"].set(str(info.get("difficulty", "—")))
                        self.fields["sync"].set("Synchronized" if info.get("synchronized") else "Syncing / isolated")
                        self.fields["mining"].set("Active" if mining.get("active") else "Inactive")
                        self.fields["speed"].set(f"{mining.get('speed', 0)} H/s")
                        self.fields["hash"].set(str(info.get("top_block_hash", "—")))
                        self.status.set("Connected to local VMRX daemon · 127.0.0.1")
                    else:
                        self.fields["height"].set("Offline")
                        self.fields["peers"].set("—")
                        self.fields["difficulty"].set("—")
                        self.fields["sync"].set("No local daemon")
                        self.fields["mining"].set("—")
                        self.fields["speed"].set("—")
                        self.fields["hash"].set("—")
                        self.status.set("No VMRX node listening on 127.0.0.1:" + self.rpc_port.get() +
                                        " · Open Node Control, select your VMRX Core binary, and start the node.")
                else:
                    if ok:
                        self.status.set(str(data))
                        messagebox.showinfo("VMRX", str(data))
                        self.refresh()
                    else:
                        self.status.set("Error: " + str(data)[:110])
                        messagebox.showerror("VMRX", str(data))
        except queue.Empty:
            pass
        self.after(150, self._drain)

    def start_mining(self):
        address = self.address.get().strip()
        if not valid_mining_address(address):
            messagebox.showerror("VMRX", "Invalid VMRX address format. Verify the full receiving address.")
            return
        try:
            threads = int(self.threads.get())
            port = int(self.rpc_port.get())
            if not (1 <= threads <= min(os.cpu_count() or 1, 64)):
                raise ValueError("Invalid CPU thread count")
        except ValueError as e:
            messagebox.showerror("VMRX", str(e))
            return
        if not messagebox.askyesno("Start CPU mining?", f"Mine to the entered VMRX address with {threads} thread(s)?\n"
                                   "CPU/power use can increase significantly. Confirm the address first."):
            return
        background = bool(self.background_mining.get())
        def job():
            rpc = VMRXRpc(port)
            info = rpc.info()
            if not info.get("synchronized"):
                raise RpcError("Daemon is not synchronized; mining would return BUSY")
            rpc.start_mining(address, threads, background)
            return "CPU mining started successfully"
        self._task("action", job)

    def stop_mining(self):
        if not messagebox.askyesno("Stop daemon mining?", "Stop CPU mining on the connected VMRX daemon?\nThis affects any miner on that daemon."):
            return
        try:
            port = int(self.rpc_port.get())
        except ValueError:
            return
        self._task("action", lambda: (VMRXRpc(port).stop_mining(), "CPU mining stopped")[1])

    def start_node(self):
        if self.child and self.child.poll() is None:
            messagebox.showinfo("VMRX", "GUI-launched daemon is already running")
            return
        try:
            rpc_port, p2p_port = int(self.rpc_port.get()), int(self.p2p_port.get())
            # This app never launches remote-access RPC.
            self.child = launch_node(self.node_exe.get(), self.node_dir.get(),
                                     rpc_port, p2p_port, self.peer.get())
            self.status.set(f"VMRX local node launched (PID {self.child.pid})")
            messagebox.showinfo("VMRX", "VMRX daemon started locally. Check Dashboard for sync status.")
        except Exception as e:
            messagebox.showerror("VMRX", f"Node was not started: {e}")

    def stop_node(self):
        if not self.child or self.child.poll() is not None:
            messagebox.showinfo("VMRX", "No GUI-owned node is running. Existing services are never stopped.")
            return
        if not messagebox.askyesno("Stop VMRX node?", "Stop only the daemon process launched by this GUI?"):
            return
        child = self.child
        self._task("action", lambda: self._terminate_owned(child))

    @staticmethod
    def _terminate_owned(child: subprocess.Popen) -> str:
        child.terminate()
        try:
            child.wait(timeout=12)
            return "GUI-owned VMRX daemon stopped"
        except subprocess.TimeoutExpired:
            return "Daemon did not stop within 12 seconds. Inspect logs; no forced kill was performed."

    def _close(self):
        if self.child and self.child.poll() is None:
            messagebox.showwarning("VMRX", "Stop the node you launched before closing the GUI.")
            return
        self.destroy()


if __name__ == "__main__":
    App().mainloop()
