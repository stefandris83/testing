# LAV Learning Library – Skills, Werkzeuge und Wissensstand

Arbeitsrepository für die **LAV Learning Library** der Helsana: zwei Agenten in Microsoft Copilot Studio
(GitHub Copilot Harness). **LAV Ingest** transkribiert Studien-PDFs vollständig und baut das Skill-Paket;
**LAV Learning Library** beantwortet Fragen nur aus den Studien, mit Seitenbeleg.

> **Öffentliches Repository.** Hier liegen nur Skills, Werkzeuge, Dokumentation und drei öffentliche Teststudien.
> Inhalte interner Studien gehören nie hierher und nie in den Copilot-Chat – nur IDs (LAV-NN) und Prüfkennzahlen.
> Details: [docs/sicherheit.md](docs/sicherheit.md).

## Schnellstart in VS Code mit GitHub Copilot

1. Repository holen: in VS Code `Ctrl+Shift+P` → **Git: Clone** → `https://github.com/stefandris83/testing` → Ordner
   wählen → öffnen. (Ohne Git: auf GitHub **Code → Download ZIP**, entpacken, Ordner in VS Code öffnen.)
2. Copilot-Chat öffnen, **Agent**-Modus wählen, Modell wählen (z. B. Claude Opus).
   Die Anweisungen in `.github/copilot-instructions.md` lädt Copilot automatisch.
3. Erste Nachricht, z. B.: `Lies docs/stand.md und sag mir kurz, was als Nächstes ansteht.`
4. Optional im Terminal: `python tools/build.py` – führt alle Tests aus und baut `dist/lav-ingest.zip`
   (Python 3.10+; für Teil B der Ingest-Tests zusätzlich `pip install pdfplumber` und `python tools/pdfs_holen.py`).

Typische Aufträge im Chat:

| Du willst … | Eingabe im Chat |
|---|---|
| ein Ergebnis aus Copilot Studio auswerten | Screenshot/CSV anhängen und `/auswerten` (oder «Werte das aus») |
| eine Skill ändern und ausliefern | Änderung beschreiben, danach `/release` |
| den Projektstand festhalten (Ende der Sitzung) | `/stand` |
| Testfragen zu den Teststudien erstellen | `/testfragen 40 Fragen, gemischt` |

Gibt es die Slash-Befehle nicht (je nach Copilot-Version), funktioniert «Folge .github/prompts/auswerten.prompt.md».

## Was wo liegt

| Ordner | Inhalt |
|---|---|
| [`dist/`](dist/) | **`lav-ingest.zip`** – diese Datei im Agenten LAV Ingest als Skill hochladen; Prüfsumme in `PRUEFSUMMEN.txt` |
| [`src/`](src/) | Quellen der beiden Skills (`lav-ingest/`, `lav-learning-library/`) |
| [`docs/`](docs/) | Wissensstand: [Stand](docs/stand.md) · [Architektur](docs/architektur.md) · [Plattform](docs/plattform.md) · [Qualität](docs/qualitaet.md) · [Entscheide](docs/entscheide.md) · [Testprotokoll](docs/testprotokoll.md) · [Sicherheit](docs/sicherheit.md) · [Bedienkarte](docs/bedienkarte.md) |
| [`testdaten/`](testdaten/) | Teststudien LAV-T01–T03: Ingest-ZIPs, Pakete, Referenztranskripte, Golden Sets |
| [`tests/`](tests/), [`tools/`](tools/) | automatische Tests; Build und Hilfswerkzeuge |
| [`.github/`](.github/) | Anweisungen und Abläufe für Copilot; Tests bei jedem Push (GitHub Actions) |
| [`archiv/`](archiv/) | überholte Übergabe v3.1 |

## Bedienung im Tenant

Die genauen Eingaben für beide Agenten stehen in der **[Bedienkarte](docs/bedienkarte.md)**. Kurz:
- LAV Ingest: `Studie aufnehmen: LAV-NN, <Kurztitel>, <Jahr>` (PDF anhängen) · `Paket bauen` (Ingest-ZIPs und
  bisheriges Paket anhängen).
- LAV Learning Library, nach dem Ersetzen der Skill im neuen Gespräch:
  `Wartung lav-learning-library: Paket selbst prüfen`.

Dateien mit Kontrollwörtern (`kontrollwoerter*.csv`, Golden-Set-Dateien) nie in einen Agenten hochladen.
