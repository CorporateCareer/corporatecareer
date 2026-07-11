#!/usr/bin/env python3
"""Minifyt js/i18n.js naar js/i18n.min.js.

Verwijdert commentaarregels, inspringing en lege regels. Elke regel blijft
een eigen regel (veilig voor automatic semicolon insertion) en de inhoud van
strings wordt niet aangeraakt. i18n.js blijft de leesbare bron; draai dit
script na elke wijziging aan i18n.js zodat i18n.min.js meeloopt.
"""
import io, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "js", "i18n.js")
OUT = os.path.join(BASE, "js", "i18n.min.js")

src = io.open(SRC, encoding="utf-8").read()
out = []
in_block = False
for line in src.split("\n"):
    st = line.strip()
    if in_block:
        if "*/" in st:
            in_block = False
            st = st.split("*/", 1)[1].strip()
            if not st:
                continue
        else:
            continue
    if st.startswith("/*"):
        if "*/" in st:
            st = st.split("*/", 1)[1].strip()
            if not st:
                continue
        else:
            in_block = True
            continue
    if st.startswith("//"):
        continue
    if st == "":
        continue
    out.append(st)

mini = "\n".join(out) + "\n"
io.open(OUT, "w", encoding="utf-8").write(mini)
print(f"i18n.min.js: {len(mini)} bytes (bron {len(src)} bytes)")
