  /* ---------- PDF: draws the rendered report ----------
     The report is laid out in a hidden frame at a fixed width, in light mode,
     with every section about this agent's answers opened.
     Each box, border, line of text and map shape is then drawn into the PDF
     at the position the browser gave it, in the same fonts. Text stays
     selectable, and pages break between blocks, never through a line.
     Text in scripts the bundled fonts don't cover is drawn as an image. */
  var PDF_W = 800;                                      // CSS px the report is laid out at
  var PDF_M = { top: 40, side: 36, bottom: 46 };        // page margins, pt
  var PDF_GLYPHS = /^[\x20-\x7E\xA0-ſ‐-‧‰-›€™←-↓−]*$/;
  var PDF_CSS = [
    "html, body { background: #fff !important; }",
    "body { margin: 0 !important; padding: 0 !important; }",
    "#app { max-width: none !important; margin: 0 !important; padding: 0 !important; }",
    "#v-map .btnrow, #v-map button, #exportNote, #copyCard { display: none !important; }",
    "details > summary { list-style: none !important; }",
    "details > summary::-webkit-details-marker { display: none; }",
    "*, *::before, *::after { animation: none !important; transition: none !important; }"
  ].join("\n");
  var WHITE = { r: 255, g: 255, b: 255, a: 1 };
  var colorCtx = null;

  function pdfNum(s) { return parseFloat(s) || 0; }
  function pdfAlpha(s) { var n = parseFloat(s); return isNaN(n) ? 1 : /%$/.test(s) ? n / 100 : n; }
  function pdfColor(v) {
    if (!v || v === "transparent" || v === "none" || /^url\(/.test(v)) return null;
    var m = /^rgba?\(([^)]*)\)$/.exec(v), p;
    if (!m) {
      var c = /^color\(srgb\s+([^)]*)\)$/.exec(v);
      if (c) { p = c[1].split(/[\s\/]+/).filter(Boolean); return { r: pdfNum(p[0]) * 255, g: pdfNum(p[1]) * 255, b: pdfNum(p[2]) * 255, a: p.length > 3 ? pdfAlpha(p[3]) : 1 }; }
      if (!colorCtx) colorCtx = document.createElement("canvas").getContext("2d");
      colorCtx.fillStyle = "#000"; colorCtx.fillStyle = v; v = colorCtx.fillStyle;
      if (v.charAt(0) === "#") return { r: parseInt(v.substr(1, 2), 16), g: parseInt(v.substr(3, 2), 16), b: parseInt(v.substr(5, 2), 16), a: 1 };
      m = /^rgba?\(([^)]*)\)$/.exec(v); if (!m) return null;
    }
    p = m[1].split(/[\s,\/]+/).filter(Boolean);
    return { r: pdfNum(p[0]), g: pdfNum(p[1]), b: pdfNum(p[2]), a: p.length > 3 ? pdfAlpha(p[3]) : 1 };
  }
  function pdfOver(c, bg, op) {
    var a = Math.max(0, Math.min(1, c.a * (op == null ? 1 : op)));
    return { r: c.r * a + bg.r * (1 - a), g: c.g * a + bg.g * (1 - a), b: c.b * a + bg.b * (1 - a), a: 1 };
  }
  function pdfRgb(c) { return [Math.round(c.r), Math.round(c.g), Math.round(c.b)]; }
  function pdfCss(c) { return "rgb(" + pdfRgb(c).join(",") + ")"; }
  function pdfFont(cs) {
    var fonts = window.__ABM_FONTS || [];
    if (!fonts.length) return { id: "helvetica", ratio: 0.78 };
    var first = (cs.fontFamily || "").split(",")[0].replace(/["']/g, "").trim().toLowerCase();
    var w = parseInt(cs.fontWeight, 10) || 400, fam = "plex";
    if (first === "fraunces") fam = "fraunces";
    else if (/mono|menlo|consolas|courier/.test(first)) fam = "mono";
    var wt = fam === "plex" ? (w < 450 ? 400 : w < 550 ? 500 : 600) : (w < 500 ? 400 : 600);
    for (var i = 0; i < fonts.length; i++) if (fonts[i].id === fam + "-" + wt) return fonts[i];
    return fonts[0];
  }
  function pdfClean(t) { return String(t).replace(/[^\x20-\x7E\xA0-ſ‐-‧‰-›€™←-↓−]/g, ""); }

  // Remove whole CSS blocks that start with the given pattern (balanced braces).
  function pdfStrip(css, re) {
    var out = "", last = 0, m;
    re.lastIndex = 0;
    while ((m = re.exec(css))) {
      var i = m.index + m[0].length, depth = 1;
      while (i < css.length && depth) { if (css[i] === "{") depth++; else if (css[i] === "}") depth--; i++; }
      out += css.slice(last, m.index); last = i; re.lastIndex = i;
    }
    return out + css.slice(last);
  }

  // Lay out a copy of the report in a hidden frame at PDF_W, light mode, all sections open.
  function pdfLayout() {
    var fr = document.createElement("iframe");
    fr.setAttribute("aria-hidden", "true"); fr.tabIndex = -1; fr.title = "PDF layout";
    fr.style.cssText = "position:fixed;left:-20000px;top:0;width:" + PDF_W + "px;height:1200px;border:0;opacity:0;pointer-events:none;color-scheme:light";
    var loaded = new Promise(function (res) { fr.addEventListener("load", res, { once: true }); setTimeout(res, 400); });
    document.body.appendChild(fr);
    return loaded.then(function () {
      var w = fr.contentWindow, d = fr.contentDocument;
      if (!d.head) d.documentElement.appendChild(d.createElement("head"));
      if (!d.body) d.documentElement.appendChild(d.createElement("body"));
      var css = Array.prototype.map.call(document.querySelectorAll("style"), function (s) { return s.textContent; }).join("\n");
      css = pdfStrip(css, /@media\s*\(prefers-color-scheme:\s*dark\)\s*\{/g);
      css = pdfStrip(css, /:root\[data-theme="dark"\]\s*\{/g);
      var st = d.createElement("style"); st.textContent = css + "\n" + PDF_CSS; d.head.appendChild(st);
      var waits = (window.__ABM_FONTS || []).map(function (f) {
        try { var ff = new w.FontFace(f.family, f.buf, { weight: String(f.weight), style: "normal" }); d.fonts.add(ff); return ff.load(); } catch (e) { return null; }
      }).filter(Boolean);
      var app = d.createElement("div"); app.id = "app"; app.className = "wrap";
      var sec = document.getElementById("v-map").cloneNode(true);
      sec.hidden = false;
      app.appendChild(d.adoptNode(sec)); d.body.appendChild(app);
      // Open everything about this agent's answers. Generic illustrative examples stay closed, as in the Markdown export.
      Array.prototype.forEach.call(sec.querySelectorAll("details"), function (x) {
        var s = x.querySelector("summary"); x.open = !(s && /^More examples\b/.test(s.textContent.trim()));
      });
      return Promise.all(waits).then(function () { return d.fonts.ready; }).then(function () {
        return new Promise(function (res) { requestAnimationFrame(function () { requestAnimationFrame(res); }); });
      }).then(function () {
        return { w: w, d: d, root: sec, remove: function () { fr.remove(); } };
      });
    });
  }

  // Walk the laid-out report and record what to draw, in paint order, in CSS px.
  function pdfCollect(L) {
    var w = L.w, d = L.d, base = L.root.getBoundingClientRect();
    var items = [], blocks = [], lines = [], range = d.createRange();
    function box(r) { return { x: r.left - base.left, y: r.top - base.top, w: r.width, h: r.height }; }
    function radius(cs, r) {
      var v = cs.borderTopLeftRadius || "0", n = parseFloat(v) || 0;
      if (/%$/.test(v)) n = Math.min(r.w, r.h) * n / 100;
      return Math.max(0, Math.min(n, r.w / 2, r.h / 2));
    }
    function dashOf(style, lw) { return style === "dashed" ? [3 * lw, 2.5 * lw] : style === "dotted" ? [lw, lw] : null; }
    function borders(cs, r, bg, o) {
      var sides = ["Top", "Right", "Bottom", "Left"].map(function (s) {
        return { s: s, w: pdfNum(cs["border" + s + "Width"]), st: cs["border" + s + "Style"], c: pdfColor(cs["border" + s + "Color"]) };
      });
      var on = sides.filter(function (s) { return s.w > 0 && s.st !== "none" && s.st !== "hidden" && s.c && s.c.a > 0; });
      if (!on.length || r.w <= 0 || r.h <= 0) return;
      var rad = radius(cs, r), s0 = on[0];
      var same = on.length === 4 && on.every(function (s) { return s.w === s0.w && s.st === s0.st && s.c.r === s0.c.r && s.c.g === s0.c.g && s.c.b === s0.c.b && s.c.a === s0.c.a; });
      if (same) {
        var round = rad >= Math.min(r.w, r.h) / 2 - 0.5, dash = dashOf(s0.st, s0.w);
        if (round && dash && s0.st === "dashed") { var circ = Math.PI * (Math.min(r.w, r.h) - s0.w), seg = circ / Math.max(4, Math.round(circ / (2.4 * s0.w))); dash = [seg * 0.55, seg * 0.45]; }
        items.push({ k: "frame", x: r.x + s0.w / 2, y: r.y + s0.w / 2, w: r.w - s0.w, h: r.h - s0.w, rad: Math.max(0, rad - s0.w / 2), lw: s0.w, c: pdfOver(s0.c, bg, o), dash: dash });
        return;
      }
      on.forEach(function (s) {
        var c = pdfOver(s.c, bg, o), clip = s.s === "Top" ? { x: r.x, y: r.y, w: r.w, h: s.w } : s.s === "Bottom" ? { x: r.x, y: r.y + r.h - s.w, w: r.w, h: s.w }
          : s.s === "Left" ? { x: r.x, y: r.y, w: s.w, h: r.h } : { x: r.x + r.w - s.w, y: r.y, w: s.w, h: r.h };
        if (s.st === "solid" || s.st === "double") items.push({ k: "band", x: r.x, y: r.y, w: r.w, h: r.h, rad: rad, clip: clip, c: c });
        else {
          var horiz = s.s === "Top" || s.s === "Bottom";
          items.push({ k: "dline", x: clip.x, y: clip.y, w: clip.w, h: clip.h, horiz: horiz, lw: s.w, c: c, dash: dashOf(s.st, s.w) });
        }
      });
    }
    function pseudo(el, which, r, cs, bg, o) {
      var ps = w.getComputedStyle(el, which);
      if (!ps || ps.content === "none" || ps.content === "normal" || ps.display === "none" || ps.position !== "absolute") return;
      var left = parseFloat(ps.left), top = parseFloat(ps.top), pw = parseFloat(ps.width), ph = parseFloat(ps.height);
      if (isNaN(left) || isNaN(top) || !(pw > 0)) return;
      var bt = pdfNum(cs.borderTopWidth), bl = pdfNum(cs.borderLeftWidth);
      if (!(ph > 0)) { var bottom = parseFloat(ps.bottom); if (isNaN(bottom)) return; ph = r.h - bt - pdfNum(cs.borderBottomWidth) - top - bottom; }
      if (!(ph > 0)) return;
      var pr = { x: r.x + bl + left, y: r.y + bt + top, w: pw, h: ph }, f = pdfColor(ps.backgroundColor);
      if (f && f.a > 0) items.push({ k: "box", x: pr.x, y: pr.y, w: pr.w, h: pr.h, rad: radius(ps, pr), fill: pdfOver(f, bg, o) });
      borders(ps, pr, bg, o);
    }
    function marker(el, cs, r, bg, o) {
      var t = cs.listStyleType;
      if (!t || t === "none" || /^disclosure/.test(t)) return;
      var fs = pdfNum(cs.fontSize) || 14, lh = parseFloat(cs.lineHeight) || fs * 1.5, c = pdfOver(pdfColor(cs.color) || { r: 0, g: 0, b: 0, a: 1 }, bg, o);
      if (t === "decimal") {
        var n = 1, p = el.previousElementSibling; while (p) { if (p.tagName === "LI") n++; p = p.previousElementSibling; }
        var label = n + ".", lw = fs * 0.6 * label.length;
        items.push({ k: "text", x: r.x - lw - fs * 0.35, y: r.y + (lh - fs * 1.3) / 2, w: lw, h: fs * 1.3, t: label, f: pdfFont(cs), fs: fs, ls: 0, c: c, bg: bg, free: true });
      } else items.push({ k: "dot", x: r.x - fs * 0.85, y: r.y + lh / 2 - fs * 0.17, w: fs * 0.34, h: fs * 0.34, c: c, hollow: t === "circle" });
    }
    function text(node, el, cs, bg, o) {
      var s = node.nodeValue;
      if (!/\S/.test(s)) return;
      var col = pdfColor(cs.color); if (!col || col.a === 0) return;
      col = pdfOver(col, bg, o);
      var f = pdfFont(cs), fs = pdfNum(cs.fontSize) || 14, ls = cs.letterSpacing === "normal" ? 0 : pdfNum(cs.letterSpacing);
      var up = cs.textTransform === "uppercase", pre = /^pre/.test(cs.whiteSpace);
      var a = el.closest ? el.closest("a[href]") : null, href = a && /^https?:/.test(a.href) ? a.href : null;
      var cssFont = cs.fontStyle + " " + cs.fontWeight + " " + cs.fontSize + " " + cs.fontFamily;
      // Right-to-left text reorders words on screen, so group it by line only and draw the whole
      // logical run, letting the browser's bidi rendering (in the image fallback) place each word.
      var rtl = /[\u0590-\u08FF\uFB1D-\uFDFF\uFE70-\uFEFF]/.test(s);
      var line = null, re = /\S+/g, m;
      function flush() {
        if (!line) return;
        var t = s.slice(line.a, line.b); if (!pre) t = t.replace(/\s+/g, " "); if (up) t = t.toUpperCase();
        line.t = t; items.push(line); lines.push([line.y, line.y + line.h]); line = null;
      }
      function add(rc, i, j) {
        if (!rc.width && !rc.height) return;
        var x = rc.left - base.left, y = rc.top - base.top;
        if (line && Math.abs(y - line.y) < rc.height * 0.5 && (rtl || x >= line.x + line.w - 1)) {
          var right = Math.max(line.x + line.w, x + rc.width);
          line.x = Math.min(line.x, x); line.w = right - line.x; line.a = Math.min(line.a, i); line.b = Math.max(line.b, j); line.h = Math.max(line.h, rc.height);
          return;
        }
        flush();
        line = { k: "text", x: x, y: y, w: rc.width, h: rc.height, a: i, b: j, f: f, fs: fs, ls: ls, c: col, bg: bg, href: href, font: cssFont, dir: cs.direction };
      }
      while ((m = re.exec(s))) {
        range.setStart(node, m.index); range.setEnd(node, m.index + m[0].length);
        var rs = range.getClientRects();
        if (rs.length === 1) { add(rs[0], m.index, m.index + m[0].length); continue; }
        for (var i = m.index; i < m.index + m[0].length; i++) {     // a word broken across lines
          range.setStart(node, i); range.setEnd(node, i + 1);
          var cr = range.getClientRects(); if (cr.length) add(cr[0], i, i + 1);
        }
      }
      flush();
    }
    function svg(root) {
      var rr = box(root.getBoundingClientRect());
      if (rr.h > 0) blocks.push([rr.y, rr.y + rr.h, true]);
      Array.prototype.forEach.call(root.querySelectorAll("rect, line, circle, text"), function (n) {
        var cs = w.getComputedStyle(n);
        if (cs.display === "none" || cs.visibility === "hidden") return;
        var m = n.getScreenCTM(); if (!m) return;
        var op = 1; for (var a = n; a && a !== root.parentNode; a = a.parentNode) op *= a.nodeType === 1 ? parseFloat(w.getComputedStyle(a).opacity) : 1;
        if (!(op > 0)) return;
        function pt(x, y) { return { x: m.a * x + m.c * y + m.e - base.left, y: m.b * x + m.d * y + m.f - base.top }; }
        var sc = Math.abs(m.a) || 1, fill = pdfColor(cs.fill), stroke = pdfColor(cs.stroke), sw = pdfNum(cs.strokeWidth) * sc;
        var fo = parseFloat(cs.fillOpacity), so = parseFloat(cs.strokeOpacity);
        var dash = cs.strokeDasharray && cs.strokeDasharray !== "none" ? cs.strokeDasharray.split(/[\s,]+/).map(function (v) { return pdfNum(v) * sc; }) : null;
        var tag = n.tagName.toLowerCase();
        var paint = { fill: fill, stroke: stroke, fo: (isNaN(fo) ? 1 : fo) * op * (fill ? fill.a : 1), so: (isNaN(so) ? 1 : so) * op * (stroke ? stroke.a : 1), lw: sw, dash: dash, cap: cs.strokeLinecap };
        if (tag === "rect") {
          var p = pt(n.x.baseVal.value, n.y.baseVal.value), rw = n.width.baseVal.value * sc, rh = n.height.baseVal.value * sc;
          items.push(Object.assign({ k: "srect", x: p.x, y: p.y, w: rw, h: rh, rad: Math.min((n.rx.baseVal.value || n.ry.baseVal.value || 0) * sc, rw / 2, rh / 2) }, paint));
        } else if (tag === "line") {
          var p1 = pt(n.x1.baseVal.value, n.y1.baseVal.value), p2 = pt(n.x2.baseVal.value, n.y2.baseVal.value);
          items.push(Object.assign({ k: "sline", x1: p1.x, y1: p1.y, x2: p2.x, y2: p2.y, x: Math.min(p1.x, p2.x), y: Math.min(p1.y, p2.y) - sw, w: Math.abs(p2.x - p1.x), h: Math.abs(p2.y - p1.y) + 2 * sw }, paint));
        } else if (tag === "circle") {
          var c = pt(n.cx.baseVal.value, n.cy.baseVal.value), cr = n.r.baseVal.value * sc;
          items.push(Object.assign({ k: "scircle", cx: c.x, cy: c.y, r: cr, x: c.x - cr, y: c.y - cr, w: 2 * cr, h: 2 * cr }, paint));
        } else if (tag === "text" && /\S/.test(n.textContent)) {
          var b = box(n.getBoundingClientRect()), col = fill || { r: 0, g: 0, b: 0, a: 1 };
          var t = n.textContent.replace(/\s+/g, " ").trim(); if (cs.textTransform === "uppercase") t = t.toUpperCase();
          items.push({ k: "text", x: b.x, y: b.y, w: b.w, h: b.h, t: t, f: pdfFont(cs), fs: pdfNum(cs.fontSize) * sc, ls: cs.letterSpacing === "normal" ? 0 : pdfNum(cs.letterSpacing) * sc, c: pdfOver(col, WHITE, op), bg: WHITE, font: cs.fontStyle + " " + cs.fontWeight + " " + (pdfNum(cs.fontSize) * sc) + "px " + cs.fontFamily, dir: cs.direction });
          lines.push([b.y, b.y + b.h]);
        }
      });
    }
    var BLOCKS = /^(block|flex|grid|list-item|table|table-row|flow-root|inline-block|inline-flex|inline-grid)$/;
    function walk(el, bg, op) {
      var cs = w.getComputedStyle(el);
      if (cs.display === "none") return;
      if (el.namespaceURI === "http://www.w3.org/2000/svg") { if (el.tagName.toLowerCase() === "svg") svg(el); return; }
      // A closed <details> (the generic examples) is left out of the PDF entirely: its label would read
      // like a dead link, and browsers keep its hidden content in layout, stacked at one spot.
      if (el.tagName === "DETAILS" && !el.open) return;
      var o = op * (cs.opacity === "" ? 1 : parseFloat(cs.opacity));
      if (!(o > 0)) return;
      var vis = cs.visibility !== "hidden", r = box(el.getBoundingClientRect()), here = bg, fill = vis ? pdfColor(cs.backgroundColor) : null;
      if (fill && fill.a > 0) {
        here = pdfOver(fill, bg, o);
        var parts = cs.display === "inline" ? Array.prototype.map.call(el.getClientRects(), box) : [r];
        parts.forEach(function (p) { if (p.w > 0 && p.h > 0) items.push({ k: "box", x: p.x, y: p.y, w: p.w, h: p.h, rad: radius(cs, p), fill: here }); });
      }
      if (vis && cs.display !== "inline") borders(cs, r, bg, o);
      if (vis) pseudo(el, "::before", r, cs, here, o);
      var drawn = (fill && fill.a > 0) || pdfNum(cs.borderTopWidth) > 0 || pdfNum(cs.borderBottomWidth) > 0;
      if (drawn && BLOCKS.test(cs.display) && r.h > 0) { blocks.push([r.y, r.y + Math.min(r.h, 64)]); blocks.push([r.y + r.h - Math.min(r.h, 24), r.y + r.h]); }
      if (BLOCKS.test(cs.display) && r.h > 0) {
        var keep = /^(H[1-4]|SUMMARY)$/.test(el.tagName) || /\b(eyebrow|sect)\b/.test(el.className) ? 48 : 0;
        blocks.push([r.y, r.y + r.h + keep, /\bcard\b/.test(el.className) && el.querySelector("svg") ? "whole" : false]);
      }
      if (vis && cs.display === "list-item") marker(el, cs, r, here, o);
      for (var n = el.firstChild; n; n = n.nextSibling) {
        if (n.nodeType === 3) { if (vis) text(n, el, cs, here, o); }
        else if (n.nodeType === 1) walk(n, here, o);
      }
      if (vis) pseudo(el, "::after", r, cs, here, o);
    }
    walk(L.root, WHITE, 1);
    return { items: items, blocks: blocks, lines: lines, width: base.width, height: base.height };
  }

  // Choose page cuts: never through a line of text, and where possible not through a small block.
  function pdfCuts(total, pageH, blocks, lines) {
    var n = Math.ceil(total) + 2, soft = new Uint8Array(n), hard = new Uint8Array(n);
    function mark(arr, a, b) { for (var y = Math.max(0, Math.floor(a) + 1), e = Math.min(n, Math.ceil(b)); y < e; y++) arr[y] = 1; }
    lines.forEach(function (l) { mark(hard, l[0], l[1]); });
    blocks.forEach(function (b) { var h = b[1] - b[0]; if (b[2] === true || h <= pageH * 0.35 || b[2] === "whole" && h <= pageH * 0.95) mark(soft, b[0], b[1]); });
    var cuts = [0], start = 0;
    while (total - start > pageH) {
      var lim = Math.floor(start + pageH), y, cut = -1;
      for (y = lim; y > start + pageH * 0.45; y--) if (!soft[y] && !hard[y]) { cut = y; break; }
      if (cut < 0) for (y = lim; y > start + pageH * 0.2; y--) if (!hard[y]) { cut = y; break; }
      if (cut < 0) cut = lim;
      cuts.push(cut); start = cut;
    }
    cuts.push(Math.ceil(total));
    return cuts;
  }

  function pdfDraw(JsPDF, model, title) {
    var doc = new JsPDF({ unit: "pt", format: "a4", compress: true });
    (window.__ABM_FONTS || []).forEach(function (f) { doc.addFileToVFS(f.id + ".ttf", f.b64); doc.addFont(f.id + ".ttf", f.id, "normal"); });
    var PW = doc.internal.pageSize.getWidth(), PH = doc.internal.pageSize.getHeight();
    var k = (PW - 2 * PDF_M.side) / model.width, pageH = (PH - PDF_M.top - PDF_M.bottom) / k;
    var cuts = pdfCuts(model.height, pageH, model.blocks, model.lines), top = 0;
    function X(x) { return PDF_M.side + x * k; }
    function Y(y) { return PDF_M.top + (y - top) * k; }
    function alphaState(fo, so) { doc.setGState(new doc.GState({ opacity: fo, "stroke-opacity": so })); }
    function rr(x, y, w, h, rad, style) { if (rad > 0.4) doc.roundedRect(X(x), Y(y), w * k, h * k, rad * k, rad * k, style); else doc.rect(X(x), Y(y), w * k, h * k, style); }
    function raster(it) {
      var sc = 3, cw = Math.ceil(it.w * sc) + 6, ch = Math.ceil(it.h * sc) + 6, cv = document.createElement("canvas");
      cv.width = cw; cv.height = ch;
      var g = cv.getContext("2d"); g.fillStyle = pdfCss(it.bg); g.fillRect(0, 0, cw, ch); g.scale(sc, sc);
      g.font = it.font || "14px sans-serif"; g.fillStyle = pdfCss(it.c); g.textBaseline = "alphabetic";
      if (it.dir === "rtl") { g.direction = "rtl"; g.textAlign = "right"; g.fillText(it.t, it.w, it.h * it.f.ratio); } else g.fillText(it.t, 0, it.h * it.f.ratio);
      doc.addImage(cv.toDataURL("image/png"), "PNG", X(it.x), Y(it.y), cw / sc * k, ch / sc * k);
    }
    function draw(it) {
      switch (it.k) {
        case "box": doc.setFillColor.apply(doc, pdfRgb(it.fill)); rr(it.x, it.y, it.w, it.h, it.rad, "F"); break;
        case "frame":
          doc.setDrawColor.apply(doc, pdfRgb(it.c)); doc.setLineWidth(it.lw * k);
          doc.setLineDashPattern(it.dash ? it.dash.map(function (v) { return v * k; }) : [], 0);
          rr(it.x, it.y, it.w, it.h, it.rad, "S"); doc.setLineDashPattern([], 0); break;
        case "band":
          doc.saveGraphicsState(); doc.rect(X(it.clip.x), Y(it.clip.y), it.clip.w * k, it.clip.h * k, null); doc.clip(); doc.discardPath();
          doc.setFillColor.apply(doc, pdfRgb(it.c)); rr(it.x, it.y, it.w, it.h, it.rad, "F"); doc.restoreGraphicsState(); break;
        case "dline":
          doc.setDrawColor.apply(doc, pdfRgb(it.c)); doc.setLineWidth(it.lw * k); doc.setLineDashPattern((it.dash || []).map(function (v) { return v * k; }), 0);
          if (it.horiz) doc.line(X(it.x), Y(it.y + it.h / 2), X(it.x + it.w), Y(it.y + it.h / 2)); else doc.line(X(it.x + it.w / 2), Y(it.y), X(it.x + it.w / 2), Y(it.y + it.h));
          doc.setLineDashPattern([], 0); break;
        case "dot":
          doc.setFillColor.apply(doc, pdfRgb(it.c)); doc.setDrawColor.apply(doc, pdfRgb(it.c)); doc.setLineWidth(0.6);
          doc.circle(X(it.x + it.w / 2), Y(it.y + it.h / 2), it.w / 2 * k, it.hollow ? "S" : "F"); break;
        case "srect": case "sline": case "scircle":
          doc.saveGraphicsState(); alphaState(it.fill ? it.fo : 1, it.stroke ? it.so : 1);
          if (it.fill) doc.setFillColor.apply(doc, pdfRgb(it.fill));
          if (it.stroke) { doc.setDrawColor.apply(doc, pdfRgb(it.stroke)); doc.setLineWidth(it.lw * k); doc.setLineDashPattern(it.dash ? it.dash.map(function (v) { return v * k; }) : [], 0); doc.setLineCap(it.cap === "round" ? "round" : it.cap === "square" ? "square" : "butt"); }
          var style = it.fill && it.stroke ? "FD" : it.fill ? "F" : it.stroke ? "S" : null;
          if (style) {
            if (it.k === "srect") rr(it.x, it.y, it.w, it.h, it.rad, style);
            else if (it.k === "scircle") doc.circle(X(it.cx), Y(it.cy), it.r * k, style);
            else if (it.stroke) doc.line(X(it.x1), Y(it.y1), X(it.x2), Y(it.y2));
          }
          doc.restoreGraphicsState(); break;
        case "text":
          if (!it.t) break;
          if (!PDF_GLYPHS.test(it.t) || it.f.id === "helvetica" && /[^\x20-\x7E\xA0-\xFF]/.test(it.t)) { raster(it); break; }
          var size = it.fs * k; doc.setFont(it.f.id, "normal"); doc.setFontSize(size); doc.setTextColor.apply(doc, pdfRgb(it.c));
          var spacing = it.ls * k;
          if (!it.free && it.t.length > 1) {
            var natural = doc.getTextWidth(it.t) + (it.t.length - 1) * spacing, fit = spacing + (it.w * k - natural) / (it.t.length - 1);
            if (Math.abs(fit - spacing) < size * 0.12) spacing = fit;
          }
          doc.text(it.t, X(it.x), Y(it.y) + it.h * k * it.f.ratio, { charSpace: spacing, baseline: "alphabetic" });
          if (it.href) doc.link(X(it.x), Y(it.y), it.w * k, it.h * k, { url: it.href });
          break;
      }
    }
    for (var p = 0; p < cuts.length - 1; p++) {
      if (p) doc.addPage();
      top = cuts[p];
      var bottom = cuts[p + 1];
      doc.saveGraphicsState();
      doc.rect(PDF_M.side - 3, PDF_M.top - 1, PW - 2 * PDF_M.side + 6, (bottom - top) * k + 1, null); doc.clip(); doc.discardPath();
      model.items.forEach(function (it) { if (it.y + it.h > top && it.y < bottom) draw(it); });
      doc.restoreGraphicsState();
    }
    var name = pdfClean(title || "").trim(), n = doc.getNumberOfPages();
    var foot = (name ? name + "  ·  " : "") + "Agent Boundary Map  ·  self-reported, not verified";
    var ff = (window.__ABM_FONTS || []).length ? "plex-400" : "helvetica";
    for (var i = 1; i <= n; i++) {
      doc.setPage(i); doc.setFont(ff, "normal"); doc.setFontSize(7.5); doc.setTextColor(140, 136, 125);
      doc.text(ff === "helvetica" ? pdfSafe(foot) : foot, PDF_M.side, PH - 22);
      doc.text(i + " / " + n, PW - PDF_M.side, PH - 22, { align: "right" });
    }
    doc.setProperties({ title: (name ? name + " - " : "") + "Agent Boundary Map", subject: "Boundary report. Self-reported, not verified.", creator: "Agent Boundary Map" });
    return doc.output("arraybuffer");
  }

  function buildPdf(JsPDF, md, title) {
    return pdfLayout().then(function (L) {
      try { return pdfDraw(JsPDF, pdfCollect(L), title); } finally { L.remove(); }
    });
  }
