VMRX Node & Miner v0.1.2 – Windows full-node candidate
=======================================================

This bundle contains a native Windows VMRX Core built from a pinned,
independently reviewed fork commit. Before publication its real P2P tests
must match the historical VMRX chain through height 1193.

1. Unzip the entire package to a fresh folder (not just the EXE).
2. Keep core/vmrxd.exe and all supplied runtime DLLs together.
3. Launch VMRX-Node-Miner.exe; the correct local Core is auto-selected.
4. Select a separate VMRX data directory and click Start local node.
5. RPC is localhost:29781 and outbound P2P uses localhost:29780.
6. The controller will prefer both VMRX mainnet peer candidates:
   31.70.81.5:29780 (actual VMRX handshake previously observed)
   217.154.93.20:29780 (operator-provided; handshake not independently verified).
   Connections are NOT exclusive; peers must pass normal VMRX P2P validation.
   Leave the peer field blank to intentionally isolate this node.
7. Confirm peer count >0 and local chain height reaches the Windrose tip
   with matching hashes for historical blocks 0, 1, and later blocks.
8. Enable CPU mining only after genuine mainnet synchronization, and only
   to an address that has been independently restored/verified.

Block 0 expected hash:
405baab8805904ffb7d3643a5004c43b45fc3f5f4c97e712ba4c078a384139d4
Block 1 expected hash:
79030889ec6dd46cf2722defe9523bd38d2379168a27935fa3f1cdfe9397e293

Height 1/1 with zero P2P peers is ISOLATED, NOT 100% synced.
Do not import Monero or VMESH blockchain data or wallet keys.
No GUI wallet spending, wallet recovery, transfer or key management is provided.
Existing VMRX founder premine: 200,000 VMRX at historic block 1.
VMRX is not independently security audited, wallet seed recovery and
independent funds-spend verification remain unresolved.

Inspect core/CORE-SOURCE.txt for exact source commit and source license.
More: https://github.com/ati1993de/vmrx-node-miner
VMRX Core: https://github.com/ati1993de/vmrx-core
