# Skripte als Text (Ersatzweg)
Falls die Dateien unter `scripts/` nicht direkt ausführbar sind: Schreibe den Codeblock des benötigten Skripts unverändert als Datei mit dem genannten Namen in dein Arbeitsverzeichnis und führe sie mit Python aus. Nichts am Code ändern.

## inventar.py

```python
"""LAV Ingest – Inventar einer Studien-PDF (Schritt 2).

Aufruf:
  python inventar.py <studie.pdf> <arbeitsordner> [--bilder alle|grafik|keine] [--aufloesung 120]

Erzeugt im Arbeitsordner:
  inventar.txt / inventar.json   Seitentabelle: Zeichen, Wörter, Zahlen, Grafik-Elemente, Textebene, Typ-Vorschlag
  rohtext/s001.txt …             Textebene je PDF-Seite (Grundlage der wörtlichen Transkription);
                                 bei Doppelseiten (Breite ≈ 2 × Breite der Hochformat-Seiten desselben Dokuments, gleiche Höhe) getrennt
                                 nach linker und rechter Seitenhälfte. Querformat allein (A4 quer, 16:9-Folien) gilt nicht als Doppelseite.
  rohtext/s001-tabellen.md …     erkannte Tabellen als Markdown (nur wo vorhanden; am Seitenbild prüfen)
  bilder/s001.png …              Seitenbilder (Standard: alle Seiten; «grafik» = nur Seiten mit Grafiken/Bildern)
  seiten/                        leerer Ordner für die Transkription (eine Datei je Seite: s001.md …)

Benötigt: pdfplumber (enthält pypdfium2 für Seitenbilder). Keine Netzwerkzugriffe.
"""
import argparse
import json
import pathlib
import re
import sys

import pdfplumber

NUM = re.compile(r"\d+(?:[’'`]\d{3})*(?:[.,]\d+)?")


def page_type(chars, curves, rects, lines, images):
    graphic = curves + rects + lines
    if chars < 20 and images > 0:
        return "ohne Textebene (Bild/Scan)"
    if chars < 20 and graphic < 5:
        return "leer"
    if graphic >= 20 or images > 0:
        return "Grafik/Bild" if chars < 1500 else "Text + Grafik/Bild"
    return "Text"


def single_size(pdf):
    """Häufigste Hochformat-Grösse des Dokuments (Einzelseite) oder None."""
    from collections import Counter
    c = Counter((round(p.width), round(p.height)) for p in pdf.pages if p.width < p.height)
    return c.most_common(1)[0][0] if c else None


def is_double(p, single):
    """Doppelseite = Breite ≈ 2 × Einzelseitenbreite bei gleicher Höhe (Toleranz 4 %)."""
    if not single:
        return False
    w1, h1 = single
    return abs(p.width - 2 * w1) <= 0.04 * w1 and abs(p.height - h1) <= 0.04 * h1


def page_text(q, p, single):
    """Textebene der Seite. Doppelseiten: linke und rechte Hälfte getrennt, sonst mischt die Textebene die Zeilen
    beider Druckseiten (Lesereihenfolge zerstört). Gibt (text_fuer_rohtext, text_gesamt) zurück."""
    full = q.extract_text(x_tolerance=1.5) or ""
    if not is_double(p, single):
        return full, full
    half = p.width / 2
    left = q.crop((0, 0, half, p.height)).extract_text(x_tolerance=1.5) or ""
    right = q.crop((half, 0, p.width, p.height)).extract_text(x_tolerance=1.5) or ""
    return (f"--- linke Seitenhälfte (linke Druckseite) ---\n{left}\n\n--- rechte Seitenhälfte (rechte Druckseite) ---\n{right}",
            full)


def md_table(rows):
    rows = [[(c or "").replace("\n", " ").strip() for c in r] for r in rows if any((c or "").strip() for c in r)]
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    out = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * width]
    out += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("arbeitsordner")
    ap.add_argument("--bilder", choices=["grafik", "alle", "keine"], default="alle")
    ap.add_argument("--aufloesung", type=int, default=120)
    a = ap.parse_args()

    root = pathlib.Path(a.arbeitsordner)
    for sub in ("rohtext", "bilder", "seiten"):
        (root / sub).mkdir(parents=True, exist_ok=True)

    rows = []
    with pdfplumber.open(a.pdf) as pdf:
        n = len(pdf.pages)
        single = single_size(pdf)
        for i, p in enumerate(pdf.pages, 1):
            try:
                q = p.dedupe_chars()  # doppelt gezeichnete Zeichen entfernen
            except Exception:  # noqa: BLE001
                q = p
            raw, txt = page_text(q, p, single)
            words = q.extract_words(x_tolerance=1.5)
            info = {
                "seite": i,
                "breite": round(p.width), "hoehe": round(p.height),
                "quer": p.width > p.height,
                "doppelseite": is_double(p, single),
                "zeichen": len(txt.strip()),
                "woerter": len(words),
                "zahlen": len(NUM.findall(txt)),
                "kurven": len(p.curves), "rechtecke": len(p.rects), "linien": len(p.lines), "bilder": len(p.images),
            }
            info["textebene"] = info["zeichen"] >= 20
            info["typ"] = page_type(info["zeichen"], info["kurven"], info["rechtecke"], info["linien"], info["bilder"])
            (root / "rohtext" / f"s{i:03d}.txt").write_text(raw + "\n", encoding="utf-8")
            try:
                tables = [t for t in p.find_tables() if (t.bbox[2] - t.bbox[0]) > 150 and (t.bbox[3] - t.bbox[1]) > 30]
            except Exception:  # noqa: BLE001 – Tabellenerkennung ist nur Hilfe
                tables = []
            info["tabellen"] = len(tables)
            if tables:
                parts = [f"Tabelle {k} (Bereich {', '.join(str(round(v)) for v in t.bbox)}):\n\n{md_table(t.extract())}"
                         for k, t in enumerate(tables, 1)]
                (root / "rohtext" / f"s{i:03d}-tabellen.md").write_text("\n\n".join(parts) + "\n", encoding="utf-8")
            want = a.bilder == "alle" or (a.bilder == "grafik" and info["typ"] != "Text")
            if want:
                p.to_image(resolution=a.aufloesung).save(root / "bilder" / f"s{i:03d}.png")
                info["seitenbild"] = f"bilder/s{i:03d}.png"
            rows.append(info)

    (root / "inventar.json").write_text(json.dumps({"pdf": str(a.pdf), "seiten": n, "inventar": rows},
                                                   ensure_ascii=False, indent=1), encoding="utf-8")
    head = f"Inventar {a.pdf} · {n} PDF-Seiten\n"
    head += "Seite | Format | Zeichen | Wörter | Zahlen | Kurven | Rechtecke | Linien | Bilder | Tabellen | Typ-Vorschlag\n"
    lines = [f"{r['seite']:>4} | {'Doppelseite' if r['doppelseite'] else ('quer' if r['quer'] else 'hoch')} | {r['zeichen']:>6} | {r['woerter']:>5} | {r['zahlen']:>4} | "
             f"{r['kurven']:>5} | {r['rechtecke']:>5} | {r['linien']:>5} | {r['bilder']:>3} | {r['tabellen']:>2} | {r['typ']}"
             for r in rows]
    ohne = [r["seite"] for r in rows if not r["textebene"]]
    tail = f"\nSeiten ohne Textebene: {ohne or 'keine'}"
    dbl = [r["seite"] for r in rows if r["doppelseite"]]
    if dbl:
        tail += (f"\nDoppelseiten (zwei Druckseiten nebeneinander): {dbl}. Rohtext ist je Seitenhälfte getrennt "
                 "(links, dann rechts lesen); Druckseiten im Seitenmarker angeben, z. B. [[Seite 3/27 · Druckseiten 2–3]].")
    elif any(r["quer"] for r in rows):
        tail += ("\nHinweis: Querformat-Seiten sind Einzelseiten (nicht doppelt so breit wie die Hochformat-Seiten)."
                 if single else "\nHinweis: Nur Querformat-Seiten, kein Hochformat zum Vergleich: Doppelseiten sind nicht "
                 "ableitbar; am Seitenbild prüfen, ob zwei Druckseiten nebeneinander stehen.")

    report = head + "\n".join(lines) + tail + "\n"
    (root / "inventar.txt").write_text(report, encoding="utf-8")
    print(report)
    print(f"Rohtext: {root / 'rohtext'} · Seitenbilder: {root / 'bilder'} · Transkription in: {root / 'seiten'}")


if __name__ == "__main__":
    sys.exit(main())
```

## pruefen.py

```python
"""LAV Ingest – Prüfung eines Transkripts gegen die Textebene der PDF (Schritt 6).

Aufruf:
  python pruefen.py <studie.pdf> <seitenordner | volltext.md> [--schwelle 0.95] [--protokoll pruefprotokoll.txt]
                    [--nur-vorhandene]

Eingabe: Ordner mit einer Datei je PDF-Seite (s001.md, s002.md …), jede beginnt mit [[Seite n/N …]];
         oder eine Markdown-Datei bzw. ein Volltext-Teil mit solchen Seitenmarkern.
Prüft je Seite:
  1. Datei/Seite vorhanden, Seitenmarker korrekt (n und N), Inhalt vorhanden oder «[leere Seite]»
  2. Zahlen-Check: jede Zahl der Textebene steht im Transkript derselben Seite (normalisiert)
  3. Wortabdeckung: Anteil der Wörter der Textebene, die im Transkript derselben Seite vorkommen
  4. Grafikblöcke [Grafik …] … [Ende Grafik …] tragen einen Wertstatus
  5. Seite ist nicht bloss der ungeordnete Rohtext der Textebene: zu viele Zeilen identisch mit der Textebene
     oder Silbentrennung am Zeilenende nicht aufgelöst (Spalten ordnen, Absätze zusammenfügen)
  6. Keine zerlegten Textzeilen (einzelne Buchstaben, z. B. «h g e u i t t s o w de e r»), wie sie überlagerte
     oder gedrehte Beschriftungen in der Textebene erzeugen
Kopf- und Fusszeilenbereich (oberste/unterste 4.5 % der Seite) wird ignoriert.
Ausgabe: Protokoll (Text) und <protokoll>.json. Exit-Code 0 = keine Befunde, 1 = Befunde, 2 = Fehler.
"""
import argparse
import json
from collections import Counter
import pathlib
import re
import sys

import pdfplumber

NUM = re.compile(r"\d+(?:[’'`]\d{3})*(?:[.,]\d+)?")
WORD = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]{3,}")
MARKER = re.compile(r"^\[\[Seite (\d+)/(\d+)(?:\s*·[^\]]*)?\]\]\s*$")
STATUS = re.compile(r"beschriftet|abgelesen|berechnet|nicht eindeutig", re.I)
ZONE = 0.045


def norm_num(t):
    t = t.replace("’", "").replace("'", "").replace("`", "")
    return t.replace(",", ".")


def num_variants(t):
    """Akzeptierte Schreibweisen einer PDF-Zahl im Transkript."""
    n = norm_num(t)
    v = {n}
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", n):  # 1.209 als Tausendertrennung
        v.add(n.replace(".", ""))
    if re.fullmatch(r"\d{2}", n):  # zweistellige Jahreszahl auf Achsen: 97 → 1997, 03 → 2003
        v |= {"19" + n, "20" + n}
    if re.fullmatch(r"\d+\.0", n):
        v.add(n[:-2])
    return v


def glued(x, t_nums):
    """«8811» = zwei überlappende Beschriftungen 88 und 11; nicht für Jahreszahlen."""
    n = norm_num(x)
    if not re.fullmatch(r"\d{3,6}", n) or re.fullmatch(r"(19|20)\d{2}", n):
        return False
    return any(n[:k] in t_nums and n[k:] in t_nums for k in range(1, len(n)))


def load_pages(src):
    """Gibt {n: (markerzeile, text, N)} zurück."""
    p = pathlib.Path(src)
    pages = {}
    if p.is_dir():
        for f in sorted(p.glob("s[0-9][0-9][0-9].md")):
            n = int(f.stem[1:])
            txt = f.read_text(encoding="utf-8")
            first = next((l for l in txt.splitlines() if l.strip()), "")
            m = MARKER.match(first.strip())
            pages[n] = (first.strip(), txt, int(m.group(2)) if m else None, f.name)
    else:
        txt = p.read_text(encoding="utf-8")
        cur, buf, first = None, [], ""
        for line in txt.splitlines():
            m = MARKER.match(line.strip())
            if m:
                if cur is not None:
                    pages[cur[0]] = (first, "\n".join(buf), cur[1], p.name)
                cur, buf, first = (int(m.group(1)), int(m.group(2))), [line], line.strip()
            elif cur is not None:
                buf.append(line)
        if cur is not None:
            pages[cur[0]] = (first, "\n".join(buf), cur[1], p.name)
    return pages


def pdf_words(page):
    """Wörter der Textebene ohne Kopf-/Fusszeilenbereich; Silbentrennung und Tausendergruppen zusammengeführt."""
    h = page.height
    try:
        page = page.dedupe_chars()  # doppelt gezeichnete Zeichen (Fettdruck-Effekt) entfernen
    except Exception:  # noqa: BLE001
        pass
    ws = [dict(w) for w in page.extract_words(x_tolerance=1.5)
          if ZONE * h < (w["top"] + w["bottom"]) / 2 < (1 - ZONE) * h]
    out = []
    for w in ws:
        w["text"] = w["text"].replace("\u00ad", "")
        prev = out[-1] if out else None
        same_line = prev is not None and abs(prev["top"] - w["top"]) < 1.5
        wrapped = prev is not None and w["top"] > prev["top"] + 1 and w["x0"] < prev["x0"]
        if prev and prev["text"].endswith("-") and w["text"][:1].islower() and wrapped:
            prev["text"] = prev["text"][:-1] + w["text"]
            prev["x1"] = w["x1"]
        elif (prev and same_line and w["x0"] - prev["x1"] < 5 and (
                (re.fullmatch(r"\d{1,3}", prev["text"]) and re.fullmatch(r"[’']?\d{3}[.,;:%)]?", w["text"]))
                or (re.fullmatch(r"\d{1,3}[’']", prev["text"]) and re.fullmatch(r"\d{3}[.,;:%)]?", w["text"])))):
            # Tausendergruppen, die die Textebene trennt: «200 000», «1 ’200», «1’ 000»
            prev["text"] += w["text"]
            prev["x1"] = w["x1"]
        else:
            out.append(w)
    return out


def axis_ticks(words):
    """Achsenbeschriftungen: ≥ 3 reine Zahlen, bündig untereinander oder auf einer Linie, gleiche Abstände und Wertschritte."""
    nums = []
    for i, w in enumerate(words):
        if NUM.fullmatch(w["text"]):
            v = float(norm_num(w["text"]))
            nums.append((i, v, w))
    ticks = set()

    def check(group, pos_key):
        """Markiert alle Läufe von ≥ 3 Zahlen mit gleichem Wertschritt und gleichem Abstand."""
        group = sorted(group, key=lambda g: pos_key(g[2]))
        if len(group) < 3:
            return
        two = all(re.fullmatch(r"\d{2}", g[2]["text"]) for g in group)
        vals = [g[1] + ((1900 if g[1] >= 50 else 2000) if two else 0) for g in group]
        pos = [pos_key(g[2]) for g in group]
        start = 0
        while start < len(group) - 2:
            end = start + 1
            dv, dp = vals[end] - vals[start], pos[end] - pos[start]
            while (end + 1 < len(group) and dv != 0 and dp > 0
                   and abs((vals[end + 1] - vals[end]) - dv) < 1e-6
                   and abs((pos[end + 1] - pos[end]) - dp) <= 0.2 * dp):
                end += 1
            if end - start >= 2 and dv != 0 and dp > 0:
                ticks.update(g[0] for g in group[start:end + 1])
                start = end + 1
            else:
                start += 1

    def clusters(items, key, tol):
        items = sorted(items, key=key)
        out, cur = [], []
        for it in items:
            if cur and key(it) - key(cur[-1]) > tol:
                out.append(cur)
                cur = []
            cur.append(it)
        if cur:
            out.append(cur)
        return out

    # senkrechte Achsen: rechts- oder linksbündig untereinander
    for k in ("x1", "x0"):
        for g in clusters(nums, lambda it: it[2][k], 2.0):
            check(g, lambda w: (w["top"] + w["bottom"]) / 2)
    # waagrechte Achsen: gleiche Zeile
    for g in clusters(nums, lambda it: it[2]["top"], 1.5):
        check(g, lambda w: (w["x0"] + w["x1"]) / 2)
    return ticks


def single_size(pdf):
    """Häufigste Hochformat-Grösse des Dokuments (Einzelseite) oder None."""
    c = Counter((round(p.width), round(p.height)) for p in pdf.pages if p.width < p.height)
    return c.most_common(1)[0][0] if c else None


def is_double(p, single):
    """Doppelseite = Breite ≈ 2 × Einzelseitenbreite bei gleicher Höhe (Toleranz 4 %)."""
    if not single:
        return False
    return abs(p.width - 2 * single[0]) <= 0.04 * single[0] and abs(p.height - single[1]) <= 0.04 * single[1]


def roh_zeilen(page, single):
    """Zeilen der Textebene: ganze Seite und, bei Doppelseiten, je Seitenhälfte (so liefert sie inventar.py)."""
    try:
        q = page.dedupe_chars()
    except Exception:  # noqa: BLE001
        q = page
    parts = [q.extract_text(x_tolerance=1.5) or ""]
    if is_double(page, single):
        h = page.width / 2
        parts += [q.crop((0, 0, h, page.height)).extract_text(x_tolerance=1.5) or "",
                  q.crop((h, 0, page.width, page.height)).extract_text(x_tolerance=1.5) or ""]
    return {l.strip().replace("\u00ad", "") for t in parts for l in t.splitlines() if l.strip()}


def ohne_grafik(text):
    """Text ohne Grafikblöcke, Tabellenzeilen, Marker und Überschriften-/Hilfszeilen."""
    out, inside = [], False
    for l in text.splitlines():
        if re.match(r"^\s*\**\[Grafik(?:\s[^\]]*)?\]", l):
            inside = True
        if not inside:
            out.append(l.strip())
        if re.match(r"^\s*\**\[Ende Grafik", l):
            inside = False
    return out


def zerlegt(line, min_tokens=6, anteil=0.35):
    """Zeile besteht zu einem grossen Teil aus einzelnen Buchstaben (überlagerte/gedrehte Beschriftungen).
    «n», «a» und grosse Einzelbuchstaben (Legendenmarker, Optionen A/B) zählen nicht."""
    toks = line.split()
    if len(toks) < min_tokens:
        return False
    single = [t for t in toks if len(t) == 1 and t.isalpha() and t not in "naAaBCDEIOu"]
    return len(single) / len(toks) >= anteil


def rohtext_befunde(text, raw):
    """Erkennt eine Seite, die nur der ungeordnete Rohtext ist (Zeilen der Textebene, Silbentrennung am Zeilenende)."""
    lines = ohne_grafik(text)
    cand = [l for l in lines if len(l) >= 25 and not l.startswith(("|", "[[", "---", "**[", "#", "- ", "[Bild", "[Symbol"))]
    befunde = []
    if len(cand) >= 8:
        hit = sum(1 for l in cand if l in raw)
        if hit / len(cand) >= 0.5:
            befunde.append(f"unbearbeiteter Rohtext: {hit} von {len(cand)} Textzeilen sind identisch mit Zeilen der Textebene. "
                           "Spalten in Lesereihenfolge ordnen, Zeilen zu Absätzen zusammenfügen, Überschriften als ## setzen, "
                           "Kolumnentitel und Seitenzahl-Fusszeilen weglassen")
    hyph = sum(1 for a, b in zip(lines, lines[1:]) if re.search(r"[A-Za-zÀ-ÿ]-$", a) and re.match(r"[a-zà-ÿ]", b))
    if hyph >= 3:
        befunde.append(f"Silbentrennung am Zeilenende nicht aufgelöst ({hyph} Stellen); Wörter zusammenfügen, Zeilen zu Absätzen verbinden")
    zer = [l for l in lines if zerlegt(l)]
    if zer:
        befunde.append(f"zerlegte Textzeilen ({len(zer)}), z. B. «{zer[0][:50]}…»: Text am Seitenbild lesen und neu schreiben, "
                       "nicht aus der Textebene übernehmen")
    return befunde


def grafik_befunde(text):
    befunde = []
    lines = text.splitlines()
    open_idx = [i for i, l in enumerate(lines) if re.match(r"^\s*\**\[Grafik(?:\s[^\]]*)?\]", l)]
    end_idx = [i for i, l in enumerate(lines) if re.match(r"^\s*\**\[Ende Grafik", l)]
    if len(open_idx) != len(end_idx):
        befunde.append(f"{len(open_idx)} Grafikanfänge, aber {len(end_idx)} «[Ende Grafik]»")
    for a in open_idx:
        b = next((e for e in end_idx if e > a), len(lines))
        block = "\n".join(lines[a:b])
        if not STATUS.search(block):
            befunde.append(f"Grafikblock ohne Wertstatus: «{lines[a].strip('* ')[:70]}»")
    return befunde


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("transkript")
    ap.add_argument("--schwelle", type=float, default=0.95)
    ap.add_argument("--protokoll", default="pruefprotokoll.txt")
    ap.add_argument("--nur-vorhandene", action="store_true", help="fehlende Seiten nicht melden (Zwischenprüfung)")
    a = ap.parse_args()

    pages = load_pages(a.transkript)
    result = {"pdf": a.pdf, "transkript": a.transkript, "seiten": [], "global": []}
    with pdfplumber.open(a.pdf) as pdf:
        N = len(pdf.pages)
        single = single_size(pdf)
        extra = sorted(n for n in pages if n < 1 or n > N)
        if extra:
            result["global"].append(f"Seiten ausserhalb 1–{N}: {extra}")
        for n in range(1, N + 1):
            rec = {"seite": n, "befunde": []}
            if n not in pages:
                if not a.nur_vorhandene:
                    rec["befunde"].append("Seite fehlt im Transkript")
                    result["seiten"].append(rec)
                continue
            first, text, n_total, fname = pages[n]
            m = MARKER.match(first)
            if not m or int(m.group(1)) != n or int(m.group(2)) != N:
                rec["befunde"].append(f"Seitenmarker falsch oder fehlt ({fname}): «{first[:60]}» – erwartet [[Seite {n}/{N} …]]")
            body = text.split("\n", 1)[1] if "\n" in text else ""
            if not body.strip():
                rec["befunde"].append("Seite ohne Inhalt")
            elif "[leere Seite]" in body and len(body.strip()) < 40:
                rec["leer"] = True
            page = pdf.pages[n - 1]
            words = pdf_words(page)
            has_text = sum(len(w["text"]) for w in words) >= 20
            rec["textebene"] = has_text
            low = text.replace("­", "").lower()
            if has_text:
                t_list = [norm_num(x) for x in NUM.findall(text)]
                t_nums = set(t_list)
                left = Counter(t_list)  # verbleibende Vorkommen im Transkript
                ticks = axis_ticks(words)
                missing, ignored, seltener = [], [], Counter()
                for i, w in enumerate(words):
                    for x in NUM.findall(w["text"]):
                        if i in ticks:  # Achsenbeschriftung: nicht zählen
                            ignored.append(x)
                            continue
                        var = num_variants(x)
                        if len(re.sub(r"\D", "", x)) == 1 or re.fullmatch(r"(19[5-9]\d|20[0-4]\d)", x):
                            # einstellige Zahlen und Jahreszahlen: nur Vorhandensein prüfen (Achsen, Titel, Fusszeilen)
                            if not (var & t_nums) and x not in missing:
                                missing.append(x)
                            continue
                        hit = next((v for v in var if left[v] > 0), None)
                        if hit:
                            left[hit] -= 1
                        elif var & t_nums:
                            seltener[norm_num(x)] += 1  # kommt vor, aber seltener als in der PDF
                        elif not glued(x, t_nums) and x not in missing:
                            missing.append(x)
                if seltener:
                    rec["befunde"].append("seltener als in der PDF: " + ", ".join(f"{k} ({v}× zu wenig)" for k, v in seltener.items()))
                if ignored:
                    rec["achsenbeschriftungen_ignoriert"] = ignored
                if missing:
                    rec["befunde"].append(f"fehlende Zahlen ({len(missing)}): {', '.join(missing[:40])}")
                    rec["fehlende_zahlen"] = missing
                toks = {t.lower() for w in words for t in WORD.findall(w["text"])}
                found = {t for t in toks if t in low}
                cov = len(found) / len(toks) if toks else 1.0
                rec["wortabdeckung"] = round(cov, 4)
                if cov < a.schwelle:
                    miss = sorted(toks - found)
                    rec["befunde"].append(f"Wortabdeckung {cov:.1%} < {a.schwelle:.0%}; fehlend u. a.: {', '.join(miss[:25])}")
            else:
                rec["befunde"].append("keine Textebene – automatischer Abgleich nicht möglich, am Seitenbild prüfen")
            if has_text:
                rec["befunde"] += rohtext_befunde(text, roh_zeilen(page, single))
            rec["befunde"] += grafik_befunde(text)
            result["seiten"].append(rec)

    flagged = [r for r in result["seiten"] if r["befunde"]]
    covs = [r["wortabdeckung"] for r in result["seiten"] if "wortabdeckung" in r]
    summary = [
        f"Prüfprotokoll · PDF: {a.pdf} ({N} Seiten) · Transkript: {a.transkript}",
        f"Seiten im Transkript: {len([n for n in pages if 1 <= n <= N])} von {N}",
        f"Seiten mit Befunden: {len(flagged)}" + (f" ({', '.join(str(r['seite']) for r in flagged)})" if flagged else ""),
        f"Wortabdeckung: Minimum {min(covs):.1%}, Mittel {sum(covs) / len(covs):.1%}" if covs else "Wortabdeckung: –",
        f"Schwelle Wortabdeckung: {a.schwelle:.0%}",
    ] + result["global"]
    detail = [f"Seite {r['seite']}: " + " | ".join(r["befunde"]) for r in flagged]
    report = "\n".join(summary) + "\n\n" + ("\n".join(detail) if detail else "Keine Befunde.") + "\n"
    pathlib.Path(a.protokoll).write_text(report, encoding="utf-8")
    pathlib.Path(a.protokoll).with_suffix(".json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(report)
    return 1 if (flagged or result["global"]) else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001
        print(f"FEHLER: {type(e).__name__}: {e}")
        sys.exit(2)
```

## aufteilen.py

```python
"""LAV Ingest – Volltext in Teile aufteilen und Kontrollwörter setzen (Schritt 7).

Aufruf:
  python aufteilen.py <seitenordner> <zielordner> --id LAV-07 --titel "Volltitel" --quelle studie.pdf
                      [--version 1.0] [--datum 2026-10-14] [--max 18000 (Bytes)] [--bestehend kontrollwoerter.csv]

Eingabe: Ordner mit s001.md … sNNN.md (eine Datei je PDF-Seite, Beginn mit [[Seite n/N …]]), lückenlos 1…N.
Ausgabe: <zielordner>/teil-01.md … mit Kopf und Schlusszeile (zufälliges Kontrollwort je Teil);
         im übergeordneten Ordner kontrollwoerter.csv und katalog-zeile.txt (Zeile «Volltext: …» für den Katalog).
Geteilt wird nur an Seitengrenzen. Teilgrösse in Bytes (UTF-8): 18’000 Bytes bleiben sicher unter 20 KB.
Ist eine einzelne Seite grösser als --max, steht sie allein in einem Teil
und wird gemeldet (Exit-Code 1). Der Inhalt der Seite wird nie gekürzt; der Agent liest einen solchen Teil
in Zeilenbereichen bis zur Schlusszeile.
"""
import argparse
import csv
import datetime
import pathlib
import re
import secrets
import sys

MARKER = re.compile(r"^\[\[Seite (\d+)/(\d+)(?:\s*·[^\]]*)?\]\]\s*$")
WORDS = ["ALVIER", "BACHTEL", "BERNINA", "BIETSCHHORN", "BRISTEN", "CALANDA", "CHASSERAL", "CHAUMONT", "DENT",
         "DOM", "EIGER", "FALKNIS", "FINSTERAARHORN", "FRONALPSTOCK", "GALENSTOCK", "GLAERNISCH", "GRIMSEL",
         "GURTEN", "HOERNLI", "HOHGANT", "JUNGFRAU", "KAMOR", "LAGERN", "LEONE", "LISKAMM", "MATTERHORN", "MOLESON",
         "MOENCH", "MYTHEN", "NAPF", "NIESEN", "OBERALP", "PALUE", "PILATUS", "PIZOL", "RHEINWALD", "RIGI", "ROSA",
         "SAENTIS", "SCHILTHORN", "SCHRECKHORN", "SPEER", "STANSERHORN", "STOCKHORN", "SUSTEN", "TITLIS", "TOEDI",
         "UETLIBERG", "VILAN", "WEISSHORN", "WETTERHORN", "WILDHORN", "WILDSTRUBEL", "ZERVREILA", "ARVE", "LAERCHE",
         "BERGDOHLE", "STEINBOCK", "GEMSE", "MURMELTIER", "ENZIAN", "EDELWEISS", "ALPENROSE", "ARNIKA"]


def codeword(used):
    while True:
        w = f"{secrets.choice(WORDS)}-{secrets.randbelow(90) + 10}"
        if w not in used:
            used.add(w)
            return w


def header(a, i, n, von, bis, total):
    return (f"# {a.id} · Volltext · Teil {i} von {n} (PDF-Seiten {von}–{bis} von {total})\n\n"
            f"Studie: {a.titel} · Quelldatei: {a.quelle} · Transkript-Version {a.version} · {a.datum}\n"
            f"Lesehinweis: Die Studie ist nur vollständig gelesen, wenn alle {n} Teile bis zum Ende gelesen sind.\n"
            f"Konventionen: [[Seite n/N]] = Beginn der PDF-Seite n (zitieren als [{a.id}, S. n]) · Grafikwerte mit "
            f"Status (beschriftet, berechnet, abgelesen ca., nicht eindeutig ablesbar) · [Fussnote n] · [Bild: …] · "
            f"[unleserlich]\n\n---\n\n")


def ending(a, i, n, word):
    nxt = f"weiter mit teil-{i + 1:02d}.md" if i < n else f"DOKUMENTENDE {a.id}"
    return f"\n\n---\n\n— Ende Teil {i} von {n} · Kontrollwort Teil {i}: {word} · {nxt} —\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seitenordner")
    ap.add_argument("zielordner")
    ap.add_argument("--id", required=True)
    ap.add_argument("--titel", required=True)
    ap.add_argument("--quelle", required=True)
    ap.add_argument("--version", default="1.0")
    ap.add_argument("--datum", default=datetime.date.today().isoformat())
    ap.add_argument("--max", type=int, default=18000, help="maximale Grösse pro Teil in Bytes (UTF-8) inkl. Kopf und Schlusszeile")
    ap.add_argument("--bestehend", help="kontrollwoerter.csv der ganzen Library (Duplikate vermeiden)")
    a = ap.parse_args()

    files = sorted(pathlib.Path(a.seitenordner).glob("s[0-9][0-9][0-9].md"))
    if not files:
        sys.exit("FEHLER: keine Seitendateien s001.md … gefunden")
    pages, total = [], None
    for k, f in enumerate(files, 1):
        txt = f.read_text(encoding="utf-8").strip() + "\n"
        first = txt.splitlines()[0].strip()
        m = MARKER.match(first)
        if not m or int(m.group(1)) != k:
            sys.exit(f"FEHLER: {f.name} beginnt nicht mit [[Seite {k}/N …]] (gefunden: «{first[:60]}»)")
        total = total or int(m.group(2))
        if int(m.group(2)) != total:
            sys.exit(f"FEHLER: {f.name}: Gesamtseitenzahl {m.group(2)} statt {total}")
        pages.append(txt)
    if len(pages) != total:
        sys.exit(f"FEHLER: {len(pages)} Seitendateien, Seitenmarker nennen {total} Seiten")

    used = set()
    if a.bestehend and pathlib.Path(a.bestehend).exists():
        with open(a.bestehend, encoding="utf-8") as fh:
            used |= {r["kontrollwort"] for r in csv.DictReader(fh, delimiter=";")}

    # Packen mit Platzhalter-Kopf (Länge für zweistellige Teilzahl)
    def b(x):
        return len(x.encode("utf-8"))

    budget_overhead = b(header(a, 99, 99, total, total, total)) + b(ending(a, 99, 99, "WILDSTRUBEL-99"))
    groups, cur, size, oversize = [], [], 0, []
    for n_page, txt in enumerate(pages, 1):
        if cur and size + b(txt) + 1 + budget_overhead > a.max:
            groups.append(cur)
            cur, size = [], 0
        if b(txt) + budget_overhead > a.max:
            oversize.append(n_page)
        cur.append(n_page)
        size += b(txt) + 1
    if cur:
        groups.append(cur)

    out = pathlib.Path(a.zielordner)
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("teil-*.md"):
        old.unlink()
    n = len(groups)
    rows, katalog = [], []
    for i, g in enumerate(groups, 1):
        word = codeword(used)
        body = "\n".join(pages[p - 1] for p in g).rstrip("\n")
        text = header(a, i, n, g[0], g[-1], total) + body + ending(a, i, n, word)
        name = f"teil-{i:02d}.md"
        (out / name).write_text(text, encoding="utf-8")
        rows.append({"datei": f"volltext/{a.id}/{name}", "kontrollwort": word, "seiten": f"{g[0]}–{g[-1]}",
                     "bytes": len(text.encode("utf-8")), "datum": a.datum})
        katalog.append(f"teil-{i:02d} S. {g[0]}–{g[-1]}")
    meta = out.parent  # Listen gehören NICHT in den Volltext-Ordner (sonst landen sie im Skill-ZIP)
    with open(meta / "kontrollwoerter.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["datei", "kontrollwort", "seiten", "bytes", "datum"], delimiter=";")
        w.writeheader()
        w.writerows(rows)
    line = f"- Volltext: {n} Teil{'e' if n > 1 else ''} – " + " · ".join(katalog)
    (meta / "katalog-zeile.txt").write_text(line + "\n", encoding="utf-8")
    for r in rows:
        print(f"{r['datei']}: Seiten {r['seiten']}, {r['bytes']} Bytes")
    print("Katalog:", line)
    if oversize:
        print(f"WARNUNG: Seiten grösser als die Teilgrösse ({a.max} Bytes): {oversize} – stehen allein in einem Teil.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## paket.py

```python
"""LAV Ingest – Prüfung des Skill-Pakets des Library-Agenten vor dem Upload.

Aufruf:
  python paket.py <lav-learning-library.zip | ordner> [--max 45000] [--erneuern]
                  [--ausgabe geprueft.zip] [--csv kontrollwoerter.csv]
  python scripts/paket.py --selbst [--max 45000]
      (in der Library-Skill: prüft das Paket, das tatsächlich geladen ist; nur lesen, ohne Upload)

Prüft:
  - SKILL.md mit Frontmatter (name, description); Lage (oberste Ebene oder ein Unterordner) wird gemeldet
  - erlaubt sind nur SKILL.md, references/*.md und die Prüfskripte scripts/*.py
  - references/00-katalog*.md, references/01-study-cards*.md, references/volltext/LAV-XX/teil-NN.md vorhanden
  - jede Datei unter references/ endet mit einer Schlusszeile «— … Kontrollwort …: WORT-NN … —»
  - Kontrollwörter eindeutig und nirgends sonst im Paket (auch nicht in SKILL.md)
  - Dateigrösse ≤ --max Bytes (UTF-8)
  - je Studie: Teile lückenlos, Kopf «Teil i von n (PDF-Seiten a–b von N)», Seitenmarker a…b vollständig,
    Seitenbereiche lückenlos von 1 bis N
  - Katalog: Eintrag «## LAV-XX» je Studie, Zeile «Volltext: …» stimmt mit den Teilen überein
  - Study Cards: «## LAV-XX» und «— Ende Card LAV-XX —» je Studie
  - Belege der Cards: jede Zahl einer Card-Zeile mit [S. n] steht auf PDF-Seite n im Volltext derselben Studie
  - Katalog: Ausgaben derselben Reihe (gleicher Kurztitel ohne Jahr) nennen sich gegenseitig unter «Nicht verwechseln mit»
Mit --erneuern erhalten Katalog- und Card-Dateien neue Kontrollwörter (bei einem Ordner direkt in den Dateien). Mit --ausgabe wird das (erneuerte)
Paket als ZIP geschrieben, mit --csv die Liste aller Kontrollwörter (nur für Tests, nicht hochladen).
Exit-Code 0 = keine Befunde, 1 = Befunde, 2 = Fehler.
"""
import argparse
import csv
import pathlib
import re
import secrets
import sys
import tempfile
import zipfile

END = re.compile(r"^— .*Kontrollwort[^:]*: ([A-Z]+-\d{2}).*—\s*$")
HEAD = re.compile(r"^# (LAV-[\w-]+) · Volltext · Teil (\d+) von (\d+) \(PDF-Seiten (\d+)–(\d+) von (\d+)\)")
MARKER = re.compile(r"^\[\[Seite (\d+)/(\d+)(?:\s*·[^\]]*)?\]\]\s*$", re.M)
WORDS = ["ALVIER", "BACHTEL", "BERNINA", "CALANDA", "CHASSERAL", "EIGER", "GLAERNISCH", "GURTEN", "HOERNLI",
         "MYTHEN", "NAPF", "NIESEN", "PILATUS", "PIZOL", "RIGI", "SAENTIS", "SPEER", "TITLIS", "TOEDI", "WEISSHORN"]


NUMB = re.compile(r"\d+(?:[’'`]\d{3})*(?:[.,]\d+)?")
CITE = re.compile(r"\[S\. ?(\d+)(?:\s*[–-]\s*(\d+))?\]")


def nn(x):
    return x.replace("’", "").replace("'", "").replace("`", "").replace(",", ".")


def seitentexte(files):
    """{Seitennummer: Text} aus den Teil-Dateien einer Studie (Seitenmarker als Trenner)."""
    out = {}
    for f in files:
        t = f.read_text(encoding="utf-8")
        marks = list(MARKER.finditer(t))
        for i, m in enumerate(marks):
            out[int(m.group(1))] = t[m.end(): marks[i + 1].start() if i + 1 < len(marks) else len(t)]
    return out


def last_line(text):
    return next((l for l in reversed(text.splitlines()) if l.strip()), "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("quelle", nargs="?")
    ap.add_argument("--selbst", action="store_true", help="eigenes Skill-Paket prüfen (Ordner über scripts/), nur lesen")
    ap.add_argument("--max", type=int, default=45000)
    ap.add_argument("--erneuern", action="store_true")
    ap.add_argument("--ausgabe")
    ap.add_argument("--csv")
    a = ap.parse_args()

    tmp = None
    if a.selbst or not a.quelle:
        if a.erneuern or a.ausgabe:
            sys.exit("FEHLER: --selbst prüft nur und schreibt nichts (ohne --erneuern und --ausgabe)")
        a.quelle = str(pathlib.Path(__file__).resolve().parent.parent)
        print("Selbstprüfung des geladenen Pakets")
    src = pathlib.Path(a.quelle)
    if src.is_file():
        tmp = tempfile.TemporaryDirectory()
        with zipfile.ZipFile(src) as z:
            for info in z.infolist():
                target = (pathlib.Path(tmp.name) / info.filename).resolve()
                if not str(target).startswith(str(pathlib.Path(tmp.name).resolve())):
                    sys.exit(f"FEHLER: unzulässiger Pfad im ZIP: {info.filename}")
            z.extractall(tmp.name)
        src = pathlib.Path(tmp.name)
    skills = list(src.glob("SKILL.md")) + list(src.glob("*/SKILL.md"))
    if len(skills) != 1:
        sys.exit(f"FEHLER: genau eine SKILL.md erwartet (oberste Ebene oder ein Unterordner), gefunden: {len(skills)}")
    root = skills[0].parent
    befunde, info = [], [f"SKILL.md liegt {'auf oberster Ebene' if root == src else 'im Unterordner ' + root.name}"]

    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    fm = re.match(r"^---\n(.*?)\n---\n", skill, re.S)
    if not fm or not re.search(r"^name:\s*\S", fm.group(1), re.M) or not re.search(r"^description:\s*\S", fm.group(1), re.M):
        befunde.append("SKILL.md: Frontmatter mit name und description fehlt oder ist ungültig")

    ref = root / "references"
    kat = sorted(ref.glob("00-katalog*.md"))
    cards = sorted(ref.glob("01-study-cards*.md"))
    parts = sorted(ref.glob("volltext/*/teil-*.md"))
    if not kat:
        befunde.append("Katalog fehlt (references/00-katalog*.md)")
    if not cards:
        befunde.append("Study Cards fehlen (references/01-study-cards*.md)")
    all_md = sorted(ref.rglob("*.md"))
    for f in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = f.relative_to(root).as_posix()
        if "__pycache__" in rel:
            continue
        if rel != "SKILL.md" and not (rel.startswith("references/") and f.suffix == ".md") \
                and not (rel.startswith("scripts/") and f.suffix == ".py" and rel.count("/") == 1):
            befunde.append(f"{rel}: gehört nicht ins Paket (nur SKILL.md, references/*.md und scripts/*.py; "
                           "Listen wie kontrollwoerter.csv nie hochladen)")

    # Schlusszeilen, Kontrollwörter, Grössen
    words = {}
    for f in all_md:
        t = f.read_text(encoding="utf-8")
        rel = f.relative_to(root).as_posix()
        m = END.match(last_line(t).strip())
        if not m:
            befunde.append(f"{rel}: Schlusszeile mit Kontrollwort fehlt")
        else:
            words.setdefault(m.group(1), []).append(rel)
        size = len(t.encode("utf-8"))
        if size > a.max:
            befunde.append(f"{rel}: {size} Bytes > {a.max}")
    for w, fs in words.items():
        if len(fs) > 1:
            befunde.append(f"Kontrollwort {w} mehrfach vergeben: {', '.join(fs)}")
    texts = {f.relative_to(root).as_posix(): f.read_text(encoding="utf-8") for f in root.rglob("*.md")}
    for w in words:
        n = sum(t.count(w) for t in texts.values())
        if n > 1:
            befunde.append(f"Kontrollwort {w} steht {n}× im Paket (erlaubt: nur in der eigenen Schlusszeile)")

    # Studien
    studies = {}
    for f in parts:
        studies.setdefault(f.parent.name, []).append(f)
    kat_text = "\n".join(f.read_text(encoding="utf-8") for f in kat)
    card_text = "\n".join(f.read_text(encoding="utf-8") for f in cards)
    for sid, fs in sorted(studies.items()):
        fs = sorted(fs)
        n_files = len(fs)
        ranges, total = [], None
        for i, f in enumerate(fs, 1):
            rel = f.relative_to(root).as_posix()
            if f.name != f"teil-{i:02d}.md":
                befunde.append(f"{sid}: Teil-Dateien nicht lückenlos nummeriert ({f.name})")
            t = f.read_text(encoding="utf-8")
            h = HEAD.match(t)
            if not h:
                befunde.append(f"{rel}: Kopfzeile «# {sid} · Volltext · Teil i von n (PDF-Seiten a–b von N)» fehlt")
                continue
            hid, hi, hn, ha, hb, hN = h.group(1), *map(int, h.groups()[1:])
            if hid != sid or hi != i or hn != n_files:
                befunde.append(f"{rel}: Kopf nennt {hid} Teil {hi} von {hn}, erwartet {sid} Teil {i} von {n_files}")
            total = total or hN
            marks = [int(x) for x, _ in MARKER.findall(t)]
            if marks != list(range(ha, hb + 1)):
                befunde.append(f"{rel}: Seitenmarker {marks[:3]}…{marks[-3:] if marks else []} passen nicht zu Seiten {ha}–{hb}")
            if f"Teil {i} von {n_files}" not in last_line(t):
                befunde.append(f"{rel}: Schlusszeile nennt nicht «Teil {i} von {n_files}»")
            ranges.append((ha, hb))
        flat = [p for a_, b_ in ranges for p in range(a_, b_ + 1)]
        if total and flat != list(range(1, total + 1)):
            befunde.append(f"{sid}: Seitenbereiche der Teile decken nicht lückenlos 1–{total} ab: {ranges}")
        # Katalog
        km = re.search(rf"^## {re.escape(sid)}\b.*?(?=^## |\Z)", kat_text, re.S | re.M)
        if not km:
            befunde.append(f"Katalog: Eintrag «## {sid}» fehlt")
        else:
            want = " · ".join(f"teil-{i:02d} S. {x}–{y}" for i, (x, y) in enumerate(ranges, 1))
            vl = re.search(r"Volltext:\s*(\d+) Teile? – (.+)", km.group(0))
            if not vl or int(vl.group(1)) != n_files or vl.group(2).strip() != want:
                befunde.append(f"Katalog {sid}: Zeile «Volltext: …» stimmt nicht; erwartet «Volltext: {n_files} "
                               f"Teil{'e' if n_files > 1 else ''} – {want}»")
        cm = re.search(rf"^## {re.escape(sid)}\b.*?(?=^— Ende Card {re.escape(sid)} —|\Z)", card_text, re.S | re.M)
        if cm:
            pages_txt = seitentexte(fs)
            for line in cm.group(0).splitlines():
                cites = list(CITE.finditer(line))
                if not cites:
                    continue
                cited = sorted({n for c in cites for n in range(int(c.group(1)), int(c.group(2) or c.group(1)) + 1)})
                bare = CITE.sub("", line)
                have = {nn(x) for n in cited for x in NUMB.findall(pages_txt.get(n, ""))}
                have |= {y for x in list(have) for y in ([x[:-2]] if x.endswith(".0") else [])}
                miss = []
                for x in NUMB.findall(bare):
                    if nn(x) not in have and nn(x) not in miss:
                        miss.append(nn(x))
                if miss:
                    befunde.append(f"Card {sid}: Zahl {', '.join(miss)} steht nicht auf S. {', '.join(map(str, cited))} im Volltext "
                                   f"(Zeile «{bare.strip()[:60]}…»). Beleg korrigieren oder als berechnet kennzeichnen")
        if not re.search(rf"^## {re.escape(sid)}\b", card_text, re.M):
            befunde.append(f"Study Cards: Card «## {sid}» fehlt")
        elif f"— Ende Card {sid} —" not in card_text:
            befunde.append(f"Study Cards: Schlusszeile «— Ende Card {sid} —» fehlt")
    for sid in re.findall(r"^## (LAV-[\w-]+)", kat_text, re.M):
        if sid not in studies:
            befunde.append(f"Katalog nennt {sid}, aber references/volltext/{sid}/ fehlt")

    # Ausgaben derselben Reihe (z. B. Gesundheitsmonitor 2024 und 2025) müssen sich gegenseitig abgrenzen
    entries = {m.group(1): (m.group(2), m.group(3)) for m in
               re.finditer(r"^## (LAV-[\w-]+)\s*·\s*(.+?)\s*$(.*?)(?=^## |\Z)", kat_text, re.S | re.M)}

    def stamm(titel):
        return re.sub(r"[^a-zäöüéèàç]+", "", re.sub(r"\b(?:19|20)\d{2}\b", "", titel.lower()))

    ids = sorted(entries)
    for i, a_id in enumerate(ids):
        for b_id in ids[i + 1:]:
            if stamm(entries[a_id][0]) and stamm(entries[a_id][0]) == stamm(entries[b_id][0]):
                for x, y in ((a_id, b_id), (b_id, a_id)):
                    nv = re.search(r"Nicht verwechseln mit:\s*(.*)", entries[x][1])
                    if not nv or y not in nv.group(1):
                        befunde.append(f"Katalog {x}: «Nicht verwechseln mit» nennt {y} nicht, obwohl beide zur selben Reihe "
                                       f"gehören («{entries[x][0]}» / «{entries[y][0]}»)")

    # Erneuern
    if a.erneuern:
        used = set(words)
        for f in kat + cards:
            t = f.read_text(encoding="utf-8")
            ll = last_line(t)
            m = END.match(ll.strip())
            if not m:
                continue
            while True:
                new = f"{secrets.choice(WORDS)}-{secrets.randbelow(90) + 10}"
                if new not in used and all(new not in x for x in texts.values()):
                    break
            used.add(new)
            f.write_text(t.replace(ll, ll.replace(m.group(1), new)), encoding="utf-8")
            words.pop(m.group(1), None)
            words[new] = [f.relative_to(root).as_posix()]
            info.append(f"Kontrollwort erneuert: {f.relative_to(root).as_posix()} → {new}")

    if a.csv:
        with open(a.csv, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, delimiter=";")
            w.writerow(["datei", "kontrollwort"])
            for k, fs in sorted(words.items(), key=lambda kv: kv[1][0]):
                w.writerow([fs[0], k])
    if a.ausgabe:
        with zipfile.ZipFile(a.ausgabe, "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(p for p in src.rglob("*") if p.is_file()):
                z.write(f, f.relative_to(src).as_posix())
        info.append(f"Paket geschrieben: {a.ausgabe}")

    print(f"Paketprüfung: {a.quelle}")
    print(f"Studien: {len(studies)} · Volltext-Teile: {len(parts)} · Katalog-Dateien: {len(kat)} · Card-Dateien: {len(cards)}")
    print("\n".join(info))
    print("\n" + ("\n".join("BEFUND: " + b for b in befunde) if befunde else "Keine Befunde."))
    if tmp:
        tmp.cleanup()
    return 1 if befunde else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        print(f"FEHLER: {type(e).__name__}: {e}")
        sys.exit(2)
```

## paket_bauen.py

```python
"""LAV Ingest – Skill-Paket des Library-Agenten aus Ingest-Ergebnissen bauen und prüfen.

Aufruf:
  python paket_bauen.py --uploads [<ordner>] […]   (alle ZIPs im Upload-Ordner; Dateipfade erscheinen nicht im Befehl)
  python paket_bauen.py <eingabe> [<eingabe> …] [--freigabe "LAV-NN=Name, Research"] [--entfernen LAV-NN]
                        [--max 45000] [--ausgabe lav-learning-library.zip] [--csv kontrollwoerter_alle.csv]
                        [--vorlage <library-SKILL.md>]

Eingaben (beliebig gemischt, ZIP oder Ordner):
  - Ingest-Ergebnis einer Studie (LAV-NN_ingest.zip mit katalog-eintrag.md, card.md, volltext/teil-NN.md)
  - ZIP mit mehreren Ingest-ZIPs
  - höchstens ein bestehendes Library-Paket (SKILL.md + references/): seine Studien werden übernommen
Neue Ingest-Ergebnisse ersetzen Studien gleicher ID aus dem bestehenden Paket.

Ablauf:
  1. Studien einsammeln und prüfen (ID in Katalog-Eintrag, Card und Volltext-Köpfen gleich, Teile vorhanden).
  2. Freigaben setzen (--freigabe; «*=Name» für alle noch nicht freigegebenen Cards; Datum = heute).
  3. Ausgaben derselben Reihe (gleicher Titel ohne Jahr) gegenseitig unter «Nicht verwechseln mit» eintragen.
  4. Kontrollwörter der Volltexte, die zwischen Studien doppelt vorkommen, durch neue ersetzen.
  5. Katalog und Cards aus den Einträgen zusammensetzen (nach ID sortiert, bei Bedarf auf mehrere Dateien verteilt),
     SKILL.md aus der Vorlage, scripts/paket.py und scripts/belege.py dazu.
  6. paket.py prüfen lassen, Kontrollwörter von Katalog und Cards erneuern, ZIP und Kontrollwort-Liste schreiben.
Exit-Code 0 = keine Befunde, 1 = Befunde (Paket nicht verwenden), 2 = Fehler.
Nicht freigegebene Cards sind kein Befund, werden aber gemeldet: Ein solches Paket ist nur ein Testpaket.
"""
import argparse
import datetime
import io
import pathlib
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import zipfile

HERE = pathlib.Path(__file__).resolve().parent
END = re.compile(r"^— .*Kontrollwort[^:]*: ([A-Z]+-\d{2}).*—\s*$")
HEAD = re.compile(r"^# (LAV-[\w-]+) · Volltext · Teil (\d+) von (\d+)")
ENTRY = re.compile(r"^## (LAV-[\w-]+)\s*·\s*(.+?)\s*$")
WORDS = ["ALVIER", "BACHTEL", "BERNINA", "BIETSCHHORN", "BRISTEN", "CALANDA", "CHASSERAL", "CHAUMONT", "DENT",
         "DOM", "EIGER", "FALKNIS", "FINSTERAARHORN", "FRONALPSTOCK", "GALENSTOCK", "GLAERNISCH", "GRIMSEL",
         "GURTEN", "HOERNLI", "HOHGANT", "JUNGFRAU", "KAMOR", "LAGERN", "LEONE", "LISKAMM", "MATTERHORN", "MOLESON",
         "MOENCH", "MYTHEN", "NAPF", "NIESEN", "OBERALP", "PALUE", "PILATUS", "PIZOL", "RHEINWALD", "RIGI", "ROSA",
         "SAENTIS", "SCHILTHORN", "SCHRECKHORN", "SPEER", "STANSERHORN", "STOCKHORN", "SUSTEN", "TITLIS", "TOEDI",
         "UETLIBERG", "VILAN", "WEISSHORN", "WETTERHORN", "WILDHORN", "WILDSTRUBEL", "ZERVREILA", "ARVE", "LAERCHE",
         "BERGDOHLE", "STEINBOCK", "GEMSE", "MURMELTIER", "ENZIAN", "EDELWEISS", "ALPENROSE", "ARNIKA"]

# Hier legt die Plattform hochgeladene Dateien ab (Copilot-Studio-Harness: /app/uploads)
UPLOAD_ORDNER = ["/app/uploads", "uploads", "/mnt/data", "/mnt/user-data/uploads"]

KAT_KOPF = ("# LAV Learning Library – Katalog\n\n"
            "Stand: {datum} · {anzahl} Studien · Skill-Version {version}{datei}\n"
            "Zweck: Bestimmung der richtigen Studie. Inhalte stehen in den Study Cards und Volltexten.\n\n")
CARD_KOPF = ("# LAV Learning Library – Study Cards\n\n"
             "Stand: {datum} · {anzahl} Cards · Datei {i} von {k}\n"
             "Belege: [S. n] = PDF-Seite im Volltext der jeweiligen Studie.\n\n")


class Studie:
    def __init__(self, sid, titel, katalog, card, teile, herkunft):
        self.sid, self.titel, self.katalog, self.card = sid, titel, katalog, card
        self.teile = teile          # [(Dateiname, Text)]
        self.herkunft = herkunft    # Name der Eingabe


def sicher_entpacken(data, ziel):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for info in z.infolist():
            t = (ziel / info.filename).resolve()
            if not str(t).startswith(str(ziel.resolve())):
                sys.exit(f"FEHLER: unzulässiger Pfad im ZIP: {info.filename}")
        z.extractall(ziel)


def ordner_sammeln(pfad, arbeits, name, tiefe=0):
    """Liefert [(Name, Ordner)] aller Ordner mit Inhalt; ZIPs in ZIPs werden entpackt (höchstens 2 Ebenen)."""
    if pfad.is_file():
        if tiefe > 2:
            sys.exit(f"FEHLER: zu tief verschachtelte ZIPs: {name}")
        ziel = pathlib.Path(tempfile.mkdtemp(dir=arbeits))
        sicher_entpacken(pfad.read_bytes(), ziel)
        pfad = ziel
    out = [(name, pfad)]
    for inner in sorted(pfad.rglob("*.zip")):
        out += ordner_sammeln(inner, arbeits, f"{name} › {inner.name}", tiefe + 1)
    return out


def teile_lesen(ordner):
    return [(f.name, f.read_text(encoding="utf-8")) for f in sorted(ordner.glob("teil-*.md"))]


def ingest_studien(name, ordner, befunde):
    out = []
    for ke in sorted(ordner.rglob("katalog-eintrag.md")):
        root = ke.parent
        if "__MACOSX" in ke.parts:
            continue
        kat = ke.read_text(encoding="utf-8").strip()
        m = ENTRY.match(kat.splitlines()[0]) if kat else None
        if not m:
            befunde.append(f"{name}: katalog-eintrag.md beginnt nicht mit «## LAV-NN · Titel»")
            continue
        sid, titel = m.groups()
        card_f = root / "card.md"
        if not card_f.exists():
            befunde.append(f"{name}: card.md fehlt ({sid})")
            continue
        card = card_f.read_text(encoding="utf-8").strip()
        cm = ENTRY.match(card.splitlines()[0]) if card else None
        if not cm or cm.group(1) != sid:
            befunde.append(f"{name}: card.md gehört nicht zu {sid} (erste Zeile «{card.splitlines()[0][:50] if card else ''}»)")
            continue
        vt = root / "volltext"
        teile = teile_lesen(vt / sid) or teile_lesen(vt)
        if not teile:
            befunde.append(f"{name}: keine Volltext-Teile (volltext/teil-NN.md) für {sid}")
            continue
        for fn, t in teile:
            h = HEAD.match(t)
            if not h or h.group(1) != sid:
                befunde.append(f"{name}: volltext/{fn} gehört nicht zu {sid}")
        out.append(Studie(sid, titel, kat, card, teile, name))
    return out


def eintraege(text, bis_ende_card=False):
    """Teilt Katalog- oder Card-Text in {ID: Eintrag}."""
    out = {}
    if bis_ende_card:
        for m in re.finditer(r"^## (LAV-[\w-]+)\b.*?^— Ende Card \1 —", text, re.S | re.M):
            out[m.group(1)] = m.group(0).strip()
    else:
        for m in re.finditer(r"^## (LAV-[\w-]+)\b.*?(?=^## |^— Ende |\Z)", text, re.S | re.M):
            out[m.group(1)] = m.group(0).strip()
    return out


def paket_studien(name, ordner, befunde):
    skills = list(ordner.glob("SKILL.md")) + list(ordner.glob("*/SKILL.md"))
    root = skills[0].parent
    ref = root / "references"
    kat = eintraege("\n".join(f.read_text(encoding="utf-8") for f in sorted(ref.glob("00-katalog*.md"))))
    cards = eintraege("\n".join(f.read_text(encoding="utf-8") for f in sorted(ref.glob("01-study-cards*.md"))), True)
    out = []
    for sid, k in sorted(kat.items()):
        teile = teile_lesen(ref / "volltext" / sid)
        if sid not in cards or not teile:
            befunde.append(f"{name}: {sid} unvollständig (Card oder Volltext fehlt) – nicht übernommen")
            continue
        out.append(Studie(sid, ENTRY.match(k.splitlines()[0]).group(2), k, cards[sid], teile, name))
    return out


def stamm(titel):
    return re.sub(r"[^a-zäöüéèàç]+", "", re.sub(r"\b(?:19|20)\d{2}\b", "", titel.lower()))


def ist_freigegeben(card):
    m = re.search(r"^Freigegeben:\s*(.*)$", card, re.M)
    return bool(m) and not re.match(r"\s*(–|-|\[|ausstehend|offen|\(ausstehend)", m.group(1), re.I)


def freigeben(card, name, datum):
    m = re.search(r"^Freigegeben:.*$", card, re.M)
    vers = re.search(r"Volltext-Version\s*[\d.]+", m.group(0)) if m else None
    neu = f"Freigegeben: {name} · {datum}" + (f" · {vers.group(0)}" if vers else "")
    if m:
        return card[:m.start()] + neu + card[m.end():]
    z = card.split("\n", 1)
    return z[0] + "\n" + neu + ("\n" + z[1] if len(z) > 1 else "")


def verteilen(eintr, kopf_len, fuss_len, maxb):
    """Verteilt Einträge in Reihenfolge auf Dateien, deren Grösse ≤ maxb bleibt."""
    dateien, cur, size = [], [], kopf_len + fuss_len
    for e in eintr:
        b = len(e.encode("utf-8")) + 2
        if cur and size + b > maxb:
            dateien.append(cur)
            cur, size = [], kopf_len + fuss_len
        cur.append(e)
        size += b
    if cur:
        dateien.append(cur)
    return dateien


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("eingaben", nargs="*")
    ap.add_argument("--uploads", nargs="?", const="auto", metavar="ORDNER",
                    help="alle ZIPs im Upload-Ordner verwenden (ohne Ordner: Upload-Ordner der Plattform suchen)")
    ap.add_argument("--freigabe", action="append", default=[], help="«LAV-NN=Name, Research» oder «*=Name»")
    ap.add_argument("--entfernen", action="append", default=[], help="Studien-ID, die nicht ins Paket soll")
    ap.add_argument("--max", type=int, default=45000)
    ap.add_argument("--ausgabe", default="lav-learning-library.zip")
    ap.add_argument("--csv", default="kontrollwoerter_alle.csv")
    ap.add_argument("--vorlage", help="SKILL.md der Library (Standard: ../assets/library-SKILL.md neben scripts/)")
    a = ap.parse_args()
    if a.uploads:
        kandidaten = [a.uploads] if a.uploads != "auto" else UPLOAD_ORDNER
        ordner = next((pathlib.Path(k) for k in kandidaten if pathlib.Path(k).is_dir()), None)
        if not ordner:
            sys.exit(f"FEHLER: kein Upload-Ordner gefunden (gesucht: {', '.join(kandidaten)})")
        zips = sorted(f for f in ordner.iterdir() if f.is_file() and f.suffix.lower() == ".zip")
        if not zips:
            sys.exit(f"FEHLER: keine ZIP-Dateien in {ordner}")
        print(f"Upload-Ordner {ordner}: {len(zips)} ZIP-Dateien – " + ", ".join(f.name for f in zips))
        a.eingaben = list(a.eingaben) + [str(f) for f in zips]
    if not a.eingaben:
        sys.exit("FEHLER: keine Eingaben (ZIP-Dateien angeben oder --uploads verwenden)")

    vorlage = pathlib.Path(a.vorlage) if a.vorlage else HERE.parent / "assets" / "library-SKILL.md"
    if not vorlage.exists():
        sys.exit(f"FEHLER: Vorlage der Library-SKILL.md nicht gefunden: {vorlage}")
    werkzeuge = [HERE / "paket.py", HERE / "belege.py"]
    for w in werkzeuge:
        if not w.exists():
            sys.exit(f"FEHLER: {w.name} muss im selben Ordner liegen wie paket_bauen.py")
    skill_md = vorlage.read_text(encoding="utf-8")
    vm = re.search(r"^Version (\d+(?:\.\d+)*)", skill_md, re.M)
    version = vm.group(1) if vm else "?"
    datum = datetime.date.today().isoformat()

    arbeits = pathlib.Path(tempfile.mkdtemp())
    befunde, info, hinweise = [], [], []
    basis, neu = {}, {}
    basis_name = None
    for e in a.eingaben:
        p = pathlib.Path(e)
        if not p.exists():
            sys.exit(f"FEHLER: Eingabe nicht gefunden: {e}")
        for name, ordner in ordner_sammeln(p, arbeits, p.name):
            if list(ordner.glob("SKILL.md")) + list(ordner.glob("*/SKILL.md")):
                if basis_name:
                    sys.exit(f"FEHLER: mehr als ein bestehendes Library-Paket ({basis_name}, {name})")
                basis_name = name
                for s in paket_studien(name, ordner, befunde):
                    basis[s.sid] = s
            else:
                for s in ingest_studien(name, ordner, befunde):
                    if s.sid in neu:
                        befunde.append(f"{s.sid} kommt in mehreren Ingest-Ergebnissen vor ({neu[s.sid].herkunft}, {name})")
                    neu[s.sid] = s
    if not basis and not neu:
        sys.exit("FEHLER: keine Studien gefunden (erwartet: LAV-NN_ingest.zip oder Library-Paket)")

    studien = dict(basis)
    for sid, s in neu.items():
        info.append(f"{sid} · {s.titel}: {'ersetzt (neues Ingest-Ergebnis)' if sid in basis else 'neu'} – aus {s.herkunft}")
        studien[sid] = s
    for sid in basis:
        if sid not in neu:
            info.append(f"{sid} · {basis[sid].titel}: übernommen aus {basis_name}")
    for sid in a.entfernen:
        if studien.pop(sid, None):
            info.append(f"{sid}: entfernt")
        else:
            befunde.append(f"--entfernen {sid}: Studie nicht im Paket")
    if basis and not neu and not a.entfernen and not a.freigabe:
        hinweise.append("Nur ein bestehendes Paket, keine neuen Studien: Paket wird neu zusammengesetzt und geprüft")

    # Freigaben
    for fg in a.freigabe:
        if "=" not in fg:
            sys.exit(f"FEHLER: --freigabe erwartet «LAV-NN=Name» oder «*=Name», erhalten: {fg}")
        sid, name = (x.strip() for x in fg.split("=", 1))
        ziele = [s for s in studien.values() if not ist_freigegeben(s.card)] if sid == "*" else \
            [studien[sid]] if sid in studien else []
        if not ziele and sid != "*":
            befunde.append(f"--freigabe {sid}: Studie nicht im Paket")
        for s in ziele:
            s.card = freigeben(s.card, name, datum)
            info.append(f"{s.sid}: Card freigegeben durch {name} · {datum}")
    offen = [sid for sid, s in sorted(studien.items()) if not ist_freigegeben(s.card)]

    # Ausgaben derselben Reihe gegenseitig abgrenzen
    ids = sorted(studien)
    for i, x in enumerate(ids):
        for y in ids[i + 1:]:
            if stamm(studien[x].titel) and stamm(studien[x].titel) == stamm(studien[y].titel):
                for a_, b_ in ((x, y), (y, x)):
                    s = studien[a_]
                    m = re.search(r"^- Nicht verwechseln mit:\s*(.*)$", s.katalog, re.M)
                    if m and b_ in m.group(1):
                        continue
                    ja, jb = (re.findall(r"\b(?:19|20)\d{2}\b", studien[k].titel) for k in (a_, b_))
                    art = "andere" if not (ja and jb) or ja[-1] == jb[-1] else \
                        "spätere" if jb[-1] > ja[-1] else "frühere"
                    zusatz = f"{b_} {studien[b_].titel} ({art} Ausgabe derselben Reihe)"
                    if m:
                        alt = m.group(1).strip()
                        wert = zusatz if alt in ("", "–", "-") else f"{alt}; {zusatz}"
                        s.katalog = s.katalog[:m.start()] + f"- Nicht verwechseln mit: {wert}" + s.katalog[m.end():]
                    else:
                        s.katalog += f"\n- Nicht verwechseln mit: {zusatz}"
                    hinweise.append(f"{a_}: «Nicht verwechseln mit {b_}» ergänzt – Unterschied von Hand präzisieren, "
                                    "falls nötig (z. B. Erhebungsjahr, Methode)")

    # Doppelte Kontrollwörter in Volltexten ersetzen
    alle_texte = "\n".join(s.katalog + s.card + "".join(t for _, t in s.teile) + skill_md for s in studien.values())
    gesehen = {}
    for sid in ids:
        if sid not in studien:
            continue
        s = studien[sid]
        for j, (fn, t) in enumerate(s.teile):
            ll = next((l for l in reversed(t.splitlines()) if l.strip()), "")
            m = END.match(ll.strip())
            if not m:
                continue  # meldet paket.py
            w = m.group(1)
            if w in gesehen:
                while True:
                    nw = f"{secrets.choice(WORDS)}-{secrets.randbelow(90) + 10}"
                    if nw not in gesehen and nw not in alle_texte:
                        break
                s.teile[j] = (fn, t[: t.rfind(ll)] + ll.replace(w, nw) + t[t.rfind(ll) + len(ll):])
                info.append(f"{sid}/{fn}: Kontrollwort {w} war schon in {gesehen[w]} vergeben → {nw}")
                w = nw
            gesehen[w] = f"{sid}/{fn}"

    # Paket zusammensetzen
    out = arbeits / "lav-learning-library"
    ref = out / "references"
    (ref / "volltext").mkdir(parents=True)
    (out / "scripts").mkdir()
    (out / "SKILL.md").write_text(skill_md, encoding="utf-8")
    for w in werkzeuge:
        shutil.copy(w, out / "scripts" / w.name)
    for sid in sorted(studien):
        (ref / "volltext" / sid).mkdir()
        for fn, t in studien[sid].teile:
            (ref / "volltext" / sid / fn).write_text(t, encoding="utf-8")

    n = len(studien)
    kat_e = [studien[s].katalog for s in sorted(studien)]
    kopf_k = KAT_KOPF.format(datum=datum, anzahl=n, version=version, datei=" · Datei 9 von 9")
    grp = verteilen(kat_e, len(kopf_k.encode()), 80, a.max)
    for i, g in enumerate(grp, 1):
        d = f" · Datei {i} von {len(grp)}" if len(grp) > 1 else ""
        fname = "00-katalog.md" if len(grp) == 1 else f"00-katalog-{i}.md"
        fuss = f"— Ende Katalog{' Datei ' + str(i) + ' von ' + str(len(grp)) if len(grp) > 1 else ''} · Kontrollwort: NEU-{i:02d} —\n"
        (ref / fname).write_text(KAT_KOPF.format(datum=datum, anzahl=n, version=version, datei=d)
                                 + "\n\n".join(g) + "\n\n" + fuss, encoding="utf-8")
    card_e = [studien[s].card for s in sorted(studien)]
    kopf_c = CARD_KOPF.format(datum=datum, anzahl=n, i=9, k=9)
    cgrp = verteilen(card_e, len(kopf_c.encode()), 90, a.max)
    for i, g in enumerate(cgrp, 1):
        fname = "01-study-cards.md" if len(cgrp) == 1 else f"01-study-cards-{i}.md"
        fuss = f"— Ende Study Cards Datei {i} von {len(cgrp)} · Kontrollwort: NEU-{50 + i:02d} —\n"
        (ref / fname).write_text(CARD_KOPF.format(datum=datum, anzahl=n, i=i, k=len(cgrp))
                                 + "\n\n".join(g) + "\n\n" + fuss, encoding="utf-8")
    info.append(f"Katalog: {len(grp)} Datei(en) · Study Cards: {len(cgrp)} Datei(en) · SKILL.md Version {version}")

    # Bericht vor der Prüfung
    print(f"Paket bauen · {datum} · {n} Studien")
    print("\n".join(info))
    for h in hinweise:
        print("HINWEIS: " + h)
    if offen:
        print(f"NICHT FREIGEGEBEN: {', '.join(offen)} – nur als Testpaket verwenden, bis Research die Cards freigibt "
              "(«Paket bauen, Freigabe LAV-NN durch <Name>»)")
    for b in befunde:
        print("BEFUND: " + b)

    # Prüfen und schreiben (paket.py)
    print("\n--- Prüfung (paket.py) ---")
    p = subprocess.run([sys.executable, "-X", "utf8", str(HERE / "paket.py"), str(out), "--max", str(a.max), "--erneuern",
                        "--ausgabe", str(pathlib.Path(a.ausgabe).resolve()), "--csv", str(pathlib.Path(a.csv).resolve())],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(p.stdout.strip())
    if p.stderr.strip():
        print(p.stderr.strip()[-1500:])
    shutil.rmtree(arbeits, ignore_errors=True)
    ok = p.returncode == 0 and not befunde
    print("\nERGEBNIS: " + ("Paket ohne Befunde" + (" (Testpaket: Freigaben ausstehend)" if offen else "")
                            if ok else "Befunde vorhanden – Paket nicht verwenden"))
    return 0 if ok else (2 if p.returncode == 2 else 1)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        print(f"FEHLER: {type(e).__name__}: {e}")
        sys.exit(2)
```

## belege.py

```python
"""LAV Learning Library – Belegprüfung von Agentenantworten.

Aufruf:
  python scripts/belege.py <antworten.csv | antwort.md | antwort.txt>
                          [--spalte "Antwort Agent"] [--id-spalte id] [--paket <ordner>]
                          [--ausgabe belegpruefung.csv]

Prüft jede Zahl einer Antwort gegen die zitierte PDF-Seite im Volltext dieses Skills
(references/volltext/LAV-XX/teil-NN.md, Seitenmarker [[Seite n/N …]]).
Ein Beleg [LAV-XX, S. n] gilt für den Absatz, den Listenpunkt oder die Tabellenzeile, in dem er steht.
Hat eine Tabelle oder Liste keinen eigenen Beleg, gilt der Beleg des Absatzes direkt davor, ersatzweise der des
Absatzes direkt danach (Spalte beleg_aus: Zeile / Block / Absatz davor / Absatz danach).

Status je Zahl:
  gefunden                     – Zahl steht auf einer der zitierten Seiten
  nicht gefunden               – Zahl steht auf keiner zitierten Seite: Beleg oder Zahl falsch
  berechnet – Rechnung prüfen  – nicht auf der Seite, aber als «berechnet» gekennzeichnet
  in Aussage «nicht belegt»    – Zahl steht in einer Aussage, die einen fehlenden Beleg meldet
  keine Seitenangabe           – Zahl ohne Beleg (nicht prüfbar)
Jahreszahlen in Studientiteln (laut Katalog), Kontrollwörter, Datumsangaben und Aufzählungsnummern
werden nicht geprüft.

Grenzen: Das Skript prüft, ob die Zahl auf der zitierten Seite steht, nicht ob sie dort zur richtigen
Zeile, Gruppe oder Ausgabe gehört. Steht eine falsche Zahl zufällig auch auf der Seite (z. B. 18 statt 19,
wenn 18 in einer anderen Tabellenzeile vorkommt), fällt sie nicht auf. Richtung, Population und Ursache-Aussagen beurteilen Menschen.
Exit-Code 0 = keine Zahl «nicht gefunden», 1 = mindestens eine, 2 = Fehler.
"""
import argparse
import csv
import pathlib
import re
import sys

MARKER = re.compile(r"^\[\[Seite (\d+)/\d+[^\]]*\]\]\s*$", re.M)
CITE = re.compile(r"\[(LAV-[\w-]+),\s*S\.\s*([^\]]+)\]")
NUM = re.compile(r"(?<![\w.,’'])\d{1,3}(?:[’'](?:\d{3}))+(?:[.,]\d+)?(?![\d])|(?<![\w.,’'])\d+(?:[.,]\d+)?(?![\d])")
KONTROLLWORT = re.compile(r"\b[A-ZÄÖÜ]{3,}-\d{2}\b")
DATUM = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
FEHLT = re.compile(r"nicht (?:eindeutig )?belegt|nicht eindeutig|nicht ablesbar|nicht enthalten|keine Angabe", re.I)


def norm(x):
    return x.replace("’", "").replace("'", "").replace(",", ".")


def seiten_lesen(paket):
    """{(Studie, Seite): normalisierter Seitentext}."""
    out = {}
    for sd in sorted((paket / "references" / "volltext").glob("LAV-*")):
        for f in sorted(sd.glob("teil-*.md")):
            t = f.read_text(encoding="utf-8")
            ms = list(MARKER.finditer(t))
            for i, m in enumerate(ms):
                text = t[m.end(): ms[i + 1].start() if i + 1 < len(ms) else len(t)]
                text = re.sub(r"(?<=\d)[’'   ](?=\d{3}\b)", "", text)
                out[(sd.name, int(m.group(1)))] = text.replace(",", ".")
    return out


def titel_lesen(paket):
    """Studientitel aus dem Katalog; Jahreszahlen in Titeln werden nicht als Befund geprüft."""
    titel = set()
    for f in (paket / "references").glob("00-katalog*.md"):
        for m in re.finditer(r"^## LAV-[\w-]+\s*·\s*(.+?)\s*$", f.read_text(encoding="utf-8"), re.M):
            t = m.group(1).strip()
            titel.add(t)
            titel.add(re.sub(r"^Helsana-", "", t))
    return sorted(titel, key=len, reverse=True)


def seitenliste(spec):
    spec = re.sub(r"\(.*?\)", "", spec)  # «(Druckseiten 20–21)» gehört nicht zur PDF-Seite
    pages = []
    for teil in re.split(r"[,;]", spec):
        m = re.match(r"\s*(\d+)\s*(?:[–-]\s*(\d+))?\s*$", teil)
        if m:
            a, b = int(m.group(1)), int(m.group(2) or m.group(1))
            pages.extend(range(a, b + 1) if b >= a and b - a < 40 else [a])
    return pages


def belege_in(text):
    return [(m.group(1), p) for m in CITE.finditer(text) for p in seitenliste(m.group(2))]


def bloecke(antwort):
    """Teilt die Antwort in Blöcke: Absätze, Listen, Tabellen (Tabellenzeilen einzeln mit Tabellenbezug)."""
    teile = antwort.split("\n")
    # Abschlusszeilen («---», «Gelesen:», «Nicht belegt:») gehören nicht zur fachlichen Antwort
    for i in range(len(teile) - 1, -1, -1):
        if teile[i].strip() == "---" and any(l.startswith("Gelesen:") for l in teile[i:]):
            teile = teile[:i]
            break
    roh, cur = [], []
    for l in teile:
        if not l.strip():
            if cur:
                roh.append(cur)
                cur = []
            continue
        # Wechsel zwischen Tabelle und Text beginnt einen neuen Block
        if cur and (l.lstrip().startswith("|") != cur[-1].lstrip().startswith("|")):
            roh.append(cur)
            cur = []
        cur.append(l)
    if cur:
        roh.append(cur)
    return roh


def pruefe_antwort(aid, antwort, seiten, titel=()):
    rows = []
    vorher = []  # Belege des vorangehenden Text-Blocks (für Tabellen/Listen ohne eigenen Beleg)
    bl = bloecke(antwort)
    for bi, blk in enumerate(bl):
        ist_tabelle = blk[0].lstrip().startswith("|")
        ist_liste = all(re.match(r"\s*([-*•]|\d+\.)\s", l) for l in blk)
        blk_text = "\n".join(blk)
        blk_belege = belege_in(blk_text)
        erben = blk_belege or ((ist_tabelle or ist_liste) and vorher)
        danach = "\n".join(bl[bi + 1]) if bi + 1 < len(bl) else ""
        # Ersatz: Tabelle/Liste ohne Beleg und ohne Beleg davor -> Beleg des direkt folgenden Absatzes
        nachher = belege_in(danach) if (ist_tabelle or ist_liste) and not blk_belege and not vorher else []
        berechnet_blk = "berechnet" in blk_text.lower() or (ist_tabelle and "berechnet" in danach.lower()[:300])
        for zeile in blk:
            if ist_tabelle and set(zeile.strip()) <= set("|-: "):
                continue
            z_belege = belege_in(zeile) if ist_tabelle else []
            belege = z_belege or blk_belege or (vorher if erben else []) or nachher
            herkunft = ("Zeile" if z_belege else "Block" if blk_belege else "Absatz davor" if erben and vorher
                        else "Absatz danach" if nachher else "")
            text = CITE.sub(" ", zeile)
            for t in titel:
                text = text.replace(t, " ")
            text = KONTROLLWORT.sub(" ", DATUM.sub(" ", text))
            fehlt = bool(FEHLT.search(text))
            text = re.sub(r"^\s*#+\s*\d+\.\s*", " ", text)          # «## 1. Titel»
            text = re.sub(r"^\s*\d+\.\s+", " ", text)                # «1. Punkt»
            text = text.replace("**", "")
            for m in NUM.finditer(text):
                zahl = norm(m.group())
                if not belege:
                    status = "keine Seitenangabe"
                else:
                    hit = any(re.search(r"(?<![\d.])" + re.escape(zahl) + r"(?![\d])", seiten.get(b, "")) for b in belege)
                    if hit:
                        status = "gefunden"
                    elif fehlt:
                        status = "in Aussage «nicht belegt»"
                    elif berechnet_blk or "berechnet" in zeile.lower():
                        status = "berechnet – Rechnung prüfen"
                    else:
                        status = "nicht gefunden"
                ctx = re.sub(r"\s+", " ", text[max(0, m.start() - 40): m.end() + 30]).strip()
                rows.append({"id": aid, "zahl": zahl, "status": status, "beleg_aus": herkunft,
                             "seiten": "; ".join(f"{s} S. {p}" for s, p in dict.fromkeys(belege)),
                             "kontext": ctx})
        if not ist_tabelle and not ist_liste:
            vorher = blk_belege
        elif blk_belege:
            vorher = blk_belege
    return rows


def antworten_lesen(pfad, spalte, id_spalte):
    if pfad.suffix.lower() != ".csv":
        return [(pfad.stem, pfad.read_text(encoding="utf-8-sig"))]
    roh = pfad.read_text(encoding="utf-8-sig")
    kopf = roh.splitlines()[0] if roh else ""
    trenner = max(";,\t", key=kopf.count)  # Trennzeichen aus der Kopfzeile, Antworttexte enthalten Kommas
    rows = list(csv.DictReader(roh.splitlines(keepends=True), delimiter=trenner))
    if not rows:
        return []
    felder = list(rows[0].keys())
    sp = spalte or next((f for f in felder if f and "antwort" in f.lower() and "soll" not in f.lower()), felder[-1])
    ids = id_spalte if id_spalte in felder else felder[0]
    return [(r.get(ids) or str(i + 1), r.get(sp) or "") for i, r in enumerate(rows)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("eingabe")
    ap.add_argument("--spalte", help="Spalte mit den Antworten (Standard: Spalte mit «Antwort» im Namen, sonst die letzte)")
    ap.add_argument("--id-spalte", default="id")
    ap.add_argument("--paket", help="Ordner der Library-Skill (Standard: Ordner über scripts/)")
    ap.add_argument("--ausgabe", default="belegpruefung.csv")
    a = ap.parse_args()

    paket = pathlib.Path(a.paket) if a.paket else pathlib.Path(__file__).resolve().parent.parent
    seiten = seiten_lesen(paket)
    titel = titel_lesen(paket)
    if not seiten:
        sys.exit(f"FEHLER: keine Volltexte unter {paket}/references/volltext gefunden")
    alle = []
    for aid, text in antworten_lesen(pathlib.Path(a.eingabe), a.spalte, a.id_spalte):
        alle += pruefe_antwort(aid, text, seiten, titel)

    with open(a.ausgabe, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["id", "zahl", "status", "beleg_aus", "seiten", "kontext"], delimiter=";")
        w.writeheader()
        w.writerows(alle)

    stati = ["gefunden", "nicht gefunden", "berechnet – Rechnung prüfen", "in Aussage «nicht belegt»", "keine Seitenangabe"]
    print(f"Belegprüfung: {a.eingabe} · Paket: {paket}")
    print(f"Zahlen geprüft: {len(alle)} · " + " · ".join(f"{s}: {sum(r['status'] == s for r in alle)}" for s in stati))
    probleme = [r for r in alle if r["status"] != "gefunden"]
    for r in probleme:
        print(f"  {r['id']}: {r['zahl']} → {r['status']} ({r['seiten'] or 'kein Beleg'}) · «{r['kontext'][:70]}»")
    print(f"Ergebnisliste: {a.ausgabe}")
    return 1 if any(r["status"] == "nicht gefunden" for r in alle) else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        print(f"FEHLER: {type(e).__name__}: {e}")
        sys.exit(2)
```

## wiki.py

```python
"""LAV Ingest – Wiki-Seiten aus dem geprüften Library-Paket erzeugen.

Aufruf:
  python wiki.py <lav-learning-library.zip | ordner> <zielordner> [--agent-link URL] [--hinweis "Vertraulich – …"]

Erzeugt aus references/00-katalog*.md und references/01-study-cards*.md:
  index.md      Übersicht aller Studien (Tabelle mit Links)
  LAV-XX.md     eine Seite je Studie: Angaben aus dem Katalog + Study Card
Regeln: Inhalte werden nicht verändert, nur umgestellt. Kontrollwort- und Schlusszeilen entfallen;
interne Angaben (Volltext-Teile, Spalte «Teil» im Wegweiser) entfallen; «Wegweiser im Volltext» heisst im Wiki
«Wegweiser (Seiten der PDF)». Ist «Original» ein Link, werden Seitenangaben [S. n] zu Links auf die PDF-Seite
(#page=n). Verweise auf andere Studien werden nur verlinkt, wenn deren Seite existiert.
Exit-Code 0 = ok, 1 = Befunde (z. B. Card fehlt), 2 = Fehler.
"""
import argparse
import pathlib
import re
import sys
import tempfile
import zipfile

END = re.compile(r"^— .*(Kontrollwort|Ende Card).*—\s*$")
ENTRY = re.compile(r"^## (LAV-[\w-]+) · (.+)$", re.M)


def load_root(src, tmp):
    p = pathlib.Path(src)
    if p.is_file():
        with zipfile.ZipFile(p) as z:
            for info in z.infolist():
                target = (pathlib.Path(tmp) / info.filename).resolve()
                if not str(target).startswith(str(pathlib.Path(tmp).resolve())):
                    sys.exit(f"FEHLER: unzulässiger Pfad im ZIP: {info.filename}")
            z.extractall(tmp)
        p = pathlib.Path(tmp)
    skills = list(p.glob("SKILL.md")) + list(p.glob("*/SKILL.md"))
    if len(skills) != 1:
        sys.exit("FEHLER: Paket ohne eindeutige SKILL.md")
    return skills[0].parent


def blocks(text):
    """{ID: (Kurztitel, Blocktext ohne Überschrift)} für alle «## LAV-…»-Abschnitte."""
    out = {}
    marks = list(ENTRY.finditer(text))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        body = text[m.end():end]
        body = "\n".join(l for l in body.splitlines() if not END.match(l.strip()))
        out[m.group(1)] = (m.group(2).strip(), body.strip())
    return out


def fields(body):
    f = {}
    for line in body.splitlines():
        m = re.match(r"^- ([^:]+):\s*(.*)$", line.strip())
        if m:
            f[m.group(1).strip()] = m.group(2).strip()
    return f


def page_links(text, url):
    """[S. n], [S. n–m] und [S. 2, S. 10] werden zu Links auf die PDF-Seite (#page=n)."""
    if not url:
        return text

    def link(ref):
        m = re.match(r"S\. (\d+)(?:–(\d+))?$", ref.strip())
        return f"[{ref.strip()}]({url}#page={m.group(1)})" if m else ref

    def group(m):
        return ", ".join(link(r) for r in m.group(1).split(","))

    return re.sub(r"\[(S\. \d+(?:–\d+)?(?:, S\. \d+(?:–\d+)?)*)\]", group, text)


def drop_part_column(card):
    """Wegweiser-Tabelle: Spalte «Teil» entfernen (für Menschen ohne Bedeutung)."""
    out, in_table, idx = [], False, None
    for line in card.splitlines():
        if line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not in_table:
                in_table = True
                idx = cells.index("Teil") if "Teil" in cells else None
            if idx is not None and idx < len(cells):
                cells.pop(idx)
            out.append("| " + " | ".join(cells) + " |")
        else:
            in_table = False
            idx = None
            out.append(line)
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("quelle")
    ap.add_argument("ziel")
    ap.add_argument("--agent-link", default="")
    ap.add_argument("--hinweis", default="", help="Hinweis oben auf jeder Seite, z. B. Klassifizierung und Nutzerkreis")
    a = ap.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        root = load_root(a.quelle, tmp)
        ref = root / "references"
        kat_text = "\n".join(f.read_text(encoding="utf-8") for f in sorted(ref.glob("00-katalog*.md")))
        card_text = "\n".join(f.read_text(encoding="utf-8") for f in sorted(ref.glob("01-study-cards*.md")))
    stand = re.search(r"^Stand:\s*(.+)$", kat_text, re.M)
    kat, cards = blocks(kat_text), blocks(card_text)
    out = pathlib.Path(a.ziel)
    out.mkdir(parents=True, exist_ok=True)
    befunde = []
    agent = f"\n**Fragen an die Library:** [LAV Learning Library Agent]({a.agent_link})\n" if a.agent_link else ""
    banner = f"> {a.hinweis}\n\n" if a.hinweis else ""

    rows = []
    for sid, (titel, body) in sorted(kat.items()):
        f = fields(body)
        url = f.get("Original", "")
        url = url if re.match(r"^https?://", url) else ""
        meta = []
        for key in ("Volltitel", "Typ / Umfang", "Herausgeber / Jahr", "Methode / Stichprobe", "Themen",
                    "Auch genannt", "Nicht verwechseln mit"):
            if f.get(key):
                val = (re.sub(r"(LAV-[\w-]+)", lambda m: f"[{m.group(1)}]({m.group(1)}.md)" if m.group(1) in kat else m.group(1), f[key])
                       if key == "Nicht verwechseln mit" else f[key])
                meta.append(f"| {key} | {val} |")
        meta.append(f"| Original | {'[PDF öffnen](' + url + ')' if url else f.get('Original', '–')} |")
        if sid in cards:
            card = cards[sid][1]
            card = page_links(drop_part_column(card), url).replace("**Wegweiser im Volltext:**", "**Wegweiser (Seiten der PDF):**")
        else:
            card = "_Für diese Studie liegt noch keine freigegebene Study Card vor._"
            befunde.append(f"{sid}: Card fehlt")
        page = (f"{banner}# {sid} · {titel}\n{agent}\n| Angabe | Inhalt |\n|---|---|\n" + "\n".join(meta) +
                f"\n\n## Study Card\n\n{card}\n\n---\n\nSeitenangaben [S. n] beziehen sich auf die PDF-Seiten des "
                f"Originals. Quelle der Inhalte: geprüftes Paket der LAV Learning Library"
                f"{' (Stand ' + stand.group(1).strip() + ')' if stand else ''}.\n")
        if "Kontrollwort" in page:
            befunde.append(f"{sid}: Kontrollwort im Seitentext – Seite nicht geschrieben")
            continue
        (out / f"{sid}.md").write_text(page, encoding="utf-8")
        rows.append(f"| [{sid}]({sid}.md) | {titel} | {f.get('Herausgeber / Jahr', '')} | "
                    f"{f.get('Methode / Stichprobe', '')} | {f.get('Themen', '')} |")
    for sid in cards:
        if sid not in kat:
            befunde.append(f"{sid}: Card ohne Katalog-Eintrag")
    index = (banner + "# LAV Learning Library – Studienübersicht\n\n" +
             (f"Stand: {stand.group(1).strip()}\n" if stand else "") + agent +
             "\n| ID | Studie | Herausgeber / Jahr | Methode / Stichprobe | Themen |\n|---|---|---|---|---|\n" +
             "\n".join(rows) + "\n")
    (out / "index.md").write_text(index, encoding="utf-8")
    print(f"Wiki: {len(rows)} Studienseiten + index.md in {out}")
    for b in befunde:
        print("BEFUND:", b)
    return 1 if befunde else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        print(f"FEHLER: {type(e).__name__}: {e}")
        sys.exit(2)
```
