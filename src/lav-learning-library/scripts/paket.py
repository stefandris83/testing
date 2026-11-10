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
