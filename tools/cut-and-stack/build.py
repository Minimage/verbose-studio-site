import re, json, os

# Builds public/cut-and-stack/ from tool-src.html and demo-src.html. Run: python3 build.py
# The site chrome (header, footer, contact form, shared CSS) follows tools/pdf-booklet/build.py so the tools look the same.

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

# ---------- brand mark: a stack of sheets with the cuts dashed ----------
MARK = ('<svg width="30" height="30" viewBox="0 0 30 30" aria-hidden="true">'
        '<rect x="6" y="5" width="21" height="23" rx="1.5" fill="#fff" stroke="var(--line)" stroke-width="1.5"/>'
        '<rect x="3" y="2" width="21" height="23" rx="1.5" fill="#fff" stroke="var(--line)" stroke-width="1.5"/>'
        '<rect x="5.5" y="4.5" width="7" height="8" rx="1" fill="#2a8ea3"/><rect x="14.5" y="4.5" width="7" height="8" rx="1" fill="#c8cfda"/>'
        '<rect x="5.5" y="14.5" width="7" height="8" rx="1" fill="#c8cfda"/><rect x="14.5" y="14.5" width="7" height="8" rx="1" fill="#c8cfda"/>'
        '<line x1="13.5" y1="0.5" x2="13.5" y2="29.5" stroke="var(--cut)" stroke-width="1.8" stroke-dasharray="3 2"/>'
        '<line x1="0.5" y1="13.5" x2="29.5" y2="13.5" stroke="var(--cut)" stroke-width="1.8" stroke-dasharray="3 2"/></svg>')
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 30'%3E"
           "%3Crect x='6' y='5' width='21' height='23' rx='1.5' fill='white' stroke='%230e7490' stroke-width='1.5'/%3E"
           "%3Crect x='3' y='2' width='21' height='23' rx='1.5' fill='white' stroke='%230e7490' stroke-width='1.5'/%3E"
           "%3Crect x='5.5' y='4.5' width='7' height='8' rx='1' fill='%232a8ea3'/%3E"
           "%3Cline x1='13.5' y1='0.5' x2='13.5' y2='29.5' stroke='%23d6246e' stroke-width='2' stroke-dasharray='3 2'/%3E"
           "%3Cline x1='0.5' y1='13.5' x2='29.5' y2='13.5' stroke='%23d6246e' stroke-width='2' stroke-dasharray='3 2'/%3E%3C/svg%3E")

NAME = 'Cut and Stack PDF Imposer'
SLUG = 'cut-and-stack'
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
    ('Is my file uploaded anywhere?',
     'No. The whole job runs inside your browser. Your PDF is read on your own device and the new PDF is built there too. Nothing is sent to a server.'),
    ('What does cut and stack mean?',
     'It is a way of laying out small items on sheets so a whole stack can be cut at once. Each position on the sheet becomes its own pile, and each pile runs down through the stack in order. With 4 on a sheet and 4 sheets, sheet 1 holds items 1, 5, 9 and 13, and sheet 2 holds 2, 6, 10 and 14. After one cut, the piles hold 1 to 4, 5 to 8, 9 to 12 and 13 to 16, so you just put them on top of each other.'),
    ('How should my PDF be set up?',
     'One item per page, at the size you want it printed. For double-sided items, either put each back right after its front (front 1, back 1, front 2, back 2), or put one shared back as the very last page.'),
    ('The backs do not line up with the fronts. What can I do?',
     'First check that the flip setting in the tool matches the one in the print dialog. Then print one test sheet and hold it up to a light. Most home printers shift the back by a millimetre or two, so leave a little white space around the edge of your design rather than a tight border.'),
    ('Why are some spaces blank?',
     'Every sheet has the same number of spaces, so if your item count does not fill the last round, the tool adds blank spaces. They end up at the bottom of the last piles, or as whole piles of blank paper you can throw away.'),
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
demo_css = css_of(demo)
demo_html = re.search(r'<section class="sec".*?</section>', demo, re.S).group(0)
demo_js = re.search(r'<script>\n\(function \(\) \{.*?\}\)\(\);\n</script>', demo, re.S).group(0)

def ico_order():
    return ('<svg class="ico" viewBox="0 0 44 30" aria-hidden="true"><rect x="4" y="3" width="16" height="24" rx="2" fill="#fff" stroke="var(--line)" stroke-width="1.5"/>'
            '<rect x="24" y="3" width="16" height="24" rx="2" fill="#fff" stroke="var(--line)" stroke-width="1.5"/>'
            '<text x="12" y="19.5" font-size="10" font-family="sans-serif" font-weight="700" text-anchor="middle" fill="#2a8ea3">1</text>'
            '<text x="32" y="19.5" font-size="10" font-family="sans-serif" font-weight="700" text-anchor="middle" fill="#2a8ea3">2</text></svg>')
def ico_back():
    return ('<svg class="ico" viewBox="0 0 44 30" aria-hidden="true"><rect x="4" y="3" width="16" height="24" rx="2" fill="#fff" stroke="var(--line)" stroke-width="1.5"/>'
            '<rect x="24" y="3" width="16" height="24" rx="2" fill="#2a8ea3" stroke="var(--line)" stroke-width="1.5"/>'
            '<path d="M14 15 H30 M26 11 L30 15 L26 19" fill="none" stroke="var(--cut)" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')
def ico_blank():
    return ('<svg class="ico" viewBox="0 0 44 30" aria-hidden="true"><rect x="4" y="3" width="16" height="24" rx="2" fill="#fff" stroke="var(--line)" stroke-width="1.5"/>'
            '<rect x="8" y="8" width="8" height="2" rx="1" fill="#39424f"/><rect x="8" y="13" width="8" height="2" rx="1" fill="#c8cfda"/><rect x="8" y="17" width="6" height="2" rx="1" fill="#c8cfda"/>'
            '<rect x="24" y="3" width="16" height="24" rx="2" fill="none" stroke="var(--ink-2)" stroke-width="1.5" stroke-dasharray="3 2"/></svg>')

HOME_ABOVE = ('<section class="page-hero"><h1>Make a cut and stack PDF</h1>'
              '<p>Drop in a PDF of tickets, cards or postcards and get a print-ready PDF with 2, 4, 6 or 8 on each sheet. Print, stack, cut once, and every pile is already in order. Free, and your file never leaves your browser.</p>'
              '<noscript><p><strong>This tool needs JavaScript.</strong> Turn it on for this page to use it.</p></noscript>'
              '<span class="newhere">New here? <a href="#demo">See how cut and stack works</a>, or read the <a href="how-to.html">step-by-step guide</a>.</span></section>')

HOME_BELOW = """
<section class="sec" aria-labelledby="what">
  <h2 id="what">What it does</h2>
  <p>It takes a PDF with one item on each page and lays the items out on Letter or A4 sheets in cut and stack order.</p>
  <div class="cards">
    <div class="card">%s<h3>Keeps numbers in order</h3><p>Each position on the sheet is its own pile. Cut the stack, put the piles together, and item 1 is on top with the rest in order underneath.</p></div>
    <div class="card">%s<h3>Lines up the backs</h3><p>For double-sided items, the backs are mirrored to match how your printer flips the paper, so each back lands behind its own front.</p></div>
    <div class="card">%s<h3>Fills the last sheet</h3><p>If your items do not fill every sheet, the tool adds blank spaces so the piles still come out right, and tells you which piles to keep.</p></div>
  </div>
</section>

<section class="sec" aria-labelledby="howto">
  <h2 id="howto">How to cut and stack a PDF</h2>
  <ol class="steps">
    <li><b>Open your PDF</b> in the tool above. It should have one item per page, at the size you want it printed.</li>
    <li><b>Pick how many go on a sheet</b> (2, 4, 6 or 8), your paper, and single or double-sided.</li>
    <li><b>Check the preview</b> and press <b>Download cut and stack PDF</b>.</li>
    <li><b>Print it at actual size</b>. For double-sided items, use the same flip setting you chose in the tool.</li>
    <li><b>Stack the sheets</b> with sheet 1 on top, <b>cut the stack</b> along the guides, and <b>put pile 1 on pile 2</b>, then on pile 3, and so on.</li>
  </ol>
  <p>The <a href="how-to.html">full guide</a> covers lining up the backs, cutting without a guillotine and setting up your PDF.</p>
</section>

<section class="sec" aria-labelledby="useful">
  <h2 id="useful">What it is useful for</h2>
  <p>Anything small that you print several to a sheet and then cut apart. If the items are numbered, or just need to stay in a set order, cut and stack saves you sorting them by hand afterwards. Print 200 tickets four to a sheet the usual way and the cut piles come out as 1, 5, 9 and so on, ready for a long evening of sorting.</p>
  <ul class="uses">
    <li>Raffle and event tickets<span>Numbered tickets that come off the cutter in order, stubs and all.</span></li>
    <li>Numbered cards<span>Bingo cards, game cards and anything with a serial number.</span></li>
    <li>Flashcards<span>Question on the front, answer on the back, in lesson order.</span></li>
    <li>Place cards<span>Name cards for a wedding or dinner, in seating order.</span></li>
    <li>Postcards<span>A set of postcards or invitations with a printed back.</span></li>
    <li>Business cards<span>Eight to a sheet, with the back lined up behind each front.</span></li>
    <li>Small notepads<span>Quarter-page note sheets that stack straight into a pad.</span></li>
  </ul>
</section>

<section class="sec" aria-labelledby="faq">
  <h2 id="faq">Common questions</h2>
  %s
</section>

<section class="sec">
  <div class="band-cta">
    <div><h2>First time cutting a stack?</h2><p>The guide walks through printing, cutting and putting the piles together.</p></div>
    <a class="pbtn" href="how-to.html">See how to use it</a>
  </div>
</section>
""" % (ico_order(), ico_back(), ico_blank(), faq_html())

SEO_TITLE = {
    'index.html': 'Cut and Stack PDF: Free Imposition Tool for Tickets and Cards',
    'how-to.html': 'How to Print, Cut and Stack Tickets and Cards in Order',
    'about.html': 'About Cut and Stack PDF Imposer',
    'privacy.html': 'Privacy | Cut and Stack PDF Imposer',
}
DESC = {
    'index.html': 'Make a cut and stack PDF for free: 2, 4, 6 or 8 tickets or cards per sheet. Print, stack and cut, and every pile is in order. Your file is never uploaded.',
    'how-to.html': 'Step by step: lay out a PDF in cut and stack order, print it, cut the stack and put the piles together so numbered tickets and cards come out in order.',
    'about.html': 'Why Cut and Stack PDF Imposer exists and how it works.',
    'privacy.html': 'How Cut and Stack PDF Imposer handles your files and what it stores. Your PDF is never uploaded.',
}

def home():
    css = tokens + EXTRA_TOKENS + BASE_CSS + tool_rest + demo_css + "\n.app { font-size: 15px; line-height: 1.45; }\n#tool, #demo { scroll-margin-top: 12px; }\n"
    body = ('<div class="wrap">\n%s\n%s\n<section id="tool" aria-label="Cut and stack PDF imposer">\n%s\n</section>\n%s\n%s\n%s\n</div>\n%s\n' %
            (header('index.html'), HOME_ABOVE, tool_main, demo_html, HOME_BELOW, footer(), tool_dock))
    scripts = tool_libs + '\n' + tool_js + '\n' + demo_js + '\n' + faq_ld()
    return doc(SEO_TITLE['index.html'], DESC['index.html'], css, body, scripts, '')

# ---------- HOW TO ----------
HOWTO = """
<section class="page-hero"><h1>How to print, cut and stack</h1><p>From a PDF of tickets or cards to neat piles in order, in six steps.</p></section>
<div class="prose">
  <h2>1. Set up your PDF</h2>
  <p>Make a PDF with <b>one item per page</b>, at the size you want it printed: one ticket, one card or one postcard on each page. Most design apps can export a page per item, and mail merge can make numbered ones.</p>
  <p>For items with a printed back, either put each back straight after its front (front 1, back 1, front 2, back 2), or, if every item has the same back, put that back once as the very last page.</p>
  <h2>2. Open it in the tool</h2>
  <p>On the <a href="index.html#tool">tool page</a>, press <b>Open a PDF</b> or drop the file anywhere on the page. A sample of numbered raffle tickets is shown until you do.</p>
  <h2>3. Choose the layout</h2>
  <ul>
    <li><b>Items per sheet</b>: 2, 4, 6 or 8. The tool picks the grid and turns the sheet if that fits the items better.</li>
    <li><b>Paper</b>: Letter or A4, whichever is in your printer.</li>
    <li><b>Sides</b>: single-sided, double-sided with alternating pages, or double-sided with one shared back.</li>
    <li><b>Item size</b>: <b>Actual size</b> keeps your items at the size in the PDF and only shrinks them if they do not fit. <b>Fill the sheet</b> makes them as big as the paper allows.</li>
    <li><b>Cut guide lines</b> add short lines in the margin, lined up with every cut, on the front of each sheet.</li>
  </ul>
  <h2>4. Check the preview and download</h2>
  <p>Every sheet is shown with item numbers on it, front and back for double-sided items. The pink dashed lines show the cuts; they are not printed. The result box says how many sheets you need and what each pile will hold. Press <b>Download cut and stack PDF</b>.</p>
  <h2>5. Print</h2>
  <p>Print at <b>actual size</b> (100%), not fit to page, or the cut lines will move. For double-sided items, choose double-sided in the print dialog with the same flip setting you picked in the tool: <b>long edge</b> on most printers. Print one sheet first and hold it up to a light to check that the backs line up.</p>
  <h2>6. Stack, cut and collect</h2>
  <p>Put the sheets in one neat stack with <b>sheet 1 on top</b>, face up. Many printers put the pages out face down with sheet 1 at the bottom; if yours does, just turn the whole stack over.</p>
  <p>Cut the stack along the guide lines. Each position on the sheet is now its own pile. Put <b>pile 1 on top of pile 2</b>, then both on pile 3, and so on. Pile 1 is the top left position, and the piles are numbered left to right, then top to bottom, the same as you read. Your items are now in order from the top.</p>
  <h2>No guillotine?</h2>
  <p>A rotary trimmer cuts 5 to 10 sheets at a time. Cut the stack in small batches, keep the batches in order, and put each position into its own pile as you go. With scissors, do the same a sheet or two at a time.</p>
  <h2>Blank spaces</h2>
  <p>If your item count does not fill the last round of sheets, blank spaces are added. They land at the bottom of the last piles, or as whole piles of blank paper that you can recycle. The result box tells you which.</p>
</div>
"""
def howto():
    css = tokens + EXTRA_TOKENS + BASE_CSS
    body = '<div class="wrap narrow">\n%s\n%s\n<p style="margin-top:28px"><a class="pbtn" href="index.html#tool">Make a cut and stack PDF</a></p>\n%s\n</div>\n' % (header('how-to.html'), HOWTO, footer())
    return doc(SEO_TITLE['how-to.html'], DESC['how-to.html'], css, body, '', 'how-to.html')

# ---------- ABOUT ----------
ABOUT = """
<section class="page-hero"><h1>About Cut and Stack PDF Imposer</h1><p>A small free tool for one common job.</p></section>
<div class="prose">
  <h2>Why it exists</h2>
  <p>Printing numbered tickets or cards several to a sheet is easy. Getting them back in order after cutting is not: the usual layout gives you piles of 1, 5, 9 and 13, and someone has to sort them by hand. Print shops avoid this with a layout called cut and stack, usually set up in expensive software. This tool does the same for free, in your browser.</p>
  <h2>What it does</h2>
  <p>It takes a PDF with one item per page and lays the items out 2, 4, 6 or 8 to a Letter or A4 sheet, so that each position on the sheet is one pile and each pile runs down through the stack. It pads the last sheet with blank spaces, mirrors the backs of double-sided items, can add cut guides, and tells you what each pile holds.</p>
  <h2>What it does not do</h2>
  <ul>
    <li>It does not add bleed. If your design runs right to the edge, add bleed in your design app, or leave a small white border.</li>
    <li>It does not turn items sideways to fit more on a sheet. It chooses the grid and the sheet direction, and keeps every item upright.</li>
    <li>Items of different sizes all get a space as big as the largest one.</li>
    <li>Links and comments in the PDF are not carried over. Filled-in form fields are kept as printed text where possible.</li>
    <li>Password-protected PDFs, and PDFs locked against changes, cannot be used.</li>
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
  <p>Cut and Stack PDF Imposer reads your PDF and builds the new one inside your browser. Your file is not uploaded, sent to a server or kept by this site. When you close or refresh the page, it is gone from the page.</p>
  <h2>What is saved on your device</h2>
  <p>The page remembers a few settings in your browser so you do not have to pick them again: the paper size, how many items go on a sheet, single or double-sided, the flip setting, the item size and whether to add cut guides. This stays on your device and is not sent anywhere. This site does not set cookies of its own.</p>
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
