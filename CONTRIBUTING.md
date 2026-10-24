# Contributing (preview)

Submit focused issues and pull requests with reproduction steps. Never submit wallet seeds, passwords, private keys, unpublished server IPs or wallet backups. Use mock RPC responses for tests. Every PR should run `python -m unittest discover -s tests -v` and have a GUI smoke check under Windows and Linux. Preview workflow builds are not audited release binaries.

## Release process

Protect the default branch; require review and CI; audit dependencies; replace draft assets with approved project branding; verify VMRX-specific RPC and source provenance; cross-test Windows and Linux on a fresh machine; sign checksum manifests before announcing a release. Do not enable automatic GitHub release publishing from unreviewed pushes.
