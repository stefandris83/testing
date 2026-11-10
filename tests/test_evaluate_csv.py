"""Test für tools/evaluate_csv.py (Golden Set → Testsatz für Evaluate in Copilot Studio).

Aufruf:  python tests/test_evaluate_csv.py
"""
import csv
import importlib.util
import io
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("evaluate_csv", ROOT / "tools" / "evaluate_csv.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
fehler = 0


def check(name, ok, info=""):
    global fehler
    print(f"[{'OK' if ok else 'FEHLER'}] {name}")
    if not ok:
        fehler += 1
        print("   ", info)


text, weg, n = mod.umwandeln(mod.STANDARD.read_text(encoding="utf-8-sig"))
zeilen = list(csv.reader(io.StringIO(text)))
check("Kopfzeile genau «Question,Expected response», ohne BOM", text.startswith("Question,Expected response\n"), text[:40])
check("G11 (Lesebeweis mit Kontrollwörtern) weggelassen, 14 Fragen", weg == ["G11"] and n == 14 and len(zeilen) == 15, (weg, n))
check("kein Kontrollwort im Testsatz", not re.search(r"\b[A-ZÄÖÜ]{3,}-\d{2}\b", text))
check("jede Zeile genau zwei Spalten, Fragen ≤ 1’000 Zeichen",
      all(len(z) == 2 for z in zeilen) and all(len(z[0]) <= 1000 for z in zeilen[1:]))
erste = zeilen[1]
check("Umlaute und Apostroph bleiben erhalten", "’" in text and "ä" in text, erste)

print("\nErgebnis:", "alle Tests bestanden" if not fehler else f"{fehler} Test(s) fehlgeschlagen")
sys.exit(1 if fehler else 0)
