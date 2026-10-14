# Scaleform GFX icindeki DefineFont3 (tag 75) okuyucu/yazici.
# Glif sekilleri kontur listesi olarak tutulur; Turkce harfler mevcut gliflerden turetilir.
import struct


class BitReader:
    def __init__(self, data, pos=0):
        self.d, self.byte, self.bit = data, pos, 0

    def ub(self, n):
        v = 0
        for _ in range(n):
            b = (self.d[self.byte] >> (7 - self.bit)) & 1
            v = (v << 1) | b
            self.bit += 1
            if self.bit == 8:
                self.bit, self.byte = 0, self.byte + 1
        return v

    def sb(self, n):
        if n == 0:
            return 0
        v = self.ub(n)
        return v - (1 << n) if v & (1 << (n - 1)) else v

    def align(self):
        if self.bit:
            self.bit, self.byte = 0, self.byte + 1


class BitWriter:
    def __init__(self):
        self.out, self.cur, self.n = bytearray(), 0, 0

    def ub(self, n, v):
        for i in range(n - 1, -1, -1):
            self.cur = (self.cur << 1) | ((v >> i) & 1)
            self.n += 1
            if self.n == 8:
                self.out.append(self.cur)
                self.cur, self.n = 0, 0

    def sb(self, n, v):
        self.ub(n, v & ((1 << n) - 1))

    def align(self):
        if self.n:
            self.out.append(self.cur << (8 - self.n))
            self.cur, self.n = 0, 0
        return bytes(self.out)


def sbits(*vals):
    n = 1
    for v in vals:
        while not (-(1 << (n - 1)) <= v < (1 << (n - 1))):
            n += 1
    return n


# Kontur: {"x","y" (mutlak baslangic), "f0","f1" (dolgu stili), "edges": [("L",dx,dy) | ("C",cx,cy,ax,ay)]}
def parse_shape(data):
    br = BitReader(data)
    nfill, nline = br.ub(4), br.ub(4)
    contours, cur = [], None
    f0 = f1 = 0
    x = y = 0
    while True:
        if br.ub(1) == 0:
            flags = br.ub(5)
            if flags == 0:
                break
            new_styles, line_s, fs1, fs0, move = [(flags >> i) & 1 for i in (4, 3, 2, 1, 0)]
            if move:
                nb = br.ub(5)
                x, y = br.sb(nb), br.sb(nb)
            if fs0:
                f0 = br.ub(nfill)
            if fs1:
                f1 = br.ub(nfill)
            if line_s:
                br.ub(nline)
            assert not new_styles, "glifte yeni stil beklenmez"
            cur = {"x": x, "y": y, "f0": f0, "f1": f1, "edges": []}
            contours.append(cur)
        else:
            if br.ub(1):
                nb = br.ub(4) + 2
                if br.ub(1):
                    dx, dy = br.sb(nb), br.sb(nb)
                elif br.ub(1):
                    dx, dy = 0, br.sb(nb)
                else:
                    dx, dy = br.sb(nb), 0
                cur["edges"].append(("L", dx, dy))
            else:
                nb = br.ub(4) + 2
                cur["edges"].append(("C", br.sb(nb), br.sb(nb), br.sb(nb), br.sb(nb)))
    return {"nfill": nfill, "nline": nline, "contours": contours}


def encode_shape(shape):
    bw = BitWriter()
    nfill, nline = shape["nfill"], shape["nline"]
    bw.ub(4, nfill)
    bw.ub(4, nline)
    f0 = f1 = 0
    for c in shape["contours"]:
        fs0, fs1 = c["f0"] != f0, c["f1"] != f1
        flags = (fs1 << 2) | (fs0 << 1) | 1
        bw.ub(1, 0)
        bw.ub(5, flags)
        nb = sbits(c["x"], c["y"])
        bw.ub(5, nb)
        bw.sb(nb, c["x"])
        bw.sb(nb, c["y"])
        if fs0:
            bw.ub(nfill, c["f0"])
        if fs1:
            bw.ub(nfill, c["f1"])
        f0, f1 = c["f0"], c["f1"]
        for e in c["edges"]:
            bw.ub(1, 1)
            if e[0] == "L":
                _, dx, dy = e
                bw.ub(1, 1)
                if dx and dy:
                    nb = max(sbits(dx, dy), 2)
                    bw.ub(4, nb - 2); bw.ub(1, 1); bw.sb(nb, dx); bw.sb(nb, dy)
                elif dx == 0:
                    nb = max(sbits(dy), 2)
                    bw.ub(4, nb - 2); bw.ub(1, 0); bw.ub(1, 1); bw.sb(nb, dy)
                else:
                    nb = max(sbits(dx), 2)
                    bw.ub(4, nb - 2); bw.ub(1, 0); bw.ub(1, 0); bw.sb(nb, dx)
            else:
                _, cx, cy, ax, ay = e
                nb = max(sbits(cx, cy, ax, ay), 2)
                bw.ub(1, 0); bw.ub(4, nb - 2)
                for v in (cx, cy, ax, ay):
                    bw.sb(nb, v)
    bw.ub(1, 0)
    bw.ub(5, 0)
    return bw.align()


def contour_bbox(c):
    x, y = c["x"], c["y"]
    xs, ys = [x], [y]
    for e in c["edges"]:
        if e[0] == "L":
            x += e[1]; y += e[2]
            xs.append(x); ys.append(y)
        else:
            xs.append(x + e[1]); ys.append(y + e[2])
            x += e[1] + e[3]; y += e[2] + e[4]
            xs.append(x); ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)


def shape_bbox(shape):
    bs = [contour_bbox(c) for c in shape["contours"]]
    if not bs:
        return 0, 0, 0, 0
    return min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs)


def shifted(c, dx, dy):
    return {**c, "x": c["x"] + dx, "y": c["y"] + dy, "edges": list(c["edges"])}


def read_rect(br):
    nb = br.ub(5)
    return [br.sb(nb) for _ in range(4)]  # xmin xmax ymin ymax


def write_rect(bw, r):
    nb = sbits(*r)
    bw.ub(5, nb)
    for v in r:
        bw.sb(nb, v)


class Font3:
    def __init__(self, body):
        self.font_id, self.flags, self.lang = struct.unpack_from("<HBB", body, 0)
        nl = body[4]
        self.name = body[5:5 + nl]
        p = 5 + nl
        n, = struct.unpack_from("<H", body, p); p += 2
        wide = self.flags & 0x08
        assert self.flags & 0x04, "genis kod bekleniyor"
        fmt, sz = ("I", 4) if wide else ("H", 2)
        offs = list(struct.unpack_from(f"<{n}{fmt}", body, p))
        code_off, = struct.unpack_from(f"<{fmt}", body, p + sz * n)
        base = p
        ends = offs[1:] + [code_off]
        self.shapes = [body[base + offs[i]: base + ends[i]] for i in range(n)]
        p = base + code_off
        self.codes = list(struct.unpack_from(f"<{n}H", body, p)); p += 2 * n
        self.layout = bool(self.flags & 0x80)
        assert self.layout
        self.ascent, self.descent, self.leading = struct.unpack_from("<hhh", body, p); p += 6
        self.adv = list(struct.unpack_from(f"<{n}h", body, p)); p += 2 * n
        br = BitReader(body, p)
        self.bounds = []
        for _ in range(n):
            self.bounds.append(read_rect(br)); br.align()
        p = br.byte
        kc, = struct.unpack_from("<H", body, p); p += 2
        self.kern = [struct.unpack_from("<HHh", body, p + 6 * i) for i in range(kc)]
        p += 6 * kc
        self.tail = body[p:]

    def index(self, ch):
        return self.codes.index(ord(ch))

    def add(self, code, shape_bytes, adv, bounds):
        self.codes.append(code); self.shapes.append(shape_bytes)
        self.adv.append(adv); self.bounds.append(bounds)

    def build(self):
        order = sorted(range(len(self.codes)), key=lambda i: self.codes[i])
        codes = [self.codes[i] for i in order]
        shapes = [self.shapes[i] for i in order]
        adv = [self.adv[i] for i in order]
        bounds = [self.bounds[i] for i in order]
        n = len(codes)
        total = sum(len(s) for s in shapes)
        wide = (4 * (n + 1) + total) > 0xFFFF or (self.flags & 0x08)
        flags = (self.flags | 0x08) if wide else self.flags
        fmt, sz = ("I", 4) if wide else ("H", 2)
        offs, o = [], sz * (n + 1)
        for s in shapes:
            offs.append(o); o += len(s)
        out = bytearray(struct.pack("<HBB", self.font_id, flags, self.lang))
        out += bytes([len(self.name)]) + self.name + struct.pack("<H", n)
        out += struct.pack(f"<{n}{fmt}", *offs) + struct.pack(f"<{fmt}", o)
        for s in shapes:
            out += s
        out += struct.pack(f"<{n}H", *codes)
        out += struct.pack("<hhh", self.ascent, self.descent, self.leading)
        out += struct.pack(f"<{n}h", *adv)
        for r in bounds:
            bw = BitWriter(); write_rect(bw, r); out += bw.align()
        kern = sorted(set(self.kern))
        out += struct.pack("<H", len(kern))
        for k in kern:
            out += struct.pack("<HHh", *k)
        out += self.tail
        return bytes(out)


def split_tags(data):
    assert data[:3] == b"GFX"
    nbits = data[8] >> 3
    hdr_end = 8 + (5 + nbits * 4 + 7) // 8 + 4
    tags, p = [], hdr_end
    while p < len(data):
        code, = struct.unpack_from("<H", data, p); p += 2
        t, ln = code >> 6, code & 0x3F
        long_form = ln == 0x3F
        if long_form:
            ln, = struct.unpack_from("<I", data, p); p += 4
        tags.append([t, data[p:p + ln], long_form])
        p += ln
        if t == 0:
            break
    return data[:hdr_end], tags


def join_tags(hdr, tags):
    out = bytearray(hdr)
    for t, body, long_form in tags:
        if len(body) < 0x3F and not long_form:
            out += struct.pack("<H", (t << 6) | len(body))
        else:
            out += struct.pack("<HI", (t << 6) | 0x3F, len(body))
        out += body
    struct.pack_into("<I", out, 4, len(out))
    return bytes(out)
