# -*- coding: utf-8 -*-
"""Geeft de Engelse praktijkgebiedpagina's een titel die zegt waar ze over gaan.

Bij de vertaling viel "in Nederland" uit de titel. De Engelse pagina's heetten
daardoor "Private Equity", "Investment Banking", "Tax": onderwerpsnamen zonder
land en zonder loopbaan. Ze kwamen zo terecht op generieke commerciele
zoektermen. In de laatste meting leverde /en/finance/ma/ 14.292 vertoningen op
positie 32 op, met nul kliks, ofwel tweederde van alle vertoningen van de site.
Vijf pagina's hadden bovendien helemaal geen titel.

Titel en omschrijving noemen nu allebei het vak, het land en het feit dat het
om werken gaat. De Nederlandse pagina's doen dat al en staan wel goed.
"""
import os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MERK = " | CorporateCareer"

# pad -> (titel zonder merk, omschrijving)
PAGINAS = {
 "finance/asset-management": ("Asset Management Careers in the Netherlands",
   "Asset management careers in the Netherlands: what the work involves, which firms hire, what the roles pay and how students get in."),
 "finance/bedrijven": ("Finance Employers in the Netherlands",
   "Banks, trading firms, asset managers and advisory firms hiring in the Netherlands, and what it is like to start your career at each."),
 "finance/corporate-development": ("Corporate Development Careers in the Netherlands",
   "Corporate development careers in the Netherlands: in-house M&A and strategy roles, which companies hire, and how to get in as a student."),
 "finance/corporate-finance": ("Corporate Finance Careers in the Netherlands",
   "Corporate finance careers in the Netherlands: what the work involves, which firms hire, what the roles pay and how students get in."),
 "finance/debt-advisory": ("Debt Advisory Careers in the Netherlands",
   "Debt advisory careers in the Netherlands: what the work involves, which firms hire, and how students and graduates get started."),
 "finance/equity-research": ("Equity Research Careers in the Netherlands",
   "Equity research careers in the Netherlands: what analysts do, which banks and brokers hire, and how to get in as a student."),
 "finance/investment-banking": ("Investment Banking Careers in the Netherlands",
   "Investment banking careers in the Netherlands: the analyst route, which banks hire in Amsterdam, what it pays and how to prepare."),
 "finance/ma": ("M&A Careers in the Netherlands",
   "Careers in mergers and acquisitions in the Netherlands: buy-side and sell-side work, which firms hire, what it pays and how students get in."),
 "finance/private-equity": ("Private Equity Careers in the Netherlands",
   "Private equity careers in the Netherlands: what associates do, which funds hire, what it pays and how to move in from banking or consulting."),
 "finance/real-estate-finance": ("Real Estate Finance Careers in the Netherlands",
   "Real estate finance careers in the Netherlands: what the work involves, which lenders and investors hire, and how students get started."),
 "finance/risk-management": ("Risk Management Careers in the Netherlands",
   "Risk management careers at Dutch banks, insurers and asset managers: the main risk types, who hires, and how graduates start."),
 "finance/trading": ("Trading Careers in the Netherlands",
   "Trading careers in the Netherlands: proprietary trading and market making in Amsterdam, which firms hire, and how their selection works."),
 "finance/transaction-services": ("Transaction Services Careers in the Netherlands",
   "Transaction services careers in the Netherlands: due diligence work at the Big Four and others, and how students and graduates get in."),
 "finance/valuation": ("Valuation Careers in the Netherlands",
   "Valuation careers in the Netherlands: what valuation teams do, which firms hire, and how students and graduates get started."),
 "finance/venture-capital": ("Venture Capital Careers in the Netherlands",
   "Venture capital careers in the Netherlands: what analysts and associates do, which funds hire, and how to get in."),
 "finance/wealth-management": ("Wealth Management and Private Banking Careers in the Netherlands",
   "Wealth management and private banking careers in the Netherlands: what the work involves, which banks hire, and how graduates start."),

 "consulting/bedrijven": ("Consulting Firms in the Netherlands",
   "Strategy, technology and advisory consultancies hiring in the Netherlands, and what it is like to start your career at each."),
 "consulting/data-analytics": ("Data & Analytics Consulting Careers in the Netherlands",
   "Data and analytics consulting careers in the Netherlands: what the work involves, which firms hire, and how students get in."),
 "consulting/financial-deal-advisory": ("Financial & Deal Advisory Careers in the Netherlands",
   "Financial and deal advisory careers in the Netherlands: transaction work at consultancies and the Big Four, and how graduates start."),
 "consulting/operations": ("Operations Consulting Careers in the Netherlands",
   "Operations consulting careers in the Netherlands: supply chain and process work, which firms hire, and how students get in."),
 "consulting/people-organisation": ("People & Organisation Consulting Careers in the Netherlands",
   "People and organisation consulting careers in the Netherlands: what the work involves, which firms hire, and how graduates start."),
 "consulting/risk-regulatory": ("Risk & Regulatory Consulting Careers in the Netherlands",
   "Risk and regulatory consulting careers in the Netherlands: financial regulation work, which firms hire, and how students get in."),
 "consulting/strategy": ("Strategy Consulting Careers in the Netherlands",
   "Strategy consulting careers in the Netherlands: the analyst route at MBB and others, the case interview, and what it pays."),
 "consulting/sustainability": ("Sustainability Consulting Careers in the Netherlands",
   "Sustainability consulting careers in the Netherlands: ESG and energy transition work, which firms hire, and how graduates start."),
 "consulting/technology-digital": ("Technology & Digital Consulting Careers in the Netherlands",
   "Technology and digital consulting careers in the Netherlands: what the work involves, which firms hire, and how students get in."),

 "legal/administrative-law": ("Administrative Law Careers in the Netherlands",
   "Administrative law careers at Dutch law firms: what the practice involves, which firms hire trainees, and how the traineeship works."),
 "legal/antitrust-competition-trade": ("Antitrust and Competition Law Careers in the Netherlands",
   "Antitrust, competition and trade law careers at Dutch law firms: the work, the firms that hire, and how the traineeship works."),
 "legal/artificial-intelligence-digital-regulation": ("AI and Digital Regulation Law Careers in the Netherlands",
   "Artificial intelligence and digital regulation practice at Dutch law firms: the work, who hires, and how to start as a trainee."),
 "legal/banking-finance": ("Banking & Finance Law Careers in the Netherlands",
   "Banking and finance law careers at Dutch law firms: the work, which firms hire trainees, and how the traineeship works."),
 "legal/bedrijven": ("Law Firms in the Netherlands",
   "Full-service, international and boutique law firms in the Netherlands, and what it is like to start your traineeship at each."),
 "legal/commercial": ("Commercial Contracts Law Careers in the Netherlands",
   "Commercial and contract law careers at Dutch law firms: the work, which firms hire trainees, and how the traineeship works."),
 "legal/corporate-ma": ("Corporate and M&A Law Careers in the Netherlands",
   "Corporate and M&A law careers at Dutch law firms: deal work, which firms hire trainees, and how the traineeship works."),
 "legal/dispute-resolution": ("Dispute Resolution Careers in the Netherlands",
   "Dispute resolution and litigation careers at Dutch law firms: the work, which firms hire trainees, and how the traineeship works."),
 "legal/employment-labour-pensions": ("Employment and Pensions Law Careers in the Netherlands",
   "Employment, labour and pensions law careers at Dutch law firms: the work, who hires trainees, and how the traineeship works."),
 "legal/esg": ("ESG Law Careers in the Netherlands",
   "ESG practice at Dutch law firms: sustainability reporting and due diligence work, which firms hire, and how to start as a trainee."),
 "legal/intellectual-property": ("Intellectual Property Law Careers in the Netherlands",
   "Intellectual property law careers at Dutch law firms: the work, which firms hire trainees, and how the traineeship works."),
 "legal/public-procurement": ("Public Procurement Law Careers in the Netherlands",
   "Public procurement law careers at Dutch law firms: tender work, which firms hire trainees, and how the traineeship works."),
 "legal/real-estate": ("Real Estate Law Careers in the Netherlands",
   "Real estate law careers at Dutch law firms: the work, which firms hire trainees, and how the traineeship works."),
 "legal/restructuring-insolvency": ("Restructuring and Insolvency Law Careers in the Netherlands",
   "Restructuring and insolvency careers at Dutch law firms: the work, which firms hire trainees, and how the traineeship works."),
 "legal/tax": ("Tax Law Careers in the Netherlands",
   "Tax law careers at Dutch law firms: the work, which firms hire trainees, and how the traineeship works."),
}

VELDEN_TITEL = [r'(<meta property="og:title" content=")[^"]*(")',
                r'(<meta name="twitter:title" content=")[^"]*(")']
VELDEN_DESC = [r'(<meta name="description" content=")[^"]*(")',
               r'(<meta property="og:description" content=")[^"]*(")',
               r'(<meta name="twitter:description" content=")[^"]*(")']


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")


def main():
    geraakt = ontbrak = 0
    for rel, (titel, desc) in sorted(PAGINAS.items()):
        pad = os.path.join(BASE, "en", rel, "index.html")
        if not os.path.exists(pad):
            print("  ontbreekt:", rel)
            ontbrak += 1
            continue
        h = open(pad, encoding="utf-8").read()
        vol = esc(titel + MERK)
        nieuw = re.sub(r"<title>[\s\S]*?</title>", f"<title>{vol}</title>", h, count=1)
        for pat in VELDEN_TITEL:
            nieuw = re.sub(pat, lambda m: m.group(1) + esc(titel) + m.group(2), nieuw, count=1)
        for pat in VELDEN_DESC:
            nieuw = re.sub(pat, lambda m: m.group(1) + esc(desc) + m.group(2), nieuw, count=1)
        if nieuw != h:
            open(pad, "w", encoding="utf-8").write(nieuw)
            geraakt += 1
    print(f"{geraakt} Engelse praktijkpagina's van een titel voorzien, {ontbrak} niet gevonden")
    return 1 if ontbrak else 0


if __name__ == "__main__":
    sys.exit(main())
