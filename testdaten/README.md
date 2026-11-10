# Testdaten

Nur **öffentliche** Teststudien. Nie Inhalte interner Studien hier ablegen (siehe `docs/sicherheit.md`).

| ID | Studie | Seiten | Quelle der PDF |
|---|---|---|---|
| LAV-T01 | Gesundheitsmonitor 2024 – Das Wichtigste in Kürze (gfs.bern / Interpharma) | 19 | interpharma.ch/wp-content/uploads/2024/06/LY-IPH.01.24.001-–-Gesundheitsmonitor-2024_d_web.pdf |
| LAV-T02 | Gesundheitsmonitor 2025 – Das Wichtigste in Kürze (gfs.bern / Interpharma) | 27 | interpharma.ch/wp-content/uploads/2025/06/LY-IPH.01.25.001-–-Gesundheitsmonitor-2025_d_250605_def.pdf |
| LAV-T03 | Helsana-Arzneimittelreport 2024 | 102 | helsana.ch/dam/de/pdf/helsana-gruppe/publikationen/arzneimittelreport-2024.pdf |

## Ordner

| Ordner / Datei | Inhalt | Verwendet von |
|---|---|---|
| `ingest/LAV-T0x_ingest.zip` | Ergebnisse des Agenten LAV Ingest im Tenant (Volltext, Seiten, Card, Katalog-Eintrag, Protokolle, `kontrollwoerter.csv`) | `tests/test_paket_bauen.py`; Test «Paket bauen» im Tenant |
| `library/lav-learning-library_3-studien_v1.1.zip` | Library-Paket mit T01–T03 (von Hand gebaut, 9.11.2026; Volltexte identisch mit «Paket bauen») | `tests/test_belege.py`, `tools/belege_lokal.py` |
| `library/beispielpaket_LAV-T02_v3.1.zip` (+ Kontrollwörter) | Beispielpaket der Blaupause v3.1 (7 Teile à ≤ 18’000 Bytes) | `tests/test_ingest_skripte.py` |
| `referenz/LAV-T01`, `referenz/LAV-T02` | Referenztranskripte von Claude (eine Datei je Seite, geprüft), mit Prüfprotokoll und begründeten Befunden | `tests/test_ingest_skripte.py`, Vergleich mit Ingest-Ergebnissen (`tools/grafikvergleich.py`) |
| `golden-set/golden-set-mehrstudientest.csv` | Testfragen G01–G15 mit Sollantworten | Golden-Set-Runden, Auswertung |
| `golden-set/golden-set-beispiel_LAV-T01-T02.csv` | 12 Beispielfragen der Blaupause v3.1 | Hintergrund |
| `pdf/` | die drei PDFs – **nicht im Repository**, holen mit `python tools/pdfs_holen.py` | Teil B der Ingest-Tests, Nachprüfen an der PDF |

## Achtung Kontrollwörter

Die Ingest-ZIPs (`kontrollwoerter.csv`), die Golden-Set-Dateien (G11) und die Kontrollwort-Liste des Beispielpakets
enthalten Kontrollwörter. **Nie in den Library-Agenten hochladen.** Die Ingest-ZIPs gehören nur in den Agenten
LAV Ingest («Paket bauen»), der die CSV nicht ins Paket übernimmt.

Unbeschriftete Grafikwerte in den Referenztranskripten sind aus der Vektorgrafik berechnet («berechnet», ± 1 Prozentpunkt);
der Ingest-Agent liest sie am Seitenbild ab («ca.»). Abweichungen bis 3 Prozentpunkte gelten als Ablesegenauigkeit.
