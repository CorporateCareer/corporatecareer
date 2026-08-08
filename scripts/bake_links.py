# -*- coding: utf-8 -*-
"""Zet echte links naar vacaturepagina's in de HTML van de site.

Waarom dit bestaat: de vacaturekaarten op jobs.html, op de bedrijfspagina's en
op de sectorpagina's werden met JavaScript opgebouwd uit het JSON-blok in
jobs.html. Voor een bezoeker maakt dat niets uit, maar een zoekmachine die de
pagina niet uitvoert ziet dan geen enkele link. Van de ruim duizend
vacaturepagina's werd er naar 23 gelinkt, en Google liet 652 pagina's staan op
"wel gevonden, niet opgehaald".

Dit script schrijft dezelfde kaarten als de JavaScript ze zou maken alvast in
de HTML. De JavaScript blijft staan en vervangt ze zodra de pagina laadt, dus
de bezoeker ziet altijd de actuele stand; wie de pagina niet uitvoert, ziet de
ingebakken versie.

Alles staat tussen markeringen, zodat het script elke week opnieuw kan draaien
zonder dat er iets dubbel komt te staan.
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_en

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS = os.path.join(BASE, "jobs.html")

START = "<!-- ingebakken vacaturelinks: begin -->"
END = "<!-- ingebakken vacaturelinks: einde -->"

SECTOR_PAGE = {"finance": "finance.html", "consulting": "consulting.html", "advocatuur": "legal.html"}
SECTOR_LABEL = {"finance": ("Finance", "Finance"), "consulting": ("Consulting", "Consulting"),
                "advocatuur": ("Law", "Advocatuur")}
TYPE_LABEL = {"graduate": ("Graduate", "Vaste functie"), "stage": ("Internship", "Stage")}
BADGE_SECTOR = {"finance": "badge--finance", "advocatuur": "badge--advocatuur", "consulting": "badge--consulting"}
BADGE_TYPE = {"graduate": "badge--graduate", "stage": "badge--stage"}

PIN = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">'
       '<path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>'
       '<circle cx="12" cy="9" r="2.5"/></svg>')


def esc(s):
    return (str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))


def bi(en, nl):
    """Tweetalig fragment, in dezelfde vorm als de rest van de site."""
    return f'<span data-l="en" hidden>{esc(en)}</span><span data-l="nl">{esc(nl)}</span>'


def load_jobs():
    html = open(JOBS, encoding="utf-8").read()
    m = re.search(r'<script id="jobs-data" type="application/json">([\s\S]*?)</script>', html)
    jobs = [j for j in json.loads(m.group(1)) if j.get("active") is not False]
    # Nieuwste eerst, gelijk aan de standaardsortering van jobs.html.
    jobs.sort(key=lambda j: j.get("id", 0), reverse=True)
    return jobs


def job_card(j, prefix="/"):
    """De volledige kaart van jobs.html, zoals renderJob die opbouwt."""
    logo = j.get("logo")
    badge = (f'<div class="job-logo job-logo-img"><img src="{esc(logo)}" alt="{esc(j["company"])} logo" loading="lazy"></div>'
             if logo else
             f'<div class="job-logo" style="background:{esc(j.get("color") or "#0f2540")}">{esc(j.get("initials"))}</div>')
    sec_en, sec_nl = SECTOR_LABEL.get(j["sector"], (j["sector"], j["sector"]))
    typ_en, typ_nl = TYPE_LABEL.get(j["type"], (j["type"], j["type"]))
    return (
        f'<article class="job-card">{badge}'
        f'<div class="job-body"><div class="job-top"><div>'
        f'<h3 class="job-title"><a href="{prefix}vacatures/{esc(j["slug"])}.html">{esc(j["title"])}</a></h3>'
        f'<p class="job-company">{esc(j["company"])}</p></div>'
        f'<div class="job-badges">'
        f'<span class="badge {BADGE_SECTOR.get(j["sector"],"")}">{bi(sec_en, sec_nl)}</span>'
        f'<span class="badge {BADGE_TYPE.get(j["type"],"")}">{bi(typ_en, typ_nl)}</span>'
        f'</div></div>'
        f'<div class="job-meta"><span class="job-meta-item">{PIN}{esc(j.get("location"))}</span></div>'
        f'</div></article>')


def vac_card(j):
    """De compacte kaart van de bedrijfs- en sectorpagina's."""
    plaats = f' · {esc(j["location"])}' if j.get("location") else ""
    return (f'<a class="pe-vac-card" href="/vacatures/{esc(j["slug"])}.html">'
            f'<span class="pe-vac-t">{esc(j["title"])}</span>'
            f'<span class="pe-vac-c">{esc(j["company"])}{plaats}</span></a>')


def inject(html, block, anchor_re, lang="nl"):
    """Zet block tussen de markeringen binnen het element dat anchor_re vindt.

    Staat er al een ingebakken blok, dan wordt dat vervangen. Zo blijft het
    resultaat gelijk hoe vaak dit ook draait.
    """
    m = anchor_re.search(html)
    if not m:
        return html, False
    payload = START + gen_en.bake(block, lang) + END
    inner = m.group(2)
    cleaned = re.sub(re.escape(START) + r"[\s\S]*?" + re.escape(END), "", inner)
    return html[:m.start()] + m.group(1) + payload + cleaned + m.group(3) + html[m.end():], True


# ── jobs.html ────────────────────────────────────────────────────────────────
JOBSLIST = re.compile(r'(<div id="jobsList"[^>]*>)([\s\S]*?)(</div>)')


def do_jobs(jobs):
    # De compacte kaart, niet de volledige. Dit blok is er voor wie de pagina
    # niet uitvoert; de JavaScript vervangt het bij het laden door de volledige
    # kaarten. De volledige vorm zou de pagina 200 kB zwaarder maken zonder dat
    # iemand hem ooit te zien krijgt.
    p = JOBS
    html = open(p, encoding="utf-8").read()
    block = "".join(hub_card(j, cls="job-card") for j in jobs)
    out, ok = inject(html, block, JOBSLIST, "nl")
    if ok:
        open(p, "w", encoding="utf-8").write(out)
    return ok, len(jobs)


# ── bedrijfspagina's ─────────────────────────────────────────────────────────
BVAC = re.compile(r'(<div class="pe-vac-grid" id="bVac"[^>]*>)([\s\S]*?)(</div>)')


def norm(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def do_bedrijven(jobs):
    per = {}
    for j in jobs:
        per.setdefault(norm(j["company"]), []).append(j)
    done = hits = 0
    for d in sorted(os.listdir(os.path.join(BASE, "bedrijven"))):
        p = os.path.join(BASE, "bedrijven", d, "index.html")
        if not os.path.exists(p):
            continue
        html = open(p, encoding="utf-8").read()
        m = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
        naam = m.group(1).strip() if m else d
        mine = per.get(norm(naam), [])
        block = "".join(vac_card(j) for j in mine)
        out, ok = inject(html, block, BVAC, "nl")
        if not ok:
            continue
        # De JavaScript vult dezelfde bak; die moet hem eerst leegmaken,
        # anders staat alles er straks twee keer in.
        out = out.replace("var w=document.getElementById('bVac'),msg=document.getElementById('bVacMsg');",
                          "var w=document.getElementById('bVac'),msg=document.getElementById('bVacMsg');w.innerHTML='';")
        if mine:
            # De bak en de mededeling staan op de JavaScript te wachten. Met
            # kaarten in de HTML moet de bak meteen zichtbaar zijn.
            out = out.replace('<div class="pe-vac-grid" id="bVac"', '<div class="pe-vac-grid" id="bVac" style="display:grid"', 1)
            out = re.sub(r'(<p class="section-text" id="bVacMsg")', r'\1 style="display:none"', out, count=1)
        else:
            out = out.replace('<div class="pe-vac-grid" id="bVac" style="display:grid"', '<div class="pe-vac-grid" id="bVac"', 1)
            out = out.replace('<p class="section-text" id="bVacMsg" style="display:none"', '<p class="section-text" id="bVacMsg"', 1)
        open(p, "w", encoding="utf-8").write(out)
        done += 1
        hits += len(mine)
    return done, hits


# ── sectorpagina's ───────────────────────────────────────────────────────────
# finance.html had hier een raster met verzonnen vacatures in staan, die naar
# jobs.html linkten in plaats van naar een vacature. Dat raster wordt gevuld
# met de echte vacatures van die sector. consulting.html en legal.html hadden
# helemaal geen vacaturesectie; die krijgen er een in dezelfde vorm.
GRID = re.compile(r'(<div class="job-grid">)([\s\S]*?)(</div>\s*</div>\s*</section>)')


def hub_card(j, cls="job-card fade-up", prefix=""):
    """De kaartvorm die de sectorpagina's al gebruiken."""
    logo = j.get("logo")
    tegel = (f'<span class="job-logo job-logo-img"><img src="{esc(logo)}" alt="{esc(j["company"])} logo" loading="lazy"></span>'
             if logo else
             f'<span class="job-logo" style="background:{esc(j.get("color") or "#0f2540")}">{esc(j.get("initials"))}</span>')
    typ_en, typ_nl = TYPE_LABEL.get(j["type"], (j["type"], j["type"]))
    return (f'<a class="{cls}" href="{prefix}vacatures/{esc(j["slug"])}.html">{tegel}'
            f'<span class="job-body"><span class="job-title">{esc(j["title"])}</span>'
            f'<span class="job-firm">{esc(j["company"])}</span>'
            f'<span class="job-meta"><span class="job-tag">{esc(j.get("location"))}</span>'
            f'<span class="job-tag job-tag--type">{bi(typ_en, typ_nl)}</span></span></span></a>')


def sector_section(sector, cards):
    en, nl = SECTOR_LABEL[sector]
    titel_en, titel_nl = f"Current {en.lower()} vacancies", f"Actuele {nl.lower()}-vacatures"
    if sector == "advocatuur":
        titel_en, titel_nl = "Current vacancies in law", "Actuele vacatures in de advocatuur"
    return f"""
  <!-- ── VACATURES ── -->
  <section class="page-section gray" id="vacatures">
    <div class="container">
      <div class="section-head-row">
        <div>
          <p class="section-label">{bi('Vacancies', 'Vacatures')}</p>
          <h2 class="section-title">{bi(titel_en, titel_nl)}</h2>
        </div>
        <a href="jobs.html" class="link-arrow">{bi('View all vacancies', 'Bekijk alle vacatures')}</a>
      </div>
      <div class="job-grid">{START}{cards}{END}</div>
    </div>
  </section>
"""


def do_sectors(jobs):
    per = {}
    for j in jobs:
        per.setdefault(j["sector"], []).append(j)
    out = []
    for sector, fname in SECTOR_PAGE.items():
        p = os.path.join(BASE, fname)
        if not os.path.exists(p):
            continue
        html = open(p, encoding="utf-8").read()
        mine = per.get(sector, [])[:12]
        cards = gen_en.bake("".join(hub_card(j) for j in mine), "nl")
        m = GRID.search(html)
        if m:
            html = html[:m.start()] + m.group(1) + START + cards + END + m.group(3) + html[m.end():]
        else:
            blok = gen_en.bake(sector_section(sector, cards), "nl")
            # Voor de afsluitende oproep zetten, zodat de vacatures nog binnen
            # de inhoud staan en niet onder de knoppenbalk.
            mm = re.search(r'\n\s*<section class="page-cta"', html) or re.search(r'\n\s*</main>', html)
            if not mm:
                continue
            html = html[:mm.start()] + "\n" + blok + html[mm.start():]
        open(p, "w", encoding="utf-8").write(html)
        out.append((fname, len(mine)))
    return out


def main():
    jobs = load_jobs()
    ok, n = do_jobs(jobs)
    print(f"jobs.html: {'ingebakken' if ok else 'BAK NIET GELUKT'}, {n} kaarten")
    d, h = do_bedrijven(jobs)
    print(f"bedrijfspagina's: {d} bijgewerkt, {h} vacaturelinks")
    for fname, k in do_sectors(jobs):
        print(f"{fname}: {k} vacaturelinks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
