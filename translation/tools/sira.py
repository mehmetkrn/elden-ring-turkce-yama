# Ceviri sirasi: "python sira.py goster N" parcayi yazdirir, "python sira.py kontrol N" ceviriyi denetler,
# "python sira.py durum" ilerlemeyi gosterir.
import json, os, re, sys

IS = r"D:\Projeler\EldenRingTR\is"
metinler = json.load(open(os.path.join(IS, "metinler.json"), encoding="utf-8"))
parcalar = json.load(open(os.path.join(IS, "parcalar.json"), encoding="utf-8"))
KOD = re.compile(r"<\?[^?]*\?>|%[a-z0-9_]+%|\{[^}]*\}")


def yol(n):
    return os.path.join(IS, "ceviri", f"{int(n):04d}.json")


def goster(n):
    p = parcalar[int(n)]
    print(f"# parca {n} / {len(parcalar) - 1}  grup={p['grup']}")
    print(json.dumps({i: metinler[i] for i in p["idler"]}, ensure_ascii=False, indent=0))


def kontrol(n):
    p = parcalar[int(n)]
    tr = json.load(open(yol(n), encoding="utf-8"))
    hatalar = []
    for i in p["idler"]:
        if i not in tr:
            hatalar.append(f"{i}: eksik"); continue
        en, t = metinler[i], tr[i]
        if sorted(KOD.findall(en)) != sorted(KOD.findall(t)):
            hatalar.append(f"{i}: kod farki {KOD.findall(en)} -> {KOD.findall(t)}")
        if en.count("\n\n") != t.count("\n\n"):
            hatalar.append(f"{i}: paragraf sayisi farkli")
    fazla = set(tr) - set(p["idler"])
    if fazla:
        hatalar.append(f"fazla id: {sorted(fazla)[:10]}")
    print("TAMAM" if not hatalar else "\n".join(hatalar))


def birlestir(n):
    """NNNN_tr.json'daki ceviriyi alir, eksik (bilerek cevrilmeyen) idleri Ingilizce birakir."""
    p = parcalar[int(n)]
    kaynak = yol(n).replace(".json", "_tr.json")
    tr = json.load(open(kaynak, encoding="utf-8"))
    tam = {i: tr.get(i, metinler[i]) for i in p["idler"]}
    json.dump(tam, open(yol(n), "w", encoding="utf-8"), ensure_ascii=False)
    os.remove(kaynak)
    print("birlestirildi, ingilizce birakilan:", len(p["idler"]) - len(set(tr) & set(p["idler"])))
    kontrol(n)


def ara(*kelimeler):
    """Daha once cevrilmis metinlerde Ingilizce ifadeyi arar (terim tutarliligi icin)."""
    import glob
    q = " ".join(kelimeler).lower()
    bulunan = 0
    for f in sorted(glob.glob(os.path.join(IS, "ceviri", "[0-9][0-9][0-9][0-9].json"))):
        tr = json.load(open(f, encoding="utf-8"))
        for i, t in tr.items():
            if q in metinler[i].lower() and len(metinler[i]) < 120:
                print(f"{metinler[i]!r} -> {t!r}")
                bulunan += 1
                if bulunan >= 15:
                    return


def durum():
    bitti = [n for n in range(len(parcalar)) if os.path.exists(yol(n))]
    sonraki = next((n for n in range(len(parcalar)) if not os.path.exists(yol(n))), None)
    print(f"biten parca {len(bitti)}/{len(parcalar)}, sonraki: {sonraki}")


if __name__ == "__main__":
    {"goster": goster, "kontrol": kontrol, "birlestir": birlestir, "ara": ara,"durum": lambda *a: durum()}[sys.argv[1]](*sys.argv[2:])
