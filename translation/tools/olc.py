# Cevrilecek metin miktarini olcer.
import glob, os, re
import xml.etree.ElementTree as ET

ROOT = r"D:\Projeler\EldenRingTR\acik\msg\engus"
rows, uniq_all = [], set()
for path in sorted(glob.glob(os.path.join(ROOT, "*dlc02-msgbnd-dcx", "**", "*.fmg.xml"), recursive=True)):
    texts = [t.text or "" for t in ET.parse(path).getroot().iter("text")]
    texts = [t for t in texts if t.strip() and t != "%null%"]
    u = set(texts)
    new = u - uniq_all
    uniq_all |= u
    words = sum(len(re.findall(r"\w+", t)) for t in new)
    rows.append((os.path.basename(path)[:-8], len(texts), len(new), words))

rows.sort(key=lambda r: -r[3])
for r in rows:
    if r[3]:
        print(f"{r[0]:40} giris={r[1]:6} yeni_benzersiz={r[2]:6} kelime={r[3]:7}")
print("TOPLAM benzersiz:", len(uniq_all), "kelime:", sum(r[3] for r in rows),
      "karakter:", sum(len(t) for t in uniq_all))
