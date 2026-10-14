# GFX fontlarinda Turkce harflerin olup olmadigini kontrol eder.
import struct, glob, os, zlib

TR = "ıİşŞğĞçÇöÖüÜ"


def tags(data):
    if data[:3] == b"CFX":
        data = data[:8] + zlib.decompress(data[8:])
    nbits = data[8] >> 3
    p = 8 + (5 + nbits * 4 + 7) // 8 + 4
    while p < len(data):
        code, = struct.unpack_from("<H", data, p); p += 2
        t, ln = code >> 6, code & 0x3F
        if ln == 0x3F:
            ln, = struct.unpack_from("<I", data, p); p += 4
        yield t, data[p:p + ln]
        p += ln
        if t == 0:
            break


def codes_of(t, body):
    if t in (48, 75):  # DefineFont2/3
        flags = body[2]
        wide_off, wide_codes = flags & 0x08, flags & 0x04
        name_len = body[4]
        p = 5 + name_len
        n, = struct.unpack_from("<H", body, p); p += 2
        if wide_off:
            offs = struct.unpack_from(f"<{n}I", body, p); code_off, = struct.unpack_from("<I", body, p + 4 * n)
        else:
            offs = struct.unpack_from(f"<{n}H", body, p); code_off, = struct.unpack_from("<H", body, p + 2 * n)
        p2 = p + code_off
        return set(struct.unpack_from(f"<{n}H", body, p2)) if wide_codes else set(body[p2:p2 + n])
    return None


for f in sorted(glob.glob(r"D:\Projeler\EldenRingTR\orijinal\font\*\font.gfx")):
    name = os.path.basename(os.path.dirname(f))
    data = open(f, "rb").read()
    seen = {}
    allcodes = set()
    for t, body in tags(data):
        seen[t] = seen.get(t, 0) + 1
        try:
            c = codes_of(t, body)
        except Exception:
            c = None
        if c:
            allcodes |= c
    missing = "".join(ch for ch in TR if ord(ch) not in allcodes)
    # Tag 1005 (DefineCompactedFont) icin kaba arama: UTF-16 kodlar
    raw_hits = "".join(ch for ch in TR if struct.pack("<H", ord(ch)) in data)
    print(f"{name:20} taglar={seen} glif={len(allcodes)} eksik_TR='{missing}' ham_bulunan='{raw_hits}'")
