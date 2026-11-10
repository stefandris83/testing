# Qualitätssicherung

Stand: 10.11.2026. Höchstes Ziel des Projekts ist Qualität: richtige Studie, vollständig gelesen, belegte Zahlen,
sichtbare Lücken – ohne das System unnötig kompliziert zu machen.

## Prüfebenen

| Ebene | Werkzeug | Prüft | Wann |
|---|---|---|---|
| Transkript | `pruefen.py` | jede Seite vorhanden, Seitenmarker, Zahlen mit Häufigkeit, Wortabdeckung ≥ 95 %, Grafikblöcke mit Wertstatus, unbearbeiteter Rohtext | nach jeder Etappe und am Schluss |
| Unbeschriftete Grafikwerte | Mensch am Seitenbild (`grafiken-abgelesen.txt`) | abgelesene Werte | Spike: alle; danach jede fünfte, wenn Abweichung ≤ 3 Prozentpunkte und nichts vertauscht |
| Study Card | Research (Freigabe) + `paket.py` | jede Zahl gegen den Volltext; Zahlen neben `[S. n]` müssen auf Seite n stehen | vor der Freigabe |
| Library-Paket | `paket.py` (in «Paket bauen» und «Paket selbst prüfen») | Struktur, Schlusszeilen, Kontrollwörter eindeutig, Grössen, Teile lückenlos, Katalogzeile, Cards, «Nicht verwechseln mit» | jedes Paket |
| Antworten | Golden Set, `belege.py`, Mensch | Studie, Zahlen, Belege, Lücken, Prämissen, Ursachen | nach jedem Paket-Update und nach Plattformänderungen |
| Skripte und Skills | `tests/` über `python tools/build.py` | Regression | nach jeder Änderung im Repository |

## Golden Set

Format (UTF-8 mit BOM, Semikolon): `id;typ;studien;frage;sollantwort;belege;bestanden_wenn`. Antworten des Agenten
kommen in eine zusätzliche Spalte `Antwort Agent`.

| Datei | Inhalt |
|---|---|
| `testdaten/golden-set/golden-set-mehrstudientest.csv` | G01–G15 zu LAV-T01–T03 (aktuell) |
| `testdaten/golden-set/golden-set-beispiel_LAV-T01-T02.csv` | 12 Beispielfragen aus der Blaupause v3.1 |
| `tests/fixtures/m6-antworten.csv`, `v11-antworten.csv` | echte Antworten des Agenten (M6, v1.1-Regression) |

**Achtung:** Die Golden-Set-Dateien enthalten Kontrollwörter (Lesebeweis G11). Nie in einen Agenten hochladen. Für
«Belege prüfen» im Agenten nur die Spalten `id` und `Antwort Agent` hochladen und Antworten mit Kontrollwörtern
weglassen.

Fragetypen in G01–G15: Detail mit beschrifteter Grafik · Detail mit Region · gestapelter Balken in der Dokumentmitte ·
Wert ohne Beschriftung (Falle Region) · Zeitreihe · Fangfrage «nur Klasse belegt» · Karte · Fangfrage Nachbarthema ·
Mehrdeutigkeit zweier Ausgaben · Synthese über Studien · Lesebeweis (alle 8 Kontrollwörter von LAV-T03) · Katalog ·
falsche Prämisse · Ursache · Richtung und Prozentpunkte.

Lehre aus dem Projekt: Claudes eigene Sollantworten hatten Fehler (G07: Klasse «> CHF 1’100» gibt es nicht; G09
unvollständig). **Sollantworten für die Abnahme schreibt Research aus der PDF**, nicht eine KI.

## Ablauf einer Golden-Set-Runde

1. Library-Agent mit dem zu prüfenden Paket; je Frage ein neues Gespräch (sonst liest der Agent aus dem Verlauf).
   Automatisch: Testsatz mit `python tools/evaluate_csv.py` erzeugen und im Reiter «Evaluate» importieren (jede Frage
   läuft einzeln); Ergebnisse als CSV exportieren. Lesebeweis (G11) bleibt manuell.
2. Antworten wörtlich in die Spalte `Antwort Agent` kopieren (Rückfragen des Agenten und die Antwort darauf mit).
3. Zahlen prüfen: im Agenten «Wartung lav-learning-library: Belege prüfen» (bereinigte CSV) oder lokal
   `python tools/belege_lokal.py <csv>` (nur Teststudien). Erwartung: «nicht gefunden: 0».
4. Inhalt bewerten gegen `bestanden_wenn` und das Raster unten; bei Teststudien Textaussagen am Volltext
   (`testdaten/ingest/*.zip`) bzw. an der PDF prüfen.
5. Ergebnis in `docs/testprotokoll.md`.

## Bewertungsraster (Vorschlag für die Abnahme)

Je Aussage: **belegt** · **falsch wiedergegeben** · **nicht belegt** (Aussage ohne Grundlage) · **nicht prüfbar**;
jeder Mangel **kritisch** oder **klein**.
- Kritisch: falsche Zahl, falsche Studie oder Ausgabe, erfundene Aussage, Ursache als Tatsache dargestellt, falsche
  Prämisse übernommen, Lücke verschwiegen.
- Klein: Beleg an falscher Stelle, Basis oder Gruppe unvollständig genannt, leichte Verallgemeinerung, fehlender
  Methodenhinweis.
Eine Antwort besteht, wenn sie keinen kritischen Mangel hat und das Kriterium `bestanden_wenn` erfüllt.

## Statistik

- Einheit ist die **Antwort** (Aussagen derselben Antwort hängen zusammen, sie sind keine unabhängige Stichprobe).
- 0 Fehler in n unabhängigen Fragen → Fehlerrate mit 95 % Sicherheit unter `1 − 0.05^(1/n)` (≈ 3/n, «Rule of Three»):
  n = 12 → 22 % · 15 → 18 % · 40 → 7,2 % · 60 → 4,9 %.
- Bei k Fehlern: exaktes Clopper-Pearson-Intervall rechnen, nicht schätzen.
- Eine Wiederholung derselben Fragen (Regression) ist keine neue Stichprobe.
- Entwicklungstests mit drei Teststudien sind keine Abnahme.

## Abnahmekonzept vor dem Rollout (Stand 9.11.2026)

- Rund **60 echte Fragen**, geschichtet: A Textaussagen 15 · B Zahlen 15 · C studienübergreifend 10 ·
  D nicht abgedeckt 10 · E falsche Prämisse oder Verwechslung von Ausgaben 10.
- Fragen **blind erhoben**: Interviews mit 8–10 künftigen Nutzerinnen und Nutzern, bevor sie den Agenten kennen.
- Sollantworten durch Research aus der PDF; Bewertung gegen die PDF; 20 % doppelt bewertet, Übereinstimmung
  Cohens Kappa ≥ 0.7.
- **Schwellen vorab schriftlich** festgelegt und unterschrieben. Vorschlag (Blaupause v3.1): Fangfragen und Lesebeweis
  100 %; keine erfundene Zahl; Detailfragen ≥ 90 % mit richtiger Seite. Zusätzlich Obergrenze auf Antwortebene
  (0 kritische Fehler in 60 Antworten → Fehlerrate < 5 % mit 95 % Sicherheit).
- Evaluate kann für Harness-Agenten keine Sollantworten vergleichen → Auswertung per CSV.
- Pilot: Transkripte monatlich exportieren (29 Tage verfügbar) und eine Stichprobe nachprüfen.

## Simulierte Fragensammlung (geplant, nächster Schritt)

Rund 40 Fragen in Nutzersprache zu LAV-T01–T03 mit Sollantworten aus dem Volltext – **nur für Entwicklung und
Regression**, nie für die Abnahme. Vorgehen: [.github/prompts/testfragen.prompt.md](../.github/prompts/testfragen.prompt.md).

## Grenzen der automatischen Prüfung

- `belege.py` prüft, ob eine Zahl auf der zitierten Seite steht – nicht, ob sie dort zur richtigen Zeile, Gruppe
  oder Ausgabe gehört. Eine falsche Zahl, die zufällig auch auf der Seite steht, fällt nicht auf (z. B. 18 statt 19
  auf LAV-T02 S. 12). Selbst berechnete Werte werden nur markiert («berechnet – Rechnung prüfen»). Richtung,
  Population und Ursache-Aussagen beurteilen Menschen. Tabellen ohne eigenen Beleg erben den Beleg des Absatzes davor,
  ersatzweise danach (Spalte `beleg_aus`).
- `pruefen.py` sieht unbeschriftete Grafikwerte nicht (sie stehen nicht in der Textebene) und meldet bei überlappenden
  Beschriftungen einzelne Fehlalarme, die begründet werden.
- `paket.py` prüft in Cards nur Zahlen, nicht den Wortlaut.

## Bewusst zurückgestellt

- «Zitat zuerst» (der Agent zitiert vor jeder Aussage wörtlich und prüft sich selbst): erst, wenn die Abnahme Fehler
  zeigt, die damit verhindert würden – macht Antworten länger und teurer.
- Variante A2 für grosse Studien ([varianten/fall-a2-grosse-studien.md](varianten/fall-a2-grosse-studien.md)):
  nicht nötig, solange LAV-T03 (102 Seiten, 8 Teile) vollständig gelesen wird.
