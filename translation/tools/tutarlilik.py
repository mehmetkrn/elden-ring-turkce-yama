# Ajanlar arasindaki terim farklarini tek tipe getirir.
import glob, json

DEGISTIR = [
    ("Praetor ", "Pretor "),
    ("Kopuk Malenia", "Kopmuş Malenia"),
    ("Aydın Mohg", "Yüce Mohg"),
    ("Lütuf Bahşedilmiş", "Lütuf Verilmiş"),
    ("Biçimsiz Anne'ye", "Biçimsiz Ana'ya"),
    ("Biçimsiz Anne", "Biçimsiz Ana"),
    ("Ebedi ", "Ebedî "),
    ("Süseni'ni", "İrisi'ni"),
    ("Süseni'yle", "İrisi'yle"),
    ("Süseni", "İrisi"),
]
EKOL = ["Karolos", "Olivinus", "Bilge", "Haima", "Lazuli"]
EKLER = [("Okulu'nun", "Ekolü'nün"), ("Okulu'ndan", "Ekolü'nden"), ("Okulu'nda", "Ekolü'nde"), ("Okulu", "Ekolü")]

n = 0
for f in glob.glob(r"D:\Projeler\EldenRingTR\is\ceviri\[0-9][0-9][0-9][0-9].json"):
    d = json.load(open(f, encoding="utf-8"))
    degisti = False
    for i, t in d.items():
        o = t
        for a, b in DEGISTIR:
            t = t.replace(a, b)
        for ad in EKOL:
            for a, b in EKLER:
                t = t.replace(f"{ad} {a}", f"{ad} {b}")
        if t != o:
            d[i] = t
            degisti = True
            n += 1
    if degisti:
        json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False)
print("degisen satir:", n)
