#!/usr/bin/env python3
"""Builds the site's pages from tools/site.css and tools/texts.py:
index.html (Dutch), fr/index.html, en/index.html and p/index.html (what a shared product link
shows to someone without the app). Run from the repository root: python3 tools/build_site.py"""
import datetime, json, os, re, sys, urllib.parse
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
    ov = next(s for s in t["shots"] if s[0] == "overview")
    shots += f'\n    <figure class="phone extra"><div class="step"><b>4</b><div><strong>{t["steps"][3][0]}</strong><span>{t["steps"][3][1]}</span></div></div><img src="{root}screens/{code}/overview.webp" alt="{esc(ov[1])}" width="460" height="969" loading="lazy"></figure>'
    live = "\n".join(f'    <div class="step live-step{" on" if i == 0 else ""}"><b>{i + 1}</b><div><strong>{a}</strong><span>{c}</span></div></div>' for i, (a, c) in enumerate(t["steps"]))
    legend = "\n".join(f'    <li><strong style="--c:var(--{c})"><i></i>{n}</strong><span>{d}</span></li>' for c, n, d in t["legend"])
    features = "\n".join(f'    <li class="feature"><strong>{a}</strong><p>{b}</p></li>' for a, b in t["features"])
    story = "\n".join(f"    <p>{p}</p>" for p in t["story"])
    install = "\n".join(f"      <li>{x}</li>" for x in t["install_steps"])
    faq = "\n".join(f"  <details>\n    <summary>{q}</summary>\n    {a.replace('[[privacy]]', privacy)}\n  </details>" for q, a in t["faq"])
    share = "https://wa.me/?text=" + urllib.parse.quote(t["share_text"], safe="")
    js_texts = json.dumps(dict(version=t["version_label"], updated=t["updated_label"], months=MONTHS[code], decimal=t["decimal"]), ensure_ascii=False)
    def plain(s):
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s.replace("[[privacy]]", privacy))).strip()
    qa = [(t["what_q"], t["what_a"]), (t["install_q"], "<p>" + t["install_sub"] + " " + " ".join(f"{i + 1}. {x}" for i, x in enumerate(t["install_steps"])) + "</p>")] + list(t["faq"])
    site = "https://franxit.be/"
    ld = [
        {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": "Franxit", "url": url, "inLanguage": code,
         "applicationCategory": "ShoppingApplication", "operatingSystem": "Android 8.0 or newer",
         "description": t["desc"], "image": site + "icon.png", "downloadUrl": APK,
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
         "screenshot": [site + ("screens/share.webp" if n == "share" else f"screens/{code}/{n}.webp") for n, _, _ in t["shots"]],
         "featureList": [x for x, _ in t["steps"]], "dateModified": datetime.date.today().isoformat()},
        {"@context": "https://schema.org", "@type": "WebSite", "name": "Franxit", "url": site, "inLanguage": code},
        {"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": code,
         "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for q, a in qa]},
    ]
    jsonld = "\n".join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False).replace("</", "<\\/") + "</script>" for x in ld)
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
<meta property="og:site_name" content="Franxit">
<meta property="og:image:alt" content="{esc(t["og_title"])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(t["og_title"])}">
<meta name="twitter:description" content="{esc(t["desc"])}">
<meta name="twitter:image" content="https://franxit.be/{PREVIEW[code]}?v=3">
<link rel="canonical" href="{url}">
<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1">
{jsonld}
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
    <p class="source">{t["source"]}</p>
   </div>
   <div class="hero-shot"><img src="{root}screens/{code}/overview.webp" alt="{esc(t["shots"][1][1])}" width="460" height="969" fetchpriority="high"></div>
  </section>

  <section class="wide">
  <h2 class="sr-only">{t["steps_h"]}</h2>

  <div class="shots" id="shots">
{shots}
  </div>
  <div class="dots" id="dots" aria-hidden="true">{"<span></span>" * (len(shot_list) + 1)}</div>
  <div class="live" id="live" aria-live="polite">
{live}
  </div>
  <h2 class="advice-h">{t["legend_note"]}</h2>
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
  <details>
    <summary>{t["what_q"]}</summary>
    {t["what_a"]}
  </details>
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
  // A link to the install steps opens them.
  function openInstall() {{ if (location.hash === "#installeren") {{ var d = document.getElementById("installeren"); if (d) d.open = true; }} }}
  window.addEventListener("hashchange", openInstall);
  // Dots under the screens (phones only): which one is in view.
  (function () {{
    var s = document.getElementById("shots"), d = document.querySelectorAll("#dots span");
    if (!s || !d.length) return;
    function mark() {{
      var w = s.scrollWidth - s.clientWidth, i = w > 0 ? Math.round(s.scrollLeft / w * (d.length - 1)) : 0;
      d.forEach(function (x, n) {{ x.className = n === i ? "on" : ""; }});
      s.className = "shots" + (w > 0 && s.scrollLeft >= w - 4 ? " end" : "");
      document.querySelectorAll("#live .live-step").forEach(function (x, n) {{ x.className = "step live-step" + (n === i ? " on" : ""); }});
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

LLMS = """# Franxit

> Franxit is a free Android app that tells you where a product is cheapest and whether now is a good moment to buy it. It looks at the price in several shops and at what the product cost over the past year, and gives advice: buy now, consider, wait, expensive, or "no advice yet" when there is too little price history. It gives advice, not forecasts. No account, no ads. Android only (Android 8 or newer). Available in Dutch, French and English.

## Key facts
- What it does: you pick a product (type its name, or share a shop page with the app); Franxit analyses the price per shop and the price history of the past year, and gives one of five pieces of advice.
- The five advice labels: Buy now (the price is historically very attractive), Consider (good, but not exceptional), Wait (not particularly attractive; wait or set a price alert), Expensive (high compared with the price history), No advice yet (too little history to judge).
- Price: free. No subscription, no account, no advertising.
- Platform: Android only. There is no iPhone version. It is installed from an APK file because the app is not on the Google Play Store.
- Privacy: tracked products stay on the phone. The app only counts, anonymously, how many devices use it per day.
- Name: from the Belgian franc and the English "sit": sitting on your money until it is worth it.

## Pages
- [Franxit (Nederlands)](https://franxit.be/): what Franxit is, how it works, FAQ
- [Franxit (Français)](https://franxit.be/fr/): what Franxit is, how it works, FAQ
- [Franxit (English)](https://franxit.be/en/): what Franxit is, how it works, FAQ
- [Privacy](https://franxit.be/privacy.html): what the app does and does not collect

## Download
- [franxit.apk (latest release)](https://github.com/BartSchram93/franxit-download/releases/latest/download/franxit.apk)
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
    today = datetime.date.today().isoformat()
    bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User", "Claude-SearchBot", "PerplexityBot", "Perplexity-User",
            "Google-Extended", "Applebot-Extended", "Bingbot", "Googlebot", "CCBot", "cohere-ai", "Meta-ExternalAgent", "Bytespider", "Amazonbot", "DuckAssistBot", "MistralAI-User"]
    robots = "# Franxit is happy to be read, summarised and cited by search engines and AI assistants.\n\n" + "".join(f"User-agent: {x}\nAllow: /\nDisallow: /p/\n\n" for x in bots)
    robots += "User-agent: *\nAllow: /\nDisallow: /p/\n\nSitemap: https://franxit.be/sitemap.xml\n"
    open("robots.txt", "w", encoding="utf-8").write(robots)
    urls = ["https://franxit.be/" + LANGS[c]["path"] for c in ORDER]
    alts = "".join(f'    <xhtml:link rel="alternate" hreflang="{c}" href="https://franxit.be/{LANGS[c]["path"]}"/>\n' for c in ORDER) + '    <xhtml:link rel="alternate" hreflang="x-default" href="https://franxit.be/"/>\n'
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    for u in urls:
        sm += f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{today}</lastmod>\n{alts}  </url>\n"
    sm += f"  <url>\n    <loc>https://franxit.be/privacy.html</loc>\n    <lastmod>{today}</lastmod>\n  </url>\n</urlset>\n"
    open("sitemap.xml", "w", encoding="utf-8").write(sm)
    open("llms.txt", "w", encoding="utf-8").write(LLMS)
    lines = "".join(f'  <p lang="{c}" style="margin:0 0 6px">{LANGS[c]["nf"]} <a href="/{LANGS[c]["path"]}">Franxit</a></p>\n' for c in ORDER)
    open("404.html", "w", encoding="utf-8").write(f"""<!doctype html>
<html lang="nl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><title>404 · Franxit</title><link rel="icon" href="/icon.png">
<style>{CSS}
  main {{ text-align: center; padding-top: 18vh; }} img {{ width: 72px; height: 72px; border-radius: 18px; }}
</style></head><body><main>
  <img src="/icon.png" alt="" width="72" height="72">
  <h1 style="margin-top:18px">404</h1>
{lines}</main></body></html>
""")
    print("wrote robots.txt, sitemap.xml, llms.txt")
