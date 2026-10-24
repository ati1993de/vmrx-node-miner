# VMRX Node & Miner GUI security policy (preview)

This preview controls a **local daemon only**. It does not implement wallet keys, restore seeds or transfers. Please do not paste passwords or secrets into issues.

Potential security concerns:

1. An attacker controlling your local daemon can supply misleading RPC data; never treat displayed block height as proof of independent consensus.
2. Mining commands change the daemon's state. `stop_mining` stops any active miner on the attached daemon, regardless of who started it.
3. Launch only a trusted Core binary whose SHA-256 and source provenance you verified. A file chooser is not a verification tool.
4. Do not expose unrestricted RPC to the Internet or reuse Monero peer addresses for VMRX.
5. Never bundle original wallet password files, keys, caches, or private data with GUI releases.
6. This version has no log export; logs may contain sensitive node paths or host details.
7. Verify clean-install, malware scanning, code-signing and cross-platform user tests before public distribution.

GitHub maintainers should define an appropriate private disclosure route in the real repository settings before publication.
