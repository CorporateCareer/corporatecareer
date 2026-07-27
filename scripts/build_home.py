#!/usr/bin/env python3
"""Vult de dynamische blokken van de homepage met echte site-data.

De homepage toonde eerder handmatig verzonnen vacatures en cijfers. Dit script
haalt de gegevens uit het jobs-data blok in jobs.html (dezelfde bron als de
vacaturepagina's) en schrijft ze tussen de BUILD-markers in index.html:

  hero-stats   tellers: open vacatures, werkgevers, carrieregidsen
  hero-jobs    paneel met de nieuwste vacatures in de hero
  featured     zes uitgelichte vacatures met link naar de detailpagina
  sectors      drie sectorkaarten met echte aantallen per sector
  employers    logostrook met de werkgevers die nu een vacature open hebben
  itemlist     ItemList-structuurdata die naar de vacaturepagina's wijst

Teksten zijn tweetalig via data-l-spans, net als op de vacature- en
bedrijfspagina's. Draait dagelijks in de GitHub Action, na de vacaturecontrole
en het genereren van de detailpagina's.
"""
import json, os, re, html as H
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS_HTML = os.path.join(BASE, "jobs.html")
INDEX = os.path.join(BASE, "index.html")
SEEN = os.path.join(BASE, "scripts", "vacancy_seen.json")
SITEMAP = os.path.join(BASE, "sitemap.xml")
SITE = "https://corporatecareer.nl"

NEW_DAYS = 14          # tot zoveel dagen na eerste signalering heet een vacature nieuw
HERO_COUNT = 4         # rijen in het heropaneel
FEATURED_COUNT = 6     # kaarten in de uitgelichte sectie

SECTOR = {
    "finance":    ("Finance", "Finance"),
    "consulting": ("Consulting", "Consulting"),
    "advocatuur": ("Law", "Advocatuur"),
}
TYPE = {
    "stage":    ("Internship", "Stage"),
    "graduate": ("Permanent", "Vaste functie"),
}
SECTOR_PAGE = {
    "finance": "finance.html",
    "consulting": "consulting.html",
    "advocatuur": "legal.html",
}
SECTOR_INTRO = {
    "finance": (
        "Investment banking, M&amp;A, private equity, transaction services and trading. "
        "From student internships to graduate and experienced roles at banks, advisory "
        "firms and trading houses in the Netherlands.",
        "Investment banking, M&amp;A, private equity, transaction services en trading. "
        "Van studentstages tot starters- en ervaren functies bij banken, adviesbureaus "
        "en handelshuizen in Nederland."),
    "consulting": (
        "Strategy, technology and operations consulting at firms with a Dutch office, "
        "including internships, entry-level consultant roles and steps up to manager.",
        "Strategie-, technologie- en operationeel advies bij bureaus met een Nederlands "
        "kantoor, van stages en startersfuncties tot doorgroei naar manager."),
    "advocatuur": (
        "Student internships, traineeships and starting positions at law firms, plus the "
        "notarial and tax practices that sit alongside them.",
        "Studentstages, traineeships en startersfuncties bij advocatenkantoren, plus de "
        "notariële en fiscale praktijken die daarnaast staan."),
}

CHEVRON = ('<svg class="hero-job-arrow" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">'
           '<path fill-rule="evenodd" d="M7.3 4.3a1 1 0 011.4 0l5 5a1 1 0 010 1.4l-5 5a1 1 0 '
           '01-1.4-1.4L11.6 10 7.3 5.7a1 1 0 010-1.4z" clip-rule="evenodd"/></svg>')
PIN = ('<svg class="pill-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
       'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
       '<path d="M12 2C8.7 2 6 4.7 6 8c0 4.5 6 12 6 12s6-7.5 6-12c0-3.3-2.7-6-6-6z"/>'
       '<circle cx="12" cy="8" r="2.2"/></svg>')
ARROW = ('<svg viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">'
         '<path fill-rule="evenodd" d="M3 10a.75.75 0 01.75-.75h10.6L10.2 5.3a.75.75 0 '
         '111-1.1l5.5 5.25a.75.75 0 010 1.1l-5.5 5.25a.75.75 0 11-1-1.1l4.15-3.95H3.75A.75.75 '
         '0 013 10z" clip-rule="evenodd"/></svg>')


def esc(s):
    return H.escape(str(s), quote=True)


def bi(en, nl):
    """Tweetalige inline tekst, meeschakelend met de taalknop."""
    return f'<span data-l="en">{en}</span><span data-l="nl" hidden>{nl}</span>'


def load_jobs():
    html = open(JOBS_HTML, encoding="utf-8").read()
    m = re.search(r'<script id="jobs-data" type="application/json">([\s\S]*?)</script>', html)
    jobs = json.loads(m.group(1))
    return [j for j in jobs if j.get("active") is not False]


def load_seen():
    try:
        return json.load(open(SEEN, encoding="utf-8"))
    except Exception:
        return {}


def guide_count():
    """Aantal carrieregidsen: de inhoudelijke pagina's uit de sitemap.

    Vacature-, bedrijfs- en servicepagina's tellen niet mee, zodat de teller
    alleen echte gidsen weergeeft.
    """
    try:
        xml = open(SITEMAP, encoding="utf-8").read()
    except Exception:
        return 0
    skip = {"", "jobs.html", "index.html", "articles.html", "partners.html",
            "over-ons.html", "word-partner.html"}
    n = 0
    for loc in re.findall(r"<loc>([^<]+)</loc>", xml):
        path = loc.replace(SITE, "").lstrip("/")
        if path in skip or path.startswith("vacatures/") or path.startswith("bedrijven/"):
            continue
        if path.startswith("finance/bedrijven"):
            continue
        n += 1
    return n


def is_new(job, seen, today):
    first = seen.get(str(job["id"]))
    if not first:
        return False
    try:
        y, m, d = (int(x) for x in first.split("-"))
    except ValueError:
        return False
    return (today - date(y, m, d)).days <= NEW_DAYS


def sort_key(job, seen):
    """Nieuwste eerst, op datum van eerste signalering en daarna op id."""
    return (seen.get(str(job["id"]), "0000-00-00"), job["id"])


def spread(jobs, limit):
    """Kies vacatures met zo veel mogelijk verschillende werkgevers en sectoren."""
    picked, used_company, used_sector = [], {}, {}
    for cap_company, cap_sector in ((1, 3), (2, 4), (99, 99)):
        for job in jobs:
            if len(picked) >= limit:
                return picked
            if job in picked:
                continue
            if used_company.get(job["company"], 0) >= cap_company:
                continue
            if used_sector.get(job["sector"], 0) >= cap_sector:
                continue
            picked.append(job)
            used_company[job["company"]] = used_company.get(job["company"], 0) + 1
            used_sector[job["sector"]] = used_sector.get(job["sector"], 0) + 1
    return picked


# ── blokken ──────────────────────────────────────────────────────────────
def block_hero_stats(jobs, employers, guides):
    stats = [
        (str(len(jobs)), "Open vacancies", "Open vacatures"),
        (str(len(employers)), "Employers", "Werkgevers"),
        (str(guides), "Career guides", "Carrièregidsen"),
    ]
    out = []
    for i, (num, en, nl) in enumerate(stats):
        if i:
            out.append('          <div class="stat-divider"></div>')
        out.append(
            '          <div class="stat">\n'
            f'            <span class="stat-number">{num}</span>\n'
            f'            <span class="stat-label">{bi(en, nl)}</span>\n'
            '          </div>')
    return "\n".join(out)


def block_hero_jobs(picks, total, seen, today):
    rows = []
    for job in picks:
        new = (f'<span class="hero-job-new">{bi("New", "Nieuw")}</span>'
               if is_new(job, seen, today) else "")
        rows.append(
            '          <li>\n'
            f'            <a class="hero-job" href="vacatures/{esc(job["slug"])}.html">\n'
            f'              <span class="company-logo" style="background:{esc(job["color"])}">{esc(job["initials"])}</span>\n'
            '              <span class="hero-job-info">\n'
            f'                <strong>{esc(job["title"])}{new}</strong>\n'
            f'                <span>{esc(job["company"])} &middot; {esc(job["location"])}</span>\n'
            '              </span>\n'
            f'              {CHEVRON}\n'
            '            </a>\n'
            '          </li>')
    view_all = bi(f"View all {total} vacancies", f"Bekijk alle {total} vacatures")
    return (
        '        <div class="hero-panel">\n'
        '          <div class="hero-panel-head">\n'
        '            <span class="hero-panel-title">'
        f'{bi("Latest vacancies", "Nieuwste vacatures")}</span>\n'
        '            <span class="hero-panel-note"><span class="badge-dot"></span>'
        f'{bi("Checked daily", "Dagelijks gecontroleerd")}</span>\n'
        '          </div>\n'
        '          <ul class="hero-job-list">\n'
        + "\n".join(rows) + "\n"
        '          </ul>\n'
        f'          <a class="hero-panel-link" href="jobs.html">{view_all} {ARROW}</a>\n'
        '        </div>')


def block_featured(picks, seen, today):
    cards = []
    for job in picks:
        sector_en, sector_nl = SECTOR.get(job["sector"], (job["sector"], job["sector"]))
        type_en, type_nl = TYPE.get(job["type"], (job["type"], job["type"]))
        desc = job.get("description") or {}
        new = (f'\n            <span class="badge-pill badge-pill--new">{bi("New", "Nieuw")}</span>'
               if is_new(job, seen, today) else "")
        cards.append(
            '        <article class="job-card fade-up">\n'
            '          <div class="job-card-header">\n'
            f'            <div class="company-logo" style="background:{esc(job["color"])}">{esc(job["initials"])}</div>\n'
            '            <div class="job-card-title">\n'
            f'              <strong>{esc(job["title"])}</strong>\n'
            f'              <span>{esc(job["company"])}</span>\n'
            '            </div>\n'
            '          </div>\n'
            '          <div class="job-badges">\n'
            f'            <span class="badge-pill badge-pill--location">{PIN}{esc(job["location"])}</span>\n'
            f'            <span class="badge-pill badge-pill--type">{bi(sector_en, sector_nl)}</span>\n'
            f'            <span class="badge-pill badge-pill--level">{bi(type_en, type_nl)}</span>{new}\n'
            '          </div>\n'
            f'          <p class="job-desc">{bi(esc(desc.get("en", "")), esc(desc.get("nl", "")))}</p>\n'
            f'          <a href="vacatures/{esc(job["slug"])}.html" class="job-link">'
            f'{bi("View vacancy", "Bekijk vacature")} {ARROW}</a>\n'
            '        </article>')
    return "\n".join(cards)


def block_sectors(jobs):
    cards = []
    for key in ("finance", "consulting", "advocatuur"):
        rows = [j for j in jobs if j["sector"] == key]
        if not rows:
            continue
        companies = sorted({j["company"] for j in rows})
        locations = {}
        for j in rows:
            locations[j["location"]] = locations.get(j["location"], 0) + 1
        top_loc = max(locations, key=lambda k: (locations[k], k))
        interns = sum(1 for j in rows if j["type"] == "stage")
        sector_en, sector_nl = SECTOR[key]
        intro_en, intro_nl = SECTOR_INTRO[key]
        details = [
            (bi("Open vacancies", "Open vacatures"), str(len(rows))),
            (bi("Employers", "Werkgevers"), str(len(companies))),
            (bi("Internships", "Stages"), str(interns)),
            (bi("Most common location", "Meest voorkomende locatie"), esc(top_loc)),
        ]
        detail_html = "\n".join(
            '            <div class="detail">\n'
            f'              <span class="detail-label">{label}</span>\n'
            f'              <span class="detail-value">{value}</span>\n'
            '            </div>' for label, value in details)
        cards.append(
            '        <article class="career-card fade-up">\n'
            f'          <div class="card-tag">{bi("Career path", "Carrièrepad")}</div>\n'
            f'          <h3>{bi(sector_en, sector_nl)}</h3>\n'
            f'          <p>{bi(intro_en, intro_nl)}</p>\n'
            '          <div class="card-details">\n'
            f'{detail_html}\n'
            '          </div>\n'
            f'          <a href="{SECTOR_PAGE[key]}" class="card-cta">'
            f'{bi(f"Explore {sector_en.lower()}", f"Bekijk {sector_nl.lower()}")} {ARROW}</a>\n'
            '        </article>')
    return "\n".join(cards)


def block_employers(jobs):
    counts = {}
    meta = {}
    for job in jobs:
        counts[job["company"]] = counts.get(job["company"], 0) + 1
        meta[job["company"]] = (job["initials"], job["color"])
    names = sorted(counts, key=lambda c: (-counts[c], c))
    half = (len(names) + 1) // 2
    rows_src = [names[:half], names[half:]]

    def chip(name):
        initials, color = meta[name]
        n = counts[name]
        label = bi(f"{n} open vacanc{'y' if n == 1 else 'ies'}",
                   f"{n} open vacature{'' if n == 1 else 's'}")
        return (f'<a class="logo-chip" href="jobs.html">'
                f'<span class="chip-initial" style="background:{esc(color)}">{esc(initials)}</span>'
                f'<span class="chip-text"><span class="chip-name">{esc(name)}</span>'
                f'<span class="chip-count">{label}</span></span></a>')

    out = []
    for i, row in enumerate(rows_src):
        if not row:
            continue
        # Elke helft moet breder zijn dan een breed scherm, anders valt er tijdens
        # het scrollen een gat. Ruwe schatting: een chip is ongeveer 200px breed.
        repeats = max(1, -(-1800 // (len(row) * 200)))
        chips = "".join(chip(n) for n in row * repeats)
        direction = ' style="animation-direction: reverse;"' if i else ""
        out.append(
            '      <div class="logo-row-track">\n'
            f'        <div class="logo-row-inner"{direction}>\n'
            f'          {chips}\n'
            f'          {chips}\n'
            '        </div>\n'
            '      </div>')
    return "\n".join(out)


def block_employers_count(jobs):
    employers = {j["company"] for j in jobs}
    return bi(f"{len(employers)} employers with an open vacancy right now",
              f"{len(employers)} werkgevers met op dit moment een open vacature")


def block_itemlist(picks, total):
    items = [{
        "@type": "ListItem",
        "position": i + 1,
        "url": f"{SITE}/vacatures/{job['slug']}.html",
        "name": f"{job['title']}, {job['company']}",
    } for i, job in enumerate(picks)]
    data = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Open vacancies at CorporateCareer",
        "numberOfItems": total,
        "itemListElement": items,
    }
    body = json.dumps(data, indent=2, ensure_ascii=False)
    return ('  <script type="application/ld+json">\n  '
            + body.replace("\n", "\n  ") + "\n  </script>")


def replace(html, name, content):
    start, end = f"<!-- BUILD:{name} -->", f"<!-- /BUILD:{name} -->"
    i, j = html.index(start), html.index(end)
    return html[:i + len(start)] + "\n" + content + "\n" + html[j:]


def main():
    jobs = load_jobs()
    seen = load_seen()
    today = date.today()
    jobs.sort(key=lambda j: sort_key(j, seen), reverse=True)
    employers = sorted({j["company"] for j in jobs})
    guides = guide_count()

    hero_picks = spread(jobs, HERO_COUNT)
    rest = [j for j in jobs if j not in hero_picks]
    featured_picks = spread(rest, FEATURED_COUNT)

    html = open(INDEX, encoding="utf-8").read()
    html = replace(html, "hero-stats", block_hero_stats(jobs, employers, guides))
    html = replace(html, "hero-jobs", block_hero_jobs(hero_picks, len(jobs), seen, today))
    html = replace(html, "featured", block_featured(featured_picks, seen, today))
    html = replace(html, "sectors", block_sectors(jobs))
    html = replace(html, "employers", block_employers(jobs))
    html = replace(html, "employers-count", block_employers_count(jobs))
    html = replace(html, "itemlist", block_itemlist(hero_picks + featured_picks, len(jobs)))
    open(INDEX, "w", encoding="utf-8").write(html)
    print(f"index.html bijgewerkt: {len(jobs)} vacatures, {len(employers)} werkgevers, "
          f"{guides} gidsen")


if __name__ == "__main__":
    main()
