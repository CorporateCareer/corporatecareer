# -*- coding: utf-8 -*-
"""Genereert de Engelse /en/-varianten van de content- en bedrijfspaginas en
injecteert hreflang in de NL-bronnen. Vacatures worden apart door
build_vacature_pages.py gegenereerd. Draai dit na wijzigingen aan de
NL-content-paginas zodat /en/ meeloopt."""
import os, re, glob, posixpath
import gen_en

BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D=gen_en.en_dict()

def strip_tags(s): return re.sub(r'<[^>]+>','',s).replace("&amp;","&").strip()
def derive_title(html):
    m=re.search(r'<h1[^>]*\bdata-i18n(?:-html)?="([^"]+)"[^>]*>([^<]*)',html)
    if m and D.get(m.group(1)): return strip_tags(D[m.group(1)])
    m=re.search(r'<h1[^>]*>\s*<span data-l="en">([^<]*)',html)
    if m: return m.group(1).strip()
    m=re.search(r'<h1[^>]*>([^<]*)',html)
    return m.group(1).strip() if m else "CorporateCareer"
def derive_desc(html):
    m=re.search(r'<p[^>]*\bdata-i18n="([^"]+)"[^>]*>',html)
    if m and D.get(m.group(1)):
        t=strip_tags(D[m.group(1)])
        if len(t)>40: return (t[:157].rsplit(" ",1)[0]+"...") if len(t)>160 else t
    m=re.search(r'<p[^>]*>\s*<span data-l="en">([\s\S]*?)</span>',html)
    if m:
        t=strip_tags(m.group(1))
        if len(t)>40: return (t[:157].rsplit(" ",1)[0]+"...") if len(t)>160 else t
    return None

CURATED={
 "index.html":("Careers in finance, consulting and law in the Netherlands | CorporateCareer",
   "Independent career guide for finance, consulting and law in the Netherlands: career paths, employers, vacancies and in-depth interview guides for ambitious students."),
 "finance.html":("Careers in finance: investment banking, private equity and M&A | CorporateCareer",
   "Explore finance career paths in the Netherlands: investment banking, M&A, private equity, venture capital, corporate finance and more. Compare roles, employers and current vacancies."),
 "consulting.html":("Management consulting in the Netherlands: career guide | CorporateCareer",
   "Land an offer at McKinsey, BCG or Bain in Amsterdam. A complete guide to case interview preparation, CV tips and the consulting recruitment process in the Netherlands."),
 "legal.html":("Law careers in the Netherlands: the trainee guide | CorporateCareer",
   "Break into De Brauw, NautaDutilh or Freshfields. A complete guide to law firm traineeships in the Netherlands, from your master's to your first day as a trainee lawyer."),
 "jobs.html":("Vacancies in finance, consulting and law | CorporateCareer",
   "Browse current vacancies at Goldman Sachs, McKinsey, De Brauw and other leading employers in the Netherlands. Filter by sector, type and location. Updated weekly."),
 "partners.html":("Our employers in finance, consulting and law | CorporateCareer",
   "CorporateCareer covers leading employers in finance, consulting and law, including Goldman Sachs, McKinsey, BCG, De Brauw and NautaDutilh."),
 "articles.html":("Career guides and articles: finance, consulting and law | CorporateCareer",
   "In-depth career guides for ambitious students in the Netherlands: cracking the case interview, investment banking recruitment timelines and law firm traineeship strategies."),
 "over-ons.html":("About CorporateCareer | CorporateCareer",
   "About CorporateCareer: an independent career guide for students in finance, consulting and law in the Netherlands."),
 "resources/index.html":("Guides and resources for finance, consulting and law careers | CorporateCareer",
   "Guides and resources for your career in finance, consulting and law: the application guide, the case interview guide and the finance interview guide."),
 "resources/sollicitatiegids/index.html":("Application guide: CV, cover letter and the process | CorporateCareer",
   "How to apply for finance, consulting and law roles: CV, cover letter, online assessments, interviews and the process from application to offer."),
 "resources/case-interview/index.html":("Case interview guide: how to crack consulting cases | CorporateCareer",
   "Learn the consulting case interview: how to structure and solve a business problem, the main case types, mental maths, market sizing and four worked practice cases."),
 "resources/finance-interview/index.html":("Finance interview guide: private equity, M&A and corporate finance | CorporateCareer",
   "The complete guide to finance interviews in private equity, M&A and corporate finance: the process, financial statements, valuation and the finance case types with worked examples."),
}

def page_list():
    p=[os.path.basename(f) for f in glob.glob(os.path.join(BASE,"*.html"))]
    for pat in ("finance/*/index.html","consulting/*/index.html","legal/*/index.html","bedrijven/*/index.html"):
        p+=[os.path.relpath(f,BASE) for f in glob.glob(os.path.join(BASE,pat))]
    p+=["resources/index.html","resources/sollicitatiegids/index.html","resources/case-interview/index.html","resources/finance-interview/index.html"]
    return sorted(set(p))

def en_url(rel):
    return f"{gen_en.SITE}/en/{rel[:-10] if rel.endswith('/index.html') else rel}"

def update_sitemap(rels):
    sm=os.path.join(BASE,"sitemap.xml")
    xml=open(sm,encoding="utf-8").read()
    block="\n".join(f"""  <url>
    <loc>{en_url(r)}</loc>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>""" for r in rels)
    marked=f"  <!-- EN:START -->\n{block}\n  <!-- EN:END -->"
    if "<!-- EN:START -->" in xml:
        xml=re.sub(r"  <!-- EN:START -->[\s\S]*?  <!-- EN:END -->",marked,xml)
    else:
        xml=xml.replace("</urlset>",marked+"\n\n</urlset>")
    open(sm,"w",encoding="utf-8").write(xml)

def main():
    rels=page_list(); n=0
    for rel in rels:
        src=os.path.join(BASE,rel)
        html=open(src,encoding="utf-8").read()
        site_path="/"+rel
        if rel in CURATED:
            title,desc=CURATED[rel]
        else:
            h1=derive_title(html); title=f"{h1} | CorporateCareer"
            desc=derive_desc(html) or f"{h1} in the Netherlands: what the work involves, roles, the recruitment process and how to get started."
        en_html=gen_en.to_en(html, site_path, title, desc)
        out=os.path.join(BASE,"en",rel); os.makedirs(os.path.dirname(out),exist_ok=True)
        open(out,"w",encoding="utf-8").write(en_html)
        new_nl=gen_en.add_hreflang_nl(html, site_path)
        if new_nl!=html: open(src,"w",encoding="utf-8").write(new_nl)
        n+=1
    update_sitemap(rels)
    print(f"build_en: {n} content/bedrijf-paginas -> /en/ + hreflang op NL + sitemap")

if __name__=="__main__":
    main()
