# VMRX Node & Miner v0.1.2 — Mainnet synchronization and branding corrections

**Release acceptance:** Publication is gated by the linked VMRX Core and integrated GUI Windows mainnet tests, Linux GUI unit/build tests, source commit provenance and checksum verification.

## Changes since v0.1.1

- Fix missing **historical mainnet block-1 founder allocation validator** in the native VMRX Core; keep a narrow exception anchored to exact block hash, coinbase hash, both amounts and mainnet HF16, not a general consensus bypass.
- Bundle branded `core/vmrxd.exe` with an embedded official VMRX Windows icon, the original multi-resolution `core/vmrx.ico`, and the required MinGW runtime DLLs. No renamed upstream Monero release binaries.
- Show VMRX Core product/version information and correctly mark zero-peer nodes **ISOLATED**, never synced merely because the local tip equals the unknown network tip.
- Prefer `31.70.81.5:29780` (operator-observed VMRX P2P) and `217.154.93.20:29780` (operator-provided secondary, VMRX handshake not independently verified). Peers are **priority, not exclusive**, allowing real VMRX-only discovery; no upstream Monero seeds.
- Convert the five original 1254×1254 supplied brand PNGs to true transparent alpha while keeping the official artwork and same file paths. This covers GUI header, Windows ICO generation, READMEs and project preview imagery.
- Prevent CPU mining on an isolated daemon with zero P2P peers; check live synchronization before starting.
- Keep native Windows GUI+Core binary packaging gates, six historic mainnet blockhash checks and SHA256SUMS; Linux GUI still requires separate Linux Core.

## Verified so far

Fresh Linux and native Windows Core CI tests independently synchronized through historical height **1193** (more than 1,200 blockchain heights in the GitHub test), while the Windrose Linux operator candidate matched its production tip at height 1194 on 25 October 2026. The integrated GUI package's own native Windows test must separately verify the same six historical hashes, including the canonical block 1 with:
- Genesis `405baab8805904ffb7d3643a5004c43b45fc3f5f4c97e712ba4c078a384139d4`
- Block 1 `79030889ec6dd46cf2722defe9523bd38d2379168a27935fa3f1cdfe9397e293`
- Coinbase `d7f9691cb7c478fd87957e2210df12205399968e394e1d2a3e58ae56fb7b4645`
- Block-1 reward `200035184304979968` atomic units (200,000 VMRX premine + normal subsidy).

**Not yet proved:** indefinite future synchronization and resilience across arbitrary peers, GUI-driven real-world mining payouts, wallet seed restoration/spend or independently verified receiving transactions, secure handling of private keys, executable code signing, independent security audits or sustained peer availability.

## Security

VMRX is a separate Monero-derived RandomX chain; do not use upstream Monero or VMESH chain files. RPC stays on localhost by default. The historical 200,000 VMRX founder allocation and 0.6 VMRX tail subsidy (no fixed cap) must remain disclosed. The GUI is not a wallet and never handles seeds or keys.
