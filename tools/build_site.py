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
    steps = "\n".join(f"    <li><div><strong>{a}</strong><span>{b}</span></div></li>" for a, b in t["steps"])
    shots = "\n".join(
        f'    <figure class="phone"><img src="{root}screens/{"share.webp" if n == "share" else code + "/" + n + ".webp"}" alt="{esc(alt)}" width="460" height="969" loading="lazy"><figcaption>{cap}</figcaption></figure>'
        for n, alt, cap in t["shots"])
    legend = "\n".join(f'    <li><strong><i style="background:var(--{c})"></i>{n}</strong><span>{d}</span></li>' for c, n, d in t["legend"])
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
    <p class="brand">FRANXIT</p>
    <h1>{t["h1"]}</h1>
    <p class="lead">{t["lead"]}</p>
    <p class="ios-note">{t["ios_note"]}</p>
    <div class="qr"><img src="{root}qr.svg" alt="{esc(t["qr_alt"])}" width="124" height="124"><span><strong>{t["qr_strong"]}</strong><br>{t["qr_text"]}</span></div>
    <a class="get" id="download" href="{APK}">
      <span class="get-top">
        <img class="get-icon" src="{root}icon.png" alt="">
        <span class="get-text"><strong>{t["get_title"]}</strong><small><span id="meta">{t["android_min"]}</span><span>{t["android_min"]}</span></small></span>
      </span>
      <span class="get-go">{t["download"]}</span>
    </a>
    <p class="calm">{t["calm"]}</p>
    <p class="source">{t["source"]}</p>
  </section>

  <h2>{t["steps_h"]}</h2>
  <ol class="steps">
{steps}
  </ol>

  <h2>{t["see_h"]}</h2>
  <p class="sub">{t["see_sub"].format(date=date_text(code))}</p>
  <div class="shots">
{shots}
  </div>
  <details class="meaning">
    <summary>{t["legend_note"].rstrip(":").rstrip(chr(160))}</summary>
    <ul class="legend">
{legend}
    </ul>
  </details>

  <h2>{t["more_h"]}</h2>
  <p class="sub">{t["more_sub"]}</p>
  <ul class="features">
{features}
  </ul>

  <h2>{t["why_h"]}</h2>
  <div class="card">
{story}
    <p class="small">{t["signature"]}</p>
  </div>

  <h2 id="installeren">{t["install_h"]}</h2>
  <p class="sub">{t["install_sub"]}</p>
  <div class="card">
    <ol>
{install}
    </ol>
    <p class="small" style="margin-top:12px">{t["install_note"]}</p>
  </div>

  <a class="dl2" href="{APK}">{t["download"]}</a>

  <h2>{t["faq_h"]}</h2>
{faq}

  <footer>
    <p>{t["made_by"]}</p>
    <p>{t["only_android"]}</p>
    <p><a class="share" href="{share}" rel="noopener">{t["share_label"]}</a></p>
    <p><a href="{privacy}">{t["privacy_label"]}</a><span id="updated"></span></p>
  </footer>
</main>
<script>
  // Things rise a little as they come into view. What is on screen already stays as it is (no flicker);
  // no motion for people who asked for less of it, and without this script everything simply shows.
  (function () {{
    if (!("IntersectionObserver" in window) || (window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches)) return;
    var io = new IntersectionObserver(function (entries) {{
      entries.forEach(function (e) {{ if (e.isIntersecting) {{ e.target.classList.add("in"); io.unobserve(e.target); }} }});
    }}, {{ rootMargin: "0px 0px -8% 0px", threshold: 0.08 }});
    var all = document.querySelectorAll("main h2, main .sub, main .note, .steps li, .phone, .legend li, .feature, main .card, main details, main .dl2");
    Array.prototype.forEach.call(all, function (el) {{
      if (el.getBoundingClientRect().top < window.innerHeight) return;
      var inGroup = el.parentNode.tagName !== "MAIN";
      var i = inGroup ? Array.prototype.indexOf.call(el.parentNode.children, el) : 0;
      el.style.setProperty("--d", Math.min(i, 5) * 80 + "ms");
      el.classList.add("reveal");
      io.observe(el);
    }});
  }})();
  // Remember a language chosen by hand, so the page doesn't switch it back.
  document.querySelectorAll(".langs a").forEach(function (a) {{
    a.addEventListener("click", function () {{ try {{ localStorage.setItem("lang", a.getAttribute("data-lang")); }} catch (e) {{}} }});
  }});
  try {{ localStorage.setItem("lang", "{code}"); }} catch (e) {{}}
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
