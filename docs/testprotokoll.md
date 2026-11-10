# Testprotokoll

Alle Tests mit Datum und Ergebnis, neueste zuoberst. Neue Einträge oben anfügen. Nur öffentliche Teststudien
(LAV-T01–T03) mit Inhalt; bei internen Studien nur IDs und Kennzahlen (Anzahl Fragen, bestanden, Befunde).

## 10.11.2026 – Lokale Testsuite im Repository
`python tools/build.py`: alle Tests bestanden (GitHub Actions ebenfalls, inkl. Teil B mit den Original-PDFs).
- `test_evaluate_csv.py` (5 Prüfungen): Evaluate-Format, G11 ohne Kontrollwörter weggelassen.
- `test_belege.py` (10 Prüfungen): Basis M6 123 Zahlen 0 nicht gefunden; eingebaute Fehler erkannt (19→15, 7’783→7’738,
  52’916→25’916, 30→33, falsche Seite, fehlender Beleg, Tabelle mit Beleg danach 9’021→9’201); Grenze «berechnet» markiert.
- `test_ingest_skripte.py` (19 Prüfungen, Regressionstest Blaupause 10.5): aufteilen.py, paket.py mit 5 Manipulationen,
  wiki.py, skripte.md; mit PDFs: inventar.py, pruefen.py gegen Referenztranskripte (nur begründete Seiten: T01 6, 13;
  T02 13, 14, 15, 21, 26), 5 eingebaute Fehler alle erkannt.
- `test_paket_bauen.py` (17 Prüfungen): drei ZIPs, Sammel-ZIP, `--uploads`, Update mit Ersetzen, Freigabe, Entfernen,
  31 Studien mit Aufteilung und 60 ersetzten Kontrollwörtern, doppelte ID, falsche Card-Zahl.

## 10.11.2026 – Kette im Tenant (Paket bauen → Paket selbst prüfen → Belege prüfen)
- «Paket bauen» mit LAV-T01–T03_ingest.zip (Ingest-Skill 4f94d9de): ohne Befunde; 3 Studien, 12 Teile;
  Verwechslungshinweise T01↔T02 ergänzt; alle Cards ohne Freigabe (Testpaket). Erster Versuch am 9.11. scheiterte an
  der ZIP-Sperre (→ E27).
- «Paket selbst prüfen»: Kurzbefehl allein wurde nicht erkannt («Welches Paket …?», → E29); mit ausdrücklicher
  Formulierung: «Keine Befunde.» (3 Studien, 12 Teile, 1 Katalog-, 1 Card-Datei).
- «Belege prüfen» mit den v1.1-Antworten (ohne G11): 167 Zahlen, 154 gefunden, 0 nicht gefunden, 1 in Aussage
  «nicht belegt», 12 ohne Seitenangabe (G12 Katalog, G09 Rückfrage, G10 Einleitungssätze vor Tabellen) – identisch
  mit dem lokalen Lauf. analyzing-csv schlug fehl, Skript lief trotzdem.
- Offen: Kurzform `Wartung lav-learning-library: Paket selbst prüfen` mit einem Paket aus der aktuellen Ingest-Skill.

## 9.11.2026 – Regression Library v1.1 (G01–G15)
Paket `lav-learning-library_3-studien_v1.1.zip`. **15/15 bestanden, 0 kritische Fehler.**
- G13 (falsche Prämisse): zuerst richtiggestellt, 28 % → 60 %, +32 Prozentpunkte «berechnet», Methodenwechsel genannt.
- G14 (Ursache): «dürfte» als Deutung der Autoren; zusätzlich korrekt LAV-T03 S. 48 (Auswirkungen noch nicht sichtbar).
- G15 (Richtung): 75 % → 87 %, +12 Prozentpunkte «berechnet», Methodenhinweis.
- belege.py: 167 Zahlen, 0 nicht gefunden. Textaussagen von G10/G13/G14 von Claude an den Seiten geprüft: korrekt,
  inkl. Quellenkonflikt Interpharma-Vorwort (Preise sanken) gegen Arzneimittelreport (Einstiegspreise +74 %).
- Kleine Mängel: G10 Belege nach statt vor Tabellen (5 Tabellen); G10 «Mengenausweitungen als Ursache» leicht
  verallgemeinert (Report S. 17: Marktausdehnungen und teure Neueinführungen); G08 «nicht belegt» auf gezielte Suche
  gestützt, ehrlich deklariert.
- Statistik: 0/15 → Fehlerrate mit 95 % Sicherheit unter rund 18 % (Entwicklungstest).

## 9.11.2026 – M5/M6 Mehrstudientest (G01–G12)
12/12 bestanden, 0 kritische Fehler; alle Zahlen auf den zitierten Seiten im Paket und in der Textebene der PDFs.
G11: alle 8 Kontrollwörter von LAV-T03 korrekt → eine Studie mit 102 Seiten wird vollständig gelesen.

## 9.11.2026 – M4 Paketprüfung im Ingest-Agenten
«Paket prüfen» reproduzierbar blockiert: Plattform behandelt das hochgeladene ZIP als CSV. → Wartungsbefehl
«Paket selbst prüfen» (E22), später «Paket bauen» mit `--uploads` (E27).

## Nov. 2026 – M3 Paket mit drei Studien
Von Hand gebaut (Claude), `paket.py` ohne Befunde → `testdaten/library/lav-learning-library_3-studien_v1.1.zip`.

## Nov. 2026 – M2 Ingest LAV-T03 (Arzneimittelreport 2024, 102 Seiten)
8 Teile, rund 3½ h inkl. Pausen. Prüfskript 0 Befunde; gemeldete Quellenwidersprüche stehen tatsächlich im Original;
Kantonskarte S. 19 per Pixelvergleich korrekt.

## Nov. 2026 – M1 Ingest LAV-T01 (Gesundheitsmonitor 2024, 19 Seiten)
17,5 min. Der Agent berechnete unbeschriftete Grafikwerte selbst aus Vektorpfaden: 1’325 von 1’328 Zellen identisch mit
Claudes unabhängiger Referenz, 3 um 1 Punkt verschieden (`tools/grafikvergleich.py`).

## Okt./Nov. 2026 – Phase C (Library nur LAV-T02)
G01, G04, G08, G11 korrekt. Beleg «[LAV-T02, S. 12]» erscheint als Text.

## Okt./Nov. 2026 – Phase B (Ingest LAV-T02, 27 Seiten)
- Erster Lauf durchgefallen: ungeordneter Rohtext auf Doppelseiten, Serien auf S. 9 vertauscht → Skill und Prüfskript
  korrigiert (E18).
- Zweiter Lauf: 84 % der Referenzabsätze exakt bzw. ≥ 90 % gleich, beschriftete Werte korrekt, 38 min für 27 Seiten.
  Abbruch nach 4 Etappen (S. 20) → ETAPPEN_PRO_ANTWORT = 2 (E17). Fortsetzen mit Zwischen-ZIP funktioniert.

## Okt. 2026 – Phase A (Plattformtest)
Bestanden: Python 3.12, pdfplumber/pypdf/pypdfium2 vorhanden, Skripte laufen direkt aus dem Skill, Download md/csv/zip,
Teilgrösse 45’000 Bytes gemessen. Einzelheiten in plattform.md.

## 14.10.2026 – Lokale Skripttests (Blaupause v3.1, Abschnitt 2.3)
Fehlerinjektion LAV-T02 5/5 erkannt; Referenztranskripte T01/T02 nur begründbare Meldungen (Wortabdeckung min. 96,6 %);
Paketprüfung mit Manipulationen alle erkannt; Ersatzweg über skripte.md funktioniert; wiki.py ohne Kontrollwort.
