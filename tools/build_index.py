"""Build index.html from the v20 artifact export.

Usage: python3 -I tools/build_index.py src/v20-export.html <fonts.json> <jspdf.umd.min.js> <pdf_render.js> <out html>

- Renames the product to Agent Boundary Map.
- Bundles the fonts and jsPDF, removes every outside request, and adds a
  Content-Security-Policy that blocks network access.
- Replaces the text-only PDF with one drawn from the rendered report.
- Adds a browser download path when the page runs outside claude.ai.
Each replacement asserts how many times it applies, so a changed source fails loudly.
"""
import json, re, sys

src, fonts_path, jspdf_path, render_path, out = sys.argv[1:6]
html = open(src, encoding="utf-8").read()


def sub(old, new, count=1):
    global html
    n = html.count(old)
    if n != count:
        sys.exit(f"expected {count} of {old[:80]!r}, found {n}")
    html = html.replace(old, new)


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
