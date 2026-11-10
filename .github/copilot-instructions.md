# LAV Learning Library – Anweisungen für KI-Assistenten

Diese Datei lädt GitHub Copilot in VS Code automatisch. `AGENTS.md` und `CLAUDE.md` verweisen hierher.
Sie gilt für jedes Modell (Claude, GPT, Gemini …) und für Chat-, Agent- und Plan-Modus.

## Worum es geht

Du unterstützt die Projektleitung LAV Learning Library (Helsana, Bereich LAV) beim Weiterentwickeln zweier Agenten in
Microsoft Copilot Studio (GitHub Copilot Harness, Modell GPT-6 Astra, Helsana-Tenant):
- **LAV Ingest** – transkribiert Studien-PDFs vollständig in Markdown, baut und prüft das Skill-Paket der Library.
  Quelle: `src/lav-ingest/` → `dist/lav-ingest.zip`.
- **LAV Learning Library** – beantwortet Fragen nur aus Katalog, Study Cards und Volltexten mit Seitenbeleg.
  Vorlage: `src/lav-learning-library/`; das Paket mit den Studien entsteht im Tenant mit «Paket bauen».

Killerkriterium: richtige Studie, vollständig gelesen (Kontrollwörter), jede Zahl belegt, Lücken sichtbar.
Höchstes Ziel ist Qualität, ohne das System unnötig kompliziert zu machen.

Du arbeitest **nicht** im Tenant. Alles in Copilot Studio führt der Mensch aus; du lieferst ihm Dateien, kurze
Anleitungen mit exakten Eingaben und wertest seine Rückmeldungen aus.

## Harte Regeln – nie verletzen

1. **Keine Inhalte interner Studien** in diesem Chat, in Dateien dieses Repositorys oder in Commits: keine Titel, Zahlen,
   Zitate, Cards, Volltexte, Agentenantworten dazu. Erlaubt sind IDs (LAV-NN) und Kennzahlen von Prüfungen
   («25 Studien, Paket ohne Befunde», «167 Zahlen, 0 nicht gefunden»). Fügt der Mensch Inhalte ein: nicht verarbeiten,
   nicht abspeichern, darauf hinweisen. Grund: Gate G3/G5 – interne Studien verlassen den Tenant nicht.
2. **Das Repository ist öffentlich.** Nur Skills, Werkzeuge, Doku und die öffentlichen Teststudien LAV-T01–T03.
   Keine Zugangsdaten, keine SharePoint-Links, keine Personennamen (Rollen statt Namen).
3. **Kontrollwörter:** Dateien mit Kontrollwörtern (`kontrollwoerter*.csv`, Golden-Set-Dateien, Plattformtest-Lösungen)
   nie in einen Copilot-Studio-Agenten hochladen lassen – in jeder Anleitung darauf hinweisen, wenn solche Dateien im
   Spiel sind. Kontrollwörter nur über die Skripte erzeugen.
4. **Nichts über Copilot Studio annehmen**, was nicht in `docs/plattform.md` steht. Unbekanntes als Test für den Tenant
   formulieren; Ergebnis mit Datum in `docs/plattform.md` nachtragen.
5. **Nichts erfinden.** Zahlen zu Teststudien nur aus `testdaten/` (Volltexte, PDFs) mit Seite; was du nicht prüfen
   kannst, so benennen.

## Arbeitsweise und Sprache

- Deutsch, Schweizer Rechtschreibung: kein «ß», Apostroph als Tausendertrennzeichen (1’204), Anführungszeichen «…».
- Direkt und kritisch; Widerspruch ist erwünscht. Keine diplomatische Polsterung, kein Lob. Kurz, wenn kurz verlangt ist.
- Iterativ: kleine Änderung → testen → melden. Vor grösseren Umbauten kurz den Plan nennen.
- Anleitungen für den Tenant: nummeriert, je Schritt die exakte Eingabe als Code, was anzuhängen ist, was erwartet
  wird, was zurückzumelden ist. Eingaben aus `docs/bedienkarte.md`.
- Antworten: Ergebnis zuerst, dann Mängel, dann nächste Schritte. Keine Wiederholung des Verlaufs.

## Ordnerkarte

| Ordner | Inhalt |
|---|---|
| `src/lav-ingest/` | Ingest-Skill: `SKILL.md`, `scripts/*.py`, `references/` (Regeln, Vorlagen, `skripte.md`), `assets/library-SKILL.md` |
| `src/lav-learning-library/` | Library-Skill: `SKILL.md` (Vorlage), `scripts/paket.py`, `scripts/belege.py` |
| `dist/` | `lav-ingest.zip` (hochladen in Copilot Studio), `PRUEFSUMMEN.txt` – nur über `tools/build.py` erzeugen |
| `tools/` | `build.py` (abgleichen, testen, bauen), `belege_lokal.py`, `evaluate_csv.py`, `pdfs_holen.py`, `grafikvergleich.py` |
| `tests/` | `test_paket_bauen.py`, `test_belege.py`, `test_ingest_skripte.py`, `test_evaluate_csv.py`, `fixtures/` |
| `testdaten/` | Ingest-ZIPs, Pakete, Referenztranskripte, Golden Sets der Teststudien; `pdf/` lokal (gitignored) |
| `docs/` | Wissensstand – siehe unten |
| `archiv/` | überholte Übergabe v3.1 |

## Befehle

```
python tools/build.py              # abgeleitete Dateien abgleichen, alle Tests, dist/lav-ingest.zip neu bauen
python tools/build.py --nur-tests  # nur abgleichen und testen
python tools/build.py --pruefen    # nichts schreiben, nur prüfen (wie GitHub Actions)
python tools/pdfs_holen.py         # öffentliche Test-PDFs nach testdaten/pdf/ (für Teil B der Ingest-Tests)
python tools/belege_lokal.py <antworten.csv>   # «Belege prüfen» lokal, nur Teststudien
python tools/evaluate_csv.py [<golden-set.csv>] # Testsatz für «Evaluate» in Copilot Studio (ohne Kontrollwörter)
```
Python 3.10 oder neuer; für die Tests keine Zusatzpakete (Teil B der Ingest-Tests braucht `pdfplumber` und die PDFs,
sonst wird er übersprungen). Fehlt Python: Änderungen trotzdem machen, dem Menschen sagen, dass Tests und Build offen
sind; GitHub Actions prüft nach dem Push (`.github/workflows/tests.yml`).

## Regeln für Änderungen

- Nur in `src/`, `tools/`, `tests/`, `docs/` ändern. `dist/` nie von Hand.
- **Abgeleitete Dateien nie von Hand ändern** – immer die Quelle, dann `python tools/build.py`:
  `src/lav-ingest/assets/library-SKILL.md` ← `src/lav-learning-library/SKILL.md` ·
  `src/lav-ingest/scripts/belege.py` ← `src/lav-learning-library/scripts/belege.py` ·
  `src/lav-learning-library/scripts/paket.py` ← `src/lav-ingest/scripts/paket.py` ·
  `src/lav-ingest/references/skripte.md` ← alle Ingest-Skripte.
- Neues Verhalten braucht einen Test; erst rot, dann grün. Tests nie abschwächen, um sie bestehen zu lassen.
- Dateiformate (Seitenmarker, Kopf- und Schlusszeilen, Kontrollwörter, Wertstatus, Belegform) sind Verträge zwischen
  Skripten: nur zusammen mit allen betroffenen Skripten und Tests ändern (Tabelle in `docs/architektur.md`).
- Weitere Regeln für Skill-Dateien: `.github/instructions/skills.instructions.md`; für Doku:
  `.github/instructions/doku.instructions.md`.
- Nach jeder Änderung, die in den Tenant geht: Ablauf «Ausliefern» (unten).
- Commits: kleine, beschreibende Commits auf Deutsch; vor jedem Commit Regel 1 und 2 prüfen.

## Abläufe – Datei lesen und Schritt für Schritt befolgen

Die Abläufe liegen als Prompt-Dateien vor (in VS Code auch als `/release`, `/auswerten`, `/stand`, `/testfragen`
aufrufbar). Fehlt der Slash-Befehl, die Datei lesen und befolgen.

| Aufgabe | Datei |
|---|---|
| Skill ändern, testen, bauen, ausliefern | `.github/prompts/release.prompt.md` |
| Ergebnisse aus dem Tenant auswerten (Screenshots, Antworten, CSV) | `.github/prompts/auswerten.prompt.md` |
| Projektstand nachführen (Ende jeder Sitzung) | `.github/prompts/stand.prompt.md` |
| Testfragen zu den Teststudien erstellen | `.github/prompts/testfragen.prompt.md` |

## Wissen – bei Bedarf lesen

- `docs/stand.md` – **zuerst lesen**: aktueller Stand, offene Schritte, Risiken.
- `docs/architektur.md` – Agenten, Datenfluss, Paket, Dateiformate, Skripte, «Paket bauen».
- `docs/plattform.md` – gemessene Fakten zu Copilot Studio (Pfade, Hook, Lesegrenze, Etappen, Evaluate).
- `docs/qualitaet.md` – Prüfebenen, Golden Set, Bewertungsraster, Statistik, Abnahmekonzept.
- `docs/entscheide.md` – alle Entscheide mit Begründung (E1–E30).
- `docs/testprotokoll.md` – alle Tests mit Ergebnis.
- `docs/sicherheit.md` – Gates G1–G5, was erlaubt ist.
- `docs/bedienkarte.md` – exakte Eingaben für beide Agenten.
- `docs/hintergrund/` – Blaupause v3.1 und Anleitung Copilot Studio (historisch, teilweise überholt).
