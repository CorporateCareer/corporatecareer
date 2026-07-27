# -*- coding: utf-8 -*-
"""Centrale mapping van een vacature naar relevante pijler-/categoriepagina's.

Gebruikt door build_vacature_pages.py om onderaan elke vacature een blok
"Bekijk ook" met interne links te tonen. De koppeling gebruikt de bestaande
categoriedata van de vacature (sector + tags + detail.facts.Praktijk); pas de
tabellen hieronder aan om links toe te voegen of te wijzigen.

Elke pijler is een tuple (url, engelse_anchor, nederlandse_anchor).
"""

# Hoofdpijler per sector (altijd 1 link).
MAIN = {
    "finance":    ("/finance.html", "More finance jobs", "Meer vacatures in finance"),
    "consulting": ("/consulting.html", "More consulting jobs", "Meer vacatures in consulting"),
    "advocatuur": ("/legal.html", "More jobs in law", "Meer vacatures in de advocatuur"),
}

# Vangnet-tweede link (werkgevers-overzicht) als er geen sub-pijler matcht.
EMPLOYERS = {
    "finance":    ("/finance/bedrijven/", "Finance employers in the Netherlands", "Finance-werkgevers in Nederland"),
    "consulting": ("/consulting/bedrijven/", "Consulting firms in the Netherlands", "Consultancybureaus in Nederland"),
    "advocatuur": ("/legal/bedrijven/", "Law firms in the Netherlands", "Advocatenkantoren in Nederland"),
}

# Sub-pijlers per sector: (trefwoorden, url, en_anchor, nl_anchor).
# Trefwoorden worden (kleine letters) als substring gezocht in tags + praktijk + titel.
SUB = {
    "finance": [
        (("transaction service", "deals", "deal advisory", "due diligence"), "/finance/transaction-services/", "Careers in transaction services", "Carrières in transaction services"),
        (("corporate finance", "corporate origination"), "/finance/corporate-finance/", "Careers in corporate finance", "Carrières in corporate finance"),
        (("m&a", "mergers", "technology strategy & m&a"), "/finance/ma/", "Careers in M&A", "Carrières in M&A"),
        (("private equity", "private capital"), "/finance/private-equity/", "Careers in private equity", "Carrières in private equity"),
        (("investment banking",), "/finance/investment-banking/", "Careers in investment banking", "Carrières in investment banking"),
        (("debt capital markets", "debt advisory"), "/finance/debt-advisory/", "Careers in debt advisory", "Carrières in debt advisory"),
        (("trading", "global markets", "market making"), "/finance/trading/", "Careers in trading", "Carrières in trading"),
        (("valuation",), "/finance/valuation/", "Careers in valuation", "Carrières in valuation"),
        (("asset management", "robeco"), "/finance/asset-management/", "Careers in asset management", "Carrières in asset management"),
        (("risk", "credit"), "/finance/risk-management/", "Careers in risk management", "Carrières in risk management"),
        (("equity research", "quant"), "/finance/equity-research/", "Careers in equity research", "Carrières in equity research"),
        (("venture capital",), "/finance/venture-capital/", "Careers in venture capital", "Carrières in venture capital"),
        (("corporate development",), "/finance/corporate-development/", "Careers in corporate development", "Carrières in corporate development"),
        (("real estate",), "/finance/real-estate-finance/", "Careers in real estate finance", "Carrières in real estate finance"),
        (("wealth", "private banking"), "/finance/wealth-management/", "Careers in wealth management", "Carrières in wealth management"),
    ],
    "consulting": [
        (("strategy",), "/consulting/strategy/", "Careers in strategy consulting", "Carrières in strategy consulting"),
        (("data", "analytics"), "/consulting/data-analytics/", "Careers in data & analytics", "Carrières in data & analytics"),
        (("technology", "tech", "architect", "digital", " ai", "ai ", "payments"), "/consulting/technology-digital/", "Careers in technology consulting", "Carrières in technology consulting"),
        (("operations", "project", "programme", "program", "aviation", "luchtvaart", "defen"), "/consulting/operations/", "Careers in operations consulting", "Carrières in operations consulting"),
        (("people", "change", "organi", "verandering"), "/consulting/people-organisation/", "Careers in people & organisation", "Carrières in people & organisation"),
        (("sustainab", "esg", "duurzaam", "chemie", "chemicals"), "/consulting/sustainability/", "Careers in sustainability consulting", "Carrières in sustainability consulting"),
        (("m&a", "transaction", "deal", "valuation", "transfer pricing", "due diligence", "corporate finance"), "/consulting/financial-deal-advisory/", "Careers in financial & deal advisory", "Carrières in financial & deal advisory"),
        (("risk", "regulator", "complian", "forensic", "security", "assurance", "accounting", "reporting"), "/consulting/risk-regulatory/", "Careers in risk & regulatory", "Carrières in risk & regulatory"),
    ],
    "advocatuur": [
        (("corporate/m&a", "corporate m&a", "m&a"), "/legal/corporate-ma/", "Careers in corporate/M&A law", "Carrières in corporate/M&A"),
        (("dispute", "arbitr", "geschil"), "/legal/dispute-resolution/", "Careers in dispute resolution", "Carrières in dispute resolution"),
        (("banking & finance", "banking and finance"), "/legal/banking-finance/", "Careers in banking & finance law", "Carrières in banking & finance"),
        (("employment", "arbeidsrecht", "pension", "pensioen"), "/legal/employment-labour-pensions/", "Careers in employment law", "Carrières in arbeidsrecht"),
        (("intellectual", "octrooi", "ip "), "/legal/intellectual-property/", "Careers in IP law", "Carrières in intellectueel eigendom"),
        (("antitrust", "competition", "mededing"), "/legal/antitrust-competition-trade/", "Careers in competition law", "Carrières in mededingingsrecht"),
        (("administrative", "bestuursrecht"), "/legal/administrative-law/", "Careers in administrative law", "Carrières in bestuursrecht"),
        (("tax", "fiscaal"), "/legal/tax/", "Careers in tax law", "Carrières in fiscaal recht"),
        (("real estate", "vastgoed"), "/legal/real-estate/", "Careers in real estate law", "Carrières in vastgoedrecht"),
        (("restructuring", "insolven", "reorganis", "herstructurering"), "/legal/restructuring-insolvency/", "Careers in restructuring & insolvency", "Carrières in herstructurering & insolventie"),
        (("commercial", "contract"), "/legal/commercial/", "Careers in commercial law", "Carrières in commercieel recht"),
        (("esg",), "/legal/esg/", "Careers in ESG law", "Carrières in ESG"),
        (("digital regulation", "ai & digital", "digitale regulering"), "/legal/artificial-intelligence-digital-regulation/", "Careers in AI & digital regulation", "Carrières in AI & digitale regulering"),
        (("procurement", "aanbesteding"), "/legal/public-procurement/", "Careers in public procurement", "Carrières in aanbestedingsrecht"),
    ],
}

# Thematische/locatiepagina's per sector (maximaal 1 extra link).
THEMATIC = {
    "finance": [
        (("private equity", "private capital"), "/private-equity-nederland.html", "Private equity in the Netherlands", "Private equity in Nederland"),
        (("investment banking",), "/investment-banking-nederland.html", "Investment banking in the Netherlands", "Investment banking in Nederland"),
        (("venture capital",), "/venture-capital-nederland.html", "Venture capital in the Netherlands", "Venture capital in Nederland"),
        (("asset management", "robeco"), "/asset-management-nederland.html", "Asset management in the Netherlands", "Asset management in Nederland"),
        (("corporate banking",), "/corporate-banking-amsterdam.html", "Corporate banking in Amsterdam", "Corporate banking in Amsterdam"),
        (("corporate finance",), "/corporate-finance-amsterdam.html", "Corporate finance in Amsterdam", "Corporate finance in Amsterdam"),
    ],
    "consulting": [
        (("consult", "strategy", "management"), "/management-consulting-nederland.html", "Management consulting in the Netherlands", "Management consulting in Nederland"),
    ],
    "advocatuur": [
        (("notari",), "/notariaat-stage-amsterdam.html", "Notarial traineeships", "Notariaat-stages"),
        (("fiscaal", "tax"), "/fiscaal-recht-amsterdam.html", "Tax law in Amsterdam", "Fiscaal recht in Amsterdam"),
        (("trainee", "advocaat", "traineeship", "stage"), "/traineeship-advocatuur.html", "Law firm traineeships", "Traineeships in de advocatuur"),
    ],
}


def _signals(job):
    parts = [str(t).lower() for t in (job.get("tags") or [])]
    pr = (job.get("detail", {}).get("facts", {}).get("nl", {}) or {}).get("Praktijk", "")
    if pr:
        parts.append(str(pr).lower())
    parts.append((job.get("title") or "").lower())
    return " | ".join(parts)


def pillars_for(job):
    """Geeft 2 tot 4 (url, en_anchor, nl_anchor)-tuples, hoofdpijler eerst,
    gededupliceerd op url. Nooit meer dan 4."""
    sector = job.get("sector")
    text = _signals(job)
    out, seen = [], set()

    def add(entry):
        if entry and entry[0] not in seen:
            out.append(entry)
            seen.add(entry[0])

    add(MAIN.get(sector))
    subs = 0
    for kws, url, en, nl in SUB.get(sector, []):
        if any(k in text for k in kws):
            add((url, en, nl))
            subs += 1
            if subs >= 2:
                break
    for kws, url, en, nl in THEMATIC.get(sector, []):
        if len(out) >= 4:
            break
        if any(k in text for k in kws):
            add((url, en, nl))
            break
    if len(out) < 2:
        add(EMPLOYERS.get(sector))
    return out[:4]
