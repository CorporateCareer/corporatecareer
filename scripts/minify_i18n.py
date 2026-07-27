#!/usr/bin/env python3
"""Schrijft js/i18n.min.js: de kleine runtime die het grote vertaalbestand
vervangt. De paginatekst wordt bij de build in de juiste taal ingebakken
(zie scripts/gen_en.py: bake), dus de browser heeft de volledige
vertaaltabel niet meer nodig. js/i18n.js blijft de bron van de vertalingen
en wordt bij de build gebruikt om in te bakken en om de paar sleutels voor
de runtime op te halen.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_en

if __name__ == "__main__":
    gen_en.write_runtime()
    size = os.path.getsize(os.path.join(gen_en.BASE, "js", "i18n.min.js"))
    print(f"js/i18n.min.js (mini-runtime): {size} bytes")
