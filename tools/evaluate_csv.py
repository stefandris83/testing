"""Golden Set → Testsatz für «Evaluate» in Copilot Studio (CSV mit den Spalten Question, Expected response).

Aufruf:  python tools/evaluate_csv.py [<golden-set.csv>] [--ausgabe <datei.csv>]
Ohne Argument: testdaten/golden-set/golden-set-mehrstudientest.csv → testdaten/golden-set/evaluate_<name>.csv

Format laut Microsoft: Kopfzeile genau `Question,Expected response`, Komma als Trennzeichen, höchstens 100 Fragen,
je Frage höchstens 1’000 Zeichen, Datei höchstens 5 MB. Geschrieben wird UTF-8 ohne BOM (ein BOM würde die erste
Spaltenüberschrift verfälschen).
Fragen, deren Sollantwort Kontrollwörter enthält (Lesebeweis wie G11), werden weggelassen: Kontrollwörter gehören nicht
nach Copilot Studio. Den Lesebeweis weiterhin von Hand prüfen.
"""
import argparse
import csv
import io
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
STANDARD = ROOT / "testdaten" / "golden-set" / "golden-set-mehrstudientest.csv"
KONTROLLWORT = re.compile(r"\b[A-ZÄÖÜ]{3,}-\d{2}\b")


def umwandeln(text):
    """Liefert (CSV-Text, weggelassene IDs, Anzahl Fragen)."""
    zeilen = list(csv.DictReader(io.StringIO(text), delimiter=";"))
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["Question", "Expected response"])
    weg, n = [], 0
    for z in zeilen:
        frage, soll = (z.get("frage") or "").strip(), (z.get("sollantwort") or "").strip()
        if not frage:
            continue
        if KONTROLLWORT.search(soll) or KONTROLLWORT.search(frage):
            weg.append(z.get("id", "?"))
            continue
        if len(frage) > 1000:
            raise ValueError(f"Frage {z.get('id')} hat mehr als 1’000 Zeichen")
        w.writerow([frage, soll])
        n += 1
    if n > 100:
        raise ValueError(f"{n} Fragen – Evaluate erlaubt höchstens 100 pro Testsatz")
    return buf.getvalue(), weg, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("golden_set", nargs="?", default=str(STANDARD))
    ap.add_argument("--ausgabe")
    a = ap.parse_args()
    quelle = pathlib.Path(a.golden_set)
    ziel = pathlib.Path(a.ausgabe) if a.ausgabe else quelle.with_name(f"evaluate_{quelle.stem}.csv")
    text, weg, n = umwandeln(quelle.read_text(encoding="utf-8-sig"))
    ziel.write_text(text, encoding="utf-8", newline="")
    print(f"{n} Fragen → {ziel}" + (f" · weggelassen (Kontrollwörter): {', '.join(weg)}" if weg else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
