# LAV Learning Library – Testdateien

Nur öffentliche Testdaten und Skills. Keine internen Studien (Regel G5).
Stand: 9.11.2026

| Datei | Zweck | SHA-256 (Anfang) |
|---|---|---|
| `lav-ingest.zip` | Skill des Agenten **LAV Ingest** (Studien aufnehmen, Library-Paket bauen und prüfen) | `4f94d9de` |
| `mehrstudientest/lav-learning-library_3-studien_v1.1.zip` | Skill des Agenten **LAV Learning Library** mit den drei öffentlichen Teststudien LAV-T01 bis LAV-T03, Version 1.1 | `bfca37c7` |
| `mehrstudientest/golden-set-mehrstudientest.csv` | Testfragen G01–G15 mit Sollantworten. Enthält Kontrollwörter: **nie in einen Agenten hochladen** | `ebde1bc7` |
| `library-vorlage_v1.1.zip` | Baukasten für das Library-Paket mit echten Studien (SKILL.md, Prüfskripte, Vorlagen für Katalog und Cards) | `1f47aac5` |
| `LAV_Learning_Library_Uebergabe_v3.1.zip` | Blaupause v3.1, Anleitung, Plattformtest, Referenztranskripte (wird durch v3.2 ersetzt) | `3350c6d7` |
| `upload-test/LAV-T01_ingest.zip` … `LAV-T03_ingest.zip` | Ingest-Ergebnisse der drei öffentlichen Teststudien (Test «Paket bauen»). Enthalten kontrollwoerter.csv: nur in LAV Ingest hochladen, nie in den Library-Agenten | `8371ae78` · `f80cf72f` · `c24b41a9` |

## Neu in lav-ingest.zip: Befehl «Paket bauen»
- Baut aus den Ingest-ZIPs (und optional dem bestehenden Library-Paket) das fertige, geprüfte `lav-learning-library.zip`.
- Ersetzt Studien gleicher ID, trägt Ausgaben derselben Reihe gegenseitig unter «Nicht verwechseln mit» ein, ersetzt doppelte Kontrollwörter, verteilt Katalog und Cards bei Bedarf auf mehrere Dateien.
- Freigabe durch Research per Befehl («Freigabe LAV-NN durch <Name>»); ohne Freigabe nur Testpaket.

## Neu in Version 1.1 der Library-Skill
- Antwortregeln: falsche Annahmen zuerst richtigstellen; keine Ursache-Aussagen ohne Beleg; zu jeder Zahl Gruppe, Basis, Jahr und Art des Werts; Veränderungen in Prozentpunkten, Selbstgerechnetes als «berechnet»; Methodenhinweis bei Vergleichen.
- Wartungsbefehle für das Pflegeteam: «Paket selbst prüfen» (prüft das geladene Paket, ohne Upload) und «Belege prüfen» (jede Zahl einer Antwort gegen die zitierte Seite).
