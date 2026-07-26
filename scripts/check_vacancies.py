#!/usr/bin/env python3
"""Dagelijkse vacaturecontrole.

Leest het jobs-data JSON-blok in jobs.html en controleert per vacature of de
officiele bronpagina nog bestaat. Per brontype:

- Workday (myworkdayjobs.com): via het publieke CXS-endpoint van dezelfde
  vacature. Dat endpoint geeft 200 zolang de vacature open is en 404 zodra
  ze gesloten is. De gewone vacaturepagina is een JavaScript-schil en is
  daarom niet bruikbaar voor tekstcontrole.
- Alle overige bronnen: de pagina moet status 200 geven en de checkText
  (of anders de functietitel) moet in de HTML staan.

Na twee opeenvolgende mislukte controles gaat de vacature op inactief;
zodra de bron weer klopt wordt ze automatisch hersteld. De tellerstand per
vacature staat in scripts/vacancy_state.json.
"""
import json, os, re, sys, urllib.error, urllib.request

JOBS_HTML = "jobs.html"
STATE = "scripts/vacancy_state.json"
FAIL_LIMIT = 2
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "*/*",
        "Accept-Language": "en,nl;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return None, str(e)

def adzuna_ids(firm_key, app_id, app_key):
    """Haalt de huidige Adzuna-advertentie-ids op voor een bedrijf (NL)."""
    ids = set()
    for page in (1, 2, 3):
        url = (f"https://api.adzuna.com/v1/api/jobs/nl/search/{page}?app_id={app_id}"
               f"&app_key={app_key}&results_per_page=50&what_phrase={firm_key}"
               f"&content-type=application/json")
        status, body = fetch(url)
        if status != 200:
            continue
        try:
            for r in json.loads(body).get("results", []):
                ids.add(str(r.get("id")))
        except Exception:
            pass
    return ids

def workday_cxs(url):
    """Zet een publieke Workday-vacature-URL om naar het CXS-endpoint."""
    m = re.match(
        r"https://([a-z0-9]+)\.(wd\d+)\.myworkdayjobs\.com/(?:[a-zA-Z]{2}-[a-zA-Z]{2}/)?([^/]+)/job/(.+)",
        url)
    if not m:
        return None
    tenant, dc, site, rest = m.groups()
    return f"https://{tenant}.{dc}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/job/{rest}"

def main():
    html = open(JOBS_HTML, encoding="utf-8").read()
    m = re.search(r'(<script id="jobs-data" type="application/json">)([\s\S]*?)(</script>)', html)
    if not m:
        print("jobs-data blok niet gevonden"); sys.exit(1)
    jobs = json.loads(m.group(2))

    try:
        state = json.load(open(STATE, encoding="utf-8"))
    except Exception:
        state = {}

    cache = {}
    adz_cache = {}
    changed = False
    for job in jobs:
        url, key = job.get("url"), str(job["id"])
        # Adzuna-vacatures: de bronpagina rate-limit (429) bot-verzoeken, dus
        # controleer via de Adzuna-API of de advertentie nog in de resultaten
        # van het bedrijf staat. Zonder API-sleutel slaan we de controle over
        # (de vacature blijft ongewijzigd) zodat een ontbrekende sleutel de
        # Adzuna-vacatures niet ten onrechte op inactief zet.
        if job.get("source") == "adzuna":
            akey = job.get("adzunaKey")
            aid, akk = os.environ.get("ADZUNA_APP_ID"), os.environ.get("ADZUNA_APP_KEY")
            if not (akey and aid and akk):
                print(f"[{job['company']}] {job['title']}: adzuna-controle overgeslagen (geen sleutel)")
                continue
            if akey not in adz_cache:
                adz_cache[akey] = adzuna_ids(akey, aid, akk)
            ok = str(job.get("checkText")) in adz_cache[akey]
            fails = 0 if ok else state.get(key, 0) + 1
            state[key] = fails
            should_be_active = fails < FAIL_LIMIT
            if job.get("active", True) != should_be_active:
                job["active"] = should_be_active; changed = True
                print(f"[{job['company']}] {job['title']}: actief -> {should_be_active} (fails={fails})")
            else:
                print(f"[{job['company']}] {job['title']}: ok={ok} fails={fails}")
            continue
        cxs = workday_cxs(url)
        target = cxs or url
        if target not in cache:
            cache[target] = fetch(target)
        status, body = cache[target]
        if cxs:
            ok = status == 200
        else:
            check = (job.get("checkText") or job["title"]).lower()
            # Sommige bronnen (Avature, SmartRecruiters) zijn JavaScript-schillen
            # waar de titel niet in de ruwe HTML staat, maar de req-id wel in de
            # URL. Een gesloten vacature geeft daar 404, dus de statuscheck vangt
            # de sluiting op; de tekstcheck bevestigt enkel dat de pagina klopt.
            ok = status == 200 and (check in body.lower() or check in url.lower())
        fails = 0 if ok else state.get(key, 0) + 1
        state[key] = fails
        should_be_active = fails < FAIL_LIMIT
        if job.get("active", True) != should_be_active:
            job["active"] = should_be_active
            changed = True
            print(f"[{job['company']}] {job['title']}: actief -> {should_be_active} (fails={fails})")
        else:
            print(f"[{job['company']}] {job['title']}: ok={ok} fails={fails}")

    if changed:
        new = m.group(1) + "\n" + json.dumps(jobs, ensure_ascii=False, indent=2) + "\n" + m.group(3)
        open(JOBS_HTML, "w", encoding="utf-8").write(html[:m.start()] + new + html[m.end():])
    json.dump(state, open(STATE, "w", encoding="utf-8"), indent=2)
    print("klaar; wijzigingen:", changed)

if __name__ == "__main__":
    main()
