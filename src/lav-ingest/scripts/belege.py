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
