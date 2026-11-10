---
applyTo: "src/**"
description: Regeln für Änderungen an den Skills LAV Ingest und LAV Learning Library (SKILL.md, Skripte, Vorlagen)
---

# Regeln für Skill-Dateien

## SKILL.md
- Leser ist ein anderes Modell (GPT-6 Astra im GitHub Copilot Harness von Copilot Studio), nicht der Mensch:
  Du-Form, Imperativ, Deutsch (Schweiz), konkret, ohne Fülltext. Befehle, Pfade und Dateinamen exakt.
- Die `description` im Frontmatter entscheidet, ob der Agent die Skill lädt: alle Befehle nennen, die die Skill
  bedient (z. B. «Paket bauen», «Wartung lav-learning-library: …»). Höchstens 1’024 Zeichen.
- Library-SKILL.md wird bei jeder Anfrage gelesen: kurz halten (heute rund 7’300 Zeichen, Richtwert ≤ 10’000).
  Neue Regeln nur, wenn ein beobachteter Fehler sie verlangt; bestehende vorher auf Überschneidung prüfen.
- Kopfzeile der Library-SKILL.md `Version x.y · Stand JJJJ-MM-TT` bei jeder inhaltlichen Änderung erhöhen
  («Paket bauen» übernimmt die Version in den Katalogkopf).
- Grundsätze der Library nie aufweichen: nur aus den Skill-Dateien, jede Aussage mit `[LAV-XX, S. n]`, Lücken
  ausdrücklich, Wertstatus übernehmen, keine Schätzungen.
- Grundsätze des Ingest nie aufweichen: wörtlich, vollständig, seitengetreu; nie kürzen oder paraphrasieren;
  Unsicheres kennzeichnen; Kontrollwörter nur über Skripte.
- Ändert sich, was der Mensch im Tenant eingibt: `docs/bedienkarte.md` im selben Schritt nachführen.

## Skripte
- Python 3.12 (Sandbox), nur Standardbibliothek; `inventar.py` und `pruefen.py` dürfen pdfplumber/pypdfium2 nutzen.
  Kein Netzwerk, keine neuen Abhängigkeiten.
- Ausgaben auf Deutsch; Exit-Code 0 = keine Befunde, 1 = Befunde, 2 = Fehler; Fehler als «FEHLER: …».
- Dateien immer mit `encoding="utf-8"` lesen und schreiben; Unterprozesse mit `-X utf8` (Windows-Tests).
- Plattform: Befehle, die der Agent ausführt, dürfen keine Upload-Pfade von ZIP-Dateien enthalten (Hook hält ZIPs
  für CSV und sperrt); Skripte suchen Uploads selbst (Muster: `paket_bauen.py --uploads`). Pfade nie raten.
- Neues Skript: in `tools/build.py` (ORDER) eintragen, in der Skriptliste der SKILL.md nennen, Test schreiben.

## Formate sind Verträge
Seitenmarker, Kopf- und Schlusszeilen, Kontrollwort-Muster, Wertstatus, Belegform, Katalog- und Card-Struktur werden
von mehreren Skripten erzeugt und geprüft (Tabelle in `docs/architektur.md`). Nur gemeinsam mit allen betroffenen
Skripten, Vorlagen und Tests ändern.

## Abgeleitete Dateien (nie von Hand)
`src/lav-ingest/assets/library-SKILL.md`, `src/lav-ingest/scripts/belege.py`, `src/lav-learning-library/scripts/paket.py`,
`src/lav-ingest/references/skripte.md` – Quelle ändern, dann `python tools/build.py`.

## Nach jeder Änderung
`python tools/build.py` – alle Tests grün, `dist/lav-ingest.zip` aktualisiert. Danach Ablauf
`.github/prompts/release.prompt.md`.
