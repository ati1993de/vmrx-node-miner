# VMRX Node & Miner

<p align="center"><img src="assets/vmrx-logo.png" alt="Official VMRX logo" width="144"></p>

**VargaMesh RX · published v0.1.1; v0.1.2-dev Windows synchronization and branding corrections under review**

[Latest release](https://github.com/ati1993de/vmrx-node-miner/releases/latest) · [VMRX Core](https://github.com/ati1993de/vmrx-core) · [Security](SECURITY.md)

VMRX Node & Miner is a desktop application for monitoring and controlling a **local VMRX daemon**. It shows blockchain height, peer count, difficulty, synchronization, chain tip and mining hashrate; it can start/stop CPU mining on a connected local daemon. All RPC traffic goes to `127.0.0.1`.

> **Release status:** **v0.1.1 is officially published for Windows x64 and Linux x86_64.** The [Windows ZIP](https://github.com/ati1993de/vmrx-node-miner/releases/download/v0.1.1/VMRX-Node-Miner-windows-x64.zip) includes the real VMRX `core/monerod.exe` (upstream executable name in this older package) and passed a native build + localhost RPC genesis test, **but failed to synchronize past the genesis block in a real Windows test**. The old v0.1.0 was GUI-only. Linux remains GUI-only and requires the separate [VMRX Core Linux release](https://github.com/ati1993de/vmrx-core/releases/tag/v0.1.1). Neither GUI handles wallet keys or seeds. The v0.1.2-dev branch replaces `monerod.exe` with `vmrxd.exe`, allows non-exclusive preferred VMRX peers, includes transparent PNG logo assets, and makes real mainnet block-1 sync mandatory before a new release. Wallet spend/recovery remain unaudited.

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

**Download the official [Windows v0.1.1 ZIP](https://github.com/ati1993de/vmrx-node-miner/releases/download/v0.1.1/VMRX-Node-Miner-windows-x64.zip)** and extract the **entire ZIP** (not only the EXE). Keep `core/monerod.exe` and DLLs next to `VMRX-Node-Miner.exe` (the upcoming tested build will use `core/vmrxd.exe`). Open **Node Control**, where the packaged node is auto-selected, and click **Start local node**. Wait until fully synchronized before using CPU Mining with an independently verified VMRX receiving address. See `README-WINDOWS.txt` within the ZIP. The old v0.1.0 ZIP has no node.

### Linux x86_64 desktop

Extract `VMRX-Node-Miner-linux-x86_64.tar.gz` and run `./VMRX-Node-Miner` **in a graphical desktop session**. Separately download and verify the Linux Core from [VMRX Core releases](https://github.com/ati1993de/vmrx-core/releases/latest). In **Node Control**, select the released VMRX daemon (`monerod` in the present fork), choose a fresh data directory and launch it. Wait for sync before enabling CPU mining.

The v0.1.2-dev candidate prioritizes both `31.70.81.5:29780` (Windrose P2P observed) and `217.154.93.20:29780` (operator-supplied; live VMRX handshake unverified), **non-exclusively**. Older v0.1.1 only offers the single exclusive Windrose peer. Never connect to upstream Monero peers or reuse Monero/VMESH data directories. P2P and RPC bind to loopback in this controller; running a public seed node is a separate administrative task.

### Dashboard says Offline / WinError 10061

This means no daemon currently accepts connections at `127.0.0.1:29781`. In the v0.1.1 integrated Windows archive, verify `core/monerod.exe` exists and is preselected in **Node Control**; click **Start local node**. Examine `<data directory>/vmrx-node.log` if the daemon exits. The old **v0.1.0 ZIP has no node**.

## Native Windows full-node bundle (released)

The [official v0.1.1 Windows GUI ZIP](https://github.com/ati1993de/vmrx-node-miner/releases/tag/v0.1.1) bundles `VMRX-Node-Miner.exe` together with a fork-specific native `core/monerod.exe` and DLLs. The daemon is preselected but never started without a user action. Its build workflow verified the real Windows executable and the VMRX mainnet genesis over localhost RPC. Independently, the [official Windows-only Core package](https://github.com/ati1993de/vmrx-core/releases/tag/v0.1.1) is available. **Known v0.1.1 defect:** Windows connected to Windrose, learned block 807, but banned its peer and remained at height 1. Do not interpret 1/1 (100%) with zero peers as a synced node. See [sync issue #2](https://github.com/ati1993de/vmrx-node-miner/issues/2). Do not substitute upstream Monero binaries, reuse Monero blockchain data or assume wallet recovery/spend safety just because genesis passed.

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

On Windows run `scripts/build-windows.ps1` for a **GUI-only developer build**. The integrated GitHub Actions workflow checks out pinned [VMRX Core](https://github.com/ati1993de/vmrx-core) source, compiles the real Windows x64 daemon using MSYS2/MinGW64, collects DLLs, starts a local node and verifies the fork-specific genesis before publishing a tagged Windows integrated archive. The next release must additionally pass a **live VMRX block-1 network sync test**; a genesis-only test is insufficient. Do not publish a candidate while the block-1 check fails. This is not a consensus/security audit or proof of recoverable wallet balances and spends.

## Branding

The 1,254 × 1,254 original owner-approved PNG logos have been processed to remove only edge-connected black backdrops. The PNGs now have real transparent alpha (verified in the separate branding CI). GitHub READMEs and the Tk/Windows icon use the same `assets/vmrx-logo.png` so images retain transparency on light and dark backgrounds.


The desktop icon, header, README and release project imagery are derived from the **owner-provided** `assets/vmrx-logo.png`. Other supplied graphics are stored under [`assets/branding/`](assets/ASSETS.md). Placeholder draft icons are not used by this version.

## Security & disclosure

- Local-only daemon RPC; never expose unrestricted RPC on a public IP.
- Mining consumes CPU power and electricity. Always verify the payout address.
- No wallet files, passwords, mnemonic seed phrases, transaction signing, or on-chain transfers are implemented.
- VMRX is a **separate Monero-derived RandomX** chain, not SHA256d/AuxPoW VMESH.
- See [VMRX Core](https://github.com/ati1993de/vmrx-core) for the **200,000 VMRX founder premine** and other network parameters.

## License

Respect the repository license and all upstream third-party notices; the VMRX daemon is maintained separately under the Core repository.
