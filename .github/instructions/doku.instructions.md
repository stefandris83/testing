---
applyTo: "docs/**,README.md,testdaten/README.md"
description: Regeln für die Projektdokumentation (Stand, Entscheide, Testprotokoll, Plattform, Bedienkarte)
---

# Regeln für die Dokumentation

- Deutsch (Schweiz): kein «ß», 1’204, «…». Kurze Sätze, Tabellen für Vergleiche.
- Immer absolute Daten (10.11.2026), nie «heute», «gestern», «letzte Woche».
- **Keine Inhalte interner Studien** – nur IDs (LAV-NN) und Prüfkennzahlen. Das Repository ist öffentlich.
- `docs/stand.md`: Stand-Datum oben anpassen; «Offene Schritte» aktuell halten (Erledigtes streichen, nicht sammeln);
  Verlauf: höchstens eine Zeile pro Tag.
- `docs/entscheide.md`: neuer Eintrag mit Nummer, Datum, Entscheid, Begründung; alte Einträge nicht umschreiben,
  sondern durch einen neuen ersetzen («ersetzt E17»).
- `docs/testprotokoll.md`: neueste Einträge oben; was getestet, mit welcher Version, Ergebnis, Kennzahlen, Mängel.
- `docs/plattform.md`: nur Gemessenes oder Beobachtetes, mit Datum und Quelle; Vermutungen als «offen» markieren.
- `docs/bedienkarte.md`: exakte Eingaben, die im Tenant funktionieren; nach jeder Änderung an Befehlen nachführen.
- `docs/hintergrund/`: historische Dokumente – nicht ändern.
