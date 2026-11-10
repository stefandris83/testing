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
