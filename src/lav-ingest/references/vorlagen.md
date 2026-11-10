# Vorlagen für den Ingest

## Katalog-Eintrag (`katalog-eintrag.md`, höchstens ca. 600 Zeichen)
Die Zeile «Volltext» wird unverändert aus `katalog-zeile.txt` übernommen (erzeugt von `aufteilen.py`).

```
## LAV-[NN] · [Kurztitel] [Jahr]
- Volltitel: [wie auf dem Titelblatt]
- Typ / Umfang: [Foliendeck | Bericht] · [N] PDF-Seiten
- Volltext: [Zeile aus katalog-zeile.txt]
- Herausgeber / Jahr: [Team bzw. Institut] · [Erscheinungsdatum, Feldzeit]
- Methode / Stichprobe: [z. B. Online-Befragung, n = 1’204 Versicherte]
- Themen: [5–8 Schlagworte]
- Auch genannt: [Namen, unter denen die Studie intern bekannt ist]
- Nicht verwechseln mit: [LAV-ID und Unterschied, z. B. Vorgängerstudie 2023] | –
- Original: [SharePoint-Link]
```

## Study Card (`card.md`, höchstens ca. 3’000 Zeichen)
Nur Aussagen aus dem geprüften Volltext, jede mit [S. n] (PDF-Seite). «Schlussfolgerungen der Studie» enthält
nur, was die Studie selbst folgert. Die «Redaktionelle Einordnung LAV» schreibt ein Mensch; der Ingest-Agent
lässt sie leer («–»).

```
## LAV-[NN] · [Kurztitel] [Jahr]
Freigegeben: [Name, Research] · [Datum] · Volltext-Version [x.y]

**Fragestellung:** [Geschäftsfrage, Anlass] [S. n]

**Methode & Stichprobe:** [Methode, n, Zielgruppe, Feldzeit, Gewichtung] [S. n]

**Kernergebnisse:**
- [Befund mit Zahl und Basis; Wertstatus übernehmen, z. B. «ca.» oder «berechnet»] [S. n]
- [… 4–8 Befunde]

**Schlussfolgerungen der Studie:** [nur, was die Studie selbst folgert] [S. n]

**Was die Studie nicht beantwortet:** [fehlende Zielgruppen, Themen, Zeiträume;
Grenzen der Methode] [S. n]

**Wegweiser im Volltext:**
| Thema | Seiten | Teil |
|---|---|---|
| [z. B. Wechselmotive nach Alter] | [18–21] | [teil-02] |

**Redaktionelle Einordnung LAV** (optional; keine Studienaussage, nie mit Seitenbeleg
zitieren): [Einordnung, Autorin/Autor, Datum] | –

— Ende Card LAV-[NN] —
```

## Teil-Kopf und Schlusszeile
Erzeugt `aufteilen.py`; nie von Hand schreiben oder ändern.
