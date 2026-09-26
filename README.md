# Verbose Studio site

Small, free, private browser tools. Live at verbosestudio.com.

## Layout

```
public/                 What gets deployed (Cloudflare Pages output directory)
  index.html            Studio landing page (edit by hand)
  tallpdf/              Tall PDF Slicer, generated. Do not edit by hand.
tools/
  tallpdf/              Source for Tall PDF Slicer
    tool-src.html       The tool itself
    guide-src.html      How-to page source
    build.py            Builds public/tallpdf/ (python3 build.py)
```

## Adding a new tool

1. Make `tools/<name>/` with its source and a build script that writes to `public/<name>/`.
2. Add a card for it on `public/index.html`.
3. Commit and push. Cloudflare Pages redeploys on its own.

## Deploying

Cloudflare Pages: build command empty, output directory `public`.
The contact form key is set in `tools/tallpdf/build.py` (`FORM_KEY`).
