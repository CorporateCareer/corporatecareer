# -*- coding: utf-8 -*-
"""Bouwt de bedrijven-hub (/finance/bedrijven/) met filters en per bedrijf een
detailpagina (/bedrijven/<slug>/). Nederlands-primair, tweetalig via data-l
(zoals de vacaturepagina's), met lopend verhaal in de uitleg-secties,
dynamische vacatures, Organization-structuurdata en een word-partner-CTA.
Pilot: 4 bedrijven. Alleen verdedigbare feiten, geen verzonnen cijfers."""
import io, os, re, html, json
ROOT = "/home/user/corporatecareer"
PE = os.path.join(ROOT, "finance", "private-equity", "index.html")
CSS = os.path.join(ROOT, "css", "style.css")
SITE = "https://corporatecareer.nl"

def esc(s): return html.escape(s, quote=False)
def bi(en, nl):
    return f'<span data-l="en" hidden>{esc(en)}</span><span data-l="nl">{esc(nl)}</span>'

# ── filtercategorieen ──
FILTERS = [("bank","Banks","Banken"),("trading","Trading","Trading"),
 ("asset-management","Asset management","Vermogensbeheer"),("pension","Pension","Pensioen"),
 ("pe-dealmaking","PE & dealmaking","Private equity & dealmaking"),
 ("advisory","Accountancy & advisory","Accountancy & advies")]
FLABEL={k:(en,nl) for k,en,nl in FILTERS}

# ── pilotbedrijven (feitelijk, tweetalig) ──
COMPANIES = [
 dict(slug="abn-amro", name="ABN AMRO", initials="AA", color="#142a45", city="Amsterdam",
   types=["bank"], site="https://www.abnamro.com",
   tagline_en="One of the largest Dutch banks, with retail, private and corporate & institutional banking.",
   tagline_nl="Een van de grootste Nederlandse banken, met retail, private banking en corporate & institutional banking.",
   intro_en="ABN AMRO is one of the Netherlands' three large banks. It serves private individuals, entrepreneurs, companies and institutions, from everyday payments and mortgages to corporate lending, capital markets and advisory. The bank in its current form dates from the 1991 merger of ABN and AMRO. After state support during the 2008 financial crisis it was nationalised, and it returned to the stock market on Euronext Amsterdam in 2015.",
   intro_nl="ABN AMRO is een van de drie grote banken van Nederland. De bank bedient particulieren, ondernemers, bedrijven en instellingen, van dagelijkse betalingen en hypotheken tot zakelijke kredieten, kapitaalmarkten en advies. De bank in de huidige vorm ontstond in 1991 uit de fusie van ABN en AMRO. Na staatssteun in de kredietcrisis van 2008 werd ze genationaliseerd, en in 2015 keerde ze terug naar de beurs op Euronext Amsterdam.",
   nl_en="The head office is on the Gustav Mahlerlaan on the Amsterdam Zuidas, and ABN AMRO is one of the largest employers in the country, with offices across the Netherlands. For finance students, the most relevant work sits in Corporate & Institutional Banking, markets, risk and finance.",
   nl_nl="Het hoofdkantoor staat aan de Gustav Mahlerlaan op de Amsterdamse Zuidas, en ABN AMRO is een van de grootste werkgevers van het land, met kantoren door heel Nederland. Voor finance-studenten zit het meest relevante werk in Corporate & Institutional Banking, markets, risk en finance.",
   struct_en="The bank is organised around a few main areas: Personal & Business Banking (retail and entrepreneurs), Wealth Management (private banking), and Corporate Banking, which houses corporate finance, capital markets and coverage of larger companies. Supporting these are large risk, finance and technology functions where finance graduates also start.",
   struct_nl="De bank is opgebouwd rond een paar hoofdonderdelen: Personal & Business Banking (retail en ondernemers), Wealth Management (private banking) en Corporate Banking, waar corporate finance, kapitaalmarkten en de begeleiding van grotere bedrijven zitten. Daaromheen zijn er grote risk-, finance- en technologiefuncties waar finance-afgestudeerden ook starten.",
   paths=[("investment-banking","Investment Banking"),("corporate-finance","Corporate Finance"),("asset-management","Asset Management")],
   join_en="Most students enter through a traineeship, an internship or a working-student role. ABN AMRO runs a well-known traineeship programme with tracks in areas such as banking, risk and finance.",
   join_nl="De meeste studenten stromen in via een traineeship, een stage of een werkstudentbaan. ABN AMRO heeft een bekend traineeshipprogramma met richtingen in onder meer banking, risk en finance.",
   facts=[("Type","Type","Bank","Bank"),("Head office","Hoofdkantoor","Amsterdam","Amsterdam"),
     ("Founded","Opgericht","1991 (current form)","1991 (huidige vorm)"),
     ("Ownership","Eigendom","Listed (Euronext Amsterdam)","Beursgenoteerd (Euronext Amsterdam)")]),

 dict(slug="optiver", name="Optiver", initials="OP", color="#e2372b", city="Amsterdam",
   types=["trading"], site="https://www.optiver.com",
   tagline_en="One of the world's leading market makers, trading options and other derivatives for its own account.",
   tagline_nl="Een van 's werelds toonaangevende market makers, die opties en andere derivaten voor eigen rekening verhandelt.",
   intro_en="Optiver is a proprietary trading firm and one of the world's leading market makers. It trades options, ETFs and other derivatives for its own account and provides liquidity on exchanges around the world, which means it continuously quotes prices at which others can buy and sell. The firm was founded in 1986 on the floor of the Amsterdam options exchange and grew from there into a global technology-driven trading house.",
   intro_nl="Optiver is een proprietary trading-firma en een van 's werelds toonaangevende market makers. Het verhandelt opties, ETF's en andere derivaten voor eigen rekening en levert liquiditeit op beurzen over de hele wereld, wat betekent dat het doorlopend prijzen afgeeft waartegen anderen kunnen kopen en verkopen. Het bedrijf werd in 1986 opgericht op de vloer van de Amsterdamse optiebeurs en groeide van daaruit uit tot een wereldwijd, technologiegedreven handelshuis.",
   nl_en="Amsterdam is Optiver's birthplace and largest office, on the Strawinskylaan on the Zuidas. It is one of the reasons Amsterdam is a major European hub for proprietary trading, alongside firms like IMC and Flow Traders.",
   nl_nl="Amsterdam is de bakermat en het grootste kantoor van Optiver, aan de Strawinskylaan op de Zuidas. Het is een van de redenen dat Amsterdam een belangrijk Europees knooppunt voor proprietary trading is, naast bedrijven als IMC en Flow Traders.",
   struct_en="The work centres on three closely connected groups: trading (traders who manage risk and prices in the market), research (quantitative analysts who build the models and strategies) and technology (engineers who build the low-latency systems). Optiver is known for how closely these teams work together.",
   struct_nl="Het werk draait om drie nauw verbonden groepen: trading (traders die risico en prijzen in de markt beheren), research (kwantitatieve analisten die de modellen en strategieen bouwen) en technology (engineers die de systemen met lage latency bouwen). Optiver staat bekend om hoe nauw deze teams samenwerken.",
   paths=[("asset-management","Asset Management")],
   join_en="Optiver hires through internships and graduate programmes for traders, researchers and engineers. Selection is intensive and typically includes numerical and mental-maths tests, so strong quantitative skills matter more than a specific degree.",
   join_nl="Optiver werft via stages en graduate-programma's voor traders, researchers en engineers. De selectie is intensief en bevat doorgaans numerieke en hoofdrekentests, dus sterke kwantitatieve vaardigheden tellen zwaarder dan een specifieke studie.",
   facts=[("Type","Type","Proprietary trading / market maker","Proprietary trading / market maker"),
     ("Head office","Hoofdkantoor","Amsterdam","Amsterdam"),("Founded","Opgericht","1986","1986"),
     ("Ownership","Eigendom","Private","Privaat")]),

 dict(slug="robeco", name="Robeco", initials="RO", color="#1d4ed8", city="Rotterdam",
   types=["asset-management"], site="https://www.robeco.com",
   tagline_en="An international asset manager from Rotterdam, known for research-driven and sustainable investing.",
   tagline_nl="Een internationale vermogensbeheerder uit Rotterdam, bekend om research-gedreven en duurzaam beleggen.",
   intro_en="Robeco is an international asset manager founded in Rotterdam in 1929. It invests on behalf of institutional and private clients through active fundamental and quantitative strategies across equities and fixed income, and is well known for its work on sustainable investing. Robeco is part of the Japanese financial group ORIX.",
   intro_nl="Robeco is een internationale vermogensbeheerder die in 1929 in Rotterdam werd opgericht. Het belegt namens institutionele en particuliere klanten via actieve fundamentele en kwantitatieve strategieen in aandelen en vastrentende waarden, en staat bekend om zijn werk op het gebied van duurzaam beleggen. Robeco is onderdeel van de Japanse financiele groep ORIX.",
   nl_en="The head office is in Rotterdam, and Robeco is one of the best-known Dutch names in asset management. For students it is one of the most direct routes into a research-driven investment career in the Netherlands.",
   nl_nl="Het hoofdkantoor staat in Rotterdam, en Robeco is een van de bekendste Nederlandse namen in vermogensbeheer. Voor studenten is het een van de meest directe routes naar een research-gedreven beleggingscarriere in Nederland.",
   struct_en="The firm is built around its investment teams (equities, fixed income, quant and sustainable investing), supported by research, client and distribution teams, and operations. Analysts and portfolio managers sit at the heart of the organisation.",
   struct_nl="Het bedrijf is opgebouwd rond de beleggingsteams (aandelen, vastrentend, quant en duurzaam beleggen), ondersteund door research-, klant- en distributieteams en operations. Analisten en portefeuillebeheerders vormen het hart van de organisatie.",
   paths=[("asset-management","Asset Management"),("equity-research","Equity Research")],
   join_en="Robeco offers internships, graduate programmes and traineeships, often starting in a research or investment-support role. A CFA charter is valued for investment roles, though not required to start.",
   join_nl="Robeco biedt stages, graduate-programma's en traineeships, vaak startend in een research- of beleggingsondersteunende rol. Een CFA-charter wordt gewaardeerd voor beleggingsfuncties, al is het niet vereist om te beginnen.",
   facts=[("Type","Type","Asset manager","Vermogensbeheerder"),("Head office","Hoofdkantoor","Rotterdam","Rotterdam"),
     ("Founded","Opgericht","1929","1929"),("Ownership","Eigendom","Part of ORIX","Onderdeel van ORIX")]),

 dict(slug="deloitte", name="Deloitte", initials="DE", color="#26890d", city="Rotterdam",
   types=["advisory","pe-dealmaking"], site="https://www.deloitte.com/nl",
   tagline_en="One of the Big Four: audit, tax, consulting and financial advisory, including M&A and transaction services.",
   tagline_nl="Een van de Big Four: audit, belastingadvies, consulting en financial advisory, waaronder M&A en transaction services.",
   intro_en="Deloitte is one of the Big Four professional-services firms and one of the largest business-services employers in the Netherlands. It combines audit and assurance, tax, consulting and financial advisory, the last of which includes corporate finance and M&A advice, transaction services (financial due diligence), valuations and restructuring.",
   intro_nl="Deloitte is een van de Big Four-dienstverleners en een van de grootste werkgevers in de zakelijke dienstverlening van Nederland. Het combineert audit en assurance, belastingadvies, consulting en financial advisory, waarbij dat laatste corporate finance en M&A-advies, transaction services (financiele due diligence), waarderingen en herstructurering omvat.",
   nl_en="The Dutch head office is in Rotterdam, on the Maas, with offices across the country. For finance students, Deloitte is one of the most common places to start a career, whether in audit or on the deal-advisory side.",
   nl_nl="Het Nederlandse hoofdkantoor staat in Rotterdam, aan de Maas, met kantoren door het hele land. Voor finance-studenten is Deloitte een van de meest voorkomende plekken om een carriere te starten, of dat nu in audit is of aan de dealadvies-kant.",
   struct_en="The firm is organised into a few large practices: Audit & Assurance, Tax, Consulting, and Financial Advisory. That advisory practice is where the transaction work sits, corporate finance and M&A, transaction services, valuations, forensic and restructuring, which is the part most finance students target.",
   struct_nl="Het bedrijf is ingedeeld in een paar grote praktijken: Audit & Assurance, Tax, Consulting en Financial Advisory. In die advisory-praktijk zit het transactiewerk: corporate finance en M&A, transaction services, waarderingen, forensic en restructuring, het onderdeel waar de meeste finance-studenten op mikken.",
   paths=[("transaction-services","Transaction Services"),("corporate-finance","Corporate Finance"),("ma","M&A"),("valuation","Valuation")],
   join_en="Students usually start through a working-student role, an internship or the graduate intake, often in audit or transaction services. It is a common first step from which many later move into corporate finance, private equity or industry.",
   join_nl="Studenten starten meestal via een werkstudentbaan, een stage of de startersinstroom, vaak in audit of transaction services. Het is een gebruikelijke eerste stap van waaruit velen later doorstromen naar corporate finance, private equity of het bedrijfsleven.",
   facts=[("Type","Type","Big Four / advisory","Big Four / advies"),("Head office (NL)","Hoofdkantoor (NL)","Rotterdam","Rotterdam"),
     ("Part of","Onderdeel van","Deloitte (global)","Deloitte (wereldwijd)"),("Sector","Sector","Accountancy & advisory","Accountancy & advies")]),
]

# ── CSS (eenmalig toevoegen aan style.css) ──
BEDRIJF_CSS = """
/* ── BEDRIJVEN (company directory) ─────────────── */
.bedrijf-badge { width: 60px; height: 60px; border-radius: 14px; display: inline-flex; align-items: center; justify-content: center; color: #fff; font-weight: 800; font-size: 1.2rem; letter-spacing: -0.02em; box-shadow: 0 6px 20px rgba(10,22,40,0.28); margin-bottom: 18px; }
.bedrijf-tags { display: flex; flex-wrap: wrap; gap: 8px; margin: 14px 0 4px; }
.bedrijf-tag { font-size: 0.76rem; font-weight: 600; padding: 5px 12px; border-radius: 999px; background: rgba(255,255,255,0.14); color: #fff; border: 1px solid rgba(255,255,255,0.22); }
.page-section .bedrijf-tag { background: var(--gray-100); color: var(--gray-700); border-color: var(--gray-200); }
.bedrijf-facts { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1px; background: var(--gray-200); border: 1px solid var(--gray-200); border-radius: 14px; overflow: hidden; margin-top: 12px; }
.bedrijf-fact { background: var(--white); padding: 16px 18px; }
.bedrijf-fact dt { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--gray-500); font-weight: 700; margin-bottom: 4px; }
.bedrijf-fact dd { font-size: 0.95rem; color: var(--navy-950); font-weight: 600; }
/* hub */
.bedrijf-filters { display: flex; flex-wrap: wrap; gap: 10px; margin: 6px 0 34px; }
.bedrijf-filter { font-size: 0.85rem; font-weight: 600; padding: 9px 18px; border-radius: 999px; border: 1px solid var(--gray-300); background: var(--white); color: var(--gray-700); cursor: pointer; transition: all var(--t) var(--ease); }
.bedrijf-filter:hover { border-color: var(--blue-400); color: var(--blue-600); }
.bedrijf-filter.active { background: var(--navy-950); border-color: var(--navy-950); color: #fff; }
.bedrijf-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 18px; }
.bedrijf-card { display: flex; flex-direction: column; padding: 22px; background: var(--white); border: 1px solid var(--gray-200); border-radius: 16px; text-decoration: none; transition: box-shadow var(--t) var(--ease), transform var(--t) var(--ease), border-color var(--t) var(--ease); }
.bedrijf-card:hover { box-shadow: var(--shadow-md); transform: translateY(-3px); border-color: var(--gray-300); }
.bedrijf-card-badge { width: 46px; height: 46px; border-radius: 11px; display: inline-flex; align-items: center; justify-content: center; color: #fff; font-weight: 800; font-size: 0.95rem; margin-bottom: 14px; }
.bedrijf-card-name { font-weight: 700; color: var(--navy-950); font-size: 1.05rem; margin-bottom: 4px; }
.bedrijf-card-meta { font-size: 0.82rem; color: var(--gray-500); }
.bedrijf-card-tags { margin-top: 12px; display: flex; flex-wrap: wrap; gap: 6px; }
.bedrijf-card-tags span { font-size: 0.7rem; font-weight: 600; padding: 3px 9px; border-radius: 999px; background: var(--gray-100); color: var(--gray-600); }
.bedrijf-empty { color: var(--gray-500); padding: 20px 0; display: none; }
"""

def add_css():
    css = io.open(CSS, encoding="utf-8").read()
    if "── BEDRIJVEN (company directory)" in css:
        return
    io.open(CSS, "a", encoding="utf-8").write("\n"+BEDRIJF_CSS)

# ── shared chrome from PE page ──
pe = io.open(PE, encoding="utf-8").read()
NAV = pe[pe.index('<nav class="navbar" id="navbar">'):pe.index('</nav>')+6]
FOOTER = pe[pe.index('<footer class="footer">'):pe.index('</footer>')+len('</footer>')]
STYLE = pe[pe.index('  <style>'):pe.index('</style>')+len('</style>')]
GTAG = ('  <script async src="https://www.googletagmanager.com/gtag/js?id=G-TXBG97YW6Y"></script>\n'
        "  <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}"
        "gtag('js',new Date());gtag('config','G-TXBG97YW6Y');</script>")
FONTS = ('  <link rel="preload" href="/fonts/fraunces-latin.woff2" as="font" type="font/woff2" crossorigin>\n'
         '  <link rel="preload" href="/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>')
TOGGLE = """  <script>
  (function(){
    function apply(l){document.querySelectorAll('[data-l]').forEach(function(e){e.hidden=e.getAttribute('data-l')!==l;});}
    function cur(){return window.CURRENT_LANG||localStorage.getItem('cc-lang')||'nl';}
    apply(cur());
    var t=document.getElementById('langToggle');
    if(t)t.addEventListener('click',function(){setTimeout(function(){apply(cur());},20);});
  })();
  </script>"""

def head(title, desc, url, extra_ld=""):
    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="UTF-8">
  <script>window.__ccDefaultLang='nl';</script>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="author" content="CorporateCareer">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="CorporateCareer">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:url" content="{url}">
  <meta property="og:locale" content="nl_NL">
  <meta property="og:locale:alternate" content="en_GB">
{extra_ld}
  <meta name="description" content="{esc(desc)}">
  <title>{esc(title)}</title>
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{FONTS}
  <link rel="stylesheet" href="/css/style.css">
{STYLE}
{GTAG}
</head>
<body>

{NAV}
"""

def bc(items):
    lis = ""
    for i,(nm, href) in enumerate(items):
        sep = '<li class="sep" aria-hidden="true">/</li>' if i else ''
        if href:
            lis += f'{sep}<li><a href="{href}">{esc(nm)}</a></li>'
        else:
            lis += f'{sep}<li aria-current="page">{esc(nm)}</li>'
    return f'  <nav class="breadcrumb" aria-label="Breadcrumb"><div class="container"><ol>{lis}</ol></div></nav>'

NAMES = {"private-equity":"Private Equity","ma":"M&A","venture-capital":"Venture Capital","corporate-finance":"Corporate Finance",
 "asset-management":"Asset Management","investment-banking":"Investment Banking","transaction-services":"Transaction Services",
 "equity-research":"Equity Research","valuation":"Valuation"}

def company_page(c):
    url = f"{SITE}/bedrijven/{c['slug']}/"
    firms_js = '"'+c["name"]+'"'
    title = f"Werken bij {c['name']}: {FLABEL[c['types'][0]][1].lower()} in {c['city']} | CorporateCareer"
    desc = c["tagline_nl"]
    org = {"@context":"https://schema.org","@type":"Organization","name":c["name"],"url":c["site"],
      "address":{"@type":"PostalAddress","addressLocality":c["city"],"addressCountry":"NL"},"sameAs":[c["site"]]}
    crumb = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
      {"@type":"ListItem","position":1,"name":"Home","item":SITE+"/"},
      {"@type":"ListItem","position":2,"name":"Finance","item":SITE+"/finance.html"},
      {"@type":"ListItem","position":3,"name":"Bedrijven","item":SITE+"/finance/bedrijven/"},
      {"@type":"ListItem","position":4,"name":c["name"],"item":url}]}
    ld = ('  <script type="application/ld+json">\n'+json.dumps(org,ensure_ascii=False,indent=2)+'\n  </script>\n'
          '  <script type="application/ld+json">\n'+json.dumps(crumb,ensure_ascii=False,indent=2)+'\n  </script>')
    tags = "".join(f'<span class="bedrijf-tag">{esc(FLABEL[t][1])}</span>' for t in c["types"])
    facts = "".join(f'<div class="bedrijf-fact"><dt>{bi(le,ln)}</dt><dd>{bi(ve,vn)}</dd></div>' for le,ln,ve,vn in c["facts"])
    paths = "".join(f'<a class="pe-rel-card fade-up" href="/finance/{s}/"><span>{esc(NAMES[s])}</span>'
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="15" height="15" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>' for s,_ in c["paths"])
    return head(title, desc, url, ld) + f"""
{bc([("Home","/index.html"),("Finance","/finance.html"),("Bedrijven","/finance/bedrijven/"),(c["name"],None)])}

  <section class="page-hero" style="background:linear-gradient(135deg,#142a45,#234b7e)"><div class="container inner">
    <span class="bedrijf-badge" style="background:{c['color']}">{esc(c['initials'])}</span>
    <h1>{esc(c['name'])}</h1>
    <p class="lead">{bi(c['tagline_en'], c['tagline_nl'])}</p>
    <div class="bedrijf-tags">{tags}<span class="bedrijf-tag">{esc(c['city'])}</span></div>
    <div class="hero-cta" style="margin-top:22px"><a href="#vacatures" class="btn-primary">{bi('View vacancies','Bekijk vacatures')}</a><a href="/finance.html" class="btn-outline">{bi('Explore finance paths','Ontdek finance-paden')}</a></div>
  </div></section>

  <main>
  <section class="page-section"><div class="container"><div class="pe-prose">
    <p class="section-label">{bi('The organisation','De organisatie')}</p>
    <h2 class="section-title">{bi('What '+c['name']+' does','Wat '+c['name']+' doet')}</h2>
    <p>{bi(c['intro_en'], c['intro_nl'])}</p>
  </div></div></section>

  <section class="page-section gray"><div class="container"><div class="pe-prose">
    <p class="section-label">{bi('In the Netherlands','In Nederland')}</p>
    <h2 class="section-title">{bi(c['name']+' in the Netherlands', c['name']+' in Nederland')}</h2>
    <p>{bi(c['nl_en'], c['nl_nl'])}</p>
  </div></div></section>

  <section class="page-section"><div class="container"><div class="pe-prose">
    <p class="section-label">{bi('Structure','Structuur')}</p>
    <h2 class="section-title">{bi('Divisions and where you work','Divisies en waar je werkt')}</h2>
    <p>{bi(c['struct_en'], c['struct_nl'])}</p>
  </div></div></section>

  <section class="page-section gray"><div class="container"><div class="pe-prose">
    <p class="section-label">{bi('Getting in','Instromen')}</p>
    <h2 class="section-title">{bi('How students start here','Hoe studenten hier starten')}</h2>
    <p>{bi(c['join_en'], c['join_nl'])}</p>
  </div></div></section>

  <section class="page-section"><div class="container">
    <p class="section-label">{bi('Key facts','Kerngegevens')}</p>
    <h2 class="section-title">{bi('At a glance','In het kort')}</h2>
    <dl class="bedrijf-facts">{facts}</dl>
  </div></section>

  <section class="page-section gray" id="vacatures"><div class="container">
    <p class="section-label">{bi('Vacancies','Vacatures')}</p>
    <h2 class="section-title">{bi('Vacancies at '+c['name'],'Vacatures bij '+c['name'])}</h2>
    <p class="section-text" id="bVacMsg">{bi('We only show real, current openings with a link to the employer. When '+c['name']+' has an opening here, it will appear below.','We tonen alleen echte, actuele vacatures met een link naar de werkgever. Zodra '+c['name']+' hier een vacature heeft, verschijnt die hieronder.')}</p>
    <div class="pe-vac-grid" id="bVac"></div>
    <a class="link-arrow" href="/jobs.html" style="color:var(--blue-600);font-weight:700;text-decoration:none;display:inline-block;margin-top:18px">{bi('View all vacancies','Bekijk alle vacatures')}</a>
    <script>
    (function(){{
      var FIRMS=[{firms_js}];
      fetch('/jobs.html').then(function(r){{return r.text();}}).then(function(t){{
        var n=new DOMParser().parseFromString(t,'text/html').getElementById('jobs-data'); if(!n)return;
        var jobs=JSON.parse(n.textContent).filter(function(j){{return j.active!==false;}});
        var m=jobs.filter(function(j){{return FIRMS.indexOf(j.company)!==-1;}}); if(!m.length)return;
        var w=document.getElementById('bVac'),msg=document.getElementById('bVacMsg');
        m.forEach(function(j){{var a=document.createElement('a');a.className='pe-vac-card';a.href='/vacatures/'+j.slug+'.html';
          var ti=document.createElement('span');ti.className='pe-vac-t';ti.textContent=j.title;
          var co=document.createElement('span');co.className='pe-vac-c';co.textContent=j.company+(j.location?' \\u00b7 '+j.location:'');
          a.appendChild(ti);a.appendChild(co);w.appendChild(a);}});
        w.style.display='grid';if(msg)msg.style.display='none';
      }}).catch(function(){{}});
    }})();
    </script>
  </div></section>

  <section class="page-section"><div class="container">
    <p class="section-label">{bi('Related','Gerelateerd')}</p>
    <h2 class="section-title">{bi('Relevant finance paths','Relevante finance-paden')}</h2>
    <div class="pe-related">{paths}</div>
  </div></section>

  <section class="page-cta"><div class="container">
    <h2>{bi('Explore '+c['name']+' and other finance employers','Ontdek '+c['name']+' en andere finance-werkgevers')}</h2>
    <p>{bi('Browse open vacancies, or see all finance companies active in the Netherlands.','Bekijk openstaande vacatures, of zie alle finance-bedrijven die actief zijn in Nederland.')}</p>
    <div class="btn-row"><a href="/jobs.html" class="btn-primary">{bi('View vacancies','Bekijk vacatures')}</a><a href="/finance/bedrijven/" class="btn-outline">{bi('All companies','Alle bedrijven')}</a></div>
    <p style="margin-top:22px;font-size:.9rem;color:var(--gray-500)">{bi('Are you '+c['name']+' and want to update this page or stand out to students? ','Ben jij '+c['name']+' en wil je deze pagina bijwerken of opvallen bij studenten? ')}<a href="/word-partner.html" style="color:var(--blue-600);font-weight:600">{bi('Become a partner','Word partner')}</a>.</p>
  </div></section>
  </main>

{FOOTER}

  <script src="/js/i18n.min.js"></script>
  <script src="/js/main.js"></script>
{TOGGLE}
</body>
</html>
"""

def hub_page():
    url = f"{SITE}/finance/bedrijven/"
    title = "Finance-bedrijven in Nederland: banken, trading, vermogensbeheer | CorporateCareer"
    desc = "Ontdek de grote finance-kantoren die actief zijn in Nederland: banken, tradingfirma's, vermogensbeheerders, pensioenuitvoerders en advieskantoren. Filter op type en bekijk per bedrijf de uitleg en openstaande vacatures."
    crumb = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
      {"@type":"ListItem","position":1,"name":"Home","item":SITE+"/"},
      {"@type":"ListItem","position":2,"name":"Finance","item":SITE+"/finance.html"},
      {"@type":"ListItem","position":3,"name":"Bedrijven","item":url}]}
    ld = '  <script type="application/ld+json">\n'+json.dumps(crumb,ensure_ascii=False,indent=2)+'\n  </script>'
    filters = '<button class="bedrijf-filter active" data-f="all">'+ bi('All','Alle') +'</button>'
    filters += "".join(f'<button class="bedrijf-filter" data-f="{k}">{bi(en,nl)}</button>' for k,en,nl in FILTERS)
    cards = ""
    for c in sorted(COMPANIES, key=lambda x: x["name"].lower()):
        tp = " ".join(c["types"])
        ctags = "".join(f'<span>{esc(FLABEL[t][1])}</span>' for t in c["types"])
        cards += (f'<a class="bedrijf-card fade-up" href="/bedrijven/{c["slug"]}/" data-types="{tp}">'
          f'<span class="bedrijf-card-badge" style="background:{c["color"]}">{esc(c["initials"])}</span>'
          f'<span class="bedrijf-card-name">{esc(c["name"])}</span>'
          f'<span class="bedrijf-card-meta">{esc(c["city"])}</span>'
          f'<span class="bedrijf-card-tags">{ctags}</span></a>\n')
    return head(title, desc, url, ld) + f"""
{bc([("Home","/index.html"),("Finance","/finance.html"),("Bedrijven",None)])}

  <section class="page-hero" style="background:linear-gradient(135deg,#142a45,#234b7e)"><div class="container inner">
    <span class="badge">{bi('Companies','Bedrijven')}</span>
    <h1>{bi('Finance companies in the Netherlands','Finance-bedrijven in Nederland')}</h1>
    <p class="lead">{bi('The large finance firms active in the Netherlands, from banks and trading firms to asset managers and advisory firms. Filter by type and open a company to read what it does and see its vacancies.',"De grote finance-kantoren die actief zijn in Nederland, van banken en tradingfirma's tot vermogensbeheerders en advieskantoren. Filter op type en open een bedrijf om te lezen wat het doet en de vacatures te zien.")}</p>
  </div></section>

  <main>
  <section class="page-section"><div class="container">
    <div class="bedrijf-filters" id="bedrijfFilters">{filters}</div>
    <div class="bedrijf-grid" id="bedrijfGrid">
{cards}    </div>
    <p class="bedrijf-empty" id="bedrijfEmpty">{bi('No companies in this category yet.','Nog geen bedrijven in deze categorie.')}</p>
  </div></section>
  </main>

{FOOTER}

  <script>
  (function(){{
    var fs=document.getElementById('bedrijfFilters'), cards=document.querySelectorAll('#bedrijfGrid .bedrijf-card'), empty=document.getElementById('bedrijfEmpty');
    fs.addEventListener('click',function(e){{
      var b=e.target.closest('.bedrijf-filter'); if(!b)return;
      fs.querySelectorAll('.bedrijf-filter').forEach(function(x){{x.classList.remove('active');}}); b.classList.add('active');
      var f=b.getAttribute('data-f'), shown=0;
      cards.forEach(function(c){{
        var ok = f==='all' || (' '+c.getAttribute('data-types')+' ').indexOf(' '+f+' ')!==-1;
        c.style.display = ok ? '' : 'none'; if(ok)shown++;
      }});
      empty.style.display = shown? 'none':'block';
    }});
  }})();
  </script>
  <script src="/js/i18n.min.js"></script>
  <script src="/js/main.js"></script>
{TOGGLE}
</body>
</html>
"""

# ── sitemap ──
SITEMAP = os.path.join(ROOT, "sitemap.xml")

def update_sitemap():
    xml = io.open(SITEMAP, encoding="utf-8").read()
    urls = [f"""  <url>
    <loc>{SITE}/finance/bedrijven/</loc>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>"""]
    for c in sorted(COMPANIES, key=lambda x: x["slug"]):
        urls.append(f"""  <url>
    <loc>{SITE}/bedrijven/{c['slug']}/</loc>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>""")
    marked = "  <!-- BEDRIJVEN:START -->\n" + "\n".join(urls) + "\n  <!-- BEDRIJVEN:END -->"
    if "<!-- BEDRIJVEN:START -->" in xml:
        xml = re.sub(r"  <!-- BEDRIJVEN:START -->[\s\S]*?  <!-- BEDRIJVEN:END -->", marked, xml)
    else:
        xml = xml.replace("</urlset>", marked + "\n\n</urlset>")
    io.open(SITEMAP, "w", encoding="utf-8").write(xml)

# ── write ──
add_css()
os.makedirs(os.path.join(ROOT,"finance","bedrijven"), exist_ok=True)
io.open(os.path.join(ROOT,"finance","bedrijven","index.html"),"w",encoding="utf-8").write(hub_page())
for c in COMPANIES:
    d = os.path.join(ROOT,"bedrijven",c["slug"]); os.makedirs(d, exist_ok=True)
    io.open(os.path.join(d,"index.html"),"w",encoding="utf-8").write(company_page(c))
update_sitemap()
print("hub + bedrijfspagina's:", len(COMPANIES), "->", [c["slug"] for c in COMPANIES])
