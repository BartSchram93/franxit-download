#!/usr/bin/env python3
"""Builds the site's pages from tools/site.css and tools/texts.py:
index.html (Dutch), fr/index.html, en/index.html and p/index.html (what a shared product link
shows to someone without the app). Run from the repository root: python3 tools/build_site.py"""
import json, os, sys, urllib.parse
sys.path.insert(0, os.path.dirname(__file__))
from texts import LANGS, MONTHS, date_text

CSS = open(os.path.join(os.path.dirname(__file__), "site.css"), encoding="utf-8").read()
APK = "https://github.com/BartSchram93/franxit-download/releases/latest/download/franxit.apk"
RELEASES_API = "https://api.github.com/repos/BartSchram93/franxit-download/releases/latest"
ORDER = ["nl", "fr", "en"]
PREVIEW = {"nl": "preview.png", "fr": "preview-fr.png", "en": "preview-en.png"}

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def page(code):
    t = LANGS[code]
    root = "" if code == "nl" else "../"
    url = "https://franxit.be/" + t["path"]
    privacy = f"{root}privacy.html#{code}"
    langs_nav = " · ".join(
        f"<b>{LANGS[c]['name']}</b>" if c == code else f'<a href="/{LANGS[c]["path"]}" hreflang="{c}" data-lang="{c}">{LANGS[c]["name"]}</a>'
        for c in ORDER)
    alternates = "\n".join(f'<link rel="alternate" hreflang="{c}" href="https://franxit.be/{LANGS[c]["path"]}">' for c in ORDER)
    alternates += '\n<link rel="alternate" hreflang="x-default" href="https://franxit.be/">'
    shot_list = [s for s in t["shots"] if s[0] != "overview"]
    shots = "\n".join(
        f'    <figure class="phone"><div class="step"><b>{i + 1}</b><div><strong>{t["steps"][i][0]}</strong><span>{t["steps"][i][1]}</span></div></div><img src="{root}screens/{"share.webp" if n == "share" else code + "/" + n + ".webp"}" alt="{esc(alt)}" width="460" height="969" loading="lazy"></figure>'
        for i, (n, alt, cap) in enumerate(shot_list))
    legend = "\n".join(f'    <li><strong style="--c:var(--{c})"><i></i>{n}</strong><span>{d}</span></li>' for c, n, d in t["legend"])
    features = "\n".join(f'    <li class="feature"><strong>{a}</strong><p>{b}</p></li>' for a, b in t["features"])
    story = "\n".join(f"    <p>{p}</p>" for p in t["story"])
    install = "\n".join(f"      <li>{x}</li>" for x in t["install_steps"])
    faq = "\n".join(f"  <details>\n    <summary>{q}</summary>\n    {a.replace('[[privacy]]', privacy)}\n  </details>" for q, a in t["faq"])
    share = "https://wa.me/?text=" + urllib.parse.quote(t["share_text"], safe="")
    js_texts = json.dumps(dict(version=t["version_label"], updated=t["updated_label"], months=MONTHS[code], decimal=t["decimal"]), ensure_ascii=False)
    redirect = ""
    if code == "nl":
        # First visit from a French or English phone: show that language (unless a language was chosen before).
        redirect = """<script>try{if(!localStorage.getItem("lang")){var l=(navigator.language||"").slice(0,2);if(l==="fr")location.replace("/fr/");else if(l==="en")location.replace("/en/");}}catch(e){}</script>
"""
    return f"""<!doctype html>
<html lang="{code}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(t["title"])}</title>
<meta name="description" content="{esc(t["desc"])}">
<meta name="theme-color" content="#2f6fdb">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="{t["og_locale"]}">
<meta property="og:title" content="{esc(t["og_title"])}">
<meta property="og:description" content="{esc(t["desc"])}">
<meta property="og:image" content="https://franxit.be/{PREVIEW[code]}?v=3">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{url}">
{alternates}
<link rel="icon" href="{root}icon.png">
<link rel="apple-touch-icon" href="{root}icon.png">
{redirect}<script>(function(){{var u=navigator.userAgent||"",d=document.documentElement;d.className=/iPhone|iPad|iPod/.test(u)||(/Macintosh/.test(u)&&navigator.maxTouchPoints>1)?"ios":/Android/.test(u)?"android":"desktop";}})();</script>
<style>
{CSS}</style>
</head>
<body>
<main>

  <nav class="langs" aria-label="Language">{langs_nav}</nav>

  <section class="hero">
   <div class="hero-copy">
    <p class="brand"><img src="{root}icon.png" alt="" width="28" height="28">FRANXIT</p>
    <h1>{t["h1"]}</h1>
    <p class="lead">{t["lead"]}</p>
    <p class="ios-note">{t["ios_note"]}</p>
    <div class="qr"><img src="{root}qr.svg" alt="{esc(t["qr_alt"])}" width="160" height="160"><span><strong>{t["qr_strong"]}</strong><br>{t["qr_text"]}</span></div>
    <a class="get" id="download" href="{APK}">
      <span class="get-top">
        <img class="get-icon" src="{root}icon.png" alt="">
        <span class="get-text"><strong>{t["get_title"]}</strong><small><span id="meta">{t["android_min"]}</span><span>{t["android_min"]}</span></small></span>
      </span>
      <span class="get-go">{t["download"]}</span>
    </a>
    <p class="calm">{t["calm"]}</p>
    <button class="copy" type="button" data-done="{esc(t["copied"])}" data-url="{url}">{t["copy_label"]}</button>
    <p class="source">{t["source"]}</p>
   </div>
   <div class="hero-shot"><img src="{root}screens/{code}/overview.webp" alt="{esc(t["shots"][1][1])}" width="460" height="969" fetchpriority="high"></div>
  </section>

  <section class="wide">

  <h2>{t["steps_h"]}</h2>
  <div class="shots" id="shots">
{shots}
  </div>
  <div class="dots" id="dots" aria-hidden="true">{"<span></span>" * len(t["shots"])}</div>
  <p class="advice-h">{t["legend_note"]}</p>
  <ul class="legend">
{legend}
  </ul>

  </section>

  <section class="narrow">
  <h2>{t["why_h"]}</h2>
  <div class="story">
{story}
    <p class="signature">{t["signature"]}</p>
  </div>

  <h2 class="minor">{t["faq_h"]}</h2>
  <div class="faq">
  <details id="installeren">
    <summary>{t["install_q"]}</summary>
    <p>{t["install_sub"]}</p>
    <ol class="install-steps">
{install}
    </ol>
    <p class="small">{t["install_note"]}</p>
  </details>
{faq}
  </div>

  <a class="dl2" href="{APK}">{t["download"]}</a>
  </section>

  <footer>
    <p>{t["made_by"]}</p>
    <p>{t["only_android"]}</p>
    <p><a class="share" href="{share}" rel="noopener">{t["share_label"]}</a></p>
    <p><a href="{privacy}">{t["privacy_label"]}</a><span id="updated"></span></p>
  </footer>
</main>
<script>
  // Remember a language chosen by hand, so the page doesn't switch it back.
  document.querySelectorAll(".langs a").forEach(function (a) {{
    a.addEventListener("click", function () {{ try {{ localStorage.setItem("lang", a.getAttribute("data-lang")); }} catch (e) {{}} }});
  }});
  try {{ localStorage.setItem("lang", "{code}"); }} catch (e) {{}}
  // "Copy the link" under the QR code.
  var cp = document.querySelector(".copy");
  if (cp) cp.addEventListener("click", function () {{
    var done = function () {{ var o = cp.textContent; cp.textContent = cp.getAttribute("data-done"); setTimeout(function () {{ cp.textContent = o; }}, 2000); }};
    try {{ navigator.clipboard.writeText(cp.getAttribute("data-url")).then(done, function () {{}}); }} catch (e) {{}}
  }});
  // A link to the install steps opens them.
  function openInstall() {{ if (location.hash === "#installeren") {{ var d = document.getElementById("installeren"); if (d) d.open = true; }} }}
  openInstall(); window.addEventListener("hashchange", openInstall);
  // Dots under the screens (phones only): which one is in view.
  (function () {{
    var s = document.getElementById("shots"), d = document.querySelectorAll("#dots span");
    if (!s || !d.length) return;
    function mark() {{
      var w = s.scrollWidth - s.clientWidth, i = w > 0 ? Math.round(s.scrollLeft / w * (d.length - 1)) : 0;
      d.forEach(function (x, n) {{ x.className = n === i ? "on" : ""; }});
      s.className = "shots" + (w > 0 && s.scrollLeft >= w - 4 ? " end" : "");
    }}
    s.addEventListener("scroll", mark, {{ passive: true }}); mark();
  }})();
  // Fills in the version and size of the latest release (no problem if this fails).
  var T = {js_texts};
  fetch("{RELEASES_API}")
    .then(function (r) {{ return r.ok ? r.json() : null; }})
    .then(function (rel) {{
      if (!rel || !rel.tag_name) return;
      var apk = (rel.assets || []).filter(function (a) {{ return a.name === "franxit.apk"; }})[0];
      var parts = [T.version + " " + rel.tag_name.replace(/^v/, "")];
      if (apk && apk.size) parts.push((apk.size / 1e6).toFixed(1).replace(".", T.decimal) + " MB");
      var meta = document.getElementById("meta");
      meta.textContent = parts.join(" · ");
      meta.className = "on";
      if (rel.published_at) {{
        var d = new Date(rel.published_at);
        document.getElementById("updated").textContent = " · " + T.updated + " " + d.getDate() + " " + T.months[d.getMonth()] + " " + d.getFullYear();
      }}
    }})
    .catch(function () {{}});
</script>
</body>
</html>
"""

def landing():
    """p/index.html: the page behind a shared product link, for someone who doesn't have the app (a phone
    that has it opens the app instead). All three languages; the visitor's own is shown."""
    sections = []
    for c in ORDER:
        t = LANGS[c]
        sections.append(f"""  <section lang="{c}" data-lang="{c}" hidden>
    <img class="logo" src="../icon.png" alt="" width="84" height="84">
    <h1>{t["p_title"]}</h1>
    <p class="lead">{t["p_text"]}</p>
    <a class="dl2 only-android" href="{APK}">{t["p_button"]}</a>
    <p class="ios-note-p only-other">{t["p_android_only"]}</p>
    <p class="small">{t["p_installed"]}</p>
    <p><a href="/{t["path"]}">{t["p_more"]}</a></p>
  </section>""")
    sections = "\n".join(sections)
    return f"""<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Franxit</title>
<meta name="theme-color" content="#2f6fdb">
<meta property="og:type" content="website">
<meta property="og:title" content="Franxit">
<meta property="og:description" content="{esc(LANGS["nl"]["p_title"])} · {esc(LANGS["fr"]["p_title"])} · {esc(LANGS["en"]["p_title"])}">
<meta property="og:image" content="https://franxit.be/preview-en.png?v=3">
<link rel="icon" href="../icon.png">
<style>
{CSS}
  .logo {{ border-radius: 21px; display: block; margin: 40px auto 18px; box-shadow: 0 6px 20px rgba(47,111,219,.28); }}
  section {{ text-align: center; }}
  .ios-note-p {{ color: var(--muted); }}
  .only-other {{ display: none; }}
  html:not(.android) .only-android {{ display: none; }}
  html:not(.android) .only-other {{ display: block; }}
</style>
<script>(function(){{var u=navigator.userAgent||"",d=document.documentElement;d.className=/iPhone|iPad|iPod/.test(u)||(/Macintosh/.test(u)&&navigator.maxTouchPoints>1)?"ios":/Android/.test(u)?"android":"desktop";}})();</script>
</head>
<body>
<main>
{sections}
</main>
<script>
  var l = "";
  try {{ l = localStorage.getItem("lang") || ""; }} catch (e) {{}}
  if (["nl", "fr", "en"].indexOf(l) < 0) l = (navigator.language || "").slice(0, 2);
  if (["nl", "fr", "en"].indexOf(l) < 0) l = "en";
  document.documentElement.lang = l;
  document.querySelector('section[data-lang="' + l + '"]').hidden = false;
</script>
</body>
</html>
"""

if __name__ == "__main__":
    for c in ORDER:
        path = os.path.join(LANGS[c]["path"], "index.html")
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        open(path, "w", encoding="utf-8").write(page(c))
        print("wrote", path)
    os.makedirs("p", exist_ok=True)
    open("p/index.html", "w", encoding="utf-8").write(landing())
    print("wrote p/index.html")
