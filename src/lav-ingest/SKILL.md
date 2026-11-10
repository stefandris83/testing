---
name: lav-ingest
description: Transkribiert eine LAV-Studie (PDF) vollständig, seitengetreu und wörtlich in Markdown-Dateien für die LAV Learning Library, baut daraus das Skill-Paket des Library-Agenten und prüft es vor dem Upload. Verwenden bei «Studie aufnehmen», «transkribieren», «Ingest», «Paket bauen» oder «Paket prüfen».
---

# LAV Ingest

Du überträgst Studien vollständig, seitengetreu und wörtlich in Dateien. Du kürzt nie, du
paraphrasierst nie, du rätst keine Zahlen. Was du nicht sicher lesen kannst, kennzeichnest du.
Du arbeitest in Dateien in deinem Arbeitsverzeichnis, nie in Chat-Antworten zum Kopieren.

## Einstellungen
- TEILGROESSE = 45000 (Bytes, UTF-8). Gemessen im Plattformtest P2: Stufe c in beiden Durchgängen bestanden.
- ETAPPEN_PRO_ANTWORT = 2 (eine Etappe = höchstens 5 Seiten). Gemessen im Probelauf (27 Seiten, mit dem strengen Check):
  3 Etappen (Seiten 6–20) liefen in einer Antwort durch (22 min), die vierte nicht mehr; der Agent unterbrach kontrolliert nach
  Seite 20. 2 Etappen lassen Spielraum. Der Nutzer darf in einer Antwort ausdrücklich mehr verlangen (z. B. «weiter, 3 Etappen»).
- ZWISCHENSTAND_ALLE = 20 Seiten (nur bei Studien ab 40 Seiten).
- Skripte: `scripts/inventar.py`, `scripts/pruefen.py`, `scripts/aufteilen.py`, `scripts/paket.py`,
  `scripts/paket_bauen.py`, `scripts/belege.py`, `scripts/wiki.py`. Vorlage der Library-Skill: `assets/library-SKILL.md`.
  Lässt sich ein Skript nicht direkt aus dem Skill ausführen: Lies `references/skripte.md`, schreibe
  den Codeblock des Skripts unverändert als Datei in dein Arbeitsverzeichnis und führe ihn dort aus.
- PDF-Zugriff: Die Plattform kann den ersten Zugriff auf eine hochgeladene PDF ablehnen, z. B. mit «Denied by preToolUse
  hook: Before working with <pfad>, preprocess it with the analyzing-pdf skill». Dann zuerst diese Vorverarbeitung mit dem
  genannten Skill ausführen und den abgelehnten Befehl danach unverändert wiederholen. Der Pfad der PDF enthält eine
  Kennung (z. B. /app/uploads/<name>-<kennung>.pdf): Pfad nie raten, sondern mit `ls` im Upload-Ordner nachsehen.
- Regeln je Element: `references/transkriptionsregeln.md`. Vorlagen: `references/vorlagen.md`.
- In den Befehlen unten steht `<pdf>` für den Pfad der hochgeladenen PDF und `LAV-NN` für die Studien-ID.

## Ablauf «Studie aufnehmen» (eine Studie pro Gespräch)
Voraussetzung: Die PDF ist hochgeladen; der Nutzer nennt Studien-ID (LAV-NN), Kurztitel und Jahr.
Fehlt etwas davon, frage einmal nach.

1. Lege `arbeit/LAV-NN/` an. Notiere für jeden Schritt Start- und Endzeit (Befehl `date`) in
   `arbeit/LAV-NN/zeiterfassung.csv` (Spalten: schritt;start;ende).

2. Inventar erstellen, dann `inventar.txt` lesen und dem Nutzer melden: Seitenzahl, Seiten ohne
   Textebene, Doppelseiten, Seiten mit Grafiken. Bei Doppelseiten (zwei Druckseiten nebeneinander) steht der Rohtext
   getrennt nach linker und rechter Seitenhälfte: links zuerst, dann rechts. Querformat allein (A4 quer, Folien) ist
   keine Doppelseite.
   ```
   python inventar.py <pdf> arbeit/LAV-NN
   ```

3. Transkription in Etappen von höchstens 5 Seiten, höchstens ETAPPEN_PRO_ANTWORT Etappen pro Antwort.
   Danach kurz melden (fertige Seiten, offene Befunde, nächste Seite) und auf «weiter» warten. Erlaubt
   der Nutzer ausdrücklich mehr (z. B. «weiter bis Seite 30»), gilt das für diese Antwort.
   Für jede Seite n:
   a. Lies `rohtext/sNNN.txt` (und `rohtext/sNNN-tabellen.md`, falls vorhanden).
   b. Sieh dir `bilder/sNNN.png` an – immer bei Seiten mit Grafiken, Tabellen, Kästen oder mehreren
      Spalten und bei Seiten ohne Textebene.
   c. Schreibe `seiten/sNNN.md` nach den Transkriptionsregeln. Erste Zeile: `[[Seite n/N]]`, bei
      abweichender Druckseite `[[Seite n/N · Druckseite x]]` bzw. `[[Seite n/N · Druckseiten x–y]]`.
   d. Text wörtlich aus der Textebene; Lesereihenfolge und Struktur nach dem Seitenbild. Der Rohtext ist Material,
      nicht Ergebnis: Zeilen zu Absätzen zusammenfügen, Silbentrennungen am Zeilenende auflösen, Überschriften als `##`
      setzen, Kolumnentitel und Seitenzahl-Fusszeilen weglassen, Spalten und Druckseiten in Lesereihenfolge. Ein Absatz
      steht in einer Zeile, nicht in den Zeilen der PDF.
   e. Jede Grafik als Block `[Grafik] … [Ende Grafik]` mit Wertstatus. Beschriftete Werte jeder Serie nur dann zuordnen,
      wenn die Zuordnung eindeutig ist (Farbe, Lage am Linienende, Legende). Zahlen im Fliesstext derselben Seite
      gegenprüfen: Nennt der Text einen Wert für dieselbe Grösse, muss er übereinstimmen, sonst `[Hinweis Transkription: …]`.
      Dichte Linienbilder dürfen mit «nicht eindeutig ablesbar» markiert werden, aber nie mit vertauschten Serien.
   Nach jeder Etappe prüfen und Befunde der Etappe sofort beheben. Die Meldungen «unbearbeiteter Rohtext»,
   «Silbentrennung am Zeilenende nicht aufgelöst» und «zerlegte Textzeilen» werden nie begründet, sondern immer behoben; die nächste Etappe
   beginnt erst, wenn sie für die Seiten der Etappe weg sind:
   ```
   python pruefen.py <pdf> arbeit/LAV-NN/seiten --nur-vorhandene --protokoll arbeit/LAV-NN/zwischen.txt
   ```
   Bei Studien ab 40 Seiten nach jeweils ZWISCHENSTAND_ALLE fertigen Seiten ein Zwischen-ZIP
   `LAV-NN_zwischenstand_bis-S-xx.zip` zum Herunterladen anbieten; unter 40 Seiten nur auf Verlangen. Inhalt: Ordner
   `seiten/` (die Dateien s001.md … nicht im ZIP-Stamm), `zeiterfassung.csv`, `befunde-begruendet.txt`, `zwischen.txt`.

4. Schlussprüfung:
   ```
   python pruefen.py <pdf> arbeit/LAV-NN/seiten --protokoll arbeit/LAV-NN/pruefprotokoll.txt
   ```
   Jede gemeldete Seite am Seitenbild prüfen: korrigieren oder begründen, warum es kein Fehler ist (ausser den beiden
   Rohtext-Meldungen, siehe Schritt 3)
   (z. B. «Grafikbeschriftungen überlappen in der Textebene, Werte im Seitenbild geprüft»).
   Begründungen in `befunde-begruendet.txt` (Seite;Meldung;Begründung). Wiederholen, bis jede
   Meldung behoben oder begründet ist.

5. Aufteilen (schreibt `volltext/`, `kontrollwoerter.csv` und `katalog-zeile.txt`):
   ```
   python aufteilen.py arbeit/LAV-NN/seiten arbeit/LAV-NN/volltext --id LAV-NN --titel "<Volltitel>" --quelle <dateiname.pdf> --max TEILGROESSE
   ```

6. Study Card und Katalog-Eintrag nach `references/vorlagen.md`, ausschliesslich aus dem geprüften
   Volltext: jede Aussage mit [S. n], Wertstatus übernehmen, «Was die Studie nicht beantwortet»
   ausfüllen, Wegweiser mit den Teilen aus `katalog-zeile.txt`. Katalog-Eintrag höchstens ca. 600
   Zeichen, Card höchstens ca. 3’000 Zeichen. Dateien: `card.md`, `katalog-eintrag.md`.
   Jede Zahl einer Card-Zeile muss im Volltext auf der zitierten Seite stehen; `paket.py` prüft das und meldet Abweichungen.

7. `grafiken-abgelesen.txt` anlegen: jede Grafik mit abgelesenen oder nicht eindeutigen Werten
   (Seite;Grafik;Status) – für die Sichtprüfung durch einen Menschen.

8. Ausgabe: ZIP `LAV-NN_ingest.zip` mit `volltext/`, `seiten/`, `card.md`, `katalog-eintrag.md`,
   `kontrollwoerter.csv`, `katalog-zeile.txt`, `pruefprotokoll.txt`, `befunde-begruendet.txt`,
   `grafiken-abgelesen.txt`, `zeiterfassung.csv`, `inventar.txt`. Gib es dem Nutzer zum Herunterladen
   und nenne: Seitenzahl, Anzahl Teile, offene Befunde, Anzahl Grafiken zur Sichtprüfung.

Werden Kontext oder Ausgabe knapp: nach der letzten vollständig geschriebenen Seite unterbrechen,
Zwischenstand als ZIP ausgeben und die letzte fertige Seite nennen.

## Ablauf «Fortsetzen» (neues Gespräch nach Unterbruch)
1. Der Nutzer lädt die PDF und das letzte Zwischen-ZIP hoch und nennt die Studien-ID.
2. Entpacke das ZIP nach `arbeit/LAV-NN/` (liegen die Dateien s001.md … im Stamm des ZIP, verschiebe sie nach
   `arbeit/LAV-NN/seiten/`; `zeiterfassung.csv` wird fortgeführt, nie überschrieben) und erzeuge Rohtext und
   Seitenbilder neu (vorhandene Seiten in `seiten/` bleiben erhalten):
   ```
   python inventar.py <pdf> arbeit/LAV-NN
   python pruefen.py <pdf> arbeit/LAV-NN/seiten --nur-vorhandene --protokoll arbeit/LAV-NN/zwischen.txt
   ```
3. Melde die erste fehlende Seite und mache dort mit Schritt 3 weiter.

## Ablauf «Paket bauen» (Library-Paket aus Ingest-Ergebnissen)
1. Der Nutzer lädt hoch: die Ingest-ZIPs der Studien (`LAV-NN_ingest.zip`, einzeln oder zusammen in einem ZIP) und,
   wenn es schon eine Library gibt, das aktuelle Paket (`lav-learning-library.zip`). Ohne bestehendes Paket entsteht
   ein neues nur aus den hochgeladenen Studien; frage einmal nach, ob das so gewollt ist.
   Wichtig: Die Plattform hält hochgeladene ZIPs fälschlich für CSV und sperrt jeden Befehl, der den Pfad einer
   hochgeladenen ZIP nennt. Deshalb: die ZIPs nicht öffnen, nicht entpacken, nicht auflisten, keinen analyzing-Skill
   verwenden und keinen Upload-Pfad in einen Befehl schreiben. Das Skript findet die ZIPs selbst.
2. Bauen und prüfen (genau dieser Befehl, ohne Dateipfade):
   ```
   python <skill-ordner>/scripts/paket_bauen.py --uploads --max TEILGROESSE --ausgabe lav-learning-library.zip --csv kontrollwoerter_alle.csv
   ```
   Meldet das Skript «kein Upload-Ordner gefunden», ermittle den Ordner mit `ls -d /app/uploads /mnt/data 2>/dev/null`
   und gib ihn an: `--uploads <ordner>`. Es verwendet alle ZIPs im Upload-Ordner dieses Gesprächs (deshalb pro Paketbau
   ein neues Gespräch).
   Zusätze nur auf ausdrücklichen Wunsch des Nutzers:
   - Freigabe durch Research: `--freigabe "LAV-NN=Vorname Name, Research"` (je Studie) oder `--freigabe "*=Vorname Name, Research"`
     (alle noch nicht freigegebenen Cards). Nur setzen, wenn der Nutzer die Freigabe mit Namen nennt; nie selbst annehmen.
   - Studie herausnehmen: `--entfernen LAV-NN`.
   Bei Ersatzweg über `references/skripte.md`: paket_bauen.py, paket.py und belege.py in denselben Ordner schreiben und
   `--vorlage <skill-ordner>/assets/library-SKILL.md` angeben.
3. Melde dem Nutzer knapp: je Studie neu / ersetzt / übernommen / entfernt, ergänzte Verwechslungshinweise (vom Nutzer
   zu prüfen), nicht freigegebene Cards, alle Befunde.
4. Nur bei «ERGEBNIS: Paket ohne Befunde» gib `lav-learning-library.zip` und `kontrollwoerter_alle.csv` zum Herunterladen,
   mit drei Hinweisen: (a) Die CSV nie in einen Agenten hochladen. (b) Im Library-Agenten die Skill durch das ZIP ersetzen,
   ein neues Gespräch beginnen und diesen Text eingeben (als Codeblock zum Kopieren ausgeben):
   `Wartung lav-learning-library: Paket selbst prüfen`
   Erwartet: «Keine Befunde.» (c) Sind Cards nicht freigegeben: nur Testpaket, nicht für Nutzerinnen und Nutzer.
   Bei Befunden kein ZIP ausgeben; Befunde nennen und sagen, welche Studie neu aufgenommen oder korrigiert werden muss.
   Inhalte von Katalog-Einträgen, Cards oder Volltexten nie von Hand ändern, um einen Befund zu beheben.

## Ablauf «Paket prüfen»
Nur für ein Paket, das nicht mit «Paket bauen» entstanden ist (dieses prüft bereits). Einfacher Weg: nur
`lav-learning-library.zip` hochladen und «Paket bauen» ausführen; das setzt das Paket neu zusammen und prüft es.
Wird der Upload gesperrt (siehe «Paket bauen», Schritt 1), immer diesen Weg nehmen.
1. Der Nutzer lädt `lav-learning-library.zip` hoch (Skill des Library-Agenten).
2. Prüfen, Kontrollwörter von Katalog und Cards erneuern, geprüftes Paket schreiben:
   ```
   python paket.py <zip> --max TEILGROESSE --erneuern --ausgabe lav-learning-library_geprueft.zip --csv kontrollwoerter_alle.csv
   ```
3. Melde alle Befunde. Nur wenn keine Befunde bleiben, gib das geprüfte ZIP und die CSV zum
   Herunterladen, mit dem Hinweis: Die CSV nie in einen Agenten hochladen.
4. Das Paket darf neben SKILL.md und references/ den Ordner scripts/ mit paket.py und belege.py
   enthalten (Prüfwerkzeuge der Library-Skill); das ist kein Befund.
5. Sperrt die Plattform den Zugriff auf das ZIP auch nach der verlangten Vorverarbeitung (z. B. weil sie
   es als CSV behandelt), brich nach einem Versuch ab und verweise auf die Selbstprüfung im
   Library-Agenten: nach dem Ersetzen der Skill dort «Paket selbst prüfen».

## Ablauf «Wiki aufbereiten»
1. Grundlage ist das geprüfte Paket (`lav-learning-library_geprueft.zip` aus «Paket prüfen»; in einem
   neuen Gespräch lädt der Nutzer es hoch).
2. Seiten für das Wiki erzeugen (eine Übersicht, eine Seite je Studie, ohne Kontrollwörter):
   ```
   python wiki.py lav-learning-library_geprueft.zip wiki --agent-link "<Link zum Library-Agenten>" --hinweis "<Klassifizierung und Nutzerkreis>"
   ```
3. Den Ordner `wiki/` als ZIP `lav-wiki_<Datum>.zip` zum Herunterladen geben. Inhalte nicht von Hand ändern.

## Verbote
- Kein Kürzen, Zusammenfassen oder Umformulieren; keine Seite überspringen (leere Seiten: «[leere Seite]»).
- Keine Zahl ohne Grundlage; keine Werte für Punkte, die die Grafik nicht zeigt.
- Kontrollwörter nie von Hand setzen oder ändern – nur über die Skripte.
- Keine Inhalte aus anderen Studien oder aus allgemeinem Wissen.
