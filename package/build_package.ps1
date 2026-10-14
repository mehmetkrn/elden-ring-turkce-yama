# Assembles the release zip (EldenRing_TR_Yama.zip) exactly as uploaded to Nexus Mods.
#
#   powershell -ExecutionPolicy Bypass -File package\build_package.ps1 -Yama <folder containing msg\ and font\>
#
# -Yama : the generated Turkish data (msg\engus\*.msgbnd.dcx, font\eu_std|eu_map\font.gfx).
#         These files are produced by translation\tools from YOUR OWN copy of the game
#         (see README "Building the translation data"); they are not stored in this repository.
#
# me3 is NOT built here: the official, unmodified me3 v0.9.0 release is downloaded from
# github.com/garyttierney/me3 and every file is checked against the SHA256 values below.
param([Parameter(Mandatory)][string]$Yama)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$dist = Join-Path $root 'dist'
$out  = Join-Path $dist 'EldenRing_TR'

$ME3_URL = 'https://github.com/garyttierney/me3/releases/download/v0.9.0/me3-windows-amd64.zip'
$ME3_SHA = @{
    'me3.exe'          = '4cab339a804b4fd55f233693f9dde019a5caec980cc6c859c50e8d16205e486f'
    'me3-launcher.exe' = '65a64d3ae5a0c51f43481b48807df5a9cad21705fcb7f6e430de3d1d09c1f84b'
    'me3_mod_host.dll' = '44139dc0c1184a5589066f70af793b38ff6654b19254f6bd1a601c17b6fe84e4'
}

# 1) Launcher
& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root 'launcher\build.ps1')

# 2) Official me3
$tmp = Join-Path $dist 'me3_official'
Invoke-WebRequest $ME3_URL -OutFile "$tmp.zip" -UseBasicParsing
Expand-Archive "$tmp.zip" $tmp -Force
foreach ($f in $ME3_SHA.Keys) {
    $h = (Get-FileHash (Join-Path $tmp "bin\$f") -Algorithm SHA256).Hash.ToLower()
    if ($h -ne $ME3_SHA[$f]) { throw "me3 hash mismatch: $f" }
}

# 3) Assemble
if (Test-Path $out) { Remove-Item $out -Recurse -Force }
New-Item -ItemType Directory -Force "$out\me3\bin", "$out\yama" | Out-Null
Copy-Item "$tmp\bin\*" "$out\me3\bin\"
Copy-Item "$tmp\LICENSE-MIT" "$out\me3\LICENSE-MIT.txt"
Copy-Item "$tmp\LICENSE-APACHE" "$out\me3\LICENSE-APACHE.txt"
Copy-Item (Join-Path $Yama 'msg'), (Join-Path $Yama 'font') "$out\yama\" -Recurse
Copy-Item "$PSScriptRoot\EldenRing_TR.me3", "$PSScriptRoot\OKU_BENI_KURULUM.txt" $out
Copy-Item "$dist\EldenRing_TR_Baslat.exe" $out

# 4) Zip
$zip = Join-Path $dist 'EldenRing_TR_Yama.zip'
if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path $out -DestinationPath $zip
Write-Host "Built $zip"
