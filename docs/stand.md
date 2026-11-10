# Projektstand

Stand: 10.11.2026 · Lebendes Dokument: nach jeder Arbeitssitzung nachführen
(Ablauf [.github/prompts/stand.prompt.md](../.github/prompts/stand.prompt.md)).

## In Kürze

Zwei Agenten in Microsoft Copilot Studio (GitHub Copilot Harness, Modell GPT-6 Astra) im Helsana-Tenant:
**LAV Ingest** transkribiert Studien-PDFs und baut das Skill-Paket, **LAV Learning Library** beantwortet Fragen mit
Seitenbelegen. Die ganze Kette – Studie aufnehmen, Paket bauen, Paket prüfen, Antworten belegen – ist mit drei
öffentlichen Teststudien im Tenant getestet. Interne Studien erst nach Gate G1. Ab 10.11.2026 wird in VS Code mit
GitHub Copilot weiterentwickelt; dieses Repository ist die einzige Quelle.

## Agenten im Tenant

| Agent | Status | Skill im Tenant |
|---|---|---|
| LAV Ingest | aktiv, nur Pflegeteam | Stand 10.11.2026 vormittags (4f94d9de oder neuer); ersetzen durch `dist/lav-ingest.zip` |
| LAV Learning Library | aktiv, nicht veröffentlicht/geteilt | Testpaket T01–T03 aus «Paket bauen» vom 10.11.2026 (Library-Skill v1.1, Cards nicht freigegeben) |
| LAV Plattformtest | nicht mehr nötig, löschen | – |

## Versionen im Repository

| Was | Version | Datei |
|---|---|---|
| Ingest-Skill | Build vom 10.11.2026 | `dist/lav-ingest.zip`, Prüfsumme `dist/PRUEFSUMMEN.txt` |
| Library-Skill (Vorlage für «Paket bauen») | v1.2 · 10.11.2026 | `src/lav-learning-library/SKILL.md` (steckt als `assets/library-SKILL.md` im Ingest-ZIP) |
| Einstellungen Ingest | TEILGROESSE 45’000 · ETAPPEN_PRO_ANTWORT 2 · ZWISCHENSTAND_ALLE 20 | `src/lav-ingest/SKILL.md` |

Seit dem letzten im Tenant bestätigten Stand geändert (noch nicht im Tenant getestet): Beschreibungen nennen die
Befehle; Wartungsbefehle in der Form «Wartung lav-learning-library: …»; «Paket bauen» gibt den Prüfbefehl zum Kopieren
aus; belege.py erbt Belege auch aus dem Absatz nach einer Tabelle; paket_bauen.py ruft paket.py im UTF-8-Modus auf.

## Was funktioniert (im Tenant bestätigt)

- Studie aufnehmen: LAV-T01 (19 S.), LAV-T02 (27 S.), LAV-T03 (102 S.); Fortsetzen mit Zwischen-ZIP.
- Paket bauen mit `--uploads` (10.11.2026), Paket selbst prüfen, Belege prüfen.
- Library-Antworten: G01–G15 bestanden, 0 kritische Fehler; Lesebeweis über 8 Teile.

## Offene Schritte (Reihenfolge)

1. **Nutzer, im Tenant:** Ingest-Skill durch `dist/lav-ingest.zip` ersetzen → neues Gespräch, drei ZIPs aus
   `testdaten/ingest/` anhängen, `Paket bauen` → im Library-Agenten Skill ersetzen, neues Gespräch,
   `Wartung lav-learning-library: Paket selbst prüfen` (Kurzform testen; erwartet «Keine Befunde.»).
2. **Simulierte Fragensammlung** (rund 40 Fragen, nur Entwicklung): [testfragen.prompt.md](../.github/prompts/testfragen.prompt.md).
3. **PowerPoint-Studie** (> 100 Seiten, aus PowerPoint exportiert) als Prüffall: öffentlich → sofort; intern → erst
   nach G1 und nur im Tenant.
4. **Testpaket für Skill-Grenzen** (9 Mini-Skills, 400 Dateien, 4 Ordnerebenen) bauen und im Tenant messen.
5. **Gate G1**; danach 3–5 echte Studien (Spike): Zeit, Credits, Ablesefehlerquote messen.
6. **Abnahme** vor dem Rollout (siehe qualitaet.md): echte Fragen blind erheben, Sollantworten durch Research,
   Bewertungsraster, Doppelbewertung, Schwellen vorab.
7. **Pilot** mit monatlichem Export der Transkripte.

## Bekannte Risiken und offene technische Punkte

- «Fortsetzen» und «Wiki aufbereiten» nennen Upload-Pfade von ZIPs und könnten an der ZIP-Sperre scheitern
  (plattform.md). Bei Auftreten dieselbe Lösung wie bei «Paket bauen» (`--uploads`).
- Vektorgrafik-Berechnung im Ingest uneinheitlich (E19) – Entscheid bei der ersten echten Studie.
- Skill-Grenzen des Harness unbekannt (Dateizahl, Grösse, Tiefe) – wichtig ab rund 25 Studien.
- Kosten (Credits) pro Studie und pro Frage nicht gemessen.
- Das Repository ist öffentlich; ab echten Studien besonders auf die Datenregeln achten (sicherheit.md).

## Verlauf (kurz)

- 14.10.2026: Blaupause v3.1, Ingest-Skill, Plattform-Testpaket, Referenztranskripte.
- Okt. 2026: Phase A Plattformtest bestanden (TEILGROESSE 45’000).
- Okt./Nov. 2026: Phase B (Ingest LAV-T02, zweiter Lauf bestanden), Phase C (Library mit LAV-T02).
- Nov. 2026: M1 LAV-T01, M2 LAV-T03 (102 Seiten), M3 Paket mit drei Studien, M5/M6 12/12.
- 9.11.2026: Library v1.1, Wartungsbefehle, Regression G01–G15 15/15, «Paket bauen».
- 10.11.2026: «Paket bauen» im Tenant mit `--uploads`; Kette im Tenant bestätigt; Umzug in dieses Repository
  (VS Code + GitHub Copilot), Library-Skill v1.2, Regressionstest der Ingest-Skripte automatisiert.
