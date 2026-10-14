# EldenRing_TR_Baslat.exe için çok boyutlu ikon (256/48/32/16, PNG gömülü ICO) üretir.
Add-Type -AssemblyName System.Drawing
$cikti = Join-Path $PSScriptRoot "ikon.ico"
$boyutlar = 256, 48, 32, 16
$pngler = @()
foreach ($s in $boyutlar) {
    $bmp = New-Object System.Drawing.Bitmap $s, $s
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = 'AntiAlias'; $g.TextRenderingHint = 'AntiAliasGridFit'
    $g.Clear([System.Drawing.Color]::Transparent)
    # Koyu zemin daire
    $zemin = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 24, 20, 14))
    $g.FillEllipse($zemin, 0, 0, $s - 1, $s - 1)
    # Altın halka
    $kalin = [Math]::Max(1.5, $s * 0.07)
    $altin = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(255, 214, 172, 82)), $kalin
    $p = $kalin / 2 + $s * 0.03
    $g.DrawEllipse($altin, $p, $p, $s - 2 * $p - 1, $s - 2 * $p - 1)
    # "TR" yazısı
    $font = New-Object System.Drawing.Font "Georgia", ($s * 0.36), ([System.Drawing.FontStyle]::Bold), ([System.Drawing.GraphicsUnit]::Pixel)
    $fmt = New-Object System.Drawing.StringFormat; $fmt.Alignment = 'Center'; $fmt.LineAlignment = 'Center'
    $yazi = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 240, 214, 140))
    $g.DrawString("TR", $font, $yazi, (New-Object System.Drawing.RectangleF 0, ($s * 0.02), $s, $s), $fmt)
    $g.Dispose()
    $ms = New-Object System.IO.MemoryStream
    $bmp.Save($ms, [System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
    $pngler += , $ms.ToArray()
}
$fs = [System.IO.File]::Create($cikti); $w = New-Object System.IO.BinaryWriter $fs
$w.Write([UInt16]0); $w.Write([UInt16]1); $w.Write([UInt16]$boyutlar.Count)
$ofset = 6 + 16 * $boyutlar.Count
for ($i = 0; $i -lt $boyutlar.Count; $i++) {
    $s = $boyutlar[$i]; $b = if ($s -ge 256) { 0 } else { $s }
    $w.Write([byte]$b); $w.Write([byte]$b); $w.Write([byte]0); $w.Write([byte]0)
    $w.Write([UInt16]1); $w.Write([UInt16]32)
    $w.Write([UInt32]$pngler[$i].Length); $w.Write([UInt32]$ofset)
    $ofset += $pngler[$i].Length
}
foreach ($d in $pngler) { $w.Write($d) }
$w.Close()
# Önizleme
$on = New-Object System.IO.MemoryStream (, $pngler[0]); [System.Drawing.Image]::FromStream($on).Save((Join-Path $PSScriptRoot "ikon_onizleme.png"))
"ikon: $cikti"
