# VMRX Node & Miner Desktop v0.1.0-rc.1 — DRAFT

**Preview release. Not a wallet. Not yet independently built or tested on target platforms.**

## Included

- Local VMRX daemon status, network height, difficulty, peer count and chain-tip hash.
- RandomX hashrate/status and explicit Start/Stop mining with address and thread controls.
- Start/Stop of a GUI-owned daemon process; existing systemd/other nodes are never terminated by the Node Stop action.
- Loopback-only RPC, intentionally isolated peer bootstrap unless a VMRX-only peer is supplied.
- Cross-platform Python/Tkinter source, seven unit tests, Windows/Linux PyInstaller scripts and preview CI workflow.

## Not included

- VMRX Core or wallet binaries, wallet key management, wallet sending, installer signing, official brand assets.
- Independent security verification or production support.

## Supported development environment

- Python 3.12, standard Tk/Tcl GUI libraries, Windows x64 or Ubuntu 24.04 x64.
- Compatible VMRX daemon local RPC on port 29781 (operator RC2).

## Release gating

The `main` branch workflow only uploads preview artifacts. It does **not** publish a GitHub Release. Verify binaries, perform fresh Windows/Linux GUI integration tests with the real VMRX Core, replace logo placeholders, and approve before adding any public tag.
