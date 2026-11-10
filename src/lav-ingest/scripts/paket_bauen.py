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
