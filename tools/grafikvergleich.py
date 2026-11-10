"""Vergleicht die Grafiktabellen zweier Transkripte (Ingest-Agent gegen Referenz) Zelle für Zelle.

Aufruf:  python tools/grafikvergleich.py <seitenordner-agent> <seitenordner-referenz>
         (Ordner mit s001.md …, z. B. seiten/ aus LAV-T01_ingest.zip und testdaten/referenz/LAV-T01/seiten)

Unabhängig von der Tabellenausrichtung (Zeilen/Spalten vertauscht). Meldet je Grafik: gleiche Zellen, Abweichung
≤ 1 und > 1 (Prozentpunkte bzw. Einheiten). So entstand der Befund M1 (LAV-T01: 1’325 von 1’328 Zellen gleich).
Nur für öffentliche Teststudien.
"""
import re, sys, pathlib
A, R = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
BLK = re.compile(r"\*\*\[Grafik ([^\]]+)\][^\n]*\n(.*?)\*\*\[Ende Grafik", re.S)
def norm(s):
    s = s.lower().replace("ca.", "").replace("(berechnet)", "").replace("(beschriftet)", "")
    s = re.sub(r"\(.*?\)", "", s)
    s = re.sub(r"[^a-zäöüéèà0-9 ]", " ", s)
    return " ".join(w for w in s.split() if w not in ("berechnet", "beschriftet", "antwort", "jahr", "in", "prozent"))
def num(c):
    c = c.replace("’", "").replace("'", "").strip()
    m = re.search(r"-?\d+(?:[.,]\d+)?", c)
    return float(m.group().replace(",", ".")) if m else None
def tables(block):
    out, cur = [], []
    for l in block.splitlines():
        if l.startswith("|"):
            cur.append([c.strip() for c in l.strip().strip("|").split("|")])
        elif cur:
            out.append(cur); cur = []
    if cur: out.append(cur)
    return out
def cells(block):
    d = {}
    for t in tables(block):
        if len(t) < 3: continue
        head = t[0]; rows = [r for r in t[2:] if len(r) == len(head)]
        for r in rows:
            for j in range(1, len(head)):
                v = num(r[j])
                if v is None: continue
                k = frozenset([norm(r[0]), norm(head[j])])
                d[k] = v
    return d
tot = same = near = 0; far = []
for fa in sorted(A.glob("s*.md")):
    fr = R / fa.name
    if not fr.exists(): continue
    ga = {m.group(1).strip(): m.group(2) for m in BLK.finditer(fa.read_text(encoding="utf-8"))}
    gr = {m.group(1).strip(): m.group(2) for m in BLK.finditer(fr.read_text(encoding="utf-8"))}
    for g in sorted(set(ga) & set(gr), key=lambda x: (len(x), x)):
        ca, cr = cells(ga[g]), cells(gr[g])
        common = set(ca) & set(cr)
        if not common: 
            print(f"{fa.name} Grafik {g}: keine gemeinsamen Zellen (Agent {len(ca)}, Ref {len(cr)})"); continue
        diffs = [(k, ca[k], cr[k]) for k in common]
        s = sum(1 for _, a, r in diffs if a == r); n1 = sum(1 for _, a, r in diffs if 0 < abs(a - r) <= 1)
        bad = [(sorted(k), a, r) for k, a, r in diffs if abs(a - r) > 1]
        tot += len(diffs); same += s; near += n1; far += [(fa.name, g, *b) for b in bad]
        print(f"{fa.name} Grafik {g}: {len(diffs)} Zellen verglichen · gleich {s} · ±1 {n1} · grösser {len(bad)} · nur Agent {len(set(ca)-set(cr))} · nur Ref {len(set(cr)-set(ca))}")
print(f"\nGESAMT: {tot} Zellen · gleich {same} ({same/max(tot,1):.0%}) · Abweichung ≤ 1 {near} · Abweichung > 1: {len(far)}")
for x in far[:25]: print("  >1:", x)
