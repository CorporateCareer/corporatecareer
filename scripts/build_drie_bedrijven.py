# -*- coding: utf-8 -*-
"""Maakt de bedrijfspagina's van drie consulting-werkgevers die er nog geen hadden.

Zonder bedrijfspagina slaat source_ats.py een kantoor over: het leidt de sector
af uit de hubs, en zonder vermelding daar komt er geen sector uit. Sia,
BCG Platinion en EY-Parthenon hadden samen 23 vacatures die daardoor nooit
ververst werden; ze verouderden tot ze een voor een dichtgingen.

De pagina van AlixPartners dient als geraamte: dezelfde sector, dezelfde opzet,
en ook zonder logo. Alleen de bedrijfsspecifieke tekst wordt vervangen. Alle
feiten komen van de eigen site van het kantoor of uit de vacaturebeschrijving
die het kantoor zelf meelevert; er wordt niets bij verzonnen.
"""
import html as H
import os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SJABLOON = os.path.join(BASE, "bedrijven", "alixpartners", "index.html")
SJABLOON_EN = os.path.join(BASE, "en", "bedrijven", "alixpartners", "index.html")
BRON_NAAM = "AlixPartners"

PAD = {
    "financial-deal-advisory": "Financial &amp; Deal Advisory",
    "operations": "Operations",
    "strategy": "Strategy",
    "technology-digital": "Technology &amp; Digital",
    "data-analytics": "Data &amp; Analytics",
    "risk-regulatory": "Risk &amp; Regulatory",
}

BEDRIJVEN = [
 dict(
   slug="sia", naam="Sia", initialen="SI", tint="#2f5d50", stad="Amsterdam",
   tags=["Financial services", "Amsterdam"],
   lead="Een internationaal adviesbureau met kantoren in Amsterdam en Maastricht, sterk in financial services en data.",
   doet="Sia, tot voor kort Sia Partners, is een internationaal management consulting bureau. Het werkt aan strategie, digitale transformatie en operationele verbetering, met zwaartepunten in banken, verzekeraars, energie, farmacie, retail en transport.",
   nl="Sia opende zijn Amsterdamse kantoor in 2009 en kwam er in 2025 een vestiging in Maastricht bij door de overname van Precedence, een adviesbureau voor digitale transformatie en operational excellence. In Amsterdam staat een van de vier wereldwijde Data Science Centers of Excellence van het bureau.",
   bekend="Het bureau is in Nederland vooral bekend om zijn werk voor banken en verzekeraars, en om de combinatie van sectorkennis met data science en AI.",
   instroom="Studenten starten meestal als Consultant, vaak binnen financial services. De vacatures lopen via het eigen wervingssysteem van het kantoor.",
   feiten=[("Type", "Managementadvies"), ("Kantoren (NL)", "Amsterdam en Maastricht"),
           ("Opgericht in NL", "2009"), ("Sector", "Financial services en energie")],
   paden=["financial-deal-advisory", "data-analytics"],
   faq_wat="Sia is een internationaal management consulting bureau met kantoren in Amsterdam en Maastricht, sterk in financial services en data.",
   faq_start="Studenten starten meestal als Consultant, vaak binnen financial services.",
   faq_waar="Het bureau heeft in Nederland kantoren in Amsterdam en Maastricht.",
   en_lead="An international consultancy with offices in Amsterdam and Maastricht, strong in financial services and data.",
   en_doet="Sia, until recently Sia Partners, is an international management consulting firm. It works on strategy, digital transformation and operational improvement, with a focus on banks, insurers, energy, pharmaceuticals, retail and transport.",
   en_nl="Sia opened its Amsterdam office in 2009 and added a Maastricht office in 2025 through the acquisition of Precedence, a consultancy for digital transformation and operational excellence. Amsterdam hosts one of the firm's four global Data Science Centers of Excellence.",
   en_bekend="In the Netherlands the firm is known above all for its work for banks and insurers, and for combining sector knowledge with data science and AI.",
   en_instroom="Students usually start as a Consultant, often within financial services. Vacancies run through the firm's own recruitment system.",
   en_feiten=[("Type", "Management consulting"), ("Offices (NL)", "Amsterdam and Maastricht"),
              ("Founded in NL", "2009"), ("Sector", "Financial services and energy")],
   en_faq_wat="Sia is an international management consulting firm with offices in Amsterdam and Maastricht, strong in financial services and data.",
   en_faq_start="Students usually start as a Consultant, often within financial services.",
   en_faq_waar="The firm has Dutch offices in Amsterdam and Maastricht.",
 ),
 dict(
   slug="bcg-platinion", naam="BCG Platinion", initialen="BP", tint="#1c5c4a", stad="Amsterdam",
   tags=["Technologie &amp; digitaal", "Amsterdam"],
   lead="De technologie- en implementatietak van Boston Consulting Group, met een kantoor in Amsterdam.",
   doet="BCG Platinion is het onderdeel van Boston Consulting Group dat zich richt op technologie: IT-architectuur, grootschalige IT-transformaties, datalandschappen en het inbouwen van AI in bedrijfsprocessen. Waar BCG de strategie bepaalt, werkt Platinion die uit tot in de techniek.",
   nl="Het Amsterdamse kantoor werkt voor Nederlandse en internationale clienten, met opdrachten in onder meer financiele dienstverlening, energie en consumentenmerken.",
   bekend="Platinion staat bekend om het samengaan van strategisch advies en technische uitvoering: architectuur, migraties en AI-implementaties op schaal.",
   instroom="De rollen die in Nederland openstaan liggen rond AI en technologie, van consultant tot architect. Solliciteren gaat via de wervingssite van BCG.",
   feiten=[("Type", "Technologie-advies"), ("Hoofdkantoor (NL)", "Amsterdam"),
           ("Onderdeel van", "Boston Consulting Group"), ("Sector", "Managementadvies")],
   paden=["technology-digital", "data-analytics"],
   faq_wat="BCG Platinion is de technologie- en implementatietak van Boston Consulting Group, gericht op IT-architectuur, datalandschappen en AI.",
   faq_start="De openstaande rollen in Nederland liggen rond AI en technologie; solliciteren gaat via de wervingssite van BCG.",
   faq_waar="Het Nederlandse kantoor staat in Amsterdam.",
   en_lead="The technology and implementation arm of Boston Consulting Group, with an office in Amsterdam.",
   en_doet="BCG Platinion is the part of Boston Consulting Group that focuses on technology: IT architecture, large-scale IT transformations, data landscapes and embedding AI in business processes. Where BCG sets the strategy, Platinion works it through to the engineering.",
   en_nl="The Amsterdam office serves Dutch and international clients, on engagements in financial services, energy and consumer brands among others.",
   en_bekend="Platinion is known for joining strategic advice to technical delivery: architecture, migrations and AI implementations at scale.",
   en_instroom="The roles open in the Netherlands sit around AI and technology, from consultant to architect. Applications go through the BCG careers site.",
   en_feiten=[("Type", "Technology consulting"), ("Head office (NL)", "Amsterdam"),
              ("Part of", "Boston Consulting Group"), ("Sector", "Management consulting")],
   en_faq_wat="BCG Platinion is the technology and implementation arm of Boston Consulting Group, focused on IT architecture, data landscapes and AI.",
   en_faq_start="The roles open in the Netherlands sit around AI and technology; applications go through the BCG careers site.",
   en_faq_waar="The Dutch office is in Amsterdam.",
 ),
 dict(
   slug="ey-parthenon", naam="EY-Parthenon", initialen="EP", tint="#3a3f4b", stad="Amsterdam",
   tags=["Strategy", "Amsterdam"],
   lead="De strategietak van EY, gericht op groei, transacties en waardecreatie.",
   doet="EY-Parthenon is de strategietak van EY. Het werkt aan groeistrategie, commerciele strategie, herstructurering en transacties, en adviseert daarbij bestuurders, private-equityinvesteerders en overheden.",
   nl="Het Nederlandse team zit in Amsterdam en werkt veel aan commercial due diligence en waardecreatie rond overnames, vaak samen met de transactieteams van EY.",
   bekend="EY-Parthenon is vooral bekend om commercial due diligence: het doorlichten van de markt en de commerciele vooruitzichten van een overnamekandidaat.",
   instroom="Studenten starten doorgaans als Consultant of Senior Consultant, vaak via een stage of het traineeprogramma van EY. Solliciteren gaat via de wervingssite van EY.",
   feiten=[("Type", "Strategie-advies"), ("Hoofdkantoor (NL)", "Amsterdam"),
           ("Onderdeel van", "EY"), ("Sector", "Managementadvies")],
   paden=["strategy", "financial-deal-advisory"],
   faq_wat="EY-Parthenon is de strategietak van EY en werkt aan groeistrategie, transacties en waardecreatie.",
   faq_start="Studenten starten doorgaans als Consultant of Senior Consultant, vaak via een stage of het traineeprogramma van EY.",
   faq_waar="Het Nederlandse kantoor staat in Amsterdam.",
   en_lead="The strategy arm of EY, focused on growth, transactions and value creation.",
   en_doet="EY-Parthenon is the strategy arm of EY. It works on growth strategy, commercial strategy, restructuring and transactions, advising boards, private equity investors and governments.",
   en_nl="The Dutch team sits in Amsterdam and works largely on commercial due diligence and value creation around acquisitions, often alongside EY's transaction teams.",
   en_bekend="EY-Parthenon is known above all for commercial due diligence: assessing the market and the commercial outlook of an acquisition target.",
   en_instroom="Students usually start as a Consultant or Senior Consultant, often via an internship or EY's graduate programme. Applications go through the EY careers site.",
   en_feiten=[("Type", "Strategy consulting"), ("Head office (NL)", "Amsterdam"),
              ("Part of", "EY"), ("Sector", "Management consulting")],
   en_faq_wat="EY-Parthenon is the strategy arm of EY, working on growth strategy, transactions and value creation.",
   en_faq_start="Students usually start as a Consultant or Senior Consultant, often via an internship or EY's graduate programme.",
   en_faq_waar="The Dutch office is in Amsterdam.",
 ),
]

PIJL = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round" width="15" height="15" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>')


def esc(s):
    return H.escape(str(s), quote=False)


def vervang_sectie(html, titelmarker, nieuwe_alinea):
    """De alinea onder een sectiekop vervangen, de kop zelf laten staan."""
    pat = (r'(section-title"><span data-l="nl">' + re.escape(titelmarker) +
           r'</span></h2>\s*<p><span data-l="nl">)([\s\S]*?)(</span></p>)')
    return re.sub(pat, lambda m: m.group(1) + nieuwe_alinea + m.group(3), html, count=1)


def bouw(c, sjabloon):
    h = sjabloon
    naam = c["naam"]

    # Kop en omschrijving.
    titel = f"{naam} | Consulting werkgever in Nederland | CorporateCareer"
    desc = f"{naam} in Nederland: wat het kantoor doet, hoe studenten instromen en welke vacatures er openstaan."
    h = re.sub(r"<title>[^<]*</title>", f"<title>{esc(titel)}</title>", h, count=1)
    h = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + esc(desc) + m.group(2), h, count=1)
    for pat in [r'(<meta property="og:description" content=")[^"]*(")',
                r'(<meta name="twitter:description" content=")[^"]*(")']:
        h = re.sub(pat, lambda m: m.group(1) + esc(desc) + m.group(2), h, count=1)

    # De URL's van het geraamte wijzen naar alixpartners.
    h = h.replace("/bedrijven/alixpartners/", f"/bedrijven/{c['slug']}/")

    # Hero: tint, initialen en omschrijving.
    h = h.replace('background:linear-gradient(135deg,#142a45,#234b7e)',
                  f'background:linear-gradient(135deg,#142a45,{c["tint"]})', 1)
    h = h.replace('<span class="bedrijf-badge" style="background:#234b7e">AP</span>',
                  f'<span class="bedrijf-badge" style="background:{c["tint"]}">{esc(c["initialen"])}</span>', 1)
    h = re.sub(r'(<p class="lead"><span data-l="nl">)[^<]*(</span></p>)',
               lambda m: m.group(1) + esc(c["lead"]) + m.group(2), h, count=1)
    tags = "".join(f'<span class="bedrijf-tag">{t}</span>' for t in c["tags"])
    h = re.sub(r'<div class="bedrijf-tags">[\s\S]*?</div>', f'<div class="bedrijf-tags">{tags}</div>', h, count=1)

    # De vier tekstsecties. De koppen dragen nog de naam van het geraamte,
    # dus die markers gebruiken we voordat de naam wordt omgezet.
    h = vervang_sectie(h, f"Wat {BRON_NAAM} doet", esc(c["doet"]))
    h = vervang_sectie(h, f"{BRON_NAAM} in Nederland", esc(c["nl"]))
    h = vervang_sectie(h, "Waar ze bekend om staan", esc(c["bekend"]))
    h = vervang_sectie(h, "Hoe studenten hier starten", esc(c["instroom"]))

    # Kerngegevens.
    feiten = "".join(
        f'<div class="bedrijf-fact"><dt><span data-l="nl">{esc(k)}</span></dt>'
        f'<dd><span data-l="nl">{esc(v)}</span></dd></div>' for k, v in c["feiten"])
    h = re.sub(r'<dl class="bedrijf-facts">[\s\S]*?</dl>', f'<dl class="bedrijf-facts">{feiten}</dl>', h, count=1)

    # Verwante praktijkgebieden.
    kaarten = "".join(
        f'<a class="pe-rel-card fade-up" href="/consulting/{p}/"><span>{PAD[p]}</span>{PIJL}</a>'
        for p in c["paden"])
    kaarten += f'<a class="pe-rel-card fade-up" href="/consulting.html"><span data-l="nl">Consulting overzicht</span>{PIJL}</a>'
    h = re.sub(r'<div class="pe-related">[\s\S]*?</div>\s*</div></section>',
               f'<div class="pe-related">{kaarten}</div>\n  </div></section>', h, count=1)

    # Veelgestelde vragen: drie antwoorden, zowel zichtbaar als in de structuurdata.
    for oud, nieuw in [
        ("AlixPartners is een wereldwijd adviesbureau bekend om turnaround, herstructurering en prestatieverbetering.", c["faq_wat"]),
        ("Studenten starten meestal als Analyst of Consultant via een stage of sollicitatie.", c["faq_start"]),
        ("Het Nederlandse kantoor staat in Amsterdam.", c["faq_waar"]),
    ]:
        h = h.replace(oud, esc(nieuw))

    # Als laatste de naam zelf, in de koppen, de structuurdata en het script dat
    # de vacatures ophaalt.
    h = h.replace(BRON_NAAM, esc(naam))
    return h


def bouw_en(c, sjabloon):
    """De Engelse pagina, uit het Engelse geraamte. Zelfde opzet, eigen tekst."""
    h = sjabloon
    naam = c["naam"]
    titel = f"{naam} | CorporateCareer"
    desc = f"{naam} in the Netherlands: what the firm does, how students get in and which vacancies are open."
    h = re.sub(r"<title>[^<]*</title>", f"<title>{esc(titel)}</title>", h, count=1)
    for pat in [r'(<meta name="description" content=")[^"]*(")',
                r'(<meta property="og:description" content=")[^"]*(")',
                r'(<meta name="twitter:description" content=")[^"]*(")']:
        h = re.sub(pat, lambda m: m.group(1) + esc(desc) + m.group(2), h, count=1)
    h = h.replace("/bedrijven/alixpartners/", f"/bedrijven/{c['slug']}/")

    h = h.replace('background:linear-gradient(135deg,#142a45,#234b7e)',
                  f'background:linear-gradient(135deg,#142a45,{c["tint"]})', 1)
    h = h.replace('<span class="bedrijf-badge" style="background:#234b7e">AP</span>',
                  f'<span class="bedrijf-badge" style="background:{c["tint"]}">{esc(c["initialen"])}</span>', 1)
    h = re.sub(r'(<p class="lead"><span data-l="en">)[^<]*(</span></p>)',
               lambda m: m.group(1) + esc(c["en_lead"]) + m.group(2), h, count=1)
    tags = "".join(f'<span class="bedrijf-tag">{t}</span>' for t in c["en_tags"])
    h = re.sub(r'<div class="bedrijf-tags">[\s\S]*?</div>', f'<div class="bedrijf-tags">{tags}</div>', h, count=1)

    def sec(html, marker, tekst):
        pat = (r'(section-title"><span data-l="en">' + re.escape(marker) +
               r'</span></h2>\s*<p><span data-l="en">)([\s\S]*?)(</span></p>)')
        return re.sub(pat, lambda m: m.group(1) + tekst + m.group(3), html, count=1)

    h = sec(h, f"What {BRON_NAAM} does", esc(c["en_doet"]))
    h = sec(h, f"{BRON_NAAM} in the Netherlands", esc(c["en_nl"]))
    h = sec(h, "What they are known for", esc(c["en_bekend"]))
    h = sec(h, "How students start here", esc(c["en_instroom"]))

    feiten = "".join(
        f'<div class="bedrijf-fact"><dt><span data-l="en">{esc(k)}</span></dt>'
        f'<dd><span data-l="en">{esc(v)}</span></dd></div>' for k, v in c["en_feiten"])
    h = re.sub(r'<dl class="bedrijf-facts">[\s\S]*?</dl>', f'<dl class="bedrijf-facts">{feiten}</dl>', h, count=1)

    kaarten = "".join(
        f'<a class="pe-rel-card fade-up" href="/en/consulting/{p}/"><span>{PAD[p]}</span>{PIJL}</a>'
        for p in c["paden"])
    kaarten += f'<a class="pe-rel-card fade-up" href="/en/consulting.html"><span data-l="en">Consulting overview</span>{PIJL}</a>'
    h = re.sub(r'<div class="pe-related">[\s\S]*?</div>\s*</div></section>',
               f'<div class="pe-related">{kaarten}</div>\n  </div></section>', h, count=1)

    for oud, nieuw in [
        ("AlixPartners is a global consultancy known for turnaround, restructuring and performance improvement.", c["en_faq_wat"]),
        ("Students usually start as an Analyst or Consultant via an internship or graduate application.", c["en_faq_start"]),
        ("The Dutch office is in Amsterdam.", c["en_faq_waar"]),
    ]:
        h = h.replace(oud, esc(nieuw))

    h = h.replace(BRON_NAAM, esc(naam))
    return h


def hub_kaart(c):
    tags = "".join(f"<span>{t}</span>" for t in c["tags"][:1])
    return (f'<a class="bedrijf-card fade-up" href="/bedrijven/{c["slug"]}/" data-types="{c["hubtype"]}">'
            f'<span class="bedrijf-card-badge" style="background:{c["tint"]}">{esc(c["initialen"])}</span>'
            f'<span class="bedrijf-card-name">{esc(c["naam"])}</span>'
            f'<span class="bedrijf-card-meta">{esc(c["stad"])}</span>'
            f'<span class="bedrijf-card-tags">{tags}</span></a>')


HUBTYPE = {"sia": "financial data", "bcg-platinion": "technology data", "ey-parthenon": "strategy financial"}


def main():
    sjabloon = open(SJABLOON, encoding="utf-8").read()
    sjabloon_en = open(SJABLOON_EN, encoding="utf-8").read()
    for c in BEDRIJVEN:
        c["hubtype"] = HUBTYPE[c["slug"]]
        c.setdefault("en_tags", [t.replace("Technologie &amp; digitaal", "Technology &amp; digital")
                                  .replace("Financial services", "Financial services") for t in c["tags"]])
        d = os.path.join(BASE, "bedrijven", c["slug"])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(bouw(c, sjabloon))
        de = os.path.join(BASE, "en", "bedrijven", c["slug"])
        os.makedirs(de, exist_ok=True)
        open(os.path.join(de, "index.html"), "w", encoding="utf-8").write(bouw_en(c, sjabloon_en))
        print(f"  geschreven: bedrijven/{c['slug']}/ en en/bedrijven/{c['slug']}/")

    # De hub is wat source_ats.py leest om de sector te bepalen.
    hub = os.path.join(BASE, "consulting", "bedrijven", "index.html")
    html = open(hub, encoding="utf-8").read()
    toegevoegd = 0
    for c in BEDRIJVEN:
        if f'href="/bedrijven/{c["slug"]}/"' in html:
            continue
        # Alfabetisch invoegen: voor de eerste kaart die later komt.
        kaarten = list(re.finditer(r'<a class="bedrijf-card[\s\S]*?</a>', html))
        doel = None
        for m in kaarten:
            nm = re.search(r'bedrijf-card-name">([^<]+)<', m.group(0))
            if nm and H.unescape(nm.group(1)).lower() > c["naam"].lower():
                doel = m
                break
        kaart = hub_kaart(c)
        if doel:
            html = html[:doel.start()] + kaart + html[doel.start():]
        else:
            html = html[:kaarten[-1].end()] + kaart + html[kaarten[-1].end():]
        toegevoegd += 1
    open(hub, "w", encoding="utf-8").write(html)
    print(f"  consulting-hub: {toegevoegd} kaarten toegevoegd")

    # De sitemap. De vacature- en EN-blokken worden door andere scripts beheerd
    # tussen hun eigen markeringen; de bedrijfspagina's staan er los in, dus die
    # voegen we voor </urlset> toe als ze er nog niet staan.
    sm = os.path.join(BASE, "sitemap.xml")
    xml = open(sm, encoding="utf-8").read()
    nieuw = 0
    for c in BEDRIJVEN:
        for pad in (f"/bedrijven/{c['slug']}/", f"/en/bedrijven/{c['slug']}/"):
            loc = f"https://corporatecareer.nl{pad}"
            if f"<loc>{loc}</loc>" in xml:
                continue
            blok = (f"  <url>\n    <loc>{loc}</loc>\n"
                    f"    <changefreq>monthly</changefreq>\n"
                    f"    <priority>0.6</priority>\n  </url>\n")
            xml = xml.replace("</urlset>", blok + "</urlset>", 1)
            nieuw += 1
    open(sm, "w", encoding="utf-8").write(xml)
    print(f"  sitemap: {nieuw} URL's toegevoegd")
    return 0


if __name__ == "__main__":
    sys.exit(main())
