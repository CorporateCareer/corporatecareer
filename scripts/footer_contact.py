# -*- coding: utf-8 -*-
"""Zet de contactlink in elke footer, en repareert de doodlopende Blog-link.

Twee dingen waren scheefgegroeid in de tweede footerkolom:

    Contact   stond op zes pagina's, terwijl bezoekers vanuit Google juist op
              de vacature- en bedrijfspagina's binnenkomen. Wie daar contact
              wilde zoeken, kon nergens heen.
    Blog      wees op 1.952 pagina's naar "#". Dat is een link die niets doet
              en die zoekmachines als kapot lezen.

Het pad wordt niet geraden maar afgeleid van de buurlink in hetzelfde blok.
Staat "Over ons" er als ../over-ons.html, dan wordt Blog ../articles.html;
staat hij er als /en/over-ons.html, dan wordt het /en/articles.html. Dat is
nodig omdat de pagina's op verschillende diepten staan en de bouwscripts
relatieve links naderhand nog een ../ voorzetten.

De bouwscripts kopiëren hun footer uit een bestaande pagina: de vacatures uit
jobs.html, de bedrijfspagina's uit de private-equity-pagina. Die bronpagina's
zijn zelf ook gewoon HTML, dus door alles in één keer langs te lopen blijven
bron en uitvoer gelijk en overleeft de wijziging de wekelijkse herbouw.

Het script is herhaalbaar: een tweede run verandert niets meer.

Gebruik:
    python scripts/footer_contact.py            aanpassen
    python scripts/footer_contact.py --droog     alleen tonen wat er zou gebeuren
"""
import os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OVERSLAAN = {".git", "node_modules"}

CONTACT = '<a href="mailto:partner@corporatecareer.nl" data-i18n="footer.col2.contact">Contact</a>'

# Het blok van de tweede footerkolom: vanaf de kop tot de afsluitende div.
BLOK = re.compile(r'(<h2 data-i18n="footer\.col2\.title">.*?</h2>)(.*?)(\n\s*</div>)', re.S)
LINK = re.compile(r'<a href="([^"]*)" data-i18n="([^"]+)"[^>]*>(.*?)</a>', re.S)


def blog_pad(binnen):
    """Het juiste pad naar de artikelenpagina, afgeleid van de buurlink."""
    for href, sleutel, _ in LINK.findall(binnen):
        if sleutel == "footer.col2.about" and href.endswith("over-ons.html"):
            return href[: -len("over-ons.html")] + "articles.html"
    return None


def pas_blok_aan(m, rapport):
    kop, binnen, staart = m.group(1), m.group(2), m.group(3)
    origineel = binnen

    # 1. De doodlopende Blog-link naar de artikelenpagina wijzen.
    if 'href="#" data-i18n="footer.col2.blog"' in binnen:
        pad = blog_pad(binnen)
        if pad:
            binnen = binnen.replace('<a href="#" data-i18n="footer.col2.blog"',
                                    f'<a href="{pad}" data-i18n="footer.col2.blog"')
            rapport["blog"] += 1

    # 2. De contactlink toevoegen als hij ontbreekt.
    if 'data-i18n="footer.col2.contact"' not in binnen:
        regels = [r for r in binnen.split("\n") if "<a " in r]
        inspring = re.match(r"\s*", regels[-1]).group(0) if regels else "          "
        binnen = binnen.rstrip("\n") + "\n" + inspring + CONTACT
        rapport["contact"] += 1

    return kop + binnen + staart if binnen != origineel else m.group(0)


def loop_bestanden():
    for dp, dn, fn in os.walk(BASE):
        dn[:] = [d for d in dn if d not in OVERSLAAN]
        for f in fn:
            if f.endswith(".html"):
                yield os.path.join(dp, f)


def main(droog=False):
    rapport = {"blog": 0, "contact": 0}
    gewijzigd = 0
    for pad in loop_bestanden():
        html = open(pad, encoding="utf-8").read()
        nieuw = BLOK.sub(lambda m: pas_blok_aan(m, rapport), html, count=1)
        if nieuw != html:
            gewijzigd += 1
            if not droog:
                open(pad, "w", encoding="utf-8").write(nieuw)
    woord = "zouden wijzigen" if droog else "gewijzigd"
    print(f"{gewijzigd} pagina's {woord}")
    print(f"  contactlink toegevoegd: {rapport['contact']}")
    print(f"  Blog-link gerepareerd:  {rapport['blog']}")
    return 0


if __name__ == "__main__":
    sys.exit(main("--droog" in sys.argv))
