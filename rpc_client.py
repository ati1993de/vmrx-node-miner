"""Minimal VMRX daemon RPC client. Never connects to non-loopback addresses.

No wallet passwords, keys or seed phrases are accepted or stored here.
"""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request

_ADDRESS = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{90,110}$")


class RpcError(Exception):
    """A connection, response, or node-status error."""


def valid_mining_address(value: str) -> bool:
    """Conservative character/length sanity check; checksum is verified by daemon."""
    return bool(_ADDRESS.fullmatch(value.strip()))


class VMRXRpc:
    """Requests are hard-bound to 127.0.0.1; no remote/full RPC exposure."""

    def __init__(self, port: int = 29781, timeout: float = 3.0):
        self.port = int(port)
        if not (1024 <= self.port <= 65535):
            raise ValueError("RPC port must be between 1024 and 65535")
        self.timeout = float(timeout)

    def request(self, method: str, data: dict | None = None) -> dict:
        if not re.fullmatch(r"[a-z_]+", method):
            raise RpcError("Invalid RPC method")
        url = f"http://127.0.0.1:{self.port}/{method}"
        body = json.dumps(data if data is not None else {}).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                result = json.load(response)
        except (OSError, urllib.error.URLError, ValueError) as e:
            raise RpcError(f"RPC {method}: {e}") from e
        if not isinstance(result, dict):
            raise RpcError("Daemon returned an invalid JSON object")
        return result

    def info(self) -> dict:
        result = self.request("get_info")
        if result.get("status") not in ("OK", None):
            raise RpcError(f"get_info: {result.get('status')}")
        return result

    def mining_status(self) -> dict:
        result = self.request("mining_status")
        if result.get("status") != "OK":
            raise RpcError(f"mining_status: {result.get('status', 'unknown error')}")
        return result

    def start_mining(self, address: str, threads: int, background: bool = False) -> dict:
        if not valid_mining_address(address):
            raise RpcError("Address format looks invalid; verify your VMRX address")
        if not 1 <= int(threads) <= 64:
            raise RpcError("CPU threads must be between 1 and 64")
        result = self.request("start_mining", {
            "miner_address": address.strip(),
            "threads_count": int(threads),
            "do_background_mining": bool(background),
            "ignore_battery": False,
        })
        if result.get("status") != "OK":
            raise RpcError(f"Mining was NOT started: {result.get('status', 'unknown error')}")
        return result

    def stop_mining(self) -> dict:
        result = self.request("stop_mining")
        if result.get("status") != "OK":
            raise RpcError(f"Mining was NOT stopped: {result.get('status', 'unknown error')}")
        return result
