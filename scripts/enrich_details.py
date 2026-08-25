# -*- coding: utf-8 -*-
"""Vult vacatures aan met kerngegevens en een citaat van het kantoor zelf.

Het resultaat wordt in jobs.html opgeslagen, bij de vacature zelf. Zo hoeft
het bouwen van de pagina's niets op te halen en blijft de uitkomst gelijk als
je opnieuw bouwt. Alleen vacatures die het nog niet hebben worden opgehaald,
dus een wekelijkse run raakt vrijwel alleen de nieuwe.

Met --refresh wordt alles opnieuw opgehaald. Dat is nodig als een kantoor zijn
vacaturetekst herschrijft; dat merken we hier verder niet.
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ats_detail

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS = os.path.join(BASE, "jobs.html")


def main(refresh=False):
    html = open(JOBS, encoding="utf-8").read()
    m = re.search(r'(<script id="jobs-data" type="application/json">)([\s\S]*?)(</script>)', html)
    jobs = json.loads(m.group(2))

    def leeg(j):
        d = j.get("detail") or {}
        return not d.get("quote") and not d.get("atsFacts")

    actief = [j for j in jobs if j.get("active") is not False and j.get("url")]
    # Ook opnieuw proberen bij vacatures waar niets uit kwam. Een lege uitkomst
    # betekent meestal dat het kantoor het verzoek weigerde, niet dat er niets
    # te halen valt.
    todo = [j for j in actief if refresh or "quote" not in (j.get("detail") or {}) or leeg(j)]
    print(f"{len(actief)} actieve vacatures, {len(todo)} op te halen")
    if not todo:
        return 0

    res = ats_detail.enrich(todo, log=print)

    behouden = 0
    for j in jobs:
        r = res.get(j.get("id"))
        if r is None:
            continue
        d = j.setdefault("detail", {})
        if not r["quote"] and not r["facts"] and (d.get("quote") or d.get("atsFacts")):
            # Niets teruggekregen terwijl er al iets stond. Dat is een mislukte
            # poging, geen lege vacature: laten staan wat er is.
            behouden += 1
            continue
        d["quote"] = r["quote"]
        d["quoteLang"] = r["lang"] or ""
        d["atsFacts"] = r["facts"]
        # Een adres uit de bron is per vacature juist. Alleen overschrijven als
        # er werkelijk een is; anders blijft staan wat er stond.
        if r.get("address"):
            d["address"] = r["address"]

    met_citaat = sum(1 for j in jobs if (j.get("detail") or {}).get("quote"))
    met_feiten = sum(1 for j in jobs if (j.get("detail") or {}).get("atsFacts"))
    if behouden:
        print(f"\n{behouden} vacatures kregen niets terug; bestaande gegevens behouden")

    open(JOBS, "w", encoding="utf-8").write(
        html[:m.start()] + m.group(1) + "\n" + json.dumps(jobs, ensure_ascii=False, indent=2)
        + "\n" + m.group(3) + html[m.end():])
    print(f"\nopgeslagen: {met_citaat} met citaat, {met_feiten} met kerngegevens")
    return 0


if __name__ == "__main__":
    sys.exit(main("--refresh" in sys.argv))
