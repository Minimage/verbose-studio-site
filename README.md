# Verbose Studio site

Small, free, private browser tools. Live at verbosestudio.com.

## Layout

```
public/                 What gets deployed (Cloudflare Pages output directory)
  index.html            Studio landing page (edit by hand)
  tallpdf/              Tall PDF Slicer, generated. Do not edit by hand.
  pdf-booklet/          PDF Booklet Maker, generated (og.png is kept by hand).
  cut-and-stack/        Cut and Stack PDF Imposer, generated (og.png is kept by hand).
  dust-jacket-maker/    Dust Jacket Maker, generated (og.png is kept by hand).
tools/
  tallpdf/              Source for Tall PDF Slicer
    tool-src.html       The tool itself
    guide-src.html      How-to page source
    build.py            Builds public/tallpdf/ (python3 build.py)
  pdf-booklet/          Source for PDF Booklet Maker
    tool-src.html       The tool itself
    build.py            Builds public/pdf-booklet/ (python3 build.py)
  cut-and-stack/        Source for Cut and Stack PDF Imposer
    tool-src.html       The tool itself
    demo-src.html       The interactive cut and stack demo on the tool page
    build.py            Builds public/cut-and-stack/ (python3 build.py)
  dust-jacket-maker/    Source for Dust Jacket Maker
    tool-src.html       The tool itself
    demo-src.html       The interactive measure, lay out, print and fold demo on the tool page
    build.py            Builds public/dust-jacket-maker/ (python3 build.py)
```

## Adding a new tool

1. Make `tools/<name>/` with its source and a build script that writes to `public/<name>/`.
2. Add a card for it on `public/index.html`.
3. Commit and push. Cloudflare Pages redeploys on its own.

## Deploying

Cloudflare (Workers static assets): build command empty, deploy command `npx wrangler deploy`. `wrangler.jsonc` points it at `public/`.
The contact form key is set in `tools/tallpdf/build.py` (`FORM_KEY`).

## Vendored files

`public/vendor/` holds pdf.js, pdf-lib and the two fonts (Instrument Sans, JetBrains Mono), so the site makes no third-party requests. To update a library, replace the file there.
