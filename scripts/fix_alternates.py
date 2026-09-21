# -*- coding: utf-8 -*-
"""Zet canonical, hreflang en og:url op elke pagina op dezelfde URL.

Een mappagina is via twee URL's bereikbaar met dezelfde inhoud:

    /bedrijven/akd/            <- staat in de sitemap en in de canonical
    /bedrijven/akd/index.html  <- stond in de hreflang en in de Engelse canonical

Google negeert een hreflang-groep waarvan de URL's niet de canonieke zijn. In
Search Console kwam dat terug als "Alternate page with proper canonical tag",
een groep die groeide van 45 naar 55 pagina's met de validatie op Failed.

Dit script loopt alle gebouwde pagina's langs en trekt de drie velden recht.
De generator doet het voortaan vanzelf; dit is voor wat er al staat.
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_en import SITE, canon_path

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OVERSLAAN = {"404.html"}


def site_path_of(pad):
    """/home/.../en/bedrijven/akd/index.html -> ('/bedrijven/akd/', 'en')"""
    rel = "/" + os.path.relpath(pad, BASE).replace(os.sep, "/")
    lang = "nl"
    if rel.startswith("/en/") or rel == "/en/index.html":
        lang, rel = "en", rel[3:]
    return canon_path(rel), lang


def fix(html, site_path, lang):
    url = SITE + ("/en" if lang == "en" else "") + site_path
    nl = SITE + site_path
    en = SITE + "/en" + site_path
    out = html
    out = re.sub(r'(<link rel="canonical" href=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), out, count=1)
    out = re.sub(r'(<meta property="og:url" content=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), out, count=1)
    out = re.sub(r'(<link rel="alternate" hreflang="nl" href=")[^"]*(")', lambda m: m.group(1) + nl + m.group(2), out, count=1)
    out = re.sub(r'(<link rel="alternate" hreflang="en" href=")[^"]*(")', lambda m: m.group(1) + en + m.group(2), out, count=1)
    out = re.sub(r'(<link rel="alternate" hreflang="x-default" href=")[^"]*(")', lambda m: m.group(1) + nl + m.group(2), out, count=1)
    return out


def main():
    geraakt = bekeken = 0
    for wortel, mappen, files in os.walk(BASE):
        mappen[:] = [m for m in mappen if m not in (".git", ".github", "scripts", "node_modules")]
        for f in files:
            if not f.endswith(".html") or f in OVERSLAAN:
                continue
            pad = os.path.join(wortel, f)
            html = open(pad, encoding="utf-8").read()
            sp, lang = site_path_of(pad)
            nieuw = fix(html, sp, lang)
            bekeken += 1
            if nieuw != html:
                open(pad, "w", encoding="utf-8").write(nieuw)
                geraakt += 1
    print(f"{bekeken} pagina's bekeken, {geraakt} rechtgetrokken")
    return 0


if __name__ == "__main__":
    sys.exit(main())
