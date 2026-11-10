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
