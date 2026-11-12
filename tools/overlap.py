"""Report words in a PDF whose boxes overlap another word (overprinted text). Usage: overlap.py <bbox.html>"""
import re, sys
html = open(sys.argv[1], encoding="utf-8").read()
bad = 0
for pn, page in enumerate(re.findall(r"<page[^>]*>(.*?)</page>", html, re.S), 1):
    words = [(float(a), float(b), float(c), float(d), w) for a, b, c, d, w in
             re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>', page)]
    for i, (x0, y0, x1, y1, w) in enumerate(words):
        for (a0, b0, a1, b1, v) in words[i + 1:]:
            ox = min(x1, a1) - max(x0, a0); oy = min(y1, b1) - max(y0, b0)
            if ox > 1.5 and oy > 0.5 * min(y1 - y0, b1 - b0):
                bad += 1
                if bad <= 5: print(f"  page {pn}: {w!r} overlaps {v!r}")
print("overlapping word pairs:", bad)
