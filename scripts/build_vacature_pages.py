#!/usr/bin/env python3
"""Genereert een detailpagina per actieve vacature (tweetalig EN/NL).

Leest het jobs-data blok in jobs.html en schrijft voor elke actieve vacature
een statische pagina naar vacatures/<slug>.html. De omschrijving (eigen tekst,
gebaseerd op de officiele vacature) staat in het Engels en het Nederlands en
schakelt mee met de taalknop van de site. Bevat JobPosting-structuurdata en
een knop naar de officiele vacature. Pagina's van niet langer actieve
vacatures worden opgeruimd en de sitemap wordt bijgewerkt. Wordt dagelijks
door de GitHub Action uitgevoerd, na de vacaturecontrole.
"""
import json, os, re, sys, html as H
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_en
import vacancy_pillars

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN_VAC_DIR = os.path.join(BASE, "en", "vacatures")
JOBS_HTML = os.path.join(BASE, "jobs.html")
VAC_DIR = os.path.join(BASE, "vacatures")
SITEMAP = os.path.join(BASE, "sitemap.xml")
SEEN = os.path.join(BASE, "scripts", "vacancy_seen.json")
SITE = "https://corporatecareer.nl"

def esc(s): return H.escape(str(s), quote=True)

def bi(en, nl):
    """Inline tweetalige tekst: toont Engels of Nederlands via de taalknop."""
    return (f'<span data-l="en">{esc(en)}</span>'
            f'<span data-l="nl" hidden>{esc(nl)}</span>')

def read_island():
    html = open(JOBS_HTML, encoding="utf-8").read()
    m = re.search(r'<script id="jobs-data" type="application/json">([\s\S]*?)</script>', html)
    return json.loads(m.group(1))

def fragment(html, start_marker, end_tag):
    i = html.index(start_marker)
    j = html.index(end_tag, i) + len(end_tag)
    return html[i:j]

CHECK_SVG = ('<svg viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">'
             '<path fill-rule="evenodd" d="M16.7 5.3a1 1 0 010 1.4l-7.5 7.5a1 1 0 01-1.4 0l-3.5-3.5a1 1 0 011.4-1.4l2.8 2.8 6.8-6.8a1 1 0 011.4 0z" clip-rule="evenodd"/></svg>')
ARROW_SVG = ('<svg viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">'
             '<path fill-rule="evenodd" d="M3 10a.75.75 0 01.75-.75h10.6L10.2 5.3a.75.75 0 111-1.1l5.5 5.25a.75.75 0 010 1.1l-5.5 5.25a.75.75 0 11-1-1.1l4.15-3.95H3.75A.75.75 0 013 10z" clip-rule="evenodd"/></svg>')

def li_list(items):
    return "\n".join(f'            <li>{CHECK_SVG}{esc(x)}</li>' for x in items)

def dual_list(does):
    return (f'          <ul class="vac-list" data-l="en">\n{li_list(does["en"])}\n          </ul>\n'
            f'          <ul class="vac-list" data-l="nl" hidden>\n{li_list(does["nl"])}\n          </ul>')

EMP_TYPE = {"stage": "INTERN", "graduate": "FULL_TIME"}

# Provincie afgeleid van de plaats, alleen voor plaatsen die we zeker weten.
# Onbekende plaatsen krijgen geen addressRegion; we gokken niet.
NL_REGION = {
    "Amsterdam": "Noord-Holland", "Amstelveen": "Noord-Holland",
    "Hoofddorp": "Noord-Holland", "Haarlem": "Noord-Holland",
    "Zaandam": "Noord-Holland", "Diemen": "Noord-Holland",
    "Rotterdam": "Zuid-Holland", "Den Haag": "Zuid-Holland",
    "The Hague": "Zuid-Holland", "Leiden": "Zuid-Holland", "Delft": "Zuid-Holland",
    "Utrecht": "Utrecht", "Amersfoort": "Utrecht",
    "Eindhoven": "Noord-Brabant", "'s-Hertogenbosch": "Noord-Brabant",
    "Den Bosch": "Noord-Brabant", "Tilburg": "Noord-Brabant", "Breda": "Noord-Brabant",
    "Groningen": "Groningen", "Arnhem": "Gelderland", "Nijmegen": "Gelderland",
    "Maastricht": "Limburg", "Enschede": "Overijssel", "Zwolle": "Overijssel",
    "Almere": "Flevoland", "Leeuwarden": "Friesland", "Assen": "Drenthe",
    "Middelburg": "Zeeland",
}

# Echte kantooradressen (straat + postcode), per bedrijf en plaats, overgenomen
# van de eigen contact-/vestigingenpagina van het bedrijf. Alleen invullen als
# het adres met een officiele bron is geverifieerd; onbekende combinaties
# krijgen geen straatadres, we gokken niet.
OFFICE_ADDRESS = {
    ("BCG", "Amsterdam"): ("Hildegard von Bingenstraat 16-20", "1081 LH"),
    ("BCG Platinion", "Amsterdam"): ("Gustav Mahlerlaan 40", "1082 MC"),
    ("BDO Netherlands", "Eindhoven"): ("Philitelaan 73", "5617 AM"),
    ("BNP Paribas", "Amsterdam"): ("Parnassusweg 789", "1082 LZ"),
    ("Baker Tilly Netherlands", "Amsterdam"): ("Laarderhoogtweg 25", "1101 EB"),
    ("Crowe Foederer", "Eindhoven"): ("Beukenlaan 60", "5651 CD"),
    ("Da Vinci Trading", "Amsterdam"): ("Hildegard von Bingenstraat 12", "1081 LH"),
    ("Deloitte", "Amsterdam"): ("Gustav Mahlerlaan 2970", "1081 LA"),
    ("Deutsche Bank", "Amsterdam"): ("De Entree 195", "1101 HE"),
    ("EQT", "Amsterdam"): ("Johannes Vermeerplein 9", "1071 DV"),
    ("EY Netherlands", "Amsterdam"): ("Antonio Vivaldistraat 150", "1083 HP"),
    ("EY-Parthenon", "Amsterdam"): ("Antonio Vivaldistraat 150", "1083 HP"),
    ("Flow Traders", "Amsterdam"): ("Jacob Bontiusplaats 9", "1018 LL"),
    ("Goldman Sachs", "The Hague"): ("Prinses Beatrixlaan 35", "2595 AK"),
    ("Hogan Lovells", "Amsterdam"): ("Strawinskylaan 4129", "1077 ZX"),
    ("IMC Trading", "Amsterdam"): ("Amstelveenseweg 500", "1081 KL"),
    ("ING", "Amsterdam"): ("Bijlmerdreef 24", "1102 CT"),
    ("Linklaters", "Amsterdam"): ("Zuidplein 180", "1077 XV"),
    ("MUFG Bank", "Amsterdam"): ("Strawinskylaan 1887", "1077 XX"),
    ("Marktlink", "Amsterdam"): ("Trompenburgstraat 2C", "1079 TX"),
    ("Oliver Wyman", "Amsterdam"): ("Strawinskylaan 4101", "1077 ZX"),
    ("Optiver", "Amsterdam"): ("Strawinskylaan 3095", "1077 ZX"),
    ("PwC Netherlands", "Amsterdam"): ("Thomas R. Malthusstraat 5", "1066 JR"),
    ("PwC Netherlands", "Rotterdam"): ("Fascinatio Boulevard 350", "3065 WB"),
    ("RSM Netherlands", "Utrecht"): ("Oorsprongpark 12", "3581 ET"),
    ("Roland Berger", "Amsterdam"): ("Strawinskylaan 581", "1077 XW"),
    ("Sia", "Amsterdam"): ("Amstelplein 1", "1096 HA"),
    ("Van Lanschot Kempen", "Amsterdam"): ("Beethovenstraat 300", "1077 WZ"),
}

def related_block(job, active):
    same = [j for j in active if j["id"] != job["id"] and j["sector"] == job["sector"]]
    same = same[:5] if len(same) >= 3 else [j for j in active if j["id"] != job["id"]][:5]
    if not same:
        return ""
    items = "\n".join(
        f'          <li>{CHECK_SVG}<a href="{esc(j["slug"])}.html">{esc(j["title"])}</a>'
        f' <span style="color:var(--gray-500)">{bi("at "+j["company"], "bij "+j["company"])}</span></li>'
        for j in same)
    label_en = job["detail"]["facts"]["en"]["Sector"].lower()
    label_nl = job["detail"]["facts"]["nl"]["Sector"].lower()
    return f"""
        <section class="vac-block">
          <h2>{bi("More jobs in "+label_en, "Meer vacatures in "+label_nl)}</h2>
          <ul class="vac-list">
{items}
          </ul>
        </section>"""

def pillar_block(job):
    """Blok 'Bekijk ook' met 2 tot 4 interne links naar relevante pijler-
    en categoriepagina's, afgeleid uit de sector en tags van de vacature."""
    links = vacancy_pillars.pillars_for(job)
    if len(links) < 2:
        return ""
    items = "\n".join(
        f'          <li>{CHECK_SVG}<a href="{url}">{bi(en, nl)}</a></li>'
        for url, en, nl in links)
    return f"""
        <section class="vac-block">
          <h2>{bi("See also", "Bekijk ook")}</h2>
          <ul class="vac-list">
{items}
          </ul>
        </section>"""

def facts_dl(facts, lang, hidden):
    rows = "\n".join(
        f'            <div class="vac-fact"><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>'
        for k, v in facts[lang].items())
    h = ' hidden' if hidden else ''
    return f'          <dl class="vac-facts" data-l="{lang}"{h}>\n{rows}\n          </dl>'

def build_page(job, nav, footer, first_seen, active):
    d = job["detail"]
    slug = job["slug"]
    url = f"{SITE}/vacatures/{slug}.html"
    posted = first_seen.get(str(job["id"]), date.today().isoformat())
    valid = (date.fromisoformat(posted) + timedelta(days=90)).isoformat()

    tags_html = "".join(f'<span class="vac-tag">{esc(t)}</span>' for t in job["tags"])

    if job.get("logo"):
        vac_logo_class = "vac-logo vac-logo-img"
        vac_logo_style = ""
        vac_logo_inner = f'<img src="{esc(job["logo"])}" alt="{esc(job["company"])} logo">'
    else:
        vac_logo_class = "vac-logo"
        vac_logo_style = f' style="background:{esc(job["color"])}"'
        vac_logo_inner = esc(job["initials"])

    # JobPosting-structuurdata: Engelse tekst (standaardtaal van de site)
    desc_parts = [f"<p>{esc(d['intro']['en'])}</p>", "<p><strong>What you will do:</strong></p><ul>"]
    desc_parts += [f"<li>{esc(x)}</li>" for x in d["does"]["en"]]
    desc_parts += ["</ul><p><strong>What we are looking for:</strong></p><ul>"]
    desc_parts += [f"<li>{esc(x)}</li>" for x in d["brings"]["en"]]
    desc_parts += ["</ul>", f"<p>{esc(d['firmBlurb']['en'])}</p>"]
    desc_html = "".join(desc_parts)

    job_address = {"@type": "PostalAddress", "addressLocality": job["location"]}
    _office = OFFICE_ADDRESS.get((job["company"], job["location"]))
    if _office:
        job_address["streetAddress"] = _office[0]
        job_address["postalCode"] = _office[1]
    _region = NL_REGION.get(job["location"])
    if _region:
        job_address["addressRegion"] = _region
    job_address["addressCountry"] = "NL"

    jobposting = {
        "@context": "https://schema.org", "@type": "JobPosting",
        "title": job["title"], "description": desc_html,
        "datePosted": posted, "validThrough": valid,
        "employmentType": EMP_TYPE[job["type"]],
        "hiringOrganization": {"@type": "Organization", "name": job["company"], "sameAs": d["firmSite"]},
        "jobLocation": {"@type": "Place", "address": job_address},
        "identifier": {"@type": "PropertyValue", "name": job["company"],
                       "value": str(job.get("checkText") or job["id"])},
        "directApply": False, "url": url,
    }
    bs = job.get("baseSalary")
    if bs:
        jobposting["baseSalary"] = {
            "@type": "MonetaryAmount", "currency": bs["currency"],
            "value": {
                "@type": "QuantitativeValue",
                "minValue": bs["min"], "maxValue": bs["max"],
                "unitText": bs["period"],
            },
        }
    breadcrumb = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Jobs", "item": SITE + "/jobs.html"},
            {"@type": "ListItem", "position": 3, "name": job["title"], "item": url},
        ],
    }
    meta_desc = f"{job['title']} bij {job['company']} in {job['location']}. Bekijk de vacature en solliciteer via de officiele vacaturepagina."
    page_title = f"{job['title']} bij {job['company']} in {job['location']} | CorporateCareer"
    sector_en = d["facts"]["en"]["Sector"]; sector_nl = d["facts"]["nl"]["Sector"]

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="UTF-8">
  <script>var d=document.documentElement;d.classList.add('js');addEventListener('DOMContentLoaded',function(){{window.__ccFade||d.classList.remove('js')}});window.__ccDefaultLang='nl';</script>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{esc(meta_desc)}">
  <meta name="author" content="CorporateCareer">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="CorporateCareer">
  <meta property="og:title" content="{esc(page_title)}">
  <meta property="og:description" content="{esc(meta_desc)}">
  <meta property="og:url" content="{url}">
  <meta property="og:locale" content="nl_NL">
  <script type="application/ld+json">
{json.dumps(jobposting, ensure_ascii=False, indent=2)}
  </script>
  <script type="application/ld+json">
{json.dumps(breadcrumb, ensure_ascii=False, indent=2)}
  </script>
  <title>{esc(page_title)}</title>
  <link rel="icon" type="image/svg+xml" href="../favicon.svg">
  <link rel="preload" href="/fonts/source-serif-4-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="../css/style.css">
  <link rel="stylesheet" href="../css/vacature.css">
  <!-- Google Analytics (GA4) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-TXBG97YW6Y"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-TXBG97YW6Y');
  </script>
</head>
<body>

{nav}

  <div class="vac-wrap">
    <nav class="vac-breadcrumb" aria-label="Breadcrumb">
      <a href="../index.html">Home</a><span>/</span><a href="../jobs.html">{bi("Jobs","Vacatures")}</a><span>/</span>{esc(job['title'])}
    </nav>

    <header class="vac-hero">
      <div class="{vac_logo_class}"{vac_logo_style}>{vac_logo_inner}</div>
      <div class="vac-hero-main">
        <p class="vac-company">{esc(job['company'])}</p>
        <h1 class="vac-title">{esc(job['title'])}</h1>
        <div class="vac-badges">
          <span class="vac-badge vac-badge--sector">{bi(sector_en, sector_nl)}</span>
          <span class="vac-badge vac-badge--type">{bi('Internship' if job['type']=='stage' else 'Permanent', 'Stage' if job['type']=='stage' else 'Vaste functie')}</span>
          <span class="vac-badge vac-badge--loc">{esc(job['location'])}</span>
        </div>
      </div>
    </header>

    <div class="vac-layout">
      <main class="vac-main">
        <section class="vac-block">
          <p>{bi(d['intro']['en'], d['intro']['nl'])}</p>
        </section>

        <section class="vac-block">
          <h2>{bi("What you will do", "Wat je gaat doen")}</h2>
{dual_list(d['does'])}
        </section>

        <section class="vac-block">
          <h2>{bi("What we are looking for", "Wat we vragen")}</h2>
{dual_list(d['brings'])}
        </section>

        <section class="vac-block">
          <h2>{bi("About "+job['company'], "Over "+job['company'])}</h2>
          <p>{bi(d['firmBlurb']['en'], d['firmBlurb']['nl'])}</p>
          <div class="vac-tags">{tags_html}</div>
        </section>
{related_block(job, active)}
{pillar_block(job)}
      </main>

      <aside class="vac-aside">
        <div class="vac-card">
{facts_dl(d['facts'], 'en', False)}
{facts_dl(d['facts'], 'nl', True)}
          <a class="vac-apply" href="{esc(job['url'])}" target="_blank" rel="noopener">
            {bi("Apply on the official site", "Solliciteer op de officiele site")} {ARROW_SVG}
          </a>
          <p class="vac-apply-note">{bi("You will be redirected to the job page of "+job['company']+".", "Je wordt doorgestuurd naar de vacaturepagina van "+job['company']+".")}</p>
          <p class="vac-disclaimer">{bi("CorporateCareer collects and checks this vacancy daily. You apply directly with "+job['company']+"; we are not an intermediary in the application process.", "CorporateCareer verzamelt en controleert deze vacature dagelijks. Solliciteren verloopt rechtstreeks bij "+job['company']+", wij zijn geen tussenpersoon in de sollicitatieprocedure.")}</p>
        </div>
      </aside>
    </div>
  </div>

{footer}

  <script src="../js/i18n.min.js"></script>
  <script src="../js/main.js"></script>
  <script>
    (function () {{
      function apply(l) {{
        document.querySelectorAll('[data-l]').forEach(function (e) {{
          e.hidden = e.getAttribute('data-l') !== l;
        }});
      }}
      apply(window.__ccDefaultLang || 'nl');
    }})();
  </script>
</body>
</html>
"""

def update_sitemap(active):
    xml = open(SITEMAP, encoding="utf-8").read()
    block = "\n".join(
        f"""  <url>
    <loc>{SITE}/vacatures/{j['slug']}.html</loc>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>""" for j in active)
    marked = f"  <!-- VACATURES:START -->\n{block}\n  <!-- VACATURES:END -->"
    if "<!-- VACATURES:START -->" in xml:
        xml = re.sub(r"  <!-- VACATURES:START -->[\s\S]*?  <!-- VACATURES:END -->", marked, xml)
    else:
        xml = xml.replace("</urlset>", marked + "\n\n</urlset>")

    en_block = "\n".join(
        f"""  <url>
    <loc>{SITE}/en/vacatures/{j['slug']}.html</loc>
    <changefreq>weekly</changefreq>
    <priority>0.5</priority>
  </url>""" for j in active)
    en_marked = f"  <!-- EN_VACATURES:START -->\n{en_block}\n  <!-- EN_VACATURES:END -->"
    if "<!-- EN_VACATURES:START -->" in xml:
        xml = re.sub(r"  <!-- EN_VACATURES:START -->[\s\S]*?  <!-- EN_VACATURES:END -->", en_marked, xml)
    else:
        xml = xml.replace("</urlset>", en_marked + "\n\n</urlset>")
    open(SITEMAP, "w", encoding="utf-8").write(xml)

HOME = os.path.join(BASE, "index.html")
SECTOR_LABEL = {"finance": "Finance", "consulting": "Consulting", "advocatuur": "Legal"}
PIN_SVG = ('<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
           'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
           '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>')


def update_home(active, first_seen):
    """Zet de vier nieuwste vacatures en de actuele aantallen in de voorpagina.
    Stonden die kaarten voorheen niet in de HTML: ze werden in de browser
    opgebouwd door het volledige jobs.html (1,6 MB) op te halen, waardoor
    crawlers een lege div zagen en de bezoeker onnodig veel downloadde."""
    if not os.path.exists(HOME):
        return
    html = open(HOME, encoding="utf-8").read()

    # Nieuwste eerst, maar hoogstens een vacature per werkgever en zo veel
    # mogelijk verschillende sectoren, anders toont de etalage vier keer
    # dezelfde bank.
    ordered = sorted(active, key=lambda j: (first_seen.get(str(j["id"]), ""), j["id"]), reverse=True)
    newest, seen_co, seen_sec = [], set(), set()
    for pool in (True, False):          # eerste ronde: ook nieuwe sector eisen
        for j in ordered:
            if len(newest) == 4:
                break
            if j in newest or j["company"] in seen_co:
                continue
            if pool and j.get("sector") in seen_sec:
                continue
            newest.append(j); seen_co.add(j["company"]); seen_sec.add(j.get("sector"))
    for j in ordered:                   # aanvullen als er te weinig overblijft
        if len(newest) == 4:
            break
        if j not in newest:
            newest.append(j)
    cards = []
    for j in newest:
        logo = (f'<div class="company-logo has-logo"><img src="{j["logo"]}" alt="{esc(j["company"])} logo" loading="lazy"></div>'
                if j.get("logo") else
                f'<div class="company-logo" style="background:{j.get("color", "#142a45")}">{esc(j.get("initials", ""))}</div>')
        cards.append(
            f'        <a class="job-card-compact fade-up" href="vacatures/{j["slug"]}.html">{logo}'
            f'<div class="compact-info"><span class="compact-title">{esc(j["title"])}</span>'
            f'<span class="compact-company">{esc(j["company"])}</span>'
            f'<div class="job-badges"><span class="badge-pill badge-pill--type">'
            f'{SECTOR_LABEL.get(j.get("sector"), j.get("sector", ""))}</span></div></div>'
            f'<div class="compact-right"><span class="compact-location">{PIN_SVG}{esc(j.get("location", ""))}</span>'
            f'<span class="job-link">View &rarr;</span></div></a>')
    html = re.sub(r'(<!-- NIEUWSTE-VACATURES:START -->)[\s\S]*?(<!-- NIEUWSTE-VACATURES:END -->)',
                  lambda m: m.group(1) + "\n" + "\n".join(cards) + "\n" + m.group(2), html, count=1)

    # aantallen: totaal en per sector, zodat de cijfers altijd kloppen
    per = {"finance": 0, "consulting": 0, "advocatuur": 0}
    for j in active:
        if j.get("sector") in per:
            per[j["sector"]] += 1
    counts = {
        "vacancies": str(len(active)),
        "finance": f'{per["finance"]} vacatures',
        "consulting": f'{per["consulting"]} vacatures',
        "legal": f'{per["advocatuur"]} vacatures',
    }
    for key, val in counts.items():
        html = re.sub(r'(data-count="' + key + r'"[^>]*>)[^<]*(<)', lambda m, v=val: m.group(1) + v + m.group(2), html)
    open(HOME, "w", encoding="utf-8").write(html)
    print(f"voorpagina bijgewerkt: 4 vacaturekaarten, {len(active)} vacatures "
          f"(finance {per['finance']}, consulting {per['consulting']}, legal {per['advocatuur']})")


def main():
    jobs = read_island()
    active = [j for j in jobs if j.get("active", True) is not False and j.get("slug") and j.get("detail")]

    html = open(JOBS_HTML, encoding="utf-8").read()
    def reroot(frag):
        return re.sub(r'href="(?!\.\./|https?:|#|mailto:)([^"]+)"', r'href="../\1"', frag)
    nav = reroot(fragment(html, '<!-- ── NAVBAR', "</nav>"))
    footer = reroot(fragment(html, '<!-- ── FOOTER', "</footer>"))

    try:
        first_seen = json.load(open(SEEN, encoding="utf-8"))
    except Exception:
        first_seen = {}
    today = date.today().isoformat()
    for j in active:
        first_seen.setdefault(str(j["id"]), today)

    os.makedirs(VAC_DIR, exist_ok=True)
    os.makedirs(EN_VAC_DIR, exist_ok=True)
    wanted = set()
    for j in active:
        fn = f"{j['slug']}.html"
        wanted.add(fn)
        site_path = f"/vacatures/{fn}"
        nl_html = gen_en.add_hreflang_nl(gen_en.bake(build_page(j, nav, footer, first_seen, active), "nl"), site_path)
        open(os.path.join(VAC_DIR, fn), "w", encoding="utf-8").write(nl_html)
        en_title = f"{j['title']} at {j['company']} in {j['location']} | CorporateCareer"
        en_desc = (f"{j['title']} at {j['company']} in {j['location']}. "
                   "View the role and apply via the official job page.")
        open(os.path.join(EN_VAC_DIR, fn), "w", encoding="utf-8").write(
            gen_en.to_en(nl_html, site_path, en_title, en_desc))

    removed = 0
    for d in (VAC_DIR, EN_VAC_DIR):
        for f in os.listdir(d):
            if f.endswith(".html") and f not in wanted:
                os.remove(os.path.join(d, f)); removed += 1

    update_sitemap(active)
    update_home(active, first_seen)
    json.dump(first_seen, open(SEEN, "w", encoding="utf-8"), indent=2)
    print(f"{len(wanted)} pagina's geschreven, {removed} verwijderd")

if __name__ == "__main__":
    main()
