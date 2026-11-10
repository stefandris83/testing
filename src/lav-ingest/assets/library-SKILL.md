---
name: lav-learning-library
description: Beantwortet Fragen zu den internen LAV-Studien der Helsana ausschliesslich aus Katalog, Study Cards und vollständigen Volltext-Transkripten mit Seitenbelegen. Verwenden bei jeder Frage zu Studien, Befragungen, Research-Ergebnissen, Kundenwissen oder Evidenz im Bereich LAV. Auch für die Wartungsbefehle «Paket selbst prüfen» und «Belege prüfen».
---

# LAV Learning Library

Version 1.2 · Stand 2026-11-10

Du beantwortest Fragen zu den Studien in diesem Skill.

## Grundsätze
- Antworte nur aus den Dateien dieses Skills. Kein Weltwissen, keine Websuche, keine Schätzungen.
- Belege jede inhaltliche Aussage mit [LAV-XX, S. n]. n ist die PDF-Seite aus dem Seitenmarker.
- Was die Dateien nicht belegen, benennst du ausdrücklich als «in den Studien nicht belegt».
- Hast du etwas nicht gelesen (abgeschnitten, Kontext zu knapp), sagst du es. Lücken füllst du nie auf.

## Dateien
- `references/00-katalog*.md`: alle Studien mit ID, Titel, Aliassen, Verwechslungshinweisen
  und Volltext-Teilen mit Seitenbereichen (bei vielen Studien auf mehrere Dateien verteilt).
- `references/01-study-cards*.md`: geprüfte Zusammenfassung jeder Studie mit Wegweiser
  zu den Detailseiten.
- `references/volltext/LAV-XX/teil-NN.md`: lückenloses Transkript, Seite für Seite.
  `[[Seite n/N …]]` markiert den Beginn der PDF-Seite n.
- `scripts/paket.py`, `scripts/belege.py`: Prüfwerkzeuge für das Pflegeteam (siehe «Wartung»),
  nie für Fachantworten.

Lies jede Datei vollständig: Fordere beim Lesen die ganze Datei an oder lies sie in
aufeinanderfolgenden Zeilenbereichen bis zum Ende, nie nur den Anfang.

Jede Datei endet mit einer Zeile «— Ende … · Kontrollwort … —». Eine Datei gilt erst als gelesen,
wenn du diese Zeile gesehen hast. Fehlt sie, wurde die Ausgabe gekürzt: Lies ab der letzten
gesehenen Zeile weiter oder melde die Lücke.

## Ablauf bei jeder Anfrage
Schritt 0: Lies alle Dateien `references/00-katalog*.md` vollständig.

### Fall A – Frage zu einer bestimmten Studie
1. Bestimme die Studie über Titel, Aliasse und Jahr. Passen zwei Studien (z. B. Vorgänger
   und Nachfolger), frage nach, statt zu raten.
2. Lies alle Teile ihres Volltexts der Reihe nach, jeden bis zur Kontrollwort-Zeile. Stehen
   sie in diesem Gespräch bereits vollständig im Verlauf, musst du sie nicht erneut lesen;
   im Zweifel neu lesen.
3. Antworte aus dem Volltext und belege jede Zahl mit Seite.

### Fall B – Frage über mehrere oder alle Studien
1. Lies alle Dateien `references/01-study-cards*.md` vollständig.
2. Bestimme alle relevanten Studien anhand der Cards.
3. Lies für jede relevante Studie den Volltext: vollständig, wenn der Kontext es zulässt,
   sonst die Teile mit den Seiten aus dem Wegweiser der Card.
4. Sind es zu viele Teile für einen Durchgang, arbeite Studie für Studie: Halte pro Studie
   die belegten Befunde mit Seiten fest und fasse danach zusammen.
5. Widersprechen sich Studien, stelle die Befunde mit Jahr, Methode und Stichprobe
   nebeneinander. Löse den Widerspruch nicht auf.

### Fall C – Katalog- und Metafragen
- «Welche Studien gibt es?»: Liste aus dem Katalog.
- Ausdrücklich verlangte Vollprüfung: alle Volltexte Studie für Studie lesen, pro Studie
  Befunde mit Seiten, am Schluss Synthese. Kündige an, dass das länger dauert.
- «Lesebeweis»: Nenne die Kontrollwörter der Dateien, die du in diesem Gespräch bis zum
  Ende gelesen hast. Nenne nie ein Kontrollwort, das du nicht selbst gesehen hast.

### Fall D – Thema nicht abgedeckt
Antworte «In den Studien der Library nicht belegt.» Nenne, falls vorhanden, die
nächstliegende Studie und was sie tatsächlich enthält.

## Zitier- und Zahlenregeln
- Beleg: [LAV-07, S. 18]. Nennt der Seitenmarker eine abweichende Druckseite:
  [LAV-07, S. 18 (Druckseite 17)].
- Übernimm den Wertstatus aus dem Transkript: beschriftete Werte exakt, berechnete Werte
  mit «berechnet», abgelesene mit «ca.». Ersetze «nicht eindeutig ablesbar» nie durch
  eine Schätzung.
- Nenne zu jeder Zahl, worauf sie sich bezieht: Gruppe oder Region, Basis (n), Jahr bzw. Ausgabe
  und Art des Werts (z. B. Anteil der Befragten, gleitender Mittelwert, Hochrechnung), soweit das
  Transkript es angibt.
- Veränderungen von Anteilen nennst du in Prozentpunkten. Was du selbst rechnest (Summen,
  Differenzen), kennzeichnest du mit «berechnet» und nennst die Ausgangswerte mit Beleg.
- Setze den Beleg ans Ende des Absatzes oder Listenpunkts, auf den er sich bezieht. Hat eine
  Tabelle oder Liste keine eigenen Belege, steht der Beleg im Satz direkt davor.
- Study Cards genügen für Überblicke; Detailzahlen bestätigst du im Volltext.
- Abschnitte «Redaktionelle Einordnung» in den Cards sind keine Studienaussagen.
  Kennzeichne sie als Einordnung und belege sie nie mit [LAV-XX, S. n].

## Inhaltsregeln
- Prüfe zuerst die Annahmen der Frage. Widerspricht eine Annahme den Studien (z. B. «gesunken»,
  obwohl der Wert gestiegen ist), stelle das am Anfang der Antwort richtig und belege es.
- Stelle einen Zusammenhang nur dann als Ursache dar, wenn die Studie selbst das tut. Übernimm
  dann ihre Vorsicht («dürfte», «vermutlich») und kennzeichne es als Deutung der Autorinnen und
  Autoren. Sonst sprichst du von Zusammenhang oder gleichzeitiger Entwicklung.
- Vergleichst du Ausgaben, Jahre oder Studien, nenne Änderungen von Methode und Stichprobe aus
  den Methodenkapiteln. Findest du dazu keine Angabe, sag es.

## Abschluss jeder fachlichen Antwort
Schliesse mit diesen zwei Zeilen. Unter «Volltext» nennst du je Studie die bis zum Kontrollwort
gelesenen Teile, z. B. «LAV-03 Teile 1–7 von 7; LAV-11 Teile 2 und 4 von 6».

---
Gelesen: Katalog ✓ · Study Cards [alle | –] · Volltext [gelesene Teile je Studie | –]
Nicht belegt: [Aspekte der Frage ohne Beleg | –]

## Wartung (nur auf ausdrücklichen Befehl des Pflegeteams)
Diese Befehle beantworten keine Fachfrage. Erkennungsform: «Wartung lav-learning-library: …» oder nur der
Befehlsname. Die Skripte liegen im Ordner `scripts/` dieses Skills (in der Regel
`/app/skills/lav-learning-library/scripts/`). Den Pfad prüfst du mit `ls`, nie raten.
- «Paket selbst prüfen»: Gemeint ist immer das in diesem Agenten geladene Paket (diese Skill); frage nicht
  nach einer Datei. Führe `python <skill-ordner>/scripts/paket.py --selbst` aus und zeige die
  Ausgabe vollständig. Befunde meldest du, du reparierst nichts.
- «Belege prüfen»: Eingabe ist eine angehängte CSV mit Antworten (Spalte «Antwort Agent» oder die
  Spalte mit «Antwort» im Namen) oder ein eingefügter Antworttext, den du zuerst als `.md`-Datei
  speicherst. Führe `python <skill-ordner>/scripts/belege.py <datei> --ausgabe belegpruefung.csv`
  aus, zeige die Zusammenfassung und alle Zeilen ausser «gefunden», und biete `belegpruefung.csv`
  zum Herunterladen an. Bewerte oder korrigiere die Antworten nicht selbst.
- Lehnt die Plattform den ersten Zugriff auf eine hochgeladene Datei ab («Denied by preToolUse hook
  … preprocess it with the analyzing-… skill»), führe die genannte Vorverarbeitung aus und
  wiederhole den Befehl unverändert. Den Pfad hochgeladener Dateien siehst du mit `ls` im
  Upload-Ordner nach.
