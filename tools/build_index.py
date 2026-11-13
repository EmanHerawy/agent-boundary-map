"""Build index.html from the v20 artifact export.

Usage: python3 -I tools/build_index.py src/v20-export.html <fonts.json> <jspdf.umd.min.js> <pdf_render.js> <out html>

- Renames the product to Agent Boundary Map.
- Bundles the fonts and jsPDF, removes every outside request, and adds a
  Content-Security-Policy that blocks network access.
- Replaces the text-only PDF with one drawn from the rendered report.
- Adds a browser download path when the page runs outside claude.ai.
- Links the evidence docs, and adds the summary report (tools/mini_report.js, read from
  this script's folder) with a Summary | Full switch for the downloads.
Each replacement asserts how many times it applies, so a changed source fails loudly.
"""
import json, os, re, sys

src, fonts_path, jspdf_path, render_path, out = sys.argv[1:6]
html = open(src, encoding="utf-8").read()


def sub(old, new, count=1):
    global html
    n = html.count(old)
    if n != count:
        sys.exit(f"expected {count} of {old[:80]!r}, found {n}")
    html = html.replace(old, new)


# 0. Harness corrections (src/harness-corrections.json, made by tools/make_corrections.py from
#    the verified harness-claims-mapping.md). Applied to the question data before anything else.
#    Options are never removed (saved answers store their position); a wrong option is only
#    offered to the harnesses where it holds. Every target text must match exactly once.
def apply_corrections():
    global html
    corr = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "harness-corrections.json"), encoding="utf-8"))
    i = html.index("var D = {"); k = html.index("{", i); depth = 0
    for p in range(k, len(html)):
        if html[p] == "{": depth += 1
        elif html[p] == "}":
            depth -= 1
            if depth == 0: end = p + 1; break
    data = json.loads(html[k:end]); qs = {q["id"]: q for q in data["qs"]}
    # Corrected values are written on one line, next to the text they apply to, so each
    # correction reads as a single line in `git diff index.html`. Untouched entries keep
    # their original layout.
    compact = {}
    def one_line(v):
        key = "__ONE_LINE_%d__" % len(compact); compact[key] = json.dumps(v, ensure_ascii=False); return key
    for c in corr["options"]:
        q = qs[c["q"]]
        hits = [n for n, o in enumerate(q["a"]) if o["t"] == c["text"]]
        if len(hits) != 1: sys.exit(f"correction: option not found once in {c['q']}: {c['text'][:60]!r}")
        o = q["a"][hits[0]]
        rest = {kk: vv for kk, vv in o.items() if kk not in ("t", "hs")}
        first = [("t", c.get("new_text") or o["t"])]
        if c.get("hs") is not None: first.append(("hs", one_line(c["hs"])))
        elif "hs" in o: first.append(("hs", o["hs"]))
        q["a"][hits[0]] = dict(first + list(rest.items()))
    for c in corr["notes"]:
        if qs[c["q"]].get("hn") != c["old"]: sys.exit(f"correction: note in {c['q']} has changed")
        qs[c["q"]]["hn"] = c["new"]
    for c in corr["where_to_check"]:
        wc = qs[c["q"]].setdefault("wc", {})
        if wc.get(c["harness"]) != c["old"]: sys.exit(f"correction: where-to-check {c['q']}/{c['harness']} isn't as expected")
        wc[c["harness"]] = one_line({"t": c["text"], "src": c["sources"]})
    text = json.dumps(data, ensure_ascii=False, indent=1)
    for key, val in compact.items():
        if text.count('"%s"' % key) != 1: sys.exit("correction: one-line placeholder lost")
        text = text.replace('"%s"' % key, val)
    html = html[:k] + text + html[end:]
    for c in corr.get("findings", []):  # finding texts (in THEMES), replaced an exact number of times
        if html.count(c["old"]) != c["count"]: sys.exit(f"correction: finding text found {html.count(c['old'])} times, expected {c['count']}: {c['old'][:60]!r}")
        html = html.replace(c["old"], c["new"])


apply_corrections()
# A "Where to check" entry can now carry its sources: show them as links under the text.
sub('wc.appendChild(el("p", null, q.wc[s.built]));',
    '(function (w) { wc.appendChild(el("p", null, typeof w === "string" ? w : w.t)); if (w && w.src && w.src.length) {'
    ' var sp = el("p", "wcsrc"); sp.appendChild(document.createTextNode("Source" + (w.src.length > 1 ? "s" : "") + ": "));'
    ' w.src.forEach(function (u, n) { if (n) sp.appendChild(document.createTextNode(" \\u00B7 ")); var a = el("a", null, u.replace(/^https?:\\/\\//, ""));'
    ' a.href = u; a.target = "_blank"; a.rel = "noopener"; a.setAttribute("aria-label", "Source: " + u + " (opens in a new tab)"); sp.appendChild(a); });'
    ' wc.appendChild(sp); } })(q.wc[s.built]);')


CSP = ("default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; "
       "img-src data: blob:; font-src data:; connect-src 'none'; frame-src 'none'; "
       "base-uri 'none'; form-action 'none'")

# 1. No outside requests: CSP, no Google Fonts.
sub("<meta charset=utf8>", '<meta charset=utf8><meta http-equiv="Content-Security-Policy" content="' + CSP + '">')
sub('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap">\n', "")

# 2. Fonts, registered before anything renders. The same bytes feed the PDF.
fonts = json.load(open(fonts_path))
manifest = json.dumps([{k: f[k] for k in ("id", "family", "weight", "ratio", "b64")} for f in fonts], separators=(",", ":"))
font_script = (
    "<script>\n/* Bundled fonts (SIL Open Font License 1.1): Fraunces, JetBrains Mono, and IBM Plex Sans\n"
    "   renamed ABM Sans (modified version; Plex is a Reserved Font Name). Static weights, subset\n"
    "   to Latin; see NOTICE for sources and licenses. Loaded from memory, no network. */\n"
    "window.__ABM_FONTS = " + manifest + ";\n"
    "(function () {\n"
    "  window.__ABM_FONTS.forEach(function (f) {\n"
    "    try {\n"
    "      var bin = atob(f.b64), u = new Uint8Array(bin.length);\n"
    "      for (var i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);\n"
    "      f.buf = u.buffer;\n"
    "      if (window.FontFace && document.fonts) document.fonts.add(new FontFace(f.family, f.buf, { weight: String(f.weight), style: \"normal\" }));\n"
    "    } catch (e) { /* fall back to system fonts */ }\n"
    "  });\n"
    "})();\n</script>\n"
)
sub("<title>Agent Trust Map</title>\n", "<title>Agent Boundary Map</title>\n" + font_script)

# 2b. The bundled IBM Plex Sans is a modified version, so it can't use the reserved name "Plex".
sub('--body: "IBM Plex Sans",', '--body: "ABM Sans",')

# 3. Name: Agent Boundary Map. The saved-answers key stays, so answers survive.
sub('<span class="eyebrow">Agent Trust Map</span>', '<span class="eyebrow">Agent Boundary Map</span>')
sub('aria-label="Example trust map"', 'aria-label="Example boundary map"')
sub('<span class="eyebrow">Trust report</span>', '<span class="eyebrow">Boundary report</span>')
sub('<span class="eyebrow">Trust map</span>', '<span class="eyebrow">Boundary map</span>')
sub('"aria-label": "Trust map: "', '"aria-label": "Boundary map: "')
sub('"AGENT TRUST MAP: "', '"AGENT BOUNDARY MAP: "')
sub('"# Trust report: "', '"# Boundary report: "')
sub(" with Agent Trust Map. ", " with Agent Boundary Map. ")
sub('"-trust-report-"', '"-boundary-report-"')

# 4. Say what the CSP guarantees.
sub("""        <li>No evidence to upload. "Don't know" is a fine answer; it shows you what to find out.</li>\n""",
    """        <li>No evidence to upload. "Don't know" is a fine answer; it shows you what to find out.</li>\n"""
    """        <li>Your answers stay in this browser. The page makes no network requests, and its security policy blocks them.</li>\n""")

# 4b. Link the evidence behind the questions (docs/user-guide-evidence.md, docs/evidence.md):
#     one line in the intro, one link per step in the quiz (never per question, to keep the
#     question blocks quiet), and the report footer plus its Markdown export. Links open in a
#     new tab, announced to screen readers through aria-label (no hidden text reaches the PDF).
#     The CSP limits requests the page makes, not navigation. ↗ (U+2197) is in the font subset.
GUIDE = "https://github.com/EmanHerawy/agent-boundary-map/blob/main/docs/user-guide-evidence.md"
REGISTER = "https://github.com/EmanHerawy/agent-boundary-map/blob/main/docs/evidence.md"
NEW_TAB = " (opens in a new tab)"
# The quiz steps that have a section in the guide; names match its "## " headings exactly.
GUIDE_STEPS = ["Instructions", "Outside content", "Memory", "Knowledge sources", "Users", "Tools", "MCP servers",
               "Skills, plugins and hooks", "Code execution", "Browser", "Actions", "Other agents", "Oversight"]


def a(href, text, label):
    return f'<a href="{href}" target="_blank" rel="noopener" aria-label="{label}{NEW_TAB}">{text} ↗</a>'


LINKS = ".hero li a, .note a, #qDesc a, .wcsrc a"
sub("@media (prefers-reduced-motion: no-preference) { .opt, .btn { transition: border-color .12s; } }\n</style>",
    "@media (prefers-reduced-motion: no-preference) { .opt, .btn { transition: border-color .12s; } }\n"
    f"{LINKS} {{ color: var(--accent); }}\n"
    f"{LINKS.replace(', ', ':visited, ')}:visited {{ color: color-mix(in srgb, var(--accent) 60%, var(--muted)); }}\n</style>")
sub("""        <li>Your answers stay in this browser. The page makes no network requests, and its security policy blocks them.</li>\n""",
    """        <li>Your answers stay in this browser. The page makes no network requests, and its security policy blocks them.</li>\n"""
    f"""        <li>Why each question is here: {a(GUIDE, "the evidence", "the evidence")}, from real incidents, research and security standards.</li>\n""")
sub("""    document.getElementById("qDesc").textContent = b.desc;\n""",
    """    document.getElementById("qDesc").textContent = b.desc;\n"""
    f"""    if ({json.dumps(GUIDE_STEPS)}.indexOf(b.name) >= 0) {{\n"""
    """      var evA = el("a", null, "Why we ask these \\u2197"), evD = document.getElementById("qDesc");\n"""
    f"""      evA.href = "{GUIDE}#" + b.name.toLowerCase().replace(/[^a-z0-9 -]/g, "").replace(/ /g, "-");\n"""
    f"""      evA.target = "_blank"; evA.rel = "noopener"; evA.setAttribute("aria-label", "Why we ask these: evidence for " + b.name + "{NEW_TAB}");\n"""
    """      evD.appendChild(document.createTextNode(" \\u00B7 ")); evD.appendChild(evA);\n"""
    """    }\n""")
sub("""      <p class="note">The rule behind every question: the model may propose, but something outside the model must authorize.</p>\n""",
    """      <p class="note">The rule behind every question: the model may propose, but something outside the model must authorize.</p>\n"""
    f"""      <p class="note">Evidence behind these questions: {a(GUIDE, "why we ask them", "why we ask them")} · {a(REGISTER, "evidence register", "evidence register")}.</p>\n""")
sub('''    out.push("", "---", "", "The rule behind every question: the model may propose, but something outside the model must authorize.");''',
    '''    out.push("", "---", "", "The rule behind every question: the model may propose, but something outside the model must authorize.");\n'''
    f'''    out.push("", "Evidence behind these questions: [why we ask them]({GUIDE}) \\u00B7 [evidence register]({REGISTER}).");''')

# 5. jsPDF is bundled, so nothing to fetch.
sub('  var JSPDF_URL = "https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js";\n', "")
old_loader = re.search(r"  function loadJsPDF\(\) \{\n.*?\n  \}\n(?=  function fileBase)", html, re.S)
if not old_loader:
    sys.exit("loadJsPDF not found")
html = html.replace(old_loader.group(0),
    "  function loadJsPDF() {\n"
    "    if (window.jspdf && window.jspdf.jsPDF) return Promise.resolve(window.jspdf.jsPDF);\n"
    "    return Promise.reject({ code: \"pdf_load\" });\n"
    "  }\n")
sub("  var DL = null, jspdfP = null;\n", "  var DL = null;\n")

# 6. The PDF is drawn from the rendered report.
old_pdf = re.search(r"  function buildPdf\(JsPDF, md, title\) \{\n.*?\n  \}\n(?=  function loadJsPDF)", html, re.S)
if not old_pdf:
    sys.exit("buildPdf not found")
html = html.replace(old_pdf.group(0), open(render_path, encoding="utf-8").read())

# 7. Outside claude.ai, save through an ordinary browser download.
sub("""  try { if (window.claude && typeof window.claude.use === "function") window.claude.use("downloads").then(function (d) { DL = d; setExport(!!d); }, function () { setExport(false); }); } catch (e) { /* no viewer */ }""",
    """  var BLOB_DL = {
    save: function (o) {
      return new Promise(function (res, rej) {
        try {
          var type = /\\.pdf$/.test(o.filename) ? "application/pdf" : "text/markdown;charset=utf-8";
          var url = URL.createObjectURL(new Blob([o.data], { type: type })), a = document.createElement("a");
          a.href = url; a.download = o.filename; a.rel = "noopener"; a.hidden = true;
          document.body.appendChild(a); a.click();
          setTimeout(function () { URL.revokeObjectURL(url); a.remove(); }, 4000);
          res();
        } catch (e) { rej(e); }
      });
    }
  };
  function useBlobDownloads() { DL = BLOB_DL; setExport(true); }
  try {
    if (window.claude && typeof window.claude.use === "function") window.claude.use("downloads").then(function (d) { if (d) { DL = d; setExport(true); } else useBlobDownloads(); }, useBlobDownloads);
    else useBlobDownloads();
  } catch (e) { useBlobDownloads(); }""")

# 7b. Summary report (tools/mini_report.js): a "Report: Summary | Full" switch that changes what's
#     on screen, opening on Summary; the downloads follow it and their labels say which they give.
#     "Copy summary" always copies the summary. One topActions() picks the
#     top actions everywhere (same ranking as before, but a finding without an action no longer
#     leaves a gap), so the screen, the full report and the summary always agree.
mini = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mini_report.js"), encoding="utf-8").read()
mini = mini.replace("__GUIDE__", GUIDE).replace("__REGISTER__", REGISTER)
sub("  window.__tmExport = { markdown: reportMarkdown, pdf: buildPdf };\n",
    mini + "  window.__tmExport = { markdown: reportMarkdown, summary: summaryMarkdown, pdf: buildPdf };\n")
sub("    if (ranked.length) {\n", "    if (topActions(ranked, s, a).length) {\n")
sub("ranked.slice(0, 3).forEach", "topActions(ranked, s, a).forEach")
sub('    if (E.risk.length) {\n      out.push("", "## Top actions", "");\n      E.risk.slice(0, 3).forEach',
    '    if (topActions(E.risk, s, a).length) {\n      out.push("", "## Top actions", "");\n      topActions(E.risk, s, a).forEach')
sub('if (E.risk.length) { out.push("", "TOP ACTIONS"); E.risk.slice(0, 3).forEach',
    'if (topActions(E.risk, s, a).length) { out.push("", "TOP ACTIONS"); topActions(E.risk, s, a).forEach')
sub("""          <div class="btnrow">\n            <button class="btn" type="button" id="editBtn">""",
    """          <div class="btnrow">\n"""
    """            <fieldset class="seg" id="reportMode"><legend>Report</legend>"""
    """<label><input type="radio" name="rmode" value="summary" checked> Summary</label>"""
    """<label><input type="radio" name="rmode" value="full"> Full</label></fieldset>\n"""
    """            <button class="btn" type="button" id="editBtn">""")
sub("""      <div class="card">\n        <div class="maphead">""", """      <div class="card" id="mapHeadCard">\n        <div class="maphead">""")
sub("""      <div class="card summary" id="summary"></div>\n""", """      <div id="sumView"></div>\n      <div class="card summary" id="summary"></div>\n""")
sub("""    document.getElementById("copyCard").hidden = true;\n    exportNote("");\n  }\n""",
    """    document.getElementById("copyCard").hidden = true;\n    exportNote("");\n    applyView();\n  }\n""")
sub("@media (prefers-reduced-motion: no-preference) { .opt, .btn { transition: border-color .12s; } }\n",
    "@media (prefers-reduced-motion: no-preference) { .opt, .btn { transition: border-color .12s; } }\n"
    ".wcsrc { font-size: 0.76rem; color: var(--muted); margin: 4px 0 0; overflow-wrap: anywhere; }\n"
    ".seg { display: inline-flex; align-items: center; border: 0; margin: 0 10px 0 0; padding: 0; min-width: 0; }\n"
    ".seg legend { float: left; padding: 0; margin-right: 12px; font-size: 0.8rem; color: var(--muted); }\n"
    ".seg label { display: inline-flex; align-items: center; gap: 6px; min-height: 36px; font-size: 0.88rem; cursor: pointer; }\n"
    ".seg label + label { margin-left: 16px; }\n"
    ".seg input { accent-color: var(--accent); width: 16px; height: 16px; margin: 0; cursor: pointer; }\n"
    ".seg label:has(input:checked) { font-weight: 600; }\n")
sub('var label = kind === "pdf" ? "PDF" : "Markdown file", md = reportMarkdown(), c = current();',
    'var mode = reportMode(), label = (mode === "summary" ? "summary " : "full report ") + (kind === "pdf" ? "PDF" : "Markdown file"), md = mode === "summary" ? summaryMarkdown() : reportMarkdown(), c = current();')
sub('buildPdf(J, md, c.name || "Your agent")', 'buildPdf(J, md, c.name || "Your agent", mode)')
sub('exportNote(label + " saved.");', 'exportNote(label.charAt(0).toUpperCase() + label.slice(1) + " saved.");')
sub('"-boundary-report-"', '(reportMode() === "summary" ? "-boundary-summary-" : "-boundary-report-")')
sub("var t = summaryText(),", "var t = summaryMarkdown(),")

left = [m.start() for m in re.finditer(r"(?i)trust map|trust report", html)]
leftover = [html[i - 30:i + 40] for i in left if "agent-trust-map-v" not in html[i - 30:i + 40]]
if leftover:
    sys.exit("old name still present: " + repr(leftover[:5]))
if re.search(r"https?://(fonts\.googleapis|cdnjs\.cloudflare)", html):
    sys.exit("outside URL still referenced (app code)")


# 8. jsPDF (MIT) after the app script, so it never delays the first render.
jspdf = open(jspdf_path, encoding="utf-8").read()
if "</script" in jspdf.lower():
    sys.exit("jsPDF contains a closing script tag")
app_end = html.rindex("</script>") + len("</script>")
html = html[:app_end] + "\n<script>\n/* jsPDF 4.2.1 (MIT), bundled unchanged from the npm package. */\n" + jspdf + "\n</script>" + html[app_end:]

open(out, "w", encoding="utf-8").write(html)
print(f"wrote {out}: {len(html.encode('utf-8')):,} bytes")
