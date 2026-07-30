# -*- coding: utf-8 -*-
"""Zet het jaartal in de copyrightregel op het huidige jaar.

De footer staat in elke pagina ingebakken, er is geen sjabloon dat op het
moment van bezoek wordt samengesteld. Zonder deze stap blijft er dus een oud
jaartal staan zodra de jaarwisseling voorbij is. De wekelijkse
vacaturecontrole draait dit mee, zodat het zichzelf in de eerste week van
januari rechtzet.

De regel staat op twee plekken: ingebakken in de pagina's zelf, en als
vertaalsleutel footer.copy in de woordenlijst. Die tweede telt net zo zwaar,
want gen_en.bake() schrijft de waarde uit de woordenlijst terug in de
pagina's. Alleen de HTML bijwerken zou dus bij de volgende build weer
teruggedraaid worden."""
import datetime, glob, os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAT = re.compile(r"(&copy;\s*|©\s*)20\d\d(\s*CorporateCareer)")
EXTRA = ("js/i18n.js", "js/i18n.min.js")


def main():
    year = str(datetime.date.today().year)
    paths = glob.glob(os.path.join(BASE, "**", "*.html"), recursive=True)
    paths += [os.path.join(BASE, p) for p in EXTRA]
    changed = []
    for path in paths:
        if not os.path.exists(path):
            continue
        src = open(path, encoding="utf-8").read()
        out = PAT.sub(lambda m: m.group(1) + year + m.group(2), src)
        if out != src:
            open(path, "w", encoding="utf-8").write(out)
            changed.append(os.path.relpath(path, BASE))
    print(f"sync_year: {len(changed)} bestanden op {year} gezet")
    return 0


if __name__ == "__main__":
    sys.exit(main())
