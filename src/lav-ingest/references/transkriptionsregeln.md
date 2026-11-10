# Transkriptionsregeln LAV Learning Library

Ziel: Ein Transkript, aus dem ein Agent jede Frage zur Studie so beantworten kann, als hätte er die PDF
vor sich – mit Seitenbeleg. Wörtlich, vollständig, seitengetreu.

## Grundsätze
- Eine Datei je PDF-Seite: `seiten/s001.md`, `seiten/s002.md` … Erste Zeile ist der Seitenmarker.
- Seitenmarker: `[[Seite n/N]]`. Weicht die gedruckte Seitenzahl ab: `[[Seite n/N · Druckseite x]]`,
  bei Doppelseiten `[[Seite n/N · Druckseiten x–y]]`, bei Umschlag `[[Seite 1/N · Umschlag]]`.
- Text wörtlich aus der Textebene. Silbentrennungen am Zeilenende auflösen, sonst nichts ändern. Zeilen der PDF zu
  Absätzen zusammenfügen (ein Absatz = eine Zeile in der Datei). Der Rohtext in `rohtext/` ist Material, nicht Ergebnis.
- Kolumnentitel und Seitenzahl-Fusszeilen («Das Wichtigste in Kürze … 10») weglassen; die Druckseite steht im Seitenmarker.
- Seiten ohne Textebene: Druckseiten aus den Nachbarseiten fortzählen; letzte Seite ohne Inhalt `Rückseite`.
- Reihenfolge wie ein Mensch die Seite liest (Spalten von links nach rechts, Kästen an ihrer Stelle).
- Schweizer Schreibweise des Originals beibehalten (kein «ß» einfügen, Tausendertrennzeichen wie im Original).

## Regeln je Element
| Element | Vorschrift | Verboten |
|---|---|---|
| Seitenbeginn | Marker wie oben; leere Seiten und Trennfolien: Marker + «[leere Seite]» bzw. ihr Titel | Seiten zusammenziehen, Trennfolien weglassen |
| Titel, Überschriften | Markdown-Überschrift (`##`), wörtlich | Titel erfinden |
| Fliesstext, Bullets | wörtlich; Bullets als `- ` | paraphrasieren, kürzen |
| Fazit- und Kernaussagen-Kästen | `**[Kernaussagen]**` … `**[Ende Kernaussagen]**`, Inhalt wörtlich | Kasten in Fliesstext auflösen |
| Zitate (O-Töne) | «…» mit Quelle bzw. Personenangabe wie im Original | Zitate glätten |
| Tabellen | Markdown-Tabelle, alle Zeilen und Spalten, Einheiten im Kopf; bei unsicherer Spaltenzuordnung zusätzlich Originallayout als Codeblock | Zeilen weglassen, Summen ergänzen |
| Diagramm mit Werten | Grafikblock (unten) mit allen beschrifteten Werten | Platzhalter wie «zeigt hohe Zufriedenheit» |
| Diagramm ohne Werte | Werte am Seitenbild ablesen, jede Zelle «ca. 12»; Genauigkeit im Darstellungstext | Werte ohne «ca.», Werte für nicht dargestellte Punkte |
| Nicht eindeutig | Zelle «nicht eindeutig ablesbar» + Grund im Darstellungstext; Eindeutiges trotzdem übernehmen | plausible Zuordnung raten |
| Karten | Tabelle Region → Klasse bzw. Wert | nur Legende übernehmen |
| Customer Journeys, 2×2-Matrizen, Prozessgrafiken | Tabelle: Phasen bzw. Quadranten als Zeilen mit allen Inhalten (Touchpoints, Pain Points, Zitate, Werte); Pfeile und Beziehungen als Text | nur Phasen- oder Achsentitel |
| Bilder, Icons, Logos | `[Bild: kurze Beschreibung]` nur, wenn sie Information tragen; Text im Bild wörtlich | Text in Bildern weglassen |
| Fussnoten, Quellen, Basis (n) | wörtlich; Fussnoten als `[Fussnote n] …` auf ihrer Seite; Verweise im Text als `[n]` | weglassen |
| Unleserliches, Widersprüche | `[unleserlich]`; `[Hinweis Transkription: …]` z. B. wenn Text und Grafik sich widersprechen | stillschweigend glätten |

## Grafikblock
```
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
- Wertstatus immer im Darstellungstext nennen: «beschriftet», «abgelesen ca.», «berechnet» (nur per Skript
  aus der Vektorgrafik, mit Genauigkeit) oder «nicht eindeutig ablesbar».
- Gestapelte Balken/Säulen: eine Spalte je Segment in Legendenreihenfolge; nicht beschriftete Segmente «–».
  Prüfe, ob die Zeilensummen 100 ergeben; Abweichungen im Original als Hinweis vermerken, nicht korrigieren.
- Legendennamen wörtlich als Spaltenköpfe.

## Muster (Referenztranskript, Gesundheitsmonitor 2025, PDF-Seite 12)
```
**[Grafik 8] Leistungskatalog**

Frage: «Die Grundversicherung deckt alle notwendigen medizinischen Leistungen ab … Sind Sie beim
Leistungskatalog, der durch die Grundversicherung abgedeckt wird, …»

Darstellung: gestapelte Säulen (100 %), 2016–2025, in % Stimmberechtigte; alle Werte beschriftet
(Zeilensummen = 100).

| Jahr | Für einen Ausbau | Für das Belassen auf heutigen Stand | Für einen Abbau | Weiss nicht/keine Antwort |
|---|---|---|---|---|
| 2024 | 33 | 60 | 4 | 3 |
| 2025 | 22 | 49 | 19 | 10 |

Quelle: © gfs.bern, Gesundheitsmonitor 2025 · * Datenerhebung: bis 2024 Face-to-Face, ab 2025 Mixed
Mode: Face-to-Face und Online-Panel (N = jeweils ca. 1’200)

**[Ende Grafik 8]**
```
(Im Muster sind die Jahre 2016–2023 und der volle Fragetext gekürzt; im echten Transkript steht alles.)
