  /* ---------- Summary report: one or two pages for people the report is forwarded to ----------
     Injected by tools/build_index.py inside the app's closure, so it uses the app's own helpers.
     Main findings say what's wrong or unknown; top actions say what to do and point to a finding
     by number, never repeating its headline. Top actions use the app's existing ranking (see
     topActions). The full report stays the source of every detail. */
  var SUM_GUIDE = "__GUIDE__", SUM_REGISTER = "__REGISTER__";
  var SUM_FULL = "Download the full report from the app for the details of every finding.";

  // The top actions: the main action of each finding, in the existing risk order (route step first,
  // then unauthorized access, sensitive information, exposure, control weakness). A finding without
  // an action is skipped rather than leaving a gap, and the list is never padded.
  function topActions(risk, s, a) {
    var out = [];
    for (var i = 0; i < risk.length && out.length < 3; i++) if (actsFor(risk[i].te, s, a)[0]) out.push(risk[i]);
    return out;
  }
  function reportMode() {
    var r = document.querySelector('input[name="rmode"]:checked');
    return r && r.value === "full" ? "full" : "summary";
  }
  function sumData() {
    var c = current(), s = c.s, a = c.a, E = evalAll(s, a), split = splitRisk(E.risk);
    var findings = split.main.map(function (x) { return x.te; }).concat(E.findTh);
    return {
      c: c, s: s, a: a, E: E, res: evaluate(s, a), findings: findings,
      acts: topActions(E.risk, s, a).map(function (x) { return { x: x, ac: actsFor(x.te, s, a)[0], f: findings.indexOf(x.te) + 1 }; }),
      other: split.other.length, un: unansweredList(s, a).length, held: E.held.length
    };
  }
  function sumStatus(te, s) { return te.worst ? lbl(te.worst.st, s) : "Not answered"; }
  function sumIds(te) { return te.vis.map(function (q) { return dispId(q); }).join(", "); }
  function sumHow(r, s) {
    var rt = routeText(r, s);
    if (r.label === "none") return rt;
    // The step list already names interrupted steps; the explanation adds something only for possible or incomplete routes.
    var extra = rt && (r.label === "potential" || r.label === "incomplete") ? ". " + rt : "";
    return r.steps.map(function (x) { return x.name + ": " + STEPLBL[x.state].toLowerCase() + " (" + x.ids.map(function (q) { return q === "sens" ? "profile" : dispId(q); }).join(", ") + ")"; }).join(" → ") + extra;
  }
  function sumWhy(x) { var w = x.p.why.join("; "); return "Why first: " + w + "."; }
  function sumFix(t) { return t.f ? "Fixes F" + t.f + "." : "Fixes: " + endDot(headOf(t.x.te, current().a)); }
  function sumCounts(D) {
    var p = [];
    if (D.other) p.push(D.other + " other gap" + (D.other === 1 ? "" : "s"));
    if (D.un) p.push(D.un + " unanswered question" + (D.un === 1 ? "" : "s"));
    if (D.held) p.push(D.held + " theme" + (D.held === 1 ? "" : "s") + " reported as enforced outside the model (not verified)");
    return p.length ? "Also: " + p.join(" · ") + ". The full report has the details." : "";
  }
  function sumEmpty(D) {
    return "No weak or unknown answers." + (D.held ? " " + D.held + " theme" + (D.held === 1 ? "" : "s") + " reported as enforced outside the model (not verified)." : "");
  }

  function summaryMarkdown() {
    var D = sumData(), s = D.s, out = [];
    out.push("# Boundary summary: " + (D.c.name || "Your agent") + (viewing.example !== null ? " (illustrative example)" : ""));
    out.push("", profileLine(s), "", "_Generated " + new Date().toISOString().slice(0, 10) + " with Agent Boundary Map. Answers are self-reported, and “reported as enforced” hasn't been verified. This is the summary: " + SUM_FULL.charAt(0).toLowerCase() + SUM_FULL.slice(1) + "_");
    out.push("", "## Verdict", "", verdictText(D.E.R));
    out.push("", "## Routes", "", "| Route | Status | Where it runs |", "| --- | --- | --- |");
    D.E.R.forEach(function (r) { out.push("| " + r.name + " | " + RLABEL[r.label] + " | " + mdEsc(sumHow(r, s)) + " |"); });
    if (!D.findings.length) out.push("", "## Findings", "", sumEmpty(D));
    else {
      out.push("", "## Main findings", "", "What's wrong or not known.", "");
      D.findings.forEach(function (te, i) { out.push("- **F" + (i + 1) + ".** " + endDot(headOf(te, D.a)) + " _" + sumStatus(te, s) + "_ · " + sumIds(te)); });
    }
    if (D.acts.length) {
      out.push("", "## Top actions", "", "What to do first.", "");
      D.acts.forEach(function (t, i) {
        var p = actParts(fillT(t.ac.t, s));
        out.push((i + 1) + ". " + p.lead + (t.ac.tags && t.ac.tags.length ? " _[" + t.ac.tags.join(", ") + "]_" : ""));
        out.push("   " + sumWhy(t.x) + " " + sumFix(t));
        if (showOwners(s) && t.ac.own) out.push("   " + ownerLine(t.ac, s));
      });
    }
    var cn = sumCounts(D); if (cn && D.findings.length) out.push("", cn);
    out.push("", "## Boundaries", ""); D.res.forEach(function (r) { out.push("- **" + r.b.name + ":** " + (r.status ? boxCount(r).text + "; weakest: " + LBL[r.status].toLowerCase() : "not answered")); });
    out.push("", "---", "", "Evidence behind these questions: [why we ask them](" + SUM_GUIDE + ") · [evidence register](" + SUM_REGISTER + ").", "", "The rule behind every question: the model may propose, but something outside the model must authorize.");
    return out.join("\n") + "\n";
  }

  // The summary laid out as page content, for the PDF renderer (never shown on screen).
  var MINI_CSS = [
    "#v-sum { display: flex; flex-direction: column; gap: 14px; }",
    "#v-sum h2 { font-size: 1.5rem; margin: 2px 0 0; }",
    "#v-sum .sh { font-family: var(--display); font-size: 1.1rem; font-weight: 600; margin: 0 0 8px; }",
    "#v-sum p { margin: 0; }",
    "#v-sum .sub { color: var(--fg2); margin-top: 4px; }",
    "#v-sum table { width: 100%; border-collapse: collapse; font-size: 0.84rem; margin-top: 10px; }",
    "#v-sum th { text-align: left; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted); font-weight: 600; padding: 0 8px 6px 0; }",
    "#v-sum td { text-align: left; vertical-align: top; padding: 7px 8px 7px 0; border-top: 1px solid var(--border); }",
    "#v-sum td.rn { font-weight: 600; white-space: nowrap; }",
    "#v-sum td.rs { white-space: nowrap; }",
    "#v-sum td.rw { color: var(--fg2); }",
    "#v-sum ol, #v-sum ul { margin: 0; padding-left: 0; list-style: none; display: flex; flex-direction: column; gap: 7px; }",
    "#v-sum li { font-size: 0.88rem; display: flex; gap: 8px; align-items: baseline; }",
    "#v-sum .fid { font-family: var(--mono); font-size: 0.76rem; color: var(--muted); min-width: 28px; }",
    "#v-sum .fb { flex: 1; min-width: 0; }",
    "#v-sum .fq { font-family: var(--mono); font-size: 0.74rem; color: var(--muted); margin-left: 6px; }",
    "#v-sum .fb .chip { margin-left: 6px; }",
    "#v-sum .am { display: block; font-size: 0.8rem; color: var(--fg2); margin-top: 3px; }",
    "#v-sum .tagt { font-size: 0.72rem; color: var(--muted); margin-left: 6px; }",
    "#v-sum .counts { font-size: 0.84rem; color: var(--fg2); }",
    "#v-sum .note a { color: var(--accent); }",
    "@media (max-width: 680px) { #v-sum table, #v-sum tbody, #v-sum tr, #v-sum td { display: block; } #v-sum tr:first-child { display: none; } #v-sum td { border-top: 0; padding: 2px 0; } #v-sum tr { border-top: 1px solid var(--border); padding: 8px 0; } #v-sum td.rn, #v-sum td.rs { white-space: normal; } }",
    "#v-map.sumv > .wrap > :not(.banner):not(#mapHeadCard):not(#copyCard):not(#sumView) { display: none !important; }",
    "#v-map:not(.sumv) #sumView { display: none; }"
  ].join("\n");
  // On screen too: the summary view uses the same styles as the PDF (the PDF copies the page's styles).
  (function () { var st = document.createElement("style"); st.textContent = MINI_CSS; document.head.appendChild(st); })();

  // The Summary | Full switch changes what's on screen; the downloads follow it and say which they give.
  function applyView() {
    var m = reportMode(), vm = document.getElementById("v-map"), sv = document.getElementById("sumView");
    vm.classList.toggle("sumv", m === "summary");
    sv.innerHTML = ""; if (m === "summary") sv.appendChild(miniDom(true));
    var w = m === "summary" ? "summary" : "full";
    document.getElementById("mdBtn").textContent = "Download " + w + " Markdown";
    document.getElementById("pdfBtn").textContent = "Download " + w + " PDF";
  }
  Array.prototype.forEach.call(document.querySelectorAll('input[name="rmode"]'), function (r) { r.addEventListener("change", applyView); });

  // screen: the in-page summary view, under the page's own header (no header card; the phone
  // layout gets the stacked map). Otherwise the PDF version, with its own header card.
  function miniDom(screen) {
    var D = sumData(), s = D.s, a = D.a;
    var sec = el("section"); sec.id = "v-sum";
    var head = el("div", "card");
    head.appendChild(el("span", "eyebrow", "Boundary summary" + (viewing.example !== null ? " · illustrative example" : "")));
    head.appendChild(el("h2", null, D.c.name || "Your agent"));
    head.appendChild(el("p", "sub", profileLine(s)));
    head.appendChild(el("p", "note", "Generated " + new Date().toISOString().slice(0, 10) + ". Answers are self-reported, and “reported as enforced” hasn't been verified. " + SUM_FULL));
    if (!screen) sec.appendChild(head);

    var v = el("div", "card");
    v.appendChild(el("p", "sh", "Verdict"));
    v.appendChild(el("p", "verdict-line", verdictText(D.E.R)));
    var tb = el("table"), tr = el("tr");
    ["Route", "Status", "Where it runs"].forEach(function (h) { tr.appendChild(el("th", null, h)); }); tb.appendChild(tr);
    D.E.R.forEach(function (r) {
      var row = el("tr"); row.appendChild(el("td", "rn", r.name));
      var st = el("td", "rs"); var ch = el("span", "chip c-" + ({ supported: "open", potential: "model", incomplete: "model", interrupted: "held", none: "unknown" }[r.label] || "unknown"), RLABEL[r.label]); st.appendChild(ch); row.appendChild(st);
      row.appendChild(el("td", "rw", sumHow(r, s))); tb.appendChild(row);
    });
    v.appendChild(tb); sec.appendChild(v);

    var f = el("div", "card");
    if (!D.findings.length) { f.appendChild(el("p", "sh", "Findings")); f.appendChild(el("p", null, sumEmpty(D))); }
    else {
      f.appendChild(el("p", "sh", "Main findings: what's wrong or not known"));
      var ol = el("ol");
      D.findings.forEach(function (te, i) {
        var li = el("li"); li.appendChild(el("span", "fid", "F" + (i + 1)));
        var b = el("span", "fb"); b.appendChild(document.createTextNode(endDot(headOf(te, a))));
        if (te.worst) b.appendChild(rchip(te.worst.st, s)); b.appendChild(el("span", "fq", sumIds(te)));
        li.appendChild(b); ol.appendChild(li);
      });
      f.appendChild(ol);
      var cn = sumCounts(D); if (cn) { var cp = el("p", "counts", cn); cp.style.marginTop = "10px"; f.appendChild(cp); }
    }
    sec.appendChild(f);

    if (D.acts.length) {
      var t = el("div", "card"); t.appendChild(el("p", "sh", "Top actions: what to do first"));
      var al = el("ol");
      D.acts.forEach(function (x, i) {
        var li = el("li"); li.appendChild(el("span", "fid", (i + 1) + "."));
        var b = el("span", "fb"), p = actParts(fillT(x.ac.t, s));
        b.appendChild(document.createTextNode(p.lead));
        if (x.ac.tags && x.ac.tags.length) b.appendChild(el("span", "tagt", "[" + x.ac.tags.join(", ") + "]"));
        b.appendChild(el("span", "am", sumWhy(x.x) + " " + sumFix(x)));
        if (showOwners(s) && x.ac.own) b.appendChild(el("span", "am", ownerLine(x.ac, s)));
        li.appendChild(b); al.appendChild(li);
      });
      t.appendChild(al); sec.appendChild(t);
    }

    var m = el("div", "card");
    m.appendChild(el("p", "sh", "Boundary map"));
    var lg = el("div", "legend"); lg.style.margin = "0 0 6px"; drawLegend(lg); m.appendChild(lg);
    var mw = el("div", "mapwrap"), ms = el("div"); mw.appendChild(ms); drawMap(ms, D.res); m.appendChild(mw);
    if (screen) { var sk = el("div", "stack-map"); drawStack(sk, D.res); m.appendChild(sk); }
    sec.appendChild(m);

    var ft = el("p", "note"), ev = function (href, text) { var x = el("a", null, text + " ↗"); x.href = href; x.target = "_blank"; x.rel = "noopener"; x.setAttribute("aria-label", text + " (opens in a new tab)"); return x; };
    ft.appendChild(document.createTextNode("Evidence behind these questions: ")); ft.appendChild(ev(SUM_GUIDE, "why we ask them"));
    ft.appendChild(document.createTextNode(" · ")); ft.appendChild(ev(SUM_REGISTER, "evidence register")); ft.appendChild(document.createTextNode("."));
    sec.appendChild(ft);
    sec.appendChild(el("p", "note", "The rule behind every question: the model may propose, but something outside the model must authorize."));
    return sec;
  }
