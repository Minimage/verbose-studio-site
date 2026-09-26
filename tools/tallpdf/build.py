import re, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
tool = open(os.path.join(HERE, 'tool-src.html')).read()
guide = open(os.path.join(HERE, 'guide-src.html')).read()

def css_of(src):
    return re.search(r'<style>\n(.*?)</style>', src, re.S).group(1)

def drop_rule(css, sel):
    return re.sub(r'(?m)^' + re.escape(sel) + r' \{[^}]*\}\n', '', css, count=1)

# ---------- tokens (from the tool, plus the few the guide adds) ----------
tool_css = css_of(tool)
cut = tool_css.index('\n* { box-sizing')
tokens = tool_css[:cut]
tool_rest = tool_css[cut:]
tool_rest = drop_rule(tool_rest, 'body')          # the site sets the body
tool_rest = drop_rule(tool_rest, '[hidden]')
tool_rest = drop_rule(tool_rest, '* { box-sizing: border-box; }'.split(' {')[0])

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
.wrap.mid { max-width: 1000px; }

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

.sec { padding-top: 56px; display: grid; gap: 18px; }
.sec h2 { margin: 0; font-size: clamp(24px, 3.4vw, 32px); line-height: 1.15; letter-spacing: -0.02em; text-wrap: balance; }
.sec > p { margin: 0; color: var(--ink-2); max-width: 44rem; }
.cards { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
.card { display: grid; align-content: start; gap: 8px; padding: 20px; background: var(--surface); border: 1px solid var(--line); border-radius: 14px; }
.card h3 { margin: 0; font-size: 18px; letter-spacing: -0.01em; }
.card p { margin: 0; color: var(--ink-2); font-size: 15.5px; }
.card .ico { width: 44px; height: 30px; }
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
.prose ul { margin: 0; padding-left: 22px; display: grid; gap: 8px; }
.prose .meta { font-family: var(--font-mono); font-size: 13px; color: var(--ink-2); }
.prose .todo { background: var(--accent-soft); border: 1px dashed var(--accent); color: var(--ink); padding: 2px 8px; border-radius: 6px; font-family: var(--font-mono); font-size: 0.9em; }

@media (max-width: 860px) { .cards { grid-template-columns: minmax(0, 1fr); } }
"""

# ---------- brand mark ----------
MARK = ('<svg width="22" height="30" viewBox="0 0 22 30" aria-hidden="true">'
        '<rect x="3" y="1" width="16" height="28" rx="3" fill="#fff" stroke="var(--line)" stroke-width="1.5"/>'
        '<rect x="7" y="5" width="8" height="2.4" rx="1" fill="#39424f"/><rect x="7" y="10" width="8" height="5" rx="1" fill="#2a8ea3"/>'
        '<line x1="0" y1="18.5" x2="22" y2="18.5" stroke="var(--cut)" stroke-width="1.8" stroke-dasharray="3 2"/>'
        '<rect x="7" y="22" width="8" height="2" rx="1" fill="#c8cfda"/></svg>')
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 22 30'%3E"
           "%3Crect x='3' y='1' width='16' height='28' rx='3' fill='white' stroke='%230e7490' stroke-width='1.5'/%3E"
           "%3Crect x='7' y='5' width='8' height='2.4' rx='1' fill='%2339424f'/%3E%3Crect x='7' y='10' width='8' height='5' rx='1' fill='%232a8ea3'/%3E"
           "%3Cline x1='0' y1='18.5' x2='22' y2='18.5' stroke='%23d6246e' stroke-width='2' stroke-dasharray='3 2'/%3E%3C/svg%3E")

PAGES = [('index.html', 'Tool'), ('how-to.html', 'How to use'), ('about.html', 'About'), ('privacy.html', 'Privacy')]

def header(current):
    links = ''.join('<a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if h == current else '', n) for h, n in PAGES)
    return ('<header class="site-head"><a class="brand" href="index.html">%s<span>Tall PDF Slicer</span></a>'
            '<nav class="site-nav" aria-label="Main">%s<button type="button" class="navbtn" data-contact>Contact</button></nav></header>' % (MARK, links))

STUDIO_HREF = '../'

def footer():
    return ('<footer class="site-foot"><span>A free tool by <a href="%s">Verbose Studio</a>. Your files stay in your browser.</span>'
            '<nav aria-label="Footer"><a href="index.html">Tool</a><a href="how-to.html">How to use</a>'
            '<a href="about.html">About</a><a href="privacy.html">Privacy</a><button type="button" class="linkbtn" data-contact>Contact</button></nav></footer>') % STUDIO_HREF

def doc(title, desc, css, body, scripts='', artifact=False, head_extra=''):
    """artifact=True: return a fragment (no doctype/html/head/body) for the Artifact tool's wrapper."""
    css = css + CONTACT_CSS
    body = body + CONTACT_HTML
    scripts = scripts + CONTACT_JS
    meta = '' if artifact else (
        '<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
        '<meta name="description" content="%s"><meta property="og:title" content="%s"><meta property="og:description" content="%s">'
        '<meta property="og:type" content="website">' % (desc, title, desc))
    fonts = ('<link rel="icon" href="%s">'
             '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
             '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">' % FAVICON)
    inner = '<title>%s</title>%s%s%s<style>\n%s</style>\n%s\n%s' % (title, meta if not artifact else '', fonts, head_extra, css, body, scripts)
    if artifact:
        return inner
    return '<!doctype html>\n<html lang="en">\n<head>%s</head>\n<body>\n%s\n%s\n</body>\n</html>\n' % (
        inner.split('<style>')[0].replace('<title>', '<title>', 1), '', '') if False else (
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<title>%s</title>\n<meta name="description" content="%s"><meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:type" content="website">\n'
        '%s%s\n<style>\n%s</style>\n</head>\n<body>\n%s\n%s\n</body>\n</html>\n' % (title, desc, title, desc, fonts, head_extra, css, body, scripts))


FORM_ENDPOINT = 'https://api.web3forms.com/submit'
FORM_KEY = '00640895-65d1-4e34-b1c1-8dc6575510a4'   # public Web3Forms key for the Tall PDF form
TOOL_TAG = 'Tall PDF Slicer'

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
    ('Does it change my original file?',
     'No. You get a new PDF. The original stays exactly as it was.'),
    ('Will the text and pictures stay sharp?',
     'Yes. The tool cuts the original page into pieces without re-drawing it, so text stays crisp and scanned images are not compressed again.'),
    ('What page sizes can I get?',
     'Letter (portrait or landscape), A4, Legal, Tabloid, A5, or any custom size you type in.'),
    ('Why is my PDF one very long page?',
     'Some note apps and scanners save a whole note or scan as one continuous page instead of breaking it into sheets as they go. Regular PDF tools split a file between pages, so they cannot help here.'),
    ('My PDF has more than one page. Can I use it?',
     'Yes. If the file has several pages, pick the one you want to slice from the Page to slice menu.'),
    ('Does it work on a phone?',
     'It is built to work in a phone browser. Placing cuts is easier on a computer with a mouse, and very long pages load faster there.'),
    ('Is it free?',
     'Yes. There is no account to make and nothing to install.'),
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
tool_libs = ('<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>\n'
             '<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf-lib/1.17.1/pdf-lib.min.js"></script>')

def ico_cut():
    return ('<svg class="ico" viewBox="0 0 44 30" aria-hidden="true"><rect x="8" y="1" width="28" height="28" rx="4" fill="#fff" stroke="var(--line)" stroke-width="1.5"/>'
            '<rect x="14" y="5" width="16" height="6" rx="1.5" fill="#2a8ea3"/><line x1="4" y1="16" x2="40" y2="16" stroke="var(--cut)" stroke-width="2" stroke-dasharray="4 3"/>'
            '<rect x="14" y="20" width="16" height="3" rx="1.5" fill="#c8cfda"/></svg>')
def ico_drag():
    return ('<svg class="ico" viewBox="0 0 44 30" aria-hidden="true"><line x1="4" y1="20" x2="40" y2="20" stroke="var(--cut)" stroke-width="2" stroke-dasharray="4 3"/>'
            '<rect x="24" y="12" width="16" height="16" rx="8" fill="var(--cut)"/><path d="M32 16 v8 M29 19 l3 -3 l3 3 M29 21 l3 3 l3 -3" stroke="var(--cut-ink)" stroke-width="1.4" fill="none"/></svg>')
def ico_skip():
    return ('<svg class="ico" viewBox="0 0 44 30" aria-hidden="true"><rect x="8" y="1" width="28" height="28" rx="4" fill="#fff" stroke="var(--line)" stroke-width="1.5"/>'
            '<rect x="8" y="10" width="28" height="10" fill="#c3c9d3"/><path d="M8 20 L18 10 M16 20 L26 10 M24 20 L34 10 M32 20 L36 16" stroke="#8b95a4" stroke-width="2"/>'
            '<rect x="14" y="4" width="16" height="3" rx="1.5" fill="#39424f"/><rect x="14" y="23" width="16" height="3" rx="1.5" fill="#c8cfda"/></svg>')

HOME_ABOVE = ('<section class="page-hero"><h1>Split a tall PDF into regular pages</h1>'
              '<p>Got a PDF that is one very long page, from a tablet note or a scanner? Drop it in and get normal Letter or A4 pages. Free, and your file never leaves your browser.</p>'
              '<span class="newhere">New here? <a href="how-to.html">See how it works in one minute</a>.</span></section>')

HOME_BELOW = """
<section class="sec" aria-labelledby="what">
  <h2 id="what">What it does</h2>
  <p>Some apps and scanners save a whole note as one giant page. This tool cuts that page into regular pages at the size you choose, so you can print, share or file it like any other PDF.</p>
  <div class="cards">
    <div class="card">%s<h3>Cuts in the gaps</h3><p>Automatic mode looks for the white space between paragraphs and pictures, so lines of text and images are not sliced in half.</p></div>
    <div class="card">%s<h3>Drag to adjust</h3><p>Every cut is a dashed line you can move. Its label tells you whether it sits in a gap or passes through content.</p></div>
    <div class="card">%s<h3>Leave sections out</h3><p>Put a cut above and below something you do not want, like a checklist, then untick it. It is skipped in the new PDF.</p></div>
  </div>
</section>

<section class="sec" aria-labelledby="faq">
  <h2 id="faq">Common questions</h2>
  %s
</section>

<section class="sec">
  <div class="band-cta">
    <div><h2>Want to see it in action?</h2><p>The guide shows each step with a short demo.</p></div>
    <a class="pbtn" href="how-to.html">See how to use it</a>
  </div>
</section>
""" % (ico_cut(), ico_drag(), ico_skip(), faq_html())

SEO_TITLE = {
    'index.html': 'Tall PDF Slicer: Split One Long PDF Page into Regular Pages',
    'how-to.html': 'How to Split a Long, Tall PDF into Regular Pages',
    'about.html': 'About Tall PDF Slicer',
    'privacy.html': 'Privacy | Tall PDF Slicer',
}
ART_TITLE = {'index.html': 'Tall PDF Slicer', 'how-to.html': 'Tall PDF Slicer: How to use', 'about.html': 'Tall PDF Slicer: About', 'privacy.html': 'Tall PDF Slicer: Privacy'}
DESC = {
    'index.html': 'Free tool that cuts a PDF that is one very tall page, like a tablet note or scan, into regular Letter or A4 pages. Works in your browser and your file is never uploaded.',
    'how-to.html': 'Five short steps, with demos, for splitting a long single-page PDF into regular pages using Tall PDF Slicer.',
    'about.html': 'Why Tall PDF Slicer exists and how it works.',
    'privacy.html': 'How Tall PDF Slicer handles your files and what it stores. Your PDF is never uploaded.',
}

def home(artifact):
    css = tokens + EXTRA_TOKENS + BASE_CSS + tool_rest + "\n.app { font-size: 15px; line-height: 1.45; }\n.app .btn { text-decoration: none; }\n#tool { scroll-margin-top: 12px; }\n"
    body = ('<div class="wrap">\n%s\n%s\n<section id="tool" aria-label="PDF slicer">\n%s\n</section>\n%s\n%s\n</div>\n%s\n' %
            (header('index.html'), HOME_ABOVE, tool_main, HOME_BELOW, footer(), tool_dock))
    scripts = tool_libs + '\n' + tool_js + '\n' + faq_ld()
    t = (ART_TITLE if artifact else SEO_TITLE)['index.html']
    return doc(t, DESC['index.html'], css, body, scripts, artifact)

# ---------- HOW TO ----------
gcss = css_of(guide)
gcut = gcss.index('\n* { box-sizing')
g_rest = gcss[gcut:]
for sel in ['* { box-sizing: border-box; }'.split(' {')[0], '[hidden]', 'body', ':focus-visible', 'a', '.wrap', '.site', '.brand', '.btn', '.btn:hover', '.btn.primary', '.btn.primary:hover']:
    g_rest = drop_rule(g_rest, sel)
g_defs = re.search(r'<svg width="0".*?</svg>', guide, re.S).group(0)
g_main_inner = re.search(r'<main id="top">(.*?)</main>', guide, re.S).group(1)
g_main_inner = g_main_inner.replace('https://claude.ai/artifact/7dFNeptbDSw1LTYHkG2DTY" target="_blank" rel="noopener', 'index.html#tool')
g_main_inner = g_main_inner.replace('<!-- Swap this address', '<!-- unused')
g_js = re.findall(r'<script>\n\(function \(\) \{.*?\}\)\(\);\n</script>', guide, re.S)[-1]
g_main_inner = g_main_inner.replace('class="btn primary" href="index.html#tool"', 'class="pbtn" href="index.html#tool"')
_x = (r'<a class="btn( primary)?" href="https://claude\.ai/artifact/[^"]*"[^>]*>', '<a class="pbtn" href="index.html#tool">', g_main_inner)

def howto(artifact):
    css = tokens + EXTRA_TOKENS + BASE_CSS + g_rest
    body = '<div class="wrap mid">\n%s\n%s\n<main id="top">%s</main>\n%s\n</div>\n' % (header('how-to.html'), g_defs, g_main_inner, footer())
    t = (ART_TITLE if artifact else SEO_TITLE)['how-to.html']
    return doc(t, DESC['how-to.html'], css, body, g_js, artifact)

# ---------- ABOUT ----------
ABOUT = """
<section class="page-hero"><h1>About Tall PDF Slicer</h1><p>A small free tool for one specific annoyance.</p></section>
<div class="prose">
  <h2>Why it exists</h2>
  <p>Many note apps and scanners save a long note as one single, very tall PDF page. Regular PDF tools split a file between its pages, so they cannot help when the whole file is one page. Tall PDF Slicer was made for that case.</p>
  <h2>What it does</h2>
  <p>It cuts one tall page into regular pages at the size you pick. It tries to cut in the gaps between content so text and pictures stay whole. You can move any cut, add your own, or leave a section out of the result.</p>
  <h2>Who makes it</h2>
  <p>One person makes and looks after this site. It is a small project, kept simple on purpose.</p>
  <h2>Your files</h2>
  <p>Your PDF is processed in your browser and is never uploaded. The <a href="privacy.html">privacy page</a> explains what the site does and does not store.</p>
  <h2>Get in touch</h2>
  <p>Questions, bug reports or ideas are welcome. Use the <button type="button" class="linkbtn" data-contact style="font-size:inherit;color:var(--accent)">Contact</button> button and your message goes straight to us.</p>
</div>
"""
def about(artifact):
    css = tokens + EXTRA_TOKENS + BASE_CSS
    body = '<div class="wrap narrow">\n%s\n%s\n%s\n</div>\n' % (header('about.html'), ABOUT, footer())
    t = (ART_TITLE if artifact else SEO_TITLE)['about.html']
    return doc(t, DESC['about.html'], css, body, '', artifact)

# ---------- PRIVACY ----------
PRIV = """
<section class="page-hero"><h1>Privacy</h1><p>Short version: your PDF stays on your device.</p></section>
<div class="prose">
  <p class="meta">Last updated: September 25, 2026</p>
  <h2>Your files</h2>
  <p>Tall PDF Slicer reads your PDF and builds the new one inside your browser. Your file is not uploaded, sent to a server or kept by this site. When you close or refresh the page, it is gone from the page.</p>
  <h2>What is saved on your device</h2>
  <p>The page remembers a few settings in your browser so you do not have to pick them again: the page size you chose, Automatic or Manual mode, and the zoom level. This stays on your device and is not sent anywhere. This site does not set cookies of its own.</p>
  <h2>Other services this page loads</h2>
  <ul>
    <li>Google Fonts supplies the typefaces.</li>
    <li>cdnjs, run by Cloudflare, supplies the open-source code libraries that read and build PDFs (pdf.js and pdf-lib).</li>
  </ul>
  <p>When your browser loads these, those services can see ordinary request details such as your IP address and browser type, as with any website. They never receive your PDF.</p>
  <h2>Analytics and ads</h2>
  <p>At the moment this site has no analytics and shows no ads. If that changes, this page will be updated first to say what is used and how you can opt out.</p>
  <h2>If you contact us</h2>
  <p>The Contact form sends us your message, the topic you chose, and your email address only if you type one in. We use it to read and reply to you, and we do not share it or add it to any list. The message is delivered by a third-party form service. Please do not put anything private in it, and never include the contents of your PDF.</p>
</div>
"""
def privacy(artifact):
    css = tokens + EXTRA_TOKENS + BASE_CSS
    body = '<div class="wrap narrow">\n%s\n%s\n%s\n</div>\n' % (header('privacy.html'), PRIV, footer())
    t = (ART_TITLE if artifact else SEO_TITLE)['privacy.html']
    return doc(t, DESC['privacy.html'], css, body, '', artifact)


# ---------- STUDIO LANDING PAGE ----------
def studio_home():
    css = tokens + EXTRA_TOKENS + BASE_CSS + """
.tools { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 300px), 1fr)); gap: 16px; }
.tool { display: grid; gap: 8px; align-content: start; padding: 22px; background: var(--surface); border: 1px solid var(--line); border-radius: 14px; color: var(--ink); text-decoration: none; }
a.tool:hover { border-color: var(--accent); box-shadow: var(--shadow); }
.tool h3 { margin: 0; font-size: 20px; letter-spacing: -0.01em; }
.tool p { margin: 0; color: var(--ink-2); font-size: 15.5px; }
a.tool .go { color: var(--accent); font-weight: 600; font-size: 15px; }
a.tool .thumb { height: 64px; }
.soon { border-style: dashed; background: none; }
.soon h3, .soon p { color: var(--ink-2); }
"""
    thumb = ('<svg class="thumb" viewBox="0 0 120 64" aria-hidden="true"><rect x="46" y="2" width="28" height="60" rx="4" fill="#fff" stroke="var(--line)" stroke-width="1.5"/>'
             '<rect x="52" y="8" width="16" height="4" rx="1.5" fill="#39424f"/><rect x="52" y="16" width="16" height="12" rx="2" fill="#2a8ea3"/>'
             '<line x1="34" y1="36" x2="86" y2="36" stroke="var(--cut)" stroke-width="2" stroke-dasharray="4 3"/>'
             '<rect x="52" y="42" width="16" height="3" rx="1.5" fill="#c8cfda"/><rect x="52" y="49" width="16" height="3" rx="1.5" fill="#c8cfda"/></svg>')
    head = ('<header class="site-head"><a class="brand" href="index.html"><span>Verbose Studio</span></a>'
            '<nav class="site-nav" aria-label="Main"><a href="tallpdf/" >Tall PDF Slicer</a><button type="button" class="navbtn" data-contact>Contact</button></nav></header>')
    foot = ('<footer class="site-foot"><span>Small, free, private tools. Your files stay in your browser.</span>'
            '<nav aria-label="Footer"><a href="tallpdf/privacy.html">Privacy</a><button type="button" class="linkbtn" data-contact>Contact</button></nav></footer>')
    body = ('<div class="wrap">%s<section class="page-hero"><h1>Small tools that do one thing well</h1>'
            '<p>Free, simple tools for everyday jobs. Nothing to install, no account, and your files never leave your browser.</p></section>'
            '<section class="sec" style="padding-top:24px"><h2>Tools</h2><div class="tools">'
            '<a class="tool" href="tallpdf/">%s<h3>Tall PDF Slicer</h3><p>Cut a PDF that is one very long page, like a tablet note or a scan, into regular Letter or A4 pages.</p><span class="go">Open the tool &rarr;</span></a>'
            '<div class="tool soon"><h3>More on the way</h3><p>Have an idea for a tool, or something that annoys you? Use Contact and tell us.</p></div>'
            '</div></section>%s</div>' % (head, thumb, foot))
    return doc('Verbose Studio: Small, Free, Private Tools', 'Small free tools that do one job well and run in your browser, so your files never leave your device.', css, body, '', False)

OUT = os.path.join(HERE, '..', '..', 'public')
import os as _os
_os.makedirs(os.path.join(OUT, 'tallpdf'), exist_ok=True)

BUILD = [('index.html', home), ('how-to.html', howto), ('about.html', about), ('privacy.html', privacy)]
for name, fn in BUILD:
    STUDIO_HREF = '../'
    open(os.path.join(OUT, 'tallpdf', name), 'w').write(fn(False))
print('built Tall PDF Slicer into public/tallpdf:', [n for n, _ in BUILD])
