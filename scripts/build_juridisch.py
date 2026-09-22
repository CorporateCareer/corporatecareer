# -*- coding: utf-8 -*-
"""Genereert de privacyverklaring, de gebruiksvoorwaarden en de cookieverklaring.

Die drie stonden wel in de footer van elke pagina, maar bestonden niet: de
links wezen naar "#". Dat waren 7.020 doodlopende links, en belangrijker: de
site laadt Google Analytics op bijna tweeduizend pagina's, dus er valt wel
degelijk iets uit te leggen.

De pagina's dragen beide talen in dezelfde bron, met data-l-blokken. Zo splitst
build_en.py ze vanzelf in een Nederlandse pagina en een Engelse onder /en/,
en regelt datzelfde script de hreflang en de sitemap. Handmatig twee bestanden
bijhouden zou betekenen dat een correctie in de ene taal de andere vergeet.

De chrome (navigatiebalk, footer, lettertypen) komt uit over-ons.html, zodat
deze pagina's niet uit de pas gaan lopen zodra daar iets aan verandert.

Gebruik:
    python scripts/build_juridisch.py
    python scripts/build_en.py        daarna, voor /en/ en de sitemap
"""
import os, re, sys
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRON = os.path.join(BASE, "over-ons.html")
SITE = "https://corporatecareer.nl"

BIJGEWERKT_NL = "22 september 2026"
BIJGEWERKT_EN = "22 September 2026"

STIJL = """  <style>
    .jur-hero{padding:120px 0 40px;background:linear-gradient(180deg,#f7f9fb 0%,#fff 100%)}
    .jur-hero h1{font-size:clamp(2rem,4vw,2.75rem);font-weight:800;color:var(--navy-900);line-height:1.15;margin:0 0 14px}
    .jur-hero p{color:var(--gray-700);font-size:1.05rem;line-height:1.7;max-width:720px;margin:0}
    .jur-meta{display:inline-block;margin-top:22px;padding:6px 12px;border-radius:6px;background:#eef3f7;color:#41556e;font-size:.85rem;font-weight:600}
    .jur-body{padding:44px 0 88px}
    .jur-prose{max-width:768px}
    .jur-prose h2{font-size:1.3rem;font-weight:800;color:var(--navy-900);line-height:1.3;margin:38px 0 12px}
    .jur-prose h2:first-child{margin-top:0}
    .jur-prose p{color:var(--gray-700);line-height:1.8;font-size:1rem;margin:0 0 14px}
    .jur-prose ul{margin:0 0 14px;padding-left:22px}
    .jur-prose li{color:var(--gray-700);line-height:1.8;margin-bottom:8px}
    .jur-prose a{color:#0e7c5a}
    .jur-table{width:100%;border-collapse:collapse;margin:8px 0 18px;font-size:.93rem}
    .jur-table th,.jur-table td{text-align:left;padding:10px 12px;border-bottom:1px solid #e3e8ee;vertical-align:top;color:var(--gray-700);line-height:1.6}
    .jur-table th{background:#f4f6f8;color:var(--navy-900);font-weight:700;white-space:nowrap}
    .jur-table code{background:#eef1f4;padding:1px 5px;border-radius:3px;font-size:.88em}
    @media (max-width:640px){.jur-table,.jur-table tbody,.jur-table tr,.jur-table td{display:block;width:100%}.jur-table thead{display:none}.jur-table tr{border-bottom:1px solid #e3e8ee;padding:8px 0}.jur-table td{border:0;padding:3px 0}}
  </style>
"""


def t(nl, en):
    """Een stuk tekst in beide talen, zodat build_en.py kan splitsen."""
    return f'<span data-l="nl">{nl}</span><span data-l="en" hidden>{en}</span>'


# ── de inhoud ────────────────────────────────────────────────────────────────

PRIVACY = [
    ("Wie verwerkt jouw gegevens", "Who processes your data", [
        ("p", "CorporateCareer, gevestigd in Amsterdam, is verantwoordelijk voor de verwerking van persoonsgegevens op corporatecareer.nl. Heb je een vraag over deze verklaring of over jouw gegevens, mail dan naar <a href=\"mailto:partner@corporatecareer.nl\">partner@corporatecareer.nl</a>.",
              "CorporateCareer, based in Amsterdam, is the controller for the processing of personal data on corporatecareer.nl. If you have a question about this statement or about your data, email <a href=\"mailto:partner@corporatecareer.nl\">partner@corporatecareer.nl</a>."),
    ]),
    ("Welke gegevens wij verwerken", "What data we process", [
        ("p", "Wij verwerken twee soorten gegevens, en niet meer dan dat.",
              "We process two kinds of data, and nothing beyond that."),
        ("p", "<strong>Bezoekgegevens.</strong> Wij gebruiken Google Analytics om te zien welke pagina's worden bekeken en hoe bezoekers de site vinden. Daarbij worden onder meer je IP-adres, de bezochte pagina's, het tijdstip, je browser en apparaat, en de verwijzende website vastgelegd. Wij gebruiken die gegevens om te bepalen welke gidsen wij uitbreiden en welke informatie blijkbaar ontbreekt.",
              "<strong>Visit data.</strong> We use Google Analytics to see which pages are viewed and how visitors find the site. This records your IP address, the pages visited, the time, your browser and device, and the referring website, among other things. We use this to decide which guides to expand and what information is evidently missing."),
        ("p", "<strong>Gegevens die je zelf achterlaat.</strong> Stuur je ons een e-mail, of vul je het partnerformulier in, dan verwerken wij het adres en de inhoud van dat bericht. Dat gebeurt alleen omdat je ons zelf benadert.",
              "<strong>Data you provide yourself.</strong> If you email us, or fill in the partner form, we process that address and the content of your message. This only happens because you contacted us."),
    ]),
    ("Wat wij niet doen", "What we do not do", [
        ("ul", [
            ("Wij verkopen of verhuren geen gegevens aan derden.", "We do not sell or rent data to third parties."),
            ("Wij plaatsen geen advertentiecookies en tonen geen advertenties.", "We do not place advertising cookies and we show no advertisements."),
            ("Wij maken geen profielen om je gericht te benaderen.", "We do not build profiles to target you."),
            ("Wij verwerken geen sollicitaties. Solliciteren doe je rechtstreeks bij de werkgever, via zijn eigen wervingssysteem. Jouw cv en motivatie komen niet langs ons.", "We do not process applications. You apply directly with the employer, through their own recruitment system. Your CV and cover letter never pass through us."),
            ("Wij vragen niet om een account. Je kunt de hele site gebruiken zonder je te registreren.", "We do not ask you to create an account. You can use the entire site without registering."),
        ]),
    ]),
    ("Op welke grondslag", "On what legal basis", [
        ("p", "Voor de bezoekgegevens beroepen wij ons op ons gerechtvaardigd belang: wij willen weten welke informatie gevonden wordt en welke niet, zodat wij de site kunnen verbeteren. Voor berichten die je ons stuurt is de grondslag dat je ons zelf benadert en wij jouw vraag willen beantwoorden.",
              "For visit data we rely on our legitimate interest: we want to know which information is found and which is not, so that we can improve the site. For messages you send us, the basis is that you approached us and we want to answer your question."),
    ]),
    ("Hoe lang wij ze bewaren", "How long we keep them", [
        ("p", "Bezoekgegevens in Google Analytics worden na veertien maanden verwijderd. E-mail bewaren wij zolang dat nodig is om je vraag af te handelen, en daarna voor zover wij die correspondentie moeten kunnen terugvinden. Wil je dat een bericht eerder wordt verwijderd, dan doen wij dat op verzoek.",
              "Visit data in Google Analytics is deleted after fourteen months. We keep email for as long as we need it to handle your question, and after that only insofar as we need to be able to retrieve that correspondence. If you want a message deleted sooner, we will do so on request."),
    ]),
    ("Wie jouw gegevens nog meer ziet", "Who else sees your data", [
        ("table",
         [("Partij", "Waarvoor", "Waar"), ("Party", "What for", "Where")],
         [
             (("Google Ireland Limited", "Google Ireland Limited"),
              ("Google Analytics, het meten van bezoek", "Google Analytics, measuring site visits"),
              ("Ierland, met mogelijke doorgifte naar de Verenigde Staten", "Ireland, with possible transfer to the United States")),
             (("GitHub, Inc.", "GitHub, Inc."),
              ("Hosting van de site. GitHub legt bij het opvragen van een pagina technische gegevens vast, waaronder je IP-adres.", "Hosting of the site. When a page is requested GitHub records technical data, including your IP address."),
              ("Verenigde Staten", "United States")),
             (("Zoho Corporation", "Zoho Corporation"),
              ("Onze e-mail. Alleen van toepassing als je ons mailt.", "Our email. Only applicable if you email us."),
              ("Europese Unie", "European Union")),
         ]),
        ("p", "Waar gegevens buiten de Europese Economische Ruimte terechtkomen, gebeurt dat op basis van de standaardcontractbepalingen van de Europese Commissie of een geldig adequaatheidsbesluit.",
              "Where data ends up outside the European Economic Area, this happens on the basis of the European Commission's standard contractual clauses or a valid adequacy decision."),
    ]),
    ("Jouw rechten", "Your rights", [
        ("p", "Je hebt het recht om te weten welke gegevens wij van je hebben, om ze te laten corrigeren of verwijderen, om de verwerking te laten beperken, en om bezwaar te maken tegen verwerking op grond van gerechtvaardigd belang. Een verzoek stuur je naar <a href=\"mailto:partner@corporatecareer.nl\">partner@corporatecareer.nl</a>. Wij reageren binnen een maand.",
              "You have the right to know what data we hold about you, to have it corrected or deleted, to have processing restricted, and to object to processing based on legitimate interest. Send a request to <a href=\"mailto:partner@corporatecareer.nl\">partner@corporatecareer.nl</a>. We respond within one month."),
        ("p", "Ben je het oneens met hoe wij met je gegevens omgaan, dan kun je een klacht indienen bij de Autoriteit Persoonsgegevens. Wij horen het liever eerst zelf, maar dat recht staat los van ons.",
              "If you disagree with how we handle your data, you can lodge a complaint with the Dutch Data Protection Authority. We would rather hear it from you first, but that right stands regardless."),
    ]),
    ("Links naar andere websites", "Links to other websites", [
        ("p", "Elke vacature op deze site verwijst door naar het wervingssysteem van de werkgever zelf. Zodra je daarop klikt verlaat je corporatecareer.nl en geldt het privacybeleid van die partij. Wij hebben geen invloed op wat daar gebeurt en kunnen er ook niet voor instaan.",
              "Every vacancy on this site links through to the employer's own recruitment system. The moment you click it you leave corporatecareer.nl and that party's privacy policy applies. We have no influence over what happens there and cannot vouch for it."),
    ]),
    ("Beveiliging", "Security", [
        ("p", "De site is uitsluitend over een beveiligde verbinding bereikbaar. Wij bewaren geen wachtwoorden, geen betaalgegevens en geen sollicitatiedocumenten, simpelweg omdat wij die niet verzamelen. Dat is de meest effectieve beveiliging die er is.",
              "The site is reachable only over a secure connection. We store no passwords, no payment details and no application documents, simply because we do not collect them. That is the most effective security there is."),
    ]),
    ("Wijzigingen", "Changes", [
        ("p", "Verandert er iets aan wat wij verwerken, dan passen wij deze verklaring aan en veranderen wij de datum hierboven. Er is geen eerdere versie: dit is de eerste.",
              "If what we process changes, we will amend this statement and change the date above. There is no earlier version: this is the first."),
    ]),
]

COOKIES = [
    ("Wat een cookie is", "What a cookie is", [
        ("p", "Een cookie is een klein bestand dat een website op je apparaat achterlaat, zodat hij je bij een volgend bezoek herkent. Sommige zijn nodig om de site te laten werken, andere dienen om te meten hoe de site gebruikt wordt.",
              "A cookie is a small file that a website leaves on your device so that it recognises you on a subsequent visit. Some are needed to make the site work, others serve to measure how the site is used."),
    ]),
    ("Wat wij plaatsen", "What we place", [
        ("table",
         [("Naam", "Door wie", "Waarvoor", "Bewaartermijn"), ("Name", "Set by", "What for", "Retention")],
         [
             (("<code>cc-lang</code>", "<code>cc-lang</code>"),
              ("CorporateCareer", "CorporateCareer"),
              ("Onthoudt of je de site in het Nederlands of het Engels leest, zodat je die keuze niet elke keer opnieuw hoeft te maken. Blijft op je eigen apparaat en wordt nergens naartoe gestuurd.", "Remembers whether you read the site in Dutch or English, so you do not have to make that choice again. Stays on your own device and is never sent anywhere."),
              ("Tot je hem wist", "Until you clear it")),
             (("<code>_ga</code>", "<code>_ga</code>"),
              ("Google Analytics", "Google Analytics"),
              ("Onderscheidt bezoekers van elkaar, zodat wij weten hoeveel verschillende mensen een pagina bekijken.", "Distinguishes visitors from one another, so that we know how many different people view a page."),
              ("2 jaar", "2 years")),
             (("<code>_ga_G-TXBG97YW6Y</code>", "<code>_ga_G-TXBG97YW6Y</code>"),
              ("Google Analytics", "Google Analytics"),
              ("Houdt de staat van een bezoek bij, zodat een reeks pagina's als één bezoek telt en niet als vijf losse.", "Keeps the state of a visit, so that a series of pages counts as one visit rather than five separate ones."),
              ("2 jaar", "2 years")),
         ]),
        ("p", "Dat is de volledige lijst. Er staat geen advertentienetwerk op deze site, geen volgpixel van een sociaal netwerk en geen chatwidget.",
              "That is the complete list. There is no advertising network on this site, no social network tracking pixel and no chat widget."),
    ]),
    ("Weigeren of verwijderen", "Refusing or deleting", [
        ("p", "Je kunt cookies op drie manieren tegenhouden, en dat werkt allemaal zonder ons.",
              "You can stop cookies in three ways, and all of them work without us."),
        ("ul", [
            ("In je browser kun je cookies van derden blokkeren of alle cookies van deze site verwijderen. Dat staat meestal onder Instellingen, Privacy.", "In your browser you can block third-party cookies or delete all cookies from this site. That is usually found under Settings, Privacy."),
            ("Google biedt een browserextensie waarmee Google Analytics je op geen enkele site meer meet.", "Google offers a browser add-on that stops Google Analytics measuring you on any site."),
            ("Vrijwel elke browser heeft een privémodus, waarin cookies na het sluiten van het venster verdwijnen.", "Virtually every browser has a private mode, in which cookies disappear once you close the window."),
        ]),
        ("p", "Blokkeer je cookies, dan blijft de hele site gewoon werken. Het enige merkbare verschil is dat je taalkeuze niet wordt onthouden. Er zit geen enkel onderdeel achter een cookie.",
              "If you block cookies, the entire site keeps working. The only noticeable difference is that your language choice is not remembered. No part of the site sits behind a cookie."),
    ]),
    ("Meer weten", "More information", [
        # Bewust een relatief pad in beide talen: de Engelse pagina staat zelf
        # onder /en/, dus "privacy.html" wijst daar naar /en/privacy.html. Een
        # absoluut "/en/privacy.html" zou door de vertaalstap nog eens van /en
        # worden voorzien en op /en/en/ uitkomen.
        ("p", "In de <a href=\"privacy.html\">privacyverklaring</a> staat wat wij met de gemeten gegevens doen, hoe lang wij ze bewaren en welke rechten je hebt.",
              "The <a href=\"privacy.html\">privacy statement</a> explains what we do with the measured data, how long we keep it and what rights you have."),
    ]),
]

VOORWAARDEN = [
    ("Waar deze voorwaarden over gaan", "What these terms cover", [
        ("p", "Deze voorwaarden gelden voor het gebruik van corporatecareer.nl. Door de site te gebruiken ga je ermee akkoord. Ben je het er niet mee eens, dan is de oplossing eenvoudig: gebruik de site niet.",
              "These terms apply to the use of corporatecareer.nl. By using the site you agree to them. If you do not agree, the solution is simple: do not use the site."),
    ]),
    ("Wat CorporateCareer is, en wat niet", "What CorporateCareer is, and what it is not", [
        ("p", "CorporateCareer is een informatieplatform over loopbanen in finance, consulting en de advocatuur in Nederland. Wij brengen in kaart welke functies er zijn, welke kantoren erin actief zijn en welke vacatures er openstaan.",
              "CorporateCareer is an information platform about careers in finance, consulting and law in the Netherlands. We map out which roles exist, which firms are active in them and which vacancies are open."),
        ("p", "Wij zijn geen werving- en selectiebureau en geen uitzendbureau. Wij bemiddelen niet, wij dragen geen kandidaten voor en wij ontvangen geen vergoeding voor een plaatsing. Wij zijn ook geen partij bij welke sollicitatie dan ook: die loopt rechtstreeks tussen jou en de werkgever.",
              "We are not a recruitment or staffing agency. We do not mediate, we do not put forward candidates and we receive no fee for a placement. Nor are we a party to any application: that runs directly between you and the employer."),
        ("p", "Wat op de site staat is algemene informatie. Het is geen juridisch, fiscaal of financieel advies, en geen loopbaanadvies dat op jouw situatie is afgestemd.",
              "What is on the site is general information. It is not legal, tax or financial advice, nor career advice tailored to your situation."),
    ]),
    ("Over de vacatures", "About the vacancies", [
        ("p", "De vacatures worden wekelijks automatisch opgehaald bij de wervingssystemen van de werkgevers zelf. Wij nemen ze niet over van andere vacaturesites. De tekst, de voorwaarden en de procedure zijn van de werkgever; wij geven ze door.",
              "Vacancies are collected automatically each week from the employers' own recruitment systems. We do not copy them from other job boards. The text, the conditions and the procedure belong to the employer; we pass them on."),
        ("p", "Tussen twee controles in kan een vacature sluiten of veranderen. Wij controleren wekelijks of een vacature nog openstaat en halen gesloten vacatures uit het overzicht, maar wij kunnen niet garanderen dat alles op elk moment actueel is. Klik altijd door naar de werkgever voor de geldende tekst.",
              "Between two checks a vacancy may close or change. We check weekly whether a vacancy is still open and remove closed ones from the overview, but we cannot guarantee that everything is current at every moment. Always click through to the employer for the applicable text."),
    ]),
    ("Over de gidsen en de kantoorprofielen", "About the guides and firm profiles", [
        ("p", "Onze gidsen en profielen zijn samengesteld uit openbare bronnen en eigen ervaring in de sector. Salarissen, functienamen en kantoorstructuren veranderen. Wij geven aan wanneer iets een indicatie is en werken bij waar wij kunnen, maar een garantie op juistheid of volledigheid geven wij niet.",
              "Our guides and profiles are compiled from public sources and our own experience in the sector. Salaries, job titles and firm structures change. We indicate when something is an estimate and update where we can, but we do not guarantee accuracy or completeness."),
        ("p", "Kom je iets tegen dat niet klopt, laat het ons weten via <a href=\"mailto:partner@corporatecareer.nl\">partner@corporatecareer.nl</a>. Wij passen het aan.",
              "If you find something that is wrong, let us know at <a href=\"mailto:partner@corporatecareer.nl\">partner@corporatecareer.nl</a>. We will correct it."),
    ]),
    ("Intellectueel eigendom", "Intellectual property", [
        ("p", "De teksten, gidsen, vormgeving en samenstelling van deze site zijn van CorporateCareer. Je mag ze lezen, delen en eruit citeren met bronvermelding. Overnemen van hele pagina's of van de vacaturedatabank, of die geautomatiseerd uitlezen om er een eigen dienst mee te voeren, mag niet zonder onze toestemming.",
              "The texts, guides, design and compilation of this site belong to CorporateCareer. You may read them, share them and quote from them with attribution. Reproducing entire pages or the vacancy database, or reading it automatically to run a service of your own, is not permitted without our consent."),
        ("p", "Namen en logo's van kantoren zijn van die kantoren. Wij gebruiken ze om naar hen te verwijzen, niet om een band te suggereren die er niet is.",
              "Firm names and logos belong to those firms. We use them to refer to them, not to suggest a relationship that does not exist."),
    ]),
    ("Gebruik van de site", "Use of the site", [
        ("p", "Je mag de site gebruiken waarvoor hij bedoeld is. Wat niet mag: de site zo belasten dat hij voor anderen traag of onbereikbaar wordt, beveiliging omzeilen, of de inhoud geautomatiseerd verzamelen op een schaal die verder gaat dan gewoon lezen.",
              "You may use the site for what it is intended for. What is not allowed: loading the site so heavily that it becomes slow or unreachable for others, circumventing security, or harvesting the content automatically on a scale beyond ordinary reading."),
    ]),
    ("Aansprakelijkheid", "Liability", [
        ("p", "Wij doen ons best om de informatie juist en actueel te houden, maar wij aanvaarden geen aansprakelijkheid voor schade die voortkomt uit het gebruik van deze site of uit beslissingen die je op basis van de informatie neemt. Dat geldt ook voor de vacatures: de werkgever is verantwoordelijk voor zijn eigen tekst en procedure.",
              "We do our best to keep the information accurate and current, but we accept no liability for damage arising from use of this site or from decisions you make on the basis of the information. The same applies to the vacancies: the employer is responsible for its own text and procedure."),
        ("p", "Deze beperking geldt niet bij opzet of bewuste roekeloosheid van onze kant.",
              "This limitation does not apply in the case of intent or deliberate recklessness on our part."),
    ]),
    ("Links naar andere websites", "Links to other websites", [
        ("p", "Deze site verwijst naar wervingssystemen en websites van werkgevers en naar andere externe bronnen. Voor de inhoud daarvan en voor de manier waarop die partijen met jouw gegevens omgaan zijn wij niet verantwoordelijk.",
              "This site links to employers' recruitment systems and websites and to other external sources. We are not responsible for their content or for how those parties handle your data."),
    ]),
    ("Wijzigingen", "Changes", [
        ("p", "Wij kunnen deze voorwaarden aanpassen. De datum bovenaan geeft aan wanneer dat voor het laatst gebeurd is. Blijf je de site gebruiken, dan gelden de aangepaste voorwaarden.",
              "We may amend these terms. The date at the top indicates when that last happened. If you keep using the site, the amended terms apply."),
    ]),
    ("Toepasselijk recht", "Governing law", [
        ("p", "Op deze voorwaarden is Nederlands recht van toepassing. Geschillen worden voorgelegd aan de bevoegde rechter in Nederland.",
              "Dutch law applies to these terms. Disputes will be submitted to the competent court in the Netherlands."),
    ]),
]

PAGINAS = [
    {
        "bestand": "privacy.html",
        "titel_nl": "Privacyverklaring", "titel_en": "Privacy statement",
        "kop_nl": "Privacyverklaring", "kop_en": "Privacy statement",
        "intro_nl": "Wat wij van bezoekers van corporatecareer.nl vastleggen, waarom wij dat doen, en wat je eraan kunt veranderen.",
        "intro_en": "What we record about visitors to corporatecareer.nl, why we do it, and what you can change about it.",
        "desc_nl": "Privacyverklaring van CorporateCareer: welke gegevens wij verwerken, op welke grondslag, hoe lang wij ze bewaren en welke rechten je hebt.",
        "desc_en": "CorporateCareer privacy statement: what data we process, on what legal basis, how long we keep it and what rights you have.",
        "keywords": "privacyverklaring corporatecareer, privacy carriereplatform, avg gegevens",
        "secties": PRIVACY,
    },
    {
        "bestand": "voorwaarden.html",
        "titel_nl": "Gebruiksvoorwaarden", "titel_en": "Terms of use",
        "kop_nl": "Gebruiksvoorwaarden", "kop_en": "Terms of use",
        "intro_nl": "De afspraken voor het gebruik van corporatecareer.nl: wat je van ons mag verwachten, en wat wij van jou.",
        "intro_en": "The terms for using corporatecareer.nl: what you may expect from us, and what we expect from you.",
        "desc_nl": "Gebruiksvoorwaarden van CorporateCareer: wat het platform wel en niet is, hoe wij met vacatures omgaan en waarvoor wij niet aansprakelijk zijn.",
        "desc_en": "CorporateCareer terms of use: what the platform is and is not, how we handle vacancies and what we are not liable for.",
        "keywords": "gebruiksvoorwaarden corporatecareer, algemene voorwaarden carriereplatform",
        "secties": VOORWAARDEN,
    },
    {
        "bestand": "cookies.html",
        "titel_nl": "Cookieverklaring", "titel_en": "Cookie statement",
        "kop_nl": "Cookieverklaring", "kop_en": "Cookie statement",
        "intro_nl": "Welke cookies corporatecareer.nl plaatst, wat ze doen en hoe je ze weigert.",
        "intro_en": "Which cookies corporatecareer.nl places, what they do and how to refuse them.",
        "desc_nl": "Cookieverklaring van CorporateCareer: welke cookies de site plaatst, waarvoor ze dienen, hoe lang ze blijven staan en hoe je ze weigert.",
        "desc_en": "CorporateCareer cookie statement: which cookies the site places, what they are for, how long they stay and how to refuse them.",
        "keywords": "cookieverklaring corporatecareer, cookies carriereplatform, google analytics cookies",
        "secties": COOKIES,
    },
]


# ── opbouw ───────────────────────────────────────────────────────────────────

def render_secties(secties):
    uit = []
    for kop_nl, kop_en, blokken in secties:
        uit.append(f"        <h2>{t(kop_nl, kop_en)}</h2>")
        for blok in blokken:
            if blok[0] == "p":
                uit.append(f"        <p>{t(blok[1], blok[2])}</p>")
            elif blok[0] == "ul":
                uit.append("        <ul>")
                for nl, en in blok[1]:
                    uit.append(f"          <li>{t(nl, en)}</li>")
                uit.append("        </ul>")
            elif blok[0] == "table":
                koppen_nl, koppen_en = blok[1]
                uit.append('        <table class="jur-table">')
                uit.append("          <thead><tr>" + "".join(
                    f"<th>{t(a, b)}</th>" for a, b in zip(koppen_nl, koppen_en)) + "</tr></thead>")
                uit.append("          <tbody>")
                for rij in blok[2]:
                    uit.append("            <tr>" + "".join(
                        f"<td>{t(nl, en)}</td>" for nl, en in rij) + "</tr>")
                uit.append("          </tbody>")
                uit.append("        </table>")
    return "\n".join(uit)


def seo_blok(p):
    url = f"{SITE}/{p['bestand']}"
    return f"""  <!-- ── SEO ──────────────────────────────── -->
  <meta name="keywords" content="{p['keywords']}">
  <meta name="author" content="CorporateCareer">
  <meta name="robots" content="index, follow">
  <link rel="alternate" hreflang="nl" href="{url}">
  <link rel="alternate" hreflang="en" href="{SITE}/en/{p['bestand']}">
  <link rel="alternate" hreflang="x-default" href="{url}">
  <link rel="canonical" href="{url}">
  <!-- Open Graph -->
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="CorporateCareer">
  <meta property="og:title" content="{p['titel_nl']} | CorporateCareer">
  <meta property="og:description" content="{p['desc_nl']}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{SITE}/img/og-cover.jpg">
  <meta property="og:locale" content="nl_NL">
  <meta property="og:locale:alternate" content="en_GB">
  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{p['titel_nl']} | CorporateCareer">
  <meta name="twitter:description" content="{p['desc_nl']}">
  <meta name="twitter:image" content="{SITE}/img/og-cover.jpg">
  <!-- Structured Data -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "WebPage",
    "@id": "{url}#page",
    "name": "{p['titel_nl']}",
    "description": "{p['desc_nl']}",
    "url": "{url}",
    "inLanguage": "nl-NL",
    "dateModified": "{date.today().isoformat()}",
    "publisher": {{"@id": "{SITE}/#organization"}},
    "breadcrumb": {{
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{"@type": "ListItem", "position": 1, "name": "Home", "item": "{SITE}/"}},
        {{"@type": "ListItem", "position": 2, "name": "{p['titel_nl']}", "item": "{url}"}}
      ]
    }}
  }}
  </script>
  <meta name="description" content="{p['desc_nl']}">
  <title>{p['titel_nl']} | CorporateCareer</title>
"""


def update_sitemap():
    """Zet de drie Nederlandse pagina's in de sitemap.

    De Engelse varianten worden door build_en.py toegevoegd, binnen zijn eigen
    EN-blok. Dit blok staat er los van en heeft eigen merktekens, zodat beide
    scripts elkaar niet overschrijven en herhaald draaien niets verdubbelt.
    """
    sm = os.path.join(BASE, "sitemap.xml")
    xml = open(sm, encoding="utf-8").read()
    blok = "\n".join(f"""  <url>
    <loc>{SITE}/{p['bestand']}</loc>
    <changefreq>yearly</changefreq>
    <priority>0.3</priority>
  </url>""" for p in PAGINAS)
    gemerkt = f"  <!-- JURIDISCH:START -->\n{blok}\n  <!-- JURIDISCH:END -->"
    if "<!-- JURIDISCH:START -->" in xml:
        xml = re.sub(r"  <!-- JURIDISCH:START -->[\s\S]*?  <!-- JURIDISCH:END -->", gemerkt, xml)
    elif "  <!-- EN:START -->" in xml:
        # Voor het Engelse blok, zodat de Nederlandse URL's bij elkaar blijven.
        xml = xml.replace("  <!-- EN:START -->", gemerkt + "\n\n  <!-- EN:START -->")
    else:
        xml = xml.replace("</urlset>", gemerkt + "\n\n</urlset>")
    open(sm, "w", encoding="utf-8").write(xml)


BESTANDEN = {"footer.col3.privacy": "privacy.html",
             "footer.col3.terms": "voorwaarden.html",
             "footer.col3.cookies": "cookies.html"}

# Het voorvoegsel wordt afgeleid van de "Over ons"-link in dezelfde footer, niet
# geraden. De pagina's staan op verschillende diepten: de homepage gebruikt
# "over-ons.html", een vacaturepagina "../over-ons.html", een bedrijfspagina
# "/over-ons.html" en een Engelse pagina "/en/over-ons.html". Dezelfde vorm
# aanhouden is de enige manier om op alle 2.340 pagina's een werkende link te
# krijgen.
OVER_ONS = re.compile(r'<a href="([^"]*?)over-ons\.html" data-i18n="footer\.col2\.about"')
TODO = re.compile(r"\s*<!--\s*TODO: deze links wijzen nog naar[\s\S]*?-->", re.S)


def update_footers():
    """Laat de drie juridische links in elke footer naar de nieuwe pagina's wijzen."""
    n = links = 0
    for dp, dn, fn in os.walk(BASE):
        dn[:] = [d for d in dn if d not in (".git", "node_modules")]
        for f in fn:
            if not f.endswith(".html"):
                continue
            pad = os.path.join(dp, f)
            html = open(pad, encoding="utf-8").read()
            m = OVER_ONS.search(html)
            if not m:
                continue
            voor = m.group(1)
            nieuw = html
            for sleutel, doel in BESTANDEN.items():
                nieuw = nieuw.replace(f'<a href="#" data-i18n="{sleutel}"',
                                      f'<a href="{voor}{doel}" data-i18n="{sleutel}"')
            # De notitie dat deze pagina's nog niet bestonden kan weg.
            nieuw = TODO.sub("", nieuw)
            if nieuw != html:
                links += sum(nieuw.count(f'"{voor}{doel}" data-i18n="{s}"')
                             for s, doel in BESTANDEN.items())
                open(pad, "w", encoding="utf-8").write(nieuw)
                n += 1
    print(f"  footers: {n} pagina's, {links} links rechtgezet")


def main():
    bron = open(BRON, encoding="utf-8").read()

    kop_start = bron.index("<!-- ── SEO")
    kop_eind = bron.index('<link rel="icon"')
    voorkant = bron[:kop_start]
    staart_head = bron[kop_eind:bron.index("<style>")]
    rest_head = bron[bron.index("</style>") + len("</style>"):bron.index("</head>")]
    navbar = bron[bron.index('<nav class="navbar"'):bron.index("</nav>") + len("</nav>")]
    footer = bron[bron.index("<!-- ── FOOTER"):bron.index("</html>")]

    for p in PAGINAS:
        body = render_secties(p["secties"])
        html = (voorkant + seo_blok(p) + staart_head + STIJL + rest_head + "</head>\n<body>\n\n  "
                + navbar + "\n\n  <main>\n\n"
                + f"""  <section class="jur-hero">
    <div class="container">
      <h1>{t(p['kop_nl'], p['kop_en'])}</h1>
      <p>{t(p['intro_nl'], p['intro_en'])}</p>
      <p class="jur-meta">{t('Laatst bijgewerkt op ' + BIJGEWERKT_NL, 'Last updated ' + BIJGEWERKT_EN)}</p>
    </div>
  </section>

  <section class="jur-body">
    <div class="container">
      <div class="jur-prose">
{body}
      </div>
    </div>
  </section>

  </main>

"""
                + footer + "</html>\n")
        uit = os.path.join(BASE, p["bestand"])
        open(uit, "w", encoding="utf-8").write(html)
        print(f"  {p['bestand']:20} {len(p['secties']):2} secties, {len(html):6} tekens")

    update_sitemap()
    update_footers()
    print(f"{len(PAGINAS)} pagina's geschreven, sitemap en footers bijgewerkt. "
          f"Draai nu scripts/build_en.py voor de /en/-varianten.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
