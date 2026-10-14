# Yeni fonttan ornek yazi cizip PNG kaydeder (cift-tek dolgu ile).
import sys
from PIL import Image, ImageDraw, ImageChops
from gfxfont import split_tags, Font3, parse_shape
from tr_font import flatten

path = sys.argv[1]
text = sys.argv[2] if len(sys.argv) > 2 else "Işık İzmir şeker Şahin ğüç Ğ çöü ÇÖÜ ıiİI"
out = sys.argv[3] if len(sys.argv) > 3 else r"D:\Projeler\EldenRingTR\onizleme.png"
hdr, tags = split_tags(open(path, "rb").read())
f = Font3(next(t[1] for t in tags if t[0] == 75))
S = 0.006
img = Image.new("L", (1800, 260), 0)
x0 = 20
for ch in text:
    if ch == " ":
        x0 += 4000 * S; continue
    i = f.codes.index(ord(ch))
    glyph = Image.new("L", img.size, 0)
    for c in parse_shape(f.shapes[i])["contours"]:
        layer = Image.new("L", img.size, 0)
        pts = [(x0 + x * S, 160 + y * S) for x, y in flatten(c)]
        ImageDraw.Draw(layer).polygon(pts, fill=255)
        glyph = ImageChops.logical_xor(glyph.convert("1"), layer.convert("1")).convert("L")
    img = ImageChops.lighter(img, glyph)
    x0 += f.adv[i] * S
ImageChops.invert(img).save(out)
print("kaydedildi", out)
