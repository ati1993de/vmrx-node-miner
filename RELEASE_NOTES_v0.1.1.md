# VMRX Node & Miner v0.1.1 — Windows integrated Core + GUI

This release fixes the **missing Windows node** in the v0.1.0 GUI-only ZIP.

## Windows x64 (build-gated)

- Ships `VMRX-Node-Miner.exe` alongside `core/monerod.exe` and the needed native MinGW runtime DLLs.
- Compiles the daemon from the **actual VMRX Core** fork at pinned revision `d39c676eae02805634ef238f4c2d87976d6bf0f1` — no Monero binary substitution.
- Native Windows smoke test is **mandatory**: launch the daemon offline on localhost, query `get_info`, and verify genesis `405baab8805904ffb7d3643a5004c43b45fc3f5f4c97e712ba4c078a384139d4` over JSON RPC.
- Stops the release pipeline if compilation, node startup, genesis verification or inclusion of `core/monerod.exe` fails.
- Preselects the bundled daemon automatically in **Node Control**; starting it remains an explicit user action.
- Adds a Windows quick-start guide, Core source provenance, license and SHA256 checksums.

## Linux x86_64

The Linux archive is **still GUI-only**. Linux VMRX Core must be installed from the separate Core repository.

## Known limits

This GUI is **not a wallet**: no seed handling, account management, funds sending or transfer signing. Seed restoration and spend/recipient confirmation in the underlying Core have not been independently verified. VMRX consensus and security have not had an independent audit. The chain includes a **200,000 VMRX founder premine in block 1** and `0.6 VMRX` tail emission (no fixed supply cap). The prefilled single VMRX peer is operator-run and may be unavailable. The bundled node binds P2P and RPC to localhost by default; it is not a publicly exposed full seed node.

**Build-gated release** means these checks must pass to publish. It does not guarantee all mainnet networking, mining payout or wallet safety. Please independently verify the downloaded ZIP with the published `SHA256SUMS` file.
