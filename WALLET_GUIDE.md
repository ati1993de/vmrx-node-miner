# VMRX Wallet (experimental development branch)

> **NOT a stable wallet release.** This GUI requires a **VMRX Core-built wallet RPC executable**; official v0.1.3 Core archives currently bundle a daemon only. Native wallet-RPC build, live wallet integration, deterministic seed recovery and actual spend/receive testing are not yet complete. Do not put valuable coins into an untested wallet.

Official project instructions: https://randomx.vargamesh.com/

## Scope of the Wallet (Beta) tab

- Launches a **user-selected local VMRX Core** `monero-wallet-rpc` / `vmrx-wallet-rpc` engine, binds only to **127.0.0.1:29882**, and uses generated HTTP Digest RPC credentials.
- Before wallet-RPC is launched, compares the connected **VMRX Core daemon's genesis hash** with `405baab8805904ffb7d3643a5004c43b45fc3f5f4c97e712ba4c078a384139d4`. It refuses other chains.
- Creates new wallets (native wallet-RPC `create_wallet`) with encrypted keys, opens existing encrypted wallets, restores deterministic wallets through **native Core** (`restore_deterministic_wallet`, with optional original-address check and selectable restore height), closes and stores them.
- Displays the primary receiving address, available/locked balances, sync height and transfer history; can populate the CPU mining receiving-address field.
- Displays a recovery mnemonic only following explicit local consent. The private seed is **never submitted to a website**, written to app logs, or added to application configuration.
- Creates local copies of the wallet cache file and password-encrypted `.keys` file, with per-file SHA256 verification. Refuses overwriting an existing backup. Backups are highly sensitive even when encrypted.
- Implements an experimental two-phase send: native wallet engine **prepares without broadcasting**, GUI shows recipient, amount and network fee for a second explicit confirmation, and only then invokes `relay_tx`. Sending is additionally opt-in and **not production-safe** yet.
- Includes a button to open https://randomx.vargamesh.com/ and an in-app safety guide.

## Installation for developers

1. Use the existing VMRX Core v0.1.3 native daemon (or later verified chain-compatible Core). Do **not** substitute upstream Monero wallet-RPC or daemon binaries.
2. Build the matching **VMRX Core wallet RPC** from its source (target `wallet_rpc_server`) for the OS, keeping every required dependency DLL beside it. Note: this target has not yet passed the required integrated release build and smoke tests.
3. Launch `app.py` on a desktop with Tkinter. In Node Control, launch the VMRX-only daemon using a fresh VMRX data directory. Verify live peers and real chain sync.
4. On Wallet (Beta), choose the locally compiled VMRX wallet-RPC executable and click Start engine. The wallet files default to `~/.vmrx-node/wallets`, distinct from any Monero/VMESH wallet directory.
5. Create a wallet with a strong unique password. Save its recovery words offline, in their exact order, and create an encrypted file backup.
6. **Recovery acceptance:** Restore the seed into a **new unused filename**, starting from height 0, and check that its address is identical to the original wallet's primary address. Confirm a real on-chain receive and spend using small amounts before any actual funds are relied upon.
7. Close and stop the GUI-owned wallet engine when finished. Never expose wallet-RPC or unrestricted daemon RPC to a public IP.

## Security limitations / blockers

**DO NOT PUBLISH a stable GUI release with wallet enabled until all these are resolved:**

- A VMRX Core wallet-RPC executable is built on **Windows x64 and Linux x64 from pinned fork source** and shipped in the actual release archives, along with runtime DLLs, verified checksums and licenses.
- Fresh isolated test wallets are created, stored, closed, reopened and recovered from their mnemonic on **both OSes**. The post-restore **primary address must match** byte-for-byte, and the recovered wallet must derive the same spend/view keys. Test both an empty wallet and historical founder-wallet recovery where possible. The existing Core documentation reports a founder wallet seed/address mismatch.
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

The dedicated cross-platform GitHub Actions workflow also smoke-launches the **Tk application** without opening a wallet. Those checks do not build the native wallet engine or substitute for wallet security tests.
