#!/usr/bin/env python3
"""Haalt actuele vacatures op via de Adzuna-API voor bedrijven zonder eigen
doorzoekbare feed. Alleen eigen-gebrande vacatures (werkgever == het bedrijf),
zonder facilitaire/uitzend-/eventruis. Omschrijvingen zijn eigen, algemene
teksten. Elke vacature krijgt source=adzuna + adzunaKey zodat de dagelijkse
controle ze via de Adzuna-API verifieert. Sleutel via ADZUNA_APP_ID/KEY (env).
"""
import os, re, json, subprocess, unicodedata

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS = os.path.join(BASE, "jobs.html")
AID, AK = os.environ.get("ADZUNA_APP_ID"), os.environ.get("ADZUNA_APP_KEY")

# company (== profielfilter) : (adzunaKey, firmSite, sector, logo, initials)
FIRMS = {
 "KPMG Netherlands": ("kpmg", "https://www.kpmg.nl", "finance", "/img/logos/kpmg-netherlands.svg", "KP"),
 "Accenture":        ("accenture", "https://www.accenture.com", "consulting", "/img/logos/accenture.svg", "Ac"),
 "Robeco":           ("robeco", "https://www.robeco.com", "finance", "/img/logos/robeco.svg", "Ro"),
 "NIBC Bank":        ("nibc", "https://www.nibc.com", "finance", "/img/logos/nibc-bank.svg", "NI"),
}
BLURB = {
 "KPMG Netherlands": {"en":"KPMG is one of the Big Four firms, providing audit, tax and advisory services, with offices across the Netherlands.",
                      "nl":"KPMG is een van de Big Four en levert audit, fiscale en adviesdiensten, met kantoren door heel Nederland."},
 "Accenture": {"en":"Accenture is a global professional services firm specialising in technology, strategy and consulting, with a large practice in the Netherlands.",
               "nl":"Accenture is een wereldwijd professioneel dienstverlener gespecialiseerd in technologie, strategie en consulting, met een grote praktijk in Nederland."},
 "Robeco": {"en":"Robeco is an international asset manager based in Rotterdam, known for its research-driven and sustainable investing.",
            "nl":"Robeco is een internationale vermogensbeheerder uit Rotterdam, bekend om onderzoeksgedreven en duurzaam beleggen."},
 "NIBC Bank": {"en":"NIBC is a Dutch bank focused on corporate and retail clients, with its head office in The Hague.",
               "nl":"NIBC is een Nederlandse bank gericht op zakelijke en particuliere clienten, met het hoofdkantoor in Den Haag."},
}
EXC = ("schoonmaak","cleaning","kok","afwasser","catering","beveilig","security","facilit","vakantiewerk",
       "hospitality","receptie","chauffeur","magazijn","monteur","business course","kennismaking","zomerse",
       "open sollicitatie","event","webinar","insight","recruitment day","meet ","meet&","meet-","schoonmaker")
INC = {"finance":("analyst","associate","trader","quant","banker","investment","finance","risk","controller","portfolio","wealth","advisor","adviseur","credit","research","developer","engineer","graduate","intern","stage","manager","consult","actuar","accountant","audit","tax","valuation","deal","corporate","data","scientist"),
       "consulting":("consult","advis","adviseur","analyst","architect","manager","strateg","transformation","lead","principal","associate","engagement","data","expert","technology","digital","engineer","intern","stage")}
DOES = {"finance":{"en":["Work on analyses, models or transactions for the business","Support decision-making with data and clear recommendations","Collaborate in teams to deliver results"],
                   "nl":["Werk aan analyses, modellen of transacties voor de business","Ondersteun besluitvorming met data en heldere aanbevelingen","Werk samen in teams om resultaten te realiseren"]},
        "consulting":{"en":["Advise clients on complex challenges and transformation","Analyse issues, processes and data to shape recommendations","Work in project teams to deliver results at the client"],
                      "nl":["Adviseer opdrachtgevers over complexe vraagstukken en transformatie","Analyseer vraagstukken, processen en data om aanbevelingen te onderbouwen","Werk in projectteams om resultaten bij de opdrachtgever te realiseren"]}}
BRINGS = {"en":["A relevant degree and strong analytical skills","Attention to detail and a structured way of working","Excellent Dutch and/or English"],
          "nl":["Een relevante opleiding en sterke analytische vaardigheden","Oog voor detail en een gestructureerde werkwijze","Uitstekend Nederlands en/of Engels"]}

def slugify(s):
    s=unicodedata.normalize("NFKD",s).encode("ascii","ignore").decode()
    return re.sub(r"-+","-",re.sub(r"[^a-zA-Z0-9]+","-",s).strip("-").lower())
def curl(url):
    return subprocess.run(["curl","-sS","-m","20",url],capture_output=True,text=True).stdout
def city_of(loc):
    loc=(loc or "").split(",")[0].strip()
    return "Netherlands" if loc.lower() in ("nederland","netherlands","") else loc

def fetch_firm(firm_key, cap=8):
    out=[]
    for page in (1,2,3):
        url=(f"https://api.adzuna.com/v1/api/jobs/nl/search/{page}?app_id={AID}&app_key={AK}"
             f"&results_per_page=50&what_phrase={firm_key}&content-type=application/json")
        try: res=json.loads(curl(url)).get("results",[])
        except: res=[]
        for r in res:
            if len(out)>=cap: break
            emp=((r.get("company",{}) or {}).get("display_name","") or "").lower()
            if firm_key not in emp: continue
            out.append(r)
    return out

def main():
    if not (AID and AK):
        print("Geen ADZUNA_APP_ID/KEY in de omgeving; sla over."); return
    html=open(JOBS,encoding="utf-8").read()
    m=re.search(r'(<script id="jobs-data" type="application/json">)([\s\S]*?)(</script>)',html)
    jobs=json.loads(m.group(2))
    existing={str(j.get("checkText")) for j in jobs}
    seen_slug={j.get("slug") for j in jobs}
    maxid=max(j["id"] for j in jobs)
    added=[]
    for company,(fkey,site,sector,logo,initials) in FIRMS.items():
        n=0
        for r in fetch_firm(fkey):
            if n>=8: break
            title=(r.get("title","") or "").strip()
            tl=title.lower()
            if any(x in tl for x in EXC): continue
            if not any(x in tl for x in INC[sector]): continue
            aid_id=str(r.get("id"))
            if aid_id in existing: continue
            # Strip de tracking-querystring: Adzuna zet de app_id in utm_source,
            # die mag niet in de publieke repo terechtkomen. De ad-id blijft in
            # het pad (.../details/<id>), dus de controle blijft werken.
            url=r.get("redirect_url","").split("?")[0]
            if not url: continue
            city=city_of((r.get("location",{}) or {}).get("display_name",""))
            typ="stage" if any(x in tl for x in ("stage","intern","werkstudent","afstudeer")) else "graduate"
            type_en="Internship" if typ=="stage" else "Permanent"; type_nl="Stage" if typ=="stage" else "Vaste functie"
            sec_en="Finance" if sector=="finance" else "Consulting"; sec_nl=sec_en if sector=="finance" else "Consulting"
            intro={"en":f"{company} is looking for a {title} in {city}. Below you can read what the role involves and what you bring; you apply directly via the official job page.",
                   "nl":f"{company} zoekt een {title} in {city}. Hieronder lees je wat de rol inhoudt en wat je meebrengt; solliciteren doe je rechtstreeks via de officiele vacaturepagina."}
            desc={"en":f"{company} has an open position for {title} in {city}. Read the full job description and apply via the official job page.",
                  "nl":f"{company} heeft een openstaande vacature voor {title} in {city}. Bekijk de volledige functieomschrijving en solliciteer via de officiele vacaturepagina."}
            facts={"en":{"Location":f"{city}, Netherlands","Sector":sec_en,"Type":type_en,"Level":"Various","Practice":sec_en},
                   "nl":{"Locatie":f"{city}, Nederland","Sector":sec_nl,"Type":type_nl,"Niveau":"Divers","Praktijk":sec_nl}}
            maxid+=1
            slug=slugify(f"{company}-{title}"); base=slug; i=2
            while slug in seen_slug: slug=f"{base}-{i}"; i+=1
            seen_slug.add(slug); existing.add(aid_id)
            e={"title":title,"company":company,"sector":sector,"type":typ,"location":city,"url":url,
               "checkText":aid_id,"tags":[sec_en, company.split()[0]],"id":maxid,"featured":False,"active":True,
               "initials":initials,"color":"#0f2540","salary":"","daysAgo":None,"description":desc,"slug":slug,"logo":logo,
               "source":"adzuna","adzunaKey":fkey,
               "detail":{"firmBlurb":BLURB[company],"firmSite":site,"intro":intro,"does":DOES[sector],"brings":BRINGS,"facts":facts}}
            jobs.append(e); added.append(e); n+=1
        print(f"{company}: +{n}")
    open(JOBS,"w",encoding="utf-8").write(html[:m.start()]+m.group(1)+"\n"+json.dumps(jobs,ensure_ascii=False,indent=2)+"\n"+m.group(3)+html[m.end():])
    print("TOTAL adzuna added:",len(added))

if __name__=="__main__":
    main()
