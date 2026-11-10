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
