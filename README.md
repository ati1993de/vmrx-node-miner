# VMRX Node & Miner

<p align="center"><img src="assets/vmrx-logo.png" alt="Official VMRX logo" width="144"></p>

**VargaMesh RX · Windows integrated Node & Miner v0.1.1 / Linux desktop GUI**

[Latest release](https://github.com/ati1993de/vmrx-node-miner/releases/latest) · [VMRX Core](https://github.com/ati1993de/vmrx-core) · [Security](SECURITY.md)

VMRX Node & Miner is a desktop application for monitoring and controlling a **local VMRX daemon**. It shows blockchain height, peer count, difficulty, synchronization, chain tip and mining hashrate; it can start/stop CPU mining on a connected local daemon. All RPC traffic goes to `127.0.0.1`.

> **Release status:** **v0.1.1 is officially published for Windows x64 and Linux x86_64.** The [Windows ZIP](https://github.com/ati1993de/vmrx-node-miner/releases/download/v0.1.1/VMRX-Node-Miner-windows-x64.zip) includes the real VMRX `core/vmrxd.exe` and passed a native build + localhost RPC genesis test. The old v0.1.0 was GUI-only. Linux remains GUI-only and requires the separate [VMRX Core Linux release](https://github.com/ati1993de/vmrx-core/releases/tag/v0.1.1). Neither GUI handles wallet keys or seeds; full mainnet P2P interoperability and wallet spend/recovery remain unaudited.

## Features

| Feature | v0.1.1 Windows release |
| --- | --- |
| Local blockchain height, difficulty, peers and chain tip | Yes |
| Synchronization and RandomX hashrate | Yes |
| CPU mining start / stop with confirmation | Yes — daemon required |
| Choose CPU threads and verified mining address | Yes |
| Select and launch a local VMRX node executable | Yes — bundled Windows daemon preselected |
| Windows x64, Linux x86_64 GUI binaries | Yes |
| Bundled Windows Core / Windows full node | **Yes** — real native Core and DLLs included, genesis RPC smoke tested |
| Sending, receiving, restoring a wallet or seed handling | **Not implemented** |
| Installer, signed binaries or external security audit | **Not provided** |

## Download & run

Download the relevant archive and `SHA256SUMS` from [Releases](https://github.com/ati1993de/vmrx-node-miner/releases/latest); verify the archive before running.

### Windows 10 / 11 x64

**Download the official [Windows v0.1.1 ZIP](https://github.com/ati1993de/vmrx-node-miner/releases/download/v0.1.1/VMRX-Node-Miner-windows-x64.zip)** and extract the **entire ZIP** (not only the EXE). Keep `core/vmrxd.exe` and DLLs next to `VMRX-Node-Miner.exe`. Open **Node Control**, where the packaged node is auto-selected, and click **Start local node**. Wait until fully synchronized before using CPU Mining with an independently verified VMRX receiving address. See `README-WINDOWS.txt` within the ZIP. The old v0.1.0 ZIP has no node.

### Linux x86_64 desktop

Extract `VMRX-Node-Miner-linux-x86_64.tar.gz` and run `./VMRX-Node-Miner` **in a graphical desktop session**. Separately download and verify the Linux Core from [VMRX Core releases](https://github.com/ati1993de/vmrx-core/releases/latest). In **Node Control**, select the released VMRX daemon (`monerod` in the present fork), choose a fresh data directory and launch it. Wait for sync before enabling CPU mining.

A VMRX-only peer `31.70.81.5:29780 and 217.154.93.20:29780` is prefilled (observed by the operator; availability not guaranteed). Never connect to upstream Monero peers or reuse Monero/VMESH data directories. P2P and RPC bind to loopback in this controller; running a public seed node is a separate administrative task.

### Dashboard says Offline / WinError 10061

This means no daemon currently accepts connections at `127.0.0.1:29781`. In the v0.1.1 integrated Windows archive, verify `core/vmrxd.exe` exists and is preselected in **Node Control**; click **Start local node**. Examine `<data directory>/vmrx-node.log` if the daemon exits. The old **v0.1.0 ZIP has no node**.

## Native Windows full-node bundle (released)

The [official v0.1.1 Windows GUI ZIP](https://github.com/ati1993de/vmrx-node-miner/releases/tag/v0.1.1) bundles `VMRX-Node-Miner.exe` together with a fork-specific native `core/vmrxd.exe` and DLLs. The daemon is preselected but never started without a user action. Its build workflow verified the real Windows executable and the VMRX mainnet genesis over localhost RPC. Independently, the [official Windows-only Core package](https://github.com/ati1993de/vmrx-core/releases/tag/v0.1.1) is available. Do not substitute upstream Monero binaries, reuse Monero blockchain data or assume wallet recovery/spend safety just because genesis passed.

## Running from source

Linux **desktop** (not headless VPS):

```bash
sudo apt-get install -y python3 python3-tk
python3 app.py
```

Windows with Python 3.12 and Tk support:

```powershell
py -3.12 app.py
```

`py -3.12` is a **Windows-specific command**, not a Linux command. Tkinter cannot open a window on an SSH-only Ubuntu server without `DISPLAY`.

## Building and testing

```bash
python3 -m unittest discover -s tests -v
python3 -m pip install -r requirements-build.txt
bash scripts/build-linux.sh
```

On Windows run `scripts/build-windows.ps1` for a **GUI-only developer build**. The integrated GitHub Actions workflow checks out pinned [VMRX Core](https://github.com/ati1993de/vmrx-core) source, compiles the real Windows x64 daemon using MSYS2/MinGW64, collects DLLs, starts a local node and verifies the fork-specific genesis before publishing a tagged Windows integrated archive. No release is published if this gate fails. This is not a consensus/security audit or proof of recoverable wallet balances and spends.

## Branding

The desktop icon, header, README and release project imagery are derived from the **owner-provided** `assets/vmrx-logo.png`. Other supplied graphics are stored under [`assets/branding/`](assets/ASSETS.md). Placeholder draft icons are not used by this version.

## Security & disclosure

- Local-only daemon RPC; never expose unrestricted RPC on a public IP.
- Mining consumes CPU power and electricity. Always verify the payout address.
- No wallet files, passwords, mnemonic seed phrases, transaction signing, or on-chain transfers are implemented.
- VMRX is a **separate Monero-derived RandomX** chain, not SHA256d/AuxPoW VMESH.
- See [VMRX Core](https://github.com/ati1993de/vmrx-core) for the **200,000 VMRX founder premine** and other network parameters.

## License

Respect the repository license and all upstream third-party notices; the VMRX daemon is maintained separately under the Core repository.
