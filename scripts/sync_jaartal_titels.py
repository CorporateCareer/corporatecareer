# -*- coding: utf-8 -*-
"""Zet het jaartal in de titels en teksten van de landingspagina's bij.

sync_year.py doet alleen de copyrightregel in de footer. De commerciele
landingspagina's dragen het jaartal ook in hun titel, en dat is precies wat
een bezoeker in Google ziet staan: "Investment Banking Nederland, Stage &
Analyst Vacatures 2025" leest in september 2026 als een verlaten site.

Dit script is bewust niet een blinde zoek-en-vervang. Een jaartal in een
lopende tekst kan een terechte verwijzing naar het verleden zijn, en die
ophogen zou een verzonnen cijfer opleveren. Drie soorten gevallen:

    ophogen        koppen, badges en vooruitkijkende zinnen
                   "Big Four Stage Amsterdam 2025" -> 2026
    doorschuiven   seizoensbereiken
                   "Deadlines 2025-2026" -> "Deadlines 2026-2027"
    met rust        gegevens die aan een jaar vastzitten
                   "gemelde stagevergoedingen in 2024-2025"
                   "in 2025 moet een kennismigrant minimaal EUR 38.274 verdienen"

Die laatste twee staan in BESCHERMD. Wil je die toch bijwerken, zoek dan eerst
het cijfer voor het nieuwe jaar op; het jaartal alleen verzetten maakt het
cijfer onwaar.

Gebruik:
    python scripts/sync_jaartal_titels.py            van 2025 naar 2026
    python scripts/sync_jaartal_titels.py --droog     alleen tonen
"""
import os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUD, NIEUW = "2025", "2026"

# Zinsdelen waarin het jaartal aan een gegeven vastzit en dus blijft staan.
BESCHERMD = (
    "in 2025 moet een kennismigrant",
    "stagevergoedingen in 2024-2025",
    "2024-2025",
)

# Seizoensbereiken schuiven een heel jaar op. Het en-streepje gaat er meteen
# uit: de huisstijl schrijft geen gedachtestreepjes, ook niet in een bereik.
BEREIKEN = [
    (re.compile(r"\b2025\s*[-–—]\s*2026\b"), "2026-2027"),
]


def splits_head(html):
    i = html.find("</head>")
    return (html[:i], html[i:]) if i != -1 else ("", html)


def verwerk(html):
    head, body = splits_head(html)
    uit = []
    for deel, is_head in ((head, True), (body, False)):
        for pat, verv in BEREIKEN:
            deel = pat.sub(verv, deel)
        if is_head:
            deel = deel.replace(OUD, NIEUW)
        else:
            # In de body eerst de beschermde zinsdelen wegzetten, dan pas
            # vervangen, dan terugzetten. Anders zou een los "2025" binnen zo'n
            # zin alsnog meegaan.
            bewaar = {}
            for n, stuk in enumerate(BESCHERMD):
                if stuk in deel:
                    sleutel = f"\x00BESCHERMD{n}\x00"
                    bewaar[sleutel] = stuk
                    deel = deel.replace(stuk, sleutel)
            deel = deel.replace(OUD, NIEUW)
            for sleutel, stuk in bewaar.items():
                deel = deel.replace(sleutel, stuk)
        uit.append(deel)
    return "".join(uit)


def relevant(html):
    """Alleen pagina's die het jaartal in hun titel dragen."""
    head, _ = splits_head(html)
    m = re.search(r"<title>(.*?)</title>", head, re.S)
    return bool(m and OUD in m.group(1))


def main(droog=False):
    geraakt = 0
    totaal = 0
    for dp, dn, fn in os.walk(BASE):
        dn[:] = [d for d in dn if d not in (".git", "node_modules")]
        for f in fn:
            if not f.endswith(".html"):
                continue
            pad = os.path.join(dp, f)
            html = open(pad, encoding="utf-8").read()
            if not relevant(html):
                continue
            nieuw = verwerk(html)
            if nieuw == html:
                continue
            n = html.count(OUD) - nieuw.count(OUD)
            totaal += n
            geraakt += 1
            print(f"  {os.path.relpath(pad, BASE):44} {n:2} keer")
            if not droog:
                open(pad, "w", encoding="utf-8").write(nieuw)
    woord = "zouden wijzigen" if droog else "gewijzigd"
    print(f"\n{geraakt} pagina's {woord}, {totaal} vermeldingen bijgewerkt")
    return 0


if __name__ == "__main__":
    sys.exit(main("--droog" in sys.argv))
