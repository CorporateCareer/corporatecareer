# -*- coding: utf-8 -*-
"""Meldt vacatures aan en af bij de Google Indexing API.

Google heeft een aparte API die alleen werkt voor JobPosting en live-uitzendingen.
Die haalt een pagina meestal binnen uren op in plaats van weken. Dat is precies
wat deze site nodig heeft: de structuurdata is geldig (de live test in Search
Console bevestigt "1 valid item detected"), maar Google kwam er simpelweg niet
aan toe. Van 1.580 pagina's met een geldige JobPosting waren er negen verwerkt.

Twee soorten berichten:

    URL_UPDATED   nieuwe of gewijzigde vacature
    URL_DELETED   vacature staat niet meer open

Dat tweede is de helft van de winst: zo weet Google meteen dat een vacature
dicht is, in plaats van dat hij het weken later zelf ontdekt.

Alleen de Nederlandse pagina's worden gemeld. De Engelse variant vindt Google
via de hreflang, en het dagquotum is beperkt; de Nederlandse pagina's leverden
in de meting van augustus per pagina bijna vier keer zoveel kliks op.

Wat er al gemeld is staat in scripts/indexing_state.json, zodat een wekelijkse
run alleen de wijzigingen doorgeeft en het quotum niet verbrandt aan pagina's
die Google allang kent.

Nodig: het secret GOOGLE_INDEXING_KEY met de JSON-sleutel van een
serviceaccount dat in Search Console als eigenaar staat. Ontbreekt dat, dan
slaat het script zichzelf over.
"""
import json, os, re, sys, time
import urllib.request, urllib.error

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS = os.path.join(BASE, "jobs.html")
STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "indexing_state.json")
SITE = "https://corporatecareer.nl"
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"

# Het standaardquotum is 200 per dag. We laten marge, want een mislukte melding
# telt ook mee en we willen niet halverwege tegen de limiet aanlopen.
PER_RUN = 180


def token(sleutel):
    """Toegangstoken via het serviceaccount."""
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request
    creds = service_account.Credentials.from_service_account_info(
        sleutel, scopes=["https://www.googleapis.com/auth/indexing"])
    creds.refresh(Request())
    return creds.token


def meld(url, soort, tok):
    """Een URL aan- of afmelden. Geeft terug of het lukte, plus de reden."""
    body = json.dumps({"url": url, "type": soort}).encode()
    req = urllib.request.Request(ENDPOINT, data=body, method="POST", headers={
        "Content-Type": "application/json", "Authorization": f"Bearer {tok}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            r.read()
        return True, ""
    except urllib.error.HTTPError as e:
        rauw = e.read().decode("utf-8", "replace")[:200]
        return False, f"{e.code} {rauw}"
    except Exception as e:
        return False, str(e)[:120]


def laad_state():
    try:
        return json.load(open(STATE, encoding="utf-8"))
    except Exception:
        return {}


def main():
    ruw = os.environ.get("GOOGLE_INDEXING_KEY", "").strip()
    if not ruw:
        print("GOOGLE_INDEXING_KEY ontbreekt; overgeslagen. De site verandert "
              "hier niet van, alleen Google hoort het later.")
        return 0
    try:
        sleutel = json.loads(ruw)
    except Exception:
        print("::error::GOOGLE_INDEXING_KEY is geen geldige JSON")
        return 1

    html = open(JOBS, encoding="utf-8").read()
    jobs = json.loads(re.search(
        r'<script id="jobs-data" type="application/json">([\s\S]*?)</script>', html).group(1))
    state = laad_state()

    # Wat moet er gemeld worden, en in welke volgorde. Afmeldingen eerst: die
    # zijn er weinig en ze zijn het meest tijdgevoelig, want een gesloten
    # vacature die in Google blijft staan stuurt mensen naar een dood spoor.
    af, aan = [], []
    for j in jobs:
        slug = j.get("slug")
        if not slug:
            continue
        url = f"{SITE}/vacatures/{slug}.html"
        dicht = j.get("active") is False
        was = state.get(url, {}).get("soort")
        if dicht and was != "URL_DELETED" and was is not None:
            # Alleen afmelden wat we ooit hebben aangemeld.
            af.append(url)
        elif not dicht and was != "URL_UPDATED":
            aan.append(url)

    todo = [(u, "URL_DELETED") for u in af] + [(u, "URL_UPDATED") for u in aan]
    print(f"{len(af)} af te melden, {len(aan)} aan te melden, quotum {PER_RUN} per run")
    if not todo:
        print("niets te melden")
        return 0
    if len(todo) > PER_RUN:
        print(f"meer dan het quotum; de rest volgt bij de volgende run")
        todo = todo[:PER_RUN]

    tok = token(sleutel)
    gelukt = mislukt = 0
    for url, soort in todo:
        ok, reden = meld(url, soort, tok)
        if ok:
            state[url] = {"soort": soort, "op": time.strftime("%Y-%m-%d")}
            gelukt += 1
        else:
            mislukt += 1
            if mislukt <= 3:
                print(f"  mislukt: {url.split('/')[-1][:50]} -> {reden}")
            if "429" in reden or "RESOURCE_EXHAUSTED" in reden:
                print("  quotum op; de rest volgt bij de volgende run")
                break
        time.sleep(0.3)

    json.dump(state, open(STATE, "w", encoding="utf-8"), indent=1, sort_keys=True)
    print(f"\n{gelukt} gemeld, {mislukt} mislukt, {len(state)} URL's in totaal bekend")
    # Een mislukking mag de run niet omvergooien: de site is dan gewoon
    # bijgewerkt, Google hoort het alleen later.
    return 0


if __name__ == "__main__":
    sys.exit(main())
