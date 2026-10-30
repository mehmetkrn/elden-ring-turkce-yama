# Elden Ring Turkish Translation (Elden Ring Türkçe Yama)

Turkish text translation for ELDEN RING and Shadow of the Erdtree (≈98.5% of all text: menus, item/spell
descriptions, dialogue, subtitles). Tested on game version **1.17** (Steam).

- Nexus Mods: https://www.nexusmods.com/eldenring/mods/11338
- Two variants (pick one, do not install both):
  - **Tam Türkçe** (`EldenRing_TR_Yama.zip`): everything in Turkish, including item, weapon, spell, boss and place names.
  - **Orijinal İsimler** (`EldenRing_TR_Yama_OrijinalIsimler.zip`): dialogue, descriptions and menus in Turkish;
    item, weapon, spell, boss and place names stay in the original English, also inside dialogue.
  Both zips contain the same executables (byte-identical); only `yama/msg` and the install guide differ.
- No game file is modified. The Turkish text is loaded at launch by the open-source
  [me3](https://github.com/garyttierney/me3) mod loader; the game runs **offline** (EAC disabled).

## What is in the release zip

```
EldenRing_TR/
├─ EldenRing_TR_Baslat.exe   ← our launcher, built from launcher/Baslat.cs (this repo)
├─ EldenRing_TR.me3          ← me3 profile (plain text, package/EldenRing_TR.me3)
├─ OKU_BENI_KURULUM.txt      ← install guide (Turkish)
├─ yama/msg/engus/*.msgbnd.dcx, yama/font/*/font.gfx   ← Turkish text + fonts with ı İ ş Ş ğ Ğ
└─ me3/                      ← official me3 v0.9.0, UNMODIFIED (see hashes below)
```

The only executables are:

| File | Origin | SHA256 |
|---|---|---|
| `EldenRing_TR_Baslat.exe` | built from `launcher/Baslat.cs` (≈60 lines of C#) | `f726032d52c9509fa84f30cc8fee1d553513272a5bf1ec3dca569a9aae2e6786` |
| `me3/bin/me3.exe` | [me3 v0.9.0 release](https://github.com/garyttierney/me3/releases/tag/v0.9.0), unmodified, code-signed by the me3 author | `4cab339a804b4fd55f233693f9dde019a5caec980cc6c859c50e8d16205e486f` |
| `me3/bin/me3-launcher.exe` | same | `65a64d3ae5a0c51f43481b48807df5a9cad21705fcb7f6e430de3d1d09c1f84b` |
| `me3/bin/me3_mod_host.dll` | same | `44139dc0c1184a5589066f70af793b38ff6654b19254f6bd1a601c17b6fe84e4` |

The official `me3-windows-amd64.zip` (v0.9.0) has SHA256
`acbfc5884f61b927b1bacf705637f894476e19cf81640f9c6a2512f1d8b1cf31`.

**About antivirus results:** a few engines (ESET, Ikarus: `HackTool.RustRegion`; Malwarebytes: ML heuristic)
flag the zip. These detections come from me3 (a Rust tool that loads mods into the game process).
Our launcher and the Turkish data files are clean when scanned separately.

## What the launcher does

`launcher/Baslat.cs` only starts

```
me3\bin\me3.exe launch -p EldenRing_TR.me3 -g eldenring
```

from its own folder. It does not touch game files, the registry, or the network, and it ignores any
command-line arguments (so it can be used as a Steam launch option: `"<path>\EldenRing_TR_Baslat.exe" %command%`).
Users who do not want to run it can type the command above themselves.

## Building

### Launcher (Windows, nothing to install)

```powershell
powershell -ExecutionPolicy Bypass -File launcher\build.ps1
```

Uses `csc.exe` from the .NET Framework 4.x that ships with Windows
(`%WINDIR%\Microsoft.NET\Framework64\v4.0.30319\csc.exe`). `launcher/ikon_yap.ps1` draws the icon with
System.Drawing. Output: `dist\EldenRing_TR_Baslat.exe`.

The old csc does not produce byte-identical (deterministic) builds, so a rebuilt exe will have a different
hash than the released one, but the same code. The exe is a small .NET assembly; the released file can be
inspected/decompiled with ILSpy or dnSpy and compared with `launcher/Baslat.cs`.

### Release zip

```powershell
powershell -ExecutionPolicy Bypass -File package\build_package.ps1 -Yama <folder with msg\ and font\>
```

Builds the launcher, downloads the official me3 v0.9.0 zip, verifies the SHA256 of every me3 file,
and assembles `dist\EldenRing_TR_Yama.zip`. Add `-OrijinalIsim` (with `-Yama` pointing at the variant's data) to build
`dist\EldenRing_TR_Yama_OrijinalIsimler.zip` with its own install guide (`package/OKU_BENI_KURULUM_OrijinalIsimler.txt`).

### Building the translation data (`yama/`)

The `.msgbnd.dcx` / `font.gfx` files are generated from your own copy of the game; game files are not
included in this repository.

Requirements: Python 3.10+ (`pip install pycryptodome pillow`), [WitchyBND](https://github.com/ividyon/WitchyBND),
and the Elden Ring binder keys from Nuxe (`res\BinderKeys\EldenRing_PC`).

1. `translation/tools/cikar_msg.py` – reads `msg/engus` and `font` out of the game's `Data*.bhd/bdt` (read-only).
2. Unpack the extracted files with WitchyBND (FMG → XML).
3. `translation/tools/hazirla.py` – builds the list of source strings (`is/metinler.json`) and `parcalar.json`.
4. Translations: `translation/ceviri/NNNN.json` (`{"string id": "Turkish text"}`) – these are the actual
   translation files; `translation/sozluk.md` is the glossary.
5. `translation/tools/uygula.py` – writes the translations into the FMGs and repacks `msgbnd.dcx` with WitchyBND.
   `uygula.py orijinal-isim` builds the "Orijinal İsimler" variant: the name FMGs (`*Name`) are left in English and
   `translation/tools/isim_orijinal.py` replaces Turkish names inside other texts with the English originals,
   re-deriving the Turkish suffix (`Roundtable Hold'a`, `Volcano Manor'dan`).
6. `translation/tools/tr_font.py` – adds ı İ ş Ş ğ Ğ glyphs to `eu_std` / `eu_map` fonts.

Paths at the top of the tools point to the author's folders (`D:\Projeler\EldenRingTR`, the Steam game folder);
change them to yours.

## License

Our code (launcher, build scripts, tools) and the Turkish translation: MIT (see `LICENSE`).
me3 is © its authors, MIT / Apache-2.0. ELDEN RING is © Bandai Namco / FromSoftware; no game files are included.
