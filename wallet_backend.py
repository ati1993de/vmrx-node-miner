"""Local VMRX wallet-RPC adapter (experimental; not a security-audited wallet).

Private keys and mnemonic operations are performed by the VMRX Core wallet engine,
NOT by Python. A fresh authenticated wallet-RPC child binds only to localhost.
No telemetry, browser wallet service or remote seed submission is involved.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
import threading
import urllib.error
import urllib.request

WALLET_PORT = 29782
ATOMIC_UNITS = 10**12
_WALLET_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,47}\Z")
_WALLET_EXES = {"vmrx-wallet-rpc", "vmrx-wallet-rpc.exe", "monero-wallet-rpc", "monero-wallet-rpc.exe"}
_RPC_METHODS = frozenset({
    "get_address", "get_balance", "get_height", "get_transfers", "refresh",
    "create_wallet", "restore_deterministic_wallet", "open_wallet", "close_wallet",
    "store", "query_key", "transfer", "relay_tx", "change_wallet_password",
})


class WalletError(RuntimeError):
    pass



VMRX_GENESIS = "405baab8805904ffb7d3643a5004c43b45fc3f5f4c97e712ba4c078a384139d4"


def verify_vmrx_daemon(port: int) -> None:
    """Refuse to handle wallet keys when localhost RPC is not the VMRX mainnet."""
    if not 1024 <= int(port) <= 65535:
        raise WalletError("Invalid VMRX daemon RPC port")
    endpoint = f"http://127.0.0.1:{int(port)}/json_rpc"
    body = json.dumps({
        "jsonrpc": "2.0", "id": "verify-vmrx", "method": "get_block_header_by_height",
        "params": {"height": 0},
    }).encode("utf-8")
    request = urllib.request.Request(
        endpoint, data=body, method="POST", headers={"Content-Type": "application/json"})
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(request, timeout=5) as response:
            payload = json.load(response)
        genesis = payload["result"]["block_header"]["hash"]
    except (OSError, ValueError, KeyError, TypeError):
        raise WalletError("Could not verify the locally running VMRX Core daemon genesis") from None
    if genesis != VMRX_GENESIS:
        raise WalletError("WRONG BLOCKCHAIN at local daemon port: VMRX genesis mismatch; refusing wallet engine")


def wallet_name(name: str) -> str:
    if not isinstance(name, str) or not _WALLET_NAME.fullmatch(name) or name in (".", ".."):
        raise WalletError("Wallet name must be 1–48 letters, digits, _ or - (starting with a letter/digit).")
    return name


def vmrx_amount(value: str) -> int:
    try:
        amount = Decimal(value.strip())
        units = amount * ATOMIC_UNITS
    except (InvalidOperation, ValueError, AttributeError):
        raise WalletError("Enter a valid amount.") from None
    if not amount.is_finite() or amount <= 0 or units != units.to_integral_value():
        raise WalletError("Amount must be positive, with at most 12 decimal places.")
    if units > 2**64 - 1:
        raise WalletError("Amount is too large.")
    return int(units)


def find_wallet_binary() -> str:
    root = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
    for name in ("vmrx-wallet-rpc.exe", "monero-wallet-rpc.exe", "vmrx-wallet-rpc", "monero-wallet-rpc"):
        candidate = root / "core" / name
        if candidate.is_file() and (os.name == "nt" or os.access(candidate, os.X_OK)):
            return str(candidate)
    return ""


class WalletRpc:
    """Authenticated JSON-RPC over localhost only; no remote wallet RPC option."""

    def __init__(self, port: int, username: str, password: str, timeout: int = 25):
        if not 1024 <= int(port) <= 65535:
            raise WalletError("Invalid local wallet-RPC port")
        self.url = f"http://127.0.0.1:{int(port)}/json_rpc"
        auth = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        auth.add_password(None, self.url, username, password)
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPDigestAuthHandler(auth))
        self.timeout = timeout

    def call(self, method: str, params: dict | None = None) -> dict:
        if method not in _RPC_METHODS:
            raise WalletError("Unsupported wallet-RPC method")
        req = urllib.request.Request(
            self.url,
            data=json.dumps({"jsonrpc": "2.0", "id": "vmrx", "method": method, "params": params or {}}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with self.opener.open(req, timeout=self.timeout) as response:
                payload = json.load(response)
        except (OSError, ValueError, urllib.error.URLError) as error:
            # Never expose request contents, wallet passwords or seeds via error strings.
            raise WalletError(f"Wallet RPC {method} failed (transport/authentication).") from None
        if not isinstance(payload, dict):
            raise WalletError(f"Wallet RPC {method} returned malformed data")
        if payload.get("error"):
            error = payload["error"]
            code = error.get("code", "?") if isinstance(error, dict) else "?"
            # Server-supplied error text may inadvertently contain private input.
            raise WalletError(f"Wallet RPC {method} rejected request (code {code}).")
        if not isinstance(payload.get("result"), dict):
            raise WalletError(f"Wallet RPC {method} returned no result")
        return payload["result"]

    def create(self, name: str, password: str) -> str:
        self.call("create_wallet", {"filename": wallet_name(name), "password": password, "language": "English"})
        return self.address()

    def restore(self, name: str, password: str, seed: str, height: int = 0) -> str:
        if not 0 <= int(height) <= 500_000_000:
            raise WalletError("Invalid recovery height")
        seed = " ".join(seed.split())
        if len(seed.split()) not in (24, 25):
            raise WalletError("Enter a valid 24/25-word mnemonic (including checksum when present).")
        result = self.call("restore_deterministic_wallet", {
            "filename": wallet_name(name), "password": password,
            "seed": seed, "seed_offset": "", "restore_height": int(height),
            "language": "English", "autosave_current": True,
        })
        return result.get("address") or self.address()

    def open(self, name: str, password: str) -> str:
        self.call("open_wallet", {"filename": wallet_name(name), "password": password, "autosave_current": True})
        return self.address()

    def close(self):
        return self.call("close_wallet", {"autosave_current": True})

    def store(self):
        return self.call("store")

    def address(self) -> str:
        result = self.call("get_address", {"account_index": 0, "address_index": [0]})
        address = result.get("address")
        if not isinstance(address, str) or not address:
            raise WalletError("Wallet returned no receiving address")
        return address

    def balance(self) -> dict:
        return self.call("get_balance", {"account_index": 0})

    def transactions(self) -> dict:
        return self.call("get_transfers", {
            "in": True, "out": True, "pending": True, "failed": True, "pool": True,
            "account_index": 0,
        })

    def refresh(self) -> dict:
        return self.call("refresh")

    def seed(self) -> str:
        seed = self.call("query_key", {"key_type": "mnemonic"}).get("key")
        if not isinstance(seed, str) or not seed:
            raise WalletError("No mnemonic available from wallet engine")
        return seed

    def prepare_transfer(self, recipient: str, amount: str) -> dict:
        if not re.fullmatch(r"[1-9A-HJ-NP-Za-km-z]{90,110}", recipient.strip()):
            raise WalletError("Check destination address")
        units = vmrx_amount(amount)
        tx = self.call("transfer", {
            "destinations": [{"address": recipient.strip(), "amount": units}],
            "account_index": 0, "priority": 1, "ring_size": 0, "unlock_time": 0,
            "payment_id": "", "get_tx_key": False, "do_not_relay": True,
            "get_tx_hex": False, "get_tx_metadata": True,
        })
        metadata = tx.get("tx_metadata")
        if not isinstance(metadata, str) or not metadata:
            raise WalletError("Wallet engine did not provide offline transaction metadata")
        return {"metadata": metadata, "tx_hash": tx.get("tx_hash", ""), "fee": int(tx.get("fee", 0)),
                "amount": units, "recipient": recipient.strip()}

    def relay(self, metadata: str) -> dict:
        if not isinstance(metadata, str) or not re.fullmatch(r"[0-9a-fA-F]+", metadata):
            raise WalletError("Invalid transaction metadata")
        return self.call("relay_tx", {"hex": metadata})


class WalletService:
    """Only starts/stops a wallet RPC process that this application owns."""

    def __init__(self):
        self.child: subprocess.Popen | None = None
        self.client: WalletRpc | None = None
        self.directory: Path | None = None
        self._credentials: tuple[str, str] | None = None
        self._lock = threading.Lock()

    def start(self, executable: str, wallet_dir: str, daemon_port: int = 29781, rpc_port: int = WALLET_PORT):
        with self._lock:
            if self.child and self.child.poll() is None:
                raise WalletError("Wallet engine is already running")
            binary = Path(executable).expanduser().resolve()
            if binary.name.lower() not in _WALLET_EXES or not binary.is_file():
                raise WalletError("Choose a real VMRX wallet-RPC executable")
            if os.name != "nt" and not os.access(binary, os.X_OK):
                raise WalletError("Wallet-RPC executable is not executable")
            if not all(1024 <= int(p) <= 65535 for p in (daemon_port, rpc_port)) or daemon_port == rpc_port:
                raise WalletError("Invalid/conflicting localhost ports")
            unresolved = Path(wallet_dir).expanduser()
            if unresolved.is_symlink():
                raise WalletError("Wallet folder must not be a symbolic link")
            target = unresolved.resolve()
            if target.is_symlink():
                raise WalletError("Wallet folder must not be a symbolic link")
            target.mkdir(parents=True, exist_ok=True, mode=0o700)
            if os.name != "nt":
                target.chmod(0o700)
            verify_vmrx_daemon(int(daemon_port))
            username, auth_secret = "vmrxgui", secrets.token_urlsafe(32)
            cmd = [
                str(binary), "--wallet-dir", str(target),
                "--rpc-bind-ip", "127.0.0.1", "--rpc-bind-port", str(rpc_port),
                "--rpc-login", f"{username}:{auth_secret}",
                "--daemon-address", f"127.0.0.1:{int(daemon_port)}",
                "--trusted-daemon",
                "--log-level", "0",
            ]
            try:
                child = subprocess.Popen(
                    cmd, shell=False, cwd=str(target), stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
            except OSError:
                raise WalletError("Could not start selected wallet-RPC binary") from None
            self.child = child
            self.directory = target
            self._credentials = (username, auth_secret)
            self.client = WalletRpc(rpc_port, username, auth_secret)
            return child.pid

    def running_client(self) -> WalletRpc:
        if not self.child or self.child.poll() is not None or not self.client:
            raise WalletError("Start the bundled VMRX wallet engine first")
        return self.client

    def stop(self):
        with self._lock:
            if self.child and self.child.poll() is None:
                try:
                    if self.client:
                        self.client.close()
                except WalletError:
                    pass
                self.child.terminate()
                try:
                    self.child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # Never kill a process holding a wallet database without warning.
                    raise WalletError("Wallet RPC did not exit; inspect running processes")
            self.child = None
            self.client = None
            self._credentials = None

    def backup(self, name: str, destination: str) -> str:
        if not self.directory:
            raise WalletError("Start wallet service")
        self.running_client().store()
        wallet = wallet_name(name)
        unresolved = Path(destination).expanduser()
        if unresolved.is_symlink():
            raise WalletError("Backup destination must not be a symbolic link")
        base = unresolved.resolve()
        if base.is_symlink() or base == self.directory or self.directory in base.parents:
            raise WalletError("Select a separate backup directory")
        base.mkdir(parents=True, exist_ok=True, mode=0o700)
        if os.name != "nt":
            base.chmod(0o700)
        sources = [self.directory / wallet, self.directory / (wallet + ".keys")]
        if any(not x.is_file() or x.is_symlink() for x in sources):
            raise WalletError("Both wallet and .keys file must exist")
        if any((base / x.name).exists() for x in sources):
            raise WalletError("Backup already exists; choose an empty directory")
        for src in sources:
            dest = base / src.name
            with src.open("rb") as source, dest.open("xb") as output:
                shutil.copyfileobj(source, output)
            if os.name != "nt":
                dest.chmod(0o600)
            if sha256(src.read_bytes()).digest() != sha256(dest.read_bytes()).digest():
                raise WalletError("Backup verification failed; do not rely on this copy")
        return str(base)
