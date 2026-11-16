import re, json, os

# Builds public/dust-jacket-maker/ from tool-src.html and demo-src.html. Run: python3 build.py
# The site chrome (header, footer, contact form, shared CSS) follows tools/cut-and-stack/build.py so the tools look the same.

HERE = os.path.dirname(os.path.abspath(__file__))
tool = open(os.path.join(HERE, 'tool-src.html')).read()
demo = open(os.path.join(HERE, 'demo-src.html')).read()

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

# ---------- brand mark: a flat jacket, five panels, with the folds dashed ----------
MARK = ('<svg width="30" height="30" viewBox="0 0 30 30" aria-hidden="true">'
        '<rect x="1" y="7" width="28" height="16" rx="1.5" fill="#f3ece0" stroke="var(--line)" stroke-width="1.2"/>'
        '<rect x="6" y="7.6" width="7.5" height="14.8" fill="#21424d"/><rect x="13.5" y="7.6" width="3" height="14.8" fill="#2a8ea3"/><rect x="16.5" y="7.6" width="7.5" height="14.8" fill="#f0a77f"/>'
        '<circle cx="21" cy="13" r="2" fill="#fbeed3"/>'
        '<line x1="13.5" y1="2" x2="13.5" y2="28" stroke="var(--cut)" stroke-width="1.4" stroke-dasharray="2.5 1.8"/>'
        '<line x1="16.5" y1="2" x2="16.5" y2="28" stroke="var(--cut)" stroke-width="1.4" stroke-dasharray="2.5 1.8"/></svg>')
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 30'%3E"
           "%3Crect x='1' y='7' width='28' height='16' rx='1.5' fill='%23f3ece0' stroke='%230e7490' stroke-width='1.2'/%3E"
           "%3Crect x='6' y='7.6' width='7.5' height='14.8' fill='%2321424d'/%3E%3Crect x='13.5' y='7.6' width='3' height='14.8' fill='%232a8ea3'/%3E"
           "%3Crect x='16.5' y='7.6' width='7.5' height='14.8' fill='%23f0a77f'/%3E"
           "%3Cline x1='13.5' y1='2' x2='13.5' y2='28' stroke='%23d6246e' stroke-width='1.6' stroke-dasharray='2.5 1.8'/%3E"
           "%3Cline x1='16.5' y1='2' x2='16.5' y2='28' stroke='%23d6246e' stroke-width='1.6' stroke-dasharray='2.5 1.8'/%3E%3C/svg%3E")

NAME = 'Dust Jacket Maker'
SLUG = 'dust-jacket-maker'
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
FORM_KEY = '00640895-65d1-4e34-b1c1-8dc6575510a4'   # public Web3Forms key, same form as the other tools
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
    ('Are my images uploaded anywhere?',
     'No. The whole job runs inside your browser. Your images are read on your own device and the PDF is built there too. Nothing is sent to a server.'),
    ('How do I measure my book for a dust jacket?',
     'Measure the boards, the hard covers, not the pages. Height is from the top of the board to the bottom. Cover width is from the spine edge to the outer edge of the front board. Spine width is straight across the spine, from the front board to the back board, with the book closed. Flaps are your choice; about half the cover width is usual.'),
    ('What is the wrap allowance?',
     'The boards have thickness, so a jacket cut to the exact board size ends up a little short once it wraps round the edges. The wrap allowance adds a small amount to the height and to each cover width. 1/8 inch (3 mm) suits most books; use a little more for thick boards.'),
    ('What is bleed, and do I need it?',
     'Bleed is extra artwork past the edge of the jacket that gets trimmed off, so there is no thin white line if the cut is slightly off. Print shops usually ask for it, often 1/8 inch or 3 mm. If you print at home and trim by hand, it still helps when your artwork runs to the edge.'),
    ('My printer cannot print something this big. What can I do?',
     'Download the tiled version. It splits the jacket over Letter or A4 sheets with a small overlap and marks in the margin. Print at actual size, cut each sheet along its cut marks, lay it over the sheet before so its edge sits on the match marks, and tape the back. A print shop can also print the full-size PDF on one large sheet for a small fee.'),
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
tool_libs = '<script src="../vendor/pdf-lib.min.js"></script>'
demo_css = css_of(demo)
demo_html = re.search(r'<section class="sec".*?</section>', demo, re.S).group(0)
demo_js = re.search(r'<script>\n\(function \(\) \{.*?\}\)\(\);\n</script>', demo, re.S).group(0)

def ico_size():
    return ('<svg class="ico" viewBox="0 0 44 30" aria-hidden="true"><rect x="2" y="6" width="40" height="18" rx="1.5" fill="#fff" stroke="var(--line)" stroke-width="1.5"/>'
            '<rect x="17" y="7" width="3" height="16" fill="#21424d"/><rect x="20" y="7" width="12" height="16" fill="#f0a77f"/>'
            '<line x1="2" y1="28" x2="42" y2="28" stroke="var(--accent)" stroke-width="1.5"/><line x1="2" y1="26" x2="2" y2="30" stroke="var(--accent)" stroke-width="1.5"/><line x1="42" y1="26" x2="42" y2="30" stroke="var(--accent)" stroke-width="1.5"/></svg>')
def ico_marks():
    return ('<svg class="ico" viewBox="0 0 44 30" aria-hidden="true"><rect x="8" y="7" width="28" height="16" fill="#f0a77f"/><rect x="19" y="7" width="4" height="16" fill="#21424d"/>'
            '<path d="M2 7 H6 M38 7 H42 M2 23 H6 M38 23 H42 M8 1 V5 M36 1 V5 M8 25 V29 M36 25 V29" stroke="var(--ink)" stroke-width="1.2"/>'
            '<path d="M19 1 V5 M23 1 V5 M19 25 V29 M23 25 V29" stroke="var(--cut)" stroke-width="1.2" stroke-dasharray="1.5 1"/></svg>')
def ico_tiles():
    return ('<svg class="ico" viewBox="0 0 44 30" aria-hidden="true"><rect x="3" y="4" width="15" height="22" rx="1" fill="#fff" stroke="var(--line)" stroke-width="1.5"/>'
            '<rect x="15" y="4" width="15" height="22" rx="1" fill="#fff" stroke="var(--line)" stroke-width="1.5"/><rect x="27" y="4" width="15" height="22" rx="1" fill="#fff" stroke="var(--line)" stroke-width="1.5"/>'
            '<rect x="5" y="10" width="35" height="10" fill="#2a8ea3" opacity="0.8"/><line x1="16.5" y1="1" x2="16.5" y2="29" stroke="var(--cut)" stroke-width="1.4" stroke-dasharray="2 1.5"/><line x1="28.5" y1="1" x2="28.5" y2="29" stroke="var(--cut)" stroke-width="1.4" stroke-dasharray="2 1.5"/></svg>')

HOME_ABOVE = ('<section class="page-hero"><h1>Dust jacket template maker</h1>'
              '<p>Type in your hardcover\'s measurements, add a front cover image, and download a print-ready dust jacket PDF at exact size, with fold and trim marks. Free, and your images never leave your browser.</p>'
              '<noscript><p><strong>This tool needs JavaScript.</strong> Turn it on for this page to use it.</p></noscript>'
              '<span class="newhere">New here? <a href="#demo">See how a dust jacket goes together</a>, or read the <a href="how-to.html">step-by-step guide</a>.</span></section>')

HOME_BELOW = """
<section class="sec" aria-labelledby="what">
  <h2 id="what">What it does</h2>
  <p>It builds a custom dust jacket template from your book's measurements and puts your artwork on it, ready to print.</p>
  <div class="cards">
    <div class="card">%s<h3>Exact size</h3><p>Five panels in the right order, sized from your measurements plus a small wrap allowance, in inches or millimetres. The PDF is the real physical size.</p></div>
    <div class="card">%s<h3>Fold and trim marks</h3><p>Fold marks at every panel edge and trim marks at the corners, all outside the artwork, with optional bleed for a print shop.</p></div>
    <div class="card">%s<h3>Print anywhere</h3><p>One full-size page for a print shop, or the same jacket tiled across Letter or A4 sheets with an overlap and matching marks.</p></div>
  </div>
</section>

<section class="sec" aria-labelledby="howto">
  <h2 id="howto">How to make a dust jacket</h2>
  <ol class="steps">
    <li><b>Measure the boards</b> of your book: height, front cover width and spine width. Pick a flap width.</li>
    <li><b>Type them in</b> above, in inches or millimetres. Leave the wrap allowance at the default unless your boards are very thick.</li>
    <li><b>Add your front cover image</b>, and a back and spine image if you have them, or pick flat colours and add spine text.</li>
    <li><b>Download</b> the full-size PDF for a print shop, or the tiled PDF to print at home.</li>
    <li><b>Print at actual size</b>, trim at the corner marks, fold at the fold marks and wrap it round the book.</li>
  </ol>
  <p>The <a href="how-to.html">full guide</a> covers measuring, paper, tiling and folding.</p>
</section>

<section class="sec" aria-labelledby="useful">
  <h2 id="useful">What it is useful for</h2>
  <p>Anywhere a hardcover needs a jacket that fits. Shop-bought templates come in a few standard sizes; this one is cut to your book.</p>
  <ul class="uses">
    <li>Finishing a handmade hardcover<span>Hobby bookbinders can give a newly bound book a proper printed jacket.</span></li>
    <li>Replacing a lost or torn jacket<span>Measure the book, scan or photograph what is left of the old cover, and print a new one.</span></li>
    <li>A jacket for an ebook-only cover<span>Got a cover image but no printed edition? Wrap a blank or printed hardcover in it.</span></li>
    <li>Matching covers for a set<span>Use the same design and colours across a series so they look right side by side on the shelf.</span></li>
    <li>Gift books<span>A personal cover for a journal, a photo book or a story you wrote, with the name on the spine.</span></li>
  </ul>
</section>

<section class="sec" aria-labelledby="faq">
  <h2 id="faq">Common questions</h2>
  %s
</section>

<section class="sec">
  <div class="band-cta">
    <div><h2>Making your first jacket?</h2><p>The guide walks through measuring, printing and folding.</p></div>
    <a class="pbtn" href="how-to.html">See how to use it</a>
  </div>
</section>
""" % (ico_size(), ico_marks(), ico_tiles(), faq_html())

SEO_TITLE = {
    'index.html': 'Dust Jacket Template Maker: Free, Custom Size, Print-Ready PDF',
    'how-to.html': 'How to Make and Print a Dust Jacket for a Hardcover Book',
    'about.html': 'About Dust Jacket Maker',
    'privacy.html': 'Privacy | Dust Jacket Maker',
}
DESC = {
    'index.html': 'Free dust jacket template maker: enter your book size, add cover images and download a print-ready PDF with fold and trim marks. Your images are never uploaded.',
    'how-to.html': 'Step by step: measure a hardcover, make a dust jacket template at exact size, print it whole or tiled on Letter or A4, then trim and fold it round the book.',
    'about.html': 'Why Dust Jacket Maker exists and how it works.',
    'privacy.html': 'How Dust Jacket Maker handles your images and what it stores. Your images are never uploaded.',
}

def home():
    css = tokens + EXTRA_TOKENS + BASE_CSS + tool_rest + demo_css + "\n.app { font-size: 15px; line-height: 1.45; }\n#tool, #demo { scroll-margin-top: 12px; }\n"
    body = ('<div class="wrap">\n%s\n%s\n<section id="tool" aria-label="Dust jacket maker">\n%s\n</section>\n%s\n%s\n%s\n</div>\n%s\n' %
            (header('index.html'), HOME_ABOVE, tool_main, demo_html, HOME_BELOW, footer(), tool_dock))
    scripts = tool_libs + '\n' + tool_js + '\n' + demo_js + '\n' + faq_ld()
    return doc(SEO_TITLE['index.html'], DESC['index.html'], css, body, scripts, '')

# ---------- HOW TO ----------
HOWTO = """
<section class="page-hero"><h1>How to make a dust jacket</h1><p>From a tape measure to a jacket on the book, in six steps.</p></section>
<div class="prose">
  <h2>1. Measure the book</h2>
  <p>Use a ruler, not a sewing tape, and measure the <b>boards</b> (the hard covers), not the pages:</p>
  <ul>
    <li><b>Book height</b>: top edge of the board to the bottom edge.</li>
    <li><b>Front cover width</b>: from where the board meets the spine to the board's outer edge.</li>
    <li><b>Spine width</b>: straight across the spine with the book closed, from the outside of the front board to the outside of the back board. A strip of paper wrapped across the spine and marked with a pencil is easier than a ruler on a round spine.</li>
    <li><b>Flap width</b>: your choice. About half the cover width is usual; 3 to 3.5 inches (75 to 90 mm) on a novel.</li>
  </ul>
  <h2>2. Enter the measurements</h2>
  <p>On the <a href="index.html#tool">tool page</a>, choose inches or millimetres and type the four numbers. Inches can be typed as fractions too, like <b>9 1/2</b>. The <b>wrap allowance</b> (1/8 inch or 3 mm by default) is added to the height and to each cover so the paper reaches round the board edges. Add a little more for very thick boards.</p>
  <h2>3. Add your artwork</h2>
  <ul>
    <li><b>Front cover</b>: a JPG, PNG or WebP image. A sample cover is shown until you choose your own.</li>
    <li><b>Back cover and spine</b>: an image, or a flat colour. The spine can have a line of text, which reads from top to bottom.</li>
    <li><b>Flaps</b>: a flat colour.</li>
    <li><b>Fill</b> crops an image to cover the whole panel; <b>Fit</b> shows all of it with the panel colour round it.</li>
  </ul>
  <p>For a sharp print, aim for images of at least 150, and ideally 300, pixels per inch at the printed size. The tool shows the figure under each image and warns when it is low.</p>
  <h2>4. Choose bleed</h2>
  <p>Tick <b>Add bleed</b> if a print shop will cut the jacket, or if your design runs to the edge. The artwork then runs a little past the trim (1/8 inch or 3 mm by default) and is cut off, so there is no white edge.</p>
  <h2>5. Print</h2>
  <p><b>At a print shop</b>: send the <b>full-size PDF</b>. It is one page at the exact jacket size, with trim marks at the corners, dashed fold marks at each panel edge and the trim and bleed sizes set in the file. Ask for it at 100%, on paper around 100 to 150 gsm (70 to 100 lb text). Gloss or matte paper both work.</p>
  <p><b>At home</b>: choose Letter or A4 and download the <b>tiled PDF</b>. The tool says how many sheets it takes. Print at <b>actual size</b> (100%), not fit to page. Each sheet shares a half inch strip with its neighbours. Lay the sheets out in order, cut each sheet along the line between its two <b>cut</b> marks, lay it over the sheet before so the cut edge sits on that sheet's <b>match</b> marks, and tape along the back. Join each row from left to right, then join the rows.</p>
  <h2>6. Trim and fold</h2>
  <p>Cut along the lines between the <b>trim marks</b> at the corners. Lay the jacket face down, put the closed book on it with the spine between the two middle fold marks, and crease along the spine edges. Wrap the covers, close the book to check the fit, then fold the flaps in at the outer fold marks and tuck them inside the covers.</p>
  <h2>If it does not fit</h2>
  <p>Too tight round the spine? Measure the spine again with the book closed and add a millimetre or two. Flaps slipping out? Make them wider. Jacket too short top to bottom? Increase the wrap allowance.</p>
</div>
"""
def howto():
    css = tokens + EXTRA_TOKENS + BASE_CSS
    body = '<div class="wrap narrow">\n%s\n%s\n<p style="margin-top:28px"><a class="pbtn" href="index.html#tool">Make a dust jacket</a></p>\n%s\n</div>\n' % (header('how-to.html'), HOWTO, footer())
    return doc(SEO_TITLE['how-to.html'], DESC['how-to.html'], css, body, '', 'how-to.html')

# ---------- ABOUT ----------
ABOUT = """
<section class="page-hero"><h1>About Dust Jacket Maker</h1><p>A small free tool for one common job.</p></section>
<div class="prose">
  <h2>Why it exists</h2>
  <p>A dust jacket is simple: one long strip of paper with five panels. Getting the sizes right is the fiddly part, and ready-made templates only come in a few book sizes. This tool works the panels out from your own measurements and gives you a PDF at the real size, with the marks a print shop or a home printer needs.</p>
  <h2>What it does</h2>
  <p>It lays out the back flap, back cover, spine, front cover and front flap from your measurements, adds a wrap allowance and optional bleed, places your images on the panels, and draws trim and fold marks outside the artwork. It makes one full-size page, or tiles the same jacket over Letter or A4 sheets with an overlap and matching marks.</p>
  <h2>What it does not do</h2>
  <ul>
    <li>It does not design the cover for you. Bring your own images, or use flat colours and spine text.</li>
    <li>It does not put text on the back cover or the flaps. Add blurbs to the images in your design app first.</li>
    <li>It does not do CMYK or spot colours. The PDF is in ordinary screen colours (RGB), which home printers and most print shops handle fine.</li>
    <li>Spine text uses one plain bold font. Text in other alphabets is drawn as a picture, so it still prints.</li>
  </ul>
  <h2>Who makes it</h2>
  <p>One person makes and looks after this site. It is a small project, kept simple on purpose.</p>
  <h2>Your files</h2>
  <p>Your images are processed in your browser and are never uploaded. The <a href="privacy.html">privacy page</a> explains what the site does and does not store.</p>
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
<section class="page-hero"><h1>Privacy</h1><p>Short version: your images stay on your device.</p></section>
<div class="prose">
  <p class="meta">Last updated: November 16, 2026</p>
  <h2>Your files</h2>
  <p>Dust Jacket Maker reads your images and builds the PDF inside your browser. Your images are not uploaded, sent to a server or kept by this site. When you close or refresh the page, they are gone from the page.</p>
  <h2>What is saved on your device</h2>
  <p>The page remembers a few settings in your browser so you do not have to enter them again: the units, your book's measurements, the wrap allowance, the bleed setting, fit or fill, and the paper size for tiling. Your images, colours and spine text are not saved. This stays on your device and is not sent anywhere. This site does not set cookies of its own.</p>
  <h2>Other services</h2>
  <p>The fonts and the open-source code library that builds PDFs (pdf-lib) are served from this site itself, so your browser does not fetch them from anyone else. The only outside service the page talks to is the contact form, and only when you send a message.</p>
  <h2>Analytics and ads</h2>
  <p>This site is hosted on Cloudflare, which can count visits for us (page views, the country a visit came from, which page was opened) using its privacy-focused web analytics. It does not use cookies and does not follow you across other sites. We do not run any other analytics and the site shows no ads. If that changes, this page will be updated first to say what is used and how you can opt out.</p>
  <h2>If you contact us</h2>
  <p>The Contact form sends us your message, the topic you chose, and your email address only if you type one in. We use it to read and reply to you, and we do not share it or add it to any list. The message is delivered by a third-party form service. Please do not put anything private in it, and never include your images.</p>
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
