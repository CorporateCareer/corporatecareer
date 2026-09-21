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
    for c in BEDRIJVEN:
        c["hubtype"] = HUBTYPE[c["slug"]]
        d = os.path.join(BASE, "bedrijven", c["slug"])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(bouw(c, sjabloon))
        print(f"  geschreven: bedrijven/{c['slug']}/index.html")

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
    return 0


if __name__ == "__main__":
    sys.exit(main())
