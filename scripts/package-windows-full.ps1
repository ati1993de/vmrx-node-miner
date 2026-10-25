# Package a fully native Windows GUI + VMRX Core without downloading unverified binaries.
# Input archives and signed-off SHA256SUMS must already be staged in incoming/gui & incoming/core.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $root

function Verify-Archive([string]$folder, [string]$archiveName) {
    $archive = Join-Path $folder $archiveName
    $sumFile = Join-Path $folder 'SHA256SUMS'
    if (-not (Test-Path $archive -PathType Leaf) -or -not (Test-Path $sumFile -PathType Leaf)) {
        throw "Missing archive or SHA256SUMS: $folder/$archiveName"
    }
    $lines = Get-Content $sumFile
    $expected = $null
    foreach ($line in $lines) {
        if ($line -match '^([a-fA-F0-9]{64})\s+\*?(.+)$' -and $Matches[2].Trim() -eq $archiveName) {
            $expected = $Matches[1].ToLowerInvariant()
        }
    }
    if (-not $expected) { throw "No SHA256 entry for $archiveName" }
    $actual = (Get-FileHash $archive -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $expected) { throw "SHA256 mismatch: $archiveName" }
    Write-Host "PASS: $archiveName SHA256 verified"
    return $archive
}

$guiArchive = Verify-Archive 'incoming/gui' 'VMRX-Node-Miner-windows-x64.zip'
$coreArchives = @(Get-ChildItem -Path 'incoming/core' -Filter 'VMRX-Core-windows-x86_64-*.zip' -File)
if ($coreArchives.Count -ne 1) { throw "Expected exactly one native Windows Core release archive, found $($coreArchives.Count)" }
$coreArchive = Verify-Archive 'incoming/core' $coreArchives[0].Name

$work = Join-Path $root 'bundle-work'
if (Test-Path $work) { Remove-Item -Recurse -Force $work }
New-Item -ItemType Directory -Force (Join-Path $work 'gui'), (Join-Path $work 'core-unpack'), (Join-Path $work 'VMRX-Windows-Full/core') | Out-Null
Expand-Archive $guiArchive (Join-Path $work 'gui')
Expand-Archive $coreArchive (Join-Path $work 'core-unpack')

$guiExecutables = @(Get-ChildItem (Join-Path $work 'gui') -Recurse -File -Filter 'VMRX-Node-Miner.exe')
$coreExecutables = @(Get-ChildItem (Join-Path $work 'core-unpack') -Recurse -File -Filter 'vmrxd.exe')
if ($guiExecutables.Count -ne 1 -or $coreExecutables.Count -ne 1) {
    throw "Expected exactly one GUI exe and exactly one native Windows VMRX daemon"
}
$destination = Join-Path $work 'VMRX-Windows-Full'
Copy-Item $guiExecutables[0].FullName (Join-Path $destination 'VMRX-Node-Miner.exe')
# Copy daemon DLLs from the validated Core package together with vmrxd.exe.
$coreBin = $coreExecutables[0].Directory.FullName
Copy-Item (Join-Path $coreBin '*') (Join-Path $destination 'core') -Recurse -Force

if (-not (Test-Path (Join-Path $destination 'core/vmrxd.exe'))) {
    throw "No core/vmrxd.exe in bundled release"
}
Copy-Item 'LICENSE-DECISION.md' (Join-Path $destination 'GUI-LICENSE-NOTES.md')
@'
VMRX Node & Miner v0.1.2 — Windows full bundle

1. Run VMRX-Node-Miner.exe on Windows 10/11 x64.
2. In Node Control, the bundled core/vmrxd.exe is preselected.
3. Confirm the node data directory and use a verified VMRX peer.
4. Click Start local node; wait for blockchain synchronization.
5. Check P2P peers and the mainnet tip, then enter an independently verified address before enabling CPU mining.

Local unrestricted RPC is available ONLY at 127.0.0.1:29781.
This controller is NOT a full wallet; no seed entry / funds management.
Mining uses CPU resources and electricity. Do not reuse Monero or VMESH databases.
The 200,000 VMRX founder premine and other network caveats are documented
in the VMRX Core repository. No independent security audit is claimed.
'@ | Set-Content -Encoding utf8 (Join-Path $destination 'README-WINDOWS.txt')

# Require native daemon to start on Windows and expose correct VMRX genesis.
$testDir = Join-Path $work 'genesis-smoke'
New-Item -ItemType Directory -Force $testDir | Out-Null
$daemon = Join-Path $destination 'core/vmrxd.exe'
$argsList = @('--non-interactive', '--offline', '--data-dir', "`"$testDir`"",
  '--p2p-bind-ip', '127.0.0.1', '--p2p-bind-port', '29780',
  '--rpc-bind-ip', '127.0.0.1', '--rpc-bind-port', '29781',
  '--no-zmq', '--no-igd', '--disable-dns-checkpoints', '--check-updates', 'disabled')
$p = Start-Process -FilePath $daemon -ArgumentList $argsList -WorkingDirectory (Split-Path $daemon) -PassThru -WindowStyle Hidden
try {
    $info = $null
    for ($i = 0; $i -lt 45; $i++) {
        Start-Sleep 2
        if ($p.HasExited) { throw "Bundled Windows Core exited with code $($p.ExitCode)" }
        try { $info = Invoke-RestMethod 'http://127.0.0.1:29781/get_info' -TimeoutSec 3; if ($info.height -ge 1) { break } } catch {}
    }
    if (-not $info -or $info.height -lt 1) { throw 'Bundled Windows node failed to start' }
    $body = @{ jsonrpc = '2.0'; id = '0'; method = 'get_block_header_by_height'; params = @{ height = 0 } } | ConvertTo-Json -Depth 5
    $result = Invoke-RestMethod 'http://127.0.0.1:29781/json_rpc' -Method POST -ContentType 'application/json' -Body $body
    $expected = '405baab8805904ffb7d3643a5004c43b45fc3f5f4c97e712ba4c078a384139d4'
    if ($result.result.block_header.hash -ne $expected) { throw "Windows Core genesis mismatch" }
    Write-Host "PASS: Packaged Windows VMRX Core started, correct genesis $expected"
} finally {
    if (-not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
}

New-Item -ItemType Directory -Force 'full-release' | Out-Null
Compress-Archive (Join-Path $destination '*') 'full-release/VMRX-Full-Node-Miner-windows-x64.zip' -CompressionLevel Optimal -Force
$sha = (Get-FileHash 'full-release/VMRX-Full-Node-Miner-windows-x64.zip' -Algorithm SHA256).Hash.ToLowerInvariant()
"$sha  VMRX-Full-Node-Miner-windows-x64.zip" | Set-Content 'full-release/SHA256SUMS' -Encoding ascii
Write-Host "PASS: Full Windows GUI + Core package generated"
