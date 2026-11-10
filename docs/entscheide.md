# Entscheide

Stand: 10.11.2026. Warum die Library so gebaut ist. Neue Entscheide unten anfügen (Nummer, Datum, Entscheid,
Begründung). Einen Entscheid nur mit neuem Eintrag ändern, nie stillschweigend.

## Aus der Blaupause v3.1 (14.10.2026)

| Nr. | Entscheid | Begründung |
|---|---|---|
| E1 | Kein Copilot-Studio-«Knowledge»; Studien als Dateien im Skill | Knowledge liefert nur Ausschnitte, verliert Grafikzahlen, kann keine Dateien auflisten und indexiert vertraulich gelabelte Dokumente nicht. |
| E2 | Drei Ebenen: Katalog (immer), Study Cards (übergreifend), Volltext in Teilen | Richtige Studie finden, ohne jedes Mal alles zu lesen. |
| E3 | Zufälliges Kontrollwort am Ende jeder Datei | Nur ein nicht ableitbares Wort beweist, dass die Datei bis zum Ende gelesen wurde. |
| E4 | Wertstatus für Grafikwerte; Ablesen am Seitenbild als Standard | Keine Scheingenauigkeit; Berechnung aus der Vektorgrafik optional. |
| E5 | Prüfung: Zahlen einzeln mit Häufigkeit, Wörter als Quote pro Seite (95 %) | Findet fehlende und veränderte Zahlen und ausgelassene Aussagen ohne Fehlalarm-Flut. |
| E6 | Unbeschriftete Grafiken: im Spike alle prüfen, danach jede fünfte | Der Zahlen-Check ist dort blind. |
| E7 | Transkription in Copilot Studio (Ingest-Agent) | Einzige zulässige Umgebung für interne Studien; Python-Sandbox vorhanden. |
| E8 | Zwei Agenten: Library (Fragen) und Ingest (Pflege) | Verschiedene Anweisungen, Rechte, Nutzerkreise. |
| E9 | Teilgrösse nach Messung | Lesewerkzeug kürzt grosse Dateien; Wert im Plattformtest bestimmt (→ E16). |
| E10 | Volltext zuerst, Study Card daraus | Card belegt Seiten des geprüften Volltexts. |
| E11 | «Schlussfolgerungen der Studie» getrennt von «Redaktioneller Einordnung LAV» | Interpretation nie als Studienbefund zitieren. |
| E12 | Golden Set: 15–20 Fragen im Spike, danach 1–2 pro Studie; Lauf nach jedem Update | Verwechslungsgefahr wächst mit jeder Studie; Plattform-Updates ändern Verhalten. |
| E13 | Ingest in Etappen mit Zwischen-ZIP und «Fortsetzen» | Zeitgrenzen pro Antwort undokumentiert; ein Abbruch darf keine Arbeit kosten (→ E17). |
| E14 | Fall A bleibt «alle Teile lesen»; Variante A2 nur nach Spike-Befund und mit Zustimmung | A2 schwächt «vollständig gelesen» ab. |
| E15 | Wiki aus demselben Paket (`wiki.py`); Agent im Wiki verlinken, einbetten nur nach Test P10 | Eine Quelle für Agent und Wiki; Embed-Sicherheit undokumentiert. |

## Seit Oktober 2026

| Nr. | Datum | Entscheid | Begründung |
|---|---|---|---|
| E16 | Okt. 2026 | `TEILGROESSE = 45000` Bytes | Lesetest P2 Stufe c in beiden Durchgängen bestanden; weniger Teile (100 Seiten ≈ 7 statt 20). |
| E17 | Okt./Nov. 2026 | `ETAPPEN_PRO_ANTWORT = 2`, Zwischen-ZIP alle 20 Seiten ab 40 Seiten | 3 Etappen liefen durch, die 4. nicht; 2 lassen Spielraum. |
| E18 | Nov. 2026 | Transkriptionsregeln verschärft: Rohtext ist Material; Rohtext-, Silbentrennungs- und Zeilenzerlegungs-Befunde werden nie begründet, immer behoben; Doppelseiten getrennt; Serienzuordnung nur eindeutig | Erster Ingest-Lauf LAV-T02 lieferte ungeordneten Rohtext auf Doppelseiten und vertauschte Serien. |
| E19 | 9.11.2026 | Vektorgrafik-Berechnung im Ingest: offen | LAV-T01 rechnete Werte aus Vektorpfaden (sehr genau), LAV-T02 nicht. Entscheid anhand der ersten echten Studie. |
| E20 | 9.11.2026 | PDFs als Knowledge mit Index (Vorschlag eines Kollegen) nicht verfolgt | Knowledge liest Suchausschnitte statt vollständig, Grafiken nur über Alt-Text; A/B-Test angeboten, falls gewünscht. |
| E21 | 9.11.2026 | Library-Skill v1.1: falsche Prämissen zuerst richtigstellen; Ursache nur mit Beleg und Vorsicht; Zahl mit Gruppe, Basis, Jahr, Art; Prozentpunkte; «berechnet»; Methodenhinweis | Aus dem Abnahmekonzept: typische Fehlerklassen von Sprachmodellen gezielt abfangen. |
| E22 | 9.11.2026 | Das Library-Paket darf `scripts/*.py` enthalten; Wartungsbefehle «Paket selbst prüfen» und «Belege prüfen» im Library-Agenten | Paketprüfung im Ingest-Agenten war durch die ZIP-Sperre blockiert; Belegprüfung muss im Tenant laufen, weil Claude interne Studien nicht sehen darf. |
| E23 | 9.11.2026 | Sollantworten für die Abnahme schreibt Research aus der PDF | Claudes Golden Set hatte Fehler (G07, G09). |
| E24 | 9.11.2026 | «Paket bauen» als Befehl in der bestehenden Ingest-Skill, kein eigener Agent und keine eigene Skill | Paketbau mit internen Studien muss im Tenant laufen; ein Befehl ist für das Pflegeteam am einfachsten. |
| E25 | 9.11.2026 | Freigabe der Cards per Befehl («Freigabe LAV-NN durch Name»); ohne Freigabe nur Testpaket | Freigabe wird im Paket sichtbar und datiert; kein Handeditieren. |
| E26 | 9.11.2026 | Doppelte Kontrollwörter der Volltexte beim Paketbau automatisch ersetzen | Kollisionswahrscheinlichkeit bei 25 Studien rund 40 %. |
| E27 | 10.11.2026 | `paket_bauen.py --uploads`: Skript liest den Upload-Ordner selbst; kein Upload-Pfad im Befehl | Plattform hält ZIPs für CSV und sperrt Befehle mit Upload-Pfad. |
| E28 | 10.11.2026 | `belege.py`: Tabellen ohne eigenen Beleg erben den Beleg des Absatzes davor, ersatzweise danach | Agent setzt Belege teils nach Tabellen; Werkzeug robust machen statt Regel weiter verschärfen. |
| E29 | 10.11.2026 | Skill-Beschreibungen nennen ihre Befehle; Wartungsbefehle in der Form «Wartung lav-learning-library: …»; Library-Skill v1.2 | Ohne Nennung in der description lud der Agent die Skill für «Paket selbst prüfen» nicht. |
| E30 | 10.11.2026 | Entwicklung in VS Code mit GitHub Copilot; dieses (öffentliche) Repository ist die einzige Quelle für Skills, Tests und Wissensstand | Arbeit auf der Helsana-Infrastruktur; jedes Modell soll mit denselben Anweisungen weiterarbeiten können. Nur öffentliche Testdaten (Gate G5 bleibt). |

## Bewusst nicht (jetzt)

- «Zitat zuerst» mit Selbstprüfung bei jeder Antwort (siehe qualitaet.md).
- Variante A2 für grosse Studien.
- Power Automate, Datenbank, eigene Website – ein statisches Skill-ZIP reicht für 2–3 neue Studien pro Jahr.
