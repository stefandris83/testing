# Sicherheit und Datenregeln

Stand: 10.11.2026. Diese Regeln gelten für Menschen und für jede KI, die in diesem Repository arbeitet.

## Gates (aus der Blaupause v3.1, Abschnitt 4)

| Gate | Bedingung | Status 10.11.2026 |
|---|---|---|
| **G1 Datenfreigabe** | Schriftliche Freigabe von Dateneigner und InfoSec für (a) die Verarbeitung im Ingest-Agenten und (b) die Ablage der Inhalte im Skill des Library-Agenten. Im Skill-ZIP verliert der Inhalt Purview-Label und Berechtigungen pro Person. | offen – ohne G1 keine interne Studie |
| **G2 Nutzerkreis** | Library-Agent nur für den Kreis, der alle enthaltenen Studien sehen darf; Studien mit engerem Kreis nicht ins ZIP. Ingest-Agent nur Pflegeteam. | offen |
| **G3 Verarbeitungsort** | Interne Studien nur im Ingest-Agenten im Helsana-Tenant. Tests ausserhalb nur mit öffentlichen Studien. | gilt |
| **G4 Wiki und Quellordner** | Publizierte Cards und SharePoint-Quellordner tragen das höchste Label der enthaltenen Studien und dieselbe Berechtigung wie Library-Agent bzw. Pflegeteam. | offen (Wiki optional) |
| **G5 Wiki-Werkzeuge und Hosting** | InfoSec-Freigabe für Wiki-Hosting, Ort des Repositorys und GitHub Copilot in VS Code – mit der Regel, dass echte Inhalte nie in den Copilot-Kontext und nie ins Repository gelangen. | offen; bis dahin gilt die Regel unten ohne Ausnahme |

## Was in dieses Repository, in VS Code und in den Copilot-Chat darf

| Erlaubt | Verboten |
|---|---|
| Skills (SKILL.md, Skripte, Vorlagen), Tests, Werkzeuge | Inhalte interner Studien: Titel, Zahlen, Zitate, Seiteninhalte, Cards, Katalog-Einträge, Volltexte |
| Öffentliche Teststudien LAV-T01–T03 und ihre Transkripte | Antworten des Library-Agenten zu internen Studien (auch Ausschnitte, auch in Screenshots) |
| IDs interner Studien (LAV-NN) ohne Titel | Kontrollwort-Listen echter Pakete (`kontrollwoerter_alle.csv` aus dem Tenant) |
| Kennzahlen von Prüfungen (z. B. «167 Zahlen, 0 nicht gefunden», «Paket ohne Befunde, 25 Studien») | Zugangsdaten, Links auf SharePoint-Ordner mit Inhalten, Namen von Personen ausser Rollen |
| Fehlermeldungen der Plattform ohne Studieninhalt | Ingest-ZIPs, Pakete oder PDFs interner Studien |

Fügt jemand trotzdem interne Inhalte in den Chat ein: nicht verarbeiten, nicht zusammenfassen, nicht in Dateien
schreiben; darauf hinweisen und um eine Fassung ohne Inhalt bitten (nur IDs und Kennzahlen).

**Das Repository ist öffentlich.** Alles, was hier committet wird, ist für alle sichtbar und bleibt in der
Git-Historie, auch nach dem Löschen. Vor jedem Commit prüfen, ob etwas aus der rechten Spalte dabei ist.
`.gitignore` blockiert die Ordner `intern/` und `testdaten/pdf/` als Sicherheitsnetz – das ersetzt die Regel nicht.

## Kontrollwörter

- Kontrollwörter beweisen, dass der Agent eine Datei bis zum Ende gelesen hat. Kennt der Agent sie vorher, ist der
  Test wertlos.
- Nie in einen Copilot-Studio-Agenten hochladen: `kontrollwoerter*.csv`, Golden-Set-Dateien mit Sollantworten zu
  Lesebeweisen, `Plattformtest_Loesungen.txt`, Antworten, die Kontrollwörter enthalten.
- In diesem Repository dürfen Kontrollwörter der **Teststudien** stehen (Testdaten). Kontrollwörter echter Pakete nie.
- Kontrollwörter nur über die Skripte erzeugen oder ändern, nie von Hand.

## Öffentliche Teststudien

| ID | Studie | Herausgeber |
|---|---|---|
| LAV-T01 | Gesundheitsmonitor 2024 – Das Wichtigste in Kürze, 19 Seiten | gfs.bern / Interpharma |
| LAV-T02 | Gesundheitsmonitor 2025 – Das Wichtigste in Kürze, 27 Seiten | gfs.bern / Interpharma |
| LAV-T03 | Helsana-Arzneimittelreport 2024, 102 Seiten | Helsana |

Die PDFs liegen nicht im Repository (Rechte der Herausgeber); `python tools/pdfs_holen.py` lädt sie lokal nach
`testdaten/pdf/`. Transkripte und Ingest-Ergebnisse dieser Studien liegen in `testdaten/` (Abdruck mit Quellenangabe).
