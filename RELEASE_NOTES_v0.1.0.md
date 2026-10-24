# VMRX Node & Miner v0.1.0 — Windows & Linux

Initial public main-channel desktop release for **local VMRX node monitoring and RandomX CPU mining control**.

## Included

- Windows x64 desktop GUI archive and Linux x86_64 desktop GUI archive.
- Owner-approved logo, app window icon, README branding and related image assets.
- Local blockchain overview: height, difficulty, peers, synchronization and latest block hash.
- CPU mining: enter receiving address, select threads, start/stop and view hashrate.
- Node Control: attach to local RPC and select/start an independently installed VMRX daemon.
- Friendly offline/onboarding message when no local daemon is running.
- SHA256SUMS for both published GUI archives.

## Critical platform limitations

**This is a GUI controller, not a standalone Windows or Linux cryptocurrency node.** The daemon binary is not bundled. No native Windows VMRX Core has yet been released. Thus Windows users cannot use mining or sync without building/providing a compatible Windows Core themselves. Linux users need to download the Linux Core separately.

No wallet accounts, seed restoration, send/receive, payments, installers, code signing, independent audit or reproducible build verification are supplied. GUI tests/builds do not validate those missing features.

RPC is restricted to `127.0.0.1` (default port 29781). Operator-observed VMRX P2P bootstrap peer `31.70.81.5:29780` may be unavailable. Do not connect to Monero peers.
