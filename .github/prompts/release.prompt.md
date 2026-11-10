---
description: Änderung an einer Skill testen, bauen, dokumentieren und für den Tenant ausliefern
agent: agent
---

# Ausliefern

Ziel: Eine Änderung an `src/` geprüft in den Tenant bringen. Schritt für Schritt, nichts überspringen.

1. **Was ist geändert?** `git status` und `git diff`. Nur `src/`, `tools/`, `tests/`, `docs/` dürfen sich ändern.
   Harte Regeln 1 und 2 prüfen (keine internen Inhalte, Repository öffentlich).
2. **Test für das neue Verhalten** vorhanden? Sonst in der passenden Datei unter `tests/` ergänzen: zuerst sehen, dass er
   ohne die Änderung fehlschlägt, dann grün.
3. **Library-SKILL.md geändert?** Kopfzeile `Version x.y · Stand JJJJ-MM-TT` erhöhen.
4. **Bauen und testen:** `python tools/build.py`. Erwartet: «ERGEBNIS: alles in Ordnung». Fehler beheben, nie Tests
   abschwächen, wiederholen. Ohne Python: dem Menschen sagen, dass Build und Tests offen sind; nach dem Push prüft
   GitHub Actions (`python tools/build.py --pruefen`).
5. **Dokumentation nachführen:**
   - `docs/stand.md`: Versionen, Abschnitt «Seit dem letzten im Tenant bestätigten Stand geändert», offene Schritte.
   - `docs/testprotokoll.md`: lokale Tests (Datum, Anzahl Prüfungen, Ergebnis).
   - `docs/bedienkarte.md`, wenn sich Eingaben im Tenant ändern.
   - `docs/entscheide.md`, wenn ein Entscheid gefallen ist.
6. **Commit** auf Deutsch, eine Zeile Zweck, z. B. `Ingest: «Fortsetzen» findet das Zwischen-ZIP selbst`.
   Pushen nur, wenn der Mensch es will und darf.
7. **Anleitung für den Tenant** an den Menschen, kurz und nummeriert:
   - welche Datei in welchem Agenten ersetzen (`dist/lav-ingest.zip` → LAV Ingest; die Library-Skill kommt über
     «Paket bauen»),
   - neues Gespräch beginnen,
   - exakte Eingabe als Code, was anzuhängen ist,
   - was erwartet wird,
   - was er zurückmelden soll (Text oder Screenshot der Antwort).
   Hinweis auf Kontrollwort-Dateien, wenn solche im Spiel sind.
