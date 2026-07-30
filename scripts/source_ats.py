#!/usr/bin/env python3
"""Haalt open vacatures op bij de wervingssystemen van de kantoren zelf.

Waar source_adzuna.py via een tussenpartij werkt, praat dit script direct met
de vacaturebank van het kantoor. Dat is de bron, dus completer en actueler, en
het heeft geen sleutel nodig: Recruitee, Greenhouse, SmartRecruiters en
Workday hebben allemaal een openbaar JSON-endpoint.

Welk systeem een kantoor gebruikt wordt afgeleid uit de URLs van de vacatures
die al in jobs.html staan. Een kantoor zonder vacature op de site is zo dus
niet te bereiken; dat vraagt om het opzoeken van hun carrierepagina.

Alleen kantoren met een profiel op de site komen in aanmerking, en alleen
functies die bij finance, consulting of de advocatuur horen. Ondersteunende
rollen bij hetzelfde kantoor (recruiter, secretaresse, netwerkbeheer) vallen
af: die horen niet bij waar de site over gaat.
"""
import json, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import source_adzuna as A

BASE = A.BASE
JOBS = A.JOBS

# systeem -> patroon om de bedrijfscode uit een vacature-URL te vissen
PLATFORMS = [
    ("recruitee",       r"https?://([a-z0-9-]+)\.recruitee\.com"),
    ("greenhouse",      r"greenhouse\.io/([a-z0-9_-]+)/jobs"),
    ("smartrecruiters", r"jobs\.smartrecruiters\.com/([A-Za-z0-9_-]+)/"),
    ("workday",         r"https?://([a-z0-9-]+)\.(wd\d+)\.myworkdayjobs\.com/([A-Za-z0-9_-]+)"),
]

# Nederlandse plaatsen; de systemen leveren de locatie als vrije tekst aan.
NL_PLACES = ("netherlands", "nederland", "holland", "amsterdam", "rotterdam", "den haag", "the hague",
             "utrecht", "eindhoven", "hilversum", "zoetermeer", "amstelveen", "leiden", "groningen",
             "breda", "tilburg", "arnhem", "nijmegen", "maastricht", "zwolle", "apeldoorn", "haarlem",
             "delft", "almere", "'s-hertogenbosch", "den bosch", "amersfoort", "enschede", "deventer")

# Rollen die bij het kantoor horen maar niet bij het vak. Iemand die op deze
# site komt zoekt geen netwerkbeheer of officemanagement.
SUPPORT = ("recruiter", "recruitment", "secretaresse", "secretaris", "assistent", "assistant",
           "administrative", "receptionist", "office manager", "interne communicatie", "marketing",
           "payroll", "hr ", "human resources", "facilit", "netwerk", "network engineer",
           "cloud engineer", "it operations", "mission critical", "sap ", "epd ", "afas", "mendix",
           "relex", "mavim", "aris", "dynamics", "erp ", "solution architect", "projectleider",
           "software engineer", "machine learning engineer", "ai engineer", "c++", "data engineer",
           "devops", "servicedesk", "helpdesk")


def get(url, post=None):
    cmd = ["curl", "-sS", "-m", "25", url, "-H", "Accept: application/json",
           "-H", "User-Agent: Mozilla/5.0 (compatible; CorporateCareer/1.0)"]
    if post is not None:
        cmd += ["-X", "POST", "-H", "Content-Type: application/json", "-d", json.dumps(post)]
    try:
        return json.loads(subprocess.run(cmd, capture_output=True, text=True).stdout)
    except Exception:
        return None


def is_nl(loc):
    return any(p in (loc or "").lower() for p in NL_PLACES)


def listings(kind, code):
    """(titel, locatie, url, checkText) per open vacature."""
    if kind == "recruitee":
        d = get(f"https://{code[0]}.recruitee.com/api/offers/") or {}
        return [(o.get("title", ""), f"{o.get('city','')} {o.get('country_code','')}",
                 o.get("careers_url") or "", o.get("title", ""))
                for o in d.get("offers", []) if o.get("status", "published") == "published"]
    if kind == "greenhouse":
        d = get(f"https://boards-api.greenhouse.io/v1/boards/{code[0]}/jobs") or {}
        return [(j.get("title", ""), (j.get("location") or {}).get("name", ""),
                 j.get("absolute_url", ""), j.get("title", ""))
                for j in d.get("jobs", [])]
    if kind == "smartrecruiters":
        out = []
        for off in (0, 100, 200):
            d = get(f"https://api.smartrecruiters.com/v1/companies/{code[0]}/postings?limit=100&offset={off}") or {}
            page = d.get("content", [])
            for p in page:
                loc = p.get("location") or {}
                pid = str(p.get("id"))
                # De vacaturepagina is een JavaScript-schil; de id staat in de
                # URL, en daar controleert check_vacancies.py op.
                out.append((p.get("name", ""), f"{loc.get('city','')} {loc.get('country','')}",
                            f"https://jobs.smartrecruiters.com/{code[0]}/{pid}", pid))
            if len(page) < 100:
                break
        return out
    if kind == "workday":
        tenant, dc, site = code
        out = []
        for off in (0, 20, 40, 60):
            d = get(f"https://{tenant}.{dc}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs",
                    {"appliedFacets": {}, "limit": 20, "offset": off, "searchText": "Netherlands"}) or {}
            page = d.get("jobPostings", [])
            for p in page:
                out.append((p.get("title", ""), p.get("locationsText", ""),
                            f"https://{tenant}.{dc}.myworkdayjobs.com/{site}{p.get('externalPath','')}",
                            p.get("title", "")))
            if len(page) < 20:
                break
        return out
    return []


def relevant(title, sector):
    tl = title.lower()
    if any(x in tl for x in A.EXC) or any(x in tl for x in SUPPORT):
        return False
    return any(x in tl for x in A.INC[sector])


def main():
    html = open(JOBS, encoding="utf-8").read()
    m = re.search(r'(<script id="jobs-data" type="application/json">)([\s\S]*?)(</script>)', html)
    jobs = json.loads(m.group(2))

    hubs = A.firms_from_hubs()
    # Op genormaliseerde naam vergelijken: de hub schrijft TwynstraGudde en
    # jobs.html Twynstra Gudde. Op de letterlijke naam zou dat kantoor stil
    # afvallen als "geen profiel", wat niet klopt.
    def norm(s):
        return re.sub(r"[^a-z0-9]", "", s.lower())
    sector_of = {norm(v["name"]): (slug, v["sector"]) for slug, v in hubs.items()}

    # Wat een kantoor al op de site heeft, bepaalt zowel het wervingssysteem
    # als het uiterlijk van de nieuwe vacature: logo, kleur, initialen en de
    # beschrijving van het kantoor worden overgenomen, zodat een nieuwe
    # vacature niet te onderscheiden is van een bestaande.
    platform, look = {}, {}
    for j in jobs:
        url = j.get("url", "") or ""
        c = j["company"]
        for kind, pat in PLATFORMS:
            mm = re.search(pat, url)
            if mm:
                platform.setdefault(c, (kind, mm.groups()))
                break
        # Per veld de eerste gevulde waarde nemen. Niet elke bestaande vacature
        # van een kantoor draagt een logo; wie de eerste de beste pakt, geeft
        # de nieuwe vacature soms geen logo terwijl het kantoor er wel een heeft.
        cur = look.setdefault(c, {"logo": "", "initials": "", "color": "", "firmSite": "", "firmBlurb": None})
        d = j.get("detail") or {}
        for k, v in (("logo", j.get("logo")), ("initials", j.get("initials")), ("color", j.get("color")),
                     ("firmSite", d.get("firmSite")), ("firmBlurb", d.get("firmBlurb"))):
            if not cur.get(k) and v:
                cur[k] = v

    known_url = {(j.get("url") or "").split("?")[0].rstrip("/") for j in jobs}
    known_tt = {(j["company"], re.sub(r"\W+", "", j["title"]).lower()) for j in jobs}
    seen_slug = {j.get("slug") for j in jobs}
    maxid = max(j["id"] for j in jobs)

    added, skipped_no_profile = [], set()
    for company, (kind, code) in sorted(platform.items()):
        if norm(company) not in sector_of:
            skipped_no_profile.add(company)
            continue
        slug_c, sector = sector_of[norm(company)]
        rows = listings(kind, code)
        n = 0
        for title, loc, url, check in rows:
            title = (title or "").strip()
            if not title or not url or not is_nl(loc):
                continue
            if url.split("?")[0].rstrip("/") in known_url:
                continue
            if (company, re.sub(r"\W+", "", title).lower()) in known_tt:
                continue
            if not relevant(title, sector):
                continue
            city = A.city_of(loc.replace(" NL", "").replace(" nl", ""))
            typ, (type_en, type_nl) = A.job_type(title)
            sec_en, sec_nl = A.SECTOR_LABEL[sector]
            lk = look.get(company, {})
            s = A.slugify(f"{company}-{title}"); b = s; i = 2
            while s in seen_slug:
                s = f"{b}-{i}"; i += 1
            seen_slug.add(s)
            maxid += 1
            e = {"title": title, "company": company, "sector": sector, "type": typ, "location": city,
                 "url": url, "checkText": check, "tags": [sec_en, company.split()[0]], "id": maxid,
                 "featured": False, "active": True, "initials": lk.get("initials", ""),
                 "color": lk.get("color", "#0f2540"), "salary": "", "daysAgo": None,
                 "description": {
                     "en": f"{company} has an open position for {title} in {city}. Read the full job description and apply via the official job page.",
                     "nl": f"{company} heeft een openstaande vacature voor {title} in {city}. Bekijk de volledige functieomschrijving en solliciteer via de officiele vacaturepagina."},
                 "slug": s, "logo": lk.get("logo", ""), "source": "ats", "atsKind": kind,
                 "detail": {
                     "firmBlurb": lk.get("firmBlurb") or {
                         "en": f"{company} is one of the employers covered on CorporateCareer.",
                         "nl": f"{company} is een van de werkgevers die op CorporateCareer worden behandeld."},
                     "firmSite": lk.get("firmSite", ""),
                     "intro": {
                         "en": f"{company} is looking for a {title} in {city}. Below you can read what the role involves and what you bring; you apply directly via the official job page.",
                         "nl": f"{company} zoekt een {title} in {city}. Hieronder lees je wat de rol inhoudt en wat je meebrengt; solliciteren doe je rechtstreeks via de officiele vacaturepagina."},
                     "does": A.DOES[sector], "brings": A.BRINGS,
                     "facts": {"en": {"Location": f"{city}, Netherlands", "Sector": sec_en, "Type": type_en,
                                      "Level": "Various", "Practice": sec_en},
                               "nl": {"Locatie": f"{city}, Nederland", "Sector": sec_nl, "Type": type_nl,
                                      "Niveau": "Divers", "Praktijk": sec_nl}}}}
            jobs.append(e); added.append(e); known_url.add(url.split("?")[0].rstrip("/")); n += 1
        print(f"  {company:28} {kind:16} {len(rows):4} open, +{n}")

    if skipped_no_profile:
        print("\nOvergeslagen, geen profiel op de site:", ", ".join(sorted(skipped_no_profile)))

    if added:
        open(JOBS, "w", encoding="utf-8").write(
            html[:m.start()] + m.group(1) + "\n" + json.dumps(jobs, ensure_ascii=False, indent=2)
            + "\n" + m.group(3) + html[m.end():])
    print(f"\nTOTAL ats added: {len(added)}")


if __name__ == "__main__":
    main()
