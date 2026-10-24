# VMRX Node & Miner

<p align="center"><img src="assets/vmrx-logo.png" alt="Official VMRX logo" width="144"></p>

**VargaMesh RX · Windows / Linux · RandomX CPU mining and local node controller**

[Latest release](https://github.com/ati1993de/vmrx-node-miner/releases/latest) · [VMRX Core](https://github.com/ati1993de/vmrx-core) · [Security](SECURITY.md)

VMRX Node & Miner is a desktop application for monitoring and controlling a **local VMRX daemon**. It shows blockchain height, peer count, difficulty, synchronization, chain tip and mining hashrate; it can start/stop CPU mining on a connected local daemon. All RPC traffic goes to `127.0.0.1`.

> **Important:** This application is a node/miner **controller**, not a complete wallet. Neither release includes a Windows Core daemon. Windows mining requires a separately built, compatible Windows VMRX Core. Linux users must install the Linux VMRX Core separately. The GUI does not hold funds or accept mnemonic seeds.

## Features

| Feature | v0.1.0 |
| --- | --- |
| Local blockchain height, difficulty, peers and chain tip | Yes |
| Synchronization and RandomX hashrate | Yes |
| CPU mining start / stop with confirmation | Yes — daemon required |
| Choose CPU threads and verified mining address | Yes |
| Select and launch a local VMRX node executable | Yes — daemon supplied separately |
| Windows x64, Linux x86_64 GUI binaries | Yes |
| Bundled Windows Core / Windows full node | **No** |
| Sending, receiving, restoring a wallet or seed handling | **Not implemented** |
| Installer, signed binaries or external security audit | **Not provided** |

## Download & run

Download the relevant archive and `SHA256SUMS` from [Releases](https://github.com/ati1993de/vmrx-node-miner/releases/latest); verify the archive before running.

### Windows 10 / 11 x64

Extract `VMRX-Node-Miner-windows-x64.zip` and launch `VMRX-Node-Miner.exe`. The GUI will show **Offline** until a compatible **Windows VMRX Core daemon** is installed separately and listening on local RPC port `29781`. There is presently **no native Windows Core binary** in the Core releases, so the GUI does not yet provide a standalone Windows node/mining installation.

### Linux x86_64 desktop

Extract `VMRX-Node-Miner-linux-x86_64.tar.gz` and run `./VMRX-Node-Miner` **in a graphical desktop session**. Separately download and verify the Linux Core from [VMRX Core releases](https://github.com/ati1993de/vmrx-core/releases/latest). In **Node Control**, select the released VMRX daemon (`monerod` in the present fork), choose a fresh data directory and launch it. Wait for sync before enabling CPU mining.

A VMRX-only peer `31.70.81.5:29780` is prefilled (observed by the operator; availability not guaranteed). Never connect to upstream Monero peers or reuse Monero/VMESH data directories. P2P and RPC bind to loopback in this controller; running a public seed node is a separate administrative task.

### Dashboard says Offline / WinError 10061

This means no daemon currently accepts connections at `127.0.0.1:29781`. Open **Node Control** to select/start VMRX Core. It is not a browser/server login failure. The Windows GUI alone cannot start mining without a separate compatible native Windows node.

## Native Windows full-node bundle (in development)

The `main` branch supports auto-selection of a **bundled** Windows daemon at `core/monerod.exe`. It never downloads or starts an executable without the user's action. The [complete Windows package workflow](.github/workflows/package-full-windows.yml) requires an independently checked **native Windows VMRX Core release**, which is not yet published. The workflow verifies both archives' SHA256SUMS and checks the bundled daemon's VMRX genesis before producing a single ZIP artifact. The GUI v0.1.0 release remains GUI-only. Do not mix it with upstream Monero binaries. See the [Windows Core build guide](https://github.com/ati1993de/vmrx-core/blob/main/docs/WINDOWS_BUILD.md).

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

On Windows run `scripts/build-windows.ps1`. Tagging `v0.1.0` triggers Windows/Linux GitHub Actions builds and then publishes the release only if **both GUI builds and tests succeed**. Build success is not evidence of working Windows Core, independent network consensus, recoverable wallets, or reproducible/security-audited binaries.

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
