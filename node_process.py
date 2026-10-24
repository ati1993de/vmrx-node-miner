"""Launch only an explicitly selected local VMRX daemon binary.

By default, the node stays isolated and cannot discover unrelated Monero peers.
"""
from __future__ import annotations

import ipaddress
import os
from pathlib import Path
import re
import subprocess
import sys

PEER_RE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9.-]*):(\d{1,5})$")


def find_bundled_daemon() -> str:
    """Return only a daemon located beside this app in the expected release layout.

    No network fetches, no executable search via PATH and no automatic process
    startup. The user must explicitly click Start local node.
    """
    root = (Path(sys.executable).resolve().parent if getattr(sys, "frozen", False)
            else Path(__file__).resolve().parent)
    candidates = (
        root / "core" / "monerod.exe",
        root / "core" / "vmrxd.exe",
        root / "core" / "monerod",
        root / "core" / "vmrxd",
    )
    for candidate in candidates:
        if candidate.is_file() and (os.name == "nt" or os.access(candidate, os.X_OK)):
            return str(candidate)
    return ""


def checked_peer(peer: str) -> str:
    peer = peer.strip()
    if not peer:
        return "127.0.0.1:1"  # intentionally isolated; no upstream peer discovery
    match = PEER_RE.fullmatch(peer)
    if not match:
        raise ValueError("Peer must have the form host:29780")
    host, port = match.groups()
    if not 1 <= int(port) <= 65535:
        raise ValueError("Invalid P2P port")
    if host.lower() in ("localhost", "monero.com", "getmonero.org"):
        raise ValueError("Use a verified VMRX-only peer, not a Monero endpoint")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        if ".." in host or host.startswith("-") or host.endswith("-"):
            raise ValueError("Invalid host")
    return peer


def build_args(executable: str, data_dir: str, rpc_port: int, p2p_port: int, peer: str) -> list[str]:
    binary = Path(executable).expanduser().resolve()
    if not binary.is_file():
        raise ValueError("Select a real local vmrxd/monerod executable")
    if os.name != "nt" and not os.access(binary, os.X_OK):
        raise ValueError("Selected binary is not executable")
    data = Path(data_dir).expanduser().resolve()
    if not data.is_absolute():
        raise ValueError("Absolute data directory required")
    if not all(1024 <= int(x) <= 65535 for x in (rpc_port, p2p_port)):
        raise ValueError("Invalid port")
    if int(rpc_port) == int(p2p_port):
        raise ValueError("P2P and RPC ports must differ")
    return [str(binary), "--non-interactive", "--data-dir", str(data),
            "--p2p-bind-ip", "127.0.0.1", "--p2p-bind-port", str(int(p2p_port)),
            "--rpc-bind-ip", "127.0.0.1", "--rpc-bind-port", str(int(rpc_port)),
            "--no-zmq", "--no-igd", "--disable-dns-checkpoints", "--check-updates", "disabled",
            "--add-exclusive-node", checked_peer(peer),
            "--log-file", str(data / "vmrx-node.log")]


def launch_node(executable: str, data_dir: str, rpc_port: int, p2p_port: int, peer: str) -> subprocess.Popen:
    args = build_args(executable, data_dir, rpc_port, p2p_port, peer)
    Path(data_dir).expanduser().mkdir(parents=True, exist_ok=True)
    return subprocess.Popen(args, stdin=subprocess.DEVNULL,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            shell=False, cwd=str(Path(data_dir).expanduser()),
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
