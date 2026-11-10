# Anweisungen für GitHub Copilot – LAV-Wiki
<!-- Ablage im Wiki-Repository unter .github/copilot-instructions.md -->

Dieses Repository enthält Code, Layout und Navigation des LAV-Wikis. Die Inhalte kommen fertig aus dem
Ingest-Agenten (`wiki.py`). Im Repository liegen nur Beispieldaten (`beispiel/`, öffentliche Teststudie
LAV-T02). Echte Inhalte gehören in `inhalt/` – dieser Ordner steht in `.gitignore`.

## Immer
- Nur mit den Beispieldaten in `beispiel/` entwickeln und testen.
- Dateien in `beispiel/` und `inhalt/` als unveränderliche Eingabe behandeln: lesen, darstellen,
  verlinken – nie ändern, kürzen, ergänzen oder umformulieren.
- Oberfläche auf Deutsch (Schweiz): kein «ß», Apostroph als Tausendertrennzeichen (1’204).
- Barrierefreiheit: semantisches HTML, Tastaturbedienung, Kontrast nach WCAG AA.
- Alle Ressourcen lokal ausliefern; keine CDNs, Tracker oder externen Schriften.
- Agent-Link und Hinweiszeile kommen aus einer Konfigurationsdatei ohne Geheimnisse.
- Die Hinweiszeile (Klassifizierung, Nutzerkreis) auf jeder Seite sichtbar lassen.

## Nie
- Echte Studieninhalte in den Chat kopieren, zusammenfassen lassen oder ins Repository legen.
- Zugangsdaten, Secrets oder Connection Strings ins Repository schreiben.
- Eine eigene Anmeldung bauen oder das Wiki öffentlich ausliefern – den Zugriffsschutz liefert die
  Plattform (Entra ID).
- Den Agenten per Embed-Code einbinden, solange Plattformtest P10 nicht bestanden ist; bis dahin nur verlinken.
- Kontrollwörter oder Volltext-Teile anzeigen.

## Abnahme
Siehe `wiki-anforderungen.md`, Abschnitt «Abnahme».
