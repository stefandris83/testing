> **Historisches Dokument.** Anleitung «Copilot Studio einrichten» vom 14.10.2026 (Begleitdokument zur Blaupause v3.1),
> nach Markdown umgewandelt. Die Klickwege in Copilot Studio (Agent anlegen, Skill hochladen, Einstellungen) sind weiterhin
> nützlich. **Überholt** sind Dateinamen und Ordner des Übergabe-ZIP, Teilgrösse und Etappen, Paketbau von Hand und die
> Paketprüfung im Ingest-Agenten. Die aktuellen Eingaben stehen in `docs/bedienkarte.md`.

LAV Learning Library · Umsetzung

# Copilot Studio einrichten – Schritt für Schritt

Arbeitsanleitung für den Helsana-PC · Begleitdokument zur Master-Blaupause v3.1 · Stand 14.10.2026

So benutzt du diese Anleitung

- Text in den beigen Kästen mit dem Titel **Eingeben** kopierst du unverändert nach Copilot Studio. Zeilenumbrüche, die beim Kopieren entstehen, spielen keine Rolle.
- Fett geschriebene Wörter wie **Build** oder **Upload a skill** sind Tabs und Knöpfe in Copilot Studio (englische Oberfläche).
- Alle Dateien liegen im entpackten Übergabe-ZIP. Der Ordner steht jeweils dabei, z. B. `03_Plattformtest/`.
- Die Phasen A bis C verwenden nur öffentliche Testdaten. Echte Studien kommen erst ab Phase D dazu, nach der Freigabe durch InfoSec.

Vier Regeln, die immer gelten

1.  **Lösungsblätter nie hochladen:** `Plattformtest_Loesungen.txt` und alle Dateien mit «kontrollwoerter» im Namen gehören in keinen Agenten. Sie sind nur für dich zum Vergleichen.
2.  **Memory aus, Knowledge leer** – bei jedem Agenten. Sonst mischt der Agent Gemerktes oder fremde Quellen in die Antworten.
3.  **Jeder Test in einem neuen Chat** (**New chat**), damit nichts aus dem vorherigen Test mitläuft.
4.  **Nach jeder Änderung neu veröffentlichen** (**Publish**). Erst dann sehen die Nutzer die neue Fassung.

### Kurz erklärt

|              |                                                                                                                                                                                                                               |
|--------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Agent        | Ein Assistent in Copilot Studio. Du baust drei: **LAV Plattformtest** (nur zum Testen, danach löschen), **LAV Ingest** (nimmt Studien auf, nur Pflegeteam) und **LAV Learning Library** (beantwortet Fragen, für die Nutzer). |
| Skill        | Eine ZIP-Datei mit der Arbeitsanleitung für den Agenten und den Dateien, die er dazu braucht. Du lädst sie im Agenten unter **Skills** hoch.                                                              |
| Kontrollwort | Ein Wort ganz am Ende einer Datei. Nennt der Agent es richtig, hat er die Datei bis zum Schluss gelesen.                                                                                                                      |
| Teilgrösse   | Wie gross die Textstücke sind, in die eine Studie zerlegt wird. Startwert 18’000 Bytes. Phase A zeigt, ob mehr geht.                                                                                                          |
| Etappe       | Fünf PDF-Seiten. Der Ingest-Agent überträgt eine Studie Etappe für Etappe und wartet dazwischen auf «weiter».                                                                                                                 |
| Preview      | Der Testchat in Copilot Studio. Dort probierst du alles aus, bevor du veröffentlichst.                                                                                                                                        |

### Überblick

| Phase | Was                             | Ergebnis                                                                                  | Daten              |
|-------|---------------------------------|-------------------------------------------------------------------------------------------|--------------------|
| 0     | Vorbereitung                    | Zugang, Credits und Freigaben sind geklärt oder angestossen.                              | –                  |
| A     | Plattformtest                   | Du weisst, was Copilot Studio kann: Teilgrösse, Datei-Upload, Download.                   | öffentlich         |
| B     | Ingest-Agent einrichten         | Der Agent nimmt eine Test-Studie korrekt auf.                                             | öffentlich         |
| C     | Library-Agent einrichten        | Der Agent beantwortet Testfragen aus dem Beispielpaket richtig.                           | öffentlich         |
| D     | Echte Studie aufnehmen          | Pro Studie ein geprüftes Ingest-ZIP im Quellordner.                                       | intern, nach G1    |
| E     | Paket bauen und veröffentlichen | Der Library-Agent kennt alle aufgenommenen Studien und ist für die Nutzer freigeschaltet. | intern, nach G1/G2 |

## 0 Vorbereitung · Einmalig

Ziel: Du darfst Agenten bauen, und die Freigaben laufen.

0.1

Mit der Power-Platform-Administration klären

- In welcher Umgebung darfst du Agenten erstellen?
- Woher kommen die Copilot Credits, und wie viele stehen zur Verfügung?
- Welche Lizenz brauchen die späteren Nutzer des Library-Agenten?

0.2

Freigaben anstossen

InfoSec-Freigabe für interne Studien (Gate G1) und Festlegung, wer den Library-Agenten nutzen darf (Gate G2). Das läuft parallel zu den Phasen A bis C.

0.3

Quellordner anlegen

SharePoint-Ordner **LAV Library – Quelle**. Zugriff nur für das Pflegeteam. Hier landen später alle Original-PDFs, Ingest-ZIPs und Pakete.

## A Plattformtest · Ca. 1 Tag · öffentliche Daten

Ziel: Herausfinden, ob Copilot Studio grosse Dateien vollständig liest, Python ausführt, PDFs annimmt und Dateien zum Herunterladen ausgibt.

A1

Testagent anlegen

Auf der Startseite von Copilot Studio einen neuen Agenten erstellen. **Nicht** über **Other ways to build** gehen – das wäre die alte Agentenart ohne Skills.

Name

``` copy
LAV Plattformtest
```

A2

Einstellen und Skill hochladen

1.  Tab **Build**: Schalter **Memory** aus. Unter **Knowledge** nichts hinzufügen.
2.  **Skills** → **Add skill** → **Upload a skill** → Datei `03_Plattformtest/lav-plattformtest.zip` hineinziehen.

A3

Lesetests (6 kurze Chats)

Tab **Preview** → **New chat** →

Eingeben

``` copy
Lesetest a
```

Der Agent nennt vier Kontrollwörter. Vergleiche sie mit `03_Plattformtest/Plattformtest_Loesungen.txt`, Abschnitt `lesetest-a.md`. Dann **New chat** und denselben Test ein zweites Mal. Danach genauso mit:

Eingeben

``` copy
Lesetest b
```

Eingeben

``` copy
Lesetest c
```

**Ergebnis:** Die grösste Stufe, bei der beide Male alle vier Wörter stimmen, ist deine Teilgrösse: a = 18’000 · b = 30’000 · c = 45’000.

**Stimmt schon «Lesetest a» nicht:** Hier stoppen. Das ist ein grundsätzliches Problem der Plattform; zuerst klären, bevor du weitermachst.

A4

Selbsttest und Download-Test (im selben Chat)

**New chat** →

Eingeben

``` copy
Selbsttest
```

**Bestanden, wenn** der Agent meldet, dass Python läuft und pdfplumber, pypdf und pypdfium2 vorhanden sind. Notiere, ob er «direkt» oder über den «Ersatzweg» gearbeitet hat.

Danach **im selben Chat** (der Download-Test braucht die Dateien aus dem Selbsttest):

Eingeben

``` copy
Download-Test
```

**Bestanden, wenn** du drei Dateien herunterladen kannst, die Umlaute in der .md- und der .csv-Datei richtig aussehen und sich das ZIP öffnen lässt.

A5

PDF-Test

**New chat** → die Datei `03_Plattformtest/gesundheitsmonitor-2025.pdf` an die Nachricht anhängen →

Eingeben

``` copy
PDF-Test Seite 10; lies im oberen Diagramm für jede Linie die Werte 2005, 2010, 2015 und 2020 ab.
```

**Bestanden, wenn** der Agent 27 Seiten erkennt, Seite 26 als Seite ohne Text meldet und die abgelesenen Werte höchstens 3 Prozentpunkte von den Referenzwerten in `Plattformtest_Loesungen.txt` abweichen, ohne vertauschte Linien.

**Lässt sich keine Datei anhängen:** Notieren. Der Ausweichweg steht in der Blaupause (Test P4).

A6

Kosten notieren

Tab **Monitor** → verbrauchte Copilot Credits ablesen und notieren.

Wenn der Agent «Lesetest» nicht kennt

Dann hat er den Skill nicht geladen. Im Tab **Build** den Skill mit dem **X** daneben löschen, stattdessen `03_Plattformtest/lav-plattformtest-ordner.zip` hochladen und A3 wiederholen. Klappt es damit, gilt ab jetzt überall die **Ordner-Variante** (siehe Anhang 1, Schritt 5).

Tipp: Schaltest du im Tab **Preview** den Schalter **End user preview** aus, siehst du, welche Dateien der Agent tatsächlich geöffnet hat.

## B Ingest-Agent einrichten · Nur Pflegeteam · öffentliche Daten

Ziel: Ein Agent, der eine Studie Seite für Seite in Textdateien überträgt – getestet mit der öffentlichen Test-Studie.

B1

Richtige Skill-Datei wählen

- **Teilgrösse aus A3 ist 18’000:** Nichts ändern. Du nimmst `01_Ingest-Skill/lav-ingest.zip` (bei Ordner-Variante `lav-ingest-ordner.zip`).
- **Teilgrösse ist 30’000 oder 45’000:** Zuerst die Zahl im Skill ändern – Anhang 1. Oder du schickst mir den Wert, und ich baue dir die fertige ZIP-Datei.

B2

Agent anlegen

Neuer Agent auf der Startseite (nicht **Other ways to build**). Im Tab **Build** eintragen:

Name

``` copy
LAV Ingest
```

Beschreibung (fragt Copilot Studio spätestens beim Veröffentlichen)

``` copy
Nimmt LAV-Studien auf und prüft Library-Pakete. Nur für das Pflegeteam.
```

Instructions (Abschnitt Instructions, danach Save)

``` copy
Du bist der LAV Ingest-Agent. Du transkribierst LAV-Studien und prüfst Skill-Pakete nach dem Skill lav-ingest. Du arbeitest in Dateien, nie in Chat-Antworten zum Kopieren. Du kürzt und paraphrasierst nie. Was du nicht sicher lesen kannst, kennzeichnest du.
```

Dann: **Memory** aus · **Knowledge** leer · Websuche aus, falls angeboten · **Skills** → **Add skill** → **Upload a skill** → Skill-Datei aus B1.

B3

Probelauf, Teil 1

**Preview** → **New chat** → `gesundheitsmonitor-2025.pdf` anhängen →

Eingeben

``` copy
Studie aufnehmen: LAV-T02, Gesundheitsmonitor 2025, 2025
```

Der Agent meldet Seitenzahl und Besonderheiten, überträgt die Seiten 1–5 und wartet. Dann:

Eingeben

``` copy
weiter, 2 Etappen ohne Pause
```

Er überträgt die Seiten 6–15. Dann:

Eingeben

``` copy
Gib mir jetzt den Zwischenstand als ZIP zum Herunterladen.
```

Das Zwischen-ZIP herunterladen.

B4

Probelauf, Teil 2: Fortsetzen

**New chat** → die PDF **und** das Zwischen-ZIP anhängen →

Eingeben

``` copy
Fortsetzen: LAV-T02
```

**Bestanden, wenn** er bei Seite 16 weitermacht.

Eingeben

``` copy
weiter, 4 Etappen ohne Pause
```

Danach jeweils `weiter`, bis er fertig meldet. Zum Schluss `LAV-T02_ingest.zip` herunterladen.

B5

Ergebnis prüfen

- Im heruntergeladenen ZIP die Dateien `seiten/s001.md` bis `s005.md` mit denselben Dateien in `04_Referenz-und-Tests/referenz-transkripte.zip` (Ordner `LAV-T02/seiten/`) vergleichen. Unterschiede sind nur bei Werten mit «ca.» erlaubt.
- Ist eine Antwort abgebrochen (hört mittendrin auf oder zeigt einen Fehler)? Wenn nicht: Die Einstellung «Etappen pro Antwort» darfst du auf 2 bzw. 4 erhöhen (Anhang 1). Das spart später «weiter»-Klicks. Wenn ja: so lassen, wie es ist.

B6

Veröffentlichen, nur fürs Pflegeteam

Wie Schritt E6, aber bei **Share** nur die Personen des Pflegeteams eintragen.

## C Library-Agent einrichten · Öffentliche Daten

Ziel: Der Agent, den die Nutzer später fragen – zuerst getestet mit einem fertigen Beispielpaket.

C1

Agent anlegen

Name

``` copy
LAV Learning Library
```

Beschreibung

``` copy
Beantwortet Fragen zu LAV-Studien ausschliesslich aus den aufbereiteten Studien, mit Seitenangaben.
```

Instructions

``` copy
Du bist der LAV Learning Library Agent der Helsana. Beantworte fachliche Fragen zu Studien, Research-Ergebnissen und Kundenwissen ausschliesslich mit dem Skill lav-learning-library und halte dich an dessen Ablauf, Zitier- und Zahlenregeln. Verwende kein allgemeines Weltwissen. Was die Studien nicht belegen, benennst du als nicht belegt.
```

**Memory** aus · **Knowledge** leer · Websuche aus, falls angeboten.

C2

Beispielpaket als Skill hochladen

**Skills** → **Add skill** → **Upload a skill** → `02_Library-Skill/beispielpaket_LAV-T02.zip`

C3

Drei Testfragen, jede in einem neuen Chat

Eingeben (Frage G01)

``` copy
Wie viele Prozent der Stimmberechtigten wollen laut Gesundheitsmonitor 2025 den Leistungskatalog der Grundversicherung abbauen?
```

**Richtig:** 19 %, mit Seite 12. Falsch wäre 22 % – das ist der Wert für «Ausbau».

Eingeben (Frage G08)

``` copy
Wie lange warten Patientinnen und Patienten laut den Studien im Durchschnitt auf einen Facharzttermin?
```

**Richtig:** «nicht belegt», ohne eine Zahl zu Facharztterminen. Erwähnen darf er die 189 Tage bis zur Aufnahme eines Medikaments in die Spezialitätenliste (Seite 4).

Eingeben (Frage G11)

``` copy
Lies den Volltext von LAV-T02 vollständig. Wie lautet das Kontrollwort von Teil 3?
```

**Richtig:** genau das Wort, das in `02_Library-Skill/beispielpaket_kontrollwoerter.csv` bei `teil-03.md` steht.

Abschluss der Testphase

Stimmen A bis C, ist die Plattform tauglich. Den Agenten «LAV Plattformtest» löschen. Die Ergebnisse festhalten – sie sind die Entscheide für den Betrieb:

|                                                |     |
|------------------------------------------------|-----|
| Teilgrösse (A3)                                |     |
| Skill-Variante: oberste Ebene oder Ordner (A2) |     |
| Python: direkt oder Ersatzweg (A4)             |     |
| PDF-Upload und Download funktionieren (A4, A5) |     |
| Etappen pro Antwort (B5)                       |     |
| Verbrauchte Credits (A6)                       |     |

## D Echte Studie aufnehmen · Pro Studie · erst nach G1

Ziel: Eine Studie vollständig und geprüft als Textdateien im Quellordner.

D1

Aufnahme starten

Ingest-Agent → **New chat** → Original-PDF anhängen → eingeben (Nummer, Kurztitel und Jahr anpassen):

Eingeben

``` copy
Studie aufnehmen: LAV-07, Kurztitel der Studie, 2025
```

Die Nummer vergibst du fortlaufend (LAV-01, LAV-02 …). Sie bleibt für immer bei dieser Studie.

D2

Durcharbeiten lassen

Nach jeder Meldung `weiter` eingeben, bis der Agent fertig meldet. Bietet er ein Zwischen-ZIP an (bei Studien ab 40 Seiten), immer herunterladen.

**Bricht eine Antwort ab:** **New chat**, PDF und das letzte Zwischen-ZIP anhängen und `Fortsetzen: LAV-07` eingeben.

D3

Ablegen

`LAV-07_ingest.zip` herunterladen und zusammen mit der Original-PDF im Quellordner in einen Ordner `LAV-07` legen.

D4

Menschliche Prüfung

- Die Datei `grafiken-abgelesen.txt` öffnen: Jede dort genannte Grafik am Original-PDF ansehen und die Werte mit «ca.» prüfen.
- Research liest `card.md` (die Zusammenfassung der Studie) und gibt sie frei. Erst danach kommt die Studie ins Paket.

## E Paket bauen und veröffentlichen · Nach D · erst nach G1/G2

Ziel: Der Library-Agent kennt alle aufgenommenen Studien und ist für die Nutzer freigeschaltet. Das Beispielpaket `beispielpaket_LAV-T02.zip` zeigt, wie das Ergebnis aussieht.

E1

Paket-Ordner zusammenstellen (beim ersten Mal)

1.  Einen neuen Ordner `lav-learning-library` anlegen.
2.  `02_Library-Skill/lav-learning-library_SKILL.md` hineinkopieren und in `SKILL.md` umbenennen.
3.  Darin einen Unterordner `references` anlegen. Dort hinein: `00-katalog_vorlage.md` → umbenennen in `00-katalog.md`; `01-study-cards_vorlage.md` → umbenennen in `01-study-cards.md`.
4.  `00-katalog.md` im Editor öffnen:
    - Alles von der Zeile `## LAV-[NN] · …` bis und mit der Zeile `[… ein Eintrag pro Studie …]` löschen und dort den Inhalt von `katalog-eintrag.md` aus dem Ingest-ZIP einfügen.
    - Die Zeile `Stand: …` ausfüllen (Datum, Anzahl Studien, Version).
    - In der letzten Zeile `[zufällig, von paket.py erzeugt]` durch `NEU-01` ersetzen.
5.  `01-study-cards.md` genauso: Platzhalter-Card durch den Inhalt von `card.md` ersetzen, `Stand: …` ausfüllen, in der letzten Zeile `Datei [1 von k]` durch `Datei 1 von 1` und `[zufällig, von paket.py erzeugt]` durch `NEU-02` ersetzen.
6.  In `references` den Ordner `volltext` anlegen, darin `LAV-07`. Dort hinein alle Dateien `teil-01.md`, `teil-02.md` … aus dem Ordner `volltext` des Ingest-ZIPs.

So sieht es danach aus:

``` tree
lav-learning-library/
  SKILL.md
  references/
    00-katalog.md
    01-study-cards.md
    volltext/
      LAV-07/
        teil-01.md
        teil-02.md
        …
```

Speichern im Editor immer als UTF-8 (Standard im Windows-Editor). Die Wörter NEU-01 und NEU-02 sind Platzhalter; die Prüfung in E3 ersetzt sie durch zufällige Kontrollwörter.

E2

Zippen

Den Ordner `lav-learning-library` öffnen, **den Inhalt** markieren (`SKILL.md` und `references`) → Rechtsklick → **Senden an → ZIP-komprimierter Ordner** (Windows 11: **In ZIP-Datei komprimieren**). Die ZIP-Datei `lav-learning-library.zip` nennen. Bei Ordner-Variante stattdessen den Ordner selbst zippen.

E3

Paket prüfen lassen

Ingest-Agent → **New chat** → `lav-learning-library.zip` anhängen →

Eingeben

``` copy
Paket prüfen
```

**Nur bei «Keine Befunde»** weiter: `lav-learning-library_geprueft.zip` und `kontrollwoerter_alle.csv` herunterladen und im Quellordner ablegen. Die CSV nie hochladen.

**Bei Befunden:** Der Agent sagt, welche Datei was hat. Korrigieren, neu zippen (E2), nochmals prüfen.

E4

Paket in den Library-Agenten laden

Library-Agent → Tab **Build** → **Skills** → beim vorhandenen Skill die drei Punkte **…** → **Replace** → `lav-learning-library_geprueft.zip`.

E5

Testfragen (Golden Set)

Jede Testfrage in einem neuen Chat stellen und die Antwort mit Sollantwort und Seitenangabe vergleichen. Die Fragen stehen in der Golden-Set-Liste im Quellordner (Vorlage: `04_Referenz-und-Tests/golden-set-beispiel.csv`).

Der Tab **Evaluate** hilft hier nicht: Er bewertet nur die allgemeine Qualität und vergleicht nicht mit der Sollantwort.

E6

Veröffentlichen und teilen

1.  Den kleinen Pfeil neben **Publish** anklicken. Im Fenster **Publish agent** den Kanal **Teams + Microsoft 365** wählen und **Make agent available in Microsoft Copilot** einschalten → **Publish**.
2.  Das Symbol **Share** neben **Publish** anklicken → nur die Personen oder Sicherheitsgruppen aus G2 eintragen → **Share**. Nie «ganze Organisation».
3.  Die Anmeldung muss auf **Authenticate with Microsoft** stehen. Ist das nicht so, meldet Copilot Studio es beim Teilen.

Bei jeder weiteren Studie

D1–D4 für die neue Studie. Dann in deinem Ordner `lav-learning-library`: den neuen Katalog-Eintrag und die neue Card jeweils **vor** der letzten Zeile einfügen, `Stand` anpassen, den Volltext-Ordner `references/volltext/LAV-NN` ergänzen. Danach E2 bis E5 und zum Schluss **Publish**.

### Optional: Wiki

Ingest-Agent → **New chat** → `lav-learning-library_geprueft.zip` anhängen → eingeben (Link und Hinweis anpassen). Ergebnis: `lav-wiki_<Datum>.zip` mit den Wiki-Seiten. Den Library-Agenten im Wiki nur verlinken.

Eingeben

``` copy
Wiki aufbereiten. Agent-Link: https://… (Link zum Library-Agenten in Teams). Hinweis: Intern – nur für Mitarbeitende LAV.
```

## 1 Anhang: Eine Einstellung im Skill ändern · Nur wenn nötig

Nötig, wenn A3 eine grössere Teilgrösse ergibt oder B5 mehr Etappen pro Antwort erlaubt. Alternativ baue ich dir die Datei.

1

Entpacken

`01_Ingest-Skill/lav-ingest.zip` → Rechtsklick → **Alle extrahieren**.

2

Datei öffnen

Im entpackten Ordner `SKILL.md` mit dem Editor (Notepad) öffnen.

3

Zahl ersetzen

Mit Ctrl+F die Zeile suchen und nur die Zahl ändern:

| Zeile steht so da         | Ändern zu                                                      |
|---------------------------|----------------------------------------------------------------|
| `TEILGROESSE = 18000`     | `TEILGROESSE = 30000` oder `TEILGROESSE = 45000` (Ergebnis A3) |
| `ETAPPEN_PRO_ANTWORT = 1` | `ETAPPEN_PRO_ANTWORT = 2` oder `4` (Ergebnis B5)               |

4

Speichern

Ctrl+S. Der Windows-Editor speichert richtig (UTF-8). Nur falls du «Speichern unter» benutzt: Codierung **UTF-8** wählen, nicht «UTF-8 mit BOM» – sonst ignoriert Copilot Studio den Skill.

5

Wieder zippen

Im entpackten Ordner **alles markieren** (Ctrl+A: `SKILL.md`, `references`, `scripts`) → Rechtsklick → **Senden an → ZIP-komprimierter Ordner** (Windows 11: **In ZIP-Datei komprimieren**). Nicht den Ordner selbst zippen – ausser A2 hat die Ordner-Variante ergeben.

6

Ersetzen und veröffentlichen

Ingest-Agent → **Build** → **Skills** → **…** beim Skill → **Replace** → neue ZIP-Datei. Danach **Publish**.

## 2 Anhang: Was tun, wenn … · Hilfe

| Problem                                                                  | Lösung                                                                                                                                                                                                                                   |
|--------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Der Agent kennt «Lesetest», «Studie aufnehmen» oder «Paket prüfen» nicht | Der Skill ist nicht geladen. Im Tab **Build** prüfen, ob er unter **Skills** steht. Neuen Chat starten. Sonst die Ordner-Variante probieren (Kasten am Ende von A).                              |
| Eine Antwort bricht mittendrin ab                                        | Neuer Chat, PDF und letztes Zwischen-ZIP anhängen, `Fortsetzen: LAV-NN`. Etappen pro Antwort nicht erhöhen.                                                                                                                              |
| Kontrollwort falsch (A3 oder Frage G11)                                  | Der Agent hat nicht bis zum Schluss gelesen. Kleinere Teilgrösse verwenden (Anhang 1) und das Paket neu bauen.                                                                                                                           |
| «Paket prüfen» meldet Befunde                                            | Häufigste Ursachen: eine Datei liegt im Paket, die nicht hineingehört (z. B. eine CSV), der Volltext-Ordner heisst anders als die Nummer im Katalog, ein Platzhalter wurde nicht ersetzt (E1). Korrigieren, neu zippen, nochmals prüfen. |
| Eine Änderung wirkt nicht                                                | Nach **Replace** neu veröffentlichen (**Publish**) und im Test einen neuen Chat starten.                                                                                                         |
| PDF lässt sich nicht anhängen                                            | Notieren und melden. Ausweichweg steht in der Blaupause (Test P4).                                                                                                                                                                       |
| Antwort enthält eine Zahl ohne Seitenangabe                              | Nicht verwenden. Frage notieren und ins Golden Set aufnehmen; Ursache mit dem Pflegeteam klären.                                                                                                                                         |

## 3 Anhang: Quellen · Microsoft Learn · Stand 14.10.2026

- Skill hochladen: learn.microsoft.com/microsoft-copilot-studio/agents-experience/skills-add-existing
- Skill ersetzen und löschen: learn.microsoft.com/microsoft-copilot-studio/agents-experience/skills-manage
- Aufbau eines Agenten (Tabs Build, Preview, Evaluate, Monitor): learn.microsoft.com/microsoft-copilot-studio/agents-experience/overview
- Testen im Preview: learn.microsoft.com/microsoft-copilot-studio/agents-experience/authoring-test-bot
- Memory: learn.microsoft.com/microsoft-copilot-studio/agents-experience/memory-overview
- Evaluate: learn.microsoft.com/microsoft-copilot-studio/agents-experience/analytics-agent-evaluation-intro
- Veröffentlichen: learn.microsoft.com/microsoft-copilot-studio/agents-experience/publication-publish-agent
- Teilen: learn.microsoft.com/microsoft-copilot-studio/agents-experience/authoring-share-agent

Ende der Anleitung · LAV Learning Library · Begleitdokument zur Master-Blaupause v3.1
