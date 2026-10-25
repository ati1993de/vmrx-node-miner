# VMRX Wallet Beta — portable VMRX Node & Miner desktop

> **EXPERIMENTAL WALLET BETA — NOT A STABLE WALLET.** The packaged VMRX Core wallet beta includes fork-native `core/vmrx-wallet-rpc(.exe)` and `core/vmrxd(.exe)`; the ordinary v0.1.3 stable Core release does NOT include wallet RPC. Native Wallet RPC authenticated wallet creation, encrypted-file persistence, reopening, and fresh mnemonic restoration were verified on Windows and Linux in [cross-platform GitHub CI](https://github.com/ati1993de/vmrx-core/actions/runs/40190734788). **Real funded receiving/sending, historical founder wallet restoration and independent security audit are still UNVERIFIED. Do not use significant funds.**

Official project instructions: https://randomx.vargamesh.com/

## Scope of the Wallet (Beta) tab

- Launches **only a locally selected VMRX-branded Core** `vmrx-wallet-rpc` / `vmrx-wallet-rpc.exe` engine, binds only to **127.0.0.1:29882**, and uses generated HTTP Digest RPC credentials.
- Before wallet-RPC is launched, compares the connected **VMRX Core daemon's genesis hash** with `405baab8805904ffb7d3643a5004c43b45fc3f5f4c97e712ba4c078a384139d4`. It refuses other chains.
- Creates new wallets (native wallet-RPC `create_wallet`) with encrypted keys, opens existing encrypted wallets, restores deterministic wallets through **native Core** (`restore_deterministic_wallet`, with optional original-address check and selectable restore height), closes and stores them.
- Displays the primary receiving address, available/locked balances, sync height and transfer history; can populate the CPU mining receiving-address field.
- Displays a recovery mnemonic only following explicit local consent. The private seed is **never submitted to a website**, written to app logs, or added to application configuration.
- Creates local copies of the wallet cache file and password-encrypted `.keys` file, with per-file SHA256 verification. Refuses overwriting an existing backup. Backups are highly sensitive even when encrypted.
- Implements an experimental two-phase send: native wallet engine **prepares without broadcasting**, GUI shows recipient, amount and network fee for a second explicit confirmation, and only then invokes `relay_tx`. Sending is additionally opt-in and **not production-safe** yet.
- Includes a button to open https://randomx.vargamesh.com/ and an in-app safety guide.

## Installation — portable Windows EXE or Linux desktop

1. Download the experimental Node & Miner wallet-beta archive from [Releases](https://github.com/ati1993de/vmrx-node-miner/releases); verify `SHA256SUMS` and extract the whole archive. On Windows keep `VMRX-Node-Miner.exe` and the complete `core/` folder together. On Linux run the bundled `VMRX-Node-Miner` executable from a desktop with X11/Tk support. The wallet engine is already bundled; do **not** substitute upstream Monero binaries.
2. In Node Control, launch the VMRX-only daemon using a fresh VMRX data directory; verify real mainnet peer connectivity and synchronization.
3. In Wallet (Beta), confirm the auto-selected bundled `core/vmrx-wallet-rpc(.exe)` file and click Start engine. The wallet files default to `~/.vmrx-node/wallets`, distinct from any Monero/VMESH wallet directory.
4. Create a wallet with a strong unique password. Save its recovery words offline, in their exact order, and create an encrypted file backup.
5. **Recovery acceptance:** Restore the seed into a **new unused filename**, starting from height 0, and check that its address is identical to the original wallet's primary address. Confirm a real on-chain receive and spend using small amounts before any actual funds are relied upon.
6. Close and stop the GUI-owned wallet engine when finished. Never expose wallet-RPC or unrestricted daemon RPC to a public IP.

## Security limitations / blockers

**DO NOT PUBLISH a stable GUI release with wallet enabled until all these are resolved:**

- **Native wallet engine build: PASSED** for Windows x64 and Linux x64 with fork-native source, packaging and checksums; stable release remains gated until the other items are complete.
- **Fresh-wallet create/store/open/restore: PASSED** on Windows and Linux. Original and recovered primary address and view key match exactly. **Historical founder-wallet recovery is NOT tested.** Earlier Core documentation reports a founder wallet seed/address mismatch.
- Fresh VMRX nodes synchronize with the genuine VMRX mainnet. Verify small, actual, reversible-in-the-test-environment **receive/spend/fee/balance** operations and result finality on an independent node. Do not rely solely on mocked requests.
- Complete an independent security assessment of seed handling, key storage, transaction generation and restore. Python strings cannot guarantee immediate memory zeroing; wallet passwords, RPC credentials and short-lived seed data exist in application process memory. **HTTP Digest RPC credentials are also visible in the locally launched child process arguments** to local users with process-inspection permissions. The current design assumes a trusted local workstation. Encrypt full-disk storage and protect the user account.
- Harden GUI cancellation/shutdown and storage against crashes/partial backups. No device hardware-wallet integration, signed Windows installer, auto-updates or macOS bundle is supplied.
- Never assume that passing Python mock tests is evidence of real native wallet, network, recovery or spend compatibility.

VMRX is an independent Monero-derived RandomX chain with an already disclosed **200,000 VMRX founder allocation**. It is unrelated to SHA-256d VMESH. Never enter VMRX recovery phrases on `randomx.vargamesh.com`, GitHub, in chats, support tickets, or untrusted wallets.

## Development tests

```bash
python -m compileall -q app.py wallet_backend.py wallet_ui.py tests
python -m unittest discover -s tests -v
```

The dedicated cross-platform GitHub Actions workflow also smoke-launches the **Tk application** without opening a wallet. Separate Core CI builds the native wallet engines and tests seed recovery on both operating systems. Neither GUI mock tests nor native empty-wallet restoration certify real receiving/spending or a security audit.
