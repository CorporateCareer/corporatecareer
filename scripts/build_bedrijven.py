# -*- coding: utf-8 -*-
"""Bouwt de bedrijven-hub (/finance/bedrijven/) met filters en per bedrijf een
detailpagina (/bedrijven/<slug>/). Nederlands-primair, tweetalig via data-l
(zoals de vacaturepagina's), met lopend verhaal in de uitleg-secties,
dynamische vacatures, Organization-structuurdata en een word-partner-CTA.
Finance-bedrijven met 100+ medewerkers in Nederland. Alleen verdedigbare feiten, geen verzonnen cijfers."""
import io, os, re, html, json
ROOT = "/home/user/corporatecareer"
PE = os.path.join(ROOT, "finance", "private-equity", "index.html")
CSS = os.path.join(ROOT, "css", "style.css")
SITE = "https://corporatecareer.nl"
LOGOS_DIR = os.path.join(ROOT, "img", "logos")

def logo_url(slug):
    for ext in ("svg", "png"):
        if os.path.isfile(os.path.join(LOGOS_DIR, f"{slug}.{ext}")):
            return f"/img/logos/{slug}.{ext}"
    return None

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
   paths=[("investment-banking","Investment Banking"),("corporate-finance","Corporate Finance"),("wealth-management","Wealth Management & Private Banking")],
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
   paths=[("trading","Trading")],
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

dict(slug="ing", name="ING", initials="IN", color="#ff6200", city="Amsterdam",
        types=["bank"], site="https://www.ing.com",
        tagline_en="One of the Netherlands' three large banks, active in retail, wholesale and digital banking across Europe and beyond.",
        tagline_nl="Een van de drie grote Nederlandse banken, actief in retail, wholesale en digital banking in Europa en daarbuiten.",
        intro_en="ING is one of the Netherlands' largest financial institutions, offering retail banking, business banking and wholesale banking services. It was formed in 1991 through the merger of insurer Nationale-Nederlanden and NMB Postbank Group, combining banking and insurance activities under one holding company. ING later divested its insurance arm to focus purely on banking. The bank serves millions of customers across the Netherlands and operates in dozens of countries, with a large presence in retail banking, corporate lending, and financial markets. ING is listed on Euronext Amsterdam and is considered a systemically important bank in Europe.",
        intro_nl="ING is een van de grootste financiële instellingen van Nederland, met retailbanking, zakelijke bankdiensten en wholesale banking. De bank ontstond in 1991 uit de fusie van verzekeraar Nationale-Nederlanden en NMB Postbank Group, waarmee bank- en verzekeringsactiviteiten onder één holding kwamen. Later stootte ING haar verzekeringstak af om zich volledig op bankieren te richten. ING bedient miljoenen klanten in Nederland en is actief in tientallen landen, met een sterke positie in retailbanking, zakelijke kredietverlening en financiële markten. De bank staat genoteerd aan Euronext Amsterdam en geldt als systeemrelevante bank in Europa.",
        nl_en="ING's global head office is in Amsterdam, on the Bijlmerdreef in Amsterdam-Zuidoost, and the bank is one of the largest financial employers in the Netherlands. For finance students, ING offers exposure to wholesale banking, capital markets, corporate lending, risk management and treasury, alongside its large retail banking operations.",
        nl_nl="Het wereldwijde hoofdkantoor van ING staat aan de Bijlmerdreef in Amsterdam-Zuidoost, en de bank is een van de grootste financiële werkgevers van Nederland. Voor finance-studenten biedt ING inzicht in wholesale banking, kapitaalmarkten, zakelijke kredietverlening, risicomanagement en treasury, naast de omvangrijke retailactiviteiten.",
        struct_en="ING is organised broadly into Retail Banking, serving individuals and small businesses, and Wholesale Banking, which covers corporate lending, financial markets, transaction services and sectors such as real estate and infrastructure finance. Finance graduates typically start in wholesale banking, risk, finance or treasury functions, or in analyst programmes tied to specific product lines such as debt capital markets or corporate finance advisory.",
        struct_nl="ING is grofweg opgebouwd rond Retail Banking, gericht op particulieren en kleine bedrijven, en Wholesale Banking, waaronder zakelijke kredietverlening, financiële markten, transaction services en sectoren als vastgoed- en infrastructuurfinanciering vallen. Finance-afgestudeerden starten doorgaans binnen wholesale banking, risk, finance of treasury, of in analistenprogramma's gekoppeld aan specifieke productlijnen zoals debt capital markets of corporate finance advies.",
        paths=[("investment-banking","Investment Banking"),("corporate-finance","Corporate Finance"),("debt-advisory","Debt Advisory"),("risk-management","Risk Management")],
        join_en="Most graduates join ING through analyst or graduate programmes within wholesale banking, or through internships and working-student roles across risk, finance and markets functions.",
        join_nl="De meeste afgestudeerden komen bij ING binnen via analisten- of graduate-programma's binnen wholesale banking, of via stages en werkstudentplekken bij risk-, finance- en marktenafdelingen.",
        facts=[("Type","Type","Bank","Bank"),("Head office","Hoofdkantoor","Amsterdam","Amsterdam"),
            ("Founded","Opgericht","1991 (merger of Nationale-Nederlanden and NMB Postbank Group)","1991 (fusie van Nationale-Nederlanden en NMB Postbank Group)"),
            ("Ownership","Eigendom","Listed (Euronext Amsterdam)","Beursgenoteerd (Euronext Amsterdam)")]),

    dict(slug="rabobank", name="Rabobank", initials="RB", color="#004b87", city="Utrecht",
        types=["bank"], site="https://www.rabobank.com",
        tagline_en="A cooperative bank with roots in agricultural lending, now one of the Netherlands' largest banks.",
        tagline_nl="Een coöperatieve bank met wortels in agrarische kredietverlening, nu een van de grootste banken van Nederland.",
        intro_en="Rabobank is a Dutch cooperative bank that grew out of local farmers' credit cooperatives founded in the late 19th century. Two central organisations, the Coöperatieve Centrale Raiffeisen-Bank and the Coöperatieve Centrale Boerenleenbank, merged in 1972 to form what became known as Rabobank. Unlike most large banks, Rabobank is not listed on the stock exchange: it is owned by its network of local member banks rather than shareholders. Today it is one of the Netherlands' three large banks, with a strong position in retail banking, food and agribusiness financing, and corporate and wholesale banking. It also has an international network focused on food and agri clients.",
        intro_nl="Rabobank is een Nederlandse coöperatieve bank die is voortgekomen uit lokale boerenleenbanken uit de late negentiende eeuw. Twee centrale organisaties, de Coöperatieve Centrale Raiffeisen-Bank en de Coöperatieve Centrale Boerenleenbank, fuseerden in 1972 tot wat bekend werd als Rabobank. Anders dan de meeste grote banken staat Rabobank niet op de beurs: de bank is eigendom van haar netwerk van lokale ledenbanken in plaats van aandeelhouders. Vandaag de dag is Rabobank een van de drie grote Nederlandse banken, met een sterke positie in retailbanking, food- en agrifinanciering en zakelijke en wholesale banking. Ook heeft de bank een internationaal netwerk gericht op food- en agriklanten.",
        nl_en="Rabobank's head office is in Utrecht, and the bank is one of the largest financial employers in the country, with a nationwide network of local banks alongside its central organisation. For finance students, the most relevant roles sit within wholesale banking, corporate clients, risk and treasury, as well as the bank's well-known food and agribusiness research and advisory teams.",
        nl_nl="Het hoofdkantoor van Rabobank staat in Utrecht, en de bank is een van de grootste financiële werkgevers van het land, met een landelijk netwerk van lokale banken naast de centrale organisatie. Voor finance-studenten zit het meest relevante werk binnen wholesale banking, corporate clients, risk en treasury, en bij de bekende food- en agri-onderzoeks- en adviesteams.",
        struct_en="Rabobank is organised around Domestic Retail Banking, serving individuals and businesses through its local bank network, and Wholesale & Rural, which covers corporate banking, trade and commodity finance, and international food and agri clients. Group functions such as risk, finance and treasury operate across the organisation. Finance graduates typically start in corporate banking, risk, or one of Rabobank's traineeships that rotate across several of these areas.",
        struct_nl="Rabobank is opgebouwd rond Domestic Retail Banking, dat particulieren en bedrijven bedient via het lokale bankennetwerk, en Wholesale & Rural, waaronder corporate banking, handels- en grondstoffenfinanciering en internationale food- en agriklanten vallen. Groepsfuncties zoals risk, finance en treasury opereren organisatiebreed. Finance-afgestudeerden starten doorgaans binnen corporate banking, risk, of via een van de traineeships van Rabobank die door meerdere van deze afdelingen heen rouleren.",
        paths=[("corporate-finance","Corporate Finance"),("debt-advisory","Debt Advisory"),("risk-management","Risk Management")],
        join_en="Rabobank recruits graduates through traineeships and analyst programmes, alongside internships and working-student roles across corporate banking, risk and treasury.",
        join_nl="Rabobank werft afgestudeerden via traineeships en analistenprogramma's, naast stages en werkstudentplekken binnen corporate banking, risk en treasury.",
        facts=[("Type","Type","Bank (cooperative)","Bank (coöperatie)"),("Head office","Hoofdkantoor","Utrecht","Utrecht"),
            ("Founded","Opgericht","1972 (merger forming Rabobank; roots to 1898)","1972 (fusie tot Rabobank; wortels tot 1898)"),
            ("Ownership","Eigendom","Cooperative (owned by member banks, not listed)","Coöperatie (eigendom van ledenbanken, niet beursgenoteerd)")]),

    dict(slug="de-volksbank", name="de Volksbank (ASN Bank)", initials="VB", color="#009640", city="Utrecht",
        types=["bank"], site="https://www.asnbank.nl",
        tagline_en="State-owned Dutch bank built around sustainability, formerly operating the SNS, ASN Bank and RegioBank brands and since 2025 consolidated under the ASN Bank name.",
        tagline_nl="Staatsbank gericht op duurzaamheid, voorheen actief onder de merken SNS, ASN Bank en RegioBank en sinds 2025 samengevoegd onder de naam ASN Bank.",
        intro_en="De Volksbank is a Dutch retail bank wholly owned by the Dutch State through the foundation NLFI, following the 2013 nationalisation of its predecessor SNS REAAL after losses at its property finance unit. For over a decade the bank operated multiple retail brands, SNS, ASN Bank and RegioBank, alongside mortgage label BLG Wonen, each with its own positioning but sharing one balance sheet. From 2025 the bank has been consolidating these brands into a single one, ASN Bank, known for its focus on sustainable and socially responsible banking, and its legal name changed accordingly. The bank focuses on everyday retail banking and mortgages in the Netherlands rather than wholesale or investment banking.",
        intro_nl="De Volksbank is een Nederlandse retailbank die volledig eigendom is van de Nederlandse Staat via stichting NLFI, sinds de nationalisatie van voorganger SNS REAAL in 2013 na verliezen bij de vastgoedfinancieringstak. Meer dan tien jaar lang voerde de bank meerdere retailmerken, SNS, ASN Bank en RegioBank, naast hypotheeklabel BLG Wonen, elk met een eigen positionering maar met één gezamenlijke balans. Vanaf 2025 voegt de bank deze merken samen tot één merk, ASN Bank, bekend om haar focus op duurzaam en maatschappelijk verantwoord bankieren, en is ook de statutaire naam hierop aangepast. De bank richt zich op alledaags retailbankieren en hypotheken in Nederland, niet op wholesale of investment banking.",
        nl_en="The bank's head office is in Utrecht, and it is a notable employer in Dutch retail banking, with a presence across the country through its branch network and online services. Finance students will find relevant roles in risk management, treasury, sustainable finance and product management for savings and mortgages, rather than in dealmaking or capital markets.",
        nl_nl="Het hoofdkantoor staat in Utrecht, en de bank is een bekende werkgever in het Nederlandse retailbankwezen, met een landelijke aanwezigheid via het kantorennetwerk en online dienstverlening. Finance-studenten vinden hier relevant werk in risicomanagement, treasury, duurzame financiering en productmanagement voor sparen en hypotheken, eerder dan in dealmaking of kapitaalmarkten.",
        struct_en="The bank is organised around retail banking activities, savings, payments and mortgages, delivered through its brands, alongside central functions such as risk, finance, treasury and sustainability. It also runs a sustainable investment fund range under the ASN name. Finance graduates typically start in risk, finance, treasury or product and proposition roles rather than in corporate finance or advisory.",
        struct_nl="De bank is opgebouwd rond retailactiviteiten, sparen, betalen en hypotheken, aangeboden via de merken, aangevuld met centrale functies zoals risk, finance, treasury en duurzaamheid. Ook beheert de bank een reeks duurzame beleggingsfondsen onder de ASN-naam. Finance-afgestudeerden starten doorgaans in risk, finance, treasury of product- en propositierollen, eerder dan in corporate finance of advies.",
        paths=[("corporate-finance","Corporate Finance"),("risk-management","Risk Management")],
        join_en="Entry is mainly through traineeships, internships and working-student roles in risk, finance and product teams; the bank does not run large dealmaking or markets-focused graduate tracks.",
        join_nl="Instroom verloopt vooral via traineeships, stages en werkstudentplekken bij risk-, finance- en productteams; de bank kent geen grote dealmaking- of marktengerichte graduate-tracks.",
        facts=[("Type","Type","Bank (retail)","Bank (retail)"),("Head office","Hoofdkantoor","Utrecht","Utrecht"),
            ("Founded","Opgericht","Predecessor SNS Bank dates to the 19th century; de Volksbank name adopted in 2013, renamed ASN Bank N.V. in 2025","Voorganger SNS Bank gaat terug tot de 19e eeuw; naam de Volksbank sinds 2013, in 2025 hernoemd tot ASN Bank N.V."),
            ("Ownership","Eigendom","State-owned (via NLFI)","Staatseigendom (via NLFI)")]),

    dict(slug="van-lanschot-kempen", name="Van Lanschot Kempen", initials="VK", color="#1c3f60", city="'s-Hertogenbosch",
        types=["bank","asset-management"], site="https://www.vanlanschotkempen.com",
        tagline_en="The Netherlands' oldest independent financial institution, combining private banking, merchant banking and investment management.",
        tagline_nl="De oudste onafhankelijke financiële instelling van Nederland, met private banking, merchant banking en vermogensbeheer.",
        intro_en="Van Lanschot Kempen traces its origins to 1737, when the Van Lanschot trading and banking house was founded in 's-Hertogenbosch, making it the oldest independent financial institution in the Netherlands. In 2007 Van Lanschot acquired merchant bank Kempen & Co, known for its equity capital markets, M&A advisory and institutional asset management activities, and the combined group adopted the name Van Lanschot Kempen in 2017. Kempen's investment management arm, long known as Kempen Capital Management, was renamed Van Lanschot Kempen Investment Management in 2023. The group is listed on Euronext Amsterdam through depositary receipts and focuses on wealth management, investment banking and asset management for private clients, entrepreneurs and institutional investors.",
        intro_nl="Van Lanschot Kempen gaat terug tot 1737, toen het handels- en bankhuis Van Lanschot werd opgericht in 's-Hertogenbosch, waarmee het de oudste onafhankelijke financiële instelling van Nederland is. In 2007 nam Van Lanschot merchant bank Kempen & Co over, bekend van aandelenkapitaalmarkten, M&A-advies en institutioneel vermogensbeheer, en in 2017 nam de gecombineerde groep de naam Van Lanschot Kempen aan. De vermogensbeheertak van Kempen, lang bekend als Kempen Capital Management, werd in 2023 hernoemd tot Van Lanschot Kempen Investment Management. De groep staat via certificaten genoteerd aan Euronext Amsterdam en richt zich op wealth management, investment banking en vermogensbeheer voor particuliere klanten, ondernemers en institutionele beleggers.",
        nl_en="The statutory head office is in 's-Hertogenbosch, with a large office presence in Amsterdam, where much of the investment banking and asset management activity, including the former Kempen Capital Management business, is based. For finance students, Van Lanschot Kempen offers exposure to both private banking and dealmaking, through corporate finance, equity capital markets and institutional asset management teams.",
        nl_nl="Het statutaire hoofdkantoor staat in 's-Hertogenbosch, met een grote vestiging in Amsterdam, waar een groot deel van de investment banking- en vermogensbeheeractiviteiten zit, inclusief het voormalige Kempen Capital Management. Voor finance-studenten biedt Van Lanschot Kempen inzicht in zowel private banking als dealmaking, via corporate finance, aandelenkapitaalmarkten en institutionele vermogensbeheerteams.",
        struct_en="The group operates through a few main divisions: Private Banking, serving wealthy individuals and entrepreneurs; Investment Banking, covering corporate finance, equity capital markets and M&A advisory under the Kempen name; and Investment Management, running institutional and fund strategies for pension funds, insurers and other investors. Finance graduates typically join through the investment banking or investment management divisions, or through private banking advisory roles.",
        struct_nl="De groep is opgebouwd rond een aantal hoofdonderdelen: Private Banking, gericht op vermogende particulieren en ondernemers; Investment Banking, met corporate finance, aandelenkapitaalmarkten en M&A-advies onder de naam Kempen; en Investment Management, met institutionele en fondsstrategieën voor pensioenfondsen, verzekeraars en andere beleggers. Finance-afgestudeerden komen doorgaans binnen via investment banking of investment management, of via adviesrollen binnen private banking.",
        paths=[("investment-banking","Investment Banking"),("ma","M&A"),("wealth-management","Wealth Management & Private Banking")],
        join_en="Students typically join through internships, analyst and graduate programmes within investment banking or investment management, or through working-student roles across private banking and advisory teams.",
        join_nl="Studenten stromen doorgaans in via stages, analisten- en graduate-programma's binnen investment banking of investment management, of via werkstudentplekken bij private banking en adviesteams.",
        facts=[("Type","Type","Bank and asset manager","Bank en vermogensbeheerder"),("Head office","Hoofdkantoor","'s-Hertogenbosch","'s-Hertogenbosch"),
            ("Founded","Opgericht","1737","1737"),
            ("Ownership","Eigendom","Listed (Euronext Amsterdam, via depositary receipts)","Beursgenoteerd (Euronext Amsterdam, via certificaten)")]),

    dict(slug="nibc-bank", name="NIBC Bank", initials="NB", color="#c8102e", city="The Hague",
        types=["bank","pe-dealmaking"], site="https://www.nibc.com",
        tagline_en="A Dutch corporate and merchant bank focused on financing and advisory for mid-sized companies and specialist sectors.",
        tagline_nl="Een Nederlandse corporate en merchant bank gericht op financiering en advies voor middelgrote bedrijven en specialistische sectoren.",
        intro_en="NIBC Bank was founded in 1945 by the Dutch government and a group of commercial banks and institutional investors, originally to help finance the country's post-war economic recovery. Over the decades it evolved into a corporate and merchant bank, with activities in corporate lending, savings, mortgages and financing for sectors such as commercial real estate and infrastructure. NIBC was listed on Euronext Amsterdam in 2018 before being acquired by private equity firm Blackstone in 2020. In late 2025, ABN AMRO agreed to acquire NIBC from Blackstone, a deal expected to complete during the course of 2026.",
        intro_nl="NIBC Bank werd in 1945 opgericht door de Nederlandse overheid samen met een groep handelsbanken en institutionele beleggers, oorspronkelijk om de naoorlogse economische wederopbouw van Nederland te financieren. In de loop der decennia ontwikkelde de bank zich tot een corporate en merchant bank, met activiteiten in zakelijke kredietverlening, sparen, hypotheken en financiering voor sectoren als commercieel vastgoed en infrastructuur. NIBC ging in 2018 naar de beurs op Euronext Amsterdam, voordat private-equityhuis Blackstone de bank in 2020 overnam. Eind 2025 kwam ABN AMRO een overname van NIBC van Blackstone overeen, een deal die naar verwachting in de loop van 2026 wordt afgerond.",
        nl_en="NIBC's head office is in The Hague, and the bank is a notable, specialist employer within Dutch corporate finance and structured lending. For finance students it offers exposure to deal-oriented work in corporate and leveraged finance, real estate and infrastructure finance, and advisory, in a smaller and more transaction-focused setting than the large universal banks.",
        nl_nl="Het hoofdkantoor van NIBC staat in Den Haag, en de bank is een opvallende, specialistische werkgever binnen de Nederlandse corporate finance en structured lending. Voor finance-studenten biedt NIBC inzicht in dealgericht werk binnen corporate en leveraged finance, vastgoed- en infrastructuurfinanciering en advies, in een kleinere en meer transactiegerichte omgeving dan de grote universele banken.",
        struct_en="NIBC is organised around Corporate Banking, covering lending and advisory for corporates in sectors such as real estate, infrastructure and shipping, and Retail Banking, which provides savings and mortgages to consumers, mainly through online brands. Finance graduates typically start in corporate banking, in sector or product teams, or in risk and finance functions.",
        struct_nl="NIBC is opgebouwd rond Corporate Banking, met kredietverlening en advies voor bedrijven in sectoren als vastgoed, infrastructuur en scheepvaart, en Retail Banking, dat sparen en hypotheken aanbiedt aan consumenten, vooral via online merken. Finance-afgestudeerden starten doorgaans binnen corporate banking, in sector- of productteams, of in risk- en financefuncties.",
        paths=[("corporate-finance","Corporate Finance"),("ma","M&A"),("risk-management","Risk Management")],
        join_en="NIBC recruits through internships, analyst and graduate programmes within corporate banking, and working-student roles across risk, finance and origination teams.",
        join_nl="NIBC werft via stages, analisten- en graduate-programma's binnen corporate banking, en werkstudentplekken bij risk-, finance- en origination-teams.",
        facts=[("Type","Type","Bank (corporate/merchant bank, dealmaking advisory)","Bank (corporate/merchant bank, dealmaking en advies)"),
            ("Head office","Hoofdkantoor","The Hague","Den Haag"),
            ("Founded","Opgericht","1945","1945"),
            ("Ownership","Eigendom","Privately owned (Blackstone); acquisition by ABN AMRO agreed in 2025, expected to complete in 2026","Privaat eigendom (Blackstone); overname door ABN AMRO overeengekomen in 2025, verwachte afronding in 2026")]),

    dict(slug="triodos-bank", name="Triodos Bank", initials="TB", color="#1a6b4a", city="Zeist",
        types=["bank","asset-management"], site="https://www.triodos.com",
        tagline_en="A values-driven bank that finances only sustainable enterprises, with its own investment management arm.",
        tagline_nl="Een missiegedreven bank die uitsluitend duurzame ondernemingen financiert, met een eigen vermogensbeheertak.",
        intro_en="Triodos Bank was founded in 1980 in the Netherlands, growing out of study groups from the late 1960s that explored alternative, values-based approaches to finance. From the start it set out to lend only to organisations and projects with social, cultural or environmental value, such as renewable energy, organic farming and social housing. The bank operates across several European countries in addition to the Netherlands, and alongside its banking activities it runs Triodos Investment Management, launched in 1999 to offer sustainable investment funds to institutional and private investors. Triodos Bank is not listed on a stock exchange in the ordinary sense: its shares are held by a dedicated foundation, and investors instead hold depository receipts.",
        intro_nl="Triodos Bank werd in 1980 opgericht in Nederland, voortkomend uit studiegroepen uit de late jaren zestig die alternatieve, waardengedreven benaderingen van financiën verkenden. Vanaf het begin financierde de bank uitsluitend organisaties en projecten met sociale, culturele of ecologische waarde, zoals duurzame energie, biologische landbouw en sociale huisvesting. Naast Nederland is de bank actief in meerdere Europese landen, en naast het bankbedrijf voert Triodos ook Triodos Investment Management, opgericht in 1999 om duurzame beleggingsfondsen aan te bieden aan institutionele en particuliere beleggers. Triodos Bank staat niet op een reguliere manier op de beurs: de aandelen worden gehouden door een speciale stichting, en beleggers houden in plaats daarvan certificaten.",
        nl_en="Triodos Bank's head office is in Zeist, near Utrecht, and the bank is a distinctive employer for finance students interested in sustainable and impact finance rather than conventional dealmaking. Roles here typically combine financial analysis with sector expertise in areas such as renewable energy, social housing and sustainable food and agriculture.",
        nl_nl="Het hoofdkantoor van Triodos Bank staat in Zeist, bij Utrecht, en de bank is een opvallende werkgever voor finance-studenten die geïnteresseerd zijn in duurzame en impactfinanciering in plaats van conventionele dealmaking. Functies hier combineren doorgaans financiële analyse met sectorkennis op gebieden als duurzame energie, sociale huisvesting en duurzame voeding en landbouw.",
        struct_en="The organisation is built around retail and business banking, which finances sustainable enterprises and offers savings and payment services, and Triodos Investment Management, which manages funds investing in areas such as energy transition, financial inclusion and sustainable food and agriculture. Finance graduates typically start in lending or sector teams within the bank, or as analysts within the investment management funds.",
        struct_nl="De organisatie is opgebouwd rond retail- en zakelijke bankdiensten, die duurzame ondernemingen financieren en spaar- en betaaldiensten aanbieden, en Triodos Investment Management, dat fondsen beheert die investeren in onder meer energietransitie, financiële inclusie en duurzame voeding en landbouw. Finance-afgestudeerden starten doorgaans in kredietverlenings- of sectorteams binnen de bank, of als analist binnen de beleggingsfondsen.",
        paths=[("asset-management","Asset Management"),("corporate-finance","Corporate Finance")],
        join_en="Entry is generally through internships, traineeships and working-student roles within lending, sector teams or the investment management funds, with fewer positions overall than at the large universal banks.",
        join_nl="Instroom verloopt over het algemeen via stages, traineeships en werkstudentplekken bij kredietverlening, sectorteams of de beleggingsfondsen, met minder posities in totaal dan bij de grote universele banken.",
        facts=[("Type","Type","Bank and asset manager","Bank en vermogensbeheerder"),("Head office","Hoofdkantoor","Zeist","Zeist"),
            ("Founded","Opgericht","1980","1980"),
            ("Ownership","Eigendom","Owned via a foundation (SAAT); investors hold depository receipts","Eigendom via een stichting (SAAT); beleggers houden certificaten")]),

    dict(slug="bng-bank", name="BNG Bank", initials="BN", color="#0b2545", city="The Hague",
        types=["bank"], site="https://www.bngbank.com",
        tagline_en="A public-sector bank financing Dutch municipalities, provinces, water boards and public institutions.",
        tagline_nl="Een publieke sectorbank die Nederlandse gemeenten, provincies, waterschappen en publieke instellingen financiert.",
        intro_en="BNG Bank was founded in 1914 by the Association of Dutch Municipalities as a credit institution to fund local government investment. Over time it grew into the Bank Nederlandse Gemeenten, and it has carried the name BNG Bank since 2018. The bank does not serve private customers: it exclusively finances the Dutch public sector, including municipalities, provinces, water boards, public housing corporations and healthcare and education institutions. Its shares are held half by the Dutch State and half by municipalities, provinces and a water board, reflecting its role as a public-sector financing institution rather than a commercial bank.",
        intro_nl="BNG Bank werd in 1914 opgericht door de Vereniging van Nederlandse Gemeenten als kredietinstelling om investeringen van lokale overheden te financieren. In de loop der tijd groeide de bank uit tot de Bank Nederlandse Gemeenten, en sinds 2018 draagt zij de naam BNG Bank. De bank bedient geen particuliere klanten: zij financiert uitsluitend de Nederlandse publieke sector, waaronder gemeenten, provincies, waterschappen, woningcorporaties en zorg- en onderwijsinstellingen. De aandelen zijn voor de helft in handen van de Nederlandse Staat en voor de helft van gemeenten, provincies en een waterschap, wat haar rol als publieke financieringsinstelling onderstreept in plaats van een commerciële bank.",
        nl_en="BNG Bank's head office is in The Hague, close to the ministries and public bodies it works with. For finance students, the bank offers a specialist environment focused on public-sector funding, capital markets issuance and sustainability-linked financing, rather than retail or investment banking in the traditional sense.",
        nl_nl="Het hoofdkantoor van BNG Bank staat in Den Haag, dicht bij de ministeries en publieke instanties waarmee de bank samenwerkt. Voor finance-studenten biedt de bank een specialistische omgeving gericht op publieke financiering, kapitaalmarktuitgiftes en duurzaamheidsgerelateerde financiering, in plaats van traditionele retail- of investment banking.",
        struct_en="BNG Bank is organised around lending to public-sector clients, treasury and capital markets funding, since the bank itself borrows extensively on international capital markets to fund its lending, and risk management. Finance graduates typically start in treasury, funding, credit or risk roles, working closely with public-sector clients and institutional investors.",
        struct_nl="BNG Bank is opgebouwd rond kredietverlening aan publieke klanten, treasury en kapitaalmarktfinanciering, aangezien de bank zelf op grote schaal leent op internationale kapitaalmarkten om haar kredietverlening te financieren, en risicomanagement. Finance-afgestudeerden starten doorgaans in treasury-, funding-, krediet- of riskrollen, in nauwe samenwerking met publieke klanten en institutionele beleggers.",
        paths=[("debt-advisory","Debt Advisory"),("corporate-finance","Corporate Finance"),("risk-management","Risk Management")],
        join_en="BNG Bank recruits a relatively small number of graduates each year through traineeships, internships and working-student roles in treasury, credit and risk functions.",
        join_nl="BNG Bank werft jaarlijks een relatief klein aantal afgestudeerden via traineeships, stages en werkstudentplekken bij treasury-, krediet- en riskfuncties.",
        facts=[("Type","Type","Bank (public sector)","Bank (publieke sector)"),("Head office","Hoofdkantoor","The Hague","Den Haag"),
            ("Founded","Opgericht","1914","1914"),
            ("Ownership","Eigendom","State and public authorities (50% Dutch State, 50% municipalities, provinces and a water board)","Staat en publieke instanties (50% Nederlandse Staat, 50% gemeenten, provincies en een waterschap)")]),

    dict(slug="nwb-bank", name="NWB Bank", initials="NW", color="#007a87", city="The Hague",
        types=["bank"], site="https://www.nwbbank.com",
        tagline_en="The Dutch water authorities' bank, financing water management and public infrastructure.",
        tagline_nl="De bank van de Nederlandse waterschappen, gericht op de financiering van waterbeheer en publieke infrastructuur.",
        intro_en="NWB Bank, the Nederlandse Waterschapsbank, was founded in 1954 to help the Dutch water boards finance the large-scale investment needed for flood defence and water management. It has since broadened its lending to other parts of the public sector, including municipalities, provinces, housing corporations and healthcare institutions, but water authorities remain central to its identity and ownership. Like BNG Bank, NWB Bank does not serve private customers and instead raises funds on international capital markets to finance public-sector borrowers, typically at favourable rates reflecting the strength of its public shareholders.",
        intro_nl="NWB Bank, de Nederlandse Waterschapsbank, werd in 1954 opgericht om de Nederlandse waterschappen te helpen bij het financieren van de grootschalige investeringen die nodig zijn voor waterveiligheid en waterbeheer. Sindsdien heeft de bank haar kredietverlening verbreed naar andere delen van de publieke sector, waaronder gemeenten, provincies, woningcorporaties en zorginstellingen, maar de waterschappen blijven centraal staan in haar identiteit en aandeelhouderschap. Net als BNG Bank bedient NWB Bank geen particuliere klanten en haalt de bank in plaats daarvan financiering op via internationale kapitaalmarkten om publieke kredietnemers te financieren, doorgaans tegen gunstige tarieven dankzij de kracht van haar publieke aandeelhouders.",
        nl_en="NWB Bank's head office is in The Hague, and the bank is a small but distinctive employer within Dutch public-sector finance. Finance students will find relevant work in treasury, funding and credit analysis, in an organisation closely tied to water management and broader public infrastructure financing.",
        nl_nl="Het hoofdkantoor van NWB Bank staat in Den Haag, en de bank is een kleine maar herkenbare werkgever binnen de Nederlandse publieke financiering. Finance-studenten vinden hier relevant werk in treasury, funding en kredietanalyse, binnen een organisatie die nauw verbonden is met waterbeheer en bredere publieke infrastructuurfinanciering.",
        struct_en="NWB Bank is organised around lending to public authorities and related institutions, treasury and capital markets funding, and risk management. Because the bank funds itself almost entirely through international bond issuance, treasury and funding roles are especially central, alongside credit analysis for public-sector borrowers.",
        struct_nl="NWB Bank is opgebouwd rond kredietverlening aan publieke instanties en gerelateerde instellingen, treasury en kapitaalmarktfinanciering, en risicomanagement. Omdat de bank zichzelf vrijwel volledig financiert via internationale obligatie-uitgiftes, zijn treasury- en fundingrollen bijzonder centraal, naast kredietanalyse voor publieke kredietnemers.",
        paths=[("debt-advisory","Debt Advisory"),("corporate-finance","Corporate Finance"),("risk-management","Risk Management")],
        join_en="As a small, specialist bank, NWB Bank offers a limited number of internships, working-student roles and entry-level positions, mainly within treasury, funding and credit functions.",
        join_nl="Als kleine, specialistische bank biedt NWB Bank een beperkt aantal stages, werkstudentplekken en startersfuncties, vooral binnen treasury-, funding- en kredietfuncties.",
        facts=[("Type","Type","Bank (public sector, water authorities)","Bank (publieke sector, waterschappen)"),
            ("Head office","Hoofdkantoor","The Hague","Den Haag"),
            ("Founded","Opgericht","1954","1954"),
            ("Ownership","Eigendom","Public authorities (Dutch water boards, state and provinces)","Publieke instanties (Nederlandse waterschappen, Rijk en provincies)")]),

    dict(slug="bunq", name="bunq", initials="BQ", color="#e0447c", city="Amsterdam",
        types=["bank"], site="https://www.bunq.com",
        tagline_en="A Dutch neobank offering fully digital banking across Europe, with no physical branches.",
        tagline_nl="Een Nederlandse neobank met volledig digitaal bankieren in Europa, zonder fysieke kantoren.",
        intro_en="bunq was founded in 2012 by entrepreneur Ali Niknam, who had previously founded web hosting company TransIP, and received its own European banking licence from the Dutch central bank, De Nederlandsche Bank, in 2014. It positions itself as a mobile-first, fully digital bank aimed at people who live and work across borders, offering payment accounts and related services through its app rather than physical branches. bunq grew mainly on the back of its founder's own investment before raising external funding, and by the early 2020s had become one of the larger neobanks in the European Union, expanding its licensed operations across dozens of European countries.",
        intro_nl="bunq werd in 2012 opgericht door ondernemer Ali Niknam, die eerder hostingbedrijf TransIP had opgericht, en kreeg in 2014 een eigen Europese bankvergunning van De Nederlandsche Bank. De bank positioneert zich als een mobile-first, volledig digitale bank gericht op mensen die grensoverschrijdend leven en werken, met betaalrekeningen en aanverwante diensten via de app in plaats van fysieke kantoren. bunq groeide vooral dankzij de eigen investeringen van de oprichter voordat externe financiering werd opgehaald, en werd begin jaren twintig een van de grotere neobanken van de Europese Unie, met vergunningen in tientallen Europese landen.",
        nl_en="bunq's head office is in Amsterdam, and the company is a notable employer among Dutch fintechs for finance and business students interested in digital banking, product and risk. Because it operates without branches, roles tend to combine financial expertise with technology and product development rather than traditional relationship banking.",
        nl_nl="Het hoofdkantoor van bunq staat in Amsterdam, en het bedrijf is een opvallende werkgever onder Nederlandse fintechs voor finance- en bedrijfskundestudenten die geïnteresseerd zijn in digitaal bankieren, product en risk. Omdat de bank zonder kantoren opereert, combineren functies vaak financiële expertise met technologie en productontwikkeling, in plaats van traditioneel relatiebeheer.",
        struct_en="bunq is organised around its digital banking product, with teams covering areas such as risk and compliance, finance and treasury, and product and engineering, all built around a single app-based platform. Finance-oriented graduates typically work in risk, compliance, finance or treasury functions, often alongside product and data teams given the company's technology-driven culture.",
        struct_nl="bunq is opgebouwd rond het digitale bankproduct, met teams op het gebied van onder meer risk en compliance, finance en treasury, en product en engineering, allemaal gebouwd rond één app-gebaseerd platform. Finance-gerichte afgestudeerden werken doorgaans in risk-, compliance-, finance- of treasuryfuncties, vaak in samenwerking met product- en data-teams gezien de technologiegedreven cultuur van het bedrijf.",
        paths=[("corporate-finance","Corporate Finance"),("risk-management","Risk Management")],
        join_en="bunq recruits mainly through internships, working-student roles and direct hires rather than large structured graduate programmes, reflecting its smaller, fast-moving organisation compared with the traditional banks.",
        join_nl="bunq werft vooral via stages, werkstudentplekken en directe aanstellingen in plaats van grote gestructureerde graduate-programma's, passend bij de kleinere, snel bewegende organisatie in vergelijking met de traditionele banken.",
        facts=[("Type","Type","Bank (digital-only neobank)","Bank (volledig digitale neobank)"),
            ("Head office","Hoofdkantoor","Amsterdam","Amsterdam"),
            ("Founded","Opgericht","2012 (banking licence granted in 2014)","2012 (bankvergunning verkregen in 2014)"),
            ("Ownership","Eigendom","Privately owned (founder-led)","Privaat eigendom (onder leiding van de oprichter)")]),

dict(slug="goldman-sachs", name="Goldman Sachs", initials="GS", color="#7399c6", city="The Hague",
     types=["bank","asset-management"], site="https://www.goldmansachs.com",
     tagline_en="A leading global investment bank, with its Dutch asset management arm based in The Hague.",
     tagline_nl="Een toonaangevende wereldwijde investeringsbank, met haar Nederlandse vermogensbeheertak gevestigd in Den Haag.",
     intro_en="Goldman Sachs is a global investment bank and financial services firm headquartered in New York. Founded in 1869, it grew from a commercial paper business into one of the world's largest players in investment banking, securities trading, asset management and wealth management. The firm advises corporations, governments and institutions on mergers, capital raising and financing, and its trading and asset management arms serve clients worldwide. Goldman Sachs is listed on the New York Stock Exchange.",
     intro_nl="Goldman Sachs is een wereldwijde investeringsbank en financiële dienstverlener met hoofdkantoor in New York. De bank werd in 1869 opgericht en groeide van een handel in commercial paper uit tot een van de grootste spelers ter wereld in investment banking, effectenhandel, vermogensbeheer en wealth management. Goldman Sachs adviseert bedrijven, overheden en instellingen bij fusies, overnames en financiering, en de trading- en asset-managementtakken bedienen klanten wereldwijd. De bank staat genoteerd aan de New York Stock Exchange.",
     nl_en="Goldman Sachs has long had a presence in Amsterdam for its banking and markets business, but its most significant Dutch footprint came in 2022, when it completed the acquisition of NN Investment Partners, the asset manager based in The Hague that had grown out of Dutch insurer NN Group. That business was integrated into Goldman Sachs Asset Management, making The Hague an important European location for the firm and a centre of expertise in sustainable investing within public markets. For finance students, this means Goldman Sachs offers both classic investment banking exposure through its Amsterdam office and asset management roles through the former NN IP operation in The Hague.",
     nl_nl="Goldman Sachs is al langer aanwezig in Amsterdam met bankieren en markets, maar de belangrijkste Nederlandse stap kwam in 2022, toen de overname van NN Investment Partners werd afgerond. Deze vermogensbeheerder, gevestigd in Den Haag en voortgekomen uit de Nederlandse verzekeraar NN Group, werd geïntegreerd in Goldman Sachs Asset Management. Daarmee werd Den Haag een belangrijke Europese vestigingsplaats voor de bank en een centrum voor duurzaam beleggen binnen publieke markten. Voor finance-studenten betekent dit dat Goldman Sachs zowel klassieke investment banking biedt via het kantoor in Amsterdam, als vermogensbeheerfuncties via de voormalige NN IP-organisatie in Den Haag.",
     struct_en="In the Netherlands, Goldman Sachs operates through two distinct strands: the Amsterdam office, which covers investment banking coverage, markets and related client-facing work, and the Goldman Sachs Asset Management organisation in The Hague, which manages public and private market strategies including fixed income, equities and sustainability-focused mandates. Finance graduates typically join either through banking and markets functions or through portfolio management, research and client-facing roles within asset management.",
     struct_nl="In Nederland werkt Goldman Sachs via twee aparte onderdelen: het kantoor in Amsterdam, gericht op investment banking coverage, markets en aanverwant klantcontact, en de organisatie van Goldman Sachs Asset Management in Den Haag, die publieke en private marktstrategieën beheert, waaronder vastrentende waarden, aandelen en duurzaamheidsgerichte mandaten. Finance-afgestudeerden komen doorgaans binnen via banking- en marketsfuncties, of via portfoliomanagement, research en klantgerichte rollen binnen asset management.",
     paths=[("investment-banking","Investment Banking"),("asset-management","Asset Management"),("ma","M&A")],
     join_en="Goldman Sachs runs global summer analyst internships and graduate analyst programmes in investment banking and asset management, which are the main entry routes for students. The Hague office also recruits for asset management roles, including analyst and associate positions in investment and client-facing teams.",
     join_nl="Goldman Sachs biedt wereldwijd summer analyst-stages en graduate analyst-programma's aan in investment banking en asset management, de belangrijkste instapmogelijkheden voor studenten. Het kantoor in Den Haag werft ook voor asset-managementfuncties, waaronder analist- en associate-posities in investment- en klantgerichte teams.",
     facts=[("Type","Type","Bank and asset manager","Bank en vermogensbeheerder"),
       ("Head office","Hoofdkantoor","Global: New York / NL offices: Amsterdam and The Hague","Wereldwijd: New York / NL-kantoren: Amsterdam en Den Haag"),
       ("Founded","Opgericht","1869","1869"),
       ("Ownership","Eigendom","Listed (NYSE: GS)","Beursgenoteerd (NYSE: GS)")]),

  dict(slug="bnp-paribas", name="BNP Paribas", initials="BP", color="#00915a", city="Amsterdam",
     types=["bank"], site="https://www.bnpparibas.nl",
     tagline_en="A major French bank with a Dutch history going back to the 19th century.",
     tagline_nl="Een grote Franse bank met een Nederlandse geschiedenis die teruggaat tot de negentiende eeuw.",
     intro_en="BNP Paribas is one of Europe's largest banks, headquartered in Paris, with corporate and institutional banking, retail banking and asset management activities across the world. It was formed in 2000 through the merger of Banque Nationale de Paris and Paribas, itself a bank with roots in the 19th century. BNP Paribas is active in around seventy countries and is one of the largest banking groups in the eurozone. The bank is listed on Euronext Paris.",
     intro_nl="BNP Paribas is een van de grootste banken van Europa, met hoofdkantoor in Parijs en activiteiten in corporate en institutional banking, retailbankieren en vermogensbeheer wereldwijd. De bank ontstond in 2000 uit de fusie van Banque Nationale de Paris en Paribas, dat op zijn beurt wortels heeft in de negentiende eeuw. BNP Paribas is actief in ongeveer zeventig landen en is een van de grootste bankgroepen van de eurozone. De bank staat genoteerd aan Euronext Parijs.",
     nl_en="BNP Paribas has an unusually long history in the Netherlands: one of its predecessor banks was founded in Amsterdam in 1863, and the Paribas name itself grew out of a Dutch-French merger in 1872. Today the Amsterdam office focuses on corporate and institutional banking for Dutch and international clients. Finance students will mainly find corporate banking, markets and transaction banking work here.",
     nl_nl="BNP Paribas heeft een ongewoon lange geschiedenis in Nederland: een van de voorlopers van de bank werd al in 1863 in Amsterdam opgericht, en de naam Paribas zelf ontstond in 1872 uit een Nederlands-Franse fusie. Tegenwoordig richt het kantoor in Amsterdam zich op corporate en institutional banking voor Nederlandse en internationale klanten. Finance-studenten vinden hier vooral werk binnen corporate banking, markets en transaction banking.",
     struct_en="In the Netherlands, BNP Paribas operates as part of its Corporate & Institutional Banking division, covering corporate clients, financial institutions and markets activity, alongside smaller specialist units such as equipment and car fleet financing. Finance graduates typically start in corporate banking coverage, markets, or transaction banking and cash management roles.",
     struct_nl="In Nederland opereert BNP Paribas als onderdeel van de divisie Corporate & Institutional Banking, gericht op zakelijke klanten, financiële instellingen en markets-activiteiten, naast kleinere gespecialiseerde onderdelen zoals financiering van bedrijfsmiddelen en wagenparken. Finance-afgestudeerden starten doorgaans in corporate banking coverage, markets, of transaction banking en cash management.",
     paths=[("corporate-finance","Corporate Finance"),("investment-banking","Investment Banking"),("transaction-services","Transaction Services")],
     join_en="Entry is typically through internships and graduate programmes within BNP Paribas' European corporate and institutional banking recruitment, which places graduates into coverage, markets or transaction banking teams, including in Amsterdam.",
     join_nl="Instroom verloopt doorgaans via stages en graduate-programma's binnen de Europese werving van BNP Paribas voor corporate en institutional banking, waarbij afgestudeerden terechtkomen in coverage-, markets- of transaction bankingteams, ook in Amsterdam.",
     facts=[("Type","Type","Bank","Bank"),
       ("Head office","Hoofdkantoor","Global: Paris / NL office: Amsterdam","Wereldwijd: Parijs / NL-kantoor: Amsterdam"),
       ("Founded","Opgericht","2000 (merger); Dutch roots from 1863","2000 (fusie); Nederlandse wortels vanaf 1863"),
       ("Ownership","Eigendom","Listed (Euronext Paris)","Beursgenoteerd (Euronext Parijs)")]),

  dict(slug="mufg-bank", name="MUFG Bank", initials="MU", color="#e60012", city="Amsterdam",
     types=["bank"], site="https://www.mufgemea.com",
     tagline_en="Japan's largest bank, which chose Amsterdam as its EU booking hub after Brexit.",
     tagline_nl="De grootste bank van Japan, die na de brexit Amsterdam koos als EU-vestigingsplaats.",
     intro_en="MUFG Bank is part of Mitsubishi UFJ Financial Group, Japan's largest financial group, headquartered in Tokyo. The current group was formed through a series of mergers of Japanese banking houses with histories going back to the 19th and early 20th centuries, most notably the 2005 merger that created Mitsubishi UFJ Financial Group. MUFG is one of the largest banks in the world by assets, active in commercial banking, trust banking and securities across Asia, the Americas and Europe. Mitsubishi UFJ Financial Group is listed on the Tokyo Stock Exchange.",
     intro_nl="MUFG Bank maakt deel uit van Mitsubishi UFJ Financial Group, de grootste financiële groep van Japan, met hoofdkantoor in Tokio. De huidige groep ontstond uit een reeks fusies van Japanse bankhuizen met een geschiedenis die teruggaat tot de negentiende en vroege twintigste eeuw, met als belangrijkste stap de fusie in 2005 die Mitsubishi UFJ Financial Group vormde. MUFG behoort tot de grootste banken ter wereld naar balanstotaal en is actief in commercial banking, trust banking en effectenzaken in Azië, Amerika en Europa. Mitsubishi UFJ Financial Group staat genoteerd aan de beurs van Tokio.",
     nl_en="MUFG chose Amsterdam in 2017 as the location for its new EU banking subsidiary, MUFG Bank (Europe) N.V., in order to keep serving EU clients after the United Kingdom left the European Union and the bank could no longer rely on passporting rights from London. Amsterdam now functions as the hub in MUFG's European hub-and-spoke model, handling capital, risk management, regulatory reporting and back-office processing for its European branch network. For finance students, this means an office focused on corporate and investment banking, risk and finance functions supporting European clients.",
     nl_nl="MUFG koos in 2017 voor Amsterdam als vestigingsplaats voor haar nieuwe EU-bankdochter, MUFG Bank (Europe) N.V., om EU-klanten te kunnen blijven bedienen nadat het Verenigd Koninkrijk de Europese Unie verliet en de bank niet langer kon rekenen op passporting-rechten vanuit Londen. Amsterdam functioneert nu als spil in het Europese hub-and-spoke-model van MUFG, met kapitaal, risicomanagement, regelgevende rapportage en backofficeverwerking voor het Europese kantorennetwerk. Voor finance-studenten betekent dit een kantoor gericht op corporate en investment banking, risk en finance ter ondersteuning van Europese klanten.",
     struct_en="MUFG Bank (Europe) N.V. in Amsterdam is organised around corporate and investment banking coverage for European clients, alongside risk, finance, treasury and regulatory functions that support the wider European branch network from the Amsterdam hub. Finance graduates typically join through coverage, risk or finance teams.",
     struct_nl="MUFG Bank (Europe) N.V. in Amsterdam is opgebouwd rond corporate en investment banking coverage voor Europese klanten, samen met risk-, finance-, treasury- en regelgevingsfuncties die vanuit de Amsterdamse hub het bredere Europese kantorennetwerk ondersteunen. Finance-afgestudeerden komen doorgaans binnen via coverage-, risk- of financeteams.",
     paths=[("corporate-finance","Corporate Finance"),("investment-banking","Investment Banking"),("risk-management","Risk Management")],
     join_en="MUFG recruits in Amsterdam mainly through internships and graduate or analyst positions within its European corporate banking, risk and finance functions; opportunities are more limited in number than at the larger universal banks given the size of the Amsterdam office.",
     join_nl="MUFG werft in Amsterdam vooral via stages en graduate- of analistenposities binnen de Europese corporate banking-, risk- en financefuncties; het aantal mogelijkheden is beperkter dan bij de grotere universele banken, gezien de omvang van het Amsterdamse kantoor.",
     facts=[("Type","Type","Bank","Bank"),
       ("Head office","Hoofdkantoor","Global: Tokyo / NL office: Amsterdam (EU banking hub)","Wereldwijd: Tokio / NL-kantoor: Amsterdam (EU-bankhub)"),
       ("Founded","Opgericht","MUFG formed 2005; Amsterdam EU entity established 2017-2018","MUFG gevormd in 2005; EU-entiteit in Amsterdam opgericht in 2017-2018"),
       ("Ownership","Eigendom","Listed parent, Mitsubishi UFJ Financial Group (Tokyo Stock Exchange)","Beursgenoteerde moeder, Mitsubishi UFJ Financial Group (beurs van Tokio)")]),

  dict(slug="jpmorgan", name="J.P. Morgan", initials="JM", color="#5a7fa6", city="Amsterdam",
     types=["bank"], site="https://www.jpmorgan.com/NL/en/about-us",
     tagline_en="One of the world's largest banks, with an Amsterdam branch serving as part of its EU network.",
     tagline_nl="Een van de grootste banken ter wereld, met een Amsterdams kantoor als onderdeel van haar EU-netwerk.",
     intro_en="J.P. Morgan is the corporate and investment banking arm of JPMorgan Chase & Co, one of the largest banks in the world by assets, headquartered in New York. Its history traces back to banking houses from the 19th century, including J.P. Morgan & Co., with the modern group formed through the 2000 merger of J.P. Morgan and Chase Manhattan. The firm offers investment banking, markets, asset management and commercial banking services to corporations, governments and institutions worldwide. JPMorgan Chase & Co. is listed on the New York Stock Exchange.",
     intro_nl="J.P. Morgan is de corporate en investment banking-tak van JPMorgan Chase & Co, een van de grootste banken ter wereld naar balanstotaal, met hoofdkantoor in New York. De geschiedenis gaat terug tot negentiende-eeuwse bankhuizen, waaronder J.P. Morgan & Co., en de huidige groep ontstond in 2000 uit de fusie van J.P. Morgan en Chase Manhattan. De bank biedt investment banking, markets, asset management en commercial banking aan bedrijven, overheden en instellingen wereldwijd. JPMorgan Chase & Co. staat genoteerd aan de New York Stock Exchange.",
     nl_en="J.P. Morgan has had a presence in Amsterdam for years, but restructured its European legal entities after Brexit: since 2020 the Amsterdam office operates as a branch of J.P. Morgan SE, the bank's EU-licensed entity headquartered in Frankfurt. From Amsterdam, J.P. Morgan offers products and services spanning its Commercial & Investment Bank, Asset Management and Private Bank to Dutch clients. It is a comparatively small office relative to the bank's global scale, focused on client coverage and specific product lines rather than being a major employment centre.",
     nl_nl="J.P. Morgan is al jaren aanwezig in Amsterdam, maar herstructureerde na de brexit haar Europese juridische entiteiten: sinds 2020 opereert het Amsterdamse kantoor als bijkantoor van J.P. Morgan SE, de EU-vergunninghoudende entiteit van de bank met hoofdkantoor in Frankfurt. Vanuit Amsterdam biedt J.P. Morgan producten en diensten aan Nederlandse klanten binnen de Commercial & Investment Bank, Asset Management en Private Bank. Het is een relatief klein kantoor ten opzichte van de wereldwijde omvang van de bank, gericht op klantcontact en specifieke productlijnen, eerder dan een groot werkgelegenheidscentrum.",
     struct_en="The Amsterdam office covers coverage and origination for Dutch corporate and institutional clients, private banking for wealthy clients, and elements of asset management, operating as part of the wider J.P. Morgan SE structure headquartered in Frankfurt. Finance graduates who join in Amsterdam typically work in client coverage, markets-related roles, or private banking.",
     struct_nl="Het kantoor in Amsterdam richt zich op coverage en originatie voor Nederlandse zakelijke en institutionele klanten, private banking voor vermogende klanten, en onderdelen van asset management, als onderdeel van de bredere structuur van J.P. Morgan SE met hoofdkantoor in Frankfurt. Finance-afgestudeerden die in Amsterdam beginnen, werken doorgaans in klantcontact, markets-gerelateerde rollen of private banking.",
     paths=[("investment-banking","Investment Banking"),("corporate-finance","Corporate Finance"),("asset-management","Asset Management")],
     join_en="J.P. Morgan runs global summer internship and graduate analyst programmes in investment banking, markets and asset management, mostly based in larger European hubs such as London and Frankfurt; the Amsterdam office offers a smaller number of local roles and internships focused on Dutch client coverage.",
     join_nl="J.P. Morgan biedt wereldwijd summer internship- en graduate analyst-programma's aan in investment banking, markets en asset management, vooral gevestigd in grotere Europese hubs zoals Londen en Frankfurt; het kantoor in Amsterdam biedt een kleiner aantal lokale functies en stages gericht op Nederlandse klantbediening.",
     facts=[("Type","Type","Bank","Bank"),
       ("Head office","Hoofdkantoor","Global: New York / EU entity: Frankfurt / NL office: Amsterdam","Wereldwijd: New York / EU-entiteit: Frankfurt / NL-kantoor: Amsterdam"),
       ("Founded","Opgericht","Traces to the 19th century; current group formed 2000","Wortels in de negentiende eeuw; huidige groep gevormd in 2000"),
       ("Ownership","Eigendom","Listed (NYSE: JPM)","Beursgenoteerd (NYSE: JPM)")]),

  dict(slug="morgan-stanley", name="Morgan Stanley", initials="MS", color="#012a5e", city="Amsterdam",
     types=["bank"], site="https://www.morganstanley.com/about-us/global-offices/europe-middle-east-africa/netherlands",
     tagline_en="A major US investment bank with an Amsterdam office open since the late 1990s.",
     tagline_nl="Een grote Amerikaanse investeringsbank met een Amsterdams kantoor dat al sinds de late jaren negentig open is.",
     intro_en="Morgan Stanley is a global investment bank and financial services firm headquartered in New York, founded in 1935. It operates across institutional securities, wealth management and investment management, advising corporations, governments, institutions and individuals worldwide. The firm is one of the largest players in mergers and acquisitions advisory, equity and debt capital markets, and sales and trading. Morgan Stanley is listed on the New York Stock Exchange.",
     intro_nl="Morgan Stanley is een wereldwijde investeringsbank en financiële dienstverlener met hoofdkantoor in New York, opgericht in 1935. De bank is actief in institutional securities, wealth management en investment management, en adviseert bedrijven, overheden, instellingen en particulieren wereldwijd. Het is een van de grootste spelers in fusie- en overnameadvies, aandelen- en obligatiekapitaalmarkten, en sales en trading. Morgan Stanley staat genoteerd aan de New York Stock Exchange.",
     nl_en="Morgan Stanley opened its Amsterdam office in 1997, well before Brexit made the city a popular EU base for banks, and later established Morgan Stanley Europe SE as a Dutch-incorporated entity to support its EU business after the UK's departure from the EU. From Amsterdam the firm offers services spanning mergers and acquisitions advisory, corporate finance, equity and debt capital markets access, sales and trading, real estate investing and investment management. It remains a modest office relative to the firm's scale, focused on client coverage and specific product lines.",
     nl_nl="Morgan Stanley opende het kantoor in Amsterdam al in 1997, ruim voordat de brexit de stad populair maakte als EU-vestigingsplaats voor banken, en richtte later Morgan Stanley Europe SE op als Nederlandse entiteit ter ondersteuning van de EU-activiteiten na het vertrek van het VK uit de EU. Vanuit Amsterdam biedt de bank diensten op het gebied van fusie- en overnameadvies, corporate finance, toegang tot aandelen- en obligatiekapitaalmarkten, sales en trading, vastgoedinvesteringen en vermogensbeheer. Het blijft een bescheiden kantoor ten opzichte van de omvang van de bank, gericht op klantcontact en specifieke productlijnen.",
     struct_en="The Amsterdam office spans investment banking coverage for Dutch corporates, sales and trading functions connected to European markets, and elements of investment management. Finance graduates who join here typically work in corporate finance and M&A coverage, capital markets, or sales and trading support roles.",
     struct_nl="Het Amsterdamse kantoor omvat investment banking coverage voor Nederlandse bedrijven, sales- en tradingfuncties gekoppeld aan Europese markten, en onderdelen van investment management. Finance-afgestudeerden die hier beginnen, werken doorgaans in corporate finance- en M&A-coverage, capital markets, of ondersteunende sales- en tradingrollen.",
     paths=[("ma","M&A"),("investment-banking","Investment Banking"),("corporate-finance","Corporate Finance")],
     join_en="Morgan Stanley runs global summer analyst internships and graduate analyst programmes in investment banking and related divisions, primarily recruited through its larger European hubs; the Amsterdam office offers a smaller number of local roles tied to Dutch client coverage.",
     join_nl="Morgan Stanley biedt wereldwijd summer analyst-stages en graduate analyst-programma's aan in investment banking en aanverwante divisies, vooral geworven via de grotere Europese hubs; het kantoor in Amsterdam biedt een kleiner aantal lokale functies gekoppeld aan Nederlandse klantbediening.",
     facts=[("Type","Type","Bank","Bank"),
       ("Head office","Hoofdkantoor","Global: New York / NL office: Amsterdam","Wereldwijd: New York / NL-kantoor: Amsterdam"),
       ("Founded","Opgericht","1935; Amsterdam office opened 1997","1935; kantoor Amsterdam geopend in 1997"),
       ("Ownership","Eigendom","Listed (NYSE: MS)","Beursgenoteerd (NYSE: MS)")]),

  dict(slug="deutsche-bank", name="Deutsche Bank", initials="DB", color="#0018a8", city="Amsterdam",
     types=["bank"], site="https://www.deutschebank.nl",
     tagline_en="Germany's largest bank, with a Dutch presence stretching back more than a century.",
     tagline_nl="De grootste bank van Duitsland, met een Nederlandse aanwezigheid van meer dan een eeuw.",
     intro_en="Deutsche Bank is Germany's largest bank and a major global financial institution, headquartered in Frankfurt. Founded in 1870 to finance German trade with other European countries and overseas markets, it has grown into a universal bank spanning corporate and investment banking, private banking and asset management. It operates in dozens of countries and is one of the most systemically important banks in Europe. Deutsche Bank is listed on the Frankfurt Stock Exchange and the New York Stock Exchange.",
     intro_nl="Deutsche Bank is de grootste bank van Duitsland en een belangrijke wereldwijde financiële instelling, met hoofdkantoor in Frankfurt. De bank werd in 1870 opgericht om Duitse handel met andere Europese landen en overzeese markten te financieren, en groeide uit tot een universele bank met corporate en investment banking, private banking en asset management. Deutsche Bank is actief in tientallen landen en behoort tot de systeemrelevante banken van Europa. De bank staat genoteerd aan de beurs van Frankfurt en aan de New York Stock Exchange.",
     nl_en="Deutsche Bank has done business in the Netherlands for over a century, longer than most other international banks, and describes itself as the largest international bank operating in the country. Its Amsterdam office serves corporate and institutional clients through corporate and investment banking activities, distinct from the smaller Brexit-driven booking entities some other banks set up in the city. For finance students, this makes Deutsche Bank one of the more established international banks with a genuine long-term Dutch client business rather than a purely post-Brexit outpost.",
     nl_nl="Deutsche Bank doet al meer dan een eeuw zaken in Nederland, langer dan de meeste andere internationale banken, en noemt zichzelf de grootste internationale bank die actief is in het land. Het kantoor in Amsterdam bedient zakelijke en institutionele klanten via corporate en investment banking, en onderscheidt zich daarmee van de kleinere, door de brexit ontstane vestigingsentiteiten die sommige andere banken in de stad hebben opgezet. Voor finance-studenten maakt dit Deutsche Bank een van de meer gevestigde internationale banken met een echte langdurige Nederlandse klantenpraktijk, in plaats van een puur post-brexit vestiging.",
     struct_en="In the Netherlands, Deutsche Bank organises its business around Corporate Bank and Investment Bank client coverage, alongside private banking and wealth management services for Dutch clients. Finance graduates typically enter through coverage teams, markets-related roles, or risk and finance functions supporting the Dutch business.",
     struct_nl="In Nederland is Deutsche Bank georganiseerd rond klantcoverage vanuit Corporate Bank en Investment Bank, naast private banking en wealth management voor Nederlandse klanten. Finance-afgestudeerden komen doorgaans binnen via coverageteams, markets-gerelateerde rollen, of risk- en financefuncties die de Nederlandse activiteiten ondersteunen.",
     paths=[("corporate-finance","Corporate Finance"),("investment-banking","Investment Banking"),("transaction-services","Transaction Services")],
     join_en="Deutsche Bank recruits students through internships and graduate programmes across its corporate and investment bank, with roles in Amsterdam typically tied to Dutch corporate coverage, markets and support functions.",
     join_nl="Deutsche Bank werft studenten via stages en graduate-programma's binnen de corporate en investment bank, waarbij functies in Amsterdam doorgaans gekoppeld zijn aan Nederlandse zakelijke coverage, markets en ondersteunende functies.",
     facts=[("Type","Type","Bank","Bank"),
       ("Head office","Hoofdkantoor","Global: Frankfurt / NL office: Amsterdam","Wereldwijd: Frankfurt / NL-kantoor: Amsterdam"),
       ("Founded","Opgericht","1870; active in the Netherlands for over a century","1870; al meer dan een eeuw actief in Nederland"),
       ("Ownership","Eigendom","Listed (Frankfurt Stock Exchange, NYSE)","Beursgenoteerd (beurs van Frankfurt, NYSE)")]),

  dict(slug="citi", name="Citi", initials="CG", color="#003b70", city="Amsterdam",
     types=["bank"], site="https://www.citigroup.com/citi/about/countries-and-jurisdictions/netherlands.html",
     tagline_en="A global US bank with one of the longest continuous foreign bank presences in the Netherlands.",
     tagline_nl="Een wereldwijde Amerikaanse bank met een van de langst ononderbroken aanwezigheden van een buitenlandse bank in Nederland.",
     intro_en="Citi is the institutional and consumer banking arm of Citigroup, a global financial services company headquartered in New York. Citigroup traces its roots to the City Bank of New York, founded in 1812, and grew through decades of mergers into one of the largest banks in the world, with a presence in dozens of countries. Its institutional business spans corporate and investment banking, markets, treasury and trade solutions, and securities services for multinational clients, governments and institutions. Citigroup is listed on the New York Stock Exchange.",
     intro_nl="Citi is de institutionele en consumentenbankentak van Citigroup, een wereldwijde financiële dienstverlener met hoofdkantoor in New York. Citigroup gaat terug tot de City Bank of New York, opgericht in 1812, en groeide via tientallen jaren van fusies uit tot een van de grootste banken ter wereld, actief in tientallen landen. De institutionele tak omvat corporate en investment banking, markets, treasury and trade solutions, en effectendiensten voor multinationale klanten, overheden en instellingen. Citigroup staat genoteerd aan de New York Stock Exchange.",
     nl_en="Citi has operated in the Netherlands since 1964, making it one of the longest-established foreign banks in the country, well before Brexit prompted other banks to open Amsterdam offices. Its office is located near Schiphol Airport, reflecting its focus on serving large multinational corporations, financial institutions and public sector organisations rather than Dutch retail customers. For finance students, Citi Netherlands offers roles connected to global banking, global markets and transaction services for international clients.",
     nl_nl="Citi is al sinds 1964 actief in Nederland, wat de bank een van de langst gevestigde buitenlandse banken in het land maakt, ruim voordat de brexit andere banken ertoe aanzette een kantoor in Amsterdam te openen. Het kantoor bevindt zich bij Schiphol, wat aansluit bij de focus op grote multinationale ondernemingen, financiële instellingen en publieke organisaties, in plaats van Nederlandse particuliere klanten. Voor finance-studenten biedt Citi Nederland functies binnen global banking, global markets en transaction services voor internationale klanten.",
     struct_en="Citi Netherlands operates as part of Citi's Institutional Clients Group, organised around Global Banking (corporate and investment banking coverage), Global Markets (sales and trading) and Global Transaction Services (cash management and trade finance). Finance graduates typically join through coverage, markets or transaction services teams.",
     struct_nl="Citi Nederland maakt deel uit van de Institutional Clients Group van Citi, georganiseerd rond Global Banking (corporate en investment banking coverage), Global Markets (sales en trading) en Global Transaction Services (cash management en trade finance). Finance-afgestudeerden komen doorgaans binnen via coverage-, markets- of transaction servicesteams.",
     paths=[("investment-banking","Investment Banking"),("corporate-finance","Corporate Finance"),("transaction-services","Transaction Services")],
     join_en="Citi runs internship and graduate analyst programmes across its institutional businesses, with the Amsterdam office recruiting for local roles in coverage, markets and transaction services aimed at Dutch and international clients.",
     join_nl="Citi biedt stage- en graduate analyst-programma's aan binnen de institutionele activiteiten, waarbij het kantoor in Amsterdam werft voor lokale functies in coverage, markets en transaction services gericht op Nederlandse en internationale klanten.",
     facts=[("Type","Type","Bank","Bank"),
       ("Head office","Hoofdkantoor","Global: New York / NL office: Amsterdam (Schiphol)","Wereldwijd: New York / NL-kantoor: Amsterdam (Schiphol)"),
       ("Founded","Opgericht","1812; active in the Netherlands since 1964","1812; actief in Nederland sinds 1964"),
       ("Ownership","Eigendom","Listed (NYSE: C)","Beursgenoteerd (NYSE: C)")]),

  dict(slug="bank-of-america", name="Bank of America", initials="BA", color="#e11f26", city="Amsterdam",
     types=["bank"], site="https://www.bankofamerica.com",
     tagline_en="One of the largest US banks, with an Amsterdam branch of its Dublin-based EU entity.",
     tagline_nl="Een van de grootste Amerikaanse banken, met een Amsterdams bijkantoor van haar in Dublin gevestigde EU-entiteit.",
     intro_en="Bank of America is one of the largest banks in the United States, headquartered in Charlotte, North Carolina. Its roots go back to the Bank of Italy, founded in San Francisco in 1904, and the modern group took shape through major mergers, including the 1998 combination with NationsBank and the 2008 acquisition of Merrill Lynch, which brought its investment banking and wealth management franchise. The bank serves individuals, businesses and institutions across consumer banking, wealth management, and global banking and markets. Bank of America is listed on the New York Stock Exchange.",
     intro_nl="Bank of America is een van de grootste banken van de Verenigde Staten, met hoofdkantoor in Charlotte, North Carolina. De wortels liggen bij de Bank of Italy, opgericht in San Francisco in 1904, en de huidige groep ontstond via grote fusies, waaronder de samenvoeging met NationsBank in 1998 en de overname van Merrill Lynch in 2008, waarmee de investment banking- en wealth managementtak werd toegevoegd. De bank bedient particulieren, bedrijven en instellingen binnen consumer banking, wealth management, en global banking en markets. Bank of America staat genoteerd aan de New York Stock Exchange.",
     nl_en="After the Brexit referendum, Bank of America restructured its European operations by merging its main EU banking business into its Irish subsidiary, making Dublin its EU hub, with Amsterdam operating as one of several branches of that Dublin-based entity across Europe. The Amsterdam branch serves Dutch and regional clients with banking and markets services as part of this wider European network. It is a modest office focused on client coverage rather than a large employment centre.",
     nl_nl="Na het brexit-referendum herstructureerde Bank of America de Europese activiteiten door de belangrijkste EU-bankactiviteiten onder te brengen bij de Ierse dochteronderneming, waarmee Dublin de EU-hub werd en Amsterdam een van de meerdere bijkantoren van deze in Dublin gevestigde entiteit binnen Europa. Het Amsterdamse bijkantoor bedient Nederlandse en regionale klanten met bankieren en markets als onderdeel van dit bredere Europese netwerk. Het is een bescheiden kantoor, gericht op klantcontact, geen groot werkgelegenheidscentrum.",
     struct_en="The Amsterdam branch covers corporate and institutional client coverage and markets-related activity for the Dutch market, operating within Bank of America's Global Banking and Global Markets structure. Finance graduates who join in Amsterdam typically work in coverage or markets support roles.",
     struct_nl="Het Amsterdamse bijkantoor richt zich op corporate en institutionele klantcoverage en markets-gerelateerde activiteiten voor de Nederlandse markt, binnen de structuur van Global Banking en Global Markets van Bank of America. Finance-afgestudeerden die in Amsterdam beginnen, werken doorgaans in coverage- of ondersteunende marketsrollen.",
     paths=[("investment-banking","Investment Banking"),("corporate-finance","Corporate Finance")],
     join_en="Bank of America runs global internship and graduate analyst programmes in global banking and markets, mainly recruited through its larger European hubs such as London and Dublin; opportunities in the Amsterdam branch are limited given its smaller size.",
     join_nl="Bank of America biedt wereldwijd stage- en graduate analyst-programma's aan in global banking en markets, vooral geworven via de grotere Europese hubs zoals Londen en Dublin; de mogelijkheden bij het Amsterdamse bijkantoor zijn beperkt gezien de kleinere omvang.",
     facts=[("Type","Type","Bank","Bank"),
       ("Head office","Hoofdkantoor","Global: Charlotte, US / EU hub: Dublin / NL branch: Amsterdam","Wereldwijd: Charlotte, VS / EU-hub: Dublin / NL-bijkantoor: Amsterdam"),
       ("Founded","Opgericht","1904 (Bank of Italy); modern group formed 1998","1904 (Bank of Italy); huidige groep gevormd in 1998"),
       ("Ownership","Eigendom","Listed (NYSE: BAC)","Beursgenoteerd (NYSE: BAC)")]),

  dict(slug="hsbc", name="HSBC", initials="HS", color="#db0011", city="Amsterdam",
     types=["bank"], site="https://www.about.hsbc.nl",
     tagline_en="A major London-headquartered global bank with an Amsterdam office serving corporate clients.",
     tagline_nl="Een grote Londense wereldbank met een Amsterdams kantoor voor zakelijke klanten.",
     intro_en="HSBC is one of the world's largest banking and financial services organisations, headquartered in London. It traces its origins to the Hongkong and Shanghai Banking Corporation, founded in Hong Kong in 1865 to finance trade between Europe and Asia. Today HSBC serves individuals, businesses and institutions across dozens of countries, with a particular strength in trade and cross-border banking. HSBC Holdings is listed on the London Stock Exchange and the Hong Kong Stock Exchange.",
     intro_nl="HSBC is een van de grootste bank- en financiëledienstverleners ter wereld, met hoofdkantoor in Londen. De oorsprong ligt bij de Hongkong and Shanghai Banking Corporation, opgericht in Hongkong in 1865 om handel tussen Europa en Azië te financieren. Tegenwoordig bedient HSBC particulieren, bedrijven en instellingen in tientallen landen, met een bijzondere sterkte in handelsfinanciering en grensoverschrijdend bankieren. HSBC Holdings staat genoteerd aan de beurs van Londen en aan de beurs van Hongkong.",
     nl_en="HSBC opened a branch in Amsterdam in 1999, and later, as part of its post-Brexit European restructuring, incorporated HSBC Continental Europe, with the Amsterdam office continuing to serve as a Dutch base for corporate and institutional clients. From Amsterdam, HSBC offers global payments, trade finance, hedging and financing services to Dutch and internationally active companies. For finance students, this is a relatively compact office focused on corporate banking relationships rather than large-scale trading operations.",
     nl_nl="HSBC opende in 1999 een kantoor in Amsterdam, en bracht later, als onderdeel van de Europese herstructurering na de brexit, activiteiten onder bij HSBC Continental Europe, waarbij het kantoor in Amsterdam een Nederlandse uitvalsbasis bleef voor zakelijke en institutionele klanten. Vanuit Amsterdam biedt HSBC wereldwijde betalingsoplossingen, handelsfinanciering, hedging en financiering aan Nederlandse en internationaal actieve bedrijven. Voor finance-studenten is dit een relatief compact kantoor, gericht op zakelijke bankrelaties in plaats van grootschalige handelsactiviteiten.",
     struct_en="HSBC's Amsterdam office is organised around Commercial Banking and Global Banking and Markets client relationships, covering trade finance, payments, financing and hedging solutions for Dutch corporates. Finance graduates typically start in relationship management, product or markets-support roles.",
     struct_nl="Het Amsterdamse kantoor van HSBC is georganiseerd rond klantrelaties binnen Commercial Banking en Global Banking and Markets, met handelsfinanciering, betalingen, financiering en hedgingoplossingen voor Nederlandse bedrijven. Finance-afgestudeerden starten doorgaans in relatiebeheer, product- of ondersteunende marketsrollen.",
     paths=[("corporate-finance","Corporate Finance"),("transaction-services","Transaction Services")],
     join_en="HSBC offers internships and graduate programmes across its commercial and global banking businesses in Europe; the Amsterdam office recruits on a smaller scale for roles tied to Dutch corporate relationships.",
     join_nl="HSBC biedt stages en graduate-programma's aan binnen de commercial en global banking-activiteiten in Europa; het kantoor in Amsterdam werft op kleinere schaal voor functies gekoppeld aan Nederlandse zakelijke relaties.",
     facts=[("Type","Type","Bank","Bank"),
       ("Head office","Hoofdkantoor","Global: London / NL office: Amsterdam","Wereldwijd: Londen / NL-kantoor: Amsterdam"),
       ("Founded","Opgericht","1865; Amsterdam branch opened 1999","1865; kantoor Amsterdam geopend in 1999"),
       ("Ownership","Eigendom","Listed (London Stock Exchange, Hong Kong Stock Exchange)","Beursgenoteerd (beurs van Londen, beurs van Hongkong)")]),

  dict(slug="societe-generale", name="Société Générale", initials="SG", color="#e60000", city="Amsterdam",
     types=["bank"], site="https://www.societegenerale.nl",
     tagline_en="A major French bank present in the Netherlands since the late 1970s.",
     tagline_nl="Een grote Franse bank die sinds de late jaren zeventig aanwezig is in Nederland.",
     intro_en="Société Générale is one of France's largest banks, headquartered in Paris and founded in 1864 by imperial decree to support the development of trade and industry in France. It has grown into a diversified banking group active in retail banking, corporate and investment banking, and asset management across dozens of countries. Its corporate and investment banking arm serves large companies, financial institutions and investors globally. Société Générale is listed on Euronext Paris.",
     intro_nl="Société Générale is een van de grootste banken van Frankrijk, met hoofdkantoor in Parijs, opgericht in 1864 bij keizerlijk decreet om de ontwikkeling van handel en industrie in Frankrijk te ondersteunen. De bank groeide uit tot een gediversifieerde bankgroep, actief in retailbankieren, corporate en investment banking, en vermogensbeheer in tientallen landen. De corporate en investment bankingtak bedient grote bedrijven, financiële instellingen en beleggers wereldwijd. Société Générale staat genoteerd aan Euronext Parijs.",
     nl_en="Société Générale has operated in the Netherlands since 1977 through its Amsterdam branch, well before Brexit, alongside smaller specialist units such as an equipment finance arm and a car fleet management subsidiary elsewhere in the country. The Amsterdam team, based in the Rembrandt Tower, focuses on corporate and investment banking and global transaction banking, including cash management and trade finance for Dutch clients. It is a modest but long-standing presence rather than a large-scale operation.",
     nl_nl="Société Générale is sinds 1977 actief in Nederland via het kantoor in Amsterdam, ruim voor de brexit, naast kleinere gespecialiseerde onderdelen zoals een financieringstak voor bedrijfsmiddelen en een dochter voor wagenparkbeheer elders in het land. Het Amsterdamse team, gevestigd in de Rembrandt Tower, richt zich op corporate en investment banking en global transaction banking, waaronder cash management en handelsfinanciering voor Nederlandse klanten. Het is een bescheiden maar langdurige aanwezigheid, geen grootschalige operatie.",
     struct_en="In Amsterdam, Société Générale is organised around Corporate and Investment Banking client coverage and Global Transaction Banking, alongside separate specialist financing subsidiaries elsewhere in the Netherlands. Finance graduates typically join through coverage, markets-support, or transaction banking roles.",
     struct_nl="In Amsterdam is Société Générale georganiseerd rond klantcoverage binnen Corporate and Investment Banking en Global Transaction Banking, naast aparte gespecialiseerde financieringsdochters elders in Nederland. Finance-afgestudeerden komen doorgaans binnen via coverage-, marketsondersteunende, of transaction bankingrollen.",
     paths=[("corporate-finance","Corporate Finance"),("transaction-services","Transaction Services")],
     join_en="Société Générale recruits students through internships and graduate programmes across its corporate and investment banking division in Europe, with the Amsterdam office offering a smaller number of local roles tied to Dutch client coverage.",
     join_nl="Société Générale werft studenten via stages en graduate-programma's binnen de corporate en investment bankingdivisie in Europa, waarbij het kantoor in Amsterdam een kleiner aantal lokale functies biedt gekoppeld aan Nederlandse klantcoverage.",
     facts=[("Type","Type","Bank","Bank"),
       ("Head office","Hoofdkantoor","Global: Paris / NL office: Amsterdam","Wereldwijd: Parijs / NL-kantoor: Amsterdam"),
       ("Founded","Opgericht","1864; active in the Netherlands since 1977","1864; actief in Nederland sinds 1977"),
       ("Ownership","Eigendom","Listed (Euronext Paris)","Beursgenoteerd (Euronext Parijs)")]),

  dict(slug="barclays", name="Barclays", initials="BC", color="#00aeef", city="Amsterdam",
     types=["bank"], site="https://www.barclays.com",
     tagline_en="A major British bank with an Amsterdam branch of its EU banking entity.",
     tagline_nl="Een grote Britse bank met een Amsterdams bijkantoor van haar EU-bankentiteit.",
     intro_en="Barclays is one of the United Kingdom's largest banks, headquartered in London, with a history dating back to 1690, making it one of the oldest banks in the world. It operates across consumer banking, corporate banking, and investment banking and markets, serving clients globally. Its investment bank advises on mergers and acquisitions, capital raising, and provides trading and markets services to corporations, governments and institutions. Barclays is listed on the London Stock Exchange.",
     intro_nl="Barclays is een van de grootste banken van het Verenigd Koninkrijk, met hoofdkantoor in Londen en een geschiedenis die teruggaat tot 1690, waarmee het een van de oudste banken ter wereld is. De bank is actief in consumentenbankieren, zakelijk bankieren, en investment banking en markets, met klanten wereldwijd. De investment bank adviseert bij fusies en overnames en kapitaalophaling, en biedt trading- en marketsdiensten aan bedrijven, overheden en instellingen. Barclays staat genoteerd aan de beurs van Londen.",
     nl_en="After Brexit, Barclays restructured its EU business through Barclays Bank Ireland, based in Dublin, which became the group's EU banking hub. Barclays operates an Amsterdam branch of that Irish entity to serve Dutch clients, part of a wider European branch network that also includes Belgium, France, Germany and other countries. The Amsterdam presence is a client-facing branch rather than a large standalone operation, focused on corporate and investment banking coverage.",
     nl_nl="Na de brexit herstructureerde Barclays de EU-activiteiten via Barclays Bank Ireland, gevestigd in Dublin, dat de EU-bankhub van de groep werd. Barclays heeft een Amsterdams bijkantoor van deze Ierse entiteit om Nederlandse klanten te bedienen, onderdeel van een breder Europees netwerk van bijkantoren, waaronder ook België, Frankrijk, Duitsland en andere landen. De aanwezigheid in Amsterdam is een klantgericht bijkantoor, geen grote zelfstandige operatie, gericht op corporate en investment banking coverage.",
     struct_en="The Amsterdam branch covers corporate and investment banking relationships with Dutch clients, operating within Barclays' Corporate and Investment Bank division and reporting into the Dublin-based EU entity. Finance graduates who join in Amsterdam typically work in coverage or markets-support roles.",
     struct_nl="Het Amsterdamse bijkantoor onderhoudt corporate en investment banking-relaties met Nederlandse klanten, binnen de Corporate and Investment Bank-divisie van Barclays en vallend onder de in Dublin gevestigde EU-entiteit. Finance-afgestudeerden die in Amsterdam beginnen, werken doorgaans in coverage- of ondersteunende marketsrollen.",
     paths=[("investment-banking","Investment Banking"),("corporate-finance","Corporate Finance")],
     join_en="Barclays runs global internship and graduate analyst programmes within its investment bank, mainly recruited through London and other larger European hubs; the Amsterdam branch offers a limited number of local roles tied to Dutch client coverage.",
     join_nl="Barclays biedt wereldwijd stage- en graduate analyst-programma's aan binnen de investment bank, vooral geworven via Londen en andere grotere Europese hubs; het Amsterdamse bijkantoor biedt een beperkt aantal lokale functies gekoppeld aan Nederlandse klantcoverage.",
     facts=[("Type","Type","Bank","Bank"),
       ("Head office","Hoofdkantoor","Global: London / EU hub: Dublin / NL branch: Amsterdam","Wereldwijd: Londen / EU-hub: Dublin / NL-bijkantoor: Amsterdam"),
       ("Founded","Opgericht","1690","1690"),
       ("Ownership","Eigendom","Listed (London Stock Exchange)","Beursgenoteerd (beurs van Londen)")]),

  dict(slug="natwest-markets", name="NatWest Markets", initials="NM", color="#5a287d", city="Amsterdam",
     types=["bank","trading"], site="https://www.natwestmarkets.com",
     tagline_en="The markets arm of NatWest Group, whose EU trading entity is based in Amsterdam.",
     tagline_nl="De marketstak van NatWest Group, waarvan de EU-handelsentiteit gevestigd is in Amsterdam.",
     intro_en="NatWest Markets is the markets and international banking arm of NatWest Group, the UK banking group formerly known as Royal Bank of Scotland Group, headquartered in Edinburgh. NatWest Group's roots go back to National Westminster Bank, formed in 1968, and the Royal Bank of Scotland, founded in 1727. NatWest Markets provides financing, risk management and trading services in rates, currencies and financing markets to corporate and institutional clients. NatWest Group is listed on the London Stock Exchange, with the UK government historically holding a stake built up after the 2008 financial crisis.",
     intro_nl="NatWest Markets is de markets- en internationale bankentak van NatWest Group, de Britse bankgroep die vroeger bekendstond als Royal Bank of Scotland Group, met hoofdkantoor in Edinburgh. De wortels van NatWest Group liggen bij National Westminster Bank, gevormd in 1968, en de Royal Bank of Scotland, opgericht in 1727. NatWest Markets biedt financiering, risicomanagement en handelsdiensten in rente-, valuta- en financieringsmarkten aan zakelijke en institutionele klanten. NatWest Group staat genoteerd aan de beurs van Londen, waarbij de Britse overheid historisch een belang aanhield dat werd opgebouwd na de kredietcrisis van 2008.",
     nl_en="NatWest established NatWest Markets N.V. in Amsterdam in 2019 specifically to continue serving EU-based clients after the UK left the European Union and lost its passporting rights to the bloc. Amsterdam functions as the group's dedicated EU trading and banking entity, authorised and supervised by De Nederlandsche Bank, the European Central Bank and the Dutch markets regulator AFM, with branches of its own in cities including Frankfurt, Paris, Stockholm and Milan. It is a specialised markets office rather than a large full-service bank presence.",
     nl_nl="NatWest richtte NatWest Markets N.V. in 2019 op in Amsterdam, specifiek om EU-klanten te kunnen blijven bedienen nadat het VK de Europese Unie verliet en de passporting-rechten voor de EU verloor. Amsterdam functioneert als de speciale EU-handels- en bankentiteit van de groep, onder toezicht van De Nederlandsche Bank, de Europese Centrale Bank en de AFM, met eigen bijkantoren in onder meer Frankfurt, Parijs, Stockholm en Milaan. Het is een gespecialiseerd marketskantoor, geen grote full-service bankvestiging.",
     struct_en="NatWest Markets N.V. in Amsterdam is organised around trading, risk management and financing services in rates, currencies and debt markets for corporate and institutional clients across Western Europe, with the entity itself serving as the legal and regulatory hub for several branch offices. Finance graduates who join here typically work in markets, structuring, or risk-related roles.",
     struct_nl="NatWest Markets N.V. in Amsterdam is georganiseerd rond trading, risicomanagement en financieringsdiensten in rente-, valuta- en obligatiemarkten voor zakelijke en institutionele klanten in West-Europa, waarbij de entiteit zelf dient als juridische en regelgevende hub voor meerdere bijkantoren. Finance-afgestudeerden die hier beginnen, werken doorgaans in markets-, structurerings- of risicogerelateerde rollen.",
     paths=[("investment-banking","Investment Banking"),("corporate-finance","Corporate Finance")],
     join_en="NatWest Markets recruits for markets and risk-related roles in Amsterdam mainly through internships and graduate or analyst positions tied to its trading and financing businesses, on a scale reflecting its role as a specialised EU booking entity rather than a full universal bank.",
     join_nl="NatWest Markets werft voor markets- en risicogerelateerde functies in Amsterdam vooral via stages en graduate- of analistenposities gekoppeld aan de trading- en financieringsactiviteiten, op een schaal die past bij de rol als gespecialiseerde EU-vestigingsentiteit in plaats van een volwaardige universele bank.",
     facts=[("Type","Type","Bank and trading entity","Bank en handelsentiteit"),
       ("Head office","Hoofdkantoor","Global: Edinburgh / NL office: Amsterdam (EU trading entity)","Wereldwijd: Edinburgh / NL-kantoor: Amsterdam (EU-handelsentiteit)"),
       ("Founded","Opgericht","NatWest traces to 1968 and 1727; Amsterdam EU entity established 2019","NatWest gaat terug tot 1968 en 1727; EU-entiteit Amsterdam opgericht in 2019"),
       ("Ownership","Eigendom","Listed (London Stock Exchange)","Beursgenoteerd (beurs van Londen)")]),

dict(slug="imc-trading", name="IMC Trading", initials="IM", color="#0b3d2e", city="Amsterdam",
   types=["trading"],
   site="https://www.imc.com",
   tagline_en="A Dutch-founded proprietary trading firm and market maker active on exchanges worldwide.",
   tagline_nl="Een Nederlandse proprietary trading-firma en market maker, actief op beurzen wereldwijd.",
   intro_en="IMC (originally International Marketmaker's Combination) is a proprietary trading firm and market maker that quotes prices in options, equities, ETFs, futures and other instruments on exchanges around the world. It was founded in 1989 by two floor traders on the Amsterdam European Options Exchange, at a time when trading was still done by open outcry, and grew alongside the shift toward electronic and computer-assisted trading. IMC makes money from the bid-ask spread and from managing the risk that comes with continuously providing liquidity, rather than from taking large directional market bets. Over the decades it expanded beyond options into equities, ETFs, fixed income and other asset classes, and beyond Europe into the United States and Asia. The firm remains privately held and is not listed on a stock exchange.",
   intro_nl="IMC (oorspronkelijk International Marketmaker's Combination) is een proprietary trading-firma en market maker die doorlopend prijzen afgeeft in opties, aandelen, ETF's, futures en andere instrumenten op beurzen over de hele wereld. Het bedrijf werd in 1989 opgericht door twee vloerhandelaren op de Amsterdamse Europese Optiebeurs, in een tijd waarin nog via open outcry werd gehandeld, en groeide mee met de overgang naar elektronische en computerondersteunde handel. IMC verdient aan het verschil tussen bied- en laatprijzen en aan het beheersen van het risico dat komt kijken bij het doorlopend leveren van liquiditeit, niet aan het innemen van grote directionele posities. In de loop der decennia breidde het bedrijf uit van opties naar aandelen, ETF's, vastrentende waarden en andere activaklassen, en van Europa naar de Verenigde Staten en Azie. Het bedrijf is nog altijd privaat en staat niet genoteerd aan een beurs.",
   nl_en="IMC is a Dutch firm through and through: it was born on the floor of the Amsterdam options exchange, and Amsterdam remains one of its main hubs alongside Chicago. That floor-trading culture, where traders learned to price risk quickly and competitively face to face, is part of the reason Amsterdam became a breeding ground for the proprietary trading industry, with IMC, Optiver and Flow Traders all tracing their roots to the same exchange. For finance and quant students, IMC's Amsterdam office offers a route into trading, quantitative research and trading technology at a firm with a genuinely Dutch heritage.",
   nl_nl="IMC is door en door een Nederlands bedrijf: het is ontstaan op de vloer van de Amsterdamse optiebeurs, en Amsterdam blijft een van de belangrijkste vestigingen naast Chicago. Die vloerhandelcultuur, waarin handelaren leerden om risico snel en competitief in te prijzen, oog in oog met elkaar, is een van de redenen dat Amsterdam is uitgegroeid tot een kweekvijver voor de proprietary trading-sector, met IMC, Optiver en Flow Traders die allemaal terug te voeren zijn op dezelfde beurs. Voor finance- en quantstudenten biedt het Amsterdamse kantoor van IMC een ingang tot trading, kwantitatief onderzoek en handelstechnologie bij een bedrijf met een echt Nederlandse achtergrond.",
   struct_en="IMC organises its work broadly around trading (managing risk and quoting prices in the market), quantitative research (building and refining pricing models and strategies) and technology (building the systems that execute trades at speed and scale). Graduates typically join as traders, quantitative researchers or software engineers, with close day-to-day collaboration between the three groups.",
   struct_nl="IMC organiseert het werk grofweg rond trading (risico beheren en prijzen afgeven in de markt), quantitative research (het bouwen en verfijnen van prijsmodellen en strategieen) en technology (het bouwen van de systemen die trades snel en op schaal uitvoeren). Afgestudeerden komen doorgaans binnen als trader, quantitative researcher of software engineer, met nauwe dagelijkse samenwerking tussen de drie groepen.",
   paths=[("trading","Trading")],
   join_en="IMC recruits through internships and graduate programmes for trading, research and technology roles. Selection is intensive and typically includes numerical and logical reasoning tests, so strong quantitative ability tends to matter more than a specific degree, though many hires come from mathematics, physics, engineering or econometrics backgrounds.",
   join_nl="IMC werft via stages en graduate-programma's voor trading-, research- en technologiefuncties. De selectie is intensief en bevat doorgaans numerieke en logisch-redeneertests, waardoor sterke kwantitatieve vaardigheden vaak zwaarder tellen dan een specifieke studie, al komen veel nieuwe medewerkers uit de wiskunde, natuurkunde, techniek of econometrie.",
   facts=[("Type","Type","Proprietary trading / market maker","Proprietary trading / market maker"),
     ("Head office","Hoofdkantoor","Amsterdam / Chicago","Amsterdam / Chicago"),
     ("Founded","Opgericht","1989","1989"),
     ("Ownership","Eigendom","Private","Privaat")]),

dict(slug="flow-traders", name="Flow Traders", initials="FT", color="#f7931e", city="Amsterdam",
   types=["trading"],
   site="https://www.flowtraders.com",
   tagline_en="An Amsterdam-founded market maker specialised in exchange-traded products such as ETFs.",
   tagline_nl="Een in Amsterdam opgerichte market maker gespecialiseerd in beursverhandelde producten zoals ETF's.",
   intro_en="Flow Traders is a proprietary trading firm that focuses on making markets in exchange-traded products, mainly ETFs, but also other exchange-traded notes and commodities. It was founded in Amsterdam in 2004 by two former Optiver traders, at a time when European ETF markets were still young and often had wide, inefficient spreads. Flow Traders built its business on technology that lets it continuously quote buy and sell prices for thousands of listings across exchanges in Europe, the Americas and Asia Pacific, earning income from the spread and from managing the associated risk. Unlike the other Dutch prop trading firms, Flow Traders went public: it listed on Euronext Amsterdam in 2015, which means its shares are traded but the underlying trading business still operates as a proprietary market maker.",
   intro_nl="Flow Traders is een proprietary trading-firma die zich richt op het maken van markten in beursverhandelde producten, voornamelijk ETF's, maar ook andere exchange-traded notes en grondstoffen. Het bedrijf werd in 2004 in Amsterdam opgericht door twee voormalige Optiver-handelaren, in een tijd waarin de Europese ETF-markten nog jong waren en vaak brede, inefficiente spreads kenden. Flow Traders bouwde zijn bedrijf op technologie waarmee het doorlopend bied- en laatprijzen kan afgeven voor duizenden noteringen op beurzen in Europa, Amerika en Azie-Pacific, en verdient aan de spread en aan het beheersen van het bijbehorende risico. In tegenstelling tot de andere Nederlandse proprietary trading-firma's ging Flow Traders naar de beurs: het noteerde in 2015 op Euronext Amsterdam, wat betekent dat de aandelen verhandelbaar zijn terwijl de onderliggende handelsactiviteit nog steeds als proprietary market maker opereert.",
   nl_en="Flow Traders was founded in Amsterdam and keeps its head office there, with its founders having learned the trade at Optiver on the Amsterdam options exchange floor before starting their own firm. This lineage is typical of the city's proprietary trading scene, which grew out of that exchange floor culture into a cluster of technology-driven trading houses. For students, the Amsterdam office is where most trading, research and technology roles for Europe are based.",
   nl_nl="Flow Traders is opgericht in Amsterdam en houdt daar ook zijn hoofdkantoor, waarbij de oprichters het vak leerden bij Optiver op de vloer van de Amsterdamse optiebeurs voordat ze hun eigen bedrijf begonnen. Deze afkomst is kenmerkend voor de Amsterdamse proprietary trading-scene, die vanuit die beursvloercultuur is uitgegroeid tot een cluster van technologiegedreven handelshuizen. Voor studenten is het Amsterdamse kantoor de plek waar de meeste trading-, research- en technologiefuncties voor Europa zijn gevestigd.",
   struct_en="The firm is organised around trading desks for different product categories, a technology organisation that builds and maintains its trading systems, and quantitative research that develops pricing and risk models. Graduates typically start as traders or in technology and research roles, working closely with experienced traders on live risk.",
   struct_nl="Het bedrijf is georganiseerd rond tradingdesks voor verschillende productcategorieen, een technologieorganisatie die de handelssystemen bouwt en onderhoudt, en quantitative research dat prijs- en risicomodellen ontwikkelt. Afgestudeerden beginnen doorgaans als trader of in technologie- en researchfuncties, en werken nauw samen met ervaren traders op live risico.",
   paths=[("trading","Trading")],
   join_en="Flow Traders hires through internships and graduate programmes for trading, technology and quantitative research. As with most prop trading firms, selection involves rigorous numerical and analytical testing, so quantitative aptitude generally weighs more heavily than a specific degree.",
   join_nl="Flow Traders werft via stages en graduate-programma's voor trading, technology en quantitative research. Zoals bij de meeste proprietary trading-firma's bestaat de selectie uit stevige numerieke en analytische tests, waardoor kwantitatieve aanleg doorgaans zwaarder weegt dan een specifieke studie.",
   facts=[("Type","Type","Proprietary trading / market maker","Proprietary trading / market maker"),
     ("Head office","Hoofdkantoor","Amsterdam","Amsterdam"),
     ("Founded","Opgericht","2004","2004"),
     ("Ownership","Eigendom","Listed (Euronext Amsterdam)","Beursgenoteerd (Euronext Amsterdam)")]),

dict(slug="da-vinci-trading", name="Da Vinci Trading", initials="DV", color="#7c3aed", city="Amsterdam",
   types=["trading"],
   site="https://davincitrading.com",
   tagline_en="An Amsterdam proprietary trading firm known for options and futures market making.",
   tagline_nl="Een Amsterdamse proprietary trading-firma bekend van market making in opties en futures.",
   intro_en="Da Vinci Trading, formerly known as Da Vinci Derivatives, is a proprietary trading firm founded in Amsterdam in 2015. It combines market making, continuously quoting buy and sell prices in options and futures on European and US exchanges, with position taking, where the firm takes calculated directional views based on its own research. Compared with older Amsterdam trading houses, Da Vinci is a relatively young firm, and it has expanded beyond traditional listed derivatives into digital assets, including acting as a designated market maker on crypto exchanges. It remains privately owned and has grown from its Amsterdam base into additional offices abroad.",
   intro_nl="Da Vinci Trading, voorheen bekend als Da Vinci Derivatives, is een proprietary trading-firma die in 2015 in Amsterdam is opgericht. Het bedrijf combineert market making, het doorlopend afgeven van bied- en laatprijzen in opties en futures op Europese en Amerikaanse beurzen, met position taking, waarbij het bedrijf op basis van eigen onderzoek weloverwogen directionele posities inneemt. Vergeleken met de oudere Amsterdamse handelshuizen is Da Vinci een relatief jonge firma, en het heeft zich vanuit traditionele beursgenoteerde derivaten uitgebreid naar digitale activa, onder meer als aangewezen market maker op cryptobeurzen. Het bedrijf is nog altijd privaat en is vanuit Amsterdam uitgegroeid naar extra kantoren in het buitenland.",
   nl_en="Da Vinci was founded in Amsterdam and is still headquartered there, making it one of several Amsterdam-born prop trading firms alongside IMC, Optiver and Flow Traders, all part of a trading culture that traces back to the city's historic options exchange floor. Although younger than those firms, Da Vinci fits the same mould: technology-driven market making built by traders with floor and exchange experience. For students, its Amsterdam office is the centre of its trading and research activity.",
   nl_nl="Da Vinci is opgericht in Amsterdam en heeft daar nog altijd zijn hoofdkantoor, wat het bedrijf tot een van de meerdere in Amsterdam geboren proprietary trading-firma's maakt, naast IMC, Optiver en Flow Traders, die allemaal onderdeel zijn van een handelscultuur die teruggaat op de historische Amsterdamse optiebeursvloer. Hoewel jonger dan die bedrijven, past Da Vinci in hetzelfde patroon: technologiegedreven market making, opgebouwd door handelaren met vloer- en beurservaring. Voor studenten is het Amsterdamse kantoor het centrum van de trading- en researchactiviteiten.",
   struct_en="The firm is built around trading teams that manage market making and position taking, supported by quantitative research and a technology function that develops the trading infrastructure. Graduates typically join as traders or in quant/technology roles, working alongside experienced traders early on.",
   struct_nl="Het bedrijf is opgebouwd rond tradingteams die market making en position taking beheren, ondersteund door quantitative research en een technologiefunctie die de handelsinfrastructuur ontwikkelt. Afgestudeerden komen doorgaans binnen als trader of in quant-/technologiefuncties, en werken al vroeg samen met ervaren traders.",
   paths=[("trading","Trading")],
   join_en="Da Vinci recruits through internships and graduate programmes for trading and quantitative/technology roles. As with peer firms, the process is selective and leans heavily on numerical and analytical tests, so quantitative skill generally counts for more than a specific field of study.",
   join_nl="Da Vinci werft via stages en graduate-programma's voor trading- en quant-/technologiefuncties. Net als bij vergelijkbare firma's is het proces selectief en leunt het zwaar op numerieke en analytische tests, waardoor kwantitatieve vaardigheden doorgaans zwaarder wegen dan een specifieke studierichting.",
   facts=[("Type","Type","Proprietary trading / market maker","Proprietary trading / market maker"),
     ("Head office","Hoofdkantoor","Amsterdam","Amsterdam"),
     ("Founded","Opgericht","2015","2015"),
     ("Ownership","Eigendom","Private","Privaat")]),

dict(slug="jane-street", name="Jane Street", initials="JS", color="#c1272d", city="Amsterdam",
   types=["trading"],
   site="https://www.janestreet.com",
   tagline_en="A US quantitative trading firm with a major European trading office in Amsterdam.",
   tagline_nl="Een Amerikaanse kwantitatieve handelsfirma met een groot Europees handelskantoor in Amsterdam.",
   intro_en="Jane Street is a quantitative trading firm founded in New York in 2000. It trades a broad range of instruments, including ETFs, equities, options and fixed income, acting as a market maker and liquidity provider on exchanges worldwide, and it is also known for its work in the ETF market and for training in functional programming, particularly OCaml. The firm operates as a private partnership and is not listed on a stock exchange. Beyond New York, it has built out international offices in London, Hong Kong, Singapore and Amsterdam to trade during European and Asian hours and to be close to local exchanges and clients.",
   intro_nl="Jane Street is een kwantitatieve handelsfirma die in 2000 in New York werd opgericht. Het bedrijf verhandelt een breed scala aan instrumenten, waaronder ETF's, aandelen, opties en vastrentende waarden, en treedt op als market maker en liquiditeitsverschaffer op beurzen wereldwijd. Jane Street staat ook bekend om zijn rol in de ETF-markt en om het gebruik van functioneel programmeren, met name OCaml. Het bedrijf opereert als een privaat partnerschap en staat niet genoteerd aan een beurs. Naast New York bouwde het internationale kantoren op in Londen, Hongkong, Singapore en Amsterdam, om tijdens de Europese en Aziatische handelsuren actief te zijn en dicht bij lokale beurzen en klanten te zitten.",
   nl_en="Jane Street is a US firm, not a Dutch one: it was founded in New York, and its European operations are formally headquartered in London, with Amsterdam as a substantial trading and technology office. Jane Street chose Amsterdam, as many foreign trading firms have, because the city has a deep pool of traders and engineers shaped by the legacy of its historic options exchange floor and by neighbouring firms like Optiver, IMC and Flow Traders. For finance and quant students in the Netherlands, the Amsterdam office offers access to Jane Street's trading, research and engineering work without needing to relocate abroad.",
   nl_nl="Jane Street is een Amerikaans bedrijf, geen Nederlands: het werd opgericht in New York, en de Europese activiteiten zijn formeel gevestigd in Londen, met Amsterdam als een substantieel handels- en technologiekantoor. Jane Street koos voor Amsterdam, zoals veel buitenlandse handelsfirma's, omdat de stad een diepe vijver aan traders en engineers kent, gevormd door de erfenis van de historische optiebeursvloer en door omliggende bedrijven als Optiver, IMC en Flow Traders. Voor finance- en quantstudenten in Nederland biedt het Amsterdamse kantoor toegang tot het trading-, research- en engineeringwerk van Jane Street, zonder dat ze naar het buitenland hoeven te verhuizen.",
   struct_en="Jane Street's work is organised around trading (managing risk and pricing in live markets), quantitative research (building pricing and risk models) and software engineering (building the systems trading runs on, often in OCaml). Graduates typically join as traders, quantitative researchers or software engineers, and the firm is known for blurring the lines between these roles more than some competitors.",
   struct_nl="Het werk bij Jane Street is georganiseerd rond trading (risico en prijsvorming in de levende markt beheren), quantitative research (het bouwen van prijs- en risicomodellen) en software engineering (het bouwen van de systemen waarop de handel draait, vaak in OCaml). Afgestudeerden komen doorgaans binnen als trader, quantitative researcher of software engineer, en het bedrijf staat erom bekend de grenzen tussen deze rollen sterker te laten vervagen dan sommige concurrenten.",
   paths=[("trading","Trading")],
   join_en="Jane Street recruits in Amsterdam through internships and graduate programmes for trading, research and engineering. The process is known for being highly quantitative, including puzzle-based and probabilistic reasoning interviews, so mathematical and analytical strength generally matters more than a specific degree.",
   join_nl="Jane Street werft in Amsterdam via stages en graduate-programma's voor trading, research en engineering. Het proces staat bekend als sterk kwantitatief, met puzzelgebaseerde en kansrekeninggerichte gesprekken, waardoor wiskundige en analytische sterkte doorgaans zwaarder telt dan een specifieke studie.",
   facts=[("Type","Type","Proprietary trading / market maker","Proprietary trading / market maker"),
     ("Head office","Hoofdkantoor","New York (Europe: Amsterdam / London)","New York (Europa: Amsterdam / Londen)"),
     ("Founded","Opgericht","2000","2000"),
     ("Ownership","Eigendom","Private partnership","Privaat partnerschap")]),

dict(slug="drw", name="DRW", initials="DR", color="#004b87", city="Amsterdam",
   types=["trading"],
   site="https://drw.com",
   tagline_en="A Chicago-founded proprietary trading firm with a European trading hub in Amsterdam.",
   tagline_nl="Een in Chicago opgerichte proprietary trading-firma met een Europees handelsknooppunt in Amsterdam.",
   intro_en="DRW is a diversified proprietary trading firm founded in Chicago in 1992 by Don Wilson, a former options trader at the Chicago Mercantile Exchange. It trades a wide range of asset classes, including futures, fixed income, energy, and equities, and through its Cumberland business, it is also active as a market maker in digital assets. DRW makes markets and manages risk across many exchanges rather than relying on a single product line, and it has grown from a Chicago trading firm into a global organisation with its own trading technology built largely in-house. The firm is privately held and not publicly listed.",
   intro_nl="DRW is een gediversifieerde proprietary trading-firma die in 1992 in Chicago werd opgericht door Don Wilson, een voormalig optiehandelaar op de Chicago Mercantile Exchange. Het bedrijf verhandelt een breed scala aan activaklassen, waaronder futures, vastrentende waarden, energie en aandelen, en is via zijn onderdeel Cumberland ook actief als market maker in digitale activa. DRW maakt markten en beheert risico op veel beurzen in plaats van te leunen op een enkele productlijn, en groeide van een Chicagose handelsfirma uit tot een wereldwijde organisatie met grotendeels zelf ontwikkelde handelstechnologie. Het bedrijf is privaat en staat niet genoteerd aan een beurs.",
   nl_en="DRW is a US firm headquartered in Chicago, with Amsterdam serving as one of its European trading offices alongside London. As with other foreign entrants, DRW's presence in Amsterdam reflects the city's standing as a European centre for proprietary trading, built on decades of talent shaped by the historic options exchange floor and the cluster of Dutch firms that grew out of it, such as Optiver, IMC and Flow Traders. For students, DRW's Amsterdam office is a place to work in trading, quantitative research or technology for a large, diversified US trading firm without leaving the Netherlands.",
   nl_nl="DRW is een Amerikaans bedrijf met hoofdkantoor in Chicago, waarbij Amsterdam een van de Europese handelskantoren is, naast Londen. Net als bij andere buitenlandse toetreders weerspiegelt de aanwezigheid van DRW in Amsterdam de status van de stad als Europees centrum voor proprietary trading, gebouwd op decennia aan talent gevormd door de historische optiebeursvloer en het cluster van Nederlandse firma's dat daaruit is voortgekomen, zoals Optiver, IMC en Flow Traders. Voor studenten is het Amsterdamse kantoor van DRW een plek om in trading, quantitative research of technology te werken voor een groot, gediversifieerd Amerikaans handelsbedrijf, zonder Nederland te hoeven verlaten.",
   struct_en="DRW is organised around trading desks for its different asset classes, supported by quantitative research and a substantial technology organisation that builds trading systems and infrastructure in-house. Graduates typically enter as traders, quantitative researchers or software engineers, often rotating across products before specialising.",
   struct_nl="DRW is georganiseerd rond tradingdesks voor de verschillende activaklassen, ondersteund door quantitative research en een aanzienlijke technologieorganisatie die handelssystemen en infrastructuur zelf bouwt. Afgestudeerden komen doorgaans binnen als trader, quantitative researcher of software engineer, en draaien vaak eerst mee langs verschillende producten voordat ze zich specialiseren.",
   paths=[("trading","Trading")],
   join_en="DRW hires in Amsterdam through internships and graduate programmes for trading, research and technology. Selection typically includes rigorous quantitative and analytical testing, so numerical strength tends to matter more than a specific degree, though many hires come from technical or quantitative fields.",
   join_nl="DRW werft in Amsterdam via stages en graduate-programma's voor trading, research en technology. De selectie bevat doorgaans stevige kwantitatieve en analytische tests, waardoor numerieke sterkte vaak zwaarder telt dan een specifieke studie, al komen veel nieuwe medewerkers uit technische of kwantitatieve richtingen.",
   facts=[("Type","Type","Proprietary trading / market maker","Proprietary trading / market maker"),
     ("Head office","Hoofdkantoor","Chicago (Europe: Amsterdam)","Chicago (Europa: Amsterdam)"),
     ("Founded","Opgericht","1992","1992"),
     ("Ownership","Eigendom","Private","Privaat")]),

dict(slug="sig", name="Susquehanna International Group (SIG)", initials="SI", color="#8a1538", city="Amsterdam",
   types=["trading"],
   site="https://sig.com",
   tagline_en="A US options-trading and market-making partnership with a significant European office in Amsterdam.",
   tagline_nl="Een Amerikaans partnerschap in optiehandel en market making, met een groot Europees kantoor in Amsterdam.",
   intro_en="Susquehanna International Group, generally known as SIG, is a quantitative trading and market-making firm founded in 1987 near Philadelphia, Pennsylvania, by a group of friends with backgrounds in options trading and, notably, poker and game theory, which shaped its early approach to pricing risk under uncertainty. SIG is best known for options market making, but it also trades equities, fixed income and other asset classes, and has expanded into related activities such as venture capital investing. It operates as a private partnership rather than a publicly listed company. Over time SIG built out a network of offices across the Americas, Asia and Europe, including Amsterdam, to trade closer to local markets and exchange hours.",
   intro_nl="Susquehanna International Group, doorgaans SIG genoemd, is een kwantitatieve handels- en market making-firma die in 1987 werd opgericht in de buurt van Philadelphia, Pennsylvania, door een groep vrienden met een achtergrond in optiehandel en, opvallend genoeg, poker en speltheorie, wat de vroege manier van prijzen onder onzekerheid vormgaf. SIG staat vooral bekend om market making in opties, maar verhandelt ook aandelen, vastrentende waarden en andere activaklassen, en heeft zich uitgebreid naar aanverwante activiteiten zoals venture capital-investeringen. Het bedrijf opereert als een privaat partnerschap in plaats van een beursgenoteerde onderneming. In de loop der tijd bouwde SIG een netwerk van kantoren op in Amerika, Azie en Europa, waaronder Amsterdam, om dichter bij lokale markten en beursuren te handelen.",
   nl_en="SIG is a US partnership headquartered near Philadelphia, and Amsterdam is one of its European trading offices, part of a wider European network that also includes other cities. Its presence in Amsterdam is another example of a foreign trading firm setting up in the city because of its concentration of trading talent that traces back to the historic options exchange floor and the Dutch prop trading firms it produced, such as Optiver and IMC. For students, the Amsterdam office is where SIG's European options and equities trading and research work is largely based.",
   nl_nl="SIG is een Amerikaans partnerschap met hoofdkantoor bij Philadelphia, en Amsterdam is een van de Europese handelskantoren, onderdeel van een breder Europees netwerk dat ook andere steden omvat. De aanwezigheid in Amsterdam is opnieuw een voorbeeld van een buitenlandse handelsfirma die zich in de stad vestigt vanwege de concentratie aan handelstalent die teruggaat op de historische optiebeursvloer en de Nederlandse proprietary trading-firma's die daaruit voortkwamen, zoals Optiver en IMC. Voor studenten is het Amsterdamse kantoor de plek waar het grootste deel van het Europese optie- en aandelenhandels- en researchwerk van SIG is gevestigd.",
   struct_en="SIG's work centres on trading (pricing and managing risk in options and other products), quantitative research (developing pricing models and strategies) and technology (building the systems that support trading at scale). Graduates typically join as traders, quantitative researchers or software developers.",
   struct_nl="Het werk bij SIG draait om trading (het prijzen en beheren van risico in opties en andere producten), quantitative research (het ontwikkelen van prijsmodellen en strategieen) en technology (het bouwen van de systemen die trading op schaal ondersteunen). Afgestudeerden komen doorgaans binnen als trader, quantitative researcher of software developer.",
   paths=[("trading","Trading")],
   join_en="SIG recruits in Amsterdam through internships and graduate programmes for trading, research and technology roles. Its selection process is known for probability and game-theory-based assessments in addition to standard quantitative testing, so strong logical and numerical reasoning matters more than a specific degree.",
   join_nl="SIG werft in Amsterdam via stages en graduate-programma's voor trading-, research- en technologiefuncties. Het selectieproces staat bekend om kansrekening- en speltheoriegebaseerde opdrachten naast standaard kwantitatieve tests, waardoor sterk logisch en numeriek redeneren zwaarder weegt dan een specifieke studie.",
   facts=[("Type","Type","Proprietary trading / market maker","Proprietary trading / market maker"),
     ("Head office","Hoofdkantoor","Bala Cynwyd, Pennsylvania (Europe: Amsterdam)","Bala Cynwyd, Pennsylvania (Europa: Amsterdam)"),
     ("Founded","Opgericht","1987","1987"),
     ("Ownership","Eigendom","Private partnership","Privaat partnerschap")]),

dict(slug="jump-trading", name="Jump Trading", initials="JU", color="#1b1b3a", city="Amsterdam",
   types=["trading"],
   site="https://www.jumptrading.com",
   tagline_en="A Chicago-founded high-frequency and quantitative trading firm with a European office in Amsterdam.",
   tagline_nl="Een in Chicago opgerichte high-frequency en kwantitatieve handelsfirma met een Europees kantoor in Amsterdam.",
   intro_en="Jump Trading is a proprietary trading firm founded in Chicago in 1999 by two former futures pit traders at the Chicago Mercantile Exchange. It is best known for high-frequency and algorithmic trading in futures and other liquid instruments, using low-latency technology to react to price changes across global markets, and it has also become active in digital assets. Jump earns income from market making and from short-term quantitative strategies rather than from long-term investment positions. The firm is privately held and has grown from its Chicago base into a network of offices around the world, including Amsterdam, used to trade closer to European exchanges and time zones.",
   intro_nl="Jump Trading is een proprietary trading-firma die in 1999 in Chicago werd opgericht door twee voormalige futures-vloerhandelaren van de Chicago Mercantile Exchange. Het bedrijf staat vooral bekend om high-frequency en algoritmische handel in futures en andere liquide instrumenten, met technologie met lage latency om te reageren op prijsveranderingen op wereldwijde markten, en is inmiddels ook actief in digitale activa. Jump verdient aan market making en aan kortetermijn kwantitatieve strategieen, niet aan langetermijn beleggingsposities. Het bedrijf is privaat en groeide vanuit Chicago uit tot een netwerk van kantoren wereldwijd, waaronder Amsterdam, dat wordt gebruikt om dichter bij Europese beurzen en tijdzones te handelen.",
   nl_en="Jump Trading is a US firm headquartered in Chicago, and Amsterdam functions as one of its European offices for trading and technology. Its choice of Amsterdam fits a broader pattern among high-frequency and quantitative trading firms, which are drawn to the city's dense pool of trading and engineering talent shaped by the legacy of the historic Amsterdam options exchange floor and by neighbouring firms such as Optiver, IMC and Flow Traders. For students, Jump's Amsterdam office offers exposure to low-latency trading technology and quantitative strategy work within a large US trading firm.",
   nl_nl="Jump Trading is een Amerikaans bedrijf met hoofdkantoor in Chicago, en Amsterdam fungeert als een van de Europese kantoren voor trading en technology. De keuze voor Amsterdam past in een breder patroon onder high-frequency en kwantitatieve handelsfirma's, die worden aangetrokken door de dichte vijver aan handels- en engineeringtalent in de stad, gevormd door de erfenis van de historische Amsterdamse optiebeursvloer en door omliggende firma's zoals Optiver, IMC en Flow Traders. Voor studenten biedt het Amsterdamse kantoor van Jump blootstelling aan low-latency handelstechnologie en kwantitatief strategiewerk binnen een grote Amerikaanse handelsfirma.",
   struct_en="Jump's work is organised around trading and quantitative research, which develop and run trading strategies, and a large technology and engineering function responsible for the low-latency infrastructure the firm's strategies depend on. Graduates typically join as quantitative researchers, traders or software/hardware engineers.",
   struct_nl="Het werk bij Jump is georganiseerd rond trading en quantitative research, die handelsstrategieen ontwikkelen en uitvoeren, en een grote technology- en engineeringfunctie die verantwoordelijk is voor de low-latency infrastructuur waarop de strategieen van het bedrijf steunen. Afgestudeerden komen doorgaans binnen als quantitative researcher, trader of software-/hardware-engineer.",
   paths=[("trading","Trading")],
   join_en="Jump recruits in Amsterdam through internships and graduate programmes for trading, research and engineering roles. The process is highly quantitative and technical, so strong mathematical, programming or engineering ability generally matters more than a specific degree title.",
   join_nl="Jump werft in Amsterdam via stages en graduate-programma's voor trading-, research- en engineeringfuncties. Het proces is sterk kwantitatief en technisch, waardoor sterke wiskundige, programmeer- of technische vaardigheden doorgaans zwaarder wegen dan een specifieke studietitel.",
   facts=[("Type","Type","Proprietary trading / high-frequency trading","Proprietary trading / high-frequency trading"),
     ("Head office","Hoofdkantoor","Chicago (Europe: Amsterdam)","Chicago (Europa: Amsterdam)"),
     ("Founded","Opgericht","1999","1999"),
     ("Ownership","Eigendom","Private","Privaat")]),

dict(slug="tower-research-capital", name="Tower Research Capital", initials="TW", color="#a67c00", city="Amsterdam",
   types=["trading"],
   site="https://tower-research.com",
   tagline_en="A New York-founded quantitative trading firm with a European office in Amsterdam.",
   tagline_nl="Een in New York opgerichte kwantitatieve handelsfirma met een Europees kantoor in Amsterdam.",
   intro_en="Tower Research Capital is a quantitative trading firm founded in New York in 1998, making it one of the earlier firms to build automated, algorithmic trading strategies. It trades across asset classes including equities, futures and foreign exchange, generally through short-term, technology-driven strategies rather than long-term fundamental investing, acting as a liquidity provider on exchanges around the world. Tower is privately held and structured as an investment manager for its own trading capital rather than for outside client money. From its New York base it built out a global office network, including Amsterdam, to trade in European hours and access European markets directly.",
   intro_nl="Tower Research Capital is een kwantitatieve handelsfirma die in 1998 in New York werd opgericht, wat het een van de vroegere firma's maakt op het gebied van geautomatiseerde, algoritmische handelsstrategieen. Het bedrijf handelt in verschillende activaklassen, waaronder aandelen, futures en valuta, doorgaans via kortetermijn, technologiegedreven strategieen in plaats van langetermijn fundamentele beleggingen, en treedt op als liquiditeitsverschaffer op beurzen wereldwijd. Tower is privaat en gestructureerd als vermogensbeheerder voor zijn eigen handelskapitaal, niet voor extern klantgeld. Vanuit New York bouwde het bedrijf een wereldwijd kantorennetwerk op, waaronder Amsterdam, om tijdens Europese handelsuren te opereren en rechtstreeks toegang te hebben tot Europese markten.",
   nl_en="Tower Research Capital is a US firm headquartered in New York, with Amsterdam serving as its European trading office. As with other US quantitative trading firms, Amsterdam was a natural choice given the city's long history as a hub for options and derivatives trading, rooted in its historic exchange floor and the local firms, such as Optiver, IMC and Flow Traders, that grew out of it. For students, Tower's Amsterdam office provides access to algorithmic trading and technology work for a US firm without relocating outside the Netherlands.",
   nl_nl="Tower Research Capital is een Amerikaans bedrijf met hoofdkantoor in New York, waarbij Amsterdam dient als het Europese handelskantoor. Net als bij andere Amerikaanse kwantitatieve handelsfirma's was Amsterdam een voor de hand liggende keuze, gezien de lange geschiedenis van de stad als knooppunt voor optie- en derivatenhandel, geworteld in de historische beursvloer en de lokale firma's, zoals Optiver, IMC en Flow Traders, die daaruit zijn voortgekomen. Voor studenten biedt het Amsterdamse kantoor van Tower toegang tot algoritmische handel en technologiewerk voor een Amerikaans bedrijf, zonder buiten Nederland te hoeven verhuizen.",
   struct_en="Tower organises its work around trading teams that run algorithmic strategies, quantitative research that develops and tests models, and a technology organisation responsible for its trading infrastructure. Graduates typically join as quantitative researchers, traders or software engineers.",
   struct_nl="Tower organiseert het werk rond tradingteams die algoritmische strategieen draaien, quantitative research dat modellen ontwikkelt en test, en een technologieorganisatie die verantwoordelijk is voor de handelsinfrastructuur. Afgestudeerden komen doorgaans binnen als quantitative researcher, trader of software engineer.",
   paths=[("trading","Trading")],
   join_en="Tower recruits in Amsterdam through internships and graduate programmes for trading, research and technology roles. Selection is quantitative and technical in nature, so mathematical and programming ability tends to matter more than a specific field of study.",
   join_nl="Tower werft in Amsterdam via stages en graduate-programma's voor trading-, research- en technologiefuncties. De selectie is kwantitatief en technisch van aard, waardoor wiskundige en programmeervaardigheden doorgaans zwaarder wegen dan een specifieke studierichting.",
   facts=[("Type","Type","Proprietary trading / quantitative trading","Proprietary trading / quantitative trading"),
     ("Head office","Hoofdkantoor","New York (Europe: Amsterdam)","New York (Europa: Amsterdam)"),
     ("Founded","Opgericht","1998","1998"),
     ("Ownership","Eigendom","Private","Privaat")]),

dict(slug="aegon-asset-management", name="Aegon Asset Management", initials="AG", color="#003da5", city="The Hague",
   types=["asset-management"], site="https://www.aegonam.com",
   tagline_en="The international asset management arm of insurer Aegon, based in The Hague.",
   tagline_nl="De internationale vermogensbeheertak van verzekeraar Aegon, gevestigd in Den Haag.",
   intro_en="Aegon Asset Management is the international asset manager of the Aegon group, a Dutch financial services company with roots as an insurer going back to the nineteenth century. Aegon Asset Management itself was established as a separate asset management business in the late 1980s and invests across fixed income, equities, real assets and multi-asset strategies for both Aegon's own insurance balance sheets and external institutional and retail clients. It operates internationally, with investment teams in the Netherlands, the United States and the United Kingdom, among other locations. Following Aegon's 2023 combination of its Dutch insurance operations with a.s.r., Aegon Asset Management remained a wholly owned part of Aegon and continues to manage part of the combined group's investments under a long-term agreement.",
   intro_nl="Aegon Asset Management is de internationale vermogensbeheerder van de Aegon-groep, een Nederlandse financiele dienstverlener die zijn wortels als verzekeraar heeft in de negentiende eeuw. Aegon Asset Management zelf werd eind jaren tachtig als apart vermogensbeheerbedrijf opgezet en belegt in vastrentende waarden, aandelen, real assets en multi-assetstrategieen, zowel voor de eigen verzekeringsbalansen van Aegon als voor externe institutionele en particuliere klanten. Het bedrijf werkt internationaal, met beleggingsteams in onder meer Nederland, de Verenigde Staten en het Verenigd Koninkrijk. Na de samenvoeging van Aegons Nederlandse verzekeringsactiviteiten met a.s.r. in 2023 bleef Aegon Asset Management volledig eigendom van Aegon en beheert het onder een langetermijnovereenkomst nog steeds een deel van de beleggingen van de gecombineerde groep.",
   nl_en="The Dutch business is headquartered in The Hague, alongside Aegon's other Dutch activities, and manages investments for Aegon's insurance operations as well as Dutch and international institutional clients. For finance students it is one of the clearer routes into asset management from within a large, internationally connected Dutch financial group.",
   nl_nl="De Nederlandse tak is gevestigd in Den Haag, naast de andere Nederlandse activiteiten van Aegon, en beheert beleggingen voor de verzekeringsactiviteiten van Aegon en voor Nederlandse en internationale institutionele klanten. Voor finance-studenten is het een van de duidelijkere routes naar vermogensbeheer vanuit een grote, internationaal verbonden Nederlandse financiele groep.",
   struct_en="The organisation is built around investment teams by asset class, fixed income, equities, real assets and multi-asset, supported by research, risk management, client and distribution teams, and operations. Graduates typically start as analysts within an investment team or in a client-facing or risk-related support function.",
   struct_nl="De organisatie is opgebouwd rond beleggingsteams per beleggingscategorie: vastrentende waarden, aandelen, real assets en multi-asset, ondersteund door research-, risicobeheer-, klant- en distributieteams en operations. Afgestudeerden beginnen doorgaans als analisten binnen een beleggingsteam of in een klantgerichte of risicogerelateerde ondersteunende functie.",
   paths=[("asset-management","Asset Management"),("equity-research","Equity Research")],
   join_en="Aegon Asset Management offers internships and graduate roles, typically starting in an investment analyst or investment support position. As with most asset managers, a CFA charter is valued in investment roles but is not required to begin.",
   join_nl="Aegon Asset Management biedt stages en graduate-functies, doorgaans startend als investment analist of in een beleggingsondersteunende rol. Zoals bij de meeste vermogensbeheerders wordt een CFA-charter gewaardeerd in beleggingsfuncties, maar is het geen vereiste om te beginnen.",
   facts=[("Type","Type","Asset manager","Vermogensbeheerder"),("Head office","Hoofdkantoor","The Hague","Den Haag"),
     ("Founded","Opgericht","Established in the late 1980s as part of Aegon","Eind jaren tachtig opgericht als onderdeel van Aegon"),
     ("Ownership","Eigendom","Wholly owned subsidiary of Aegon","Volledige dochteronderneming van Aegon")]),

 dict(slug="achmea-investment-management", name="Achmea Investment Management", initials="AC", color="#0a7a3d", city="Zeist",
   types=["asset-management"], site="https://www.achmeainvestmentmanagement.nl",
   tagline_en="The fiduciary and asset management specialist of insurer Achmea, based in Zeist.",
   tagline_nl="De fiduciaire en vermogensbeheerspecialist van verzekeraar Achmea, gevestigd in Zeist.",
   intro_en="Achmea Investment Management is the institutional asset manager of the Achmea group, the Dutch insurer behind brands such as Centraal Beheer and Zilveren Kruis. The firm grew out of Achmea's long-standing pension and investment activities, previously operating under the name Syntrus Achmea Vermogensbeheer before it was rebranded. It manages investments for pension funds and other institutional investors across fixed income, equities and multi-asset strategies, and is one of the larger providers of fiduciary management in the Dutch market. Achmea Investment Management operates as a distinct business within the wider Achmea group, which is itself majority owned by the member association Vereniging Achmea alongside Rabobank as a strategic shareholder.",
   intro_nl="Achmea Investment Management is de institutionele vermogensbeheerder van de Achmea-groep, de Nederlandse verzekeraar achter merken als Centraal Beheer en Zilveren Kruis. Het bedrijf komt voort uit de langlopende pensioen- en beleggingsactiviteiten van Achmea en opereerde eerder onder de naam Syntrus Achmea Vermogensbeheer, voordat het werd omgedoopt. Het beheert beleggingen voor pensioenfondsen en andere institutionele beleggers in vastrentende waarden, aandelen en multi-assetstrategieen, en is een van de grotere aanbieders van fiduciair management in de Nederlandse markt. Achmea Investment Management opereert als apart bedrijfsonderdeel binnen de bredere Achmea-groep, die op haar beurt voor het merendeel eigendom is van de ledenvereniging Vereniging Achmea, met Rabobank als strategisch aandeelhouder.",
   nl_en="The office is in Zeist, in the same area as several other Dutch pension-sector organisations. For finance students it offers exposure to fiduciary management, a distinctly Dutch specialism that sits between traditional asset management and pension fund advisory.",
   nl_nl="Het kantoor staat in Zeist, in dezelfde regio als verschillende andere Nederlandse pensioenorganisaties. Voor finance-studenten biedt het bedrijf blootstelling aan fiduciair management, een typisch Nederlandse specialisatie die tussen traditioneel vermogensbeheer en pensioenfondsadvies in zit.",
   struct_en="The firm is organised around investment teams (fixed income, equities and multi-asset), a fiduciary management practice that advises and implements portfolios on behalf of pension fund clients, and supporting research, risk and client teams. Graduates typically join an investment or fiduciary team as an analyst.",
   struct_nl="Het bedrijf is opgebouwd rond beleggingsteams (vastrentende waarden, aandelen en multi-asset), een fiduciaire praktijk die namens pensioenfondsklanten portefeuilles adviseert en uitvoert, en ondersteunende research-, risico- en klantteams. Afgestudeerden komen doorgaans als analist terecht in een beleggings- of fiduciair team.",
   paths=[("asset-management","Asset Management")],
   join_en="Achmea Investment Management recruits interns and graduates mainly into investment analyst or fiduciary support roles. A quantitative or finance-related degree is common among entrants, and a CFA charter is valued for investment roles.",
   join_nl="Achmea Investment Management werft stagiairs en afgestudeerden vooral in investment analist- of fiduciaire ondersteunende functies. Een kwantitatieve of financieel-economische studie is gebruikelijk bij instromers, en een CFA-charter wordt gewaardeerd voor beleggingsfuncties.",
   facts=[("Type","Type","Fiduciary and asset manager","Fiduciair en vermogensbeheerder"),
     ("Head office","Hoofdkantoor","Zeist","Zeist"),
     ("Founded","Opgericht","Rebranded from Syntrus Achmea Vermogensbeheer in 2016","In 2016 omgedoopt vanuit Syntrus Achmea Vermogensbeheer"),
     ("Ownership","Eigendom","Part of Achmea","Onderdeel van Achmea")]),

 dict(slug="cardano", name="Cardano", initials="CA", color="#7c2d12", city="Rotterdam",
   types=["asset-management"], site="https://www.cardano.nl",
   tagline_en="A fiduciary and risk management specialist for pension funds and insurers, now part of Mercer.",
   tagline_nl="Een fiduciair en risicomanagementspecialist voor pensioenfondsen en verzekeraars, nu onderdeel van Mercer.",
   intro_en="Cardano is a fiduciary manager and investment risk specialist founded in the Netherlands around 2000, known in particular for its work on liability-driven investment for pension funds and insurers. In 2022 Cardano acquired the Dutch sustainable asset manager ACTIAM, and in 2023 the combined business was brought together under the single Cardano name, with ACTIAM's investment funds, processes and teams continuing under the Cardano brand. In November 2024 Cardano was itself acquired by Mercer, part of the global professional services firm Marsh McLennan, and now operates as part of Mercer's investment business in the Netherlands and the United Kingdom. It advises and manages assets for pension funds, insurers and other institutional clients, with a particular focus on risk management, liability-driven investing and sustainable and impact investing.",
   intro_nl="Cardano is een fiduciair vermogensbeheerder en specialist in beleggingsrisico, rond 2000 opgericht in Nederland en vooral bekend van zijn werk op het gebied van liability-driven investing voor pensioenfondsen en verzekeraars. In 2022 nam Cardano de Nederlandse duurzame vermogensbeheerder ACTIAM over, en in 2023 werden beide bedrijven samengebracht onder de naam Cardano, waarbij de beleggingsfondsen, processen en teams van ACTIAM onder het merk Cardano doorgingen. In november 2024 werd Cardano zelf overgenomen door Mercer, onderdeel van het wereldwijde adviesconcern Marsh McLennan, en het bedrijf opereert nu als onderdeel van de beleggingstak van Mercer in Nederland en het Verenigd Koninkrijk. Het adviseert en beheert vermogen voor pensioenfondsen, verzekeraars en andere institutionele klanten, met een focus op risicomanagement, liability-driven investing en duurzaam en impactbeleggen.",
   nl_en="Cardano's Dutch office is in Rotterdam, and the firm is one of the more specialised names in the Dutch pension and fiduciary management landscape. For students it is a route into risk-focused investment work, distinct from traditional stock-picking asset management.",
   nl_nl="Het Nederlandse kantoor van Cardano staat in Rotterdam, en het bedrijf is een van de meer gespecialiseerde namen in het Nederlandse pensioen- en fiduciaire landschap. Voor studenten is het een route naar risicogericht beleggingswerk, anders dan traditioneel vermogensbeheer gericht op aandelenselectie.",
   struct_en="The firm combines investment and risk management teams, a fiduciary management practice that works directly with pension fund and insurer clients, and the former ACTIAM investment fund range covering sustainable equities, bonds and impact strategies. Graduates typically start as an analyst in risk management, fiduciary management or one of the investment teams.",
   struct_nl="Het bedrijf combineert beleggings- en risicomanagementteams, een fiduciaire praktijk die rechtstreeks samenwerkt met pensioenfonds- en verzekeraarklanten, en het voormalige ACTIAM-fondsenaanbod met duurzame aandelen-, obligatie- en impactstrategieen. Afgestudeerden beginnen doorgaans als analist in risicomanagement, fiduciair management of een van de beleggingsteams.",
   paths=[("asset-management","Asset Management")],
   join_en="Cardano hires interns and graduates into analyst roles within risk management, fiduciary management and investment teams. Quantitative and finance-related degrees are common, and since the Mercer acquisition entrants also have access to Mercer's broader graduate infrastructure.",
   join_nl="Cardano werft stagiairs en afgestudeerden in analistfuncties binnen risicomanagement, fiduciair management en beleggingsteams. Kwantitatieve en financieel-economische studies komen veel voor, en sinds de overname door Mercer hebben instromers ook toegang tot de bredere graduate-infrastructuur van Mercer.",
   facts=[("Type","Type","Fiduciary manager / investment risk specialist","Fiduciair vermogensbeheerder / risicospecialist"),
     ("Head office","Hoofdkantoor","Rotterdam","Rotterdam"),
     ("Founded","Opgericht","Around 2000; rebranded from ACTIAM in 2023","Rond 2000 opgericht; in 2023 omgedoopt vanuit ACTIAM"),
     ("Ownership","Eigendom","Part of Mercer (Marsh McLennan)","Onderdeel van Mercer (Marsh McLennan)")]),

 dict(slug="asr-asset-management", name="a.s.r. asset management", initials="AS", color="#0f766e", city="Utrecht",
   types=["asset-management"], site="https://asrassetmanagement.com",
   tagline_en="The institutional asset management business of Dutch insurer a.s.r., strong in real estate and mortgages.",
   tagline_nl="De institutionele vermogensbeheertak van verzekeraar a.s.r., sterk in vastgoed en hypotheken.",
   intro_en="a.s.r. asset management is the institutional investment arm of a.s.r., a Dutch insurer whose predecessor companies date back to the nineteenth century and which took its current form through a series of mergers, most recently combining with Aegon's Dutch insurance business in 2023. It manages investments on behalf of a.s.r.'s own insurance balance sheet as well as external institutional investors, with particular strength in real estate, where a.s.r. real estate has invested for institutional clients for well over a century, and in Dutch residential mortgages. The business also covers fixed income and other real asset strategies such as infrastructure. a.s.r. is listed on Euronext Amsterdam.",
   intro_nl="a.s.r. asset management is de institutionele beleggingstak van a.s.r., een Nederlandse verzekeraar waarvan de voorlopers teruggaan tot de negentiende eeuw en die zijn huidige vorm kreeg via een reeks fusies, waarvan de meest recente in 2023 de samenvoeging met de Nederlandse verzekeringsactiviteiten van Aegon was. Het bedrijf beheert beleggingen voor de eigen verzekeringsbalans van a.s.r. en voor externe institutionele beleggers, met een sterke positie in vastgoed, waar a.s.r. real estate al ruim een eeuw voor institutionele klanten belegt, en in Nederlandse woninghypotheken. Daarnaast beslaat het bedrijf vastrentende waarden en andere real assets-strategieen zoals infrastructuur. a.s.r. staat genoteerd aan Euronext Amsterdam.",
   nl_en="The head office is in Utrecht, and the real estate and mortgage franchises in particular give the firm a distinct profile among Dutch asset managers. For finance students it is a relevant place to see how an insurer's balance sheet and external institutional money are managed side by side.",
   nl_nl="Het hoofdkantoor staat in Utrecht, en vooral de vastgoed- en hypothekentak geven het bedrijf een eigen profiel binnen het Nederlandse vermogensbeheerlandschap. Voor finance-studenten is het een relevante plek om te zien hoe de balans van een verzekeraar en extern institutioneel geld naast elkaar worden beheerd.",
   struct_en="The business is organised by asset class, including real estate (a.s.r. real estate), mortgages, fixed income and multi-asset, alongside research, risk and client teams that serve both internal insurance clients and external institutional investors. Graduates typically start as an analyst within one of these investment teams.",
   struct_nl="Het bedrijf is ingedeeld naar beleggingscategorie, waaronder vastgoed (a.s.r. real estate), hypotheken, vastrentende waarden en multi-asset, met daaromheen research-, risico- en klantteams die zowel interne verzekeringsklanten als externe institutionele beleggers bedienen. Afgestudeerden beginnen doorgaans als analist binnen een van deze beleggingsteams.",
   paths=[("asset-management","Asset Management"),("real-estate-finance","Real Estate Finance")],
   join_en="a.s.r. asset management offers internships and graduate roles, often starting in an analyst position within real estate, mortgages or one of the investment teams. Relevant finance, real estate or econometrics degrees are common entry points.",
   join_nl="a.s.r. asset management biedt stages en graduate-functies, vaak startend als analist binnen vastgoed, hypotheken of een van de beleggingsteams. Relevante studies zoals finance, vastgoedkunde of econometrie zijn gangbare instapwegen.",
   facts=[("Type","Type","Asset manager (insurer-owned)","Vermogensbeheerder (in eigendom van verzekeraar)"),
     ("Head office","Hoofdkantoor","Utrecht","Utrecht"),
     ("Founded","Opgericht","a.s.r. formed in 2000; predecessor companies much older","a.s.r. ontstaan in 2000; voorlopers veel ouder"),
     ("Ownership","Eigendom","Part of a.s.r., listed on Euronext Amsterdam","Onderdeel van a.s.r., genoteerd aan Euronext Amsterdam")]),

 dict(slug="apg", name="APG", initials="AP", color="#004b87", city="Heerlen",
   types=["pension","asset-management"], site="https://www.apg.nl",
   tagline_en="The Netherlands' largest pension asset manager and administrator, executing the pension scheme of ABP.",
   tagline_nl="De grootste pensioenuitvoerder van Nederland, die de pensioenregeling van ABP uitvoert.",
   intro_en="APG is a Dutch pension executor that combines pension administration and asset management on behalf of pension funds. It was established in 2008 as the executive organisation of Stichting Pensioenfonds ABP, the pension fund for Dutch government and education employees and the largest pension fund in the Netherlands, and later that year merged with Cordares, which administered pensions for the construction sector fund bpfBOUW. APG remains a direct subsidiary of ABP and is one of the largest pension asset managers in the world, investing pension contributions across equities, fixed income, real estate, infrastructure and other asset classes. APG has announced plans to focus its asset management activities exclusively on ABP over time, while continuing pension administration for several funds.",
   intro_nl="APG is een Nederlandse pensioenuitvoerder die pensioenadministratie en vermogensbeheer combineert namens pensioenfondsen. Het bedrijf werd in 2008 opgericht als uitvoeringsorganisatie van Stichting Pensioenfonds ABP, het pensioenfonds voor werknemers in het Nederlandse overheids- en onderwijsdomein en het grootste pensioenfonds van Nederland, en fuseerde later dat jaar met Cordares, dat de pensioenadministratie voor bouwsector-fonds bpfBOUW verzorgde. APG is nog steeds een directe dochteronderneming van ABP en is een van de grootste pensioenvermogensbeheerders ter wereld, en belegt pensioenpremies in aandelen, vastrentende waarden, vastgoed, infrastructuur en andere beleggingscategorieen. APG heeft aangekondigd zijn vermogensbeheeractiviteiten op termijn exclusief op ABP te richten, terwijl het de pensioenadministratie voor meerdere fondsen blijft uitvoeren.",
   nl_en="APG has its main offices in Heerlen and Amsterdam, with additional international offices supporting its global investment activities. Given its scale and the breadth of its investment mandate, APG is one of the most significant employers in Dutch institutional asset management and pension administration, and a well-known destination for finance graduates interested in long-horizon institutional investing.",
   nl_nl="APG heeft zijn belangrijkste kantoren in Heerlen en Amsterdam, met aanvullende internationale vestigingen die de wereldwijde beleggingsactiviteiten ondersteunen. Gezien de schaal en de breedte van het beleggingsmandaat is APG een van de belangrijkste werkgevers in Nederlands institutioneel vermogensbeheer en pensioenadministratie, en een bekende bestemming voor finance-afgestudeerden met interesse in langetermijn institutioneel beleggen.",
   struct_en="APG's asset management side is organised by asset class and region, covering equities, fixed income, real estate, infrastructure and private markets, supported by research, risk and responsible investment teams. Alongside this sits a large pension administration business handling contributions, records and payments for fund participants. Finance graduates typically join the investment side as an analyst or in a strategy, risk or responsible investment role.",
   struct_nl="De beleggingskant van APG is ingedeeld naar beleggingscategorie en regio, met aandelen, vastrentende waarden, vastgoed, infrastructuur en private markten, ondersteund door research-, risico- en verantwoord-beleggenteams. Daarnaast is er een grote pensioenadministratietak die premies, gegevens en uitkeringen voor deelnemers verwerkt. Finance-afgestudeerden komen doorgaans terecht aan de beleggingskant als analist of in een strategie-, risico- of verantwoord-beleggenrol.",
   paths=[("asset-management","Asset Management"),("real-estate-finance","Real Estate Finance")],
   join_en="APG offers internships, traineeships and graduate roles, typically starting as an analyst within one of the investment teams or in a supporting strategy, risk or data function. A quantitative, finance or econometrics background is common among entrants.",
   join_nl="APG biedt stages, traineeships en graduate-functies, doorgaans startend als analist binnen een van de beleggingsteams of in een ondersteunende strategie-, risico- of datafunctie. Een kwantitatieve, financieel-economische of econometrische achtergrond komt vaak voor bij instromers.",
   facts=[("Type","Type","Pension executor (asset management and administration)","Pensioenuitvoerder (vermogensbeheer en administratie)"),
     ("Head office","Hoofdkantoor","Heerlen and Amsterdam","Heerlen en Amsterdam"),
     ("Founded","Opgericht","2008","2008"),
     ("Ownership","Eigendom","Subsidiary of pension fund ABP","Dochteronderneming van pensioenfonds ABP")]),

 dict(slug="pggm", name="PGGM", initials="PG", color="#9a1f40", city="Zeist",
   types=["pension","asset-management"], site="https://www.pggm.nl",
   tagline_en="A large Dutch pension asset manager and administrator, executing the pension scheme of PFZW.",
   tagline_nl="Een grote Nederlandse pensioenuitvoerder, die de pensioenregeling van PFZW uitvoert.",
   intro_en="PGGM is a Dutch pension executor whose origins go back to a pension fund for the healthcare and social work sector founded in 1969. In 2008 the fund's policy-setting and execution functions were split: the fund itself continued as Stichting Pensioenfonds Zorg en Welzijn (PFZW), while a newly formed cooperative, PGGM, took over asset management and pension administration on its behalf. PGGM invests pension contributions across equities, fixed income, real estate, infrastructure and other asset classes, and also administers pensions and provides pension services to a small number of other Dutch pension funds. In 2024 PGGM took over pension administration for PMT from fellow pension executor MN, expanding the number of participants it serves.",
   intro_nl="PGGM is een Nederlandse pensioenuitvoerder die zijn oorsprong heeft in een pensioenfonds voor de sector zorg en welzijn, opgericht in 1969. In 2008 werden de beleidsvormende en uitvoerende functies van het fonds gesplitst: het fonds zelf ging verder als Stichting Pensioenfonds Zorg en Welzijn (PFZW), terwijl een nieuw opgerichte coöperatie, PGGM, namens het fonds het vermogensbeheer en de pensioenadministratie overnam. PGGM belegt pensioenpremies in aandelen, vastrentende waarden, vastgoed, infrastructuur en andere beleggingscategorieen, en verzorgt daarnaast pensioenadministratie en -diensten voor een klein aantal andere Nederlandse pensioenfondsen. In 2024 nam PGGM de pensioenadministratie van PMT over van collega-pensioenuitvoerder MN, waarmee het aantal deelnemers dat het bedient toenam.",
   nl_en="PGGM's head office is in Zeist, and following the 2024 integration with part of MN it also has a substantial presence in The Hague. It is one of the largest institutional investors in the Netherlands and a well-known employer for finance graduates interested in pension investing on behalf of healthcare and social work sector employees.",
   nl_nl="Het hoofdkantoor van PGGM staat in Zeist, en na de integratie in 2024 met een deel van MN heeft het bedrijf ook een substantiele aanwezigheid in Den Haag. Het is een van de grootste institutionele beleggers van Nederland en een bekende werkgever voor finance-afgestudeerden die geinteresseerd zijn in pensioenbeleggen namens werknemers in de zorg- en welzijnssector.",
   struct_en="PGGM's investment side is organised by asset class, including equities, fixed income, real estate, infrastructure and private equity, supported by responsible investment, risk and research teams. Alongside this sits a large pension administration and client services organisation. Finance graduates typically start as an analyst within an investment team or in a supporting strategy or risk role.",
   struct_nl="De beleggingskant van PGGM is ingedeeld naar beleggingscategorie, waaronder aandelen, vastrentende waarden, vastgoed, infrastructuur en private equity, ondersteund door teams voor verantwoord beleggen, risico en research. Daarnaast is er een grote organisatie voor pensioenadministratie en klantdiensten. Finance-afgestudeerden beginnen doorgaans als analist binnen een beleggingsteam of in een ondersteunende strategie- of risicorol.",
   paths=[("asset-management","Asset Management"),("real-estate-finance","Real Estate Finance")],
   join_en="PGGM offers internships and graduate roles, typically starting as an analyst within one of the investment teams. A quantitative, finance or econometrics background is common, and a CFA charter is valued for investment roles.",
   join_nl="PGGM biedt stages en graduate-functies, doorgaans startend als analist binnen een van de beleggingsteams. Een kwantitatieve, financieel-economische of econometrische achtergrond komt vaak voor, en een CFA-charter wordt gewaardeerd voor beleggingsfuncties.",
   facts=[("Type","Type","Pension executor (asset management and administration)","Pensioenuitvoerder (vermogensbeheer en administratie)"),
     ("Head office","Hoofdkantoor","Zeist","Zeist"),
     ("Founded","Opgericht","Pension fund founded 1969; PGGM formed as cooperative in 2008","Pensioenfonds opgericht in 1969; PGGM als coöperatie gevormd in 2008"),
     ("Ownership","Eigendom","Cooperative, executes the pension scheme of PFZW","Coöperatie, voert de pensioenregeling van PFZW uit")]),

 dict(slug="mn", name="MN", initials="MO", color="#5b3a29", city="The Hague",
   types=["pension","asset-management"], site="https://www.mn.nl",
   tagline_en="A fiduciary asset manager for Dutch pension funds, historically rooted in the metal and technology sector.",
   tagline_nl="Een fiduciair vermogensbeheerder voor Nederlandse pensioenfondsen, van oudsher geworteld in de metaal- en technologiesector.",
   intro_en="MN is a Dutch fiduciary asset manager based in The Hague, originating in the early 1990s from the pension organisation for the metal and technology sector. It manages investments on behalf of a number of Dutch pension funds, most notably PMT, the large pension fund for the metal and technology industry, and PME, the pension fund for the metal and electrical engineering sector, as well as several smaller company pension funds. MN operates without a profit motive and works on a fiduciary basis, meaning it advises on and implements investment policy set by its pension fund clients. In 2024 MN's pension administration activities for PMT transferred to fellow pension executor PGGM, so MN now focuses on fiduciary asset management for its pension fund clients.",
   intro_nl="MN is een Nederlandse fiduciair vermogensbeheerder gevestigd in Den Haag, die begin jaren negentig is voortgekomen uit de pensioenorganisatie voor de metaal- en technologiesector. Het bedrijf beheert beleggingen namens een aantal Nederlandse pensioenfondsen, met name PMT, het grote pensioenfonds voor de metaal- en technieksector, en PME, het pensioenfonds voor de metalektro, plus enkele kleinere ondernemingspensioenfondsen. MN werkt zonder winstoogmerk en op fiduciaire basis, wat betekent dat het advies geeft over en uitvoering geeft aan het beleggingsbeleid dat de pensioenfondsklanten zelf vaststellen. In 2024 ging de pensioenadministratie van MN voor PMT over naar collega-pensioenuitvoerder PGGM, waardoor MN zich nu richt op fiduciair vermogensbeheer voor zijn pensioenfondsklanten.",
   nl_en="MN's office is in The Hague, in the same city as several other Dutch financial institutions. For finance students it offers a route into fiduciary asset management with a strong industrial-sector client base, distinct from the healthcare-linked PGGM or government-linked APG.",
   nl_nl="Het kantoor van MN staat in Den Haag, in dezelfde stad als verschillende andere Nederlandse financiele instellingen. Voor finance-studenten biedt het bedrijf een route naar fiduciair vermogensbeheer met een sterke klantenbasis in de industriele sector, anders dan het aan de zorg gelinkte PGGM of het aan de overheid gelinkte APG.",
   struct_en="MN is organised around investment teams by asset class, including equities, fixed income, real estate and private markets, together with a fiduciary management practice that works directly with pension fund boards, and supporting risk, research and client teams. Finance graduates typically start as an analyst within an investment or fiduciary team.",
   struct_nl="MN is opgebouwd rond beleggingsteams per beleggingscategorie, waaronder aandelen, vastrentende waarden, vastgoed en private markten, samen met een fiduciaire praktijk die rechtstreeks samenwerkt met pensioenfondsbesturen, en ondersteunende risico-, research- en klantteams. Finance-afgestudeerden beginnen doorgaans als analist binnen een beleggings- of fiduciair team.",
   paths=[("asset-management","Asset Management")],
   join_en="MN offers internships and graduate roles, typically starting as an analyst within an investment or fiduciary management team. A quantitative, finance or econometrics background is common among entrants.",
   join_nl="MN biedt stages en graduate-functies, doorgaans startend als analist binnen een beleggings- of fiduciair managementteam. Een kwantitatieve, financieel-economische of econometrische achtergrond komt vaak voor bij instromers.",
   facts=[("Type","Type","Fiduciary asset manager","Fiduciair vermogensbeheerder"),
     ("Head office","Hoofdkantoor","The Hague","Den Haag"),
     ("Founded","Opgericht","Early 1990s, from the metal sector pension organisation","Begin jaren negentig, vanuit de pensioenorganisatie voor de metaalsector"),
     ("Ownership","Eigendom","Owned by its pension fund clients, mainly PMT","Eigendom van de aangesloten pensioenfondsen, voornamelijk PMT")]),

dict(slug="pwc-netherlands", name="PwC Netherlands", initials="PW", color="#ff8200", city="Amsterdam",
       types=["advisory","pe-dealmaking"], site="https://www.pwc.nl",
       tagline_en="One of the Big Four: audit, tax, consulting and deals advisory, including corporate finance and M&A.",
       tagline_nl="Een van de Big Four: audit, belastingadvies, consulting en deals advisory, waaronder corporate finance en M&A.",
       intro_en="PwC is one of the Big Four professional-services firms and one of the largest employers in Dutch business and professional services. The Dutch firm traces its roots back over a century, through a long line of mergers among Dutch and international accountancy practices, and today operates under the global PwC network. It combines audit and assurance, tax and legal services, consulting, and a dedicated deals practice. That deals practice covers corporate finance and M&A advice, transaction services (financial due diligence), valuations and business restructuring, serving clients from large corporates to private equity investors.",
       intro_nl="PwC is een van de Big Four-dienstverleners en een van de grootste werkgevers in de Nederlandse zakelijke en professionele dienstverlening. De Nederlandse organisatie heeft wortels die meer dan een eeuw teruggaan, via een lange reeks fusies tussen Nederlandse en internationale accountantskantoren, en opereert tegenwoordig onder het wereldwijde PwC-netwerk. Het combineert audit en assurance, belasting- en juridisch advies, consulting en een aparte deals-praktijk. Die deals-praktijk omvat corporate finance en M&A-advies, transaction services (financiele due diligence), waarderingen en bedrijfsherstructurering, voor klanten varierend van grote ondernemingen tot private-equity-investeerders.",
       nl_en="The Dutch head office is in Amsterdam, with offices across the country. PwC is one of the most recognised employers among finance students in the Netherlands, and a common entry point into either audit or deal-advisory work.",
       nl_nl="Het Nederlandse hoofdkantoor staat in Amsterdam, met kantoren door het hele land. PwC is een van de bekendste werkgevers onder finance-studenten in Nederland, en een gebruikelijke toegangspoort tot audit of dealadvies.",
       struct_en="The firm is organised into a handful of large practices: Assurance, Tax & Legal, Consulting, and Deals. The Deals practice is where the transaction work sits, corporate finance and M&A advice, transaction services, valuations and restructuring, and it is this practice that most finance students target when they apply.",
       struct_nl="Het bedrijf is ingedeeld in een aantal grote praktijken: Assurance, Tax & Legal, Consulting en Deals. In de Deals-praktijk zit het transactiewerk: corporate finance en M&A-advies, transaction services, waarderingen en herstructurering. Dit is de praktijk waar de meeste finance-studenten op solliciteren.",
       paths=[("corporate-finance","Corporate Finance"),("ma","M&A"),("transaction-services","Transaction Services"),("valuation","Valuation")],
       join_en="Students typically join through an internship, a working-student role or the graduate programme, often starting in audit or within the Deals practice itself. Many later move on to corporate finance, private equity or industry roles after a few years of deal experience.",
       join_nl="Studenten stromen meestal in via een stage, een werkstudentbaan of het traineeprogramma, vaak startend in audit of direct binnen de Deals-praktijk. Velen stappen na een paar jaar deal-ervaring door naar corporate finance, private equity of het bedrijfsleven.",
       facts=[("Type","Type","Big Four / advisory","Big Four / advies"),("Head office (NL)","Hoofdkantoor (NL)","Amsterdam","Amsterdam"),
         ("Part of","Onderdeel van","PwC (global)","PwC (wereldwijd)"),("Sector","Sector","Accountancy & advisory","Accountancy & advies")]),

    dict(slug="ey-netherlands", name="EY Netherlands", initials="EY", color="#ffc700", city="Amsterdam",
       types=["advisory","pe-dealmaking"], site="https://www.ey.com/en_nl",
       tagline_en="One of the Big Four: audit, tax, strategy and transactions advisory, including M&A and corporate finance.",
       tagline_nl="Een van de Big Four: audit, belastingadvies, strategie en transactieadvies, waaronder M&A en corporate finance.",
       intro_en="EY is one of the Big Four professional-services firms and, like the other three, one of the largest employers in Dutch business services. The Dutch firm has a history stretching back more than a century through predecessor accountancy practices and today operates under the global EY network. Its main service lines are Assurance, Tax, Consulting, and Strategy and Transactions. The Strategy and Transactions practice includes corporate finance advice, M&A support on the buy side and sell side, transaction diligence, valuations and restructuring, serving corporates, private equity firms and public-sector clients.",
       intro_nl="EY is een van de Big Four-dienstverleners en, net als de andere drie, een van de grootste werkgevers in de Nederlandse zakelijke dienstverlening. De Nederlandse organisatie kent een geschiedenis van meer dan een eeuw via voorgangers in de accountancy en opereert tegenwoordig onder het wereldwijde EY-netwerk. De belangrijkste praktijken zijn Assurance, Tax, Consulting en Strategy and Transactions. De praktijk Strategy and Transactions omvat corporate finance-advies, M&A-ondersteuning aan koop- en verkoopzijde, transactie due diligence, waarderingen en herstructurering, voor ondernemingen, private-equity-partijen en publieke opdrachtgevers.",
       nl_en="EY's Dutch head office is in Amsterdam. It is one of the most familiar names for finance students in the Netherlands, and a well-trodden route into audit, consulting or deal-advisory work.",
       nl_nl="Het Nederlandse hoofdkantoor van EY staat in Amsterdam. Het is een van de bekendste namen onder finance-studenten in Nederland, en een veelbewandelde route naar audit, consulting of dealadvies.",
       struct_en="The firm is built around four main practices: Assurance, Tax, Consulting, and Strategy and Transactions. It is the Strategy and Transactions practice, whose strategy work is sometimes carried under the EY-Parthenon name, where the corporate finance, M&A advisory and transaction services teams sit, which is what most finance students are aiming for.",
       struct_nl="Het bedrijf is opgebouwd rond vier hoofdpraktijken: Assurance, Tax, Consulting en Strategy and Transactions. In de praktijk Strategy and Transactions, waarvan het strategiewerk soms onder de naam EY-Parthenon loopt, zitten de teams voor corporate finance, M&A-advies en transaction services. Dat is het onderdeel waar de meeste finance-studenten op mikken.",
       paths=[("ma","M&A"),("corporate-finance","Corporate Finance"),("transaction-services","Transaction Services"),("valuation","Valuation")],
       join_en="Entry is usually through an internship, working-student position or the graduate programme, frequently starting in audit or directly within Strategy and Transactions. Deal experience here is a common stepping stone towards corporate finance, private equity or in-house roles.",
       join_nl="Instroom verloopt meestal via een stage, een werkstudentplek of het traineeprogramma, vaak startend in audit of direct binnen Strategy and Transactions. Deal-ervaring hier is een gebruikelijke opstap naar corporate finance, private equity of interne functies bij bedrijven.",
       facts=[("Type","Type","Big Four / advisory","Big Four / advies"),("Head office (NL)","Hoofdkantoor (NL)","Amsterdam","Amsterdam"),
         ("Part of","Onderdeel van","EY (global)","EY (wereldwijd)"),("Sector","Sector","Accountancy & advisory","Accountancy & advies")]),

    dict(slug="kpmg-netherlands", name="KPMG Netherlands", initials="KM", color="#003087", city="Amstelveen",
       types=["advisory","pe-dealmaking"], site="https://kpmg.com/nl",
       tagline_en="One of the Big Four: audit, tax, advisory and deal advisory, including M&A and corporate finance.",
       tagline_nl="Een van de Big Four: audit, belastingadvies, advisory en deal advisory, waaronder M&A en corporate finance.",
       intro_en="KPMG is one of the Big Four professional-services firms and a major employer in Dutch business services. The Dutch firm has operated under the KPMG name since the international network was formed through a series of mergers in the twentieth century, building on Dutch accountancy practices that go back further still. Its main service lines are Audit, Tax & Legal, and Advisory. Within Advisory sits Deal Advisory, covering corporate finance and M&A support, transaction services (financial due diligence), valuations and restructuring, alongside management consulting and risk advisory.",
       intro_nl="KPMG is een van de Big Four-dienstverleners en een grote werkgever in de Nederlandse zakelijke dienstverlening. De Nederlandse organisatie draagt de naam KPMG sinds het internationale netwerk in de twintigste eeuw ontstond via een reeks fusies, voortbouwend op Nederlandse accountancypraktijken die verder teruggaan. De belangrijkste praktijken zijn Audit, Tax & Legal en Advisory. Binnen Advisory zit Deal Advisory, met corporate finance- en M&A-ondersteuning, transaction services (financiele due diligence), waarderingen en herstructurering, naast management consulting en risicoadvies.",
       nl_en="The Dutch head office is in Amstelveen, near Amsterdam, with offices elsewhere in the country. KPMG is one of the standard first employers finance students consider, whether in audit or on the deal-advisory side.",
       nl_nl="Het Nederlandse hoofdkantoor staat in Amstelveen, bij Amsterdam, met kantoren elders in het land. KPMG is een van de vanzelfsprekende eerste werkgevers voor finance-studenten, of dat nu in audit is of aan de dealadvies-kant.",
       struct_en="The firm is organised into Audit, Tax & Legal, and Advisory. Deal Advisory, part of the Advisory practice, is where the transaction work sits: corporate finance, M&A support, transaction services and valuations, which is the entry point most finance students look for.",
       struct_nl="Het bedrijf is ingedeeld in Audit, Tax & Legal en Advisory. Deal Advisory, onderdeel van de Advisory-praktijk, is waar het transactiewerk zit: corporate finance, M&A-ondersteuning, transaction services en waarderingen. Dit is de instap die de meeste finance-studenten zoeken.",
       paths=[("ma","M&A"),("corporate-finance","Corporate Finance"),("transaction-services","Transaction Services"),("valuation","Valuation")],
       join_en="Students usually start through an internship, a working-student role or the graduate intake, often in audit or within Deal Advisory itself. It is a common first step before moving into corporate finance, private equity or industry.",
       join_nl="Studenten starten meestal via een stage, een werkstudentbaan of de startersinstroom, vaak in audit of direct binnen Deal Advisory. Het is een gebruikelijke eerste stap voordat men doorstroomt naar corporate finance, private equity of het bedrijfsleven.",
       facts=[("Type","Type","Big Four / advisory","Big Four / advies"),("Head office (NL)","Hoofdkantoor (NL)","Amstelveen","Amstelveen"),
         ("Part of","Onderdeel van","KPMG (global)","KPMG (wereldwijd)"),("Sector","Sector","Accountancy & advisory","Accountancy & advies")]),

    dict(slug="bdo-netherlands", name="BDO Netherlands", initials="BO", color="#e2001a", city="Eindhoven",
       types=["advisory","pe-dealmaking"], site="https://www.bdo.nl",
       tagline_en="A mid-tier accountancy and advisory network with a Dutch deal advisory practice covering corporate finance and M&A.",
       tagline_nl="Een middelgroot accountancy- en adviesnetwerk met een Nederlandse deal advisory-praktijk voor corporate finance en M&A.",
       intro_en="BDO is a member firm of BDO International, one of the larger accountancy and advisory networks in the world outside the Big Four. The Dutch practice traces its roots to accountancy firms founded in the first half of the twentieth century that later joined the international BDO network. In the Netherlands, BDO combines audit, tax and accountancy services with an advisory arm that includes Deal Advisory, corporate finance, valuations, debt advisory, and buy-side and sell-side transaction (due diligence) support, working mostly for mid-market companies, private equity investors and family-owned businesses.",
       intro_nl="BDO is een lid-organisatie van BDO International, een van de grotere accountancy- en adviesnetwerken ter wereld buiten de Big Four. De Nederlandse praktijk heeft wortels in accountantskantoren die in de eerste helft van de twintigste eeuw zijn opgericht en die later aansloten bij het internationale BDO-netwerk. In Nederland combineert BDO audit, belastingadvies en accountancy met een adviestak die Deal Advisory omvat: corporate finance, waarderingen, debt advisory en ondersteuning bij aan- en verkooptransacties (due diligence), vooral voor middelgrote ondernemingen, private-equity-investeerders en familiebedrijven.",
       nl_en="The Dutch head office is in Eindhoven, with a wide network of offices across the country. BDO is a well-known name for finance students, particularly those interested in mid-market audit or deal work rather than the largest listed-company clients.",
       nl_nl="Het Nederlandse hoofdkantoor staat in Eindhoven, met een breed netwerk van kantoren door het hele land. BDO is een bekende naam onder finance-studenten, vooral voor wie geinteresseerd is in audit of dealwerk in het middensegment in plaats van de grootste beursgenoteerde klanten.",
       struct_en="BDO in the Netherlands is organised around Audit & Assurance, Tax, Accountancy and Advisory. The Deal Advisory practice within Advisory is where the transaction work sits, corporate finance, M&A support, due diligence, debt advisory and valuations, and the firm describes it as one of the larger deal advisory teams serving private equity and family-owned businesses in the Dutch market.",
       struct_nl="BDO Nederland is ingedeeld in Audit & Assurance, Tax, Accountancy en Advisory. In de Deal Advisory-praktijk binnen Advisory zit het transactiewerk: corporate finance, M&A-ondersteuning, due diligence, debt advisory en waarderingen. Het bedrijf omschrijft dit als een van de grotere deal advisory-teams voor private equity en familiebedrijven in de Nederlandse markt.",
       paths=[("corporate-finance","Corporate Finance"),("ma","M&A"),("debt-advisory","Debt Advisory"),("valuation","Valuation")],
       join_en="Students typically join through an internship, a working-student role or the graduate programme, often starting in audit or accountancy before moving into Deal Advisory. It can be a practical first step towards corporate finance or private equity roles, particularly for those interested in mid-market deals.",
       join_nl="Studenten stromen meestal in via een stage, een werkstudentbaan of het traineeprogramma, vaak startend in audit of accountancy voordat ze doorstromen naar Deal Advisory. Het kan een praktische eerste stap zijn richting corporate finance of private equity, vooral voor wie geinteresseerd is in middensegment-deals.",
       facts=[("Type","Type","Accountancy & advisory network","Accountancy- en adviesnetwerk"),("Head office (NL)","Hoofdkantoor (NL)","Eindhoven","Eindhoven"),
         ("Part of","Onderdeel van","BDO International","BDO International"),("Sector","Sector","Accountancy & advisory","Accountancy & advies")]),

    dict(slug="forvis-mazars-netherlands", name="Forvis Mazars Netherlands", initials="FZ", color="#12234f", city="Rotterdam",
       types=["advisory","pe-dealmaking"], site="https://www.forvismazars.com/nl/en",
       tagline_en="A top ten global accountancy network, formed from Mazars and Forvis, with a Dutch corporate finance and M&A practice.",
       tagline_nl="Een wereldwijd top tien accountancynetwerk, ontstaan uit Mazars en Forvis, met een Nederlandse corporate finance- en M&A-praktijk.",
       intro_en="Forvis Mazars is the network formed when the French-rooted firm Mazars and the American firm Forvis combined under a single global brand, creating one of the larger accountancy and advisory networks in the world. In the Netherlands the firm operates under the name it carried as Mazars for decades before the rebrand, offering audit and assurance, tax, and financial advisory services. The financial advisory practice includes corporate finance and M&A support, financial and tax due diligence, valuations, and litigation support, serving both Dutch mid-market companies and cross-border transactions through the international network.",
       intro_nl="Forvis Mazars is het netwerk dat is ontstaan toen het Franse Mazars en het Amerikaanse Forvis samengingen onder een gezamenlijk wereldwijd merk, wat een van de grotere accountancy- en adviesnetwerken ter wereld opleverde. In Nederland opereert de organisatie onder de naam die zij decennialang als Mazars droeg voordat de naam veranderde, met audit en assurance, belastingadvies en financial advisory. De financial advisory-praktijk omvat corporate finance- en M&A-ondersteuning, financiele en fiscale due diligence, waarderingen en forensisch advies, voor zowel Nederlandse middelgrote bedrijven als grensoverschrijdende transacties via het internationale netwerk.",
       nl_en="The Dutch head office is in Rotterdam, with several other offices around the country. Forvis Mazars is a familiar name for finance students who want exposure to audit or mid-market deal work at a firm smaller than the Big Four but with an international network behind it.",
       nl_nl="Het Nederlandse hoofdkantoor staat in Rotterdam, met verschillende andere kantoren door het land. Forvis Mazars is een bekende naam voor finance-studenten die audit of dealwerk in het middensegment willen ervaren bij een kantoor dat kleiner is dan de Big Four, maar met een internationaal netwerk erachter.",
       struct_en="The Dutch firm is organised into Audit & Assurance, Tax, and Financial Advisory. The transaction work, corporate finance and M&A advice, due diligence and valuations, sits within Financial Advisory, which collaborates closely with corporate finance teams in the firm's other country practices on cross-border deals.",
       struct_nl="De Nederlandse organisatie is ingedeeld in Audit & Assurance, Tax en Financial Advisory. Het transactiewerk, corporate finance- en M&A-advies, due diligence en waarderingen, zit binnen Financial Advisory, die nauw samenwerkt met corporate finance-teams in andere landenpraktijken van de organisatie bij grensoverschrijdende deals.",
       paths=[("corporate-finance","Corporate Finance"),("ma","M&A"),("valuation","Valuation")],
       join_en="Students usually enter through an internship, a working-student role or the graduate programme, often starting in audit before moving towards Financial Advisory. It offers a smaller-firm route into deal work compared with the Big Four, with international transaction exposure through the network.",
       join_nl="Studenten komen meestal binnen via een stage, een werkstudentbaan of het traineeprogramma, vaak startend in audit voordat ze doorstromen naar Financial Advisory. Het biedt een instap in dealwerk bij een kleinere organisatie dan de Big Four, met internationale transactie-ervaring via het netwerk.",
       facts=[("Type","Type","Accountancy & advisory network","Accountancy- en adviesnetwerk"),("Head office (NL)","Hoofdkantoor (NL)","Rotterdam","Rotterdam"),
         ("Part of","Onderdeel van","Forvis Mazars (global network)","Forvis Mazars (wereldwijd netwerk)"),("Sector","Sector","Accountancy & advisory","Accountancy & advies")]),

    dict(slug="grant-thornton-netherlands", name="Grant Thornton Netherlands", initials="GN", color="#7c3aed", city="Amsterdam",
       types=["advisory","pe-dealmaking"], site="https://www.grantthornton.nl",
       tagline_en="A global accountancy and advisory network with a Dutch corporate finance and deal advisory practice.",
       tagline_nl="Een wereldwijd accountancy- en adviesnetwerk met een Nederlandse corporate finance- en deal advisory-praktijk.",
       intro_en="Grant Thornton is a member firm of Grant Thornton International, one of the larger networks of independent accounting and advisory firms in the world. The Dutch firm offers audit, tax and (financial) advisory services from a handful of offices around the country. Within advisory sits a Deal Advisory practice covering corporate finance, M&A support on both the buy side and sell side, due diligence and valuations, alongside broader consulting and legal services, aimed mainly at mid-sized Dutch companies and their owners.",
       intro_nl="Grant Thornton is een lid-organisatie van Grant Thornton International, een van de grotere netwerken van onafhankelijke accountancy- en adviesorganisaties ter wereld. De Nederlandse organisatie biedt audit, belastingadvies en (financial) advisory vanuit een aantal kantoren door het land. Binnen advisory zit een Deal Advisory-praktijk met corporate finance, M&A-ondersteuning aan koop- en verkoopzijde, due diligence en waarderingen, naast bredere consulting- en juridische diensten, vooral gericht op middelgrote Nederlandse bedrijven en hun eigenaren.",
       nl_en="The Dutch head office is in Amsterdam, with other offices including Rotterdam. Grant Thornton is a somewhat smaller name than the Big Four for finance students, but offers a comparable route into audit or mid-market deal advisory work.",
       nl_nl="Het Nederlandse hoofdkantoor staat in Amsterdam, met andere kantoren waaronder Rotterdam. Grant Thornton is voor finance-studenten een wat kleinere naam dan de Big Four, maar biedt een vergelijkbare route naar audit of dealadvies in het middensegment.",
       struct_en="The firm is organised into Audit, Tax, and Advisory (which includes Corporate Finance, Legal and consulting services). The Corporate Finance team within Advisory handles the transaction work, deal support, due diligence and valuations, which is where most finance students aim to work.",
       struct_nl="Het bedrijf is ingedeeld in Audit, Tax en Advisory (waaronder Corporate Finance, Legal en consultingdiensten vallen). Het Corporate Finance-team binnen Advisory doet het transactiewerk: dealondersteuning, due diligence en waarderingen. Dat is waar de meeste finance-studenten willen werken.",
       paths=[("corporate-finance","Corporate Finance"),("ma","M&A"),("valuation","Valuation")],
       join_en="Students typically join through an internship, a working-student role or the graduate programme, often starting in audit before moving into Corporate Finance. It offers a route into mid-market deal work that can lead on to private equity, corporate finance boutiques or industry roles.",
       join_nl="Studenten stromen meestal in via een stage, een werkstudentbaan of het traineeprogramma, vaak startend in audit voordat ze doorstromen naar Corporate Finance. Het biedt een route naar dealwerk in het middensegment, van waaruit velen doorstromen naar private equity, corporate finance-boutiques of het bedrijfsleven.",
       facts=[("Type","Type","Accountancy & advisory network","Accountancy- en adviesnetwerk"),("Head office (NL)","Hoofdkantoor (NL)","Amsterdam","Amsterdam"),
         ("Part of","Onderdeel van","Grant Thornton International","Grant Thornton International"),("Sector","Sector","Accountancy & advisory","Accountancy & advies")]),

    dict(slug="baker-tilly-netherlands", name="Baker Tilly Netherlands", initials="BK", color="#00a19a", city="Utrecht",
       types=["advisory","pe-dealmaking"], site="https://www.bakertilly.nl",
       tagline_en="A global accountancy and advisory network with a Dutch corporate finance practice serving mid-market deals.",
       tagline_nl="Een wereldwijd accountancy- en adviesnetwerk met een Nederlandse corporate finance-praktijk voor middensegment-deals.",
       intro_en="Baker Tilly is a member firm of Baker Tilly International, one of the larger global networks of independent accounting and advisory firms. The Dutch firm has a long history in Dutch accountancy, built up over more than a century through a series of local firms that eventually joined the Baker Tilly network. It offers audit, tax and legal advisory alongside a Corporate Finance practice covering company acquisitions and sales, due diligence, valuations and financing advice, primarily for mid-sized Dutch businesses and their owners.",
       intro_nl="Baker Tilly is een lid-organisatie van Baker Tilly International, een van de grotere wereldwijde netwerken van onafhankelijke accountancy- en adviesorganisaties. De Nederlandse organisatie heeft een lange geschiedenis in de Nederlandse accountancy, opgebouwd over meer dan een eeuw via een reeks lokale kantoren die uiteindelijk aansloten bij het Baker Tilly-netwerk. Het biedt audit, belastingadvies en juridisch advies naast een Corporate Finance-praktijk voor bedrijfsovernames en -verkopen, due diligence, waarderingen en financieringsadvies, vooral voor middelgrote Nederlandse ondernemingen en hun eigenaren.",
       nl_en="The Dutch head office is in Utrecht, with branches across the country. Baker Tilly is a less prominent name among finance students than the Big Four, but its Corporate Finance team offers a real route into mid-market deal work.",
       nl_nl="Het Nederlandse hoofdkantoor staat in Utrecht, met vestigingen door het hele land. Baker Tilly is een minder prominente naam onder finance-studenten dan de Big Four, maar het Corporate Finance-team biedt een echte route naar dealwerk in het middensegment.",
       struct_en="The firm is organised into Audit, Tax, Legal and Corporate Finance, alongside smaller specialist practices. The Corporate Finance team handles acquisition and sale processes, due diligence and valuations, and is the practice most relevant to finance students interested in deal work.",
       struct_nl="Het bedrijf is ingedeeld in Audit, Tax, Legal en Corporate Finance, naast kleinere gespecialiseerde praktijken. Het Corporate Finance-team behandelt aan- en verkoopprocessen, due diligence en waarderingen, en is de praktijk die het meest relevant is voor finance-studenten die dealwerk willen doen.",
       paths=[("corporate-finance","Corporate Finance"),("ma","M&A"),("valuation","Valuation")],
       join_en="Students usually join through an internship, a working-student role or the graduate intake, often in audit before moving towards Corporate Finance. It is a smaller-scale but workable route into deal advisory for students who prefer a less corporate environment than the Big Four.",
       join_nl="Studenten stromen meestal in via een stage, een werkstudentbaan of de startersinstroom, vaak in audit voordat ze doorstromen naar Corporate Finance. Het is een kleinschaligere maar werkbare route naar dealadvies voor studenten die een minder corporate omgeving prefereren dan de Big Four.",
       facts=[("Type","Type","Accountancy & advisory network","Accountancy- en adviesnetwerk"),("Head office (NL)","Hoofdkantoor (NL)","Utrecht","Utrecht"),
         ("Part of","Onderdeel van","Baker Tilly International","Baker Tilly International"),("Sector","Sector","Accountancy & advisory","Accountancy & advies")]),

    dict(slug="rsm-netherlands", name="RSM Netherlands", initials="RM", color="#009645", city="Rotterdam",
       types=["advisory","pe-dealmaking"], site="https://www.rsm.global/netherlands/en",
       tagline_en="A global accountancy and advisory network with a Dutch M&A Services practice covering corporate finance, due diligence and valuation.",
       tagline_nl="Een wereldwijd accountancy- en adviesnetwerk met een Nederlandse M&A Services-praktijk voor corporate finance, due diligence en waardering.",
       intro_en="RSM is a member firm of RSM International, one of the larger global networks of independent audit, tax and advisory firms. The Dutch firm has been active in Dutch accountancy for more than a century, growing through mergers of regional practices that eventually came together under the RSM brand. It offers Assurance, Tax and Consulting services, with M&A Services as part of the consulting practice, covering corporate finance advice, due diligence, debt advisory and valuations for companies, private shareholders, management teams and private equity investors.",
       intro_nl="RSM is een lid-organisatie van RSM International, een van de grotere wereldwijde netwerken van onafhankelijke audit-, tax- en adviesorganisaties. De Nederlandse organisatie is al meer dan een eeuw actief in de Nederlandse accountancy en is gegroeid via fusies van regionale kantoren die uiteindelijk samenkwamen onder het merk RSM. Het biedt Assurance, Tax en Consulting, met M&A Services als onderdeel van de consultingpraktijk: corporate finance-advies, due diligence, debt advisory en waarderingen voor bedrijven, particuliere aandeelhouders, managementteams en private-equity-investeerders.",
       nl_en="The Dutch head office is registered in Rotterdam, with offices spread across the country. RSM is a less prominent name than the Big Four for finance students, but its M&A Services practice offers a genuine route into deal-advisory work.",
       nl_nl="Het Nederlandse hoofdkantoor is geregistreerd in Rotterdam, met kantoren verspreid door het land. RSM is een minder prominente naam dan de Big Four voor finance-studenten, maar de M&A Services-praktijk biedt een echte route naar dealadvies.",
       struct_en="The firm is organised into Assurance, Tax and Consulting. M&A Services sits within Consulting and is built around four pillars: corporate finance, due diligence, debt advisory and valuation, which together make up the practice most finance students target.",
       struct_nl="Het bedrijf is ingedeeld in Assurance, Tax en Consulting. M&A Services valt onder Consulting en is opgebouwd rond vier pijlers: corporate finance, due diligence, debt advisory en waardering. Samen vormen die de praktijk waar de meeste finance-studenten op mikken.",
       paths=[("corporate-finance","Corporate Finance"),("ma","M&A"),("debt-advisory","Debt Advisory"),("valuation","Valuation")],
       join_en="Students typically start through an internship, a working-student role or the graduate programme, often in audit before moving into M&A Services. It provides a workable first step towards corporate finance, private equity or industry roles.",
       join_nl="Studenten starten meestal via een stage, een werkstudentbaan of het traineeprogramma, vaak in audit voordat ze doorstromen naar M&A Services. Het biedt een werkbare eerste stap richting corporate finance, private equity of het bedrijfsleven.",
       facts=[("Type","Type","Accountancy & advisory network","Accountancy- en adviesnetwerk"),("Head office (NL)","Hoofdkantoor (NL)","Rotterdam","Rotterdam"),
         ("Part of","Onderdeel van","RSM International","RSM International"),("Sector","Sector","Accountancy & advisory","Accountancy & advies")]),

    dict(slug="crowe-foederer", name="Crowe Foederer", initials="CW", color="#8b1e3f", city="Eindhoven",
       types=["advisory","pe-dealmaking"], site="https://www.foederer.nl",
       tagline_en="A Dutch accountancy and advisory firm, member of the Crowe Global network, with a corporate finance and M&A team.",
       tagline_nl="Een Nederlands accountancy- en adviesbedrijf, lid van het Crowe Global-netwerk, met een corporate finance- en M&A-team.",
       intro_en="Crowe Foederer is a Dutch accountancy and advisory firm and the Dutch member of Crowe Global, one of the larger global networks of independent accounting and advisory firms. Founded in Eindhoven in the early 1960s, it has grown into a firm active across several Dutch regions while remaining more compact than the Big Four. It offers audit, tax, HR and IT advisory services alongside a Corporate Finance practice covering M&A support, funding and debt advisory, valuations, due diligence and restructuring, mostly for entrepreneurial and family-owned businesses.",
       intro_nl="Crowe Foederer is een Nederlands accountancy- en adviesbedrijf en het Nederlandse lid van Crowe Global, een van de grotere wereldwijde netwerken van onafhankelijke accountancy- en adviesorganisaties. Het bedrijf is begin jaren zestig opgericht in Eindhoven en is uitgegroeid tot een organisatie die actief is in meerdere Nederlandse regio's, terwijl het compacter blijft dan de Big Four. Het biedt audit, tax, HR- en IT-advies naast een Corporate Finance-praktijk voor M&A-ondersteuning, financiering en debt advisory, waarderingen, due diligence en herstructurering, vooral voor ondernemende en familiebedrijven.",
       nl_en="The head office is in Eindhoven, where more than half of its staff are based, with further offices elsewhere in the south and centre of the Netherlands. Crowe Foederer is a smaller and more regional name than the Big Four, appealing to finance students who want closer contact with entrepreneurial mid-market clients.",
       nl_nl="Het hoofdkantoor staat in Eindhoven, waar meer dan de helft van het personeel werkt, met verdere kantoren elders in het zuiden en midden van Nederland. Crowe Foederer is een kleinere en meer regionale naam dan de Big Four, wat aantrekkelijk is voor finance-studenten die dichter bij ondernemende middensegment-klanten willen werken.",
       struct_en="The firm is organised into Audit, Tax, HR and Corporate Finance practices, working closely together on transactions. The Corporate Finance team, which covers M&A, debt advisory, valuation and transaction services, is where the deal work sits and is the practice most relevant to finance students.",
       struct_nl="Het bedrijf is ingedeeld in de praktijken Audit, Tax, HR en Corporate Finance, die nauw samenwerken bij transacties. Het Corporate Finance-team, dat M&A, debt advisory, waardering en transaction services omvat, is waar het dealwerk zit en de praktijk die het meest relevant is voor finance-studenten.",
       paths=[("corporate-finance","Corporate Finance"),("ma","M&A"),("debt-advisory","Debt Advisory"),("valuation","Valuation")],
       join_en="Students usually join through an internship or a working-student role, sometimes starting in audit before moving into Corporate Finance. Its smaller scale means more direct exposure to deal teams than at the Big Four, which appeals to students who want hands-on experience early.",
       join_nl="Studenten komen meestal binnen via een stage of een werkstudentbaan, soms startend in audit voordat ze doorstromen naar Corporate Finance. Door de kleinere schaal is er directer contact met dealteams dan bij de Big Four, wat aantrekkelijk is voor studenten die vroeg praktijkervaring willen opdoen.",
       facts=[("Type","Type","Accountancy & advisory network","Accountancy- en adviesnetwerk"),("Head office (NL)","Hoofdkantoor (NL)","Eindhoven","Eindhoven"),
         ("Part of","Onderdeel van","Crowe Global","Crowe Global"),("Sector","Sector","Accountancy & advisory","Accountancy & advies")]),

dict(slug="waterland", name="Waterland Private Equity Investments", initials="WL", color="#0f766e", city="Bussum",
   types=["pe-dealmaking"],
   site="https://www.waterlandpe.com",
   tagline_en="A Dutch-founded private equity investor known for its buy-and-build strategy across Europe, headquartered in Bussum.",
   tagline_nl="Een Nederlandse private-equity-investeerder die bekendstaat om zijn buy-and-buildstrategie in Europa, met het hoofdkantoor in Bussum.",
   intro_en="Waterland Private Equity Investments is a private equity firm founded in the Netherlands in 1999 and headquartered in Bussum. It invests in mid-sized, entrepreneur-led companies across Europe, typically using a buy-and-build approach: backing a platform company and then helping it grow through further acquisitions in a fragmented market. Waterland works across a range of sectors, including healthcare, business services, education and technology, and operates through offices in several European countries. Unlike many international private equity firms, Waterland's roots and much of its investment team are based in the Netherlands.",
   intro_nl="Waterland Private Equity Investments is een private-equityfirma die in 1999 in Nederland is opgericht en die haar hoofdkantoor in Bussum heeft. Het bedrijf investeert in middelgrote, door ondernemers geleide bedrijven in heel Europa, meestal via een buy-and-buildaanpak: een platformbedrijf ondersteunen en dat vervolgens laten groeien door verdere overnames in een gefragmenteerde markt. Waterland is actief in uiteenlopende sectoren, zoals zorg, zakelijke dienstverlening, onderwijs en technologie, en werkt vanuit kantoren in verschillende Europese landen. In tegenstelling tot veel internationale private-equityfirma's liggen de wortels van Waterland, en een groot deel van het investeringsteam, in Nederland.",
   nl_en="Waterland's head office is in Bussum, in the Gooi region near Amsterdam, and this is genuinely the firm's home base rather than a small satellite office. Much of the investment team works from here, alongside colleagues in other European offices. For finance students it is one of the more accessible ways into Dutch-based private equity, with real deal teams working on Dutch and international transactions from the Netherlands.",
   nl_nl="Het hoofdkantoor van Waterland staat in Bussum, in het Gooi bij Amsterdam, en dit is echt de thuisbasis van de firma en geen klein satellietkantoor. Een groot deel van het investeringsteam werkt hiervandaan, samen met collega's op andere Europese kantoren. Voor finance-studenten is dit een van de meer toegankelijke routes naar in Nederland gevestigde private equity, met echte dealteams die vanuit Nederland aan Nederlandse en internationale transacties werken.",
   struct_en="Waterland organises its investment activity around country and sector teams, supported by a dedicated performance improvement team that works with portfolio companies after acquisition. Deal teams source, evaluate and execute transactions, then support portfolio companies through further buy-and-build acquisitions. Graduates and interns typically join an investment team or the performance improvement team, working alongside associates and investment managers on live deals.",
   struct_nl="Waterland organiseert zijn investeringsactiviteiten rond landen- en sectorteams, ondersteund door een apart performance-improvementteam dat na overname met portfoliobedrijven samenwerkt. Dealteams sourcen, beoordelen en voeren transacties uit, en ondersteunen portfoliobedrijven daarna bij verdere buy-and-buildovernames. Starters en stagiairs komen doorgaans terecht in een investeringsteam of het performance-improvementteam, waar ze samen met associates en investment managers aan lopende deals werken.",
   paths=[("private-equity","Private Equity"),("ma","M&A")],
   join_en="Waterland offers internships and analyst positions for students, including roles that combine deal work with portfolio support. As with most private equity firms, competition for permanent investment roles is intense, and many associates join after a first working experience elsewhere, such as investment banking, consulting or a Big Four transaction advisory practice, though direct entry from a strong internship is possible.",
   join_nl="Waterland biedt stages en analistenposities voor studenten, waaronder rollen die dealwerk combineren met portfolio-ondersteuning. Zoals bij de meeste private-equityfirma's is de concurrentie voor vaste investeringsfuncties groot, en veel associates komen binnen na een eerste werkervaring elders, zoals investment banking, consulting of een transactieadviespraktijk van een Big Four-kantoor, al is directe instroom via een sterke stage ook mogelijk.",
   facts=[("Type","Type","Private equity investor","Private-equity-investeerder"), ("Head office","Hoofdkantoor","Bussum, Netherlands","Bussum, Nederland"),
     ("Founded","Opgericht","1999","1999"), ("Ownership","Eigendom","Independent private equity firm","Onafhankelijke private-equityfirma")]),

dict(slug="alpinvest", name="AlpInvest Partners", initials="AV", color="#6d28d9", city="Amsterdam",
   types=["pe-dealmaking"],
   site="https://www.carlylealpinvest.com",
   tagline_en="A private equity fund-of-funds and co-investment platform based in Amsterdam, part of Carlyle Group.",
   tagline_nl="Een private-equity fund-of-funds- en co-investeringsplatform met een basis in Amsterdam, onderdeel van Carlyle Group.",
   intro_en="AlpInvest Partners is a private equity investor founded in Amsterdam in 2000, originally to manage private equity allocations for two large Dutch pension funds. Rather than buying companies directly, AlpInvest invests in private equity funds, alongside those funds in individual deals, and in secondary transactions where existing fund stakes change hands. Since 2011 Carlyle Group has held a stake in AlpInvest, and it later became a wholly owned subsidiary, now operating as Carlyle's global private equity solutions platform. It remains one of the larger private equity investors of its kind, with Amsterdam as one of its main offices alongside locations such as New York and Hong Kong.",
   intro_nl="AlpInvest Partners is een private-equity-investeerder die in 2000 in Amsterdam is opgericht, oorspronkelijk om de private-equitybeleggingen van twee grote Nederlandse pensioenfondsen te beheren. In plaats van zelf bedrijven te kopen, belegt AlpInvest in private-equityfondsen, samen met die fondsen in individuele deals, en in secondary-transacties waarbij bestaande fondsbelangen van eigenaar wisselen. Sinds 2011 heeft Carlyle Group een belang in AlpInvest, en later werd het een volledige dochteronderneming die nu fungeert als het wereldwijde private-equityplatform van Carlyle. Amsterdam is nog altijd een van de belangrijkste kantoren, naast locaties zoals New York en Hongkong.",
   nl_en="AlpInvest's office is in Amsterdam, and this is a genuine, substantial base for the firm rather than a small regional outpost, alongside its offices in New York and Hong Kong. Much of the investment team that evaluates funds, co-investments and secondaries works from Amsterdam. For finance students this is one of the more established Dutch entry points into the fund investing side of private equity, distinct from firms that buy and run companies directly.",
   nl_nl="Het kantoor van AlpInvest staat in Amsterdam, en dit is een echte, substantiele vestiging van de firma en geen klein regionaal bijkantoor, naast de kantoren in New York en Hongkong. Een groot deel van het investeringsteam dat fondsen, co-investeringen en secondaries beoordeelt, werkt vanuit Amsterdam. Voor finance-studenten is dit een van de meer gevestigde Nederlandse ingangen tot de fondsbeleggingskant van private equity, anders dan bij firma's die zelf bedrijven kopen en runnen.",
   struct_en="AlpInvest is organised around three main investment strategies: fund investments (commitments to other private equity funds), co-investments (investing alongside those funds directly into companies), and secondaries (buying existing stakes in funds or portfolios). Each strategy has its own investment team, supported by shared research, portfolio monitoring and operations functions. Analysts and associates typically join one of these investment teams.",
   struct_nl="AlpInvest is opgebouwd rond drie hoofdstrategieen: fondsinvesteringen (toezeggingen aan andere private-equityfondsen), co-investeringen (samen met die fondsen rechtstreeks in bedrijven investeren) en secondaries (het overnemen van bestaande belangen in fondsen of portefeuilles). Elke strategie heeft een eigen investeringsteam, ondersteund door gedeelde research-, portfoliomonitoring- en operationsfuncties. Analisten en associates komen doorgaans in een van deze investeringsteams terecht.",
   paths=[("private-equity","Private Equity"),("ma","M&A")],
   join_en="AlpInvest runs a structured internship and analyst programme for students, including roles aimed specifically at bachelor and master students interested in private equity, responsible investment and analytics. This gives it a somewhat more accessible entry route for students than firms that buy companies directly, though competition for permanent roles remains high and many hires also come with prior experience in banking or consulting.",
   join_nl="AlpInvest heeft een gestructureerd stage- en analistenprogramma voor studenten, met rollen die specifiek gericht zijn op bachelor- en masterstudenten met interesse in private equity, verantwoord beleggen en analytics. Dat maakt de instap voor studenten wat toegankelijker dan bij firma's die zelf bedrijven overnemen, al blijft de concurrentie voor vaste functies groot en komen veel nieuwe medewerkers ook binnen met eerdere ervaring in banking of consulting.",
   facts=[("Type","Type","Private equity fund-of-funds and co-investment platform","Private-equity fund-of-funds- en co-investeringsplatform"), ("Head office","Hoofdkantoor","Amsterdam, Netherlands","Amsterdam, Nederland"),
     ("Founded","Opgericht","2000","2000"), ("Ownership","Eigendom","Subsidiary of Carlyle Group","Dochteronderneming van Carlyle Group")]),

dict(slug="cvc-capital-partners", name="CVC Capital Partners", initials="CC", color="#92400e", city="Amsterdam",
   types=["pe-dealmaking"],
   site="https://www.cvc.com",
   tagline_en="A global private equity and private markets manager with roots in Europe and an office in Amsterdam.",
   tagline_nl="Een wereldwijde private-equity- en private-marketsbeheerder met Europese wortels en een kantoor in Amsterdam.",
   intro_en="CVC Capital Partners is a global private markets investor that traces its origins to 1981, when it began as the European arm of Citicorp Venture Capital before becoming an independent firm in the early 1990s. Today CVC invests across private equity, credit, secondaries and infrastructure through a network of offices worldwide, and the firm itself listed its shares on Euronext Amsterdam in 2024. It backs established companies across a wide range of sectors and geographies, typically taking controlling or influential minority stakes and working with management teams over several years.",
   intro_nl="CVC Capital Partners is een wereldwijde private-marketsinvesteerder die zijn oorsprong heeft in 1981, toen het begon als de Europese tak van Citicorp Venture Capital voordat het begin jaren negentig een zelfstandige firma werd. Tegenwoordig belegt CVC in private equity, credit, secondaries en infrastructuur vanuit een wereldwijd netwerk van kantoren, en sinds 2024 staat CVC zelf genoteerd aan Euronext Amsterdam. Het bedrijf investeert in gevestigde ondernemingen in uiteenlopende sectoren en regio's, meestal met controlerende of invloedrijke minderheidsbelangen, en werkt daarbij meerdere jaren samen met managementteams.",
   nl_en="CVC has an office in Amsterdam, part of its global network of local offices, staffed by a deal team that works on investments in the Netherlands and the wider Benelux region. It is a genuinely global firm, and its Amsterdam presence should be understood as a focused local deal team rather than a large employer in the way a domestic Dutch firm would be. Students interested in CVC would typically be looking at a small, highly selective team working on international transactions.",
   nl_nl="CVC heeft een kantoor in Amsterdam, onderdeel van het wereldwijde netwerk aan lokale kantoren, bemenst door een dealteam dat werkt aan investeringen in Nederland en de bredere Benelux. Het is een echt mondiale firma, en de aanwezigheid in Amsterdam moet gezien worden als een gericht lokaal dealteam en niet als een grote werkgever zoals een binnenlandse Nederlandse firma dat zou zijn. Studenten die geinteresseerd zijn in CVC kijken doorgaans naar een klein, zeer selectief team dat aan internationale transacties werkt.",
   struct_en="CVC organises its investment activity by strategy (private equity, credit, secondaries, infrastructure) and by regional and sector deal teams within those strategies. Local offices such as Amsterdam house deal teams that source and execute transactions in their region, supported by central functions elsewhere in the network. Graduates who join tend to do so as analysts or associates within a specific deal team, most often after earlier experience in investment banking or consulting.",
   struct_nl="CVC organiseert zijn investeringsactiviteiten per strategie (private equity, credit, secondaries, infrastructuur) en per regionaal en sectoraal dealteam binnen die strategieen. Lokale kantoren zoals Amsterdam huisvesten dealteams die transacties in hun regio sourcen en uitvoeren, ondersteund door centrale functies elders in het netwerk. Starters die instromen doen dat doorgaans als analist of associate binnen een specifiek dealteam, meestal na eerdere ervaring in investment banking of consulting.",
   paths=[("private-equity","Private Equity"),("ma","M&A")],
   join_en="CVC occasionally offers internships in its European offices, but permanent analyst and associate roles are highly selective and, as at most large buyout firms, are typically filled by candidates who already have a year or more of experience in investment banking or consulting rather than students hired straight from university. A Dutch student aiming for CVC would generally build that experience first.",
   join_nl="CVC biedt af en toe stages aan op zijn Europese kantoren, maar vaste analisten- en associateposities zijn zeer selectief en worden, zoals bij de meeste grote buyoutfirma's, doorgaans ingevuld door kandidaten die al een jaar of meer ervaring hebben in investment banking of consulting, en niet door studenten die rechtstreeks van de universiteit komen. Een Nederlandse student die CVC ambieert, bouwt die ervaring meestal eerst elders op.",
   facts=[("Type","Type","Global private equity and private markets firm","Wereldwijde private-equity- en private-marketsfirma"), ("Head office","Hoofdkantoor","Luxembourg (global); Amsterdam office","Luxemburg (wereldwijd); kantoor in Amsterdam"),
     ("Founded","Opgericht","1981","1981"), ("Ownership","Eigendom","Publicly listed on Euronext Amsterdam","Beursgenoteerd aan Euronext Amsterdam")]),

dict(slug="eqt", name="EQT", initials="EQ", color="#7f1d1d", city="Amsterdam",
   types=["pe-dealmaking"],
   site="https://eqtgroup.com",
   tagline_en="A global investment organisation founded in Sweden, with an office in Amsterdam.",
   tagline_nl="Een wereldwijde investeringsorganisatie die is opgericht in Zweden, met een kantoor in Amsterdam.",
   intro_en="EQT is a global investment organisation founded in Stockholm in 1994, originally backed by Swedish investors including Investor AB. It has grown from its Nordic private equity roots into a broader alternative investment manager, active across private equity, infrastructure, real estate and other strategies, and it is listed on the stock exchange. EQT invests in companies it believes can grow sustainably over the medium to long term, working closely with management teams during its ownership period. The firm operates from offices across Europe, North America and Asia, including Amsterdam.",
   intro_nl="EQT is een wereldwijde investeringsorganisatie die in 1994 in Stockholm is opgericht, aanvankelijk gesteund door Zweedse investeerders waaronder Investor AB. Het bedrijf is uitgegroeid van zijn Scandinavische private-equitywortels tot een bredere alternatieve vermogensbeheerder, actief in private equity, infrastructuur, vastgoed en andere strategieen, en staat genoteerd aan de beurs. EQT investeert in bedrijven waarvan het denkt dat ze op de middellange tot lange termijn duurzaam kunnen groeien, en werkt daarbij nauw samen met managementteams gedurende de periode van eigenaarschap. De firma werkt vanuit kantoren in Europa, Noord-Amerika en Azie, waaronder Amsterdam.",
   nl_en="EQT has an office in Amsterdam that forms part of its European network of local deal teams. As with other large global private equity firms, the Amsterdam office should be seen as a focused, senior deal team working on Benelux and broader European transactions, not as a large-scale local employer. It offers a route into a genuinely international private equity career from a Dutch base, but for a small number of highly selective roles.",
   nl_nl="EQT heeft een kantoor in Amsterdam dat deel uitmaakt van zijn Europese netwerk van lokale dealteams. Zoals bij andere grote mondiale private-equityfirma's moet het kantoor in Amsterdam gezien worden als een gericht, senior dealteam dat aan Benelux- en bredere Europese transacties werkt, en niet als een grootschalige lokale werkgever. Het biedt een route naar een echt internationale private-equitycarriere vanuit een Nederlandse uitvalsbasis, maar voor een klein aantal zeer selectieve functies.",
   struct_en="EQT organises its work around investment strategies (such as private equity, infrastructure and real estate) and, within those, around sector and regional teams. Local offices like Amsterdam host deal teams that identify, execute and manage investments in their region, supported by central investment committees and shared functions. Finance graduates who join typically start as analysts or associates within one of these deal teams.",
   struct_nl="EQT organiseert zijn werk rond investeringsstrategieen (zoals private equity, infrastructuur en vastgoed) en, daarbinnen, rond sector- en regioteams. Lokale kantoren zoals Amsterdam huisvesten dealteams die investeringen in hun regio identificeren, uitvoeren en beheren, ondersteund door centrale investeringscommissies en gedeelde functies. Finance-starters die instromen, beginnen doorgaans als analist of associate binnen een van deze dealteams.",
   paths=[("private-equity","Private Equity"),("ma","M&A")],
   join_en="EQT recruits centrally for its analyst and associate programmes across its European offices, and these are competitive, often drawing candidates with prior experience in investment banking or consulting rather than offering large-scale direct entry from university. Internships are available in some offices and can be a way in for students, but permanent investment roles in Amsterdam are limited in number.",
   join_nl="EQT werft centraal voor zijn analisten- en associateprogramma's op zijn Europese kantoren, en deze zijn competitief: vaak gaat het om kandidaten met eerdere ervaring in investment banking of consulting, en minder om grootschalige directe instroom vanaf de universiteit. Op sommige kantoren zijn stages beschikbaar en die kunnen voor studenten een ingang zijn, maar het aantal vaste investeringsfuncties in Amsterdam is beperkt.",
   facts=[("Type","Type","Global private equity and alternative investment firm","Wereldwijde private-equity- en alternatieve investeringsfirma"), ("Head office","Hoofdkantoor","Stockholm (global); Amsterdam office","Stockholm (wereldwijd); kantoor in Amsterdam"),
     ("Founded","Opgericht","1994","1994"), ("Ownership","Eigendom","Publicly listed","Beursgenoteerd")]),

dict(slug="kkr", name="KKR", initials="KR", color="#155e75", city="Amsterdam",
   types=["pe-dealmaking"],
   site="https://www.kkr.com",
   tagline_en="One of the original global buyout firms, founded in New York, with an office in Amsterdam.",
   tagline_nl="Een van de oorspronkelijke wereldwijde buyoutfirma's, opgericht in New York, met een kantoor in Amsterdam.",
   intro_en="KKR is a global investment firm founded in New York in 1976 by Jerome Kohlberg and cousins Henry Kravis and George Roberts, who had previously worked together in finance. It is widely regarded as one of the pioneers of the leveraged buyout, and has since grown into a diversified alternative asset manager active in private equity, credit, infrastructure and real assets, listed on the stock exchange. KKR invests in companies across a wide range of industries and regions, typically taking significant or controlling stakes and working with management over a multi-year holding period. It operates through a global network of offices, including one in Amsterdam.",
   intro_nl="KKR is een wereldwijde investeringsfirma die in 1976 in New York is opgericht door Jerome Kohlberg en neven Henry Kravis en George Roberts, die eerder samen in de financiele sector hadden gewerkt. De firma geldt algemeen als een van de pioniers van de leveraged buyout en is uitgegroeid tot een gediversifieerde alternatieve vermogensbeheerder, actief in private equity, credit, infrastructuur en real assets, genoteerd aan de beurs. KKR investeert in bedrijven in uiteenlopende sectoren en regio's, meestal met aanzienlijke of controlerende belangen, en werkt daarbij meerdere jaren samen met het management. De firma werkt vanuit een wereldwijd netwerk van kantoren, waaronder een kantoor in Amsterdam.",
   nl_en="KKR's Amsterdam office is part of its European network and houses a local deal team covering the Netherlands and surrounding markets. As with the other large global buyout firms, this should be understood as a compact, senior team rather than a major local employer. It gives Dutch-based candidates access to a well-known global private equity brand, but through a small number of highly competitive roles.",
   nl_nl="Het kantoor van KKR in Amsterdam maakt deel uit van het Europese netwerk en huisvest een lokaal dealteam dat Nederland en omliggende markten bedient. Zoals bij de andere grote mondiale buyoutfirma's moet dit gezien worden als een compact, senior team en niet als een grote lokale werkgever. Het geeft in Nederland gevestigde kandidaten toegang tot een bekend mondiaal private-equitymerk, maar via een klein aantal zeer competitieve functies.",
   struct_en="KKR is organised around asset classes and strategies, such as private equity, credit, infrastructure and real estate, with sector and regional teams operating within each. Local offices like Amsterdam host deal professionals who source and execute transactions in their market, working alongside colleagues in larger hubs such as London. Analysts and associates typically sit within one of these deal teams, reporting up through regional and global investment leadership.",
   struct_nl="KKR is georganiseerd rond beleggingscategorieen en strategieen, zoals private equity, credit, infrastructuur en vastgoed, met sector- en regioteams binnen elke strategie. Lokale kantoren zoals Amsterdam huisvesten dealprofessionals die transacties in hun markt sourcen en uitvoeren, in samenwerking met collega's op grotere hubs zoals Londen. Analisten en associates werken doorgaans binnen een van deze dealteams, met verantwoording aan regionale en mondiale investeringsleiding.",
   paths=[("private-equity","Private Equity"),("ma","M&A")],
   join_en="KKR runs student and graduate programmes in some of its larger offices, but roles based in Amsterdam are limited and highly competitive. As at other mega-funds, most analysts and associates arrive with prior experience from investment banking or consulting rather than joining straight after a bachelor's or master's degree, though internships offer an entry point for strong candidates.",
   join_nl="KKR heeft student- en graduateprogramma's op enkele van zijn grotere kantoren, maar functies in Amsterdam zijn beperkt in aantal en zeer competitief. Zoals bij andere grote buyoutfirma's komen de meeste analisten en associates binnen met eerdere ervaring uit investment banking of consulting, en niet direct na een bachelor- of masteropleiding, al bieden stages een ingang voor sterke kandidaten.",
   facts=[("Type","Type","Global private equity and alternative investment firm","Wereldwijde private-equity- en alternatieve investeringsfirma"), ("Head office","Hoofdkantoor","New York (global); Amsterdam office","New York (wereldwijd); kantoor in Amsterdam"),
     ("Founded","Opgericht","1976","1976"), ("Ownership","Eigendom","Publicly listed","Beursgenoteerd")]),

dict(slug="marktlink", name="Marktlink", initials="MK", color="#ea580c", city="Deventer",
   types=["pe-dealmaking"],
   site="https://www.marktlink.com",
   tagline_en="A Dutch-founded M&A advisory firm focused on mid-market deals for entrepreneurs.",
   tagline_nl="Een Nederlandse M&A-adviesfirma gericht op mid-marketdeals voor ondernemers.",
   intro_en="Marktlink is a mergers and acquisitions advisory firm founded in the Netherlands in 1996, originally focused on advising entrepreneurs and family-owned businesses on the sale, purchase or financing of mid-sized companies. Rather than managing its own investment funds in the way a private equity firm does, Marktlink acts as an advisor, guiding business owners through the transaction process from valuation to closing. Over time the firm has expanded from its Dutch base into a network of offices across several European countries, while continuing to focus on the mid-market segment. It also has a capital arm that invests directly in businesses alongside its advisory work.",
   intro_nl="Marktlink is een fusie- en overnameadviesfirma die in 1996 in Nederland is opgericht, oorspronkelijk gericht op het adviseren van ondernemers en familiebedrijven bij de verkoop, aankoop of financiering van middelgrote bedrijven. In tegenstelling tot een private-equityfirma beheert Marktlink geen eigen investeringsfondsen, maar treedt het op als adviseur en begeleidt het ondernemers door het transactieproces, van waardering tot closing. In de loop der tijd is de firma vanuit haar Nederlandse basis uitgegroeid tot een netwerk van kantoren in verschillende Europese landen, met behoud van de focus op het mid-marketsegment. Daarnaast heeft de firma een investeringstak die naast het advieswerk ook rechtstreeks in bedrijven investeert.",
   nl_en="Marktlink is headquartered in the Netherlands and operates from multiple Dutch offices, including Amsterdam, alongside its head office location. This is a genuinely Dutch firm with a substantial local headcount, not a small satellite of a foreign parent, and finance students would find real deal teams working on Dutch mid-market transactions day to day.",
   nl_nl="Marktlink heeft zijn hoofdkantoor in Nederland en werkt vanuit meerdere Nederlandse kantoren, waaronder Amsterdam, naast de locatie van het hoofdkantoor. Dit is een echt Nederlandse firma met een substantiele lokale personeelsbezetting, geen klein satellietkantoor van een buitenlandse moeder, en finance-studenten treffen er dealteams die dagelijks aan Nederlandse mid-markettransacties werken.",
   struct_en="Marktlink organises its advisory work in deal teams that support clients through the full transaction process, alongside a separate capital arm for direct investments. Junior staff typically start as analysts or consultants within a deal team, building financial models, preparing valuations and supporting negotiations, before progressing to more senior advisory roles or moving into a permanent deal team.",
   struct_nl="Marktlink organiseert zijn adviespraktijk in dealteams die klanten begeleiden door het volledige transactieproces, naast een aparte investeringstak voor directe investeringen. Junior medewerkers beginnen doorgaans als analist of consultant binnen een dealteam, waar ze financiele modellen bouwen, waarderingen voorbereiden en onderhandelingen ondersteunen, voordat ze doorgroeien naar meer senior adviesfuncties of een vaste plek in een dealteam.",
   paths=[("ma","M&A"),("corporate-finance","Corporate Finance")],
   join_en="Marktlink regularly hires interns and starting analysts directly from bachelor's and master's programmes, with a defined path from internship to junior consultant and onward within a deal team. This makes it one of the more direct routes into M&A advisory for Dutch finance students, compared with firms that mainly recruit people with prior banking or consulting experience.",
   join_nl="Marktlink werft regelmatig stagiairs en startende analisten rechtstreeks vanuit bachelor- en masteropleidingen, met een duidelijk groeipad van stage naar junior consultant en verder binnen een dealteam. Dat maakt de firma een van de meer directe routes naar M&A-advies voor Nederlandse finance-studenten, vergeleken met firma's die vooral mensen met eerdere bankieren- of consultingervaring aannemen.",
   facts=[("Type","Type","M&A advisory firm","M&A-adviesfirma"), ("Head office","Hoofdkantoor","Deventer, Netherlands","Deventer, Nederland"),
     ("Founded","Opgericht","1996","1996"), ("Ownership","Eigendom","Independent advisory firm","Onafhankelijke adviesfirma")]),
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
.bedrijf-faq { display: flex; flex-direction: column; gap: 10px; max-width: 760px; }
.bedrijf-faq-item { background: var(--white); border: 1px solid var(--gray-200); border-radius: 12px; padding: 16px 20px; }
.bedrijf-faq-item summary { cursor: pointer; font-weight: 700; color: var(--navy-950); list-style: none; }
.bedrijf-faq-item summary::-webkit-details-marker { display: none; }
.bedrijf-faq-item summary::after { content: "+"; float: right; color: var(--blue-600); font-weight: 700; }
.bedrijf-faq-item[open] summary::after { content: "\\2212"; }
.bedrijf-faq-item p { margin-top: 12px; color: var(--gray-700); line-height: 1.6; }
.bedrijf-badge-logo { background: #fff; padding: 10px; box-shadow: 0 6px 20px rgba(10,22,40,0.16); }
.bedrijf-card-badge.bedrijf-badge-logo { padding: 7px; box-shadow: none; border: 1px solid var(--gray-200); }
.bedrijf-badge-logo img { width: 100%; height: 100%; object-fit: contain; display: block; }
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
 "equity-research":"Equity Research","valuation":"Valuation","corporate-development":"Corporate Development",
 "debt-advisory":"Debt Advisory","real-estate-finance":"Real Estate Finance",
 "trading":"Trading","wealth-management":"Wealth Management & Private Banking","risk-management":"Risk Management"}

def faq_items(c):
    head_office = next((ve for le,ln,ve,vn in c["facts"] if le=="Head office"), c["city"])
    head_office_nl = next((vn for le,ln,ve,vn in c["facts"] if le=="Head office"), c["city"])
    path_names = [NAMES[s] for s,_ in c["paths"]]
    def joinlist(items, sep_last):
        if len(items)==1: return items[0]
        return ", ".join(items[:-1]) + f" {sep_last} " + items[-1]
    paths_en = joinlist(path_names, "and") if path_names else "finance"
    paths_nl = joinlist(path_names, "en") if path_names else "finance"
    return [
      (f"What does {c['name']} do?", f"Wat doet {c['name']}?",
       c["tagline_en"], c["tagline_nl"]),
      (f"How do I get an internship or graduate role at {c['name']}?", f"Hoe kom ik aan een stage of traineeship bij {c['name']}?",
       c["join_en"], c["join_nl"]),
      (f"Which finance career paths are relevant at {c['name']}?", f"Welke finance-paden zijn relevant bij {c['name']}?",
       f"At {c['name']}, the most relevant finance career paths are {paths_en}.", f"Bij {c['name']} zijn de meest relevante finance-paden {paths_nl}."),
      (f"Where is {c['name']} based in the Netherlands?", f"Waar zit {c['name']} in Nederland?",
       f"Head office: {head_office}.", f"Hoofdkantoor: {head_office_nl}."),
    ]

def company_page(c):
    url = f"{SITE}/bedrijven/{c['slug']}/"
    firms_js = '"'+c["name"]+'"'
    title = f"Werken bij {c['name']}: stage, traineeship en vacatures | CorporateCareer"
    desc = f"{c['tagline_nl']} Bekijk stages, traineeships en vacatures bij {c['name']}."
    org = {"@context":"https://schema.org","@type":"Organization","name":c["name"],"url":c["site"],
      "address":{"@type":"PostalAddress","addressLocality":c["city"],"addressCountry":"NL"},"sameAs":[c["site"]]}
    crumb = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
      {"@type":"ListItem","position":1,"name":"Home","item":SITE+"/"},
      {"@type":"ListItem","position":2,"name":"Finance","item":SITE+"/finance.html"},
      {"@type":"ListItem","position":3,"name":"Bedrijven","item":SITE+"/finance/bedrijven/"},
      {"@type":"ListItem","position":4,"name":c["name"],"item":url}]}
    faqs = faq_items(c)
    faqpage = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
      {"@type":"Question","name":q_nl,"acceptedAnswer":{"@type":"Answer","text":a_nl}} for q_en,q_nl,a_en,a_nl in faqs]}
    ld = ('  <script type="application/ld+json">\n'+json.dumps(org,ensure_ascii=False,indent=2)+'\n  </script>\n'
          '  <script type="application/ld+json">\n'+json.dumps(crumb,ensure_ascii=False,indent=2)+'\n  </script>\n'
          '  <script type="application/ld+json">\n'+json.dumps(faqpage,ensure_ascii=False,indent=2)+'\n  </script>')
    tags = "".join(f'<span class="bedrijf-tag">{esc(FLABEL[t][1])}</span>' for t in c["types"])
    facts = "".join(f'<div class="bedrijf-fact"><dt>{bi(le,ln)}</dt><dd>{bi(ve,vn)}</dd></div>' for le,ln,ve,vn in c["facts"])
    paths = "".join(f'<a class="pe-rel-card fade-up" href="/finance/{s}/"><span>{esc(NAMES[s])}</span>'
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="15" height="15" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>' for s,_ in c["paths"])
    faq_html = "".join(f'<details class="bedrijf-faq-item"><summary>{bi(q_en,q_nl)}</summary><p>{bi(a_en,a_nl)}</p></details>' for q_en,q_nl,a_en,a_nl in faqs)
    logo = logo_url(c["slug"])
    badge = (f'<span class="bedrijf-badge bedrijf-badge-logo"><img src="{logo}" alt="{esc(c["name"])} logo" width="60" height="60" loading="eager"></span>'
      if logo else f'<span class="bedrijf-badge" style="background:{c["color"]}">{esc(c["initials"])}</span>')
    return head(title, desc, url, ld) + f"""
{bc([("Home","/index.html"),("Finance","/finance.html"),("Bedrijven","/finance/bedrijven/"),(c["name"],None)])}

  <section class="page-hero" style="background:linear-gradient(135deg,#142a45,#234b7e)"><div class="container inner">
    {badge}
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

  <section class="page-section gray"><div class="container">
    <p class="section-label">{bi('FAQ','Veelgestelde vragen')}</p>
    <h2 class="section-title">{bi('Frequently asked questions about '+c['name'],'Veelgestelde vragen over '+c['name'])}</h2>
    <div class="bedrijf-faq">{faq_html}</div>
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
        logo = logo_url(c["slug"])
        card_badge = (f'<span class="bedrijf-card-badge bedrijf-badge-logo"><img src="{logo}" alt="{esc(c["name"])} logo" width="46" height="46" loading="lazy"></span>'
          if logo else f'<span class="bedrijf-card-badge" style="background:{c["color"]}">{esc(c["initials"])}</span>')
        cards += (f'<a class="bedrijf-card fade-up" href="/bedrijven/{c["slug"]}/" data-types="{tp}">'
          f'{card_badge}'
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
