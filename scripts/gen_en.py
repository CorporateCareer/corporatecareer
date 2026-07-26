# -*- coding: utf-8 -*-
"""Herbruikbare transformer: maak van een NL-pagina de Engelse /en/-variant,
en injecteer hreflang in de NL-pagina. Gebruikt door scripts/build_en.py
(content + bedrijven) en scripts/build_vacature_pages.py (vacatures)."""
import re, os, posixpath

BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE="https://corporatecareer.nl"
ASSET_PREFIXES=("css/","js/","img/","fonts/")
ASSET_EXT=(".css",".js",".woff2",".woff",".svg",".png",".jpg",".jpeg",".webp",".ico",".gif")

def en_dict():
    src=open(os.path.join(BASE,"js","i18n.js"),encoding="utf-8").read()
    m=re.search(r"\ben:\s*\{(.*?)\n\s*\},\s*\n\s*nl:\s*\{", src, re.S)
    pairs=re.findall(r"'((?:[^'\\]|\\.)*)'\s*:\s*'((?:[^'\\]|\\.)*)'", m.group(1))
    return {k.replace("\\'","'"):v.replace("\\'","'") for k,v in pairs}

def _is_asset(ab):
    p=ab.lstrip("/")
    if any(p.startswith(a) for a in ASSET_PREFIXES): return True
    if p in ("favicon.svg","favicon.ico","robots.txt","sitemap.xml"): return True
    return ab.lower().endswith(ASSET_EXT) and not ab.lower().endswith(".html")

def _rewrite_link(src_dir, href):
    if re.match(r"^(https?:|mailto:|tel:|#|data:|//)", href): return href
    frag=""
    if "#" in href: href,frag=href.split("#",1); frag="#"+frag
    if href=="": return frag or "#"
    ab=href if href.startswith("/") else "/"+posixpath.normpath(posixpath.join(src_dir,href)).lstrip("/")
    return (ab if _is_asset(ab) else "/en"+ab)+frag

def _hreflang(site_path):
    en=f"{SITE}/en{site_path}"; nl=f"{SITE}{site_path}"
    return (f'  <link rel="alternate" hreflang="nl" href="{nl}">\n'
            f'  <link rel="alternate" hreflang="en" href="{en}">\n'
            f'  <link rel="alternate" hreflang="x-default" href="{nl}">\n')

def to_en(html, site_path, title, desc):
    """html = NL-bron; site_path = bv /finance.html of /vacatures/x.html."""
    src_dir=posixpath.dirname(site_path)
    en_url=f"{SITE}/en{site_path}"
    html=re.sub(r'<html lang="[a-z]*"','<html lang="en"',html,count=1)
    if "__ccDefaultLang" in html:
        html=re.sub(r"__ccDefaultLang='[a-z]*'","__ccDefaultLang='en'",html,count=1)
    else:
        html=html.replace('<meta charset="UTF-8">','<meta charset="UTF-8">\n  <script>window.__ccDefaultLang=\'en\';</script>',1)
    html=re.sub(r'\b(href|src)=(")([^"]*)"',lambda m:f'{m.group(1)}="{_rewrite_link(src_dir,m.group(3))}"',html)
    html=re.sub(r'(<link rel="canonical" href=")[^"]*(")',lambda m:m.group(1)+en_url+m.group(2),html,count=1)
    html=re.sub(r'(property="og:url" content=")[^"]*(")',lambda m:m.group(1)+en_url+m.group(2),html,count=1)
    html=re.sub(r'(property="og:locale" content=")[^"]*(")',r'\1en_GB\2',html,count=1)
    html=re.sub(r'(property="og:locale:alternate" content=")[^"]*(")',r'\1nl_NL\2',html,count=1)
    html=re.sub(r'<title>.*?</title>','<title>'+title+'</title>',html,count=1,flags=re.S)
    for pat in [r'(name="description" content=")[^"]*(")',r'(property="og:description" content=")[^"]*(")',r'(name="twitter:description" content=")[^"]*(")']:
        html=re.sub(pat,lambda m:m.group(1)+desc+m.group(2),html,count=1)
    for pat in [r'(property="og:title" content=")[^"]*(")',r'(name="twitter:title" content=")[^"]*(")']:
        html=re.sub(pat,lambda m:m.group(1)+title.split(" | ")[0]+m.group(2),html,count=1)
    if 'hreflang="en"' not in html:
        if re.search(r'  <link rel="canonical"[^>]*>\n',html):
            html=re.sub(r'(  <link rel="canonical"[^>]*>\n)',_hreflang(site_path)+r'\1',html,count=1)
        else:
            html=html.replace('</head>',_hreflang(site_path)+'</head>',1)
    return html

def add_hreflang_nl(html, site_path):
    if 'hreflang="en"' in html: return html
    if re.search(r'  <link rel="canonical"[^>]*>\n',html):
        return re.sub(r'(  <link rel="canonical"[^>]*>\n)',_hreflang(site_path)+r'\1',html,count=1)
    return html.replace('</head>',_hreflang(site_path)+'</head>',1)
