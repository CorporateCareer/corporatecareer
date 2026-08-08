# -*- coding: utf-8 -*-
"""Haalt per vacature de gegevens op bij het wervingssysteem van het kantoor.

Wat hiermee gebeurt, staat los van elkaar en dat is bewust:

1. De kerngegevens komen uit de gestructureerde velden van het systeem:
   contractvorm, uren, ervarings- en opleidingsniveau, werkvorm en het
   praktijkgebied. Dat zijn losse waarden, geen tekst, dus die kan de site in
   het Nederlands en in het Engels zelf verwoorden. Beide taalversies kloppen
   daardoor, en er is geen auteursrechtvraag.

2. Het citaat is een begrensd stuk uit de tekst die het kantoor zelf schreef,
   met bronvermelding. Het wordt kort gehouden: hooguit drie alinea's en
   MAX_QUOTE tekens. De volledige tekst blijft bij het kantoor, waar de knop
   op de pagina al naartoe wijst.

Het citaat draagt de taal waarin het kantoor schreef. Die taal wordt bepaald
en meegegeven, zodat de vacaturepagina het citaat alleen laat zien op de
taalversie waar het thuishoort. Op de andere taalversie komt een verwijzing,
zodat daar geen blok in een vreemde taal staat.
"""
import html as _html
import json, os, re, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ats_detail_cache.json")

MAX_QUOTE = 480          # tekens
MAX_PARAGRAPHS = 3
MIN_PARAGRAPH = 60       # kortere regels zijn kopjes of kruimels

PLATFORMS = [
    ("recruitee", r"https?://([a-z0-9-]+)\.recruitee\.com"),
    ("greenhouse", r"greenhouse\.io/([a-z0-9_-]+)/jobs/(\d+)"),
    ("smartrecruiters", r"jobs\.smartrecruiters\.com/([A-Za-z0-9_-]+)/(\d+)"),
    ("workday", r"https?://([a-z0-9-]+)\.(wd\d+)\.myworkdayjobs\.com/([A-Za-z0-9_-]+)(/job/.+)$"),
]

# ── taalbepaling ─────────────────────────────────────────────────────────────
NL_WORDS = set("de het een en van voor met je jij we wij ons onze bij aan op in "
               "die dat als om te zijn wordt worden heb hebt heeft niet ook naar "
               "waar wat hoe zoals binnen samen werk werken jouw uur per".split())
EN_WORDS = set("the a an and of for with you your we our at on in that as to be "
               "is are will have has not also into where what how such within "
               "together work working role team per".split())


def detect_lang(text):
    woorden = re.findall(r"[a-zA-Zàâäéèêëïîôöùûüç']+", (text or "").lower())
    if len(woorden) < 20:
        return None
    nl = sum(1 for w in woorden if w in NL_WORDS)
    en = sum(1 for w in woorden if w in EN_WORDS)
    if nl == en:
        return None
    return "nl" if nl > en else "en"


# ── tekstbewerking ───────────────────────────────────────────────────────────
def paragraphs(raw):
    """De alinea's uit de aangeleverde HTML, ontdaan van opmaak."""
    if not raw:
        return []
    # Sommige systemen leveren de HTML dubbel ontsnapt aan, waardoor er anders
    # &amp; in de lopende tekst blijft staan. Net zolang terugdraaien tot er
    # niets meer verandert.
    s = raw
    for _ in range(3):
        t = _html.unescape(s)
        if t == s:
            break
        s = t
    s = re.sub(r"<(script|style)[\s\S]*?</\1>", " ", s, flags=re.I)
    s = re.sub(r"<\s*(br|/p|/div|/li|/h[1-6]|/tr)\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("\xa0", " ")
    out = []
    for regel in s.split("\n"):
        regel = re.sub(r"\s+", " ", regel).strip(" •-\t")
        if regel:
            out.append(regel)
    return out


def is_prose(p):
    """Of een regel lopende tekst is en geen gegevensbalk.

    Veel kantoren zetten bovenaan de vacature een regel als
    "31-38.75 uur per week | Utrecht | Hybride | € 5.086- € 8.376". Die is lang
    genoeg om door de lengtegrens te komen en verschilt per vacature, dus de
    standaardtekstfilter vangt hem ook niet. Kenmerkend is dat er geen zin in
    staat: geen punt, vraagteken of uitroepteken, en vaak scheidingstekens.
    """
    if p.count("|") >= 2 or p.count("·") >= 2:
        return False
    return any(t in p for t in ".?!")


def quote_from(raw, boilerplate=()):
    """Een begrensd citaat: hooguit drie alinea's en MAX_QUOTE tekens.

    Regels korter dan MIN_PARAGRAPH worden overgeslagen. Dat zijn kopjes en
    de balk met uren en plaats die veel kantoren bovenaan zetten; die zeggen
    niets en zouden het citaat opvullen.

    boilerplate bevat alinea's die bij meerdere vacatures van hetzelfde
    kantoor voorkomen. Dat is het bedrijfsverhaal dat vooraan de tekst staat,
    en dat is precies wat het citaat niet moet zijn: twee vacatures van
    Roland Berger leverden anders woord voor woord hetzelfde op.
    """
    gekozen, lengte = [], 0
    for p in paragraphs(raw):
        if len(p) < MIN_PARAGRAPH or p in boilerplate or not is_prose(p):
            continue
        if lengte + len(p) > MAX_QUOTE and gekozen:
            break
        gekozen.append(p)
        lengte += len(p)
        if len(gekozen) >= MAX_PARAGRAPHS or lengte >= MAX_QUOTE:
            break
    if not gekozen:
        return ""
    tekst = " ".join(gekozen)
    if len(tekst) > MAX_QUOTE:
        # Op een zinseinde afkappen, anders op een spatie.
        knip = tekst.rfind(". ", 0, MAX_QUOTE)
        tekst = (tekst[:knip + 1] if knip > MAX_QUOTE // 2 else tekst[:MAX_QUOTE].rsplit(" ", 1)[0] + "...")
    return tekst.strip()


# ── ophalen per systeem ──────────────────────────────────────────────────────
_LAST = {}
PAUSE = 1.2       # seconden tussen twee verzoeken aan dezelfde host
TRIES = 3


def _curl(url, post=None, timeout=25):
    """Een verzoek, met rust tussen opeenvolgende verzoeken aan dezelfde host.

    Zonder pauze weigert Workday na enkele tientallen verzoeken alles, ook de
    vacaturelijst. Bij een kantoor met veertig vacatures loop je daar zo
    tegenaan, en dan lijkt het alsof het kantoor niets meer aanlevert.
    """
    host = re.sub(r"^https?://([^/]+).*$", r"\1", url)
    wacht = PAUSE - (time.time() - _LAST.get(host, 0))
    if wacht > 0:
        time.sleep(wacht)
    # -L: Workday antwoordt met een 303 naar de eigen onderhoudspagina zodra
    # het systeem er even uit ligt. Zonder omleidingen te volgen komt daar een
    # leeg antwoord uit en lijkt het alsof het kantoor niets aanlevert.
    cmd = ["curl", "-sSL", "-m", str(timeout), url, "-H", "Accept: application/json",
           "-H", "User-Agent: Mozilla/5.0 (compatible; CorporateCareer/1.0)"]
    if post is not None:
        cmd += ["-X", "POST", "-H", "Content-Type: application/json", "-d", json.dumps(post)]
    for poging in range(TRIES):
        try:
            uit = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10).stdout
            _LAST[host] = time.time()
            if uit.strip():
                return json.loads(uit)
        except Exception:
            _LAST[host] = time.time()
        if poging < TRIES - 1:
            time.sleep(2 * (poging + 1))
    return None


HOURS = re.compile(r"^\s*(\d{1,2})\s*[-tot/]+\s*(\d{1,2}(?:[.,]\d+)?)\s*uur", re.I)

EMPLOY = {
    "fulltime_permanent": ("Permanent, full-time", "Vast, voltijd"),
    "parttime_permanent": ("Permanent, part-time", "Vast, deeltijd"),
    "temporary": ("Temporary", "Tijdelijk"),
    "internship": ("Internship", "Stage"),
    "contract": ("Contract", "Contract"),
    "freelance": ("Freelance", "Freelance"),
    "permanent": ("Permanent", "Vast"),
    "full_time": ("Full-time", "Voltijd"),
    "part_time": ("Part-time", "Deeltijd"),
}
EXPERIENCE = {
    "student": ("Student", "Student"), "entry_level": ("Entry level", "Starter"),
    "junior": ("Junior", "Junior"), "mid_level": ("Mid level", "Medior"),
    "medior": ("Medior", "Medior"), "senior": ("Senior", "Senior"),
    "senior_executive": ("Senior", "Senior"), "executive": ("Executive", "Directie"),
    "associate": ("Associate", "Associate"), "internship": ("Internship", "Stage"),
    "experienced": ("Experienced", "Ervaren"), "director": ("Director", "Directie"),
}
EDUCATION = {
    "high_school": ("Secondary school", "Middelbare school"),
    "vocational": ("Vocational", "Mbo"),
    "professional_bachelor": ("Bachelor (applied sciences)", "Hbo-bachelor"),
    "bachelor_degree": ("Bachelor", "Bachelor"),
    "master_degree": ("Master", "Master"),
    "doctorate_degree": ("Doctorate", "Doctoraat"),
}


def _label(tabel, code):
    if not code:
        return None
    return tabel.get(str(code).strip().lower())


def _workform(o):
    if o.get("remote") and not o.get("on_site"):
        return ("Remote", "Op afstand")
    if o.get("hybrid"):
        return ("Hybrid", "Hybride")
    if o.get("on_site"):
        return ("On site", "Op kantoor")
    return None


def from_recruitee(code, url):
    d = _curl(f"https://{code}.recruitee.com/api/offers/") or {}
    doel = url.split("?")[0].rstrip("/")
    for o in d.get("offers", []):
        if (o.get("careers_url") or "").split("?")[0].rstrip("/") != doel:
            continue
        tekst = (o.get("description") or "") + "\n" + (o.get("requirements") or "")
        feiten = {}
        if o.get("min_hours") or o.get("max_hours"):
            lo, hi = o.get("min_hours"), o.get("max_hours")
            bereik = bool(lo and hi and lo != hi)
            en = f"{lo} to {hi}" if bereik else str(hi or lo)
            nl = f"{lo} tot {hi}" if bereik else str(hi or lo)
            feiten["hours"] = (f"{en} hours per week", f"{nl} uur per week")
        for sleutel, tabel, veld in (("contract", EMPLOY, "employment_type_code"),
                                     ("level", EXPERIENCE, "experience_code"),
                                     ("education", EDUCATION, "education_code")):
            lab = _label(tabel, o.get(veld))
            if lab:
                feiten[sleutel] = lab
        wf = _workform(o)
        if wf:
            feiten["workform"] = wf
        afd = (o.get("department") or "").strip()
        if afd:
            feiten["department"] = (afd, afd)
        return {"raw": tekst, "lang": detect_lang(" ".join(paragraphs(tekst))), "facts": feiten}
    return None


def from_greenhouse(code, jid, url):
    j = _curl(f"https://boards-api.greenhouse.io/v1/boards/{code}/jobs/{jid}") or {}
    tekst = j.get("content") or ""
    feiten = {}
    afd = [d.get("name") for d in (j.get("departments") or []) if d.get("name")]
    if afd:
        feiten["department"] = (afd[0].strip(), afd[0].strip())
    taal = (j.get("language") or {})
    taalcode = taal.get("code") if isinstance(taal, dict) else None
    return {"raw": tekst,
            "lang": (taalcode[:2] if taalcode else None) or detect_lang(" ".join(paragraphs(tekst))),
            "facts": feiten}


def from_smartrecruiters(code, pid, url):
    p = _curl(f"https://api.smartrecruiters.com/v1/companies/{code}/postings/{pid}") or {}
    secties = ((p.get("jobAd") or {}).get("sections") or {})
    tekst = "\n".join((secties.get(k) or {}).get("text") or "" for k in ("jobDescription", "qualifications"))
    feiten = {}
    for sleutel, veld in (("contract", "typeOfEmployment"), ("level", "experienceLevel")):
        w = p.get(veld) or {}
        # Alleen codes die in de tabel staan. Een onbekend label als
        # "Mid-Senior Level" is Engelse systeemtekst en hoort niet op de
        # Nederlandse pagina, dus dat veld blijft dan liever leeg.
        lab = _label(EMPLOY if sleutel == "contract" else EXPERIENCE, w.get("id"))
        if lab:
            feiten[sleutel] = lab
    fn = (p.get("function") or {}).get("label")
    if fn:
        feiten["department"] = (fn, fn)
    taal = (p.get("language") or {}).get("code")
    return {"raw": tekst,
            "lang": (taal[:2] if taal else None) or detect_lang(" ".join(paragraphs(tekst))),
            "facts": feiten}


def from_workday(tenant, dc, site, path, url):
    d = _curl(f"https://{tenant}.{dc}.myworkdayjobs.com/wday/cxs/{tenant}/{site}{path}") or {}
    info = d.get("jobPostingInfo") or {}
    tekst = info.get("jobDescription") or ""
    feiten = {}
    tt = info.get("timeType")
    lab = _label(EMPLOY, str(tt).replace(" ", "_")) if tt else None
    if lab:
        feiten["contract"] = lab
    return {"raw": tekst, "lang": detect_lang(" ".join(paragraphs(tekst))), "facts": feiten}


def for_job(url):
    """Kerngegevens en citaat voor een vacature, of None."""
    if not url:
        return None
    for kind, patroon in PLATFORMS:
        m = re.search(patroon, url)
        if not m:
            continue
        g = m.groups()
        try:
            if kind == "recruitee":
                return from_recruitee(g[0], url)
            if kind == "greenhouse":
                return from_greenhouse(g[0], g[1], url)
            if kind == "smartrecruiters":
                return from_smartrecruiters(g[0], g[1], url)
            if kind == "workday":
                return from_workday(g[0], g[1], g[2], g[3], url)
        except Exception:
            return None
    return None


def enrich(jobs, log=None):
    """Kerngegevens en citaat voor een lijst vacatures, per kantoor verwerkt.

    Per kantoor wordt eerst opgehaald en daarna bepaald welke alinea's bij
    meerdere vacatures voorkomen. Dat is het bedrijfsverhaal, en dat wordt uit
    het citaat gelaten. Het kan alleen zo: of een alinea standaardtekst is,
    blijkt pas als je de andere vacatures van hetzelfde kantoor ernaast legt.
    """
    per_kantoor = {}
    for j in jobs:
        per_kantoor.setdefault(j.get("company", ""), []).append(j)

    uit = {}
    for kantoor, lijst in sorted(per_kantoor.items()):
        ruw = {}
        for j in lijst:
            r = for_job(j.get("url"))
            if r:
                ruw[j["id"]] = r
        if not ruw:
            continue
        # Alinea's die bij meer dan een vacature van dit kantoor voorkomen.
        telling = {}
        for r in ruw.values():
            for p in set(paragraphs(r.get("raw"))):
                if len(p) >= MIN_PARAGRAPH:
                    telling[p] = telling.get(p, 0) + 1
        standaard = {p for p, n in telling.items() if n > 1} if len(ruw) > 1 else set()
        for jid, r in ruw.items():
            citaat = quote_from(r.get("raw"), standaard)
            uit[jid] = {"quote": citaat, "lang": r.get("lang"), "facts": r.get("facts") or {}}
        if log:
            met = sum(1 for v in uit.values() if v["quote"])
            log(f"  {kantoor:28} {len(ruw):4} opgehaald, {len(standaard):3} standaardalinea's")
    return uit


def load_cache():
    try:
        return json.load(open(CACHE, encoding="utf-8"))
    except Exception:
        return {}


def save_cache(c):
    json.dump(c, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
