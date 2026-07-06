#!/usr/bin/env python3
"""Genereert een detailpagina per actieve vacature.

Leest het jobs-data blok in jobs.html en schrijft voor elke actieve vacature
een statische pagina naar vacatures/<slug>.html, met een eigen omschrijving
(geen brontekst gekopieerd), JobPosting-structuurdata en een knop naar de
officiele vacature. Pagina's van niet langer actieve vacatures worden
opgeruimd en de sitemap wordt bijgewerkt. Wordt dagelijks door de
GitHub Action uitgevoerd, na de vacaturecontrole.
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
    return "\n".join(f'          <li>{CHECK_SVG}{esc(x)}</li>' for x in items)

EMP_TYPE = {"stage": "INTERN", "graduate": "FULL_TIME"}

def related_block(job, active):
    same = [j for j in active if j["id"] != job["id"] and j["sector"] == job["sector"]]
    same = same[:5] if len(same) >= 3 else [j for j in active if j["id"] != job["id"]][:5]
    if not same:
        return ""
    items = "\n".join(
        f'          <li>{CHECK_SVG}<a href="{esc(j["slug"])}.html">{esc(j["title"])}</a>'
        f' <span style="color:var(--gray-500)">bij {esc(j["company"])}</span></li>'
        for j in same)
    label = job["detail"]["facts"]["Sector"].lower()
    return f"""
        <section class="vac-block">
          <h2>Meer vacatures in {esc(label)}</h2>
          <ul class="vac-list">
{items}
          </ul>
        </section>"""

def build_page(job, nav, footer, first_seen, active):
    d = job["detail"]
    slug = job["slug"]
    url = f"{SITE}/vacatures/{slug}.html"
    posted = first_seen.get(str(job["id"]), date.today().isoformat())
    valid = (date.fromisoformat(posted) + timedelta(days=90)).isoformat()

    facts_html = "\n".join(
        f'            <div class="vac-fact"><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>'
        for k, v in d["facts"].items())

    tags_html = "".join(f'<span class="vac-tag">{esc(t)}</span>' for t in job["tags"])

    # Omschrijving voor de structuurdata (eigen tekst)
    desc_parts = [f"<p>{esc(d['intro'])}</p>", "<p><strong>Wat je gaat doen:</strong></p><ul>"]
    desc_parts += [f"<li>{esc(x)}</li>" for x in d["does"]]
    desc_parts += ["</ul><p><strong>Wat we vragen:</strong></p><ul>"]
    desc_parts += [f"<li>{esc(x)}</li>" for x in d["brings"]]
    desc_parts += ["</ul>", f"<p>{esc(d['firmBlurb'])}</p>"]
    desc_html = "".join(desc_parts)

    jobposting = {
        "@context": "https://schema.org",
        "@type": "JobPosting",
        "title": job["title"],
        "description": desc_html,
        "datePosted": posted,
        "validThrough": valid,
        "employmentType": EMP_TYPE[job["type"]],
        "hiringOrganization": {
            "@type": "Organization",
            "name": job["company"],
            "sameAs": d["firmSite"],
        },
        "jobLocation": {
            "@type": "Place",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": job["location"],
                "addressCountry": "BE",
            },
        },
        "directApply": False,
        "url": url,
    }
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Vacatures", "item": SITE + "/jobs.html"},
            {"@type": "ListItem", "position": 3, "name": job["title"], "item": url},
        ],
    }

    meta_desc = f"{job['title']} bij {job['company']} in {job['location']}. Bekijk de functie en solliciteer via de officiele vacaturepagina."
    page_title = f"{job['title']} bij {job['company']} in {job['location']} | CorporateCareer"

    return f"""<!DOCTYPE html>
<html lang="nl">
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
  <meta property="og:locale" content="nl_BE">
  <script type="application/ld+json">
{json.dumps(jobposting, ensure_ascii=False, indent=2)}
  </script>
  <script type="application/ld+json">
{json.dumps(breadcrumb, ensure_ascii=False, indent=2)}
  </script>
  <title>{esc(page_title)}</title>
  <link rel="icon" type="image/svg+xml" href="../favicon.svg">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Fraunces:opsz,wght@9..144,300..900&display=swap" rel="stylesheet">
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
      <a href="../index.html">Home</a><span>/</span><a href="../jobs.html">Vacatures</a><span>/</span>{esc(job['title'])}
    </nav>

    <header class="vac-hero">
      <div class="vac-logo" style="background:{esc(job['color'])}">{esc(job['initials'])}</div>
      <div class="vac-hero-main">
        <p class="vac-company">{esc(job['company'])}</p>
        <h1 class="vac-title">{esc(job['title'])}</h1>
        <div class="vac-badges">
          <span class="vac-badge vac-badge--sector">{esc(job['detail']['facts']['Sector'])}</span>
          <span class="vac-badge vac-badge--type">{esc('Stage' if job['type']=='stage' else 'Vaste functie')}</span>
          <span class="vac-badge vac-badge--loc">{esc(job['location'])}</span>
        </div>
      </div>
    </header>

    <div class="vac-layout">
      <main class="vac-main">
        <section class="vac-block">
          <p>{esc(d['intro'])}</p>
        </section>

        <section class="vac-block">
          <h2>Wat je gaat doen</h2>
          <ul class="vac-list">
{li_list(d['does'])}
          </ul>
        </section>

        <section class="vac-block">
          <h2>Wat we vragen</h2>
          <ul class="vac-list">
{li_list(d['brings'])}
          </ul>
        </section>

        <section class="vac-block">
          <h2>Over {esc(job['company'])}</h2>
          <p>{esc(d['firmBlurb'])}</p>
          <div class="vac-tags">{tags_html}</div>
        </section>
{related_block(job, active)}
      </main>

      <aside class="vac-aside">
        <div class="vac-card">
          <dl class="vac-facts">
{facts_html}
          </dl>
          <a class="vac-apply" href="{esc(job['url'])}" target="_blank" rel="noopener">
            Solliciteer op de officiele site {ARROW_SVG}
          </a>
          <p class="vac-apply-note">Je wordt doorgestuurd naar de vacaturepagina van {esc(job['company'])}.</p>
          <p class="vac-disclaimer">CorporateCareer verzamelt en controleert deze vacature dagelijks. Solliciteren verloopt rechtstreeks bij {esc(job['company'])}, wij zijn geen tussenpersoon in de sollicitatieprocedure.</p>
        </div>
      </aside>
    </div>
  </div>

{footer}

  <script src="../js/i18n.js"></script>
  <script src="../js/main.js"></script>
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
    # Nav en footer staan in de hoofdmap; vanuit vacatures/ moeten interne
    # links een ../ voorvoegsel krijgen (externe links, ankers en mailto niet).
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
