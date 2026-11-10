---
description: Projektstand in docs/stand.md nachführen (am Ende jeder Arbeitssitzung)
agent: agent
---

# Projektstand nachführen

`docs/stand.md` ist das Gedächtnis des Projekts: Wer morgen mit einem anderen Modell weiterarbeitet, liest zuerst
diese Datei.

1. Lies `docs/stand.md`, den Verlauf dieser Sitzung und `git log` seit dem letzten Stand.
2. Passe an:
   - Stand-Datum oben,
   - Tabellen «Agenten im Tenant» und «Versionen im Repository»,
   - «Seit dem letzten im Tenant bestätigten Stand geändert»,
   - «Was funktioniert» (nur im Tenant Bestätigtes),
   - «Offene Schritte»: Erledigtes entfernen, Neues an der richtigen Stelle einreihen,
   - «Bekannte Risiken»,
   - «Verlauf»: höchstens eine Zeile für heute.
3. Prüfe, ob `docs/testprotokoll.md`, `docs/entscheide.md`, `docs/plattform.md` und `docs/bedienkarte.md`
   nachgeführt sind; sonst ergänzen.
4. Keine Inhalte interner Studien. `stand.md` kurz halten (rund 150 Zeilen); Details gehören in die anderen Dateien.
5. Commit `Stand JJJJ-MM-TT nachgeführt`.
6. Dem Menschen in 3–5 Zeilen: was neu ist und was als Nächstes ansteht.
