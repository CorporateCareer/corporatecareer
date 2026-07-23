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
import json, os, re, html as H
from datetime import date, timedelta

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
    meta_desc = f"{job['title']} at {job['company']} in {job['location']}. View the role and apply via the official job page."
    page_title = f"{job['title']} at {job['company']} in {job['location']} | CorporateCareer"
    sector_en = d["facts"]["en"]["Sector"]; sector_nl = d["facts"]["nl"]["Sector"]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
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
  <link rel="preload" href="/fonts/fraunces-latin.woff2" as="font" type="font/woff2" crossorigin>
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
      function cur() {{ return window.CURRENT_LANG || localStorage.getItem('cc-lang') || 'en'; }}
      apply(cur());
      var tg = document.getElementById('langToggle');
      if (tg) tg.addEventListener('click', function () {{ setTimeout(function () {{ apply(cur()); }}, 20); }});
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
    open(SITEMAP, "w", encoding="utf-8").write(xml)

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
    wanted = set()
    for j in active:
        fn = f"{j['slug']}.html"
        wanted.add(fn)
        open(os.path.join(VAC_DIR, fn), "w", encoding="utf-8").write(
            build_page(j, nav, footer, first_seen, active))

    removed = 0
    for f in os.listdir(VAC_DIR):
        if f.endswith(".html") and f not in wanted:
            os.remove(os.path.join(VAC_DIR, f)); removed += 1

    update_sitemap(active)
    json.dump(first_seen, open(SEEN, "w", encoding="utf-8"), indent=2)
    print(f"{len(wanted)} pagina's geschreven, {removed} verwijderd")

if __name__ == "__main__":
    main()
