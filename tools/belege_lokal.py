"""Belegprüfung von Agentenantworten zu den öffentlichen Teststudien – lokal, ohne Copilot Studio.

Aufruf:  python tools/belege_lokal.py <antworten.csv | antwort.md> [--ausgabe belegpruefung.csv]

Macht dasselbe wie der Wartungsbefehl «Belege prüfen» im Library-Agenten: jede Zahl einer Antwort wird gegen die
zitierte PDF-Seite im Volltext geprüft. Als Paket dient testdaten/library/lav-learning-library_3-studien_v1.1.zip
(LAV-T01 bis LAV-T03), als Skript der aktuelle Stand von src/lav-learning-library/scripts/belege.py.
CSV: Semikolon, Spalte mit «Antwort» im Namen (nicht «soll»), Spalte «id». Nur für die Teststudien –
Antworten zu internen Studien gehören nicht in dieses Repository und nicht in diesen Chat.
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAKET = ROOT / "testdaten" / "library" / "lav-learning-library_3-studien_v1.1.zip"
SKRIPTE = ROOT / "src" / "lav-learning-library" / "scripts"


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    tmp = pathlib.Path(tempfile.mkdtemp())
    try:
        skill = tmp / "lav-learning-library"
        with zipfile.ZipFile(PAKET) as z:
            z.extractall(skill)
        shutil.copytree(SKRIPTE, skill / "scripts", dirs_exist_ok=True)
        args = [pathlib.Path(sys.argv[1]).resolve().as_posix()] + sys.argv[2:]
        if "--ausgabe" not in args:
            args += ["--ausgabe", "belegpruefung.csv"]
        return subprocess.run([sys.executable, "-X", "utf8", "-I", str(skill / "scripts" / "belege.py"), *args]).returncode
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
