"""Tests für src/lav-ingest/scripts/paket_bauen.py («Paket bauen»).

Aufruf:  python tests/test_paket_bauen.py [<LAV-T01_ingest.zip> <LAV-T02_ingest.zip> <LAV-T03_ingest.zip>]
Ohne Argumente: die Ingest-Ergebnisse der öffentlichen Teststudien aus testdaten/ingest/.
"""
import io
import pathlib
import shutil
import re
import subprocess
import sys
import tempfile
import zipfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
SCRIPT = ROOT / "src" / "lav-ingest" / "scripts" / "paket_bauen.py"
STANDARD = [ROOT / "testdaten" / "ingest" / f"LAV-T0{i}_ingest.zip" for i in (1, 2, 3)]
fehler = 0

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def bauen(tmp, name, *args):
    aus, csv = tmp / f"{name}.zip", tmp / f"{name}.csv"
    p = subprocess.run([sys.executable, "-X", "utf8", "-I", str(SCRIPT), *map(str, args), "--ausgabe", str(aus),
                        "--csv", str(csv)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout + p.stderr, aus


def lesen(zipf, pfad):
    with zipfile.ZipFile(zipf) as z:
        return z.read(pfad).decode("utf-8")


def namen(zipf):
    with zipfile.ZipFile(zipf) as z:
        return z.namelist()


def check(name, ok, out=""):
    global fehler
    print(f"[{'OK' if ok else 'FEHLER'}] {name}")
    if not ok:
        fehler += 1
        print("   ", out.strip().replace("\n", "\n    ")[-1500:])


def umbenennen(src, ziel, neu_id, neu_titel):
    """Kopie eines Ingest-ZIPs mit anderer ID und anderem Titel (für den Aufteilungstest)."""
    with zipfile.ZipFile(src) as zi, zipfile.ZipFile(ziel, "w") as zo:
        for i in zi.infolist():
            d = zi.read(i)
            if i.filename.endswith((".md", ".txt", ".csv")):
                t = d.decode("utf-8").replace("LAV-T01", neu_id).replace("Gesundheitsmonitor 2024", neu_titel)
                d = t.encode("utf-8")
            zo.writestr(i.filename, d)


def main():
    t1, t2, t3 = map(pathlib.Path, sys.argv[1:4] if len(sys.argv) >= 4 else STANDARD)
    tmp = pathlib.Path(tempfile.mkdtemp())

    # 1. Drei einzelne Ingest-ZIPs
    rc, out, p1 = bauen(tmp, "drei", t1, t2, t3)
    kat = lesen(p1, "references/00-katalog.md") if p1.exists() else ""
    check("drei Ingest-ZIPs: ohne Befunde, 3 Studien", rc == 0 and "3 Studien" in kat, out)
    check("Reihe erkannt: T01 ↔ T02 gegenseitig, mit spätere/frühere Ausgabe",
          "LAV-T02 Gesundheitsmonitor 2025 (spätere Ausgabe" in kat and "LAV-T01 Gesundheitsmonitor 2024 (frühere Ausgabe" in kat, out)
    check("T03 ohne Verwechslungseintrag", re.search(r"## LAV-T03.*?Nicht verwechseln mit: –", kat, re.S) is not None, kat)
    check("Paketinhalt: SKILL.md, scripts/paket.py, scripts/belege.py, keine CSV",
          {"SKILL.md", "scripts/paket.py", "scripts/belege.py"} <= set(namen(p1)) and not any(n.endswith(".csv") for n in namen(p1)))
    check("nicht freigegebene Cards werden gemeldet", "NICHT FREIGEGEBEN: LAV-T01, LAV-T02, LAV-T03" in out, out)
    check("Kontrollwörter erneuert (keine NEU-xx im Paket)", "NEU-" not in kat + lesen(p1, "references/01-study-cards.md"))

    # 1b. --uploads: Skript findet die ZIPs im Upload-Ordner selbst (kein Dateipfad im Befehl)
    up = tmp / "uploads"
    up.mkdir()
    for f, n in ((t1, "LAV-T01_ingest-1e1c81f2.zip"), (t2, "LAV-T02_ingest-aa11.zip"), (t3, "LAV-T03_ingest-bb22.zip")):
        (up / n).write_bytes(f.read_bytes())
    (up / "studie.pdf").write_bytes(b"%PDF-1.4")
    rc, out, pu = bauen(tmp, "uploads", "--uploads", up)
    check("--uploads: 3 ZIPs gefunden, PDF ignoriert, Paket wie mit Einzelangabe",
          rc == 0 and "3 ZIP-Dateien" in out and lesen(pu, "references/00-katalog.md").count("## LAV-") == 3, out)
    rc, out, _ = bauen(tmp, "uploads-leer", "--uploads", tmp / "gibtsnicht")
    check("--uploads ohne Ordner: klare Fehlermeldung", rc != 0 and "kein Upload-Ordner gefunden" in out, out)

    # 2. Ein ZIP mit allen Ingest-ZIPs
    sammel = tmp / "sammel.zip"
    with zipfile.ZipFile(sammel, "w") as z:
        for f in (t1, t2, t3):
            z.write(f, f.name)
    rc, out, p2 = bauen(tmp, "sammel", sammel)
    check("Sammel-ZIP: gleiche Studien wie einzeln", rc == 0 and "3 Studien" in lesen(p2, "references/00-katalog.md"), out)

    # 3. Bestehendes Paket + neues Ingest-Ergebnis derselben ID
    t3neu = tmp / "LAV-T03_ingest_neu.zip"
    with zipfile.ZipFile(t3) as zi, zipfile.ZipFile(t3neu, "w") as zo:
        for i in zi.infolist():
            d = zi.read(i)
            if i.filename.endswith("katalog-eintrag.md"):
                d = d.decode("utf-8").replace("- Auch genannt: Arzneimittelreport", "- Auch genannt: Arzneimittelreport; AMR").encode()
            zo.writestr(i.filename, d)
    rc, out, p3 = bauen(tmp, "update", p1, t3neu)
    kat3 = lesen(p3, "references/00-katalog.md")
    check("Update: T03 ersetzt, T01/T02 übernommen, ohne Befunde",
          rc == 0 and "LAV-T03 · Helsana-Arzneimittelreport 2024: ersetzt" in out and "LAV-T01 · Gesundheitsmonitor 2024: übernommen" in out
          and "Arzneimittelreport; AMR" in kat3 and kat3.count("## LAV-") == 3, out)
    check("Update: Volltexte des bestehenden Pakets unverändert übernommen",
          lesen(p3, "references/volltext/LAV-T02/teil-01.md") == lesen(p1, "references/volltext/LAV-T02/teil-01.md"))

    # 4. Freigabe
    rc, out, p4 = bauen(tmp, "freigabe", p1, "--freigabe", "LAV-T02=Anna Muster, Research", "--freigabe", "*=Beat Beispiel, Research")
    cards = lesen(p4, "references/01-study-cards.md")
    check("Freigabe: Name und Datum in der Card, keine offene Freigabe",
          rc == 0 and "NICHT FREIGEGEBEN" not in out and re.search(r"## LAV-T02.*?\nFreigegeben: Anna Muster, Research · \d{4}-\d{2}-\d{2} · Volltext-Version 1\.0", cards, re.S)
          and cards.count("Freigegeben: Beat Beispiel, Research") == 2, out)

    # 5. Entfernen
    rc, out, p5 = bauen(tmp, "entfernen", p1, "--entfernen", "LAV-T03")
    check("Entfernen: T03 weg (Katalog und Volltext)",
          rc == 0 and "## LAV-T03" not in lesen(p5, "references/00-katalog.md") and not any("LAV-T03" in n for n in namen(p5)), out)

    # 6. Viele Studien: Cards auf mehrere Dateien, doppelte Kontrollwörter ersetzt
    kopien = []
    for i in range(11, 41):
        k = tmp / f"LAV-T{i}_ingest.zip"
        umbenennen(t1, k, f"LAV-T{i}", f"Testreihe {'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[i % 26]}{'XYZ'[i // 26 - 0]} 2024")
        kopien.append(k)
    rc, out, p6 = bauen(tmp, "viele", t1, *kopien)
    card_dateien = [n for n in namen(p6) if n.startswith("references/01-study-cards")] if p6.exists() else []
    check("31 Studien: ohne Befunde, Cards auf mehrere Dateien verteilt", rc == 0 and len(card_dateien) >= 2, out)
    check("doppelte Kontrollwörter der Volltexte ersetzt", out.count("war schon in") == 2 * len(kopien), out)

    # 7. Gleiche ID zweimal als Ingest-Ergebnis
    rc, out, _ = bauen(tmp, "doppelt", t1, kopien[0], tmp / "LAV-T11_ingest.zip")
    check("doppelte Eingabe derselben Studie ergibt Befund", rc == 1 and "kommt in mehreren Ingest-Ergebnissen vor" in out, out)

    # 8. Falsche Zahl in der Card wird über paket.py gemeldet
    t1f = tmp / "LAV-T01_falsch.zip"
    with zipfile.ZipFile(t1) as zi, zipfile.ZipFile(t1f, "w") as zo:
        for i in zi.infolist():
            d = zi.read(i)
            if i.filename.endswith("card.md"):
                t = d.decode("utf-8")
                m = re.search(r"^- .*?(\d+)(\s*%.*?\[S\. \d+\])", t, re.M)
                t = t[:m.start(1)] + "987" + t[m.end(1):]
                d = t.encode()
            zo.writestr(i.filename, d)
    rc, out, _ = bauen(tmp, "falsch", t1f)
    check("falsche Card-Zahl: Befund, Exit 1", rc == 1 and "Zahl 987" in out, out)

    shutil.rmtree(tmp, ignore_errors=True)
    print("\nErgebnis:", "alle Tests bestanden" if not fehler else f"{fehler} Test(s) fehlgeschlagen")
    sys.exit(1 if fehler else 0)


if __name__ == "__main__":
    main()
