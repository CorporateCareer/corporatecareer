# -*- coding: utf-8 -*-
"""Haalt vacatureomschrijvingen op bij sites die ze pas in de browser opbouwen.

De meeste wervingssystemen leveren hun tekst gewoon mee: Recruitee, Greenhouse,
SmartRecruiters en Workday hebben allemaal een JSON-adres. SuccessFactors niet.
Daar staat de omschrijving niet in de HTML, ook niet verstopt in een script; ze
wordt pas in de browser opgebouwd. Een toestemmingscookie meesturen helpt niet.

Bij EY komt daar nog bij dat een rechtstreekse vacature-URL op een foutpagina
eindigt, ook met een geldige sessie. De tekst komt alleen binnen als je vanaf de
zoekpagina doorklikt, zoals een bezoeker dat doet. Vandaar dat dit script per
vacature klikt en teruggaat in plaats van de URL's los op te vragen.

Dit is bewust een apart script en geen onderdeel van ats_detail: het vraagt een
browser, het is trager, en het leunt op de opmaak van een specifieke site. Valt
het om, dan verliezen we alleen het citaat bij deze kantoren; de vacatures zelf
blijven gewoon staan, want die komen uit source_ats.

Gebruik:
    python scripts/render_detail.py            alleen wat nog geen tekst heeft
    python scripts/render_detail.py --refresh   alles opnieuw
"""
import json, os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS = os.path.join(BASE, "jobs.html")

# Per kantoor: de zoekpagina om vanaf te klikken, en hoe de vacaturerijen heten.
SITES = [
    {"naam": "EY Netherlands",
     "zoek": "https://careers.ey.com/ey/search/?q=&locationsearch=Netherlands",
     "rij": "a.jobTitle-link", "cookie": "#cookie-accept", "per_pagina": 25},
    {"naam": "EY-Parthenon",
     "zoek": "https://careers.ey.com/ey/search/?q=&locationsearch=Netherlands",
     "rij": "a.jobTitle-link", "cookie": "#cookie-accept", "per_pagina": 25},
    {"naam": "Dentons",
     "zoek": "https://careers.dentons.com/go/Opportunities-in-the-Netherlands/8677902/",
     "rij": "a.jobTitle-link", "cookie": "#cookie-accept", "per_pagina": 10},
]

# SuccessFactors zet de omschrijving in een eigen element. Dat uitlezen is veel
# betrouwbaarder dan de paginatekst afbakenen op koppen: "Apply now" staat bij
# Dentons boven de omschrijving in plaats van eronder, dus daarop knippen liet
# 42 woorden navigatie over in plaats van de 442 woorden tekst.
OMSCHRIJVING = (".jobdescription", "[itemprop='description']", ".job-description")


def chromium(p):
    """De browser starten met het pad dat deze omgeving meelevert."""
    pad = None
    for kand in ("/opt/pw-browsers/chromium-1194/chrome-linux/chrome",):
        if os.path.exists(kand):
            pad = kand
            break
    args = ["--no-sandbox"]
    # De uitgaande verbinding loopt hier via een proxy met een eigen CA. Chromium
    # leest die niet uit de systeemopslag, dus we vertrouwen precies dat ene
    # certificaat, niet alle. In GitHub Actions bestaat die proxy niet en blijft
    # deze lijst leeg, dus dan geldt gewoon de normale controle.
    spki = os.environ.get("CC_PROXY_SPKI")
    if spki:
        args.append(f"--ignore-certificate-errors-spki-list={spki}")
    return p.chromium.launch(executable_path=pad, args=args) if pad else p.chromium.launch(args=args)


def omschrijving_van(pg):
    """De omschrijving uit de pagina halen, of een lege tekst."""
    for sel in OMSCHRIJVING:
        try:
            if pg.locator(sel).count():
                txt = pg.locator(sel).first.inner_text()
                regels = [r.strip() for r in txt.splitlines()]
                return "\n".join(r for r in regels if r)
        except Exception:
            continue
    return ""


def haal_site(pg, site, wil, log):
    """Klikt op de zoekpagina elke vacature aan die we willen en leest de tekst."""
    uit = {}
    pg.goto(site["zoek"], wait_until="domcontentloaded", timeout=45000)
    pg.wait_for_timeout(1500)
    try:
        pg.locator(site["cookie"]).first.click(timeout=4000)
        pg.wait_for_timeout(2000)
    except Exception:
        pass

    start = 0
    while True:
        if start:
            pg.goto(f"{site['zoek']}{'&' if '?' in site['zoek'] else '?'}startrow={start}",
                    wait_until="domcontentloaded", timeout=45000)
            pg.wait_for_timeout(1500)
        aantal = pg.locator(site["rij"]).count()
        if not aantal:
            break
        for i in range(aantal):
            try:
                link = pg.locator(site["rij"]).nth(i)
                href = link.get_attribute("href") or ""
                url = href if href.startswith("http") else f"https://{site['zoek'].split('/')[2]}{href}"
                if url not in wil or url in uit:
                    continue
                link.click(timeout=10000)
                pg.wait_for_load_state("domcontentloaded", timeout=30000)
                pg.wait_for_timeout(1800)
                if "errorpage" not in pg.url:
                    tekst = omschrijving_van(pg)
                    if len(tekst.split()) > 40:
                        uit[url] = tekst
                pg.go_back(wait_until="domcontentloaded", timeout=30000)
                pg.wait_for_timeout(1200)
            except Exception:
                # Eén vacature die misgaat mag de rest niet meenemen.
                try:
                    pg.goto(site["zoek"] if not start else
                            f"{site['zoek']}{'&' if '?' in site['zoek'] else '?'}startrow={start}",
                            wait_until="domcontentloaded", timeout=30000)
                    pg.wait_for_timeout(1200)
                except Exception:
                    return uit
        if aantal < site["per_pagina"]:
            break
        start += site["per_pagina"]
        if start >= 400:
            break
    log(f"  {site['naam']:22} {len(uit):3} omschrijvingen opgehaald")
    return uit


def _ophalen(wil, sync_playwright):
    gevonden = {}
    with sync_playwright() as p:
        b = chromium(p)
        ctx = b.new_context(user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                                       "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")
        pg = ctx.new_page()
        for site in SITES:
            if site["naam"] not in wil:
                continue
            gevonden.update(haal_site(pg, site, wil[site["naam"]], print))
        b.close()
    return gevonden


def main(refresh=False, alleen=None, verwerk_alleen=False):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright ontbreekt; overgeslagen (de vacatures blijven staan, "
              "alleen zonder citaat)")
        return 0

    html = open(JOBS, encoding="utf-8").read()
    m = re.search(r'(<script id="jobs-data" type="application/json">)([\s\S]*?)(</script>)', html)
    jobs = json.loads(m.group(2))
    namen = {s["naam"] for s in SITES}

    wil = {}
    for j in jobs:
        if j.get("active") is False or j["company"] not in namen:
            continue
        if alleen and j["company"] != alleen:
            continue
        if not refresh and not verwerk_alleen and (j.get("detail") or {}).get("quote"):
            continue
        wil.setdefault(j["company"], set()).add((j.get("url") or "").split("?")[0])
    if not any(wil.values()):
        print("niets op te halen")
        return 0
    for n, v in wil.items():
        print(f"{n}: {len(v)} vacatures zonder tekst")

    gevonden = {}
    if verwerk_alleen:
        print("verwerkstand: bestaande teksten opnieuw tot citaat maken")
    else:
        gevonden = _ophalen(wil, sync_playwright)

    # De opgehaalde tekst door dezelfde citaatbepaling als de andere kantoren.
    # Anders zouden deze pagina's een ander soort citaat krijgen: langer, met
    # kopjes erin, en met het bedrijfsverhaal dat bij elke vacature terugkomt.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import ats_detail as D

    per_kantoor = {}
    for j in jobs:
        tekst = gevonden.get((j.get("url") or "").split("?")[0])
        if not tekst and verwerk_alleen:
            # De ruwe tekst van een eerdere run. Zo kunnen de citaatregels
            # opnieuw worden toegepast zonder alles weer op te halen.
            tekst = (j.get("detail") or {}).get("rendered")
        if tekst:
            j.setdefault("detail", {})["rendered"] = tekst
            per_kantoor.setdefault(j["company"], []).append((j, tekst))

    n = 0
    for kantoor, paren in sorted(per_kantoor.items()):
        telling = {}
        for _, tekst in paren:
            for alinea in set(D.paragraphs(tekst)):
                if len(alinea) >= D.MIN_PARAGRAPH:
                    telling[alinea] = telling.get(alinea, 0) + 1
        standaard = {a for a, k in telling.items() if k > 1} if len(paren) > 1 else set()
        met = 0
        for j, tekst in paren:
            citaat = D.quote_from(tekst, standaard)
            if not citaat:
                continue
            d = j.setdefault("detail", {})
            d["quote"] = citaat
            d["quoteLang"] = D.detect_lang(" ".join(D.paragraphs(tekst))) or ""
            met += 1
            n += 1
        print(f"  {kantoor:22} {met:3} citaten, {len(standaard):3} standaardalinea's")
    open(JOBS, "w", encoding="utf-8").write(
        html[:m.start()] + m.group(1) + "\n" + json.dumps(jobs, ensure_ascii=False, indent=2)
        + "\n" + m.group(3) + html[m.end():])
    print(f"\n{n} vacatures kregen een omschrijving")
    return 0


if __name__ == "__main__":
    alleen = None
    for a in sys.argv[1:]:
        if a.startswith("--only="):
            alleen = a.split("=", 1)[1]
    sys.exit(main("--refresh" in sys.argv, alleen, "--verwerk" in sys.argv))
