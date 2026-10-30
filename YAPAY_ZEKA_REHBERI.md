# Elden Ring Türkçe Yama – Kaynak ve Yapay Zeka Rehberi

Bu arşiv, Elden Ring Türkçe metin yamasının **kaynağıdır**: çeviri dosyaları, sözlük ve yamayı üreten Python betikleri.
Bir yapay zeka asistanına (Claude, ChatGPT vb.) bu dosyayı ve klasörü verip "çeviride şunu düzelt, yamayı yeniden üret"
diyebilirsin. Aşağıdaki bölümler hem insan hem yapay zeka için yazıldı.

Test edilen oyun sürümü: **1.17** (ana menüdeki "App Ver."). Yama 14 Ekim 2026'da bu sürümle denendi.

> **GitHub notu:** Bu rehber Nexus'taki Kaynak zip'inin düzenine göre yazıldı. Bu depoda karşılıkları: `is/ceviri` → `translation/ceviri`, `is/parcalar.json` → `translation/parcalar.json`, `sozluk.md` → `translation/sozluk.md`, betikler → `translation/tools/`.

## Kurallar (değiştirme)
- Oyunun kendi dosyalarına (`ELDEN RING\Game\` içindekilere, `eldenring.exe`'ye) **asla yazılmaz**. Yama sadece
  mod yükleyicinin (me3) okuduğu ayrı bir klasöre `msg\engus\*.msgbnd.dcx` ve `font\eu_std|eu_map\font.gfx` koyar.
- exe değiştirme, DRM/kopya koruması aşma yok. Steam dışı (korsan) kopya desteklenmez.
- Oyunun orijinal arşivleri bu pakette **yok**; herkes kendi satın aldığı oyundan çıkarır (aşağıda).

## Klasör haritası
| Yol | Ne |
|---|---|
| `is/metinler.json` | Çevrilecek benzersiz İngilizce metinler: `{"id": "İngilizce"}` (oyundan üretilir) |
| `is/parcalar.json` | Metinlerin çeviri parçalarına bölünmesi (124 parça; grup: isimler/menu/aciklama/diyalog/mesaj) |
| `is/ceviri/NNNN.json` | **Çeviriler**: `{"id": "Türkçe"}`. Düzeltmeler buraya yapılır |
| `is/turetilen.json` | Silah afinite önekleri gibi kuralla türetilen metinler |
| `is/eksik.json` | Çevrilmeden kalan metinlerin listesi |
| `sozluk.md` | Terim sözlüğü (özel isimler, oyun terimleri). Yeni çeviri yaparken önce oku, tutarlı kal |
| `dublaj_map.csv` | Türkçe dublaj modundaki satır kimlikleri (altyazının dublajla uyumu için) |
| `cikar_msg.py` | Oyunun `Data*.bhd/bdt` arşivlerinden `msg/engus` ve `font` dosyalarını **okuyup** çıkarır |
| `hazirla.py` | Çıkarılan FMG'lerden `metinler.json` + `parcalar.json` üretir |
| `sira.py` | `python sira.py goster N` parçayı yazdırır, `kontrol N` denetler, `durum` ilerlemeyi gösterir |
| `tutarlilik.py` | Toplu terim düzeltmesi (DEGISTIR listesi) – tüm `is/ceviri` dosyalarına uygular |
| `uygula.py` | Çevirileri FMG'lere yazar, WitchyBND ile `msgbnd.dcx` paketler, `TR_Yama\...\msg\engus`'a koyar |
| `isim_orijinal.py` | "Orijinal İsimler" sürümü: isim listelerini İngilizce bırakır, metin içindeki Türkçe isimleri İngilizcesiyle değiştirip eki uydurur (`'ne` → `'a`) |
| `tr_font.py`, `gfxfont.py` | Yazı tiplerine ı İ ş Ş ğ Ğ harflerini ekler (orijinal fontta yok) |
| `font_kontrol.py`, `font_onizle.py`, `olc.py` | Kontrol / önizleme / ölçüm yardımcıları |
| `baslatici/` | Oyunu me3 ile açan küçük başlatıcının C# kaynağı + ikon üreticisi |

## Gerekenler
- Python 3.10+, `pip install pycryptodome pillow`
- **WitchyBND** (FromSoftware dosya paketleyici) → `araclar\Witchy\WitchyBND.exe`
- **Nuxe**'nin `res\BinderKeys\EldenRing_PC` anahtar klasörü → `araclar\Nuxe\...` (oyun arşivlerini okumak için;
  bunlar topluluğun herkese açık araçlarıdır, bu pakete konmadı – kendi indir)
- me3 mod yükleyici: https://github.com/garyttierney/me3

## Yollar
Betiklerin başında sabit yollar var: `ANA/ROOT/IS = D:\Projeler\EldenRingTR\...` ve
`GAME = E:\SteamLibrary\steamapps\common\ELDEN RING\Game`. Kendi bilgisayarında ya bu klasörü
`D:\Projeler\EldenRingTR` olarak aç ya da yapay zekaya şunu söyle:
> "Tüm .py dosyalarındaki `D:\Projeler\EldenRingTR` yolunu `<benim klasörüm>`, oyun yolunu `<oyun klasörüm>` yap."

## Akış
1. `python cikar_msg.py` → `orijinal/msg/engus`, `orijinal/font` (oyundan okur, oyuna yazmaz)
2. WitchyBND ile `orijinal` içindekileri `acik/` altına aç (FMG → XML)
3. `python hazirla.py` → `is/metinler.json`, `is/parcalar.json` (zaten pakette var; oyun güncellenince yeniden çalıştır)
4. Çeviri: `is/ceviri/NNNN.json` dosyalarını doldur/düzelt → `python sira.py kontrol N`
5. `python tutarlilik.py` (isteğe bağlı terim birliği)
6. `python uygula.py` → `TR_Yama\Game\kaynaklar\me3\config\eldenring-mods\msg\engus\*.msgbnd.dcx`
7. `python tr_font.py` → aynı yerde `font\eu_std\font.gfx`, `font\eu_map\font.gfx`
   - Orijinal İsimler sürümü: `python uygula.py orijinal-isim` → `TR_Yama_OrijinalIsim\msg\engus\*.msgbnd.dcx`
     (eşya/silah/büyü/boss/yer adları İngilizce; diyalog, açıklama, menü Türkçe). Çeviri düzeltilince iki sürüm de yeniden üretilmeli.
8. Çıkan `msg` ve `font` klasörlerini oyuncu paketindeki `EldenRing_TR\yama\` içine koy, oyunu başlatıcıyla aç, kontrol et.

## Çeviri kuralları
- `<?...?>`, `%...%`, `{...}` biçimindeki kodlar **aynen** kalır (sira.py kontrol eder).
- Özel isimler `sozluk.md`'ye göre; yeni terim çıkarsa sözlüğe ekle.
- Kullanım sözleşmesi (ToS) bilerek çevrilmedi.
- Kullanılabilen Türkçe harfler: ç ğ ı İ ö ş ü Ç Ğ Ö Ş Ü (ı İ ş Ş ğ Ğ yazı tipine `tr_font.py` ile eklenir).

## Oyun güncellenince
`cikar_msg.py` + WitchyBND + `hazirla.py`'yi yeniden çalıştır, `is/eksik.json`'daki yeni satırları çevir, `uygula.py`.
