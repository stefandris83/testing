> **Historisches Dokument.** Master-Blaupause v3.1 vom 14.10.2026, aus dem PDF im Übergabe-ZIP (`archiv/`) nach
> Markdown umgewandelt. Konzept, Gates und Begründungen gelten weiter. **Überholt** sind insbesondere: Teilgrösse 18’000
> (jetzt 45’000 Bytes), ETAPPEN_PRO_ANTWORT 1 (jetzt 2), «nur SKILL.md und references/*.md im Paket» (jetzt auch scripts/*.py),
> Golden Set im Evaluate-Bereich (für Harness-Agenten nur «General quality»), Paketprüfung im Ingest-Agenten (jetzt «Paket bauen»
> mit `--uploads`). Massgeblich ist der aktuelle Stand in `docs/stand.md`, `docs/entscheide.md` und `docs/architektur.md`.

Umsetzungsbriefing · Helsana Bereich LAV

# LAV Learning Library Agent Master-Blaupause v3.1

Übergabefassung für die Umsetzung durch Menschen oder eine andere AI · Version 3.1 · 14.10.2026 · Status: Entwurf zur Freigabe

|                 |                                                                                                                                                                                                                                             |
|-----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Zielplattform   | Microsoft Copilot Studio · GitHub Copilot Harness · Agent Skills (ZIP)                                                                                                                                                                      |
| Arbeitsumgebung | Alles läuft in Copilot Studio: Transkription und Paketprüfung im Ingest-Agenten, Fragen im Library-Agenten. Kein lokales Python, keine AI ausserhalb des Tenants für interne Studien.                                                       |
| Architektur     | Statisches Skill-ZIP mit drei Ebenen: Katalog · Study Cards · Volltext in Teilen; Lesebeweis über zufällige Kontrollwörter                                                                                                                  |
| Umfang          | 25 Studien zum Start, maximal 60; Zuwachs ca. 2–3 Studien pro Jahr                                                                                                                                                                          |
| Stand           | Architektur entschieden; Ingest-Skill mit Prüf- und Wiki-Skripten, Vorlagen, Plattform-Testpaket, Referenztranskripte, Golden-Set-Beispiele und Wiki-Unterlagen liegen bei. Offen: Plattformtests im Tenant (Phase 0b), Gates G1–G5, Spike. |
| Dateien         | Alle Dateien sind in dieses PDF eingebettet (Anhang E; in Adobe Acrobat über die Büroklammer, Chrome und Edge zeigen sie nicht an) und liegen zusätzlich im Übergabe-ZIP.                                                                   |

So benutzt du dieses Dokument

- **Menschen:** Abschnitte 2 (Stand und Entscheidungen), 4 (Gates), 13 (Wiki und Einbindung), 14 (Aufwand) und 16 (Fahrplan) lesen; Phase 0b mit dem Testpaket durchführen.
- **Ausführende AI:** das ganze Dokument lesen und Abschnitt 1 als Arbeitsauftrag befolgen. Code nie aus dem PDF-Text abschreiben (Einrückungen gehen verloren), sondern die Dateien aus dem Übergabe-ZIP verwenden.
- **Verbindlichkeit:** Regeln mit «muss» und «nie» sind verbindlich. Wo «im Test messen» steht, gibt es noch keinen gesicherten Wert: messen, nicht annehmen.

## 1 Arbeitsauftrag an die ausführende AI · Verbindlich

**Ziel:** Eine Learning Library über 25–60 interne LAV-Studien, in der ein Agent in Copilot Studio jede Frage aus dem vollständigen Inhalt der richtigen Studie beantwortet, mit Seitenbeleg, ohne erfundene Zahlen. Die Architektur ist entschieden (Abschnitt 2.1); deine Aufgabe ist die Umsetzung, nicht ein neuer Entwurf.

### Reihenfolge

1.  **Gates prüfen lassen** (Abschnitt 4). Du entscheidest sie nicht selbst. Ohne G1 keine interne Studie verarbeiten.
2.  **Plattformtests begleiten** (Phase 0b, Abschnitt 16): Ergebnisse P1–P10 auswerten und daraus TEILGROESSE, ETAPPEN_PRO_ANTWORT, ZIP-Struktur, Skriptweg, Upload- und Download-Weg sowie die Einbindung des Agenten festlegen.
3.  **Ingest-Skill anpassen**: nur die Einstellungen in `SKILL.md` von `lav-ingest`. Skripte nur ändern, wenn ein Test es verlangt; danach den Regressionstest aus Abschnitt 10.5 wiederholen.
4.  **Spike** mit drei Studien (Phase 1), Zeit und Credits messen, Fehlerquote beim Ablesen bestimmen.
5.  **Library-Paket** bauen, mit `paket.py` prüfen, im Library-Agenten hochladen, Golden Set laufen lassen.
6.  **Rollout** in Tranchen à fünf Studien (Phase 2).
7.  **Wiki** (optional, nach G5): Seiten mit `wiki.py` erzeugen und auf der freigegebenen Plattform veröffentlichen (Abschnitt 13).

### Definition of Done

| Ergebnis              | Fertig, wenn                                                                                                                                                                                                                                                                               |
|-----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Volltext einer Studie | Eine Datei je PDF-Seite; `pruefen.py` ohne offene Meldung (jede behoben oder in `befunde-begruendet.txt` begründet); unbeschriftete Grafiken in `grafiken-abgelesen.txt` gelistet und von einem Menschen geprüft (Spike: alle, danach Stichprobe); in Teile aufgeteilt mit `aufteilen.py`. |
| Study Card            | Nach Vorlage, jede Aussage mit \[S. n\] aus dem geprüften Volltext, höchstens ca. 3’000 Zeichen, von Research freigegeben.                                                                                                                                                                 |
| Katalog-Eintrag       | Nach Vorlage, Zeile «Volltext» aus `katalog-zeile.txt`, Aliasse und Verwechslungshinweise ausgefüllt, höchstens ca. 600 Zeichen.                                                                                                                                                           |
| Library-Paket         | `paket.py` ohne Befunde; nur SKILL.md und references/\*.md im ZIP; Kontrollwort-Liste ausserhalb.                                                                                                                                                                                          |
| Library-Agent         | Golden Set im Evaluate-Bereich bestanden (Abschnitt 12.3).                                                                                                                                                                                                                                 |

### Verbindliche Regeln

- Sprache: Schweizer Hochdeutsch, kein «ß», Apostroph als Tausendertrennzeichen (1’204).
- Nichts über Copilot Studio annehmen, was nicht in Abschnitt 3.3 als belegt steht; offene Punkte im Tenant testen.
- Kontrollwörter nur über die Skripte erzeugen; `kontrollwoerter.csv` und `Plattformtest_Loesungen.txt` nie in einen Agenten hochladen.
- Nie kürzen, paraphrasieren oder Zahlen schätzen, wo die Quelle keine hergibt; Wertstatus immer angeben.
- Interne Studien nur im Tenant verarbeiten (G3). Für Tests nur die beigelegten öffentlichen Studien.
- Echte Inhalte nie in GitHub Copilot (VS Code) oder ein Repository bringen, solange G5 es nicht ausdrücklich erlaubt.

### Wann du den Menschen fragst

Bei jeder Gate-Frage; wenn ein Plattformtest als «Showstopper» endet (P2 Lesetest a, P4 Upload ohne Ersatzweg, P5 kein Seitenbild, P6 kein Download ohne Ersatzweg); wenn P8 oder P9 scheitert; wenn der gemessene Aufwand pro Studie mehr als 50 % über der Schätzung liegt; wenn eine Studie Inhalte mit engerem Berechtigungskreis enthält (G2); bevor die Variante für grosse Studien (E14) eingesetzt wird; wenn jemand den Agenten ohne bestandenen Test P10 einbetten will.

## 2 Projektstand und Entscheidungen · Stand 14.10.2026

### 2.1 Entscheidungen

| Nr. | Entscheidung                                                                                                                                                  | Begründung                                                                                                                                                 |
|-----|---------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
| E1  | Kein Copilot Studio «Knowledge»; Studien als Dateien im Skill                                                                                                 | Knowledge liefert nur Ausschnitte, verliert Grafikzahlen, kann keine Dateien auflisten und indexiert vertraulich gelabelte Dokumente nicht.                |
| E2  | Drei Ebenen: Katalog (immer), Study Cards (übergreifend), Volltext in Teilen                                                                                  | Richtige Studie finden, ohne bei jeder Frage alles zu lesen; Kontextfenster und Credits schonen.                                                           |
| E3  | Zufälliges Kontrollwort am Ende jeder Datei                                                                                                                   | Nur ein nicht ableitbares Wort beweist, dass der Agent die Datei bis zum Ende gesehen hat.                                                                 |
| E4  | Wertstatus für Grafikwerte; Ablesen am Seitenbild als Standard                                                                                                | Verhindert Scheingenauigkeit; Berechnung aus der Vektorgrafik ist optional.                                                                                |
| E5  | Prüfung: Zahlen einzeln (mit Häufigkeit), Wörter als Quote pro Seite (Schwelle 95 %)                                                                          | Findet fehlende und veränderte Zahlen sowie ausgelassene Aussagen ohne Zahlen, ohne Flut an Fehlalarmen.                                                   |
| E6  | Unbeschriftete Grafiken: im Spike alle prüfen, danach jede fünfte                                                                                             | Der Zahlen-Check ist bei diesen Werten blind; Stichprobe nur bei gemessener Fehlerquote ≤ 3 Prozentpunkte.                                                 |
| E7  | Transkription in Copilot Studio (Ingest-Agent)                                                                                                                | Einzige verfügbare Umgebung; Python-Sandbox mit pdfplumber vorhanden.                                                                                      |
| E8  | Zwei Agenten: Library (Fragen) und Ingest (Pflege)                                                                                                            | Verschiedene Anweisungen, Rechte und Nutzerkreise.                                                                                                         |
| E9  | Teilgrösse nach Messung (Startwert 18’000 Bytes)                                                                                                              | Das Lesewerkzeug kürzt laut Drittquelle über 20 KB.                                                                                                        |
| E10 | Volltext zuerst, Study Card daraus                                                                                                                            | Die Card belegt Seiten des geprüften Volltexts.                                                                                                            |
| E11 | «Schlussfolgerungen der Studie» getrennt von «Redaktioneller Einordnung LAV»                                                                                  | Der Agent darf Interpretation nie als Studienbefund zitieren.                                                                                              |
| E12 | Golden Set: 15–20 Fragen im Spike, danach 1–2 pro Studie; Lauf nach jedem Update                                                                              | Mit jeder Studie wachsen Verwechslungsgefahr und Dateigrössen; Plattform-Updates ändern das Verhalten.                                                     |
| E13 | Ingest in Etappen: höchstens ETAPPEN_PRO_ANTWORT Etappen à 5 Seiten pro Antwort (Start: 1), danach Stand melden; ab 40 Seiten alle 20 Seiten ein Zwischen-ZIP | Zeit- und Werkzeuggrenzen pro Antwort sind für den Harness nicht dokumentiert; ein Abbruch darf keine Arbeit kosten. Wert nach Test P9.                    |
| E14 | Fall A bleibt «alle Teile lesen». Die Variante für grosse Studien (A2) liegt bereit und wird nur nach Spike-Befund und mit Zustimmung eingesetzt.             | A2 schwächt «vollständig gelesen» ab. Zuerst prüfen, ob eine grössere Teilgrösse reicht (45’000 Bytes ≈ 7 statt ≈ 20 Teile bei 100 Seiten).                |
| E15 | Wiki aus demselben Paket mit `wiki.py`; Agent im Wiki verlinken, einbetten nur nach Test P10                                                                  | Eine Quelle für Agent und Wiki. Für Harness-Agenten gibt es weder SharePoint-Kanal noch Agents SDK; die Sicherheit des Embed-Codes ist nicht dokumentiert. |

### 2.2 Was vorliegt

| Ergebnis                             | Status                   | Hinweis                                                                                                                                                                                                                                                 |
|--------------------------------------|--------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Diese Blaupause                      | Entwurf zur Freigabe     | Ersetzt v1 (Gemini), v2, v2.1 und v3.0.                                                                                                                                                                                                                 |
| Skill des Library-Agenten (Vorlage)  | fertig                   | SKILL.md, Katalog- und Card-Vorlage; im Tenant ungetestet.                                                                                                                                                                                              |
| Ingest-Skill `lav-ingest`            | fertig, lokal getestet   | SKILL.md mit Etappen, Fortsetzen und Wiki-Ablauf; 5 Skripte (inkl. `wiki.py`), Regeln, Vorlagen, Skripte als Text. Lokal getestet mit Python 3.13 und pdfplumber 0.11.10; die Sandbox hat laut Drittquelle Python 3.12 und dieselbe pdfplumber-Version. |
| Plattform-Testpaket                  | fertig (Fassung 2)       | Test-Skill (zwei ZIP-Varianten), Lösungsschlüssel, Test-PDF. Lesetest-Stufen in Bytes passend zur Teilgrösse; ersetzt die erste Fassung.                                                                                                                |
| Referenztranskripte LAV-T01, LAV-T02 | geprüft                  | Gesundheitsmonitor 2024 und 2025, eine Datei je Seite, mit Prüfprotokoll. Der Prüfer fand dabei zwei echte Fehler in LAV-T02 (fehlende Lesehilfe S. 15, fehlende «Weiss nicht»-Werte S. 20); beide behoben.                                             |
| Referenztranskript LAV-T03           | Entwurf, nicht beigelegt | Helsana-Arzneimittelreport 2024 (102 Seiten); Seiten 1–37 bearbeitet, Rest offen. Im Spike im Ingest-Agenten neu erstellen.                                                                                                                             |
| Beispielpaket LAV-T02                | geprüft                  | Gültiges Library-Paket mit einer Studie (7 Teile à ≤ 18’000 Bytes); `paket.py` ohne Befunde.                                                                                                                                                            |
| Golden-Set-Beispiele                 | 12 Fragen                | Mit Sollantworten und Seiten aus den öffentlichen Teststudien.                                                                                                                                                                                          |
| Wiki-Unterlagen                      | fertig                   | Anforderungen und Abnahme, Anweisungen für GitHub Copilot, Beispielausgabe von `wiki.py` (öffentliche Teststudie).                                                                                                                                      |
| Variante für grosse Studien (A2)     | vorbereitet, nicht aktiv | Baustein für SKILL.md des Library-Agenten; Einsatz nur nach Spike-Befund (E14).                                                                                                                                                                         |

### 2.3 Testergebnisse der Skripte (lokal)

| Test                                                                                                                                                                                  | Ergebnis                                                                                                                                                                                |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Fehlerinjektion in LAV-T02: Absatz ohne Zahlen gelöscht, Tabellenwert 49 → 48, Seite gelöscht, Wertstatus entfernt, falscher Seitenmarker                                             | 5 von 5 erkannt.                                                                                                                                                                        |
| Geprüftes Referenztranskript LAV-T02 (27 Seiten)                                                                                                                                      | 5 Seiten gemeldet, alle begründbar: überlappende Grafikbeschriftungen in der Textebene (4), leere Doppelseite (1). Wortabdeckung minimal 96.6 %, Mittel 99.4 %.                         |
| Geprüftes Referenztranskript LAV-T01 (19 Seiten)                                                                                                                                      | 2 Seiten gemeldet, beide begründbar. Wortabdeckung minimal 97.8 %.                                                                                                                      |
| Paketprüfung mit Manipulationen: fehlende Schlusszeile, Kontrollwort zusätzlich in SKILL.md, falscher Seitenbereich im Katalog, fehlender Seitenmarker, fremde Dateien (CSV) im Paket | Alle erkannt; gültiges Paket ohne Befunde; Erneuerung der Kontrollwörter von Katalog und Cards funktioniert.                                                                            |
| Ersatzweg: Skripte aus `references/skripte.md` herausschreiben und ausführen                                                                                                          | Code identisch, Durchlauf Inventar → Prüfung → Aufteilen → Paket → Wiki erfolgreich.                                                                                                    |
| `wiki.py` auf das Beispielpaket                                                                                                                                                       | Übersicht und Studienseite erzeugt; kein Kontrollwort im Ergebnis; Seitenangaben werden zu Links auf die PDF-Seite, sobald «Original» ein Link ist; Verweise nur auf vorhandene Seiten. |

### 2.4 Offene Punkte

| Punkt                                                        | Wer                                  | Wie geklärt                                               |
|--------------------------------------------------------------|--------------------------------------|-----------------------------------------------------------|
| Gates G1–G5                                                  | Projektleitung, InfoSec, Dateneigner | Schriftliche Freigaben (Abschnitt 4).                     |
| Plattformtests P1–P10                                        | Projektleitung im Tenant             | Phase 0b mit Testpaket, Beispielpaket und Ingest-Skill.   |
| Format für den Import des Golden Set in den Evaluate-Bereich | ausführende AI                       | Im Tenant prüfen; Beispiel-CSV bei Bedarf umformatieren.  |
| Kosten (Copilot Credits) pro Ingest und pro Frage            | Projektleitung                       | P7 und Spike.                                             |
| Einstellung «allgemeines Modellwissen» im Library-Agenten    | ausführende AI                       | Im Tenant prüfen, ob die Einstellung angeboten wird.      |
| Zeit- und Werkzeuggrenzen pro Antwort                        | ausführende AI                       | P9 (Ingest) und Spike mit grosser Studie (Library).       |
| Einbindung des Agenten in eine Website                       | Projektleitung                       | P10; bis dahin Link auf Teams bzw. Microsoft 365 Copilot. |
| Hosting des Wikis                                            | Projektleitung, InfoSec              | Gate G5, Optionen in `wiki-anforderungen.md`.             |

## 3 Kontext, Ziel und Plattform · System-Briefing

Für den Bereich LAV der Helsana entsteht eine AI-gestützte Learning Library über interne Forschungsstudien: ein Agent in Copilot Studio und ein für Menschen lesbares Wiki aus denselben Study Cards. Bestand: 25 interne Studien als PDF, gemischt aus Foliendecks mit vielen Grafiken und textlastigen Berichten mit Tabellen.

### 3.1 Killerkriterium – vier prüfbare Anforderungen

1.  **Richtige Studie:** Der Agent bestimmt die Studie eindeutig oder fragt nach, wenn zwei passen.
2.  **Vollständig gelesen:** Bei Fragen zu einer Studie liest der Agent alle Teile ihres Volltexts, nachweisbar über Kontrollwörter.
3.  **Belegte Zahlen:** Jede Aussage trägt `[LAV-XX, S. n]`, jeder Grafikwert seinen Status.
4.  **Sichtbare Lücken:** Was die Studien nicht belegen, sagt der Agent ausdrücklich.

**Nicht-Ziele:** keine Websuche, kein allgemeines Weltwissen, keine eigenen Empfehlungen des Agenten, die als Studienaussage erscheinen.

### 3.2 Warum kein «Knowledge»

Verworfen: «Knowledge» (Suche in Textabschnitten)

- Liefert nur gefundene Abschnitte; die Studie wird nie vollständig gelesen.
- Zahlen aus Grafiken fehlen oder stehen ohne Zusammenhang.
- Kann keine Dateien auflisten oder per Dateiname ansprechen.
- Vertraulich gelabelte Dokumente werden nicht indexiert; die Antwort bleibt leer.

Ziel: Skill-ZIP mit drei Ebenen

- **Katalog:** klein, bei jeder Anfrage gelesen; IDs, Aliasse, Verwechslungshinweise.
- **Study Cards:** gebündelt, für übergreifende Fragen.
- **Volltext in Teilen:** Seitenmarker, Grafikwerte mit Status, Kontrollwort am Ende jedes Teils.

Der Verzicht auf Knowledge begründet sich mit der Vollständigkeit, nicht mit dem Umgehen von Labels. Die Label-Frage regeln die Gates.

### 3.3 Was über die Plattform bekannt ist

| Aussage                                                                                                                                                                                                                                                                                          | Quelle                                                                         | Konsequenz                                                                     |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| Der GitHub Copilot Harness ist allgemein verfügbar, führt Aufgaben in einer Sandbox aus und erzeugt Word-, Excel-, PowerPoint- und PDF-Dateien.                                                                                                                                                  | Microsoft (Learn, Blog)                                                        | Grundlage für Ingest im Tenant.                                                |
| Datenschutz-, Sicherheits- und Data-Residency-Zusagen von Copilot Studio gelten; Daten gehen nicht an den GitHub-Copilot-Dienst. Verbrauch in Copilot Credits.                                                                                                                                   | Microsoft Learn                                                                | Unterlage für G1/G3.                                                           |
| Sandbox mit Python-Laufzeit, vorinstallierten Bibliotheken, ohne Netzwerkzugang; Ablage nicht dauerhaft; Skills können Skripte mitbringen.                                                                                                                                                       | Microsoft (Copilot Studio Blog)                                                | Ergebnisse pro Gespräch herunterladen; keine Pakete nachinstallieren.          |
| Datei-Upload im Chat ist eine Vorschaufunktion.                                                                                                                                                                                                                                                  | Microsoft Blog                                                                 | Test P4, Ersatzweg SharePoint.                                                 |
| Werkzeuge bash, view, grep, create, edit; Python 3.12 mit pdfplumber, pypdf, rapidocr; `view` kürzt Dateien über 20 KB, wenn nicht die ganze Datei angefordert wird.                                                                                                                             | tyto.se (Drittquelle)                                                          | Teilgrösse 18’000 Bytes als Startwert; Tests P2, P3.                           |
| Kein dokumentierter, stabiler Pfad zu gepackten Binärdateien eines Skills.                                                                                                                                                                                                                       | Microsoft Q&A (Forum)                                                          | Skripte zusätzlich als Text in `references/skripte.md`; Test P3.               |
| Jeder einzelne Antwortstrom eines Modells hat ein Zeitlimit von 5 Minuten. Grenzen für Werkzeugaufrufe oder die Dauer einer ganzen Antwort sind nicht dokumentiert; der Harness wird auf der Seite nicht erwähnt.                                                                                | Microsoft Learn (Quotas and limits)                                            | Ingest in Etappen (E13); Test P9; Spike mit grosser Studie.                    |
| Kanäle für Harness-Agenten: Microsoft 365 Copilot, Teams, Demo-Website, Web app (iframe). Nicht verfügbar: SharePoint, Native app (Direct Line), MCP-Client; das Agents SDK ist nicht aufgeführt.                                                                                                | Microsoft Learn (Kanäle für GitHub-Copilot-Agenten)                            | Agent im Wiki verlinken; Einbetten nur nach P10.                               |
| Agents SDK mit Connection String (Doku für Standard-Agenten): nur mit «Authenticate with Microsoft» oder manueller Anmeldung, App-Registrierung mit delegierter Berechtigung CopilotStudio.Copilots.Invoke. Der Embed-Code erscheint nur ohne Authentifizierung – der Agent ist dann öffentlich. | Microsoft Learn (Agents SDK)                                                   | Embed-Code ohne Anmeldung verletzt G2.                                         |
| Die Copilot-Studio-Clientbibliothek des Agents SDK unterstützt den GitHub Copilot Harness derzeit nicht.                                                                                                                                                                                         | GitHub microsoft/Agents, Issue \#730 (ohne Antwort von Microsoft); Drittquelle | Connection-String-Weg nicht einplanen; in P10 prüfen, was der Tenant anbietet. |

## 4 Harte Voraussetzungen (Gates) · Vor jeder Verarbeitung

| Gate                          | Bedingung                                                                                                                                                                                                                                                            | Warum                                                                                                                                           |
|-------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| G1 Datenfreigabe              | Schriftliche Freigabe von Dateneigner und InfoSec für (a) die Verarbeitung im Ingest-Agenten und (b) die Ablage der Inhalte im Skill des Library-Agenten.                                                                                                            | Im Skill-ZIP verliert der Inhalt das Purview-Label und die Berechtigungen pro Person. Das Label ist eine Kontrolle, kein technisches Hindernis. |
| G2 Nutzerkreis                | Library-Agent nur für den Kreis, der alle enthaltenen Studien sehen darf; Studien mit engerem Kreis nicht ins ZIP. Ingest-Agent nur für das Pflegeteam.                                                                                                              | Der Agent kennt keine Berechtigungen pro Studie.                                                                                                |
| G3 Verarbeitungsort           | Transkription interner Studien nur im Ingest-Agenten im Helsana-Tenant. Tests ausserhalb nur mit öffentlichen Studien.                                                                                                                                               | Interne Studien verlassen den Tenant nicht.                                                                                                     |
| G4 Wiki und Quellordner       | Publizierte Study Cards und der SharePoint-Quellordner tragen das höchste Label der enthaltenen Studien und dieselbe Berechtigung wie der Library-Agent bzw. das Pflegeteam.                                                                                         | Cards und Volltexte enthalten Kernzahlen vertraulicher Studien.                                                                                 |
| G5 Wiki-Werkzeuge und Hosting | Freigabe von InfoSec für (a) die Hosting-Plattform des Wikis mit Entra-Anmeldung und Nutzerkreis gemäss G2, (b) den Ort des Repositorys, (c) GitHub Copilot in VS Code mit der Regel, dass echte Inhalte nie in den Copilot-Kontext und nie ins Repository gelangen. | GitHub Copilot in VS Code ist der GitHub-Copilot-Dienst; die Datenzusage für Harness-Agenten in Copilot Studio gilt dafür nicht.                |

## 5 Architekturprinzipien · Design-Entscheidungen

1.  **Nur aus dem Skill.** Library-Agent ohne Knowledge, ohne Websuche, ohne allgemeines Modellwissen.
2.  **Zwei Agenten.** Library-Agent beantwortet Fragen; Ingest-Agent transkribiert und prüft Pakete.
3.  **Statisches Skill-ZIP.** Kein Power Automate, keine Datenbank. Ein versioniertes ZIP reicht für 2–3 neue Studien pro Jahr.
4.  **Drei Ebenen mit klarer Lesepflicht.**
    - `00-katalog*.md` – bei jeder Anfrage gelesen; höchstens ca. 600 Zeichen pro Studie; bei Bedarf auf mehrere Dateien verteilt.
    - `01-study-cards*.md` – alle Cards gebündelt, gelesen bei übergreifenden Fragen; so viele Dateien, wie die Teilgrösse verlangt.
    - `volltext/LAV-XX/teil-NN.md` – jede Studie in Teilen, nur an Seitengrenzen geteilt; Seitenbereiche im Katalog. Geteilt wird immer.
5.  **Teilgrösse nach Messung.** Startwert 18’000 Bytes (UTF-8, unter 20 KB). Der Lesetest prüft genau die Stufen 18’000, 30’000 und 45’000 Bytes; es gilt die grösste Stufe, die der Agent zuverlässig vollständig liest.
6.  **Lesebeweis über zufällige Kontrollwörter.** Jede Datei endet mit einer Zeile mit Kontrollwort (z. B. `MUSTER-17`). Das Wort ist zufällig, steht nirgends sonst und lässt sich nicht ableiten. Volltext-Teile erhalten es bei der Aufteilung, Katalog und Cards bei jeder Paketprüfung neu. Die Liste liegt im Quellordner, nie im ZIP.
7.  **Wertstatus für jede Grafikzahl:** beschriftet · abgelesen ca. · berechnet (nur per Skript, mit Genauigkeit) · nicht eindeutig ablesbar.
8.  **Eindeutige Seitenangaben.** Zitiert wird die PDF-Seite; abweichende Druckseiten stehen im Seitenmarker.
9.  **Quellordner als Ablage.** Die Sandbox speichert nichts über ein Gespräch hinaus; alle Ergebnisse liegen im SharePoint-Quellordner, das ZIP wird daraus gebaut.

## 6 Ordner- und Dateistruktur · Paket-Architektur

``` keep
lav-learning-library.zip             Skill des Library-Agenten (nur SKILL.md und references/*.md)
├── SKILL.md                         Ablauf, Zitier- und Zahlenregeln, Abschlusszeilen
└── references/
    ├── 00-katalog.md                alle Studien (bei Bedarf 00-katalog-a.md, -b.md)
    ├── 01-study-cards.md            alle Study Cards (bei Bedarf -a.md, -b.md …)
    └── volltext/
        ├── LAV-01/
        │   ├── teil-01.md           PDF-Seiten 1–4
        │   └── teil-02.md           PDF-Seiten 5–8 …
        └── …
```

``` keep
lav-ingest.zip                       Skill des Ingest-Agenten (nur Pflegeteam)
├── SKILL.md                         Abläufe: Studie aufnehmen, Fortsetzen, Paket prüfen, Wiki aufbereiten
├── scripts/
│   ├── inventar.py                  Seitentabelle, Textebene je Seite, Tabellen, Seitenbilder
│   ├── pruefen.py                   Seitenmarker, Zahlen-Check, Wortabdeckung, Grafikstatus
│   ├── aufteilen.py                 Teile, Kopf, Schlusszeile mit Kontrollwort
│   ├── paket.py                     Prüfung des Library-Pakets, Erneuerung der Kontrollwörter
│   └── wiki.py                      Wiki-Seiten aus dem geprüften Paket (ohne Kontrollwörter)
└── references/
    ├── transkriptionsregeln.md      Regeln je Element, Grafikblock, Muster
    ├── vorlagen.md                  Katalog-Eintrag, Study Card
    └── skripte.md                   alle Skripte als Text (Ersatzweg)
```

``` keep
Arbeitsordner im Ingest-Gespräch     arbeit/LAV-NN/
├── inventar.txt · inventar.json     Seitentabelle
├── rohtext/s001.txt …               Textebene je Seite (+ s001-tabellen.md, wo Tabellen erkannt)
├── bilder/s001.png …                Seitenbilder
├── seiten/s001.md …                 Transkript, eine Datei je PDF-Seite
├── volltext/teil-01.md …            aufgeteilter Volltext (geht ins Library-Paket)
├── kontrollwoerter.csv · katalog-zeile.txt
├── pruefprotokoll.txt · befunde-begruendet.txt · grafiken-abgelesen.txt · zeiterfassung.csv
└── card.md · katalog-eintrag.md

SharePoint-Quellordner «LAV Library – Quelle» (Ablage der Wahrheit)
├── LAV-07/                          original.pdf + Inhalt von LAV-07_ingest.zip
├── golden-set.csv · kontrollwoerter_alle.csv
├── pakete/lav-learning-library_v1.3.zip
└── wiki/lav-wiki_<Datum>.zip            Ausgabe von «Wiki aufbereiten»
```

## 7 Transkription · Regeln

Verbindlich: Dateien statt Chat-Antworten

Ein Transkript entsteht als Datei in der Sandbox, nie als Chat-Antwort zum Kopieren. Nie kürzen oder zusammenfassen, um in ein Ausgabelimit zu passen. Werden Kontext oder Ausgabe knapp: nach der letzten vollständigen Seite unterbrechen, Zwischenstand herunterladen, im neuen Gespräch fortsetzen. Eine Studie pro Gespräch.

### 7.1 Format

    # LAV-07 · Volltext · Teil 2 von 5 (PDF-Seiten 10–18 von 48)

    Studie: [Volltitel] · Quelldatei: [Dateiname.pdf] · Transkript-Version 1.0 · [Datum]
    Lesehinweis: Die Studie ist nur vollständig gelesen, wenn alle 5 Teile bis zum Ende gelesen sind.
    Konventionen: [[Seite n/N]] = Beginn der PDF-Seite n (zitieren als [LAV-07, S. n]) · Grafikwerte mit Status …

    ---

    [[Seite 10/48 · Druckseite 9]]

    ## Wechselmotive nach Alter
    …

    ---

    — Ende Teil 2 von 5 · Kontrollwort Teil 2: MUSTER-17 · weiter mit teil-03.md —

Kopf und Schlusszeile erzeugt `aufteilen.py`; «MUSTER-17» ist ein Beispiel. Der letzte Teil endet mit «· DOKUMENTENDE LAV-07 —».

### 7.2 Regeln je Element

| Element im PDF               | Vorschrift                                                                                                                                      | Verboten                                               |
|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------|
| Seitenbeginn                 | `[[Seite n/N]]`; bei abweichender Druckseite `[[Seite n/N · Druckseite x]]` bzw. `· Druckseiten x–y`. Leere Seiten: Marker + «\[leere Seite\]». | Seiten zusammenziehen; Trennfolien weglassen.          |
| Titel, Überschriften         | Markdown-Überschrift, wörtlich.                                                                                                                 | Titel erfinden.                                        |
| Fliesstext, Bullets          | Wörtlich; Silbentrennung auflösen, sonst nichts ändern.                                                                                         | Paraphrasieren, kürzen.                                |
| Kästen, Zitate               | `**[Kernaussagen]** … **[Ende Kernaussagen]**`; Zitate in «…» mit Quelle.                                                                       | Kästen auflösen, Zitate glätten.                       |
| Tabellen                     | Markdown-Tabelle mit allen Zeilen und Spalten; bei unsicherer Spaltenzuordnung zusätzlich Originallayout als Codeblock.                         | Zeilen weglassen; Summen ergänzen.                     |
| Diagramm mit Werten          | Grafikblock (7.3) mit allen beschrifteten Werten.                                                                                               | Platzhalter ohne Zahlen.                               |
| Diagramm ohne Werte          | Am Seitenbild ablesen; jede Zelle «ca. 12»; Genauigkeit im Darstellungstext.                                                                    | Werte ohne «ca.»; Werte für nicht dargestellte Punkte. |
| Nicht eindeutig              | Zelle «nicht eindeutig ablesbar», Grund im Darstellungstext; Eindeutiges trotzdem übernehmen.                                                   | Plausible Zuordnung raten.                             |
| Karten                       | Tabelle Region → Klasse bzw. Wert.                                                                                                              | Nur die Legende übernehmen.                            |
| Journeys, Matrizen, Prozesse | Tabelle: Phasen bzw. Quadranten als Zeilen mit allen Inhalten; Pfeile und Beziehungen als Text.                                                 | Nur Phasen- oder Achsentitel.                          |
| Bilder, Logos                | `[Bild: …]`, wenn informativ; Text im Bild wörtlich.                                                                                            | Bildtext weglassen.                                    |
| Fussnoten, Quellen, Basis    | Wörtlich; `[Fussnote n] …` auf ihrer Seite; Verweise als `[n]`.                                                                                 | Weglassen.                                             |
| Unleserliches, Widersprüche  | `[unleserlich]`; `[Hinweis Transkription: …]`.                                                                                                  | Stillschweigend glätten.                               |

### 7.3 Grafikblock und Muster

``` keep
**[Grafik 4] Titel wörtlich wie in der PDF**

Frage: «Fragetext wörtlich»
Darstellung: Liniendiagramm, 1998–2025, Anteil in % Stimmberechtigte. Wertstatus: beschriftet sind die
Werte 2025; übrige Jahre abgelesen ca. (Genauigkeit ± 2 Prozentpunkte).

| Jahr | Zahnarztrechnungen | Krankenkassenprämien |
|---|---|---|
| 2024 | ca. 12 | ca. 10 |
| 2025 (beschriftet) | 18 | 17 |

Quelle: © … wörtlich · Fussnoten wörtlich (N = …)

**[Ende Grafik 4]**
```

Gestapelte Balken und Säulen: eine Spalte je Segment in Legendenreihenfolge, nicht beschriftete Segmente «–»; Zeilensummen prüfen, Abweichungen im Original als Hinweis vermerken. Vollständige Muster: Referenztranskripte LAV-T01 und LAV-T02 (Anhang E).

## 8 Ablauf im Ingest-Agenten · Pro Studie

1.  **Hochladen:** neues Gespräch, PDF hochladen, Studien-ID, Kurztitel und Jahr nennen.
2.  **Inventar** (`inventar.py`): Seitentabelle, Textebene, Tabellen, Seitenbilder.
3.  **Transkription** in Etappen von höchstens fünf Seiten, je Seite Rohtext plus Seitenbild; nach jeder Etappe Zwischenprüfung. Höchstens ETAPPEN_PRO_ANTWORT Etappen pro Antwort, dann meldet der Agent den Stand und wartet auf «weiter». Ab 40 Seiten alle 20 Seiten ein Zwischen-ZIP.
4.  **Schlussprüfung** (`pruefen.py`): jede Meldung beheben oder begründen.
5.  **Aufteilen** (`aufteilen.py`) mit TEILGROESSE.
6.  **Study Card und Katalog-Eintrag** aus dem geprüften Volltext.
7.  **Liste der abgelesenen Grafiken** für die Sichtprüfung.
8.  **Ausgabe:** `LAV-NN_ingest.zip` herunterladen, im Quellordner ablegen.

**Unterbruch:** neues Gespräch, PDF und letztes Zwischen-ZIP hochladen, «Fortsetzen» – der Agent erzeugt Rohtext und Seitenbilder neu und macht bei der ersten fehlenden Seite weiter.

Danach: Mensch prüft gemeldete Seiten und Grafiken (12.2), Research gibt die Card frei, Katalog- und Card-Datei werden ergänzt, Paketprüfung im Ingest-Agenten (`paket.py`), Upload im Library-Agenten, Golden-Set-Lauf, bei Bedarf «Wiki aufbereiten» (`wiki.py`).

## 9 Ingest-Skill: SKILL.md · Datei im ZIP

Dateien verwenden, nicht aus dem PDF kopieren

Kopieren aus einem PDF verändert Zeilenumbrüche und Einrückungen. Massgebend sind die Dateien im Übergabe-ZIP bzw. die Anhänge dieses PDF. Im Druck umbrochene Zeilen (z. B. `description:`) stehen in den Dateien auf einer Zeile.

lav-ingest/SKILL.md

    {{FILE:ingest/skill/SKILL.md}}

## 10 Ingest-Skill: Skripte · Spezifikation

Alle Skripte: Python 3.12 oder neuer, nur Standardbibliothek und pdfplumber (inkl. pypdfium2 für Seitenbilder), kein Netzwerk. Exit-Code 0 = keine Befunde, 1 = Befunde, 2 = Fehler. Vollständiger Code im Übergabe-ZIP.

### 10.1 Übersicht

| Skript       | Aufruf                                                                                                      | Ausgabe                                                                                                | Zweck                                                                                                                |
|--------------|-------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| inventar.py  | `inventar.py <pdf> <arbeitsordner> [--bilder alle|grafik|keine] [--aufloesung 120]`                         | inventar.txt/.json, rohtext/sNNN.txt, rohtext/sNNN-tabellen.md, bilder/sNNN.png, leerer Ordner seiten/ | Grundlage der Transkription; Typ-Vorschlag je Seite (Text, Grafik/Bild, leer, ohne Textebene).                       |
| pruefen.py   | `pruefen.py <pdf> <seitenordner|datei.md> [--schwelle 0.95] [--protokoll …] [--nur-vorhandene]`             | Prüfprotokoll (Text) und .json                                                                         | Vollständigkeit und Treue gegen die Textebene (10.2).                                                                |
| aufteilen.py | `aufteilen.py <seitenordner> <zielordner> --id LAV-NN --titel … --quelle … [--max 18000] [--bestehend csv]` | teil-NN.md; im übergeordneten Ordner kontrollwoerter.csv und katalog-zeile.txt                         | Teile nur an Seitengrenzen, Grösse in Bytes; zufällige, eindeutige Kontrollwörter.                                   |
| paket.py     | `paket.py <zip|ordner> [--max 18000] [--erneuern] [--ausgabe zip] [--csv datei]`                            | Prüfbericht; geprüftes ZIP; Liste aller Kontrollwörter                                                 | Prüfung des Library-Pakets vor dem Upload (10.3).                                                                    |
| wiki.py      | `wiki.py <zip|ordner> <zielordner> [--agent-link URL] [--hinweis Text]`                                     | index.md, LAV-XX.md                                                                                    | Wiki-Seiten aus dem geprüften Paket; ohne Kontrollwörter und Volltext-Teile; Seitenlinks auf die PDF (Abschnitt 13). |

### 10.2 Prüflogik von pruefen.py

- **Seiten:** jede PDF-Seite vorhanden; erste Zeile `[[Seite n/N …]]` mit richtigem n und N; Inhalt vorhanden.
- **Textebene:** Wörter je Seite mit pdfplumber, doppelt gezeichnete Zeichen entfernt, Kopf- und Fusszeilenbereich (oberste und unterste 4.5 %) ausgeschlossen, Silbentrennung über Zeilenumbrüche zusammengeführt, getrennte Tausendergruppen («200 000», «1’ 000») vereint.
- **Zahlen-Check:** Zahlen normalisiert (Apostroph entfernt, Komma → Punkt; 1.209 ≙ 1209; zweistellige Achsenjahre 97 ≙ 1997). Achsenbeschriftungen (≥ 3 bündige Zahlen mit gleichem Abstand und gleichem Wertschritt) werden ignoriert und im JSON gelistet. Mehrstellige Zahlen werden nach Häufigkeit geprüft («seltener als in der PDF» findet veränderte Werte); einstellige Zahlen und Jahreszahlen nur auf Vorhandensein. In der Textebene zusammengeklebte Beschriftungen («8811» = 88 und 11) gelten als gefunden.
- **Wortabdeckung:** Anteil der Wörter (≥ 3 Buchstaben) der Textebene, die im Transkript derselben Seite vorkommen; Meldung unter der Schwelle mit Liste fehlender Wörter.
- **Grafikblöcke:** jeder `[Grafik …]` hat ein `[Ende Grafik …]` und einen Wertstatus (beschriftet, abgelesen, berechnet oder nicht eindeutig).
- **Grenzen:** Seiten ohne Textebene werden nur gemeldet. Unbeschriftete Grafikwerte stehen nicht in der Textebene; ihre Prüfung bleibt Sichtprüfung (E6). Überlappende Beschriftungen erzeugen einzelne Fehlalarme, die begründet werden.

### 10.3 Prüflogik von paket.py

- Genau eine SKILL.md (oberste Ebene oder ein Unterordner) mit Frontmatter `name` und `description`; nur SKILL.md und references/\*.md im Paket.
- Jede Datei unter references/ endet mit einer Schlusszeile mit Kontrollwort; Kontrollwörter eindeutig und nirgends sonst im Paket; Dateigrösse ≤ --max Bytes.
- Je Studie: teil-01 … lückenlos; Kopf «Teil i von n (PDF-Seiten a–b von N)»; Seitenmarker a…b vollständig; Bereiche decken 1–N lückenlos; Schlusszeile nennt «Teil i von n».
- Katalog: Eintrag `## LAV-NN` mit korrekter Zeile «Volltext»; Cards: `## LAV-NN` und «— Ende Card LAV-NN —»; keine Katalogeinträge ohne Volltext.
- `--erneuern`: neue Kontrollwörter für Katalog und Cards; `--ausgabe`: ZIP in derselben Struktur.

### 10.4 Dateiformate

| Datei                   | Inhalt                                                                                                                           |
|-------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| kontrollwoerter.csv     | Semikolon-getrennt: `datei;kontrollwort;seiten;bytes;datum` (je Studie) bzw. `datei;kontrollwort` (ganzes Paket). Nie hochladen. |
| katalog-zeile.txt       | `- Volltext: 7 Teile – teil-01 S. 1–4 · teil-02 S. 5–8 · …`                                                                      |
| befunde-begruendet.txt  | `Seite;Meldung;Begründung`                                                                                                       |
| grafiken-abgelesen.txt  | `Seite;Grafik;Status`                                                                                                            |
| zeiterfassung.csv       | `schritt;start;ende`                                                                                                             |
| golden-set.csv          | `id;typ;studien;frage;sollantwort;belege;bestanden_wenn` (UTF-8 mit BOM, Semikolon)                                              |
| lav-wiki\_\<Datum\>.zip | `index.md` (Übersicht) und `LAV-XX.md` (je Studie), Markdown mit Tabellen.                                                       |

### 10.5 Regressionstest nach jeder Skriptänderung

1.  `pruefen.py` gegen die Referenztranskripte LAV-T01 und LAV-T02: höchstens die in `befunde-begruendet.txt` begründeten Meldungen.
2.  Fünf Fehler in eine Kopie von LAV-T02 einbauen (Absatz ohne Zahlen löschen, Tabellenwert ändern, Seite löschen, Wertstatus entfernen, Seitenmarker verfälschen): alle fünf müssen gemeldet werden.
3.  `aufteilen.py` und `paket.py` auf das Beispielpaket: keine Befunde; fünf Manipulationen am Paket (Schlusszeile, doppeltes Kontrollwort, Katalogbereich, Seitenmarker, fremde Datei) müssen gemeldet werden.
4.  `wiki.py` auf das Beispielpaket: Übersicht und Studienseite, kein «Kontrollwort» im Ergebnis.
5.  `references/skripte.md` neu erzeugen; Code identisch mit `scripts/`.

## 11 Library-Agent: SKILL.md und Vorlagen · Dateien im ZIP

lav-learning-library/SKILL.md

    {{FILE:blaupause/vorlagen/SKILL.md}}

references/00-katalog.md (Vorlage)

    {{FILE:blaupause/vorlagen/00-katalog.md}}

references/01-study-cards.md (Vorlage)

    {{FILE:blaupause/vorlagen/01-study-cards.md}}

Vorbereitete Variante für grosse Studien (nicht aktiv, Entscheidung E14)

    {{FILE:uebergabe/Variante_Fall-A2_grosse-Studien.md}}

## 12 Qualitätssicherung und Golden Set · Prüfung

### 12.1 Automatisch

`pruefen.py` je Studie (10.2) und `paket.py` je Paket (10.3). Jede Meldung wird behoben oder begründet.

### 12.2 Manuell

- Alle Seiten, die `pruefen.py` meldet, und alle Begründungen.
- Unbeschriftete Grafiken: im Spike alle (Fehlerquote messen); danach jede fünfte, wenn die Abweichung höchstens 3 Prozentpunkte beträgt und nichts vertauscht ist; sonst alle.
- Research gibt die Card frei: jede Zahl der Card gegen den Volltext.

### 12.3 Golden Set

- **Umfang:** 15–20 Fragen im Spike, danach 1–2 pro neue Studie (bei 25 Studien ca. 40–60).
- **Fragetypen:** Detail aus der Dokumentmitte (Grafikwert, Tabellenzelle) · Wert ohne Beschriftung · übergreifend · Mehrdeutigkeit · Fangfrage · Lesebeweis · Katalog.
- **Lauf:** Evaluate-Bereich nach jedem Paket-Update und nach Plattformänderungen.
- **Abnahme (Vorschlag):** Fangfragen und Lesebeweis 100 %; keine erfundene Zahl; Detailfragen ≥ 90 % mit richtiger Seite.

Beispiele aus den öffentlichen Teststudien (vollständig mit Bewertungskriterium in `golden-set-beispiel.csv`):

ID

Typ

Frage

Sollantwort

Beleg

(Tabelle siehe testdaten/golden-set/golden-set-beispiel_LAV-T01-T02.csv)

## 13 Wiki und Einbindung des Agenten · Optional

Das Wiki ist eine Ansicht derselben freigegebenen Inhalte für Menschen: eine Übersicht aller Studien und je Studie die Study Card mit Links auf die Original-PDF. Es ist keine zweite Quelle.

### 13.1 Grundsätze

- **Eine Quelle:** Der Ingest-Agent erzeugt die Seiten mit `wiki.py` aus dem geprüften Paket (Ablauf «Wiki aufbereiten»). Im Wiki werden Inhalte nie bearbeitet.
- **Gleicher Kreis:** Zugriff nur mit Entra-Anmeldung, Nutzerkreis wie der Library-Agent (G2), Klassifizierung wie die Studien (G4).
- **Kein Rückfluss:** Das Wiki ist nie Wissensquelle («Knowledge») des Library-Agenten.

### 13.2 Bauen mit VS Code und GitHub Copilot

Geeignet für Code, Layout und Navigation. GitHub Copilot in VS Code ist aber der GitHub-Copilot-Dienst; die Zusage von Microsoft, dass Daten von Harness-Agenten in Copilot Studio nicht an diesen Dienst gehen, gilt dafür nicht. Deshalb gilt Gate G5: entwickeln nur mit der Beispielausgabe der öffentlichen Teststudie (`wiki-beispiel.zip`); echte Inhalte nie in den Copilot-Kontext und nie ins Repository, sondern erst auf der Zielplattform einspielen. Regeln für Copilot: `copilot-instructions.md` (im Repository unter `.github/`); Anforderungen, Hosting-Optionen und Abnahme: `wiki-anforderungen.md`.

### 13.3 Einbindung des Agenten

| Weg                                                      | Stand für Agenten auf dem GitHub Copilot Harness                                                                                                                                                                                                                                | Bewertung                                                                                              |
|----------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| Link auf den Agenten in Teams oder Microsoft 365 Copilot | Verfügbar; Anmeldung und Freigabe gemäss G2 greifen.                                                                                                                                                                                                                            | Standard                                                                                               |
| Web-App-Kanal (iframe, «Embed-Code»)                     | Verfügbar. Ob der Kanal mit «Authenticate with Microsoft» eine Anmeldung erzwingt und fremde Konten abweist, ist nicht dokumentiert. Bei Standard-Agenten erscheint der Embed-Code nur ohne Authentifizierung – der Agent ist dann öffentlich.                                  | Nur nach bestandenem Test P10                                                                          |
| Microsoft 365 Agents SDK (Connection String)             | In der Kanalübersicht für Harness-Agenten nicht aufgeführt; die Clientbibliothek unterstützt den Harness derzeit nicht (GitHub-Issue \#730, offen). Für Standard-Agenten: App-Registrierung mit delegierter Berechtigung, Anmeldung der Nutzer, keine Service-Principal-Tokens. | Nicht einplanen; in P10 prüfen, ob der Tenant für den Harness-Agenten einen Connection String anbietet |
| SharePoint-Kanal                                         | Für Harness-Agenten nicht verfügbar.                                                                                                                                                                                                                                            | –                                                                                                      |

Den Library-Agenten wegen des Agents SDK auf den Standard-Harness umzustellen, ist keine Option für den Spike: Sandbox und Skill-Dateien, auf denen die Lese-Garantie beruht, sind für den GitHub Copilot Harness dokumentiert.

### 13.4 Ablauf

1.  Paket prüfen (Ingest-Agent), dann «Wiki aufbereiten» mit Agent-Link und Hinweiszeile → `lav-wiki_<Datum>.zip`.
2.  Inhalt auf der freigegebenen Plattform ersetzen und veröffentlichen.
3.  Abnahme gemäss `wiki-anforderungen.md` (u. a. kein Kontrollwort, Zugriff für fremde Konten gesperrt).

## 14 Aufwand · Schätzung, im Spike messen

| Tätigkeit                                                                 | Schätzung                         |
|---------------------------------------------------------------------------|-----------------------------------|
| Plattformtests (Phase 0b)                                                 | 0.5–1 Personentag                 |
| Spike: Ingest- und Library-Agent einrichten, 3 Studien, Golden Set, Tests | 3–5 Personentage                  |
| Pro Studie: Transkription im Ingest-Agenten begleiten                     | 0.5–1.5 Stunden                   |
| Pro Studie: gemeldete Seiten und Grafik-Stichprobe prüfen                 | 0.5–1 Stunde                      |
| Pro Studie: Study Card freigeben (Research)                               | ca. 0.5 Stunden                   |
| 25 Studien à 1.5–3 Stunden                                                | 5–10 Personentage                 |
| **Gesamt bis zum Rollout**                                                | **rund 9–16 Personentage**        |
| Zusätzlich, optional: Wiki (Plattform einrichten, Layout, Abnahme)        | 1–3 Personentage, je nach Hosting |

Nicht gemessen. Der Ingest-Agent erfasst im Spike die Zeit pro Schritt; die Hochrechnung daraus geht an den Sponsor. Reicht das Budget nicht, wird der Umfang reduziert (z. B. Start mit den zehn meistgenutzten Studien), nicht die Prüfung. Ingest und Fragen verbrauchen Copilot Credits; beides wird gemessen.

## 15 Einrichtung in Copilot Studio · Implementierung

| Agent                | Einstellungen                                                                                                                                                                                                                                                                                                         | Instructions                                                                                                                                                                                                                                                                                                                                         |
|----------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| LAV Learning Library | GitHub Copilot Harness; kein Knowledge; Websuche aus; allgemeines Modellwissen aus, soweit angeboten; Skill `lav-learning-library.zip` (geprüft; für P8 zuerst `beispielpaket_LAV-T02.zip`); Freigabe gemäss G2; Golden Set im Evaluate-Bereich. Kanal: Teams bzw. Microsoft 365 Copilot; Web-App-Kanal nur nach P10. | «Du bist der LAV Learning Library Agent der Helsana. Beantworte fachliche Fragen zu Studien, Research-Ergebnissen und Kundenwissen ausschliesslich mit dem Skill lav-learning-library und halte dich an dessen Ablauf, Zitier- und Zahlenregeln. Verwende kein allgemeines Weltwissen. Was die Studien nicht belegen, benennst du als nicht belegt.» |
| LAV Ingest           | GitHub Copilot Harness; Skill `lav-ingest.zip`; Datei-Upload im Chat (Vorschau) aktiv; Websuche aus; nur Pflegeteam. TEILGROESSE und ETAPPEN_PRO_ANTWORT nach P2 und P9 in SKILL.md setzen.                                                                                                                           | «Du bist der LAV Ingest-Agent. Du transkribierst LAV-Studien und prüfst Skill-Pakete nach dem Skill lav-ingest. Du arbeitest in Dateien, nie in Chat-Antworten zum Kopieren. Du kürzt und paraphrasierst nie. Was du nicht sicher lesen kannst, kennzeichnest du.»                                                                                   |
| LAV Plattformtest    | GitHub Copilot Harness; Skill `lav-plattformtest.zip`; Datei-Upload aktiv; nur für Phase 0b, danach löschen.                                                                                                                                                                                                          | keine zusätzlichen nötig                                                                                                                                                                                                                                                                                                                             |

## 16 Fahrplan · Umsetzung

### Phase 0a – Gates

G1–G5 klären, Personenkreise festlegen. Ohne G1 wird keine interne Studie verarbeitet; G5 nur, wenn ein Wiki gebaut wird. Phase 0b kann parallel laufen, weil sie nur öffentliche Testdaten nutzt.

### Phase 0b – Plattformtests

Testagent «LAV Plattformtest» anlegen, `lav-plattformtest.zip` hochladen; Testdatei `gesundheitsmonitor-2025.pdf`. `Plattformtest_Loesungen.txt` nie hochladen. Jeden Lesetest in einem neuen Gespräch und zweimal durchführen. Für P8 den Library-Agenten, für P9 den Ingest-Agenten einrichten (Abschnitt 15).

| Test                      | Eingabe im Testbereich                                                                                                                                                                                                                              | Bestanden, wenn                                                                                                                                                                     | Falls nicht                                                                                                                           |
|---------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| P1 Skill-Upload           | ZIP hochladen, dann «Lesetest a».                                                                                                                                                                                                                   | Skill wird verwendet, Datei gelesen.                                                                                                                                                | Variante `lav-plattformtest-ordner.zip`.                                                                                              |
| P2 Lese-Limit             | «Lesetest a», «Lesetest b», «Lesetest c» (18’000 / 30’000 / 45’000 Bytes).                                                                                                                                                                          | Alle vier Kontrollwörter je Datei wie im Lösungsschlüssel, in beiden Durchgängen.                                                                                                   | TEILGROESSE = grösste Stufe, die beide Durchgänge besteht (a → 18’000, b → 30’000, c → 45’000 Bytes); scheitert schon a: Showstopper. |
| P3 Python                 | «Selbsttest»                                                                                                                                                                                                                                        | Python läuft; pdfplumber, pypdf, pypdfium2 vorhanden; Weg notiert (direkt oder Ersatzweg).                                                                                          | Fehlt pdfplumber: Skripte auf pypdf umstellen und Regressionstest.                                                                    |
| P4 Datei-Upload           | PDF hochladen: «PDF-Test Seite 10; lies im oberen Diagramm für jede Linie die Werte 2005, 2010, 2015 und 2020 ab.»                                                                                                                                  | 27 Seiten erkannt, Seite 26 ohne Text gemeldet, Seitenbild erzeugt.                                                                                                                 | PDF über SharePoint-Knowledge des Ingest-Agenten bereitstellen.                                                                       |
| P5 Ablesen                | Antwort aus P4 mit den Referenzwerten im Lösungsschlüssel vergleichen.                                                                                                                                                                              | Abweichung ≤ 3 Prozentpunkte, keine vertauschten Linien.                                                                                                                            | Unbeschriftete Grafiken immer vollständig prüfen; ohne Seitenbild: Showstopper.                                                       |
| P6 Download               | «Download-Test»                                                                                                                                                                                                                                     | Drei Dateien herunterladbar, Umlaute korrekt, ZIP öffnet.                                                                                                                           | Ausgabe über einen Flow in den Quellordner (Connector-Freigabe nötig).                                                                |
| P7 Kosten                 | Credits für P2–P6 und P8–P9 ablesen.                                                                                                                                                                                                                | Werte notiert.                                                                                                                                                                      | –                                                                                                                                     |
| P8 Library-Paket          | Library-Agent mit `beispielpaket_LAV-T02.zip` als Skill; Fragen G01, G08 und G11 aus `golden-set-beispiel.csv`.                                                                                                                                     | G01 und G08 wie Sollantwort; G11 nennt das Kontrollwort von Teil 3 aus `beispielpaket_kontrollwoerter.csv`; Dateien in Unterordnern von references/ werden gefunden.                | Falsches Kontrollwort: Teilgrösse senken (P2). Dateien nicht gefunden: ZIP-Variante und Ordnertiefe prüfen.                           |
| P9 Ingest-Durchlauf       | Ingest-Agent mit `lav-ingest.zip`; PDF hochladen: «Studie aufnehmen: LAV-T02, Gesundheitsmonitor 2025, 2025». Danach «weiter, 2 Etappen ohne Pause», dann «weiter, 4 Etappen ohne Pause». Zwischen-ZIP herunterladen, neues Gespräch, «Fortsetzen». | Jede Antwort endet regulär; Dauer pro Etappe notiert; Seiten 1–5 entsprechen dem Referenztranskript (Abweichungen nur bei «ca.»-Werten); Fortsetzen beginnt an der richtigen Seite. | ETAPPEN_PRO_ANTWORT = grösste Zahl, die ohne Abbruch durchläuft.                                                                      |
| P10 Einbindung (optional) | Library-Agent auf «Authenticate with Microsoft»; unter Kanäle → Web app prüfen, ob Embed-Code oder Connection String angeboten wird; Embed-Code in eine Testseite setzen und mit einem Konto ausserhalb des Nutzerkreises öffnen.                   | Anmeldung wird verlangt und das fremde Konto wird abgewiesen.                                                                                                                       | Agent im Wiki nur verlinken.                                                                                                          |

Nach Phase 0b: TEILGROESSE und ETAPPEN_PRO_ANTWORT in `lav-ingest/SKILL.md` setzen, ZIP-Variante wählen, Skriptweg festhalten, Einbindung des Agenten festlegen (Link oder Web-App-Kanal).

### Phase 1 – Spike mit drei Studien (kurz · lang mit 50+ Seiten · grafiklastig)

1.  Zum Einüben zuerst `gesundheitsmonitor-2025.pdf` im Ingest-Agenten aufnehmen und Seite für Seite mit dem Referenztranskript LAV-T02 vergleichen.
2.  Drei Studien aufnehmen (nach G1 interne, sonst öffentliche); Zeit pro Schritt erfassen.
3.  Alle unbeschrifteten Grafiken gegen das Original prüfen; Fehlerquote festhalten.
4.  Cards freigeben; Golden Set mit 15–20 Fragen (Vorlage: Beispiele in 12.3).
5.  Paket bauen, prüfen, hochladen; Golden Set laufen lassen; Kosten und Antwortzeit messen.
6.  Grosse Studie (über 50 Seiten): im Library-Agenten nach dem Kontrollwort des letzten Teils und nach einem Detail aus der Mitte fragen (Fall A). Scheitert das, zuerst eine grössere TEILGROESSE prüfen; erst danach die Variante für grosse Studien (Abschnitt 11) mit Zustimmung einsetzen (E14).

**Ausstieg aus dem Spike:** Abnahmekriterien 12.3 erfüllt, Fehlerquote beim Ablesen bekannt, Aufwand und Kosten pro Studie gemessen und akzeptiert. Sonst Architektur anpassen, bevor weitere Studien aufbereitet werden.

### Phase 2 – Rollout auf 25 Studien

In Tranchen à fünf Studien; nach jeder Tranche Golden Set erweitern und laufen lassen; Cards nach Freigabe als Wiki publizieren (G4).

### Phase 3 – Betrieb

Neue Studie = Aufnahme im Ingest-Agenten + Prüfung + Card-Freigabe + Paketprüfung + Golden-Set-Lauf. Skill-Version und Änderungsprotokoll im Kopf des Katalogs. Golden Set zusätzlich nach Plattformänderungen. Mit jedem Paket bei Bedarf «Wiki aufbereiten» und das Wiki aktualisieren.

## A Anhang: Änderungsprotokoll · v1 → v3.1

| Version | Wichtigste Änderungen                                                                                                                                                                                                                                                                                                                                                                                                   |
|---------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| v1      | Entwurf Gemini: Skill-ZIP mit Master-Datei (Katalog + Cards) und Volltexten, EOF-Prüfcode nach Schema, Transkription in Chat-Etappen, QA nur über Card-Freigabe.                                                                                                                                                                                                                                                        |
| v2      | Zufällige Kontrollwörter statt ableitbarem Code; Wertstatus für Grafiken; Prüfung des Volltexts statt nur der Card; schlanker Katalog, Cards nur übergreifend, Volltext immer in Teilen; Gates G1–G4; Volltext vor Card; Trennung Studienaussage / redaktionelle Einordnung; Golden Set; Aufwand in Personentagen.                                                                                                      |
| v2.1    | Alles in Copilot Studio (Ingest-Agent); Plattformtests vor dem Spike; Teilgrösse nach Messung; Ablesen als Standard, Berechnung optional; Zahlen einzeln, Wörter als Quote; Golden Set 15–20 + 1–2 pro Studie; Aufwand rund 9–16 Personentage.                                                                                                                                                                          |
| v3.0    | Arbeitsauftrag an die ausführende AI; Entscheidungsprotokoll und Projektstand; Ingest-Skill mit getesteten Skripten; Zahlen-Check mit Häufigkeit und Achsenerkennung; Teilgrösse in Bytes; Regressionstest; Beispielpaket; Referenztranskripte (zwei Fehler gefunden und behoben); Golden-Set-Beispiele; alle Dateien eingebettet.                                                                                      |
| v3.1    | Tests P8 (Library-Paket mit Unterordnern), P9 (Ingest-Durchlauf, Fortsetzen) und P10 (Einbindung); Ingest in Etappen pro Antwort mit Zwischen-ZIP und Ablauf «Fortsetzen»; vorbereitete Variante für grosse Studien (nicht aktiv); Wiki aus demselben Paket mit `wiki.py`; Gate G5; Einbindung des Agenten geprüft: Link als Standard, Web-App-Kanal nur nach Test, Agents SDK für den Harness derzeit nicht verfügbar. |

## B Anhang: Glossar · Begriffe

| Begriff           | Bedeutung                                                                                                    |
|-------------------|--------------------------------------------------------------------------------------------------------------|
| Harness           | Ausführungsumgebung eines Agenten in Copilot Studio; hier der GitHub Copilot Harness mit Sandbox und Skills. |
| Skill             | ZIP mit SKILL.md (Anweisungen) und Begleitdateien, das ein Agent bei Bedarf lädt.                            |
| Teil              | Ausschnitt des Volltexts einer Studie (ganze Seiten) bis zur Teilgrösse.                                     |
| Kontrollwort      | Zufälliges Wort in der Schlusszeile einer Datei; Beweis, dass sie bis zum Ende gelesen wurde.                |
| Wertstatus        | Herkunft einer Grafikzahl: beschriftet, abgelesen ca., berechnet, nicht eindeutig ablesbar.                  |
| Textebene         | Maschinenlesbarer Text einer PDF; Grundlage der wörtlichen Übernahme und der automatischen Prüfung.          |
| Golden Set        | Feste Testfragen mit Sollantworten, die nach jeder Änderung laufen.                                          |
| Gate              | Voraussetzung, ohne die nicht weitergearbeitet wird.                                                         |
| Etappe            | Höchstens fünf Seiten, die der Ingest-Agent am Stück überträgt und danach prüft.                             |
| Kanal             | Ort, an dem Nutzer einen Copilot-Studio-Agenten erreichen (Teams, Microsoft 365 Copilot, Web-App u. a.).     |
| Connection String | Verbindungsangabe für das Microsoft 365 Agents SDK, mit der eine eigene Anwendung einen Agenten aufruft.     |

## C Anhang: Quellen zur Plattform · Stand 14.10.2026

- Microsoft Learn: Harnesses in Copilot Studio – learn.microsoft.com/microsoft-copilot-studio/harnesses-overview
- Microsoft Copilot Blog, 2.9.2026: «What’s new in Copilot Studio, August 2026: GitHub Copilot harness»
- Microsoft Copilot Studio Blog (mcscatblog): «The New Copilot Studio Agent Sandbox»
- tyto.se: «The GitHub Copilot Harness: Tools, Skills, and Sandbox» (Drittquelle)
- Microsoft Q&A, 25.8.2026: Zugriff auf gepackte Skill-Dateien unter dem GitHub Copilot Harness
- Microsoft Learn: Available channels for agents (GitHub Copilot) – learn.microsoft.com/microsoft-copilot-studio/agents-experience/publication-channels-overview
- Microsoft Learn: Integrate with web or native apps by using Microsoft 365 Agents SDK – learn.microsoft.com/microsoft-copilot-studio/publication-integrate-web-or-native-app-m365-agents-sdk
- Microsoft Learn: Quotas and limits – learn.microsoft.com/microsoft-copilot-studio/requirements-quotas
- GitHub microsoft/Agents, Issue \#730: Unterstützung von GHCP-Harness-Agenten in der Copilot-Studio-Clientbibliothek (offen)
- Microsoft Copilot Studio Blog (mcscatblog), 2.3.2026, aktualisiert 2.8.2026: «Every Path to Integrating Your Copilot Studio Agent»

## D Anhang: Öffentliche Teststudien · Nur für Tests

| ID      | Studie                                                                                | Quelle                                                                                                            |
|---------|---------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------|
| LAV-T01 | Gesundheitsmonitor 2024 – Das Wichtigste in Kürze (gfs.bern / Interpharma), 19 Seiten | interpharma.ch/wp-content/uploads/2024/06/LY-IPH.01.24.001-–-Gesundheitsmonitor-2024_d_web.pdf                    |
| LAV-T02 | Gesundheitsmonitor 2025 – Das Wichtigste in Kürze (gfs.bern / Interpharma), 27 Seiten | interpharma.ch/wp-content/uploads/2025/06/LY-IPH.01.25.001-–-Gesundheitsmonitor-2025_d_250605_def.pdf (beigelegt) |
| LAV-T03 | Helsana-Arzneimittelreport 2024, 102 Seiten                                           | helsana.ch/dam/de/pdf/helsana-gruppe/publikationen/arzneimittelreport-2024.pdf                                    |

## E Anhang: Dateien · Eingebettet und im Übergabe-ZIP

Datei

Zweck

Hochladen?

{{DATEIEN}}

Ende des Dokuments · LAV Learning Library Agent · Master-Blaupause v3.1 · Abschnitte 1–16, Anhänge A–E
