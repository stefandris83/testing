"""Regressionstest der Ingest-Skripte (inventar.py, pruefen.py, aufteilen.py, paket.py, wiki.py, skripte.md).

Aufruf:  python tests/test_ingest_skripte.py

Teil A läuft immer (nur Standardbibliothek): aufteilen.py, paket.py mit fünf Manipulationen, wiki.py, skripte.md.
Teil B braucht die öffentlichen Test-PDFs in testdaten/pdf/ (holen mit `python tools/pdfs_holen.py`) und das
Python-Paket pdfplumber. Fehlt eines davon, wird Teil B übersprungen und gemeldet – kein Fehler.
Teil B: inventar.py auf LAV-T02; pruefen.py gegen die Referenztranskripte LAV-T01/LAV-T02 (nur begründete Befunde);
fünf eingebaute Fehler in einer Kopie von LAV-T02 müssen alle gemeldet werden.
Entspricht Abschnitt 10.5 der Blaupause v3.1 (Regressionstest nach jeder Skriptänderung).
"""
import csv
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "src" / "lav-ingest" / "scripts"
REF = ROOT / "testdaten" / "referenz"
BSP = ROOT / "testdaten" / "library" / "beispielpaket_LAV-T02_v3.1.zip"
PDF = ROOT / "testdaten" / "pdf"
fehler = 0

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def run(script, *args, cwd=None):
    p = subprocess.run([sys.executable, "-X", "utf8", "-I", str(SCRIPTS / script), *map(str, args)], cwd=cwd,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout + p.stderr


def check(name, ok, out=""):
    global fehler
    print(f"[{'OK' if ok else 'FEHLER'}] {name}")
    if not ok:
        fehler += 1
        print("   ", str(out).strip().replace("\n", "\n    ")[-1200:])


def teil_a(tmp):
    print("Teil A – ohne PDF")
    # aufteilen.py auf das Referenztranskript LAV-T02 (27 Seiten)
    ziel = tmp / "LAV-T02" / "volltext"
    rc, out = run("aufteilen.py", REF / "LAV-T02" / "seiten", ziel, "--id", "LAV-T02", "--titel",
                  "Gesundheitsmonitor 2025", "--quelle", "gesundheitsmonitor-2025.pdf", "--max", 45000)
    teile = sorted(ziel.glob("teil-*.md"))
    groessen_ok = all(t.stat().st_size <= 45000 for t in teile)
    schluss_ok = all(re.search(r"^— Ende Teil \d+ von \d+ · Kontrollwort Teil \d+: [A-Z]+-\d{2}", t.read_text(encoding="utf-8"), re.M)
                     for t in teile)
    check("aufteilen.py: Teile ≤ 45’000 Bytes, jede mit Kontrollwort-Schlusszeile", rc == 0 and teile and groessen_ok and schluss_ok, out)
    kz = (ziel.parent / "katalog-zeile.txt").read_text(encoding="utf-8") if (ziel.parent / "katalog-zeile.txt").exists() else ""
    bereiche = [(int(a), int(b)) for a, b in re.findall(r"S\. (\d+)–(\d+)", kz)]
    lueckenlos = bool(bereiche) and bereiche[0][0] == 1 and bereiche[-1][1] == 27 and all(
        bereiche[i][1] + 1 == bereiche[i + 1][0] for i in range(len(bereiche) - 1))
    check("aufteilen.py: Katalogzeile deckt Seiten 1–27 lückenlos ab", lueckenlos, kz)
    kw = list(csv.reader(open(ziel.parent / "kontrollwoerter.csv", encoding="utf-8-sig"), delimiter=";"))[1:] \
        if (ziel.parent / "kontrollwoerter.csv").exists() else []
    check("aufteilen.py: kontrollwoerter.csv mit eindeutigen Wörtern", len(kw) == len(teile) and len({r[1] for r in kw}) == len(kw), kw)

    # paket.py: gültiges Beispielpaket ohne Befunde, fünf Manipulationen mit Befund
    rc, out = run("paket.py", BSP)
    check("paket.py: Beispielpaket LAV-T02 ohne Befunde", rc == 0 and "Keine Befunde" in out, out)
    basis = tmp / "bsp"
    with zipfile.ZipFile(BSP) as z:
        z.extractall(basis)

    def manipuliert(name, aendern, erwartet):
        d = tmp / f"m-{name}"
        shutil.copytree(basis, d)
        aendern(d)
        rc, out = run("paket.py", d)
        check(f"paket.py erkennt: {name}", rc == 1 and re.search(erwartet, out, re.I) is not None, out)

    vt = pathlib.Path("references") / "volltext" / "LAV-T02"

    def ohne_schlusszeile(d):
        f = d / vt / "teil-03.md"
        f.write_text("\n".join(l for l in f.read_text(encoding="utf-8").splitlines() if not l.startswith("— Ende")) + "\n",
                     encoding="utf-8")

    def wort_in_skill(d):
        t = (d / vt / "teil-02.md").read_text(encoding="utf-8")
        w = re.search(r"Kontrollwort[^:]*: ([A-Z]+-\d{2})", t).group(1)
        with open(d / "SKILL.md", "a", encoding="utf-8") as fh:
            fh.write(f"\nBeispiel: {w}\n")

    def katalogbereich(d):
        f = d / "references" / "00-katalog.md"
        t = f.read_text(encoding="utf-8")
        f.write_text(re.sub(r"(teil-02 S\. \d+–)(\d+)", lambda m: m.group(1) + str(int(m.group(2)) + 1), t, count=1),
                     encoding="utf-8")

    def ohne_seitenmarker(d):
        f = d / vt / "teil-02.md"
        lines = f.read_text(encoding="utf-8").splitlines()
        marker = [i for i, l in enumerate(lines) if l.startswith("[[Seite ")]
        del lines[marker[1]]
        f.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def fremde_datei(d):
        (d / "references" / "notizen.csv").write_text("a;b\n1;2\n", encoding="utf-8")

    manipuliert("fehlende Schlusszeile", ohne_schlusszeile, r"schlusszeile|kontrollwort")
    manipuliert("Kontrollwort zusätzlich in SKILL.md", wort_in_skill, r"kontrollwort")
    manipuliert("falscher Seitenbereich im Katalog", katalogbereich, r"katalog|volltext|seiten")
    manipuliert("fehlender Seitenmarker", ohne_seitenmarker, r"seite|marker")
    manipuliert("fremde Datei im Paket", fremde_datei, r"notizen\.csv|unzulässig|nicht erlaubt|fremd")

    # wiki.py
    rc, out = run("wiki.py", BSP, tmp / "wiki")
    seiten = sorted(p.name for p in (tmp / "wiki").glob("*.md"))
    ohne_kw = all("Kontrollwort" not in p.read_text(encoding="utf-8") for p in (tmp / "wiki").glob("*.md"))
    check("wiki.py: index.md und LAV-T02.md, kein «Kontrollwort» im Ergebnis",
          rc == 0 and seiten == ["LAV-T02.md", "index.md"] and ohne_kw, out)

    # skripte.md (Ersatzweg) enthält jedes Skript unverändert
    sk = (ROOT / "src" / "lav-ingest" / "references" / "skripte.md").read_text(encoding="utf-8")
    fehlend = [p.name for p in sorted(SCRIPTS.glob("*.py"))
               if f"## {p.name}\n\n```python\n{p.read_text(encoding='utf-8').replace(chr(13), '')}```" not in sk]
    check("references/skripte.md enthält alle Skripte unverändert (sonst: python tools/build.py)", not fehlend, fehlend)


def teil_b(tmp):
    print("\nTeil B – mit Test-PDFs")
    try:
        import pdfplumber  # noqa: F401
    except ImportError:
        print("[ÜBERSPRUNGEN] pdfplumber fehlt (pip install pdfplumber)")
        return
    pdf24, pdf25 = PDF / "gesundheitsmonitor-2024.pdf", PDF / "gesundheitsmonitor-2025.pdf"
    if not (pdf24.exists() and pdf25.exists()):
        print("[ÜBERSPRUNGEN] Test-PDFs fehlen in testdaten/pdf/ (python tools/pdfs_holen.py)")
        return

    # inventar.py
    rc, out = run("inventar.py", pdf25, tmp / "inv", "--bilder", "keine")
    inv = json.loads((tmp / "inv" / "inventar.json").read_text(encoding="utf-8")) if (tmp / "inv" / "inventar.json").exists() else {}
    typ26 = next((r["typ"] for r in inv.get("inventar", []) if r["seite"] == 26), "")
    check("inventar.py: 27 Seiten, Seite 26 ohne Textebene, Doppelseiten erkannt",
          rc == 0 and inv.get("seiten") == 27 and typ26 == "leer" and "Doppelseiten" in out, out[-600:])

    # pruefen.py gegen die Referenztranskripte: nur die begründeten Seiten
    def gemeldete_seiten(pdf, seiten, name):
        prot = tmp / f"{name}.txt"
        rc, out = run("pruefen.py", pdf, seiten, "--protokoll", prot)
        j = json.loads(prot.with_suffix(".json").read_text(encoding="utf-8"))
        return {r["seite"]: r["befunde"] for r in j["seiten"] if r["befunde"]}, out

    for sid, pdf in (("LAV-T01", pdf24), ("LAV-T02", pdf25)):
        gemeldet, out = gemeldete_seiten(pdf, REF / sid / "seiten", sid)
        begruendet = {int(r[0]) for r in csv.reader(open(REF / sid / "befunde-begruendet.txt", encoding="utf-8"),
                                                    delimiter=";") if r and r[0].isdigit()}
        check(f"pruefen.py {sid}: nur begründete Seiten gemeldet ({sorted(gemeldet)} ⊆ {sorted(begruendet)})",
              set(gemeldet) <= begruendet, out[-800:])

    # Fünf eingebaute Fehler in einer Kopie von LAV-T02
    kopie = tmp / "fehler"
    shutil.copytree(REF / "LAV-T02" / "seiten", kopie)

    def ersetzen(n, alt, neu):
        f = kopie / f"s{n:03d}.md"
        t = f.read_text(encoding="utf-8")
        assert alt in t, f"Testtext fehlt auf Seite {n}: {alt[:40]}"
        f.write_text(t.replace(alt, neu, 1), encoding="utf-8")

    t5 = (kopie / "s005.md").read_text(encoding="utf-8")
    absatz = max((p for p in t5.split("\n\n") if not re.search(r"\d", p) and not p.startswith("[[")), key=len)
    ersetzen(5, absatz, "")                                                   # 1. Absatz ohne Zahlen gelöscht
    ersetzen(12, "| Kopfprämie | 26 | 56 |", "| Kopfprämie | 26 | 57 |")      # 2. Tabellenwert verändert
    (kopie / "s018.md").unlink()                                              # 3. Seite gelöscht
    ersetzen(12, "; alle Werte beschriftet", "")                             # 4. Wertstatus entfernt (Grafik 7)
    ersetzen(13, "[[Seite 13/27", "[[Seite 13/26")                            # 5. Seitenmarker verfälscht
    gemeldet, out = gemeldete_seiten(pdf25, kopie, "fehler")
    erwartet = {
        "Absatz ohne Zahlen gelöscht (S. 5)": (5, r"Wortabdeckung"),
        "Tabellenwert 56 → 57 (S. 12)": (12, r"fehlende Zahlen.*56|seltener.*56"),
        "Seite gelöscht (S. 18)": (18, r"Seite fehlt"),
        "Wertstatus entfernt (S. 12)": (12, r"ohne Wertstatus"),
        "Seitenmarker verfälscht (S. 13)": (13, r"Seitenmarker"),
    }
    for name, (seite, muster) in erwartet.items():
        befunde = " | ".join(gemeldet.get(seite, []))
        check(f"pruefen.py erkennt: {name}", re.search(muster, befunde) is not None, befunde or out[-600:])


def main():
    tmp = pathlib.Path(tempfile.mkdtemp())
    try:
        teil_a(tmp)
        teil_b(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("\nErgebnis:", "alle Tests bestanden" if not fehler else f"{fehler} Test(s) fehlgeschlagen")
    sys.exit(1 if fehler else 0)


if __name__ == "__main__":
    main()
