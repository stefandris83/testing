# Plattform: Copilot Studio mit GitHub Copilot Harness

Stand: 10.11.2026. Was über die Plattform im Helsana-Tenant **gemessen oder beobachtet** ist. Regel: Nichts annehmen,
was hier nicht steht – offene Punkte als Test im Tenant formulieren und das Ergebnis hier nachtragen (mit Datum).
Hintergrund und Quellen vom 14.10.2026: [hintergrund/blaupause-v3.1.md](hintergrund/blaupause-v3.1.md), Abschnitte 3.3 und C.

## Umgebung

| Thema | Befund | Quelle / Datum |
|---|---|---|
| Harness | GitHub Copilot Harness in Copilot Studio; Sandbox mit Python 3.12; pdfplumber, pypdf, pypdfium2 vorhanden; kein Netzwerk | Plattformtest P3, Oktober 2026 |
| Modell der Agenten | GPT-6 Astra | Einrichtung |
| Ablage | nicht dauerhaft: alles pro Gespräch; Ergebnisse herunterladen und in SharePoint ablegen | Microsoft, bestätigt |
| Pfade | Skills unter `/app/skills/<name>/`; Uploads unter `/app/uploads/<name>-<kennung>.<endung>`; erzeugte Dateien z. B. `/app/created/` | beobachtet, Nov. 2026 |
| Skripte im Skill | laufen direkt aus `/app/skills/<name>/scripts/`; Ersatzweg `references/skripte.md` bisher nicht nötig | Phase A und B |
| Download | md, csv, zip herunterladbar, Umlaute korrekt | P6 |
| Lesegrenze | Dateien bis 45’000 Bytes werden vollständig gelesen (Lesetest Stufe c, zwei Durchgänge) → `TEILGROESSE = 45000` | P2 |
| Länge einer Antwort | 3 Etappen à 5 Seiten (22 min) liefen durch, die 4. nicht mehr; Agent unterbrach kontrolliert → `ETAPPEN_PRO_ANTWORT = 2` | Phase B, Probelauf LAV-T02 |
| Dauer Ingest | LAV-T01 19 Seiten 17,5 min; LAV-T02 27 Seiten 38 min; LAV-T03 102 Seiten rund 3½ h inkl. Pausen | M1, Phase B, M2 |
| Credits | Anzeige im Testbereich; Gespräch «Paket bauen» mit 3 Studien: 15.31 Credits | 10.11.2026 |
| Memory | in allen Agenten aus | Einrichtung |
| Knowledge | nicht verwendet (Entscheid E1) | – |

## Skills

- Skill = ZIP mit `SKILL.md` (Frontmatter `name`, `description`) zuoberst und Begleitdateien (`references/`, `scripts/`,
  `assets/`). Die Variante mit SKILL.md auf oberster Ebene funktioniert (P1); Unterordner unter references/ werden
  gefunden (P8).
- **Die `description` entscheidet, ob der Agent die Skill überhaupt lädt.** Befehle, die nicht nach einer
  Fachfrage aussehen («Paket selbst prüfen»), wurden ohne Nennung in der description nicht erkannt (10.11.2026:
  «Welches Paket möchtest du prüfen?»). Darum nennen beide Beschreibungen ihre Befehle; die Wartungsbefehle haben
  zusätzlich die Form «Wartung lav-learning-library: …», die die Skill beim Namen nennt.
- Nach dem Ersetzen einer Skill ein **neues Gespräch** beginnen.
- Grenzen für Harness-Agenten sind nicht dokumentiert. Für Agent Builder: 8 Skills, 50 MB je ZIP, 350 Dateien,
  3 Ordnerebenen. Für unser Paket mit 60 Studien heisst das: ≈ 60 × 3–8 Teile + Katalog/Cards → im Tenant messen
  (Testpaket mit 9 Mini-Skills, 400 Dateien, 4 Ordnerebenen ist geplant).

## Uploads im Chat und der Vorverarbeitungs-Hook

- Uploads sind möglich (Vorschaufunktion). Vor dem ersten Befehl, der den Pfad einer hochgeladenen Datei nennt, verlangt
  ein Hook eine Vorverarbeitung: `Denied by preToolUse hook: Before working with <pfad>, preprocess it with the
  analyzing-<typ> skill`. Bei PDFs klappt das: Vorverarbeitung mit analyzing-pdf, dann Befehl wiederholen.
- **ZIP-Dateien erkennt die Plattform fälschlich als CSV** → verlangt analyzing-csv → das scheitert → jeder Befehl mit
  dem ZIP-Pfad bleibt gesperrt (9.11.2026, «Paket prüfen» und erster Versuch «Paket bauen»). Das blosse Auflisten
  eines ZIP klappte einmal (Upload-Test, 33 Dateien).
- **Lösung:** Das Skript findet die Uploads selbst (`paket_bauen.py --uploads`); im Befehl steht kein Upload-Pfad.
  So läuft «Paket bauen» seit 10.11.2026. Der Agent darf die ZIPs vorher nicht öffnen, auflisten oder entpacken.
- analyzing-csv scheiterte am 10.11.2026 auch an einer echten CSV mit mehrzeiligen Feldern; `belege.py` las die Datei
  danach trotzdem korrekt.
- **Offenes Risiko:** «Fortsetzen» (Zwischen-ZIP entpacken) und «Wiki aufbereiten» (Paket-ZIP) nennen noch
  Upload-Pfade. Scheitern sie, dieselbe Lösung übertragen (Skript sucht im Upload-Ordner).
- ZIPs lassen sich aus dem Helsana-Netz nicht per E-Mail verschicken; Inhalte dann flach (ohne ZIP) weitergeben.

## Testen und Auswerten in Copilot Studio

- **Evaluate** bietet für Harness-Agenten nur «General quality», keinen Vergleich mit Sollantworten → Golden Set
  manuell bzw. per CSV auswerten (`belege.py`, Bewertungsraster in qualitaet.md).
- Transkripte der Gespräche lassen sich 29 Tage lang herunterladen (für den Pilot monatlich exportieren).
- Debug-Modus im Testbereich zeigt Skill-Aufrufe und Credits.

## Kanäle und Einbindung (Stand 14.10.2026, nicht neu geprüft)

Harness-Agenten: Microsoft 365 Copilot, Teams, Demo-Website, Web-App (iframe). Nicht verfügbar: SharePoint, Direct Line,
MCP-Client; Agents SDK unterstützt den Harness derzeit nicht. Embed-Code nur ohne Authentifizierung → verletzt G2.
Standard: Agent verlinken (Teams / M365 Copilot); einbetten nur nach Test P10.

## Ergebnisse der Plattformtests P1–P10 (Phase A, Oktober 2026)

| Test | Ergebnis |
|---|---|
| P1 Skill-Upload | bestanden (ZIP mit SKILL.md zuoberst) |
| P2 Lese-Limit | Stufe c (45’000 Bytes) in beiden Durchgängen bestanden |
| P3 Python | bestanden: Python 3.12, pdfplumber, pypdf, pypdfium2; Skripte direkt aus dem Skill |
| P4/P5 Upload, Ablesen | Einzelergebnisse nicht dokumentiert. Seither belegt: PDF-Upload mit Vorverarbeitung funktioniert, Ablesen am Seitenbild klappt (M1: 1’325 von 1’328 Grafikzellen wie Referenz) |
| P6 Download | bestanden (md, csv, zip) |
| P7 Kosten | nicht dokumentiert – beim Spike messen |
| P8 Library-Paket | bestanden (Phase C: G01, G04, G08, G11 korrekt) |
| P9 Ingest-Durchlauf | erster Lauf an der Transkriptionsqualität gescheitert (Skill korrigiert), zweiter bestanden; «Fortsetzen» funktioniert |
| P10 Einbindung | nicht durchgeführt (optional) |

Hinweis: Die Ergebnisse von Phase A stammen aus dem Projektstand vom 9.11.2026; Einzelprotokolle liegen nicht im
Repository.
