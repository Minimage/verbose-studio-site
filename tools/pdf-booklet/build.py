import re, json, os

# Builds public/pdf-booklet/ from tool-src.html. Run: python3 build.py
# The site chrome (header, footer, contact form, shared CSS) follows tools/tallpdf/build.py so both tools look the same.

HERE = os.path.dirname(os.path.abspath(__file__))
tool = open(os.path.join(HERE, 'tool-src.html')).read()

def css_of(src):
    return re.search(r'<style>\n(.*?)</style>', src, re.S).group(1)

def drop_rule(css, sel):
    return re.sub(r'(?m)^' + re.escape(sel) + r' \{[^}]*\}\n', '', css, count=1)

# ---------- tokens and tool CSS ----------
tool_css = css_of(tool)
cut = tool_css.index('\n* { box-sizing')
tokens = tool_css[:cut]
tool_rest = tool_css[cut:]
tool_rest = drop_rule(tool_rest, 'body')          # the site sets the body
tool_rest = drop_rule(tool_rest, '[hidden]')
tool_rest = drop_rule(tool_rest, '*')

EXTRA_TOKENS = """
:root { --accent-soft: rgba(14, 116, 144, 0.1); --cut-ink: #ffffff; --shadow: 0 1px 2px rgba(20, 30, 50, 0.08), 0 12px 32px rgba(20, 30, 50, 0.1); }
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) { --accent-soft: rgba(76, 195, 220, 0.13); --cut-ink: #2a0715; --shadow: 0 1px 2px rgba(0, 0, 0, 0.5), 0 12px 32px rgba(0, 0, 0, 0.45); }
}
:root[data-theme="dark"] { --accent-soft: rgba(76, 195, 220, 0.13); --cut-ink: #2a0715; --shadow: 0 1px 2px rgba(0, 0, 0, 0.5), 0 12px 32px rgba(0, 0, 0, 0.45); }
"""

BASE_CSS = """
* { box-sizing: border-box; }
[hidden] { display: none !important; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: var(--font-ui);
  font-size: 17px;
  line-height: 1.55;
  padding-inline: 16px;
  padding-block: 0 48px;
}
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }
a { color: var(--accent); }
.wrap { max-width: 1120px; margin: 0 auto; }
.wrap.narrow { max-width: 46rem; }

.site-head { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px 24px; padding-block: 18px; }
.brand { display: inline-flex; align-items: center; gap: 10px; font-weight: 700; font-size: 18px; letter-spacing: -0.01em; color: var(--ink); text-decoration: none; }
.brand svg { flex: none; }
.site-nav { display: flex; flex-wrap: wrap; gap: 4px 6px; }
.site-nav a {
  padding: 7px 12px; border-radius: 8px; color: var(--ink-2); text-decoration: none; font-size: 15px; font-weight: 500;
}
.site-nav a:hover { background: var(--surface); color: var(--ink); }
.site-nav a[aria-current="page"] { color: var(--ink); background: var(--surface); box-shadow: inset 0 -2px 0 var(--accent); border-radius: 8px 8px 4px 4px; }

.site-foot { margin-top: 56px; padding-top: 24px; border-top: 1px solid var(--line); display: flex; flex-wrap: wrap; justify-content: space-between; gap: 12px 24px; color: var(--ink-2); font-size: 14px; }
.site-foot nav { display: flex; flex-wrap: wrap; gap: 6px 18px; }
.site-foot a { color: var(--ink-2); }
.site-foot a:hover { color: var(--ink); }

.page-hero { display: grid; gap: 12px; padding-block: 20px 20px; max-width: 46rem; }
.page-hero h1 { margin: 0; font-size: clamp(30px, 5vw, 44px); line-height: 1.1; font-weight: 700; letter-spacing: -0.025em; text-wrap: balance; }
.page-hero p { margin: 0; font-size: 19px; color: var(--ink-2); max-width: 38rem; }
.page-hero .newhere { font-size: 15px; }
.page-hero .newhere a { font-weight: 600; }

.sec { padding-top: 56px; display: grid; grid-template-columns: minmax(0, 1fr); gap: 18px; }
.sec h2 { margin: 0; font-size: clamp(24px, 3.4vw, 32px); line-height: 1.15; letter-spacing: -0.02em; text-wrap: balance; }
.sec > p { margin: 0; color: var(--ink-2); max-width: 44rem; }
.cards { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
.card { display: grid; align-content: start; gap: 8px; padding: 20px; background: var(--surface); border: 1px solid var(--line); border-radius: 14px; }
.card h3 { margin: 0; font-size: 18px; letter-spacing: -0.01em; }
.card p { margin: 0; color: var(--ink-2); font-size: 15.5px; }
.card .ico { width: 44px; height: 30px; }
.uses { margin: 0; padding: 0; list-style: none; display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 240px), 1fr)); gap: 10px; max-width: 46rem; }
.uses li { padding: 12px 16px; background: var(--surface); border: 1px solid var(--line); border-radius: 12px; font-weight: 600; }
.uses li span { display: block; font-weight: 400; font-size: 15px; color: var(--ink-2); }
.steps { margin: 0; padding-left: 22px; display: grid; gap: 8px; max-width: 44rem; color: var(--ink-2); }
.steps b { color: var(--ink); font-weight: 600; }
.faq { display: grid; gap: 10px; max-width: 46rem; }
.faq details { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; }
.faq summary { cursor: pointer; padding: 14px 18px; font-weight: 600; list-style: none; display: flex; justify-content: space-between; gap: 16px; align-items: center; }
.faq summary::-webkit-details-marker { display: none; }
.faq summary::after { content: "+"; font-family: var(--font-mono); font-size: 18px; color: var(--accent); }
.faq details[open] summary::after { content: "\\2212"; }
.faq details p { margin: 0; padding: 0 18px 16px; color: var(--ink-2); }
.band-cta { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 16px 24px; padding: 26px clamp(20px, 4vw, 34px); border-radius: 16px; background: var(--surface); border: 1px solid var(--line); }
.band-cta h2 { margin: 0; font-size: 24px; letter-spacing: -0.015em; }
.band-cta p { margin: 4px 0 0; color: var(--ink-2); font-size: 16px; }
.pbtn { display: inline-flex; align-items: center; justify-content: center; min-height: 44px; padding: 9px 20px; border-radius: 9px; background: var(--accent); color: var(--accent-ink); font-weight: 600; font-size: 15px; text-decoration: none; }
.pbtn:hover { background: var(--accent-hover); }

.prose { display: grid; gap: 14px; padding-bottom: 8px; }
.prose h2 { margin: 26px 0 0; font-size: 24px; letter-spacing: -0.015em; }
.prose p, .prose li { color: var(--ink-2); margin: 0; }
.prose ul, .prose ol { margin: 0; padding-left: 22px; display: grid; gap: 8px; }
.prose b { color: var(--ink); font-weight: 600; }
.prose .meta { font-family: var(--font-mono); font-size: 13px; color: var(--ink-2); }

@media (max-width: 860px) { .cards { grid-template-columns: minmax(0, 1fr); } }
"""

# ---------- brand mark: an open booklet with the fold dashed ----------
MARK = ('<svg width="30" height="30" viewBox="0 0 30 30" aria-hidden="true">'
        '<path d="M15 6 L3 3 V25 L15 28 Z" fill="#fff" stroke="var(--line)" stroke-width="1.5" stroke-linejoin="round"/>'
        '<path d="M15 6 L27 3 V25 L15 28 Z" fill="#fff" stroke="var(--line)" stroke-width="1.5" stroke-linejoin="round"/>'
        '<rect x="6" y="9" width="6" height="2.2" rx="1" fill="#39424f"/><rect x="6" y="13" width="6" height="5" rx="1" fill="#2a8ea3"/>'
        '<rect x="18" y="9" width="6" height="2" rx="1" fill="#c8cfda"/><rect x="18" y="13" width="6" height="2" rx="1" fill="#c8cfda"/><rect x="18" y="17" width="4" height="2" rx="1" fill="#c8cfda"/>'
        '<line x1="15" y1="2" x2="15" y2="29.5" stroke="var(--cut)" stroke-width="1.8" stroke-dasharray="3 2"/></svg>')
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 30'%3E"
           "%3Cpath d='M15 6 L3 3 V25 L15 28 Z' fill='white' stroke='%230e7490' stroke-width='1.5' stroke-linejoin='round'/%3E"
           "%3Cpath d='M15 6 L27 3 V25 L15 28 Z' fill='white' stroke='%230e7490' stroke-width='1.5' stroke-linejoin='round'/%3E"
           "%3Crect x='6' y='13' width='6' height='5' rx='1' fill='%232a8ea3'/%3E"
           "%3Cline x1='15' y1='2' x2='15' y2='29.5' stroke='%23d6246e' stroke-width='2' stroke-dasharray='3 2'/%3E%3C/svg%3E")

NAME = 'PDF Booklet Maker'
SLUG = 'pdf-booklet'
PAGES = [('index.html', 'Tool'), ('how-to.html', 'How to use'), ('about.html', 'About'), ('privacy.html', 'Privacy')]

def header(current):
    links = ''.join('<a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if h == current else '', n) for h, n in PAGES)
    return ('<header class="site-head"><a class="brand" href="index.html">%s<span>%s</span></a>'
            '<nav class="site-nav" aria-label="Main">%s<button type="button" class="navbtn" data-contact>Contact</button></nav></header>' % (MARK, NAME, links))

def footer():
    return ('<footer class="site-foot"><span>A free tool by <a href="../">Verbose Studio</a>. Your files stay in your browser.</span>'
            '<nav aria-label="Footer"><a href="index.html">Tool</a><a href="how-to.html">How to use</a>'
            '<a href="about.html">About</a><a href="privacy.html">Privacy</a><button type="button" class="linkbtn" data-contact>Contact</button></nav></footer>')

SITE = 'https://verbosestudio.com'
def share_meta(page, title, desc):
    url = SITE + '/' + SLUG + '/' + page
    img = SITE + '/' + SLUG + '/og.png'
    return ('<link rel="canonical" href="%s"><meta name="theme-color" content="#0e7490"><meta property="og:url" content="%s"><meta property="og:site_name" content="Verbose Studio">'
            '<meta property="og:image" content="%s"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
            '<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="%s"><meta name="twitter:description" content="%s"><meta name="twitter:image" content="%s">'
            % (url, url, img, title, desc, img))

def doc(title, desc, css, body, scripts, page):
    css = css + CONTACT_CSS
    body = body + CONTACT_HTML
    scripts = scripts + CONTACT_JS
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<title>%s</title>\n<meta name="description" content="%s"><meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:type" content="website">\n'
            '%s\n<link rel="icon" href="%s"><link rel="stylesheet" href="../vendor/fonts.css">\n<style>\n%s</style>\n</head>\n<body>\n%s\n%s\n</body>\n</html>\n'
            % (title, desc, title, desc, share_meta(page, title, desc), FAVICON, css, body, scripts))


FORM_ENDPOINT = 'https://api.web3forms.com/submit'
FORM_KEY = '00640895-65d1-4e34-b1c1-8dc6575510a4'   # public Web3Forms key, same form as Tall PDF Slicer
TOOL_TAG = NAME

CONTACT_CSS = """
.navbtn, .linkbtn { font: inherit; cursor: pointer; border: 0; background: none; }
.navbtn { padding: 7px 12px; border-radius: 8px; color: var(--ink-2); font-size: 15px; font-weight: 500; }
.navbtn:hover { background: var(--surface); color: var(--ink); }
.linkbtn { padding: 0; color: var(--ink-2); font-size: 14px; text-decoration: underline; }
.linkbtn:hover { color: var(--ink); }
dialog.contact { width: min(30rem, calc(100vw - 32px)); max-height: calc(100vh - 32px); padding: 0; border: 1px solid var(--line); border-radius: 16px; background: var(--surface); color: var(--ink); box-shadow: var(--shadow); overflow: auto; }
dialog.contact::backdrop { background: rgba(10, 14, 22, 0.55); }
.contact form, .contact .done { display: grid; gap: 14px; padding: 24px; }
.contact h2 { margin: 0; font-size: 22px; letter-spacing: -0.015em; }
.contact .lead { margin: -6px 0 0; color: var(--ink-2); font-size: 15px; }
.contact label { display: grid; gap: 6px; font-size: 14px; font-weight: 600; }
.contact label small { font-weight: 400; color: var(--ink-2); }
.contact select, .contact textarea, .contact input[type=email] { font: inherit; font-weight: 400; font-size: 16px; padding: 10px 12px; border-radius: 9px; border: 1px solid var(--line); background: var(--bg); color: var(--ink); width: 100%; }
.contact textarea { min-height: 130px; resize: vertical; }
.contact .row { display: flex; flex-wrap: wrap; gap: 10px; justify-content: flex-end; align-items: center; }
.contact .ghost { font: inherit; font-size: 15px; font-weight: 600; min-height: 44px; padding: 9px 16px; border-radius: 9px; border: 1px solid var(--line); background: none; color: var(--ink); cursor: pointer; }
.contact .pbtn { border: 0; font: inherit; font-size: 15px; font-weight: 600; cursor: pointer; }
.contact .pbtn[disabled] { opacity: .6; cursor: default; }
.contact .msg { margin: 0; font-size: 14px; color: var(--ink-2); }
.contact .msg.err { color: var(--cut); }
.contact .trap { position: absolute; left: -9999px; width: 1px; height: 1px; overflow: hidden; }
"""

CONTACT_HTML = """
<dialog class="contact" id="contactDlg" aria-labelledby="contactTitle">
  <form id="contactForm" method="dialog" novalidate>
    <h2 id="contactTitle">Contact us</h2>
    <p class="lead">Found a problem, or want a feature? Tell us. We read everything.</p>
    <label>What is it about?
      <select name="topic">
        <option>Suggestion</option><option>Something is not working</option><option>Question</option><option>Other</option>
      </select>
    </label>
    <label>Your message
      <textarea name="message" required maxlength="4000" placeholder="What happened, or what would you like to see?"></textarea>
    </label>
    <label>Your email <small>(optional, only if you would like a reply)</small>
      <input type="email" name="email" autocomplete="email" maxlength="200">
    </label>
    <div class="trap" aria-hidden="true"><label>Leave this empty <input type="checkbox" name="botcheck" tabindex="-1" autocomplete="off"></label></div>
    <p class="msg" id="contactMsg" role="status" aria-live="polite"></p>
    <div class="row"><button type="button" class="ghost" id="contactCancel">Cancel</button><button type="submit" class="pbtn" id="contactSend">Send</button></div>
  </form>
  <div class="done" id="contactDone" hidden>
    <h2>Thank you</h2>
    <p class="lead" style="margin:0">Your message was sent.</p>
    <div class="row"><button type="button" class="pbtn" id="contactClose">Close</button></div>
  </div>
</dialog>
"""

CONTACT_JS = """<script>
(function () {
  var dlg = document.getElementById('contactDlg'); if (!dlg) return;
  var form = document.getElementById('contactForm'), done = document.getElementById('contactDone');
  var msg = document.getElementById('contactMsg'), send = document.getElementById('contactSend');
  var ENDPOINT = '__ENDPOINT__', KEY = '__KEY__', TOOL = '__TOOL__';
  function open() {
    form.hidden = false; done.hidden = true; msg.textContent = ''; msg.className = 'msg'; send.disabled = false;
    if (dlg.showModal) dlg.showModal(); else dlg.setAttribute('open', '');
    var t = form.querySelector('textarea'); if (t) t.focus();
  }
  function close() { if (dlg.close) dlg.close(); else dlg.removeAttribute('open'); }
  document.querySelectorAll('[data-contact]').forEach(function (b) { b.addEventListener('click', open); });
  document.getElementById('contactCancel').addEventListener('click', close);
  document.getElementById('contactClose').addEventListener('click', close);
  dlg.addEventListener('click', function (e) { if (e.target === dlg) close(); });
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var f = form.elements;
    if (!f.message.value.trim()) { msg.className = 'msg err'; msg.textContent = 'Please write a short message first.'; f.message.focus(); return; }
    if (f.email.value && !f.email.checkValidity()) { msg.className = 'msg err'; msg.textContent = 'That email does not look right. You can also leave it blank.'; return; }
    if (f.botcheck.checked) { form.hidden = true; done.hidden = false; return; }
    if (KEY.indexOf('YOUR_') === 0) { msg.className = 'msg err'; msg.textContent = 'The contact form is not switched on yet. Please try again soon.'; return; }
    send.disabled = true; msg.className = 'msg'; msg.textContent = 'Sending...';
    var body = { access_key: KEY, subject: TOOL + ': ' + f.topic.value, from_name: TOOL + ' contact form', topic: f.topic.value, message: f.message.value, page: location.pathname };
    if (f.email.value) { body.email = f.email.value; body.replyto = f.email.value; }
    fetch(ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(body) })
      .then(function (r) { return r.json(); })
      .then(function (j) { if (j && j.success) { form.reset(); form.hidden = true; done.hidden = false; } else { throw new Error(); } })
      .catch(function () { send.disabled = false; msg.className = 'msg err'; msg.textContent = 'Sorry, that did not send. Please try again in a moment.'; });
  });
})();
</script>""".replace('__ENDPOINT__', FORM_ENDPOINT).replace('__KEY__', FORM_KEY).replace('__TOOL__', TOOL_TAG)

# ---------- FAQ ----------
FAQ = [
    ('Is my file uploaded anywhere?',
     'No. The whole job runs inside your browser. Your PDF is read on your own device and the booklet is built there too. Nothing is sent to a server.'),
    ('How do I print the booklet?',
     'Print it double-sided and choose flip on short edge (some printers call it short-edge binding). Use the paper size you picked, at actual size. Then keep the sheets in order, fold the stack in half and staple along the fold. If the back sides come out upside down, the printer was set to flip on the long edge; print again with flip on short edge.'),
    ('My printer cannot print on both sides. Can I still make a booklet?',
     'Yes, by hand. Print only the odd pages of the booklet PDF, put the printed stack back in the paper tray, then print the even pages. Which way round the stack goes back in depends on your printer, so try it with the first sheet before printing the rest.'),
    ('Why were blank pages added?',
     'Each sheet of paper holds four booklet pages, two on each side. So a booklet always has a multiple of four pages, and the tool adds blank pages to fill the last sheet. They go at the end, or just before the last page if you tick Keep the last page on the back cover.'),
    ('How many pages can one booklet have?',
     'The tool has no limit, but paper does. Past about 40 pages (10 sheets) a booklet gets hard to fold flat and staple. Use Several booklets to split a long document into smaller ones that each fold and staple on their own.'),
]

def faq_html():
    return '<div class="faq">' + ''.join('<details><summary>%s</summary><p>%s</p></details>' % (q, a) for q, a in FAQ) + '</div>'

def faq_ld():
    return ('<script type="application/ld+json">%s</script>' % json.dumps({
        '@context': 'https://schema.org', '@type': 'FAQPage',
        'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in FAQ]}))

# ---------- HOME ----------
tool_main = re.search(r'<main class="app">.*?</main>', tool, re.S).group(0)
tool_main = re.sub(r'\s*<header class="top">.*?</header>', '', tool_main, count=1, flags=re.S)
tool_dock = re.search(r'<div class="dock">.*?</div>\n', tool, re.S).group(0)
tool_js = re.search(r'<script>\n\(function \(\) \{.*?\}\)\(\);\n</script>', tool, re.S).group(0)
tool_libs = ('<script src="../vendor/pdf.min.js"></script>\n'
             '<script src="../vendor/pdf-lib.min.js"></script>')

def ico_order():
    return ('<svg class="ico" viewBox="0 0 44 30" aria-hidden="true"><rect x="2" y="3" width="40" height="24" rx="2" fill="#fff" stroke="var(--line)" stroke-width="1.5"/>'
            '<line x1="22" y1="3" x2="22" y2="27" stroke="var(--cut)" stroke-width="1.6" stroke-dasharray="3 2"/>'
            '<text x="12" y="19.5" font-size="10" font-family="sans-serif" font-weight="700" text-anchor="middle" fill="#2a8ea3">8</text>'
            '<text x="32" y="19.5" font-size="10" font-family="sans-serif" font-weight="700" text-anchor="middle" fill="#2a8ea3">1</text></svg>')
def ico_blank():
    return ('<svg class="ico" viewBox="0 0 44 30" aria-hidden="true"><rect x="4" y="3" width="16" height="24" rx="2" fill="#fff" stroke="var(--line)" stroke-width="1.5"/>'
            '<rect x="8" y="8" width="8" height="2" rx="1" fill="#39424f"/><rect x="8" y="13" width="8" height="2" rx="1" fill="#c8cfda"/><rect x="8" y="17" width="6" height="2" rx="1" fill="#c8cfda"/>'
            '<rect x="24" y="3" width="16" height="24" rx="2" fill="none" stroke="var(--ink-2)" stroke-width="1.5" stroke-dasharray="3 2"/></svg>')
def ico_split():
    return ('<svg class="ico" viewBox="0 0 44 30" aria-hidden="true"><path d="M11 6 L3 4 V24 L11 26 Z M11 6 L19 4 V24 L11 26 Z" fill="#fff" stroke="var(--line)" stroke-width="1.5" stroke-linejoin="round"/>'
            '<path d="M33 6 L25 4 V24 L33 26 Z M33 6 L41 4 V24 L33 26 Z" fill="#fff" stroke="var(--line)" stroke-width="1.5" stroke-linejoin="round"/>'
            '<rect x="5" y="11" width="4" height="6" rx="1" fill="#2a8ea3"/><rect x="27" y="11" width="4" height="6" rx="1" fill="#2a8ea3"/></svg>')

HOME_ABOVE = ('<section class="page-hero"><h1>Print a PDF as a booklet</h1>'
              '<p>Drop in a PDF and get a print-ready booklet: print it double-sided, fold it in half, staple the middle, and the pages read in order. Free, and your file never leaves your browser.</p>'
              '<noscript><p><strong>This tool needs JavaScript.</strong> Turn it on for this page to make a booklet.</p></noscript>'
              '<span class="newhere">New here? <a href="how-to.html">See how it works, step by step</a>.</span></section>')

HOME_BELOW = """
<section class="sec" aria-labelledby="what">
  <h2 id="what">What it does</h2>
  <p>It puts two pages on each side of a sheet of paper, in the order a folded booklet needs, and gives you a new PDF to print.</p>
  <div class="cards">
    <div class="card">%s<h3>Puts pages in booklet order</h3><p>The first sheet carries your first two and last two pages, the next sheet the ones inside those, and so on to the middle.</p></div>
    <div class="card">%s<h3>Fills the last sheet</h3><p>A booklet needs a multiple of four pages. The tool adds the blank pages for you, at the end or just before the back cover.</p></div>
    <div class="card">%s<h3>Splits long documents</h3><p>A thick stack will not fold flat. Split a long PDF into several booklets of the size you choose, each one folded and stapled on its own.</p></div>
  </div>
</section>

<section class="sec" aria-labelledby="howto">
  <h2 id="howto">How to print a PDF as a booklet</h2>
  <ol class="steps">
    <li><b>Open your PDF</b> in the tool above and pick <b>Letter</b> or <b>A4</b>. Each booklet page comes out half that size: 5.5 by 8.5 inches on Letter, A5 on A4.</li>
    <li><b>Check the preview</b>, then press <b>Download booklet PDF</b>.</li>
    <li><b>Print the new file double-sided</b> with <b>flip on short edge</b>, at actual size.</li>
    <li><b>Fold the stack in half</b>, keeping the sheets in order, and staple along the fold.</li>
  </ol>
  <p>The <a href="how-to.html">full guide</a> covers printers that cannot print on both sides, and stapling without a long-reach stapler.</p>
</section>

<section class="sec" aria-labelledby="useful">
  <h2 id="useful">What it is useful for</h2>
  <p>Print a PDF the usual way and you get one page on each side of a sheet: a loose stack you can only staple in the corner. A folded booklet puts four pages on every sheet, and not in a simple order. In an 8-page booklet the outside sheet carries pages 8 and 1 on one side and 2 and 7 on the other, and one slip when you work that out by hand leaves pages out of order once it is folded.</p>
  <ul class="uses">
    <li>Church programs and bulletins<span>The weekly order of service, folded and handed out at the door.</span></li>
    <li>Zines<span>Small self-published magazines, printed at home.</span></li>
    <li>Recipe collections<span>Family recipes in a little book for the kitchen.</span></li>
    <li>School handouts and study guides<span>Notes students can carry and flip through.</span></li>
    <li>Event programs<span>Weddings, recitals, plays and memorial services.</span></li>
    <li>Small manuals<span>Instructions for a product, a club or a new job.</span></li>
    <li>Short stories and poetry chapbooks<span>Your own writing as a small printed book.</span></li>
  </ul>
</section>

<section class="sec" aria-labelledby="faq">
  <h2 id="faq">Common questions</h2>
  %s
</section>

<section class="sec">
  <div class="band-cta">
    <div><h2>First booklet?</h2><p>The guide walks through printing, folding and stapling.</p></div>
    <a class="pbtn" href="how-to.html">See how to use it</a>
  </div>
</section>
""" % (ico_order(), ico_blank(), ico_split(), faq_html())

SEO_TITLE = {
    'index.html': 'Print a PDF as a Booklet: Free PDF Booklet Maker',
    'how-to.html': 'How to Print a PDF as a Booklet, Fold It and Staple It',
    'about.html': 'About PDF Booklet Maker',
    'privacy.html': 'Privacy | PDF Booklet Maker',
}
DESC = {
    'index.html': 'Print a PDF as a booklet on A4 or Letter: this free tool puts the pages in booklet order, so you print double-sided, fold, staple and they read in order. Runs in your browser; your file is never uploaded.',
    'how-to.html': 'Step by step: make a booklet PDF, print it double-sided with flip on short edge, then fold and staple it. Also covers printers without double-sided printing.',
    'about.html': 'Why PDF Booklet Maker exists and how it works.',
    'privacy.html': 'How PDF Booklet Maker handles your files and what it stores. Your PDF is never uploaded.',
}

def home():
    css = tokens + EXTRA_TOKENS + BASE_CSS + tool_rest + "\n.app { font-size: 15px; line-height: 1.45; }\n#tool { scroll-margin-top: 12px; }\n"
    body = ('<div class="wrap">\n%s\n%s\n<section id="tool" aria-label="PDF booklet maker">\n%s\n</section>\n%s\n%s\n</div>\n%s\n' %
            (header('index.html'), HOME_ABOVE, tool_main, HOME_BELOW, footer(), tool_dock))
    scripts = tool_libs + '\n' + tool_js + '\n' + faq_ld()
    return doc(SEO_TITLE['index.html'], DESC['index.html'], css, body, scripts, '')

# ---------- HOW TO ----------
HOWTO = """
<section class="page-hero"><h1>How to print a PDF as a booklet</h1><p>From a PDF to a folded, stapled booklet in five steps.</p></section>
<div class="prose">
  <h2>1. Open your PDF</h2>
  <p>On the <a href="index.html#tool">tool page</a>, press <b>Open a PDF</b> or drop the file anywhere on the page. A short sample is shown until you do, so you can see how the pages get arranged.</p>
  <h2>2. Pick your paper</h2>
  <p>Choose <b>Letter</b> or <b>A4</b>, whichever is in your printer. Each booklet page comes out half that size: 5.5 by 8.5 inches on Letter, A5 on A4.</p>
  <h2>3. Split it if it is long</h2>
  <p>One booklet suits most documents. If yours is long, choose <b>Several booklets</b> and set how many pages each one gets. It is always a multiple of four, because each sheet holds four pages. Past about 40 pages a booklet gets hard to fold and staple.</p>
  <p>If the page count does not fill the last sheet, blank pages are added at the end. Tick <b>Keep the last page on the back cover</b> to put them just before your last page instead.</p>
  <h2>4. Check the preview</h2>
  <p>Each sheet is shown front and back, with page numbers. The dashed line is the fold. Sheet 1 is the outside of the booklet; the last sheet is the middle, where the staples go.</p>
  <h2>5. Download and print</h2>
  <p>Press <b>Download booklet PDF</b>, open the file and print it with these settings:</p>
  <ul>
    <li><b>Double-sided</b> (print on both sides).</li>
    <li><b>Flip on short edge</b>. Your printer may call it short-edge binding or flip up. If the back sides come out upside down, this setting was on long edge.</li>
    <li>The same paper size you picked in the tool, at <b>actual size</b> (100%).</li>
  </ul>
  <h2>Fold and staple</h2>
  <p>Keep the sheets in the order they come out of the printer. Square up the stack, fold it in half so page 1 is on the outside, and press the fold flat. Staple twice along the fold from the outside. A long-reach stapler makes this easy; without one, open the booklet flat on a thick piece of card and staple through the fold, then bend the staple ends over by hand.</p>
  <h2>No double-sided printing?</h2>
  <p>Print only the odd pages of the booklet PDF. Put the printed stack back in the paper tray and print the even pages. Which way the stack goes back in depends on the printer, so test it with the first sheet before you print the rest.</p>
  <h2>Thick booklets</h2>
  <p>In a booklet with many sheets, the middle sheets stick out a little at the open edge once folded. That is normal. Trim the edge with a paper cutter if you want it neat, or split the document into smaller booklets.</p>
</div>
"""
def howto():
    css = tokens + EXTRA_TOKENS + BASE_CSS
    body = '<div class="wrap narrow">\n%s\n%s\n<p style="margin-top:28px"><a class="pbtn" href="index.html#tool">Make a booklet</a></p>\n%s\n</div>\n' % (header('how-to.html'), HOWTO, footer())
    return doc(SEO_TITLE['how-to.html'], DESC['how-to.html'], css, body, '', 'how-to.html')

# ---------- ABOUT ----------
ABOUT = """
<section class="page-hero"><h1>About PDF Booklet Maker</h1><p>A small free tool for one common job.</p></section>
<div class="prose">
  <h2>Why it exists</h2>
  <p>Printing a PDF as a folded booklet sounds simple, but the pages have to go on each sheet in a special order, and the print settings are easy to get wrong. Some printer drivers and PDF readers have a booklet option, many do not, and the ones that do work differently. This tool makes the booklet PDF for you, so any printer that prints on both sides can print it.</p>
  <h2>What it does</h2>
  <p>It takes your PDF, adds blank pages so the count is a multiple of four, and puts two pages on each side of a Letter or A4 sheet in booklet order. It can also split a long document into several smaller booklets.</p>
  <h2>What it does not do</h2>
  <ul>
    <li>Links and comments in the PDF are not carried over. Filled-in form fields are kept as printed text where possible.</li>
    <li>Password-protected PDFs, and PDFs locked against changes, cannot be used.</li>
    <li>It does not shift pages to make up for the thickness of the fold (sometimes called creep). For booklets of a few sheets this does not matter.</li>
  </ul>
  <h2>Who makes it</h2>
  <p>One person makes and looks after this site. It is a small project, kept simple on purpose.</p>
  <h2>Your files</h2>
  <p>Your PDF is processed in your browser and is never uploaded. The <a href="privacy.html">privacy page</a> explains what the site does and does not store.</p>
  <h2>Get in touch</h2>
  <p>Questions, bug reports or ideas are welcome. Use the <button type="button" class="linkbtn" data-contact style="font-size:inherit;color:var(--accent)">Contact</button> button and your message goes straight to us.</p>
</div>
"""
def about():
    css = tokens + EXTRA_TOKENS + BASE_CSS
    body = '<div class="wrap narrow">\n%s\n%s\n%s\n</div>\n' % (header('about.html'), ABOUT, footer())
    return doc(SEO_TITLE['about.html'], DESC['about.html'], css, body, '', 'about.html')

# ---------- PRIVACY ----------
PRIV = """
<section class="page-hero"><h1>Privacy</h1><p>Short version: your PDF stays on your device.</p></section>
<div class="prose">
  <p class="meta">Last updated: November 15, 2026</p>
  <h2>Your files</h2>
  <p>PDF Booklet Maker reads your PDF and builds the booklet inside your browser. Your file is not uploaded, sent to a server or kept by this site. When you close or refresh the page, it is gone from the page.</p>
  <h2>What is saved on your device</h2>
  <p>The page remembers a few settings in your browser so you do not have to pick them again: the paper size, whether to split into several booklets and how many pages each, and whether to keep the last page on the back cover. This stays on your device and is not sent anywhere. This site does not set cookies of its own.</p>
  <h2>Other services</h2>
  <p>The fonts and the open-source code libraries that read and build PDFs (pdf.js and pdf-lib) are served from this site itself, so your browser does not fetch them from anyone else. The only outside service the page talks to is the contact form, and only when you send a message.</p>
  <h2>Analytics and ads</h2>
  <p>This site is hosted on Cloudflare, which can count visits for us (page views, the country a visit came from, which page was opened) using its privacy-focused web analytics. It does not use cookies and does not follow you across other sites. We do not run any other analytics and the site shows no ads. If that changes, this page will be updated first to say what is used and how you can opt out.</p>
  <h2>If you contact us</h2>
  <p>The Contact form sends us your message, the topic you chose, and your email address only if you type one in. We use it to read and reply to you, and we do not share it or add it to any list. The message is delivered by a third-party form service. Please do not put anything private in it, and never include the contents of your PDF.</p>
</div>
"""
def privacy():
    css = tokens + EXTRA_TOKENS + BASE_CSS
    body = '<div class="wrap narrow">\n%s\n%s\n%s\n</div>\n' % (header('privacy.html'), PRIV, footer())
    return doc(SEO_TITLE['privacy.html'], DESC['privacy.html'], css, body, '', 'privacy.html')


OUT = os.path.join(HERE, '..', '..', 'public', SLUG)
os.makedirs(OUT, exist_ok=True)
BUILD = [('index.html', home), ('how-to.html', howto), ('about.html', about), ('privacy.html', privacy)]
for name, fn in BUILD:
    open(os.path.join(OUT, name), 'w').write(fn())
print('built %s into public/%s:' % (NAME, SLUG), [n for n, _ in BUILD])
