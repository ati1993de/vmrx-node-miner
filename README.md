# VMRX Node & Miner Desktop — RC Preview

**Windows / Linux** · Python 3.12 + Tkinter · Local daemon RPC only

A desktop control panel for your existing VMRX RandomX daemon. The GUI lets you inspect the blockchain and peers, see mining hashrate, start/stop CPU mining, and launch or stop **only** a daemon you started in this GUI.

> **Preview, not a production wallet.** This package includes no VMRX Core executable and no seed/private-key handling. The proposed build workflow produces preview executables, not a full installer or verified stable release.

## Features

| Feature | In this source |
| --- | --- |
| Network dashboard: height, difficulty, peers, chain tip | Yes |
| Real-time synchronization state | Yes (local daemon RPC) |
| RandomX mining status, H/s | Yes |
| Start mining with address + thread selection | Yes, confirmation required |
| Stop daemon mining | Yes, confirmation required |
| Launch/stop owned VMRX daemon binary | Yes, local-only |
| Connect to an existing local node | Yes |
| Windows and Linux build workflow | Yes, not yet independently run |
| Local wallet balance, send, restore, seed handling | **Not implemented** |
| Remote public RPC / public seed management | **Intentionally not implemented** |
| Bundled VMRX core or Windows installer | **Not supplied** |

## Run directly (from source)

### Linux Ubuntu 24.04+

```bash
sudo apt-get install -y python3 python3-tk
python3 app.py
```

### Windows

Install Python 3.12 with the standard Tcl/Tk option enabled. Run:

```powershell
py -3.12 app.py
```

The dashboard connects by default to `http://127.0.0.1:29781` (VMRX daemon local RPC). An existing daemon must be running, or you may select your *verified* `vmrxd` / `monerod` executable in **Node Control**.

### Node-control safety defaults

- RPC **always** on `127.0.0.1`; the GUI never permits an arbitrary remote RPC host.
- When the GUI launches a daemon, P2P binds to localhost by default; this isn't a public seed-node installer.
- If no VMRX peer is provided, the GUI adds `--add-exclusive-node 127.0.0.1:1` to keep the node isolated. Add an independently checked VMRX-only peer to actually synchronize.
- No Monero seed nodes; VMRX and Monero networks must never be mixed.
- Node Stop only terminates a process launched by this app. It never stops the operator's existing systemd service.
- If the daemon isn't synchronized, mining won't start. Mining control relies on `start_mining`, `mining_status`, `stop_mining` from the local daemon.
- RPC may expose sensitive data or dangerous commands. Do not bind unrestricted RPC to a public address.

## Build preview executables

Install build-only tools:

```bash
python -m pip install -r requirements-build.txt
```

Linux:

```bash
bash scripts/build-linux.sh
# dist/VMRX-Node-Miner
```

Windows PowerShell (run on a **Windows build machine**):

```powershell
./scripts/build-windows.ps1
# dist/VMRX-Node-Miner.exe
```

A GitHub Actions workflow `.github/workflows/build-preview.yml` builds artifacts on `ubuntu-24.04` and `windows-latest`. Check its test results and artifact checksums. On Git tags matching `v*`, after both builds and tests pass, GitHub Actions **publishes a prerelease** containing the two GUI preview archives and SHA256SUMS. This does not bundle VMRX Core.

**Note:** the Linux GUI build is a bundled Python executable, not an AppImage/.deb and does not bundle VMRX core or all host GUI libraries. A Windows Core daemon binary must be built separately from verified VMRX source for local-node start functionality.

## Attribution & branding

The artwork in `assets/` is labeled `DRAFT`. Replace it with official approved VMRX assets before publishing. The VMRX core is derived from Monero; preserve all upstream notices in the separate Core project.

## Security note

Never paste wallet seeds or private keys into this GUI, an issue, or build logs. Wallet operations should use a separately audited component. The sample UI is an early Node/Miner controller and its correctness has not been independently audited.
