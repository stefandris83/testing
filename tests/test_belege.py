"""Tests für src/lav-learning-library/scripts/belege.py (Belegprüfung von Agentenantworten, «Belege prüfen»).

Aufruf:  python tests/test_belege.py [<library-paket.zip>]
Ohne Argument: testdaten/library/lav-learning-library_3-studien_v1.1.zip (öffentliche Teststudien LAV-T01–T03).

Baut eine Kopie der Library-Skill (Paket + scripts/ aus src/lav-learning-library/scripts), führt belege.py
1. auf die unveränderten M6-Antworten aus (darf keine Fehlzahl melden) und
2. auf Antworten mit absichtlich eingebauten Fehlern (muss jeden Fehler melden).
"""
import csv
import pathlib
import shutil
import subprocess
import sys
import tempfile
import zipfile

HERE = pathlib.Path(__file__).resolve().parent
SKILL_SRC = HERE.parent / "src" / "lav-learning-library"
STANDARD = HERE.parent / "testdaten" / "library" / "lav-learning-library_3-studien_v1.1.zip"

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
FIX = HERE / "fixtures" / "m6-antworten.csv"

# (Antwort-ID, alter Text, neuer Text, erwartete Zahl, erwarteter Status)
FEHLER = [
    ("G01", "**19 Prozent**", "**15 Prozent**", "15", "nicht gefunden"),  # 18 stünde zufällig auch auf S. 12
    ("G10", "7’783", "7’738", "7738", "nicht gefunden"),
    ("G10", "52’916", "25’916", "25916", "nicht gefunden"),
    ("G09", "| **2025** | **30%** |", "| **2025** | **33%** |", "33", "nicht gefunden"),
    ("G05", "[LAV-T02, S. 21 (Druckseiten 38–39)]", "[LAV-T02, S. 26]", "43", "nicht gefunden"),
    ("G02", " [LAV-T02, S. 10 (Druckseiten 16–17)]", "", "69", "keine Seitenangabe"),
]
# Bekannte Grenze: selbst berechnete Werte kann das Skript nicht nachrechnen, es markiert sie nur.
GRENZE = ("G10", "| Zugang nach systemischem Nutzen | 83% |", "| Zugang nach systemischem Nutzen | 85% |", "85",
          "berechnet – Rechnung prüfen")


def run(skill, eingabe, ausgabe):
    p = subprocess.run([sys.executable, "-X", "utf8", "-I", str(skill / "scripts" / "belege.py"), str(eingabe),
                        "--ausgabe", str(ausgabe)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if not ausgabe.exists():
        raise AssertionError(f"belege.py lieferte keine Ausgabe (Exit {p.returncode}): {p.stderr.strip()[-300:]}")
    with open(ausgabe, encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh, delimiter=";")), p


def main():
    paket = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else STANDARD
    tmp = pathlib.Path(tempfile.mkdtemp())
    skill = tmp / "lav-learning-library"
    with zipfile.ZipFile(paket) as z:
        z.extractall(skill)
    if (SKILL_SRC / "scripts").exists():
        shutil.copytree(SKILL_SRC / "scripts", skill / "scripts", dirs_exist_ok=True)

    with open(FIX, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter=";"))
    felder = list(rows[0].keys())
    fehler = 0

    # 1. Unveränderte Antworten: keine Fehlzahl
    res, _ = run(skill, FIX, tmp / "basis.csv")
    falsch = [r for r in res if r["status"] == "nicht gefunden"]
    ok = not falsch
    print(f"[{'OK' if ok else 'FEHLER'}] Basis: {len(res)} Zahlen geprüft, nicht gefunden: {len(falsch)}")
    for r in falsch[:10]:
        print("       ", r["id"], r["zahl"], r["seiten"], r["kontext"][:80])
    fehler += not ok

    # 2. Eingebaute Fehler
    for fid, alt, neu, zahl, status in FEHLER + [GRENZE]:
        mod = [dict(r) for r in rows]
        for r in mod:
            if r["id"] == fid:
                assert alt in r["Antwort Agent"], f"Testtext nicht gefunden: {fid} {alt}"
                r["Antwort Agent"] = r["Antwort Agent"].replace(alt, neu, 1)
        f = tmp / f"fehler-{fid}-{zahl}.csv"
        with open(f, "w", encoding="utf-8-sig", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=felder, delimiter=";")
            w.writeheader()
            w.writerows(mod)
        res, _ = run(skill, f, tmp / f"aus-{fid}-{zahl}.csv")
        treffer = [r for r in res if r["id"] == fid and r["zahl"] == zahl and r["status"] == status]
        ok = bool(treffer)
        print(f"[{'OK' if ok else 'FEHLER'}] {fid}: «{alt.strip()[:30]}» → «{neu.strip()[:30]}» erwartet {zahl} = {status}")
        fehler += not ok
    # 3. Antworten v1.1 (G01–G15): Belege nach Tabellen (Absatz danach) werden geprüft
    fix2 = HERE / "fixtures" / "v11-antworten.csv"
    res, _ = run(skill, fix2, tmp / "v11.csv")
    ok = not [r for r in res if r["status"] == "nicht gefunden"] and \
        any(r["id"] == "G10" and r["zahl"] == "8518" and r["status"] == "gefunden" and r["beleg_aus"] == "Absatz danach" for r in res)
    print(f"[{'OK' if ok else 'FEHLER'}] v1.1-Antworten: keine Fehlzahl, Tabellenbeleg aus dem Absatz danach")
    fehler += not ok
    roh = fix2.read_text(encoding="utf-8-sig").replace("CHF 9’021 Mio.", "CHF 9’201 Mio.", 1)
    f = tmp / "v11-fehler.csv"
    f.write_text(roh, encoding="utf-8-sig")
    res, _ = run(skill, f, tmp / "v11-fehler-aus.csv")
    ok = any(r["id"] == "G10" and r["zahl"] == "9201" and r["status"] == "nicht gefunden" for r in res)
    print(f"[{'OK' if ok else 'FEHLER'}] G10: «9’021» → «9’201» in Tabelle mit Beleg danach erwartet 9201 = nicht gefunden")
    fehler += not ok

    print("\nErgebnis:", "alle Tests bestanden" if not fehler else f"{fehler} Test(s) fehlgeschlagen")
    shutil.rmtree(tmp, ignore_errors=True)
    sys.exit(1 if fehler else 0)


if __name__ == "__main__":
    main()
