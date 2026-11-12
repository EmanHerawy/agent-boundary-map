"""Make static, subset TTFs for the Agent Boundary Map.

Usage: venv/bin/python -I tools/build_fonts.py <font source dir> <out dir>

Each output is one weight, pinned from the variable sources in google/fonts,
cut down to the characters the app uses. IBM Plex Sans is renamed "ABM Sans",
because "Plex" is a Reserved Font Name and these are modified versions. The same TTF serves the screen
(loaded through the FontFace API) and the PDF (registered with jsPDF), so the
two always match.
"""
import base64, json, os, sys
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools import subset

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

FACES = [
    # (css family, weight, source file, axis pins, jsPDF id)
    ("Fraunces", 400, "fraunces__Fraunces[SOFT,WONK,opsz,wght].ttf", {"wght": 400, "opsz": 24, "SOFT": 0, "WONK": 0}, "fraunces-400"),
    ("Fraunces", 600, "fraunces__Fraunces[SOFT,WONK,opsz,wght].ttf", {"wght": 600, "opsz": 24, "SOFT": 0, "WONK": 0}, "fraunces-600"),
    ("ABM Sans", 400, "ibmplexsans__IBMPlexSans[wdth,wght].ttf", {"wght": 400, "wdth": 100}, "plex-400"),
    ("ABM Sans", 500, "ibmplexsans__IBMPlexSans[wdth,wght].ttf", {"wght": 500, "wdth": 100}, "plex-500"),
    ("ABM Sans", 600, "ibmplexsans__IBMPlexSans[wdth,wght].ttf", {"wght": 600, "wdth": 100}, "plex-600"),
    ("JetBrains Mono", 400, "jetbrainsmono__JetBrainsMono[wght].ttf", {"wght": 400}, "mono-400"),
    ("JetBrains Mono", 600, "jetbrainsmono__JetBrainsMono[wght].ttf", {"wght": 600}, "mono-600"),
]

# Basic Latin, Latin-1, Latin Extended-A (European names), punctuation,
# currency, arrows and the math minus. Everything the app's text uses is in here.
# Keep PDF_GLYPHS in tools/pdf_render.js in step: text outside it is drawn as an image, without its link.
RANGES = [(0x20, 0x7E), (0xA0, 0xFF), (0x100, 0x17F), (0x2010, 0x2027),
          (0x2030, 0x203A), (0x20AC, 0x20AC), (0x2122, 0x2122), (0x2190, 0x2193), (0x2197, 0x2197), (0x2212, 0x2212)]
UNICODES = [c for a, b in RANGES for c in range(a, b + 1)]

manifest = []
for family, weight, src, pins, fid in FACES:
    font = TTFont(os.path.join(SRC, src))
    axes = {a.axisTag for a in font["fvar"].axes}
    font = instancer.instantiateVariableFont(font, {k: v for k, v in pins.items() if k in axes})
    opts = subset.Options()
    opts.hinting = False
    opts.desubroutinize = True
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    opts.drop_tables += ["STAT", "DSIG"]
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=UNICODES)
    sub.subset(font)
    # "Plex" is a Reserved Font Name under the OFL, and an instanced, subset font is a Modified
    # Version, so the IBM Plex Sans faces are renamed. Every face gets its new family name.
    style = {400: "Regular", 500: "Medium", 600: "SemiBold"}[weight]
    ps = family.replace(" ", "") + "-" + style
    for rec in list(font["name"].names):
        if rec.nameID in (1, 4, 6, 16, 17, 3):
            font["name"].removeNames(nameID=rec.nameID)
    font["name"].setName(family, 1, 3, 1, 0x409); font["name"].setName(style, 2, 3, 1, 0x409)
    font["name"].setName(family + " " + style, 4, 3, 1, 0x409); font["name"].setName(ps, 6, 3, 1, 0x409)
    font["name"].setName(ps + ";agent-boundary-map", 3, 3, 1, 0x409)
    path = os.path.join(OUT, fid + ".ttf")
    font.save(path)
    data = open(path, "rb").read()
    # Where the baseline sits inside a text box the browser reports: ascent / (ascent + descent).
    # Browsers use the typo metrics when the font asks for them, otherwise hhea.
    os2, hhea = font["OS/2"], font["hhea"]
    if os2.fsSelection & (1 << 7):
        asc, desc = os2.sTypoAscender, -os2.sTypoDescender
    else:
        asc, desc = hhea.ascent, -hhea.descent
    manifest.append({"id": fid, "family": family, "weight": weight, "bytes": len(data),
                     "ratio": round(asc / (asc + desc), 4),
                     "b64": base64.b64encode(data).decode("ascii")})
    print(f"{fid:14} {family:15} {weight}  {len(data):7d} bytes")

json.dump(manifest, open(os.path.join(OUT, "fonts.json"), "w"))
print("total", sum(m["bytes"] for m in manifest), "bytes")
