"""Lädt die drei öffentlichen Test-PDFs (LAV-T01 bis LAV-T03) nach testdaten/pdf/ und prüft sie.

Aufruf:  python tools/pdfs_holen.py

Die PDFs liegen nicht im Repository (Rechte der Herausgeber); testdaten/pdf/ steht in .gitignore.
Gebraucht für: Teil B von tests/test_ingest_skripte.py, Nachprüfen von Agentenantworten an der Original-PDF,
Ingest-Tests im Tenant. Klappt der Download nicht (Proxy, Link geändert): PDF im Browser laden und unter dem
genannten Dateinamen in testdaten/pdf/ ablegen. Weicht die Prüfsumme ab, hat der Herausgeber die Datei geändert:
Seitenzahlen und Referenzwerte der Tests stimmen dann eventuell nicht mehr.
"""
import hashlib
import pathlib
import sys
import urllib.parse
import urllib.request

ZIEL = pathlib.Path(__file__).resolve().parent.parent / "testdaten" / "pdf"
PDFS = [
    ("LAV-T01", "gesundheitsmonitor-2024.pdf", 19,
     "https://www.interpharma.ch/wp-content/uploads/2024/06/LY-IPH.01.24.001-–-Gesundheitsmonitor-2024_d_web.pdf",
     "1978f26b5a163ffcf8d2da91ae6d8e384cec61662db410d92ced37dc15d78c3f"),
    ("LAV-T02", "gesundheitsmonitor-2025.pdf", 27,
     "https://www.interpharma.ch/wp-content/uploads/2025/06/LY-IPH.01.25.001-–-Gesundheitsmonitor-2025_d_250605_def.pdf",
     "d9e7b408de86c38c8453524802d119db1bf77d508717a335636c9d2f5d5dc907"),
    ("LAV-T03", "arzneimittelreport-2024.pdf", 102,
     "https://www.helsana.ch/dam/de/pdf/helsana-gruppe/publikationen/arzneimittelreport-2024.pdf",
     "114b4b40c708b314c489dcd8edbeeee81011874eeb504ad45fcefd680c13124b"),
]

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def main():
    ZIEL.mkdir(parents=True, exist_ok=True)
    probleme = 0
    for sid, name, seiten, url, sha in PDFS:
        f = ZIEL / name
        if not f.exists():
            teile = urllib.parse.urlsplit(url)
            sicher = urllib.parse.urlunsplit(teile._replace(path=urllib.parse.quote(teile.path)))
            try:
                req = urllib.request.Request(sicher, headers={"User-Agent": "Mozilla/5.0 (LAV-Testdaten)"})
                with urllib.request.urlopen(req, timeout=60) as r:
                    f.write_bytes(r.read())
            except Exception as e:  # noqa: BLE001
                print(f"{sid}: Download fehlgeschlagen ({type(e).__name__}: {e}). Von Hand laden: {url} → {f}")
                probleme += 1
                continue
        ist = hashlib.sha256(f.read_bytes()).hexdigest()
        if ist == sha:
            print(f"{sid}: {name} vorhanden, Prüfsumme stimmt ({seiten} Seiten)")
        else:
            print(f"{sid}: {name} vorhanden, aber ANDERE Prüfsumme als beim Test (Datei vom Herausgeber geändert?)")
            probleme += 1
    return 1 if probleme else 0


if __name__ == "__main__":
    sys.exit(main())
