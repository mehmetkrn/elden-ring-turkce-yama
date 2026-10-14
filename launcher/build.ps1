# Builds EldenRing_TR_Baslat.exe from Baslat.cs using the C# compiler that ships with Windows (.NET Framework 4.x).
# No SDK or third-party tools needed.  Usage:  powershell -ExecutionPolicy Bypass -File launcher\build.ps1
$ErrorActionPreference = 'Stop'
$here = $PSScriptRoot
$dist = Join-Path (Split-Path $here -Parent) 'dist'
New-Item -ItemType Directory -Force $dist | Out-Null

# 1) Icon (drawn with System.Drawing, no external image files)
& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $here 'ikon_yap.ps1')

# 2) Compile
$csc = Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
& $csc /nologo /target:winexe /codepage:65001 /optimize `
    /win32icon:"$here\ikon.ico" /r:System.Windows.Forms.dll `
    /out:"$dist\EldenRing_TR_Baslat.exe" "$here\Baslat.cs"
if ($LASTEXITCODE -ne 0) { throw "csc failed" }
Get-FileHash "$dist\EldenRing_TR_Baslat.exe" -Algorithm SHA256 | Format-List Path, Hash
