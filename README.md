# VMRX Node & Miner

<p align="center"><img src="assets/vmrx-logo.png" alt="Official VMRX logo" width="144"></p>

**VargaMesh RX · Windows x64 bundled Core + Linux desktop Node & Miner**

> **Wallet development branch (NOT RELEASED):** The experimental Wallet (Beta) tab adds local wallet-RPC creation, mnemonic recovery, backups, balances and an opt-in two-stage send interface. **It is not a complete distributable wallet yet:** the published v0.1.2 Core packages do not contain a wallet-RPC executable, and native seed recovery / send testing is still outstanding. Do not use it for valuable coins. [Wallet instructions and release blockers](WALLET_GUIDE.md) · [VMRX official website](https://randomx.vargamesh.com/). The public v0.1.2 release remains Node & Miner only.

[Latest release](https://github.com/ati1993de/vmrx-node-miner/releases/latest) · [VMRX Core](https://github.com/ati1993de/vmrx-core) · [Security](SECURITY.md) · [Wallet guide](WALLET_GUIDE.md) · [Official VMRX website](https://randomx.vargamesh.com/)

VMRX Node & Miner is a desktop application for monitoring and controlling a **local VMRX daemon**. It shows blockchain height, peer count, difficulty, synchronization, chain tip and mining hashrate; it can start/stop CPU mining on a connected local daemon. All RPC traffic goes to `127.0.0.1`.

> **Mainnet compatibility:** The Windows v0.1.1 package is obsolete: its Core starts at genesis but rejects historic mainnet block 1. The **v0.1.2** release replaces it with native **`core/vmrxd.exe`**, the original VMRX logo and MinGW dependencies, built from the fixed Core source. Its release workflow requires real P2P synchronization and matching hashes at heights 0, 1, 2, 10, 100 and 1193. The Linux GUI is distributed separately from the Linux Core. This GUI controls the node and CPU miner; it is **not a wallet**.

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

Download the [current Windows ZIP](https://github.com/ati1993de/vmrx-node-miner/releases/latest), verify `SHA256SUMS`, and extract **every file** into a fresh folder. Keep `VMRX-Node-Miner.exe`, `core/vmrxd.exe`, `core/vmrx.ico` and the MinGW runtime DLLs together. Start `VMRX-Node-Miner.exe`, open **Node Control**, and select **Start local node**. The bundled Core is auto-detected; it is **not** launched automatically. Confirm at least one connected VMRX P2P peer and synchronization with the genuine mainnet tip before enabling CPU mining to an independently verified VMRX address.

### Linux x86_64 desktop

Extract `VMRX-Node-Miner-linux-x86_64.tar.gz` and run `./VMRX-Node-Miner` **in a graphical desktop session**. Separately download and verify the Linux Core from [VMRX Core releases](https://github.com/ati1993de/vmrx-core/releases/latest). In **Node Control**, select the released VMRX daemon (`vmrxd` for v0.1.2; older builds may still use `monerod`), choose a fresh data directory and launch it. Wait for sync before enabling CPU mining.

The v0.1.2 controller prioritizes both `31.70.81.5:29780` (Windrose P2P observed) and `217.154.93.20:29780` (operator-supplied; live VMRX handshake unverified), **non-exclusively**. Older v0.1.1 only offers the single exclusive Windrose peer. Never connect to upstream Monero peers or reuse Monero/VMESH data directories. P2P and RPC bind to loopback in this controller; running a public seed node is a separate administrative task.

### Dashboard says Offline / WinError 10061

This means no daemon currently accepts connections at `127.0.0.1:29781`. In the v0.1.1 integrated Windows archive, verify `core/monerod.exe` exists and is preselected in **Node Control**; click **Start local node**. Examine `<data directory>/vmrx-node.log` if the daemon exits. The old **v0.1.0 ZIP has no node**.

## Native Windows full-node bundle and legacy v0.1.1

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
