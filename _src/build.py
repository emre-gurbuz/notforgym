#!/usr/bin/env python3
"""NotForGym sitesini üretir.

Kaynak:  _src/templates/*.html   (sayfa şablonları, {{anahtar}} yer tutucuları)
         _src/lang/<dil>.json     (her dilin metinleri)
         _src/legal/<sayfa>.<dil>.html (gizlilik ve koşullar metni)
Çıktı:   İngilizce kökte (index.html, privacy.html ...), diğer diller kendi klasöründe (tr/, de/ ...).

Çalıştır:  python3 _src/build.py
"""
import html
import json
import re
from pathlib import Path

SRC = Path(__file__).resolve().parent
OUT = SRC.parent

# (klasör kodu, html lang, menüde görünen ad, çıktı klasörü)
LANGS = [
    ("en", "en", "English", ""),
    ("tr", "tr", "Türkçe", "tr/"),
    ("de", "de", "Deutsch", "de/"),
    ("es", "es", "Español", "es/"),
    ("pt-br", "pt-BR", "Português (BR)", "pt-br/"),
    ("fr", "fr", "Français", "fr/"),
    ("it", "it", "Italiano", "it/"),
    ("ja", "ja", "日本語", "ja/"),
]
# Sitenin yayınlandığı yol. GitHub Pages proje sitesi: /notforgym/ — kendi alan adına geçince "/" yap.
SITE_BASE = "/notforgym/"

PAGES = ["index", "privacy", "support", "terms", "404"]
SHOTS = ["train", "workout", "progress", "profile", "exercise", "history"]


def esc(s):
    return html.escape(s, quote=True)


def features(t):
    return "\n".join(
        f'        <div class="card"><div class="ico">{icon}</div>\n'
        f"          <h3>{title}</h3>\n          <p>{desc}</p></div>"
        for icon, title, desc in t["features"]
    )


def gallery(t, code, root):
    return "\n".join(
        f'      <figure><div class="phone"><img src="{root}assets/shots/{code}-{shot}.jpg" alt="{esc(cap)}" loading="lazy"></div>\n'
        f"        <figcaption>{cap}</figcaption></figure>"
        for shot, cap in zip(SHOTS, t["captions"])
    )


def checks(items):
    return "\n".join(f"          <li>{i}</li>" for i in items)


def faq(t):
    return "\n".join(
        f"    <details><summary>{q}</summary>\n      <p>{a}</p></details>" for q, a in t["faq"]
    )


def rel(root, folder, page_file):
    """Sayfadan diğer dildeki karşılığına göreli bağlantı (site alt klasörde de çalışsın diye)."""
    return root + folder + (page_file or "index.html")


def lang_menu(code, root, page_file):
    opts = []
    for c, _, name, folder in LANGS:
        sel = " selected" if c == code else ""
        opts.append(f'<option value="{c}" data-href="{rel(root, folder, page_file)}"{sel}>{name}</option>')
    return '<select class="lang-select" aria-label="Language">' + "".join(opts) + "</select>"


def alternates(root, page_file):
    lines = []
    for c, hl, _, folder in LANGS:
        lines.append(f'  <link rel="alternate" hreflang="{hl}" href="{rel(root, folder, page_file)}">')
    lines.append(f'  <link rel="alternate" hreflang="x-default" href="{rel(root, "", page_file)}">')
    return "\n".join(lines)


def render(template, values):
    def sub(m):
        key = m.group(1)
        if key not in values:
            raise KeyError(f"Eksik anahtar: {key}")
        return values[key]
    return re.sub(r"\{\{([a-zA-Z0-9_]+)\}\}", sub, template)


def main():
    templates = {p: (SRC / "templates" / f"{p}.html").read_text() for p in PAGES}
    header = (SRC / "templates" / "_header.html").read_text()
    footer = (SRC / "templates" / "_footer.html").read_text()
    base = json.loads((SRC / "lang" / "en.json").read_text())
    for code, hl, _, folder in LANGS:
        t = json.loads((SRC / "lang" / f"{code}.json").read_text())
        missing = set(base) - set(t)
        if missing:
            raise SystemExit(f"{code}.json eksik anahtarlar: {sorted(missing)}")
        out_dir = OUT / folder
        out_dir.mkdir(exist_ok=True)
        for page in PAGES:
            if page == "404" and folder:
                continue  # 404 sadece kökte gerekli; her yerden açılabildiği için mutlak yollar kullanır.
            root = SITE_BASE if page == "404" else ("../" if folder else "")
            page_file = "index.html" if page == "index" else f"{page}.html"
            values = {k: v for k, v in t.items() if isinstance(v, str)}
            values.update(
                lang=hl,
                code=code,
                root=root,
                langmenu=lang_menu(code, root, "" if page in ("index", "404") else page_file),
                alternates=alternates(root, "" if page in ("index", "404") else page_file),
                features=features(t),
                gallery=gallery(t, code, root),
                pricing_list=checks(t["pricing_checks"]),
                privacy_list=checks(t["privacy_checks"]),
                faq=faq(t),
                privacy_body=(SRC / "legal" / f"privacy.{code}.html").read_text(),
                terms_body=(SRC / "legal" / f"terms.{code}.html").read_text(),
                base="",
                home="index.html",
                cur_index=' aria-current="page"' if page == "index" else "",
                cur_support=' aria-current="page"' if page == "support" else "",
                cur_privacy=' aria-current="page"' if page == "privacy" else "",
            )
            if page == "404":
                values.update(base=SITE_BASE, home=SITE_BASE)
            values["header"] = render(header, values)
            values["footer"] = render(footer, values)
            (out_dir / page_file).write_text(render(templates[page], values))
    print("Tamam:", ", ".join(c for c, *_ in LANGS))


if __name__ == "__main__":
    main()
