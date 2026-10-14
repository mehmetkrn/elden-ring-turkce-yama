# Cevirileri FMG'lere yazar, msgbnd.dcx olarak paketler ve TR_Yama klasorune koyar.
import glob, json, os, re, shutil, subprocess, sys
import xml.etree.ElementTree as ET

ANA = r"D:\Projeler\EldenRingTR"
IS = os.path.join(ANA, "is")
WITCHY = os.path.join(ANA, "araclar", "Witchy", "WitchyBND.exe")
KAYNAK = os.path.join(ANA, "orijinal", "msg", "engus")
DERLE = os.path.join(ANA, "derle", "msg", "engus")
HEDEF = os.path.join(ANA, "TR_Yama", "Game", "kaynaklar", "me3", "config", "eldenring-mods", "msg", "engus")

AFINITE_TR = {"Heavy": "Ağır", "Keen": "Keskin", "Quality": "Kaliteli", "Fire": "Ateşli",
              "Flame Art": "Alev Sanatlı", "Lightning": "Yıldırımlı", "Sacred": "Kutsal",
              "Magic": "Büyülü", "Cold": "Soğuk", "Poison": "Zehirli", "Blood": "Kanlı", "Occult": "Okült"}


def witchy(*yollar):
    for i in range(0, len(yollar), 40):
        subprocess.run([WITCHY, "-p", "-s", *yollar[i:i + 40]], check=True)


def ceviri_sozlugu():
    metinler = json.load(open(os.path.join(IS, "metinler.json"), encoding="utf-8"))
    tr = {}
    for f in glob.glob(os.path.join(IS, "ceviri", "[0-9][0-9][0-9][0-9].json")):
        for i, t in json.load(open(f, encoding="utf-8")).items():
            tr[metinler[i]] = t
    turet = json.load(open(os.path.join(IS, "turetilen.json"), encoding="utf-8"))

    def bul(s, derin=0):
        if s in tr:
            return tr[s]
        k = turet.get(s)
        if not k or derin > 5:
            return None
        taban = bul(k[1], derin + 1)
        if taban is None:
            return None
        if k[0] == "arti":
            return f"{taban} +{k[2]}"
        if k[0] == "kul":
            return f"Savaş Külü: {taban}"
        if k[0] == "kuller":
            return f"Savaş Külleri: {taban}"
        if k[0] == "afinite":
            return f"{AFINITE_TR[k[2]]} {taban}"
        return None

    return bul, len(tr), len(turet)


def main():
    bul, n_tr, n_turet = ceviri_sozlugu()
    print("ceviri:", n_tr, "turetme kurali:", n_turet)
    if os.path.exists(os.path.dirname(os.path.dirname(DERLE))):
        shutil.rmtree(os.path.dirname(os.path.dirname(DERLE)))
    shutil.copytree(KAYNAK, DERLE)
    paketler = sorted(f for f in glob.glob(os.path.join(DERLE, "*.msgbnd.dcx")) if "ngword" not in f)
    for p in paketler:
        shutil.copy(p, p + ".yedek")
    witchy(*paketler)
    fmgler = glob.glob(os.path.join(DERLE, "*-msgbnd-dcx", "**", "*.fmg"), recursive=True)
    witchy(*fmgler)
    toplam = cevrilen = 0
    eksik = {}
    for x in glob.glob(os.path.join(DERLE, "*-msgbnd-dcx", "**", "*.fmg.xml"), recursive=True):
        agac = ET.parse(x)
        degisti = False
        for t in agac.getroot().iter("text"):
            s = t.text or ""
            if not s.strip() or s == "%null%" or s.startswith("[ERROR]") or not re.search(r"[A-Za-z]", s):
                continue
            toplam += 1
            ceviri = bul(s)
            if ceviri is None:
                eksik[s] = eksik.get(s, 0) + 1
                continue
            if ceviri != s:
                t.text = ceviri
                degisti = True
            cevrilen += 1
        if degisti:
            agac.write(x, encoding="utf-8", xml_declaration=True)
    print(f"metin girisi: {toplam}, cevrilen: {cevrilen}, eksik benzersiz: {len(eksik)}")
    json.dump(sorted(eksik), open(os.path.join(IS, "eksik.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    xmller = glob.glob(os.path.join(DERLE, "*-msgbnd-dcx", "**", "*.fmg.xml"), recursive=True)
    witchy(*xmller)
    klasorler = [p.replace(".msgbnd.dcx", "-msgbnd-dcx") for p in paketler]
    witchy(*klasorler)
    os.makedirs(HEDEF, exist_ok=True)
    for p in paketler:
        shutil.copy(p, os.path.join(HEDEF, os.path.basename(p)))
        print("yazildi", os.path.basename(p), os.path.getsize(p))


if __name__ == "__main__":
    main()
