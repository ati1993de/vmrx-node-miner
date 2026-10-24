VMRX Node & Miner v0.1.1 - Windows x64 integrated release (original guide, revised for upcoming VMRX Core)
============================================================

This package is built from the independent VMRX Core source and must pass
an actual Windows node startup and genesis RPC test before publication.

1. Extract the FULL ZIP to a new directory. Do not run the EXE from inside the ZIP.
2. Keep the 'core' folder with all DLLs next to VMRX-Node-Miner.exe.
3. Double-click VMRX-Node-Miner.exe.
4. Open 'Node Control'. The packaged core/vmrxd.exe is auto-detected.
5. Leave RPC at 29781, P2P at 29780; choose a dedicated data directory.
6. Click 'Start local node', then monitor 'Dashboard' for peers and sync.
7. After the node is fully synchronized, enter a separately verified VMRX
   receiving address in CPU Mining, choose CPU threads, then confirm mining.

A known VMRX-only bootstrap peer is prefilled: 31.70.81.5:29780, 217.154.93.20:29780 (operator candidates; real P2P handshake required).
It is operator-operated and may be temporarily unavailable.
Neither VMRX nor the GUI is Monero-compatible for chain/network data.
Do not use your Monero wallet or a Monero blockchain data directory.

Local daemon RPC is restricted to 127.0.0.1. P2P is also bound to localhost
by the GUI (outbound sync only; this is not a publicly reachable seed node).
This GUI does not include a wallet, keys, seed recovery, funds transfer, or
transaction signing. Mining requires a separately recoverable receiving address.

IMPORTANT: Early VMRX code is unaudited. Founder-seed recovery and spend
verification remain unresolved. The VMRX chain contains a 200,000 VMRX
founder premine in block 1 and 0.6 VMRX tail emission (no fixed supply cap).
Do not rely on this software for significant asset custody.

If the GUI shows Offline, check that core/vmrxd.exe exists and inspect
<your data directory>/vmrx-node.log for node errors. Another process may
already be using 29781/29780. Keep unrestricted RPC off the public Internet.

Core source provenance: see core/CORE-SOURCE.txt and its LICENSE/status files.
Public source: https://github.com/ati1993de/vmrx-core
GUI source: https://github.com/ati1993de/vmrx-node-miner
