# Cevrilecek benzersiz metinleri oncelik sirasina gore numaralandirip parcalara boler.
# Cikti: is\metinler.json (id -> ingilizce), is\parcalar.json (parca listesi)
import glob, os, re, json
import xml.etree.ElementTree as ET

ROOT = r"D:\Projeler\EldenRingTR\acik\msg\engus"
IS = r"D:\Projeler\EldenRingTR\is"

ATLA = {"ToS_win64"}
ONCELIK = [
    ("isimler", r"(Place|Npc|Weapon|Protector|Accessory|Goods|Gem|Arts|Magic)Name"),
    ("menu", r"GR_|ActionButton|EventText|Loading|Tutorial|Network|GoodsDialog|TextEmbed|MovieSub|Info|Effect"),
    ("aciklama", r"Caption"),
    ("diyalog", r"TalkMsg"),
    ("mesaj", r"BloodMsg"),
]
AFINITE = ["Heavy", "Keen", "Quality", "Fire", "Flame Art", "Lightning", "Sacred", "Magic", "Cold",
           "Poison", "Blood", "Occult"]
PARCA_KELIME ={"isimler": 1500, "menu": 2000, "aciklama": 2200, "diyalog": 2200, "mesaj": 2500}


def grup(fmg):
    base = re.sub(r"_dlc0\d$", "", fmg)
    for ad, rx in ONCELIK:
        if re.search(rx, base):
            return ad
    return "menu"


def main():
    gorulen, liste = {}, []
    for path in sorted(glob.glob(os.path.join(ROOT, "*dlc02-msgbnd-dcx", "**", "*.fmg.xml"), recursive=True)):
        fmg = os.path.basename(path)[:-8]
        if re.sub(r"_dlc0\d$", "", fmg) in ATLA:
            continue
        g = grup(fmg)
        for t in ET.parse(path).getroot().iter("text"):
            s = t.text or ""
            if not s.strip() or s == "%null%" or s.startswith("[ERROR]"):
                continue
            if not re.search(r"[A-Za-z]", s):
                continue
            if s not in gorulen:
                gorulen[s] = (g, fmg)
                liste.append(s)
    # Baska bir metinden otomatik turetilebilenler (cevirisi uygula.py'de uretilir)
    kume = set(liste)
    turetilen = {}
    for s in liste:
        m = re.match(r"^(.*) \+(\d+)$", s)
        if m and m.group(1) in kume:
            turetilen[s] = ["arti", m.group(1), m.group(2)]; continue
        m = re.match(r"^Ash(?:es)? of War: (.*)$", s)
        if m and m.group(1) in kume:
            turetilen[s] = ["kul" if s.startswith("Ash of") else "kuller", m.group(1)]; continue
        if gorulen[s][1].startswith("WeaponName"):
            # Afinite kelimesi basta ya da ortada olabilir: "Heavy Dagger", "Lordsworn's Heavy Straight Sword"
            for m in re.finditer(r"(?:^| )(%s)(?= )" % "|".join(AFINITE), s):
                taban = (s[:m.start()] + s[m.end():]).strip()
                if taban in kume:
                    turetilen[s] = ["afinite", taban, m.group(1)]
                    break
    liste = [s for s in liste if s not in turetilen]
    json.dump(turetilen, open(os.path.join(IS, "turetilen.json"), "w", encoding="utf-8"), ensure_ascii=False)
    sira = {ad: i for i, (ad, _) in enumerate(ONCELIK)}
    liste.sort(key=lambda s: (sira[gorulen[s][0]], gorulen[s][1]))
    metinler, parcalar = {}, []
    cur, cur_w, cur_g = [], 0, None
    for i, s in enumerate(liste, 1):
        g = gorulen[s][0]
        w = len(re.findall(r"\w+", s))
        if cur and (g != cur_g or cur_w + w > PARCA_KELIME[g]):
            parcalar.append({"grup": cur_g, "idler": cur})
            cur, cur_w = [], 0
        cur_g = g
        metinler[str(i)] = s
        cur.append(str(i))
        cur_w += w
    if cur:
        parcalar.append({"grup": cur_g, "idler": cur})
    os.makedirs(os.path.join(IS, "ceviri"), exist_ok=True)
    json.dump(metinler, open(os.path.join(IS, "metinler.json"), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(parcalar, open(os.path.join(IS, "parcalar.json"), "w", encoding="utf-8"), ensure_ascii=False)
    from collections import Counter
    print("metin:", len(metinler), "parca:", len(parcalar), Counter(p["grup"] for p in parcalar))


if __name__ == "__main__":
    main()
