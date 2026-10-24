$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')
python -m unittest discover -s tests -v
python -m PyInstaller --noconfirm --clean --onefile --windowed `
  --name VMRX-Node-Miner --icon assets/vmrx-draft.ico --add-data 'assets;assets' app.py
$sha = (Get-FileHash 'dist/VMRX-Node-Miner.exe' -Algorithm SHA256).Hash.ToLowerInvariant()
"$sha  VMRX-Node-Miner.exe" | Set-Content 'dist/VMRX-Node-Miner.sha256' -Encoding ascii
Write-Host 'GUI preview built. Core daemon is NOT included.'
