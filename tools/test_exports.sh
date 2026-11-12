#!/bin/bash
# Export every example report from index.html as PDF and Markdown, and check:
#   - no console errors, and no request other than the page itself
#   - every finding headline on screen appears in the PDF's text
#   - no two words in the PDF are drawn on top of each other
# Needs gstack browse ($B), poppler (pdfinfo, pdftotext) and python3.
# Usage: tools/test_exports.sh <index.html> <output dir>
set -u
HTML="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"; OUT="$2"; HERE="$(cd "$(dirname "$0")" && pwd)"
B=${B:-~/.claude/skills/gstack/browse/dist/browse}
rm -rf "$OUT"; mkdir -p "$OUT"; fail=0
$B goto "file://$HTML" >/dev/null 2>&1
n=$($B js "document.querySelectorAll('#v-intro button[id^=ex-]').length" 2>&1 | grep -E '^[0-9]+$')
echo "examples: ${n:-0}"
[ "${n:-0}" -gt 0 ] 2>/dev/null || { echo "FAIL: the page did not load or has no example reports (gstack browse opens file:// only under the folder it started in)"; exit 1; }
for i in $(seq 0 $((n - 1))); do
  $B js "document.querySelectorAll('#v-intro button[id^=ex-]')[$i].click()" >/dev/null 2>&1
  name=$($B js "document.getElementById('mapTitle').textContent" 2>&1 | grep -v -- '---' | tail -1)
  slug=$(echo "$name" | tr 'A-Z ' 'a-z-' | tr -cd 'a-z-')
  $B js "(async()=>{const t0=performance.now(); const buf=await window.__tmExport.pdf(window.jspdf.jsPDF,'', document.getElementById('mapTitle').textContent); const u=new Uint8Array(buf); let s=''; for(let i=0;i<u.length;i+=32768){s+=String.fromCharCode.apply(null,u.subarray(i,i+32768));} return 'MS='+Math.round(performance.now()-t0)+' B64='+btoa(s);})()" > "$OUT/raw.txt" 2>&1
  ms=$(grep -o 'MS=[0-9]*' "$OUT/raw.txt" | cut -d= -f2)
  grep -o 'B64=[A-Za-z0-9+/=]*' "$OUT/raw.txt" | sed 's/^B64=//' | base64 -d > "$OUT/$slug.pdf"
  pages=$(pdfinfo "$OUT/$slug.pdf" 2>/dev/null | awk '/^Pages/{print $2}')
  md=$($B js "window.__tmExport.markdown().length" 2>&1 | grep -E '^[0-9]+$')
  $B js "JSON.stringify(Array.from(document.querySelectorAll('#findings h3')).map(h=>h.textContent.trim()))" 2>&1 | grep '^\[' > "$OUT/heads.json"
  pdftotext "$OUT/$slug.pdf" "$OUT/$slug.txt" 2>/dev/null
  missing=$(python3 -I -c "
import json,sys,re
heads=json.load(open(sys.argv[1])); txt=re.sub(r'\s+',' ',open(sys.argv[2]).read())
print(sum(1 for h in heads if re.sub(r'\s+',' ',h) not in txt))" "$OUT/heads.json" "$OUT/$slug.txt")
  pdftotext -bbox "$OUT/$slug.pdf" "$OUT/$slug.bbox.html" 2>/dev/null
  overlaps=$(python3 -I "$HERE/overlap.py" "$OUT/$slug.bbox.html" | awk -F': ' '/overlapping/{print $2}')
  [ "${missing:-1}" = "0" ] && [ "${overlaps:-1}" = "0" ] && [ -n "$pages" ] || fail=1
  echo "$name | pdf ${ms}ms, $pages pages | headlines missing: $missing | overlapping words: $overlaps | markdown $md chars"
  # Summary report: at most 2 pages, every main finding in the PDF, no overlaps, and the top
  # actions never repeat a finding's headline.
  $B js "(async()=>{const buf=await window.__tmExport.pdf(window.jspdf.jsPDF,'',document.getElementById('mapTitle').textContent,'summary'); const u=new Uint8Array(buf); let s=''; for(let i=0;i<u.length;i+=32768){s+=String.fromCharCode.apply(null,u.subarray(i,i+32768));} return 'B64='+btoa(s);})()" > "$OUT/raw.txt" 2>&1
  grep -o 'B64=[A-Za-z0-9+/=]*' "$OUT/raw.txt" | sed 's/^B64=//' | base64 -d > "$OUT/$slug.summary.pdf"
  $B js "window.__tmExport.summary()" 2>&1 | grep -v -- '---' > "$OUT/$slug.summary.md"
  spages=$(pdfinfo "$OUT/$slug.summary.pdf" 2>/dev/null | awk '/^Pages/{print $2}')
  pdftotext "$OUT/$slug.summary.pdf" "$OUT/$slug.summary.txt" 2>/dev/null
  scheck=$(python3 -I -c "
import re,sys
md=open(sys.argv[1]).read(); txt=re.sub(r'\s+',' ',open(sys.argv[2]).read())
heads=[re.sub(r'\s+',' ',h) for h in re.findall(r'^- \*\*F\d+\.\*\* (.+?) _', md, re.M)]
acts=md.split('## Top actions')[1].split('\n## ')[0] if '## Top actions' in md else ''
print(sum(1 for h in heads if h not in txt), sum(1 for h in heads if h.rstrip('.') in acts))" "$OUT/$slug.summary.md" "$OUT/$slug.summary.txt")
  smissing=${scheck% *}; srepeat=${scheck#* }
  pdftotext -bbox "$OUT/$slug.summary.pdf" "$OUT/$slug.summary.bbox.html" 2>/dev/null
  soverlaps=$(python3 -I "$HERE/overlap.py" "$OUT/$slug.summary.bbox.html" | awk -F': ' '/overlapping/{print $2}')
  [ -n "$spages" ] && [ "$spages" -le 2 ] && [ "${smissing:-1}" = "0" ] && [ "${srepeat:-1}" = "0" ] && [ "${soverlaps:-1}" = "0" ] || fail=1
  echo "  summary | $spages pages | findings missing: $smissing | repeated in actions: $srepeat | overlapping words: $soverlaps"
  $B js "document.getElementById('backIntroBtn').click()" >/dev/null 2>&1
done
errs=$($B console --errors 2>&1 | grep -v -- '---')
echo "console: $errs"; [ "$errs" = "(no console errors)" ] || fail=1
other=$($B network 2>&1 | grep -E '^(GET|POST|PUT|HEAD)' | grep -vF "file://$HTML")
echo "requests other than the page: ${other:-none}"; [ -z "$other" ] || fail=1
[ $fail = 0 ] && echo "PASS" || { echo "FAIL"; exit 1; }
