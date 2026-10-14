# eu_std ve eu_map fontlarina ı İ ş Ş ğ Ğ gliflerini ekler; yama klasorune yazar.
import os
from gfxfont import (split_tags, join_tags, Font3, parse_shape, encode_shape,
                     contour_bbox, shifted)

SRC = r"D:\Projeler\EldenRingTR\orijinal\font"
DST = r"D:\Projeler\EldenRingTR\TR_Yama\Game\kaynaklar\me3\config\eldenring-mods\font"


def flatten(c, steps=8):
    """Konturu cokgene cevirir (egriler dogru parcalarina bolunur)."""
    x, y = c["x"], c["y"]
    pts = [(x, y)]
    for e in c["edges"]:
        if e[0] == "L":
            x, y = x + e[1], y + e[2]
            pts.append((x, y))
        else:
            cx, cy = x + e[1], y + e[2]
            ax, ay = cx + e[3], cy + e[4]
            for k in range(1, steps + 1):
                t = k / steps
                pts.append(((1 - t) ** 2 * x + 2 * (1 - t) * t * cx + t * t * ax,
                            (1 - t) ** 2 * y + 2 * (1 - t) * t * cy + t * t * ay))
            x, y = ax, ay
    return pts


def clip_below(pts, cut):
    """Cokgenin y >= cut (taban cizgisinin alti) kismini birakir."""
    out = []
    n = len(pts)
    for i in range(n):
        p, q = pts[i], pts[(i + 1) % n]
        pin, qin = p[1] >= cut, q[1] >= cut
        if pin:
            out.append(p)
        if pin != qin:
            t = (cut - p[1]) / (q[1] - p[1])
            out.append((p[0] + t * (q[0] - p[0]), cut))
    return out


def poly_contour(pts, f0, f1):
    pts = [(round(x), round(y)) for x, y in pts]
    pts = [p for i, p in enumerate(pts) if i == 0 or p != pts[i - 1]]
    if pts[0] != pts[-1]:
        pts.append(pts[0])
    edges = [("L", b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])]
    return {"x": pts[0][0], "y": pts[0][1], "f0": f0, "f1": f1, "edges": edges}


def cx(b):
    return (b[0] + b[2]) / 2


def scaled(c, s):
    edges = [tuple([e[0]] + [round(v * s) for v in e[1:]]) for e in c["edges"]]
    return {**c, "x": round(c["x"] * s), "y": round(c["y"] * s), "edges": edges}


def build(font, donor):
    def shape(ch):
        return parse_shape(font.shapes[font.index(ch)])

    def add(ch, base, contours):
        sh = shape(base)
        sh["contours"] = contours
        font.add(ord(ch), encode_shape(sh), font.adv[font.index(base)], [0, 0, 0, 0])
        # Kerning: taban harfin ciftlerini kopyala
        bc = ord(base)
        for a, b, v in list(font.kern):
            if a == bc:
                font.kern.append((ord(ch), b, v))
            if b == bc:
                font.kern.append((a, ord(ch), v))

    # ı: i'nin noktasi (en ustteki kontur) cikarilir
    i_sh = shape("i")
    stem = max(i_sh["contours"], key=lambda c: contour_bbox(c)[3])
    dot = min(i_sh["contours"], key=lambda c: contour_bbox(c)[1])
    add("ı", "i", [stem])

    # İ: I + i'nin noktasi, buyuk harf yuksekligine tasinir
    I_sh = shape("I")
    Ib = contour_bbox(I_sh["contours"][0])
    db = contour_bbox(dot)
    gap = contour_bbox(stem)[1] - db[3]  # i'de nokta ile govde arasi bosluk
    dy = (Ib[1] - gap) - db[3]
    dx = cx(Ib) - cx(db)
    add("İ", "I", I_sh["contours"] + [shifted(dot, round(dx), round(dy))])

    # ş / Ş: s / S + ç / Ç'nin cengeli
    for low, ced_src, base in (("ş", "ç", "s"), ("Ş", "Ç", "S")):
        src = shape(ced_src)
        c = src["contours"][0]
        bowl_bottom = max(contour_bbox(k)[3] for k in shape("c" if base == "s" else "C")["contours"])
        cut = bowl_bottom + 250
        hook = poly_contour(clip_below(flatten(c), cut), c["f0"], c["f1"])
        bsh = shape(base)
        bb = contour_bbox(bsh["contours"][0])
        hb = contour_bbox(hook)
        src_b = contour_bbox(c)
        # cengelin ç icindeki yatay konumu harf merkezine gore korunur
        off = cx(hb) - cx(src_b)
        dx = cx(bb) + off * (bb[2] - bb[0]) / (src_b[2] - src_b[0]) - cx(hb)
        dy = (bb[3] + 120) - hb[1]  # harfin altina kucuk bosluk
        add(low, base, bsh["contours"] + [shifted(hook, round(dx), round(dy))])

    # ğ / Ğ: g / G + й / Й'nin kavisli isareti (fontta й bossa donor fonttan olceklenir)
    for ch, base, src_ch, ref in (("ğ", "g", "й", "o"), ("Ğ", "G", "Й", "O")):
        src, scale = shape(src_ch), 1.0
        if not src["contours"]:
            src = parse_shape(donor.shapes[donor.index(src_ch)])
            ref_h = lambda fnt: -contour_bbox(parse_shape(fnt.shapes[fnt.index(ref)])["contours"][0])[1]
            scale = ref_h(font) / ref_h(donor)
            src["contours"] = [scaled(c, scale) for c in src["contours"]]
        breve = min(src["contours"], key=lambda c: contour_bbox(c)[1])
        body_top = min(contour_bbox(c)[1] for c in src["contours"] if c is not breve)
        gap = body_top - contour_bbox(breve)[3]
        bsh = shape(base)
        top = contour_bbox(shape(ref)["contours"][0])[1]  # x-yuksekligi / buyuk harf yuksekligi
        if base == "g" and len(bsh["contours"]) > 1:
            # g'de ust govdenin (ic bosluk) merkezi
            center = cx(min((contour_bbox(c) for c in bsh["contours"][1:]), key=lambda b: b[1]))
        else:
            center = cx(contour_bbox(bsh["contours"][0]))
        brb = contour_bbox(breve)
        dx = center - cx(brb)
        dy = (top - gap) - brb[3]
        add(ch, base, bsh["contours"] + [shifted(breve, round(dx), round(dy))])


def main():
    std = open(os.path.join(SRC, "eu_std", "font.gfx"), "rb").read()
    donor = Font3(next(t[1] for t in split_tags(std)[1] if t[0] == 75))
    for name in ("eu_std", "eu_map"):
        data = open(os.path.join(SRC, name, "font.gfx"), "rb").read()
        hdr, tags = split_tags(data)
        for t in tags:
            if t[0] == 75:
                f = Font3(t[1])
                build(f, donor)
                t[1] = f.build()
                t[2] = True
        out = os.path.join(DST, name)
        os.makedirs(out, exist_ok=True)
        open(os.path.join(out, "font.gfx"), "wb").write(join_tags(hdr, tags))
        print("yazildi", name)


if __name__ == "__main__":
    main()
