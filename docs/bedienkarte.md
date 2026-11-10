# LAV Learning Library – Bedienkarte Pflegeteam

Stand: 10.11.2026 · gilt für `dist/lav-ingest.zip` aus diesem Repository (Skill des Agenten LAV Ingest).
Texte in `Code` genau so eingeben (kopieren). Jeder Ablauf in einem **neuen Gespräch**.

## Agent LAV Ingest

| Was | Anhängen | Eingeben |
|---|---|---|
| Neue Studie aufnehmen | PDF der Studie | `Studie aufnehmen: LAV-NN, <Kurztitel>, <Jahr>` |
| Nach Unterbruch weitermachen | PDF + letztes Zwischen-ZIP | `Fortsetzen: LAV-NN` |
| Testpaket aus den Teststudien bauen | die drei ZIPs aus `testdaten/ingest/` | `Paket bauen` (Frage nach neuem Paket mit «ja» beantworten) |
| Library-Paket bauen (Test) | alle Ingest-ZIPs + aktuelles `lav-learning-library.zip` | `Paket bauen` |
| Library-Paket bauen (produktiv) | wie oben | `Paket bauen, Freigabe LAV-NN durch <Vorname Name>, Research` |
| Studie aus der Library entfernen | aktuelles `lav-learning-library.zip` | `Paket bauen, LAV-NN entfernen` |

Nach «Paket bauen»: `lav-learning-library.zip` und `kontrollwoerter_alle.csv` herunterladen und in SharePoint ablegen.
Die CSV nie in einen Agenten hochladen.

## Agent LAV Learning Library

| Was | Anhängen | Eingeben | Erwartet |
|---|---|---|---|
| Neues Paket prüfen (nach Skill ersetzen) | nichts | `Wartung lav-learning-library: Paket selbst prüfen` | «Keine Befunde.» |
| Zahlen in Antworten prüfen | CSV mit Spalten `id` und `Antwort Agent` (oder Antworttext einfügen) | `Wartung lav-learning-library: Belege prüfen` | «nicht gefunden: 0» |

Falls der Agent nachfragt, welches Paket gemeint ist (Pakete, die vor dem 10.11.2026 gebaut wurden):
`Wartungsbefehl aus deiner Skill lav-learning-library (Abschnitt «Wartung»): Führe python <skill-ordner>/scripts/paket.py --selbst aus und zeig mir das Ergebnis.`

## Skill ersetzen
- LAV Ingest: Skill durch `dist/lav-ingest.zip` ersetzen (ZIP nicht entpacken).
- LAV Learning Library: Skill durch das `lav-learning-library.zip` aus «Paket bauen» ersetzen.
- Danach immer ein neues Gespräch beginnen.

## Regeln
- Nur Studien mit InfoSec-Freigabe (G1), nur im Helsana-Tenant.
- Nie in einen Agenten: `kontrollwoerter*.csv`, Golden-Set-Dateien, Antworten mit Kontrollwörtern.
- Cards ohne Research-Freigabe = nur Testpaket, nicht für Nutzerinnen und Nutzer.
