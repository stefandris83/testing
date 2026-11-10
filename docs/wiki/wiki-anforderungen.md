# LAV-Wiki – Anforderungen

## Zweck
Menschenlesbare Ansicht der LAV Learning Library: eine Übersicht aller Studien und je Studie die
freigegebene Study Card mit Links auf die Original-PDF. Dieselben Inhalte wie im Library-Agenten,
erzeugt aus denselben Dateien.

## Grundsätze
1. Eine Quelle: Inhalte kommen ausschliesslich aus `wiki.py` (Ingest-Agent, Ablauf «Wiki aufbereiten»).
   Im Wiki werden Inhalte nie bearbeitet; Korrekturen erfolgen im Quellordner und werden neu erzeugt.
2. Gleicher Nutzerkreis wie der Library-Agent (Gate G2) und Klassifizierung der enthaltenen Studien
   (Gate G4). Nie öffentlich.
3. Entwicklung nur mit Beispieldaten (öffentliche Teststudie LAV-T02). Echte Inhalte werden erst auf der
   Zielplattform eingespielt (Gate G5).
4. Der Agent wird verlinkt (Teams oder Microsoft 365 Copilot). Einbetten nur nach bestandenem
   Plattformtest P10.

## Eingabe
`lav-wiki_<Datum>.zip` aus dem Ingest-Agenten: `index.md` (Übersicht) und `LAV-XX.md` (eine Seite je
Studie). UTF-8, Markdown mit Tabellen. Erste Zeile jeder Seite: Hinweis zu Klassifizierung und Nutzerkreis.

## Muss
- Navigation Übersicht → Studie und zurück.
- Suche über Titel, Themen und Aliasse («Auch genannt»); Filter nach Jahr und Thema.
- Hinweiszeile auf jeder Seite sichtbar.
- Seitenlinks [S. n] öffnen für berechtigte Personen die Original-PDF.
- Link «Fragen an die Library» zum Agenten.
- Barrierefreiheit nach WCAG AA; nutzbar auf Laptop und Mobilgerät.

## Darf nicht
- Inhalte ändern, kürzen, ergänzen oder umformulieren.
- Kontrollwörter, Kontrollwort-Listen oder Volltext-Teile anzeigen.
- Öffentlich oder ohne Anmeldung mit Entra ID erreichbar sein.
- Externe Skripte, Schriften, Tracker oder CDNs laden.
- Als Wissensquelle («Knowledge») des Library-Agenten verwendet werden.

## Hosting – Optionen (Entscheid über Gate G5)
| Option | Vorteile | Nachteile |
|---|---|---|
| SharePoint-Seiten (Markdown-Webpart) | Entra ID, Labels und Berechtigungen wie der Quellordner; kein eigener Betrieb | Seiten per Skript (Graph/PnP) oder von Hand aktualisieren |
| Azure DevOps Code-Wiki | Markdown direkt aus einem Repository; Entra ID | nur wenn Azure DevOps im Einsatz ist; Agent nur als Link |
| Privates GitHub-Repository (Enterprise) | Markdown direkt, Arbeit in VS Code | vertrauliche Inhalte ausserhalb von Microsoft 365 – InfoSec-Entscheid; Agent nur als Link |
| Eigene Website (z. B. Azure Static Web Apps mit Entra-Anmeldung) | freie Gestaltung, Suche, Einbettung möglich | Betrieb, Freigabe und Build-Prozess nötig |

## Abnahme
- Jede Studie aus dem Katalog hat eine Seite; jede Seite ist von der Übersicht aus erreichbar.
- Im ausgelieferten Wiki kommt «Kontrollwort» nicht vor.
- Stichprobe: 5 Seitenlinks öffnen die richtige PDF-Seite.
- Ein Konto ausserhalb des Nutzerkreises erhält keinen Zugriff.
- Aktualisierungsprobe: neues `lav-wiki_*.zip` einspielen – die geänderte Card erscheint, sonst ändert sich nichts.

## Aktualisierung
Nach jedem geprüften Library-Paket: Ingest-Agent «Wiki aufbereiten» → ZIP herunterladen → Inhalt auf
der Zielplattform ersetzen → veröffentlichen.
