$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')
python -m unittest discover -s tests -v
@'
from PIL import Image
from pathlib import Path
source = Path("assets/vmrx-logo.png")
if not source.exists():
    raise SystemExit("Official VMRX logo missing: assets/vmrx-logo.png")
image = Image.open(source).convert("RGBA")
image.save("assets/vmrx.ico", format="ICO", sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
'@ | python -
if ($LASTEXITCODE -ne 0) { throw 'Icon generation failed' }
python -m PyInstaller --noconfirm --clean --onefile --windowed `
  --name VMRX-Node-Miner --icon assets/vmrx.ico --add-data 'assets;assets' app.py
$sha = (Get-FileHash 'dist/VMRX-Node-Miner.exe' -Algorithm SHA256).Hash.ToLowerInvariant()
"$sha  VMRX-Node-Miner.exe" | Set-Content 'dist/VMRX-Node-Miner.sha256' -Encoding ascii
Write-Host 'VMRX GUI build completed. Windows VMRX Core daemon is NOT included.'
