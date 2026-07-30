#!/usr/bin/env python3
"""Haalt actuele vacatures op via de Adzuna-API voor bedrijven zonder eigen
doorzoekbare feed. Alleen eigen-gebrande vacatures (werkgever == het bedrijf),
zonder facilitaire/uitzend-/eventruis. Omschrijvingen zijn eigen, algemene
teksten. Elke vacature krijgt source=adzuna + adzunaKey zodat de dagelijkse
controle ze via de Adzuna-API verifieert. Sleutel via ADZUNA_APP_ID/KEY (env).

De kantorenlijst komt uit de drie bedrijvenhubs op de site zelf, zodat een
nieuw profiel automatisch meeloopt zonder dat dit bestand mee hoeft te
veranderen. Daarnaast staat er een korte lijst handelshuizen die geen
profielpagina hebben maar wel relevant zijn.
"""
import os, re, json, subprocess, unicodedata, html as _H

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS = os.path.join(BASE, "jobs.html")
AID, AK = os.environ.get("ADZUNA_APP_ID"), os.environ.get("ADZUNA_APP_KEY")

# Hub -> sector. De hubs bevatten per bedrijf de slug, de naam en de stad.
HUBS = {
    "finance":    "finance/bedrijven/index.html",
    "consulting": "consulting/bedrijven/index.html",
    "advocatuur": "legal/bedrijven/index.html",
}

# Handelshuizen zonder profielpagina. Commodity trading zit grotendeels bij
# bedrijven die geen kantoor in de klassieke zin zijn, dus die staan hier.
COMMODITY_FIRMS = {
    "Vitol":              "https://www.vitol.com",
    "Trafigura":          "https://www.trafigura.com",
    "Gunvor":             "https://www.gunvorgroup.com",
    "Mercuria":           "https://www.mercuria.com",
    "Glencore":           "https://www.glencore.com",
    "Cargill":            "https://www.cargill.com",
    "Louis Dreyfus Company": "https://www.ldc.com",
    "Bunge":              "https://www.bunge.com",
    "Vattenfall":         "https://www.vattenfall.nl",
    "Eneco":              "https://www.eneco.nl",
    "Shell":              "https://www.shell.nl",
}

# Zoekterm wijkt af van de profielnaam. De term moet voorkomen in de
# werkgeversnaam die Adzuna teruggeeft, anders valt de vacature af.
KEY_OVERRIDE = {
    "De Brauw Blackstone Westbroek": "de brauw",
    "A&O Shearman":                  "shearman",
    "Boston Consulting Group":       "boston consulting",
    "McKinsey & Company":            "mckinsey",
    "Bain & Company":                "bain",
    "PwC Netherlands":               "pwc",
    "KPMG Netherlands":              "kpmg",
    "EY Netherlands":                "ey",
    "Deloitte Netherlands":          "deloitte",
    "NIBC Bank":                     "nibc",
    "Van Doorne":                    "van doorne",
    "Houthoff":                      "houthoff",
    "Loyens & Loeff":                "loyens",
    "Freshfields":                   "freshfields",
    "Clifford Chance":               "clifford chance",
    "Linklaters":                    "linklaters",
    "Baker McKenzie":                "baker mckenzie",
    "Norton Rose Fulbright":         "norton rose",
    "Hogan Lovells":                 "hogan lovells",
    "Stibbe":                        "stibbe",
    "NautaDutilh":                   "nautadutilh",
    "Louis Dreyfus Company":         "louis dreyfus",
}

# Zoekopdrachten die niet aan een werkgever hangen maar aan een onderwerp. De
# vangst wordt alsnog beperkt tot bekende werkgevers, zodat er geen
# uitzendbureaus binnenkomen.
TOPIC_QUERIES = [
    "commodity trading", "commodity trader", "energy trading",
    "oil trading", "power trading", "gas trading", "commodities",
    "afstudeeronderzoek", "afstudeerstage", "afstudeerscriptie",
    "graduation internship", "thesis internship", "master thesis",
]

EXC = ("schoonmaak","cleaning","kok","afwasser","catering","beveilig","security","facilit","vakantiewerk",
       "hospitality","receptie","chauffeur","magazijn","monteur","business course","kennismaking","zomerse",
       "open sollicitatie","event","webinar","insight","recruitment day","meet ","meet&","meet-","schoonmaker")

# Woorden die een titel relevant maken, per sector. Alles wat hier niet in
# staat valt af: liever een vacature missen dan ruis tonen.
_BASE = ("analyst","associate","intern","stage","stagiair","graduate","trainee","traineeship",
         "afstudeer","afstudeerder","scriptie","thesis","werkstudent","junior","starter")
INC = {
 "finance": _BASE + ("trader","trading","quant","banker","investment","finance","financial","risk","controller",
   "portfolio","wealth","advisor","adviseur","credit","research","developer","engineer","actuar","accountant",
   "audit","tax","valuation","deal","corporate","treasury","commodity","commodities","structuring","origination",
   "settlement","middle office","front office","m&a","private equity","asset management"),
 "consulting": _BASE + ("consult","advis","adviseur","architect","strateg","transformation","lead","principal",
   "engagement","expert","technology","digital","engineer","data","operations","implementation"),
 "advocatuur": _BASE + ("advocaat","advocate","lawyer","jurist","juridisch","legal","counsel","notaris","notarieel",
   "kandidaat-notaris","paralegal","legal counsel","attorney","litigation","corporate","m&a","compliance",
   "privacy","arbeidsrecht","ondernemingsrecht","mededinging","fiscaal"),
}

DOES = {
 "finance": {"en":["Work on analyses, models or transactions for the business",
                   "Support decision-making with data and clear recommendations",
                   "Collaborate in teams to deliver results"],
             "nl":["Werk aan analyses, modellen of transacties voor de business",
                   "Ondersteun besluitvorming met data en heldere aanbevelingen",
                   "Werk samen in teams om resultaten te realiseren"]},
 "consulting": {"en":["Advise clients on complex challenges and transformation",
                      "Analyse issues, processes and data to shape recommendations",
                      "Work in project teams to deliver results at the client"],
                "nl":["Adviseer opdrachtgevers over complexe vraagstukken en transformatie",
                      "Analyseer vraagstukken, processen en data om aanbevelingen te onderbouwen",
                      "Werk in projectteams om resultaten bij de opdrachtgever te realiseren"]},
 "advocatuur": {"en":["Work on files together with associates and partners",
                      "Research legal questions and draft memos and documents",
                      "Join client meetings, negotiations or hearings"],
                "nl":["Werk aan dossiers samen met medewerkers en partners",
                      "Onderzoek juridische vragen en stel memo's en stukken op",
                      "Sluit aan bij clientbesprekingen, onderhandelingen of zittingen"]},
}
BRINGS = {"en":["A relevant degree and strong analytical skills",
                "Attention to detail and a structured way of working",
                "Excellent Dutch and/or English"],
          "nl":["Een relevante opleiding en sterke analytische vaardigheden",
                "Oog voor detail en een gestructureerde werkwijze",
                "Uitstekend Nederlands en/of Engels"]}

SECTOR_LABEL = {"finance":("Finance","Finance"), "consulting":("Consulting","Consulting"),
                "advocatuur":("Law","Advocatuur")}


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower())


def curl(url):
    return subprocess.run(["curl", "-sS", "-m", "25", url], capture_output=True, text=True).stdout


def city_of(loc):
    loc = (loc or "").split(",")[0].strip()
    return "Netherlands" if loc.lower() in ("nederland", "netherlands", "") else loc


def _clean(s):
    return _H.unescape(re.sub(r"<[^>]+>", "", s)).strip()


# Automatisch afgeleide metabeschrijvingen ("<naam> in Nederland: wat het werk
# inhoudt, ..."). Die zeggen niets over het kantoor en horen niet als
# omschrijving in een vacature.
_GENERIC = re.compile(r"in (?:Nederland|the Netherlands): (?:wat|what)\b", re.I)


def profile_blurb(slug):
    """Eerste zin van de metabeschrijving van het profiel, per taal. Dat is
    tekst die al op de site staat en dus verdedigbaar is. Alleen echt
    geschreven taglines, geen automatisch afgeleide."""
    out = {}
    for lang, path in (("nl", f"bedrijven/{slug}/index.html"), ("en", f"en/bedrijven/{slug}/index.html")):
        p = os.path.join(BASE, path)
        if not os.path.exists(p):
            continue
        m = re.search(r'<meta name="description" content="([^"]+)"', open(p, encoding="utf-8").read())
        if not m:
            continue
        # De beschrijving eindigt op een wervende zin ("Bekijk stages ..."),
        # die hoort niet in de vacature.
        txt = _H.unescape(m.group(1))
        txt = re.split(r"(?:Bekijk|View|Explore|Browse)\s", txt)[0].strip()
        if txt and not _GENERIC.search(txt):
            out[lang] = txt
    return out or None


def key_matches(key, employer):
    """Op woordgrens vergelijken. Namen als ING, CMS en Sia zijn zo kort dat ze
    als deelwoord in van alles voorkomen: 'ing' zit in Booking, 'sia' in Asia.
    Een losse substring-vergelijking levert dan vacatures op van werkgevers die
    niets met het kantoor te maken hebben."""
    return re.search(r"\b" + re.escape(key) + r"\b", employer or "") is not None


def firms_from_hubs():
    """slug -> dict(name, sector, site, logo). Bedrijven die in meerdere hubs
    staan houden de eerste sector; de volgorde in HUBS bepaalt dat."""
    firms = {}
    for sector, rel in HUBS.items():
        p = os.path.join(BASE, rel)
        if not os.path.exists(p):
            continue
        html = open(p, encoding="utf-8").read()
        for m in re.finditer(r'<a class="bedrijf-card[^"]*" href="/bedrijven/([a-z0-9-]+)/"[\s\S]*?'
                             r'<span class="bedrijf-card-name">([^<]+)</span>', html):
            slug, name = m.group(1), _clean(m.group(2))
            if slug in firms:
                continue
            firms[slug] = {"name": name, "sector": sector,
                           "logo": f"/img/logos/{slug}.svg", "site": ""}
    return firms


def search_key(name):
    k = KEY_OVERRIDE.get(name)
    if k:
        return k
    n = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    n = re.sub(r"\b(netherlands|nederland|group|company|n\.v\.|b\.v\.|nv|bv|advocaten|advocatuur)\b", " ", n)
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9& ]", " ", n)).strip()


def api(path_qs):
    url = f"https://api.adzuna.com/v1/api/jobs/nl/search/{path_qs}&app_id={AID}&app_key={AK}&content-type=application/json"
    try:
        return json.loads(curl(url)).get("results", [])
    except Exception:
        return []


def fetch_firm(key):
    """Een pagina per kantoor. Met ruim honderd kantoren zou drie pagina's per
    kantoor de dagquota van de API opmaken, en een werkgeverszoekopdracht
    levert zelden meer dan vijftig treffers op."""
    return [r for r in api(f"1?results_per_page=50&what_phrase={key.replace(' ', '%20')}")
            if key_matches(key, ((r.get("company", {}) or {}).get("display_name", "") or "").lower())]


def fetch_topic(q):
    return api(f"1?results_per_page=50&what={q.replace(' ', '%20')}")


def job_type(title):
    tl = title.lower()
    if any(x in tl for x in ("afstudeer", "scriptie", "thesis", "graduation")):
        return "stage", ("Graduation placement", "Afstudeerplek")
    if any(x in tl for x in ("stage", "stagiair", "intern", "werkstudent", "student trainee")):
        return "stage", ("Internship", "Stage")
    return "graduate", ("Permanent", "Vaste functie")


def build_entry(r, company, sector, site, logo, initials, maxid, seen_slug):
    title = (r.get("title", "") or "").strip()
    city = city_of((r.get("location", {}) or {}).get("display_name", ""))
    typ, (type_en, type_nl) = job_type(title)
    sec_en, sec_nl = SECTOR_LABEL[sector]
    url = r.get("redirect_url", "").split("?")[0]
    intro = {"en": f"{company} is looking for a {title} in {city}. Below you can read what the role involves and what you bring; you apply directly via the official job page.",
             "nl": f"{company} zoekt een {title} in {city}. Hieronder lees je wat de rol inhoudt en wat je meebrengt; solliciteren doe je rechtstreeks via de officiele vacaturepagina."}
    desc = {"en": f"{company} has an open position for {title} in {city}. Read the full job description and apply via the official job page.",
            "nl": f"{company} heeft een openstaande vacature voor {title} in {city}. Bekijk de volledige functieomschrijving en solliciteer via de officiele vacaturepagina."}
    facts = {"en": {"Location": f"{city}, Netherlands", "Sector": sec_en, "Type": type_en, "Level": "Various", "Practice": sec_en},
             "nl": {"Locatie": f"{city}, Nederland", "Sector": sec_nl, "Type": type_nl, "Niveau": "Divers", "Praktijk": sec_nl}}
    slug = slugify(f"{company}-{title}"); base = slug; i = 2
    while slug in seen_slug:
        slug = f"{base}-{i}"; i += 1
    seen_slug.add(slug)
    blurb = {"en": f"{company} is one of the employers covered on CorporateCareer.",
             "nl": f"{company} is een van de werkgevers die op CorporateCareer worden behandeld."}
    return {"title": title, "company": company, "sector": sector, "type": typ, "location": city, "url": url,
            "checkText": str(r.get("id")), "tags": [sec_en, company.split()[0]], "id": maxid, "featured": False,
            "active": True, "initials": initials, "color": "#0f2540", "salary": "", "daysAgo": None,
            "description": desc, "slug": slug, "logo": logo, "source": "adzuna", "adzunaKey": search_key(company),
            "detail": {"firmBlurb": blurb, "firmSite": site, "intro": intro, "does": DOES[sector],
                       "brings": BRINGS, "facts": facts}}


def main():
    if not (AID and AK):
        print("Geen ADZUNA_APP_ID/KEY in de omgeving; sla over.")
        return
    html = open(JOBS, encoding="utf-8").read()
    m = re.search(r'(<script id="jobs-data" type="application/json">)([\s\S]*?)(</script>)', html)
    jobs = json.loads(m.group(2))
    existing = {str(j.get("checkText")) for j in jobs}
    seen_slug = {j.get("slug") for j in jobs}
    maxid = max(j["id"] for j in jobs)

    firms = firms_from_hubs()
    # naam -> (sector, site, logo, initials), voor zowel de kantoren met een
    # profiel als de handelshuizen zonder
    index = {}
    for slug, f in firms.items():
        blurb = profile_blurb(slug)
        index[f["name"]] = {"sector": f["sector"], "site": f["site"], "logo": f["logo"],
                            "initials": "".join(w[0] for w in f["name"].split()[:2]).upper(),
                            "blurb": blurb, "slug": slug}
    for name, site in COMMODITY_FIRMS.items():
        index.setdefault(name, {"sector": "finance", "site": site, "logo": "",
                                "initials": "".join(w[0] for w in name.split()[:2]).upper(),
                                "blurb": None, "slug": slugify(name)})
    print(f"kantoren uit de hubs: {len(firms)}, plus {len(COMMODITY_FIRMS)} handelshuizen "
          f"= {len(index)} werkgevers")

    added = []

    def take(r, company):
        nonlocal maxid
        meta = index[company]
        title = (r.get("title", "") or "").strip()
        tl = title.lower()
        if not title or any(x in tl for x in EXC):
            return False
        if not any(x in tl for x in INC[meta["sector"]]):
            return False
        aid_id = str(r.get("id"))
        if aid_id in existing or not r.get("redirect_url"):
            return False
        maxid += 1
        e = build_entry(r, company, meta["sector"], meta["site"], meta["logo"],
                        meta["initials"], maxid, seen_slug)
        if meta["blurb"]:
            e["detail"]["firmBlurb"] = {"en": meta["blurb"].get("en", e["detail"]["firmBlurb"]["en"]),
                                        "nl": meta["blurb"].get("nl", e["detail"]["firmBlurb"]["nl"])}
        existing.add(aid_id)
        jobs.append(e); added.append(e)
        return True

    # 1. per werkgever
    per_firm = {}
    for company, meta in index.items():
        key = search_key(company)
        if len(key) < 2:
            continue
        n = 0
        for r in fetch_firm(key):
            if n >= 8:
                break
            if take(r, company):
                n += 1
        if n:
            per_firm[company] = n
    for c, n in sorted(per_firm.items(), key=lambda x: -x[1]):
        print(f"  {c}: +{n}")

    # 2. per onderwerp, maar alleen bij werkgevers die we al kennen
    by_key = {search_key(c): c for c in index}
    topic_n = 0
    for q in TOPIC_QUERIES:
        for r in fetch_topic(q):
            emp = ((r.get("company", {}) or {}).get("display_name", "") or "").lower()
            hit = next((c for k, c in by_key.items() if len(k) >= 2 and key_matches(k, emp)), None)
            if hit and take(r, hit):
                topic_n += 1
    print(f"  via onderwerp (commodity trading, afstudeerplekken): +{topic_n}")

    open(JOBS, "w", encoding="utf-8").write(
        html[:m.start()] + m.group(1) + "\n" + json.dumps(jobs, ensure_ascii=False, indent=2) + "\n"
        + m.group(3) + html[m.end():])
    print("TOTAL adzuna added:", len(added))


if __name__ == "__main__":
    main()
