# Vorbereitete Variante für grosse Studien (Library-Agent)

Nur einsetzen, wenn der Spike zeigt, dass der Library-Agent bei einer Frage zu einer grossen Studie
nicht alle Teile in einer Antwort lesen kann (Abbruch, Zeitüberschreitung, fehlende Kontrollwörter).
Die Variante schwächt Anforderung 2 des Killerkriteriums («vollständig gelesen») für grosse Studien ab
und braucht deshalb die Zustimmung der Projektleitung (Entscheidung E14).

Einsetzen in `SKILL.md` des Library-Agenten:
1. In «Fall A», Schritt 2, am Anfang ergänzen: «Hat die Studie laut Katalog mehr als K Teile, gilt Fall A2.»
   K ist die grösste Teilzahl, die im Spike zuverlässig in einer Antwort gelesen wurde.
2. Nach «Fall A» diesen Abschnitt einfügen:

```
### Fall A2 – Frage zu einer grossen Studie (mehr als K Teile)
1. Lies die Card der Studie vollständig.
2. Suche mit grep in allen Teilen der Studie nach den Begriffen der Frage, nach Synonymen und nach
   genannten Zahlen. Lies vollständig bis zur Kontrollwort-Zeile: teil-01, alle Teile mit Treffern
   und alle Teile, auf die der Wegweiser der Card für das Thema zeigt.
   Steht grep nicht zur Verfügung, lies teil-01 und die Teile aus dem Wegweiser.
3. Antworte nur aus den gelesenen Teilen. Die Abschlusszeile nennt die gelesenen Teile,
   z. B. «LAV-03 Teile 1, 7, 8 von 22».
4. Biete an, die übrigen Teile zu lesen. Auf Wunsch liest du sie Teil für Teil über mehrere Antworten
   und ergänzt die Antwort.
```

Erst prüfen, ob eine grössere TEILGROESSE (Plattformtest P2) das Problem löst: Bei 45’000 Bytes hat
ein Bericht mit 100 Seiten rund 7 statt rund 20 Teile.
