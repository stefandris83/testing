"""Abgeleitete Dateien abgleichen, alle Tests ausführen und die Ingest-Skill für Copilot Studio bauen.

Aufruf im Repo-Ordner (Windows, macOS, Linux; Python 3.10 oder neuer, keine Zusatzpakete):
  python tools/build.py              abgleichen, testen, dist/lav-ingest.zip neu bauen (nur wenn sich der Inhalt ändert)
  python tools/build.py --nur-tests  abgleichen und testen, kein ZIP
  python tools/build.py --pruefen    nichts schreiben: meldet veraltete abgeleitete Dateien oder ein veraltetes ZIP und testet
                                     (so läuft es in GitHub Actions)

Abgeleitete Dateien – nie von Hand ändern, immer die Quelle (rechts) ändern:
  src/lav-ingest/assets/library-SKILL.md      ← src/lav-learning-library/SKILL.md
  src/lav-ingest/scripts/belege.py            ← src/lav-learning-library/scripts/belege.py
  src/lav-learning-library/scripts/paket.py   ← src/lav-ingest/scripts/paket.py
  src/lav-ingest/references/skripte.md        ← alle Skripte in src/lav-ingest/scripts/

Das ZIP enthält den Inhalt von src/lav-ingest/ auf oberster Ebene (SKILL.md zuoberst), mit LF-Zeilenenden und festen
Zeitstempeln. Gleicher Inhalt ergibt dasselbe ZIP; dist/PRUEFSUMMEN.txt nennt die SHA-256-Prüfsumme.
Exit-Code 0 = alles in Ordnung, 1 = Test fehlgeschlagen oder etwas veraltet, 2 = Fehler.
"""
import argparse
import hashlib
import io
import pathlib
import subprocess
import sys
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
INGEST = ROOT / "src" / "lav-ingest"
LIBRARY = ROOT / "src" / "lav-learning-library"
DIST = ROOT / "dist" / "lav-ingest.zip"
SUMMEN = ROOT / "dist" / "PRUEFSUMMEN.txt"
TESTS = ROOT / "tests"
# Reihenfolge der Skripte in references/skripte.md (neue Skripte werden alphabetisch angehängt)
ORDER = ["inventar.py", "pruefen.py", "aufteilen.py", "paket.py", "paket_bauen.py", "belege.py", "wiki.py"]
TEXT = {".md", ".py", ".txt", ".csv", ".json", ".yml", ".yaml"}
ZEIT = (2026, 1, 1, 0, 0, 0)

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def lesen(p):
    """Dateiinhalt als Bytes; Textdateien mit LF-Zeilenenden (unabhängig von Git-Einstellungen unter Windows)."""
    b = p.read_bytes()
    return b.replace(b"\r\n", b"\n") if p.suffix.lower() in TEXT else b


def skripte_md():
    scripts = sorted(p.name for p in (INGEST / "scripts").glob("*.py"))
    reihe = [n for n in ORDER if n in scripts] + [n for n in scripts if n not in ORDER]
    parts = ["# Skripte als Text (Ersatzweg)\n",
             "Falls die Dateien unter `scripts/` nicht direkt ausführbar sind: Schreibe den Codeblock des benötigten "
             "Skripts unverändert als Datei mit dem genannten Namen in dein Arbeitsverzeichnis und führe sie mit "
             "Python aus. Nichts am Code ändern.\n"]
    for name in reihe:
        code = lesen(INGEST / "scripts" / name).decode("utf-8")
        parts.append(f"\n## {name}\n\n```python\n{code}```\n")
    return "".join(parts).encode("utf-8")


def abgeleitet():
    """{Zieldatei: Soll-Inhalt}. Reihenfolge wichtig: belege.py vor skripte.md."""
    soll = {
        INGEST / "assets" / "library-SKILL.md": lesen(LIBRARY / "SKILL.md"),
        INGEST / "scripts" / "belege.py": lesen(LIBRARY / "scripts" / "belege.py"),
        LIBRARY / "scripts" / "paket.py": lesen(INGEST / "scripts" / "paket.py"),
    }
    return soll


def abgleichen(nur_pruefen):
    veraltet = []
    soll = abgeleitet()
    for ziel, inhalt in soll.items():
        if not ziel.exists() or lesen(ziel) != inhalt:
            veraltet.append(ziel)
            if not nur_pruefen:
                ziel.parent.mkdir(parents=True, exist_ok=True)
                ziel.write_bytes(inhalt)
    # skripte.md erst nach dem Abgleich von belege.py erzeugen
    ziel = INGEST / "references" / "skripte.md"
    inhalt = skripte_md()
    if not ziel.exists() or lesen(ziel) != inhalt:
        veraltet.append(ziel)
        if not nur_pruefen:
            ziel.write_bytes(inhalt)
    for z in veraltet:
        print(("VERALTET: " if nur_pruefen else "aktualisiert: ") + z.relative_to(ROOT).as_posix())
    return veraltet


def zip_soll():
    out = {}
    for p in sorted(INGEST.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts and p.name not in (".DS_Store", "Thumbs.db"):
            out[p.relative_to(INGEST).as_posix()] = lesen(p)
    if "SKILL.md" not in out:
        sys.exit("FEHLER: src/lav-ingest/SKILL.md fehlt")
    return out


def zip_ist(pfad):
    if not pfad.exists():
        return None
    with zipfile.ZipFile(pfad) as z:
        return {i.filename: z.read(i) for i in z.infolist() if not i.is_dir()}


def zip_bytes(inhalt):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name in sorted(inhalt, key=lambda n: (n != "SKILL.md", n)):
            info = zipfile.ZipInfo(name, date_time=ZEIT)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, inhalt[name])
    return buf.getvalue()


def tests_ausfuehren():
    fehler = []
    for t in sorted(TESTS.glob("test_*.py")):
        print(f"\n=== {t.name} ===", flush=True)
        p = subprocess.run([sys.executable, "-X", "utf8", str(t)], cwd=ROOT, capture_output=True,
                           text=True, encoding="utf-8", errors="replace")
        print((p.stdout + p.stderr).strip())
        if p.returncode != 0:
            fehler.append(t.name)
    return fehler


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--nur-tests", action="store_true")
    g.add_argument("--pruefen", action="store_true")
    a = ap.parse_args()

    print("1. Abgeleitete Dateien")
    veraltet = abgleichen(a.pruefen)
    if not veraltet:
        print("   alle aktuell")

    print("\n2. Tests")
    fehler = tests_ausfuehren()

    print("\n3. dist/lav-ingest.zip")
    soll = zip_soll()
    ist = zip_ist(DIST)
    zip_veraltet = ist != soll
    if a.nur_tests:
        print("   übersprungen (--nur-tests)" + (" · ZIP passt nicht zum Quellstand" if zip_veraltet else ""))
    elif a.pruefen:
        if zip_veraltet:
            neu = sorted(set(soll) - set(ist or {}))
            weg = sorted(set(ist or {}) - set(soll))
            anders = sorted(n for n in set(soll) & set(ist or {}) if soll[n] != ist[n])
            print("   VERALTET – python tools/build.py ausführen und dist/ mitcommitten")
            for titel, liste in (("fehlt im ZIP", neu), ("zu viel im ZIP", weg), ("anderer Inhalt", anders)):
                if liste:
                    print(f"   {titel}: {', '.join(liste)}")
        else:
            print("   aktuell")
    elif zip_veraltet:
        daten = zip_bytes(soll)
        DIST.parent.mkdir(exist_ok=True)
        DIST.write_bytes(daten)
        groesse = f"{len(daten):,}".replace(",", "’")
        print(f"   neu gebaut: {len(soll)} Dateien, {groesse} Bytes")
    else:
        print("   unverändert (Inhalt entspricht dem Quellstand)")

    if DIST.exists() and not a.pruefen:
        sha = hashlib.sha256(DIST.read_bytes()).hexdigest()
        text = (f"lav-ingest.zip  SHA-256 {sha}\n"
                f"Kurzform (erste 8 Zeichen, wie im README): {sha[:8]}\n"
                f"Dateien im ZIP: {len(zip_ist(DIST))}\n")
        if not SUMMEN.exists() or SUMMEN.read_text(encoding="utf-8") != text:
            SUMMEN.write_text(text, encoding="utf-8", newline="\n")
        print(f"   SHA-256 beginnt mit {sha[:8]}")

    print("\nERGEBNIS: ", end="")
    probleme = []
    if fehler:
        probleme.append("Tests fehlgeschlagen: " + ", ".join(fehler))
    if a.pruefen and veraltet:
        probleme.append("abgeleitete Dateien veraltet")
    if a.pruefen and zip_veraltet:
        probleme.append("dist/lav-ingest.zip veraltet")
    print("alles in Ordnung" if not probleme else " · ".join(probleme))
    return 1 if probleme else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        print(f"FEHLER: {type(e).__name__}: {e}")
        sys.exit(2)
