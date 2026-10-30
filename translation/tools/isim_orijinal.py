# "Orijinal isimler" surumu: esya/boss/yer/buyu adlari Ingilizce kalir.
# Isim FMG'leri cevrilmez; diger metinlerde gecen Turkce isimler Ingilizce asliyla degistirilir,
# arkasindaki ek ('e, 'nin, 'ndan ...) Ingilizce kelimeye gore yeniden uydurulur.
# "python isim_orijinal.py ornek" -> is\isim_ornek.txt
import glob, json, os, re, sys, unicodedata
import xml.etree.ElementTree as ET

ANA = r"D:\Projeler\EldenRingTR"
ISIM_FMG = re.compile(r"^(Place|Npc|Weapon|Protector|Accessory|Goods|Gem|Arts|Magic)Name(_dlc0\d)?$")
# Tek kelimelik Turkce karsiliklar gunluk sozcukle karisir (Mizrak, Isik...); metin icinde yalnizca bunlar degisir.
TEK_KELIME = {"Boynuzlu", "Kristalyan", "Ölümkökü"}


def isim_fmg(fmg):
    return bool(ISIM_FMG.match(fmg))


def isim_haritasi(bul):
    """Turkce isim -> Ingilizce isim (yalnizca tek anlamli olanlar)."""
    kaynak = os.path.join(ANA, "acik", "msg", "engus")
    adaylar = {}
    for x in glob.glob(os.path.join(kaynak, "*-msgbnd-dcx", "**", "*.fmg.xml"), recursive=True):
        if not isim_fmg(os.path.basename(x)[:-8]):
            continue
        for t in ET.parse(x).getroot().iter("text"):
            en = t.text or ""
            if not en.strip() or en == "%null%" or en.startswith("[ERROR]"):
                continue
            tr = bul(en)
            if tr and tr != en and len(tr) > 3 and "\n" not in tr:
                adaylar.setdefault(tr, set()).add(en)
    return {tr: ens.pop() for tr, ens in adaylar.items() if len(ens) == 1}


def _unluler(s):
    return [c for c in s.lower() if c in "aeıioöuü"]


def _son_kelime(en):
    k = unicodedata.normalize("NFD", en.lower().split()[-1])
    return re.sub(r"[^a-z]", "", k)


def _son_unlu(en):
    """Ingilizce kelimenin okunusuna gore son unlu: kalin/ince, duz/yuvarlak."""
    k = _son_kelime(en) or "a"
    if re.search(r"[^aeiou]e$", k) and len(k) > 3:  # Blade, Stone: sessiz e
        k = k[:-1]
    if re.search(r"[^aeiou]ers?$", k):  # Eater, Fingers: okunusu "ır"
        return "a"
    k = k.replace("ea", "e")  # Death, Bear
    for c in reversed(k):
        if c in "aeiou":
            return c
        if c == "y" and k.endswith("y"):
            return "i"
    return "a"


def _unluyle_bitiyor(en):
    k = _son_kelime(en)
    if re.search(r"[^aeiou]e$", k) and len(k) > 3:
        return False
    return bool(k) and k[-1] in "aeiouy"


def _sert_bitiyor(en):
    k = _son_kelime(en)
    if re.search(r"[^aeiou]e$", k) and len(k) > 3:
        k = k[:-1]
    return bool(k) and (k[-1] in "fstkph" or k.endswith("ch") or k.endswith("sh"))


def ek_uydur(en, ek):
    """Turkce isme gore yazilmis eki ('ne, 'nin, 'ndan...) Ingilizce isme gore yeniden yazar."""
    u = _son_unlu(en)
    a = "a" if u in "aou" else "e"
    i = {"a": "ı", "o": "u", "u": "u", "e": "i", "i": "i"}[u]
    unlu = _unluyle_bitiyor(en)
    d = "t" if _sert_bitiyor(en) else "d"
    m = re.match(r"^n?([dt])[ae](n?)(.*)$", ek)  # bulunma / ayrilma: 'de 'nden 'ndaki
    if m:
        return f"{d}{a}{m.group(2)}{m.group(3)}"
    m = re.match(r"^[nsy]?[ıiuü]n(.*)$", ek)  # ilgi: 'nin 'in
    if m:
        return ("n" if unlu else "") + i + "n" + m.group(1)
    m = re.match(r"^l[ae](r.*)$", ek)  # cogul: 'ler 'lerin
    if m:
        kalan = m.group(1)
        return "l" + a + re.sub(r"[ae]", a, re.sub(r"[ıiuü]", "ı" if a == "a" else "i", kalan))
    m = re.match(r"^[ny]?l[ae](.*)$", ek)  # 'yle 'la
    if m:
        return ("y" if unlu else "") + "l" + a + m.group(1)
    m = re.match(r"^[ny]?[ae]$", ek)  # yonelme: 'ne 'ye 'a
    if m:
        return ("y" if unlu else "") + a
    m = re.match(r"^[ny]?[ıiuü]$", ek)  # belirtme: 'ni 'yi 'i
    if m:
        return ("y" if unlu else "") + i
    m = re.match(r"^y?[ıiuü]([mz])$", ek)  # 'yim 'yiz
    if m:
        return ("y" if unlu else "") + i + m.group(1)
    m = re.match(r"^[ny]?[dt][ıiuü](r?)$", ek)  # 'dir 'ti
    if m:
        return f"{d}{i}{m.group(1)}"
    m = re.match(r"^[ıiuü]?m[ıiuü]z$", ek)  # 'imiz
    if m:
        return ("" if unlu else i) + "m" + i + "z"
    if ek == "n":  # 'n varsa
        return "n" if unlu else i + "n"
    return None


class Donusturucu:
    def __init__(self, harita):
        self.harita = harita
        cok = sorted((t for t in harita if " " in t or "'" in t), key=len, reverse=True)
        tek = sorted(t for t in harita if t in TEK_KELIME)
        harf = r"A-Za-zÇĞİÖŞÜçğıöşüÂâÎîÛû"
        ek = r"(?:'([a-zçğıöşü]+))?"
        self.rx_cok = re.compile(r"(?<![%s])(%s)%s(?![%s])" % (harf, "|".join(map(re.escape, cok)), ek, harf))
        # tek kelime: cumle basinda degil (oncesinde kucuk harfli kelime + bosluk)
        self.rx_tek = re.compile(r"(?<=[a-zçğıöşü,] )(%s)%s(?![%s])" % ("|".join(map(re.escape, tek)), ek, harf)) if tek else None

    def _degistir(self, m):
        tr, ek = m.group(1), m.group(2)
        en = re.sub(r"^The ", "", self.harita[tr])  # "The Two Fingers'a" degil "Two Fingers'a"
        if ek is None:
            return en
        yeni = ek_uydur(en, ek)
        if yeni is None:
            return f"{en}'{ek}"
        return f"{en}'{yeni}"

    def __call__(self, s):
        s = self.rx_cok.sub(self._degistir, s)
        if self.rx_tek:
            s = self.rx_tek.sub(self._degistir, s)
        return s


def ornek():
    sys.path.insert(0, ANA)
    from uygula import ceviri_sozlugu
    bul, _, _ = ceviri_sozlugu()
    harita = isim_haritasi(bul)
    don = Donusturucu(harita)
    metinler = json.load(open(os.path.join(ANA, "is", "metinler.json"), encoding="utf-8"))
    satirlar, ekler, n = [], {}, 0
    for f in sorted(glob.glob(os.path.join(ANA, "is", "ceviri", "[0-9][0-9][0-9][0-9].json"))):
        for i, t in json.load(open(f, encoding="utf-8")).items():
            y = don(t)
            if y != t:
                n += 1
                for m in don.rx_cok.finditer(t):
                    if m.group(2):
                        anahtar = f"{harita[m.group(1)]}  '{m.group(2)} -> '{ek_uydur(harita[m.group(1)], m.group(2))}"
                        ekler[anahtar] = ekler.get(anahtar, 0) + 1
                if len(satirlar) < 400:
                    satirlar.append(f"EN: {metinler[i]}\nTR: {t}\nYENI: {y}\n")
    with open(os.path.join(ANA, "is", "isim_ornek.txt"), "w", encoding="utf-8") as f:
        f.write(f"harita: {len(harita)} isim, degisen metin: {n}\n\n## Ek donusumleri\n")
        f.write("\n".join(f"{v:4} {k}" for k, v in sorted(ekler.items(), key=lambda x: -x[1])))
        f.write("\n\n## Ornekler\n" + "\n".join(satirlar))
    print("harita:", len(harita), "degisen metin:", n, "farkli ek:", len(ekler))


if __name__ == "__main__":
    ornek()
