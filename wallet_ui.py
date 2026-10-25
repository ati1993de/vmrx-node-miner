"""Experimental wallet tab for the VMRX Node & Miner Tk desktop controller.

Wallet cryptography is delegated to a locally launched fork-specific Core
wallet-RPC. Never enter real funds before an independently verified recovery.
"""
from __future__ import annotations

import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import webbrowser

from wallet_backend import WalletError, WalletService, find_wallet_binary, ATOMIC_UNITS

URL = "https://randomx.vargamesh.com/"
BG, SURFACE, TEXT, MUTED, CYAN = "#0c1420", "#172332", "#e8f2fa", "#a2b5c6", "#2ed7dc"


def coins(value):
    return f"{int(value) / ATOMIC_UNITS:.12f}".rstrip("0").rstrip(".") or "0"


class WalletPanel(ttk.Frame):
    def __init__(self, parent, mining_address, daemon_port):
        super().__init__(parent)
        self.mining_address = mining_address
        self.daemon_port = daemon_port
        self.service = WalletService()
        self.name = tk.StringVar()
        self.binary = tk.StringVar(value=find_wallet_binary())
        self.wallet_dir = tk.StringVar(value=str(__import__("pathlib").Path.home() / ".vmrx-node" / "wallets"))
        self.active = False
        self.address = tk.StringVar(value="No wallet open")
        self.balance = tk.StringVar(value="—")
        self.height = tk.StringVar(value="—")
        self.status = tk.StringVar(value="Experimental wallet: verify deterministic recovery before depositing.")
        self.to_address = tk.StringVar()
        self.to_amount = tk.StringVar()
        self.allow_send = tk.BooleanVar(value=False)
        self.results = queue.Queue()
        self.busy = False
        self._build()
        self.after(120, self._drain)

    def _build(self):
        canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        body = tk.Frame(canvas, bg=BG)
        canvas.create_window((0, 0), window=body, anchor="nw", tags="content")
        body.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure("content", width=e.width))

        tk.Label(body, text="VMRX Wallet · experimental", font=("Segoe UI", 16, "bold"),
                 fg=TEXT, bg=BG).pack(anchor="w", padx=16, pady=(12, 3))
        tk.Label(body, text="On-device encrypted wallet files · native VMRX Core wallet-RPC only · never enter a seed on a website",
                 fg=MUTED, bg=BG, wraplength=820, justify="left").pack(anchor="w", padx=16)
        top = tk.Frame(body, bg=BG)
        top.pack(fill="x", padx=16, pady=10)
        tk.Label(top, text="Wallet engine", fg=CYAN, bg=BG, font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, sticky="w")
        ttk.Entry(top, textvariable=self.binary).grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=4)
        ttk.Button(top, text="Browse", command=lambda: self._choose_file()).grid(row=1, column=1)
        ttk.Button(top, text="Start engine", command=self.start_engine).grid(row=1, column=2, padx=6)
        ttk.Button(top, text="Stop", command=self.stop_engine).grid(row=1, column=3)
        tk.Label(top, text="Wallet storage", fg=MUTED, bg=BG).grid(row=2, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(top, textvariable=self.wallet_dir).grid(row=3, column=0, sticky="ew", pady=4, padx=(0, 6))
        ttk.Button(top, text="Folder", command=self._choose_folder).grid(row=3, column=1)
        top.columnconfigure(0, weight=1)

        actions = tk.Frame(body, bg=BG)
        actions.pack(fill="x", padx=16, pady=6)
        for label, command in (
            ("New wallet", self.create_wallet),
            ("Restore seed", self.restore_wallet),
            ("Open wallet", self.open_wallet),
            ("Close wallet", self.close_wallet),
            ("Show recovery seed", self.show_seed),
            ("Backup files", self.backup_wallet),
        ):
            ttk.Button(actions, text=label, command=command).pack(side="left", padx=(0, 6), pady=3)

        summary = tk.Frame(body, bg=SURFACE, padx=14, pady=12)
        summary.pack(fill="x", padx=16, pady=7)
        tk.Label(summary, text="RECEIVE ADDRESS", bg=SURFACE, fg=CYAN).pack(anchor="w")
        tk.Label(summary, textvariable=self.address, bg=SURFACE, fg=TEXT, justify="left",
                 wraplength=775, font=("Consolas", 10)).pack(anchor="w", pady=6)
        tk.Label(summary, text="Balance / unlocked (VMRX)", bg=SURFACE, fg=MUTED).pack(anchor="w")
        tk.Label(summary, textvariable=self.balance, bg=SURFACE, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=3)
        row = tk.Frame(summary, bg=SURFACE)
        row.pack(anchor="w")
        ttk.Button(row, text="Refresh balance", command=self.refresh).pack(side="left")
        ttk.Button(row, text="Use address for CPU mining", command=self.use_for_mining).pack(side="left", padx=8)
        tk.Label(summary, textvariable=self.height, fg=MUTED, bg=SURFACE).pack(anchor="w", pady=(7, 0))

        send = tk.LabelFrame(body, text="Send VMRX (unsafe until recovery tests pass)",
                             fg=CYAN, bg=BG, padx=14, pady=8)
        send.pack(fill="x", padx=16, pady=7)
        tk.Label(send, text="Destination", bg=BG, fg=MUTED).grid(row=0, column=0, sticky="w")
        ttk.Entry(send, textvariable=self.to_address).grid(row=0, column=1, sticky="ew", padx=8, pady=4)
        tk.Label(send, text="Amount (VMRX)", bg=BG, fg=MUTED).grid(row=1, column=0, sticky="w")
        ttk.Entry(send, textvariable=self.to_amount, width=19).grid(row=1, column=1, sticky="w", padx=8, pady=4)
        ttk.Checkbutton(send, text="I independently tested seed restoration, understand the risks, and accept an EXPERIMENTAL send",
                        variable=self.allow_send).grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Button(send, text="Prepare, inspect fee and confirm broadcast", command=self.send).grid(
            row=3, column=1, sticky="w", padx=8)
        send.columnconfigure(1, weight=1)

        tk.Label(body, text="Recent transfers (last 15; received, sent, pending)", bg=BG,
                 fg=CYAN, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=16, pady=(9, 3))
        self.history = tk.Text(body, bg=SURFACE, fg=TEXT, font=("Consolas", 9),
                               height=5, wrap="word", relief="flat")
        self.history.pack(fill="x", padx=16, pady=(0, 7))
        self.history.insert("1.0", "Open and refresh a wallet to show transfers.")
        self.history.configure(state="disabled")

        foot = tk.Frame(body, bg=BG)
        foot.pack(fill="x", padx=16, pady=7)
        ttk.Button(foot, text="VMRX website & full instructions", command=lambda: webbrowser.open_new_tab(URL)).pack(side="left")
        ttk.Button(foot, text="Wallet safety guide", command=self.guide).pack(side="left", padx=8)
        tk.Label(body, textvariable=self.status, bg=BG, fg=MUTED,
                 justify="left", wraplength=790).pack(anchor="w", padx=16, pady=8)

    def _choose_file(self):
        path = filedialog.askopenfilename(title="VMRX Core wallet-RPC executable")
        if path:
            self.binary.set(path)

    def _choose_folder(self):
        path = filedialog.askdirectory(title="Local VMRX wallet directory")
        if path:
            self.wallet_dir.set(path)

    def _job(self, name, fn):
        if self.busy:
            messagebox.showwarning("VMRX Wallet", "Please complete the current wallet operation first.")
            return
        self.busy = True
        self.status.set(f"{name} …")
        def run():
            try:
                self.results.put((name, True, fn()))
            except Exception as exc:
                # Backend sanitizes sensitive data. No logging or tracebacks.
                self.results.put((name, False, str(exc) if isinstance(exc, WalletError) else "Wallet operation failed. Check the Core logs locally."))
        threading.Thread(target=run, daemon=True).start()

    def _drain(self):
        try:
            while True:
                name, ok, data = self.results.get_nowait()
                self.busy = False
                if not ok:
                    self.status.set(f"{name}: {data}")
                    messagebox.showerror("VMRX Wallet", str(data))
                    continue
                if name == "start":
                    self.status.set(f"Wallet engine PID {data} started; open or create a wallet.")
                elif name in ("create", "restore", "open"):
                    self.active = True
                    self.address.set(data["address"])
                    self.status.set(f"Wallet {self.name.get()} opened. Back up and verify its seed OFFLINE.")
                    self.refresh()
                    if name == "create":
                        messagebox.showwarning("Back up your recovery seed",
                            "Before receiving coins, choose 'Show recovery seed', save it OFFLINE, "
                            "then restore into a separate temporary wallet and verify the same address. "
                            "A known founder-wallet recovery discrepancy is still unresolved.")
                elif name == "close":
                    self._clear_wallet()
                    self.status.set("Wallet closed and saved.")
                elif name == "stop":
                    self._clear_wallet()
                    self.status.set("Wallet engine stopped.")
                elif name == "refresh":
                    self.address.set(data["address"])
                    self.balance.set(f"{coins(data['balance'].get('balance', 0))}  /  {coins(data['balance'].get('unlocked_balance', 0))}")
                    self.height.set(f"Wallet scan height: {data['height'].get('height', '—')}")
                    self._update_history(data["transactions"])
                    self.status.set("Wallet information refreshed from local Core.")
                elif name == "seed":
                    self._seed_window(data)
                elif name == "backup":
                    messagebox.showinfo("VMRX Wallet", f"Wallet + encrypted keys copied and checked:\n{data}\n\nKeep this backup OFFLINE.")
                    self.status.set("Wallet files backed up and hashes verified.")
                elif name == "prepare":
                    amount = coins(data["amount"])
                    fee = coins(data["fee"])
                    recipient = data["recipient"]
                    choice = messagebox.askyesno("FINAL BROADCAST CONFIRMATION",
                        f"Experimental VMRX transaction\n\nAmount: {amount} VMRX\n"
                        f"Network fee: {fee} VMRX\n\nDestination:\n{recipient}\n\n"
                        "The broadcast is irreversible. Is your backup and seed recovery VERIFIED?\n\nBroadcast now?")
                    if choice:
                        metadata = data["metadata"]
                        self._job("relay", lambda: self.service.running_client().relay(metadata))
                    else:
                        self.status.set("Transaction prepared locally but NOT broadcast.")
                elif name == "relay":
                    self.status.set(f"Transaction relayed: {str(data.get('tx_hash', ''))[:64]}")
                    messagebox.showinfo("VMRX Wallet", self.status.get())
                    self.refresh()
        except queue.Empty:
            pass
        self.after(120, self._drain)

    def _clear_wallet(self):
        self.active = False
        self.address.set("No wallet open")
        self.balance.set("—")
        self.height.set("—")
        self.allow_send.set(False)
        self.to_address.set("")
        self.to_amount.set("")
        self._update_history({})

    def _update_history(self, transfers):
        rows = []
        for kind in ("in", "out", "pending", "pool", "failed"):
            for tx in (transfers.get(kind) or []):
                rows.append(f"{kind.upper():7} {coins(tx.get('amount', 0))} VMRX   height {tx.get('height', '?')}\n{tx.get('txid', tx.get('tx_hash', '?'))}")
        self.history.configure(state="normal")
        self.history.delete("1.0", "end")
        self.history.insert("1.0", "\n".join(rows[-15:]) or "No transfers found.")
        self.history.configure(state="disabled")

    def _require(self):
        if not self.active:
            raise WalletError("Open a wallet first")
        return self.service.running_client()

    def start_engine(self):
        binary, directory = self.binary.get(), self.wallet_dir.get()
        try:
            daemon = int(self.daemon_port.get())
        except ValueError:
            messagebox.showerror("VMRX Wallet", "Invalid daemon RPC port")
            return
        self._job("start", lambda: self.service.start(binary, directory, daemon))

    def stop_engine(self):
        if not messagebox.askyesno("VMRX Wallet", "Save/close the open wallet and stop the wallet engine?"):
            return
        self._job("stop", lambda: (self.service.stop(), True)[1])

    def _password(self, confirm=False):
        pw = simpledialog.askstring("VMRX encrypted wallet", "Wallet password (12+ characters recommended):", show="*", parent=self)
        if pw is None:
            return None
        if not pw or (confirm and len(pw) < 12):
            messagebox.showerror("VMRX", "Use a non-empty password (12+ characters when creating).")
            return None
        if confirm and simpledialog.askstring("Confirm password", "Repeat wallet password:", show="*", parent=self) != pw:
            messagebox.showerror("VMRX", "Passwords do not match")
            return None
        return pw

    def _wallet_filename(self):
        name = simpledialog.askstring("VMRX Wallet", "Wallet file name (letters, digits, _ and - only):", parent=self)
        return name.strip() if name else None

    def create_wallet(self):
        name = self._wallet_filename()
        if not name:
            return
        pw = self._password(True)
        if pw is None:
            return
        self.name.set(name)
        self._job("create", lambda: {"address": self.service.running_client().create(name, pw)})

    def open_wallet(self):
        name = self._wallet_filename()
        if not name:
            return
        pw = self._password()
        if pw is None:
            return
        self.name.set(name)
        self._job("open", lambda: {"address": self.service.running_client().open(name, pw)})

    def restore_wallet(self):
        name = self._wallet_filename()
        if not name:
            return
        pw = self._password(True)
        if pw is None:
            return
        popup = tk.Toplevel(self)
        popup.title("Restore VMRX recovery seed · offline only")
        popup.geometry("650x360")
        popup.configure(bg=BG)
        popup.transient(self.winfo_toplevel())
        popup.grab_set()
        tk.Label(popup, text="Enter your 24/25-word seed locally. Never paste into websites or chats.",
                 bg=BG, fg=TEXT, wraplength=600).pack(padx=14, pady=9)
        seed_box = tk.Text(popup, width=65, height=4, wrap="word")
        seed_box.pack(padx=14, fill="x")
        tk.Label(popup, text="Optional: expected original receiving address (strongly recommended)",
                 bg=BG, fg=MUTED).pack(anchor="w", padx=14, pady=(9, 0))
        expected = ttk.Entry(popup)
        expected.pack(padx=14, fill="x")
        tk.Label(popup, text="Restore height (0 = rescan from genesis)", bg=BG, fg=MUTED).pack(anchor="w", padx=14, pady=6)
        height = ttk.Entry(popup)
        height.insert(0, "0")
        height.pack(anchor="w", padx=14)
        def submit():
            seed = seed_box.get("1.0", "end").strip()
            want = expected.get().strip()
            try:
                block = int(height.get())
            except ValueError:
                messagebox.showerror("VMRX", "Invalid restore height", parent=popup)
                return
            seed_box.delete("1.0", "end")
            popup.destroy()
            self.name.set(name)
            def job():
                address = self.service.running_client().restore(name, pw, seed, block)
                if want and address != want:
                    # Do not trust a restored wallet when it does not match the original.
                    raise WalletError(f"RECOVERY MISMATCH. Expected {want}; restored {address}. Do not deposit or spend.")
                return {"address": address}
            self._job("restore", job)
        ttk.Button(popup, text="Restore into new wallet file", command=submit).pack(pady=12)

    def close_wallet(self):
        self._job("close", lambda: self._require().close())

    def refresh(self):
        def job():
            client = self._require()
            client.refresh()
            return {"address": client.address(), "balance": client.balance(),
                    "height": client.call("get_height"), "transactions": client.transactions()}
        self._job("refresh", job)

    def show_seed(self):
        if not messagebox.askyesno("PRIVATE SEED", "Show your secret seed on this screen?\n"
                                   "Make sure nobody can see or record it. NEVER upload it."):
            return
        self._job("seed", lambda: self._require().seed())

    def _seed_window(self, seed):
        popup = tk.Toplevel(self)
        popup.title("PRIVATE VMRX recovery seed — never share")
        popup.geometry("650x290")
        popup.configure(bg=BG)
        popup.transient(self.winfo_toplevel())
        popup.grab_set()
        tk.Label(popup, text="Write this down OFFLINE. Check every word and its order. Never photograph, send or upload.",
                 fg=TEXT, bg=BG, wraplength=610).pack(padx=15, pady=15)
        field = tk.Text(popup, wrap="word", height=5)
        field.insert("1.0", seed)
        field.configure(state="disabled")
        field.pack(fill="x", padx=15)
        def close():
            field.configure(state="normal")
            field.delete("1.0", "end")
            popup.destroy()
        ttk.Button(popup, text="I saved my seed offline — hide it", command=close).pack(pady=15)
        popup.protocol("WM_DELETE_WINDOW", close)

    def backup_wallet(self):
        if not self.active:
            messagebox.showerror("VMRX", "Open a wallet first")
            return
        folder = filedialog.askdirectory(title="Choose a DIFFERENT empty directory for encrypted wallet backup")
        if folder:
            self._job("backup", lambda: self.service.backup(self.name.get(), folder))

    def use_for_mining(self):
        if not self.active:
            messagebox.showerror("VMRX", "Open a wallet first")
            return
        if messagebox.askyesno("VMRX", "Use this wallet receiving address for CPU mining?\n"
                              "Only mine once you have verified deterministic seed recovery."):
            self.mining_address.set(self.address.get())
            self.status.set("Wallet receiving address copied to CPU Mining tab.")

    def send(self):
        if not self.active or not self.allow_send.get():
            messagebox.showerror("VMRX", "Open a wallet and explicitly accept the experimental-send risk first.")
            return
        recipient, amount = self.to_address.get().strip(), self.to_amount.get().strip()
        if not messagebox.askyesno("Experimental VMRX send", "Seed recovery and real spending are not independently verified. "
                                   "Do NOT use significant funds. Prepare an unsigned-to-network transaction locally?"):
            return
        self._job("prepare", lambda: self._require().prepare_transfer(recipient, amount))

    def guide(self):
        messagebox.showinfo("VMRX Wallet · quick instructions",
            "1. Start/sync the real VMRX node first, with verified P2P peers.\n"
            "2. Select the VMRX Core wallet-RPC binary, then Start engine.\n"
            "3. Create a wallet with a strong password, or restore a seed.\n"
            "4. Write down the seed OFFLINE; back up encrypted wallet + .keys files.\n"
            "5. Restore from seed into a NEW filename with genesis scan (height 0).\n"
            "6. Confirm that the restored address is IDENTICAL before receiving/mining.\n"
            "7. Refresh balances. Broadcasting is EXPERIMENTAL and irreversible.\n\n"
            "VMRX is a different chain from VMESH and Monero.\n"
            "Never upload seeds or wallet files. Documentation: " + URL)

    def shutdown(self):
        if self.service.child and self.service.child.poll() is None:
            self.service.stop()
