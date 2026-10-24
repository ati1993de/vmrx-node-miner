#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
test -s assets/vmrx-logo.png || { echo "Official VMRX logo assets/vmrx-logo.png missing"; exit 1; }
python3 -m unittest discover -s tests -v
python3 -m PyInstaller --noconfirm --clean --onefile --windowed \
  --name VMRX-Node-Miner --add-data "assets:assets" app.py
sha256sum dist/VMRX-Node-Miner > dist/VMRX-Node-Miner.sha256
printf '\nBinary ready: dist/VMRX-Node-Miner\nIMPORTANT: VMRX Core daemon is separately packaged.\n'
