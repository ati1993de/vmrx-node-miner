# VMRX Node & Miner v0.1.2 — Mainnet synchronization and branding corrections

**Release gating:** This document belongs to the unreleased v0.1.2 candidate branch. Do not tag or publish until the linked VMRX Core and GUI Windows live-block validation complete successfully.

## Changes since v0.1.1

- Fix missing **historical mainnet block-1 founder allocation validator** in the native VMRX Core; keep a narrow exception anchored to exact block hash, coinbase hash, both amounts and mainnet HF16, not a general consensus bypass.
- Bundle branded `core/vmrxd.exe` and required MinGW DLLs, not upstream-named `monerod.exe`.
- Show VMRX Core product/version information and correctly mark zero-peer nodes **ISOLATED**, never synced merely because the local tip equals the unknown network tip.
- Prefer `31.70.81.5:29780` (operator-observed VMRX P2P) and `217.154.93.20:29780` (operator-provided secondary, VMRX handshake not independently verified). Peers are **priority, not exclusive**, allowing real VMRX-only discovery; no upstream Monero seeds.
- Convert the five original 1254×1254 supplied brand PNGs to true transparent alpha while keeping the official artwork and same file paths. This covers GUI header, Windows ICO generation, READMEs and project preview imagery.
- Keep the Windows GUI+Core packaging gate and SHA256SUMS; Linux GUI still requires separate Linux Core.

## Verified so far

An isolated native Windows Core v0.1.2-dev GitHub test, on live VMRX P2P, reached **height 201 with 1 peer**, accepted the canonical block 1 with:
- Genesis `405baab8805904ffb7d3643a5004c43b45fc3f5f4c97e712ba4c078a384139d4`
- Block 1 `79030889ec6dd46cf2722defe9523bd38d2379168a27935fa3f1cdfe9397e293`
- Coinbase `d7f9691cb7c478fd87957e2210df12205399968e394e1d2a3e58ae56fb7b4645`
- Block-1 reward `200035184304979968` atomic units (200,000 VMRX premine + normal subsidy).

**Not yet proved:** complete Windows-to-Linux current-tip synchronization, wallet seed restoration/spend and independently verified receiving transactions, secure handling of private keys, software signing, audits or sustained peer availability.

## Security

VMRX is a separate Monero-derived RandomX chain; do not use upstream Monero or VMESH chain files. RPC stays on localhost by default. The historical 200,000 VMRX founder allocation and 0.6 VMRX tail subsidy (no fixed cap) must remain disclosed. The GUI is not a wallet and never handles seeds or keys.
