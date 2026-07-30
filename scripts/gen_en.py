# -*- coding: utf-8 -*-
"""Herbruikbare transformer: maak van een NL-pagina de Engelse /en/-variant,
en injecteer hreflang in de NL-pagina. Gebruikt door scripts/build_en.py
(content + bedrijven) en scripts/build_vacature_pages.py (vacatures)."""
import re, os, posixpath, html as _H

BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE="https://corporatecareer.nl"
ASSET_PREFIXES=("css/","js/","img/","fonts/")
ASSET_EXT=(".css",".js",".woff2",".woff",".svg",".png",".jpg",".jpeg",".webp",".ico",".gif")

def _parse_block(body):
    pairs=re.findall(r"'((?:[^'\\]|\\.)*)'\s*:\s*'((?:[^'\\]|\\.)*)'", body)
    return {k.replace("\\'","'"):v.replace("\\'","'") for k,v in pairs}

def en_dict():
    src=open(os.path.join(BASE,"js","i18n.js"),encoding="utf-8").read()
    return _parse_block(re.search(r"\ben:\s*\{(.*?)\n\s*\},\s*\n\s*nl:\s*\{", src, re.S).group(1))

def nl_dict():
    src=open(os.path.join(BASE,"js","i18n.js"),encoding="utf-8").read()
    return _parse_block(re.search(r"\bnl:\s*\{(.*)\}\s*\};", src, re.S).group(1))

_DICTS={}
def _dict(lang):
    if lang not in _DICTS:
        _DICTS[lang]=en_dict() if lang=="en" else nl_dict()
    return _DICTS[lang]

def bake(html, lang):
    """Bakt de vertaalbare tekst in de gekozen taal in de ruwe HTML in, zodat
    de pagina de juiste taal toont zonder het runtime-vertaalbestand.
    Verwerkt data-i18n (tekst), data-i18n-html (html), data-i18n-placeholder,
    data-i18n-aria en de zichtbaarheid van data-l-blokken."""
    D=_dict(lang)
    # data-i18n-html: vervang de binnen-HTML, nesting-bewust (het element kan
    # een geneste tag van hetzelfde type bevatten, bv. <span> in <span>).
    open_re=re.compile(r'<(\w+)[^>]*\bdata-i18n-html="([^"]+)"[^>]*>')
    out=[]; i=0
    while True:
        m=open_re.search(html, i)
        if not m:
            out.append(html[i:]); break
        tag, key = m.group(1), m.group(2)
        out.append(html[i:m.end()])
        close="</"+tag+">"; tag_open=re.compile(r'<'+tag+r'(?:\s|>|/)')
        depth=1; j=m.end()
        while depth>0:
            nc=html.find(close, j); no=tag_open.search(html, j)
            if nc==-1: j=len(html); break
            if no and no.start()<nc: depth+=1; j=no.end()
            else: depth-=1; j=nc+len(close)
        inner_close=j-len(close)
        v=D.get(key)
        out.append(v if v is not None else html[m.end():inner_close])
        out.append(close); i=j
    html="".join(out)
    def rep_txt(m):
        v=D.get(m.group(2)); return f'{m.group(1)}{_H.escape(v)}<' if v is not None else m.group(0)
    html=re.sub(r'(<[^>]*\bdata-i18n="([^"]+)"[^>]*>)([^<]*)<', rep_txt, html)
    for attr, htmlattr in (("data-i18n-placeholder","placeholder"), ("data-i18n-aria","aria-label")):
        def rep_attr(m, a=htmlattr):
            v=D.get(m.group('k'));  tag=m.group(0)
            if v is None: return tag
            if re.search(a+r'="[^"]*"', tag):
                return re.sub(a+r'="[^"]*"', a+'="'+_H.escape(v, quote=True)+'"', tag, count=1)
            return tag[:-1]+f' {a}="{_H.escape(v, quote=True)}">'
        html=re.sub(r'<[^>]*\b'+attr+r'="(?P<k>[^"]+)"[^>]*>', rep_attr, html)
    # data-l zichtbaarheid: toon de gekozen taal, verberg de andere
    other="nl" if lang=="en" else "en"
    html=html.replace(f'data-l="{lang}" hidden>', f'data-l="{lang}">')
    html=html.replace(f'data-l="{other}">', f'data-l="{other}" hidden>')
    return html

# Mini-runtime die het 1,3 MB vertaalbestand vervangt: zet de paginataal,
# levert de paar sleutels die main.js nodig heeft, en laat de toggle naar de
# andere taal-URL navigeren. De paginatekst is verder ingebakken (zie bake()).
RUNTIME_KEYS=("nav.hamburger.open","nav.hamburger.close","cta.success","cta.btn")
def runtime_js():
    en, nl = en_dict(), nl_dict()
    def obj(d): return "{"+",".join("'%s':'%s'"%(k, d.get(k,"").replace("'","\\'")) for k in RUNTIME_KEYS)+"}"
    return ("window.CURRENT_LANG=window.__ccDefaultLang||'nl';"
            "var TRANSLATIONS={en:"+obj(en)+",nl:"+obj(nl)+"};"
            "function ccOtherLangUrl(){var p=location.pathname,e=p==='/en'||p.indexOf('/en/')===0,"
            "t=e?(p.replace(/^\\/en/,'')||'/'):('/en'+p);return t+location.search+location.hash;}"
            "document.addEventListener('DOMContentLoaded',function(){var t=document.getElementById('langToggle');"
            "if(t)t.addEventListener('click',function(){location.href=ccOtherLangUrl();});});\n")
def write_runtime():
    open(os.path.join(BASE,"js","i18n.min.js"),"w",encoding="utf-8").write(runtime_js())

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
    # De deelkaart bestaat in twee talen: de kop erop staat in het Nederlands.
    html=html.replace("/img/og-cover.jpg","/img/og-cover-en.jpg")
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
    html=bake(html, "en")
    return html

def add_hreflang_nl(html, site_path):
    if 'hreflang="en"' in html: return html
    if re.search(r'  <link rel="canonical"[^>]*>\n',html):
        return re.sub(r'(  <link rel="canonical"[^>]*>\n)',_hreflang(site_path)+r'\1',html,count=1)
    return html.replace('</head>',_hreflang(site_path)+'</head>',1)
