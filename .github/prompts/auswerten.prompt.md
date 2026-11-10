---
description: Ergebnisse aus Copilot Studio auswerten (Screenshot, Agentenantwort, CSV mit Antworten, Fehlermeldung)
agent: agent
argument-hint: Screenshot, Text oder CSV aus dem Tenant anhängen
---

# Ergebnisse aus dem Tenant auswerten

Eingabe: was der Mensch aus Copilot Studio mitbringt – Screenshot, Antworttext, CSV mit Antworten, Fehlermeldung.

0. **Sicherheit zuerst.** Betrifft die Eingabe eine interne Studie (nicht LAV-T01–T03) und enthält sie Inhalte (Titel,
   Zahlen, Zitate, Antworttext)? Dann nicht auswerten, nichts speichern, um eine Fassung nur mit Kennzahlen bitten.
   Fehlermeldungen ohne Inhalt und Kennzahlen («0 nicht gefunden») sind erlaubt.
1. **Einordnen:** Welcher Agent, welcher Befehl, welcher Skill-Stand? Erwartung aus `docs/bedienkarte.md`,
   `docs/stand.md` (offene Schritte) oder dem Golden Set (`testdaten/golden-set/`).
2. **Plattformverhalten** (Sperren, Hook-Meldungen, Abbrüche, Dauer, Credits): mit `docs/plattform.md` vergleichen.
   Neues mit Datum dort nachtragen. Ursache benennen; Lösung im Skill oder Skript bevorzugen, statt dem Menschen
   dauerhaft Umwege aufzubürden.
3. **Antworten zu Teststudien prüfen:**
   a. Zahlen: CSV mit Spalten `id` und `Antwort Agent` → `python tools/belege_lokal.py <csv>`; erwartet
      «nicht gefunden: 0». Zeilen «berechnet – Rechnung prüfen» selbst nachrechnen.
   b. Inhalt: gegen `sollantwort` und `bestanden_wenn`; Textaussagen am Volltext prüfen (in
      `testdaten/ingest/LAV-T0x_ingest.zip` unter `volltext/`, Seiten beginnen mit `[[Seite n/N …]]`), bei Bedarf an
      der PDF (`testdaten/pdf/`, `python tools/pdfs_holen.py`).
   c. Je Frage bewerten nach dem Raster in `docs/qualitaet.md`: bestanden ja/nein; Mängel kritisch oder klein, je mit
      Seite.
   d. Statistik: 0 Fehler in n Fragen → obere 95-%-Grenze `1 − 0.05^(1/n)`. Eine Wiederholung ist keine neue Stichprobe.
4. **Ursache bei Fehlern:** Skill-Anweisung, Paketdaten (Transkript, Card), Werkzeug oder Plattform? Vorschlag mit
   Aufwand; nach Zustimmung umsetzen (Ablauf `release.prompt.md`).
5. **Nachführen:** `docs/testprotokoll.md` (neuester Eintrag oben), `docs/stand.md`, falls nötig `docs/plattform.md`
   und `docs/entscheide.md`.
6. **Antwort an den Menschen:** Ergebnis in einem Satz, dann die Mängel, dann der nächste Schritt mit exakter Eingabe.
