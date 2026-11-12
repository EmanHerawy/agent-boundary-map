# Building index.html

`index.html` is generated. Don't edit it by hand: change the source or these scripts and rebuild.

| File | What it does |
|---|---|
| `build_fonts.py` | Pins the variable fonts to static weights, subsets them to Latin and writes `fonts.json` (base64 plus baseline metrics). |
| `build_index.py` | Starts from the v20 export (`src/v20-export.html`, the published Agent Trust Map artifact, unchanged): renames the product, bundles fonts and jsPDF, adds the network-blocking CSP, swaps in the PDF renderer and the browser download path. Each replacement asserts its count. |
| `pdf_render.js` | The PDF renderer: lays the report out in a hidden frame and draws it into jsPDF. |
| `test_exports.sh` | Exports all five example reports and checks headlines, overlapping text, console errors and network requests. |
| `overlap.py` | Finds words drawn on top of each other in a PDF (used by the test). |

## Inputs (not committed)

- Fonts, from `google/fonts` at commit `c30b221beb0c1da59d563feb91ec8656a1fa972a`, saved as
  `fraunces__Fraunces[SOFT,WONK,opsz,wght].ttf`, `ibmplexsans__IBMPlexSans[wdth,wght].ttf` and
  `jetbrainsmono__JetBrainsMono[wght].ttf` in one folder.
- jsPDF: `npm pack jspdf@4.2.1`, check the tarball against the integrity in `NOTICE`, and use
  `package/dist/jspdf.umd.min.js`.

## Steps

```sh
python3 -m venv .venv && .venv/bin/pip install fonttools
.venv/bin/python -I tools/build_fonts.py <font folder> build/fonts
python3 -I tools/build_index.py src/v20-export.html build/fonts/fonts.json <jspdf.umd.min.js> tools/pdf_render.js index.html
tools/test_exports.sh index.html build/test
```

The test needs gstack browse and poppler (`pdfinfo`, `pdftotext`).
