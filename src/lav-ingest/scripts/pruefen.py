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
