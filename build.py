# -*- coding: utf-8 -*-
"""Build inner pages from markdown + index.html chrome. Not part of the public site."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

INNER_CSS = """
/* inner page layout */
.page-title{background:var(--mist);padding:52px 0 44px}
.page-body{padding:48px 0 72px}
.page-col{max-width:800px;margin:0 auto;padding:0 20px}
.page-col p{max-width:none}
.page-col h2{margin-top:2.4em}
.page-col > h2:first-child{margin-top:0}
.page-col h3{margin-top:1.35em}
.page-col ul,.page-col ol{margin:0 0 1.15em;padding-left:1.3em}
.page-col li{margin:0 0 .4em}
.page-actions{display:flex;flex-wrap:wrap;gap:12px;margin:22px 0 0}
.btn--outline{background:#fff;color:var(--ink);border-color:var(--ink)}
.related{margin:1em 0 0}
.related a{font-weight:700}
.cta .form-card{color:var(--ink);max-width:560px;margin-top:8px}
.cta .form-card h2{color:var(--ink)}
.cta .form-card .form-note{color:var(--slate)}
.cta .page-col > p a{color:inherit;font-weight:700}
.page-body .form-card{margin-top:10px}
.page-col .faq{margin-top:8px}
"""

NOTE_RE = re.compile(r"[ \t]*\*\([^)]*\)\*")
HREF_RE = re.compile(r'href="(/[^"]*)"')
TOKEN_PLAIN = [
    ("[Business Name]", "{{BUSINESS_NAME}}"),
    ("[Email]", "contact@pestcontroldownersgroveil.com"),
    ("[Date]", "{{EFFECTIVE_DATE}}"),
    ("[License number]", "{{LICENSE_NUMBER}}"),
]

PEST_OPTIONS = [
    "Ants",
    "Carpenter ants",
    "Termites",
    "Mice",
    "Rats",
    "Bed bugs",
    "Cockroaches",
    "Spiders",
    "Wasps or hornets",
    "Yellow jackets",
    "Mosquitoes",
    "Ticks",
    "Fleas",
    "Boxelder bugs",
    "Stink bugs",
    "Asian lady beetles",
    "Carpenter bees",
    "Silverfish",
    "Centipedes",
    "Earwigs",
    "Not sure",
    "Year round protection plan",
]

CONTACT_PEST_OPTIONS = [
    "Ants",
    "Carpenter ants",
    "Termites",
    "Mice",
    "Rats",
    "Bed bugs",
    "Cockroaches",
    "Spiders",
    "Wasps or hornets",
    "Yellow jackets",
    "Mosquitoes",
    "Ticks",
    "Fleas",
    "Boxelder bugs",
    "Stink bugs",
    "Lady beetles",
    "Carpenter bees",
    "Silverfish",
    "Centipedes",
    "Earwigs",
    "Not sure",
    "Year round protection plan",
]

def md_files() -> list[Path]:
    files = sorted(ROOT.glob("[0-9][0-9]-*.md"), key=lambda p: p.name)
    return [p for p in files if not p.name.startswith("01-")]


def slash_path(url: str) -> str:
    if not url.startswith("/") or url.startswith("//"):
        return url
    if url == "/":
        return "/"
    if "#" in url:
        path, frag = url.split("#", 1)
        if path and path != "/" and not path.endswith("/"):
            path += "/"
        return f"{path}#{frag}" if path else f"#{frag}"
    last = url.rstrip("/").split("/")[-1]
    if "." in last:
        return url
    if not url.endswith("/"):
        url += "/"
    return url


def add_trailing_slashes(html: str) -> str:
    def repl(m: re.Match) -> str:
        href = m.group(1)
        return f'href="{slash_path(href)}"'

    return HREF_RE.sub(repl, html)


def apply_plain_tokens(text: str) -> str:
    for a, b in TOKEN_PLAIN:
        text = text.replace(a, b)
    return text


def strip_notes(text: str) -> str:
    return NOTE_RE.sub("", text)


def inline(text: str) -> str:
    def link_sub(m: re.Match) -> str:
        label, url = m.group(1), m.group(2)
        return f'<a href="{slash_path(url)}">{label}</a>'

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_sub, text)
    text = text.replace("[Phone]", '<a href="tel:{{PHONE_TEL}}">{{PHONE_DISPLAY}}</a>')
    text = text.replace("[Email]", '<a href="mailto:contact@pestcontroldownersgroveil.com">contact@pestcontroldownersgroveil.com</a>')
    text = apply_plain_tokens(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return text


def plain_text(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = text.replace("[Phone]", "{{PHONE_DISPLAY}}")
    text = apply_plain_tokens(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def option_tags(options: list[str]) -> str:
    parts = ['          <option value="">Choose one</option>']
    for o in options:
        parts.append(f"          <option>{o}</option>")
    return "\n".join(parts)


def estimate_form(source_page: str = "/", options: list[str] | None = None) -> str:
    opts = option_tags(options or PEST_OPTIONS)
    return f"""    <form id="estimate" class="form-card" action="{{{{FORM_ACTION_URL}}}}" method="post">
      <h2>Get your free estimate</h2>
      <p class="sub">Tell us what you are seeing. We will call or text you back.</p>
      <div class="hp" aria-hidden="true"><label>Leave this empty<input type="text" name="company" tabindex="-1" autocomplete="off"></label></div>
      <input type="hidden" name="source_page" value="{source_page}">
      <div class="field">
        <label for="f-name">Full name</label>
        <input id="f-name" name="name" type="text" autocomplete="name" required>
      </div>
      <div class="row2">
        <div class="field">
          <label for="f-phone">Phone number</label>
          <input id="f-phone" name="phone" type="tel" autocomplete="tel" required>
        </div>
        <div class="field">
          <label for="f-zip">ZIP code</label>
          <input id="f-zip" name="zip" type="text" inputmode="numeric" pattern="[0-9]{{5}}" maxlength="5" autocomplete="postal-code" required>
        </div>
      </div>
      <div class="field">
        <label for="f-property">Is this for a home or a business?</label>
        <select id="f-property" name="property_type" required>
          <option value="">Choose one</option>
          <option>Home</option>
          <option>Apartment or rental property</option>
          <option>Business</option>
        </select>
      </div>
      <div class="field">
        <label for="f-pest">What pest are you dealing with?</label>
        <select id="f-pest" name="pest" required>
{opts}
        </select>
      </div>
      <div class="field">
        <label for="f-details">Where are you seeing them? (optional)</label>
        <textarea id="f-details" name="details"></textarea>
      </div>
      <label class="consent"><input type="checkbox" name="consent" required><span>I agree to be contacted about my request by call, text or email.</span></label>
      <button class="btn btn--gold btn--lg" type="submit">Request my free estimate</button>
      <p class="form-note">Prefer to talk? Call <a href="tel:{{{{PHONE_TEL}}}}">{{{{PHONE_DISPLAY}}}}</a></p>
    </form>"""


def contact_form() -> str:
    opts = option_tags(CONTACT_PEST_OPTIONS)
    return f"""    <form id="estimate" class="form-card" action="{{{{FORM_ACTION_URL}}}}" method="post">
      <div class="hp" aria-hidden="true"><label>Leave this empty<input type="text" name="company" tabindex="-1" autocomplete="off"></label></div>
      <input type="hidden" name="source_page" value="/contact/">
      <div class="field">
        <label for="f-name">Full name</label>
        <input id="f-name" name="name" type="text" autocomplete="name" required>
      </div>
      <div class="row2">
        <div class="field">
          <label for="f-phone">Phone number</label>
          <input id="f-phone" name="phone" type="tel" autocomplete="tel" required>
        </div>
        <div class="field">
          <label for="f-email">Email address</label>
          <input id="f-email" name="email" type="email" autocomplete="email" required>
        </div>
      </div>
      <div class="field">
        <label for="f-address">Street address or ZIP code</label>
        <input id="f-address" name="address" type="text" autocomplete="street-address" required>
      </div>
      <div class="field">
        <label for="f-property">Is this for a home or a business?</label>
        <select id="f-property" name="property_type" required>
          <option value="">Choose one</option>
          <option>Home</option>
          <option>Apartment or rental property</option>
          <option>Business</option>
        </select>
      </div>
      <div class="field">
        <label for="f-pest">What pest are you dealing with?</label>
        <select id="f-pest" name="pest" required>
{opts}
        </select>
      </div>
      <div class="field">
        <label for="f-details">Where are you seeing them, and for how long?</label>
        <textarea id="f-details" name="details"></textarea>
      </div>
      <div class="field">
        <label for="f-time">Best time to reach you</label>
        <select id="f-time" name="best_time">
          <option value="">Choose one</option>
          <option>Morning</option>
          <option>Afternoon</option>
          <option>Evening</option>
        </select>
      </div>
      <label class="consent"><input type="checkbox" name="consent" required><span>I agree to be contacted about my request by call, text or email.</span></label>
      <button class="btn btn--gold btn--lg" type="submit">Request My Free Estimate</button>
    </form>"""


def is_button_line(line: str) -> bool:
    s = line.strip()
    return bool(
        re.fullmatch(
            r"\*\*\[Call (?:Now|\[Phone\])\]\*\*(?:\s+\*\*\[(?:Get a Free Estimate|Book an Inspection)\]\*\*)?",
            s,
        )
    )


def button_html(line: str) -> str:
    s = line.strip()
    parts = []
    if "**[Call [Phone]]**" in s:
        parts.append(
            '<a class="btn btn--gold btn--lg" href="tel:{{PHONE_TEL}}"><svg class="i" aria-hidden="true"><use href="#i-phone"/></svg>Call {{PHONE_DISPLAY}}</a>'
        )
    elif "**[Call Now]**" in s:
        parts.append(
            '<a class="btn btn--gold btn--lg" href="tel:{{PHONE_TEL}}"><svg class="i" aria-hidden="true"><use href="#i-phone"/></svg>Call Now</a>'
        )
    if "**[Get a Free Estimate]**" in s:
        parts.append(
            '<a class="btn btn--outline btn--lg" href="#estimate">Get a Free Estimate</a>'
        )
    elif "**[Book an Inspection]**" in s:
        parts.append(
            '<a class="btn btn--outline btn--lg" href="#estimate">Book an Inspection</a>'
        )
    return '      <div class="page-actions">\n        ' + "\n        ".join(parts) + "\n      </div>"


def is_ul(line: str) -> bool:
    return bool(re.match(r"^\*\s+", line))


def is_ol(line: str) -> bool:
    return bool(re.match(r"^\d+\.\s+", line))


def ul_item(line: str) -> str:
    return re.sub(r"^\*\s+", "", line)


def ol_item(line: str) -> str:
    return re.sub(r"^\d+\.\s+", "", line)


def linked_heading(line: str) -> re.Match | None:
    return re.fullmatch(r"\*\*\[([^\]]+)\]\(([^)]+)\)\*\*", line.strip())


def related_html(line: str) -> str:
    raw = line.strip()
    raw = re.sub(r"^\*\*(Related (?:services|pages):)\*\*\s*", r"<strong>\1</strong> ", raw)
    return f'      <p class="related">{inline(raw)}</p>'


def lines_to_html(lines: list[str], *, skip_buttons: bool = False) -> str:
    out: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        raw = line.strip()

        if raw in ("***", "* * *"):
            i += 1
            continue

        if is_button_line(raw):
            if not skip_buttons:
                out.append(button_html(raw))
            i += 1
            continue

        if raw.startswith("**Related services:**") or raw.startswith("**Related pages:**"):
            out.append(related_html(raw))
            i += 1
            continue

        if raw.startswith("## "):
            title = raw[3:].strip()
            if title.startswith("H1:"):
                i += 1
                continue
            out.append(f'      <h2>{inline(title)}</h2>')
            i += 1
            continue

        if raw.startswith("### "):
            out.append(f'      <h3>{inline(raw[4:].strip())}</h3>')
            i += 1
            continue

        if raw in ("**Form fields**",) or raw.startswith("**Button:**"):
            i += 1
            continue

        lh = linked_heading(raw)
        if lh:
            out.append(f'      <h3><a href="{slash_path(lh.group(2))}">{lh.group(1)}</a></h3>')
            i += 1
            continue

        if is_ul(raw):
            items = []
            while i < n and is_ul(lines[i].strip() if lines[i].strip() else ""):
                items.append(f"        <li>{inline(ul_item(lines[i].strip()))}</li>")
                i += 1
            out.append("      <ul>\n" + "\n".join(items) + "\n      </ul>")
            continue

        if is_ol(raw):
            items = []
            while i < n and is_ol(lines[i].strip() if lines[i].strip() else ""):
                items.append(f"        <li>{inline(ol_item(lines[i].strip()))}</li>")
                i += 1
            out.append("      <ol>\n" + "\n".join(items) + "\n      </ol>")
            continue

        if (
            out
            and out[-1].startswith("      <p>")
            and not out[-1].startswith("      <p class=")
            and raw[:1].islower()
        ):
            inner = out[-1][len("      <p>") : -len("</p>")]
            out[-1] = f"      <p>{inner} {inline(raw)}</p>"
        else:
            out.append(f"      <p>{inline(raw)}</p>")
        i += 1
    return "\n".join(out)


def parse_faq(section: str) -> tuple[str, list[tuple[str, str]]]:
    lines = [ln.rstrip() for ln in section.strip().split("\n")]
    heading = lines[0][3:].strip() if lines and lines[0].startswith("## ") else "Frequently Asked Questions"
    body_lines = lines[1:]
    faqs: list[tuple[str, str]] = []
    q = None
    ans: list[str] = []

    def flush() -> None:
        nonlocal q, ans
        if q:
            faqs.append((q, " ".join(a.strip() for a in ans if a.strip())))
        q, ans = None, []

    for ln in body_lines:
        s = ln.strip()
        if not s:
            continue
        m = re.fullmatch(r"\*\*(.+?)\*\*", s)
        if m and s.startswith("**") and s.endswith("**") and not s.startswith("**Related"):
            flush()
            q = m.group(1).strip()
            ans = []
        else:
            ans.append(s)
    flush()
    return heading, faqs


def faq_html(heading: str, faqs: list[tuple[str, str]]) -> str:
    parts = [
        f'      <h2 id="h-faq">{inline(heading)}</h2>',
        '      <div class="faq">',
    ]
    for q, a in faqs:
        parts.append("        <details>")
        parts.append(f"          <summary>{inline(q)}</summary>")
        parts.append(f"          <div class=\"ans\"><p>{inline(a)}</p></div>")
        parts.append("        </details>")
    parts.append("      </div>")
    return "\n".join(parts)


def faq_jsonld(slug: str, faqs: list[tuple[str, str]]) -> str:
    entities = []
    for q, a in faqs:
        entities.append(
            {
                "@type": "Question",
                "name": plain_text(q),
                "acceptedAnswer": {"@type": "Answer", "text": plain_text(a)},
            }
        )
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "@id": f"{{{{SITE_URL}}}}/{slug}/#faq",
        "mainEntity": entities,
    }
    dumped = json.dumps(data, indent=2, ensure_ascii=False)
    return f'<script type="application/ld+json">\n{dumped}\n</script>'


def parse_markdown(path: Path) -> dict:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    text = re.split(r"\n\*\*Build notes\*\*", text, maxsplit=1)[0]
    lines = text.split("\n")

    meta: dict[str, str] = {}
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        m = re.match(r"\*\*(URL|SEO Title|Meta Description):\*\*\s*(.*)$", s)
        if m:
            key, val = m.group(1), m.group(2).strip().strip("`")
            meta[key] = val
        if s.startswith("## H1:"):
            meta["H1"] = s.split("H1:", 1)[1].strip()
            i += 1
            break
        i += 1

    rest = "\n".join(lines[i:])
    rest = strip_notes(rest)

    chunks = re.split(r"\n\s*\*\*\*\s*\n", rest)
    chunks = [c.strip("\n") for c in chunks]
    intro = chunks[0].strip() if chunks else ""
    sections = [c.strip() for c in chunks[1:] if c.strip()]

    url = meta["URL"].strip()
    slug = url.strip("/")
    kind = slug  # contact, about, services, etc.

    return {
        "slug": slug,
        "url": url if url.endswith("/") or url == "/" else url,
        "title": apply_plain_tokens(meta["SEO Title"]).replace("[Phone]", "{{PHONE_DISPLAY}}"),
        "description": apply_plain_tokens(meta["Meta Description"]).replace("[Phone]", "{{PHONE_DISPLAY}}"),
        "h1": apply_plain_tokens(meta["H1"]).replace("[Phone]", "{{PHONE_DISPLAY}}"),
        "intro": intro,
        "sections": sections,
        "kind": kind,
        "path": path.name,
    }


NO_CTA = {"contact", "privacy-policy", "terms"}


def side_call_card(estimate_href: str) -> str:
    return f"""    <aside class="town-side">
      <div class="side-card side-card--call">
        <h2>Need pest control?</h2>
        <p>Call or request a free estimate. We will inspect the problem and explain the price before any work starts.</p>
        <a class="btn btn--gold" href="tel:{{{{PHONE_TEL}}}}"><svg class="i" aria-hidden="true"><use href="#i-phone"></use></svg>Call {{{{PHONE_DISPLAY}}}}</a>
        <a class="btn btn--outline" href="{estimate_href}">Get a free estimate</a>
      </div>
    </aside>"""


def render_page(page: dict, chrome: dict) -> str:
    slug = page["slug"]
    title = page["title"]
    desc = page["description"]
    h1 = page["h1"]
    kind = page["kind"]

    intro_lines = page["intro"].split("\n")
    intro_html = lines_to_html(intro_lines)

    body_parts: list[str] = []
    faqs: list[tuple[str, str]] = []
    faq_heading = "Frequently Asked Questions"
    cta_heading = None
    cta_copy = None
    related = None

    sections = page["sections"]
    cta_index = None
    if kind not in NO_CTA:
        for idx in range(len(sections) - 1, -1, -1):
            first = sections[idx].strip().split("\n", 1)[0]
            if first.startswith("## ") and "Frequently Asked Questions" not in first:
                cta_index = idx
                break

    for idx, sec in enumerate(sections):
        first = sec.strip().split("\n", 1)[0].strip()

        if first.startswith("## Frequently Asked Questions"):
            faq_heading, faqs = parse_faq(sec)
            body_parts.append(faq_html(faq_heading, faqs))
            continue

        if first.startswith("## Request Your Free Estimate"):
            body_parts.append(f"      <h2>{inline(first[3:].strip())}</h2>")
            body_parts.append(contact_form())
            continue

        if idx == cta_index:
            lines = sec.split("\n")
            heading = lines[0][3:].strip() if lines[0].startswith("## ") else heading_fallback(kind)
            copy_lines = []
            extra = []
            for ln in lines[1:]:
                s = ln.strip()
                if not s:
                    continue
                if is_button_line(s):
                    continue
                if s.startswith("**Related services:**") or s.startswith("**Related pages:**"):
                    extra.append(ln)
                    continue
                copy_lines.append(s)
            cta_heading = heading
            cta_copy = " ".join(copy_lines)
            if extra:
                related = lines_to_html(extra)
            continue

        body_parts.append(lines_to_html(sec.split("\n")))

    if related:
        body_parts.append(related)

    canonical = f"{{{{SITE_URL}}}}/{slug}/"
    faq_block = "\n" + faq_jsonld(slug, faqs) + "\n" if faqs else "\n"

    cta_html = ""
    if cta_heading:
        cta_html = f"""
<section class="cta" aria-labelledby="h-cta">
  <div class="page-col">
    <h2 id="h-cta">{inline(cta_heading)}</h2>
    <p>{inline(cta_copy)}</p>
{estimate_form(f"/{slug}/")}
  </div>
</section>
"""

    estimate_href = "#estimate" if cta_heading or kind == "contact" else "/contact/#estimate"
    sidebar_html = side_call_card(estimate_href)
    body_content = chr(10).join(body_parts)
    if kind in {"privacy-policy", "terms"}:
        body_html = f"""<div class="page-body">
  <div class="page-col legal-copy">
{body_content}
  </div>
</div>"""
    else:
        body_html = f"""<div class="page-body">
  <div class="wrap town-layout">
    <div class="town-main">
{body_content}
    </div>
{sidebar_html}
  </div>
</div>"""

    header = chrome["header"].replace('href="#areas"', 'href="/#areas"')
    callbar = chrome["callbar"]
    if kind in {"privacy-policy", "terms"}:
        callbar = callbar.replace('href="#estimate"', 'href="/contact/"')

    return f"""<!DOCTYPE html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#10253a">

<meta property="og:type" content="website">
<meta property="og:locale" content="en_US">
<meta property="og:site_name" content="{{{{BUSINESS_NAME}}}}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{{{{OG_IMAGE_URL}}}}">
<meta name="twitter:card" content="summary_large_image">

<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%2310253a'/%3E%3Ccircle cx='16' cy='17' r='6' fill='%23f0b429'/%3E%3C/svg%3E">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Bricolage+Grotesque:opsz,wght@12..96,600..800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
{faq_block}</head>

<body>
{chrome["skip"]}
{chrome["sprite"]}
{header}

<main id="main">

<section class="page-title" aria-labelledby="h1">
  <div class="page-col">
    <h1 id="h1">{inline(h1)}</h1>
{intro_html}
  </div>
</section>

{body_html}
{cta_html}
</main>

{chrome["footer"]}

{callbar}

{chrome["script"]}
</body>
</html>
"""


def heading_fallback(kind: str) -> str:
    return "Get a free estimate"


def extract_chrome(index_html: str) -> dict:
    skip = re.search(r'<a class="skip".*?</a>', index_html, re.S).group(0)
    sprite = re.search(
        r'<!-- icon sprite -->\s*(<svg width="0".*?</svg>)', index_html, re.S
    ).group(1)
    header = re.search(r"<header class=\"site-header\">.*?</header>", index_html, re.S).group(0)
    footer = re.search(r"<footer class=\"site-footer\">.*?</footer>", index_html, re.S).group(0)
    callbar = re.search(r'<div class="callbar">.*?</div>', index_html, re.S).group(0)
    script = """<script>
(function () {
  // mobile menu
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // footer year
  var yr = document.getElementById('yr');
  if (yr) { yr.textContent = new Date().getFullYear(); }
})();
</script>"""
    return {
        "skip": skip,
        "sprite": sprite,
        "header": header,
        "footer": footer,
        "callbar": callbar,
        "script": script,
    }


def extract_and_write_css(index_html: str) -> str:
    m = re.search(r"<style>(.*?)</style>", index_html, re.S)
    if not m:
        raise SystemExit("No <style> block in index.html")
    css = m.group(1)
    if css.startswith("\n"):
        css_out = css[1:]
    else:
        css_out = css
    if not css_out.endswith("\n"):
        css_out += "\n"
    css_out = css_out + INNER_CSS
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    (assets / "style.css").write_text(css_out, encoding="utf-8", newline="\n")
    return css_out


def update_index(index_html: str) -> str:
    html = re.sub(r"<style>.*?</style>", '<link rel="stylesheet" href="/assets/style.css">', index_html, count=1, flags=re.S)
    html = add_trailing_slashes(html)
    return html


def build_all_pages(index_html: str) -> list[str]:
    chrome = extract_chrome(index_html)
    slugs: list[str] = []
    for path in md_files():
        page = parse_markdown(path)
        html = render_page(page, chrome)
        out_dir = ROOT / page["slug"]
        out_dir.mkdir(exist_ok=True)
        (out_dir / "index.html").write_text(html, encoding="utf-8", newline="\n")
        slugs.append(page["slug"])
        print("wrote", page["slug"] + "/index.html")
    return slugs


def write_sitemap(slugs: list[str]) -> None:
    urls = ["{{SITE_URL}}/"]
    urls.extend(f"{{{{SITE_URL}}}}/{slug}/" for slug in slugs)
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for loc in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        lines.append("  </url>")
    lines.append("</urlset>")
    lines.append("")
    (ROOT / "sitemap.xml").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"wrote sitemap.xml ({len(urls)} URLs)")


def write_robots() -> None:
    text = "User-agent: *\nAllow: /\n\nSitemap: {{SITE_URL}}/sitemap.xml\n"
    (ROOT / "robots.txt").write_text(text, encoding="utf-8", newline="\n")
    print("wrote robots.txt")


def main() -> None:
    index_path = ROOT / "index.html"
    original = index_path.read_text(encoding="utf-8")
    if "<style>" in original:
        extract_and_write_css(original)
        updated = update_index(original)
        index_path.write_text(updated, encoding="utf-8", newline="\n")
        print("updated index.html and assets/style.css")
        index_html = updated
    else:
        print("index.html already uses shared CSS")
        index_html = original
    slugs = build_all_pages(index_html)
    write_sitemap(slugs)
    write_robots()


if __name__ == "__main__":
    main()
