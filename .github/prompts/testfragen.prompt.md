---
description: Testfragen mit geprüften Sollantworten zu den öffentlichen Teststudien erstellen (nur Entwicklung und Regression)
agent: agent
argument-hint: Anzahl und Schwerpunkt, z. B. «40 Fragen, gemischt»
---

# Testfragen erstellen

Zweck: Entwicklung und Regression. **Nie für die Abnahme** – dafür braucht es echte, blind erhobene Fragen und
Sollantworten von Research aus der PDF (`docs/qualitaet.md`).

Quelle: ausschliesslich die Volltexte der Teststudien LAV-T01–T03 (`testdaten/ingest/LAV-T0x_ingest.zip` → `volltext/`)
und bei Bedarf die PDFs (`testdaten/pdf/`). Kein Weltwissen.

1. **Verteilung** (Standard 40 Fragen): A Textaussagen 10 · B Zahlen 10 (davon mindestens 3 Grafikwerte und 2 Werte
   ohne Beschriftung) · C studienübergreifend 7 · D nicht abgedeckt 7 · E falsche Prämisse oder Verwechslung der
   Ausgaben 2024/2025 6. Fragen in Nutzersprache (Mitarbeitende: kurz, umgangssprachlich, teils ungenau), nicht im
   Wortlaut der Studie. Doppelungen mit `testdaten/golden-set/golden-set-mehrstudientest.csv` vermeiden.
2. **Sollantwort** je Frage aus dem Volltext mit `[LAV-XX, S. n]`, Wertstatus übernehmen («ca.», «berechnet»), Gruppe,
   Basis und Jahr nennen. Bei D: «nicht belegt» und was die nächstliegende Studie tatsächlich enthält.
3. **`bestanden_wenn`** prüfbar: was enthalten sein muss, was nicht vorkommen darf (z. B. falsche Region, falsche Ausgabe).
4. **Jede Zahl der Sollantworten maschinell prüfen:** Hilfs-CSV mit Spalten `id` und `Antwort Agent` (= Sollantwort)
   erzeugen und `python tools/belege_lokal.py <hilfs.csv>` ausführen → «nicht gefunden: 0». Abweichungen korrigieren,
   Hilfs-CSV danach löschen.
5. Keine Lesebeweis-Fragen mit Kontrollwörtern (die gibt es in G11).
6. **Ausgabe:** `testdaten/golden-set/testfragen-simuliert.csv` (UTF-8 mit BOM, Semikolon, Spalten
   `id;typ;studien;frage;sollantwort;belege;bestanden_wenn`, IDs S01 …).
7. **Kurzbericht** an den Menschen: Verteilung, Besonderheiten, wie er die Runde im Tenant fährt (Ablauf
   «Golden-Set-Runde» in `docs/qualitaet.md`); Eintrag in `docs/testprotokoll.md` erst nach der Runde.
