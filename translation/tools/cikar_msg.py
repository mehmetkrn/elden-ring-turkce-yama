# Elden Ring Data*.bhd/bdt icinden verilen onekteki dosyalari cikarir (varsayilan /msg/engus; oyun dosyalarina yazmaz).
import struct, sys, os
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES

GAME = r"E:\SteamLibrary\steamapps\common\ELDEN RING\Game"
KEYS = r"D:\Projeler\EldenRingTR\araclar\Nuxe\Nuxe 1.2.1\res\BinderKeys\EldenRing_PC"
OUT = r"D:\Projeler\EldenRingTR\orijinal"


def rsa_decrypt(data, pem):
    key = RSA.import_key(pem)
    n, e = key.n, key.e
    ks = (n.bit_length() + 7) // 8
    out = bytearray()
    for i in range(0, len(data), ks):
        c = int.from_bytes(data[i:i + ks], "big")
        out += pow(c, e, n).to_bytes(ks - 1, "big")
    return bytes(out)


def er_hash(path):
    h = 0
    for ch in path.lower().replace("\\", "/"):
        h = (h * 0x85 + ord(ch)) & 0xFFFFFFFFFFFFFFFF
    return h


def main(archive="Data0", prefix="/msg/engus/"):
    raw = open(os.path.join(GAME, archive + ".bhd"), "rb").read()
    if raw[:4] != b"BHD5":
        raw = rsa_decrypt(raw, open(os.path.join(KEYS, "Key", archive + ".pem")).read())
    assert raw[:4] == b"BHD5", "BHD cozulemedi"
    bucket_count, buckets_off = struct.unpack_from("<ii", raw, 0x10)
    entries = {}
    for b in range(bucket_count):
        cnt, off = struct.unpack_from("<ii", raw, buckets_off + b * 8)
        for f in range(cnt):
            p = off + f * 0x28
            h, padded, unpadded, foff, sha_off, aes_off = struct.unpack_from("<QiiqqQ", raw, p)
            entries[h] = (padded, unpadded, foff, aes_off)

    names = [l.strip() for l in open(os.path.join(KEYS, "Hash", archive + ".txt"), encoding="utf-8")
             if l.strip().startswith(prefix)]
    bdt = open(os.path.join(GAME, archive + ".bdt"), "rb")
    os.makedirs(OUT, exist_ok=True)
    for name in names:
        e = entries.get(er_hash(name))
        if not e:
            print("YOK:", name); continue
        padded, unpadded, foff, aes_off = e
        bdt.seek(foff)
        data = bytearray(bdt.read(padded))
        if aes_off:
            key = raw[aes_off:aes_off + 16]
            rc = struct.unpack_from("<i", raw, aes_off + 16)[0]
            aes = AES.new(key, AES.MODE_ECB)
            for r in range(rc):
                s, t = struct.unpack_from("<qq", raw, aes_off + 20 + r * 16)
                if s == -1 or t == -1 or s == t:
                    continue
                data[s:t] = aes.decrypt(bytes(data[s:t]))
        size = unpadded if unpadded > 0 else padded
        dst = os.path.join(OUT, name.lstrip("/").replace("/", os.sep))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        open(dst, "wb").write(data[:size])
        print("OK", name, size, bytes(data[:4]))


if __name__ == "__main__":
    main(*sys.argv[1:])
