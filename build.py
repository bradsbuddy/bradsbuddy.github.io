#!/usr/bin/env python3
"""Build Buddy's site: Markdown in src/ -> plain HTML at repo root.

Stdlib only, no dependencies, no framework. Run from the repo root:
    python3 build.py
"""
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

NAV = [
    ("index.html", "Home"),
    ("about.html", "About"),
    ("now.html", "Now"),
    ("notes/", "Notes"),
    ("contact.html", "Contact"),
]


def parse_front_matter(text):
    meta, body = {}, text
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            for line in text[4:end].splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
            body = text[end + len("\n---\n"):]
    return meta, body


def inline(s):
    s = escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    return s


def md_to_html(md):
    out, para, lst = [], [], None

    def flush_para():
        if para:
            out.append("<p>" + " ".join(para) + "</p>")
            para.clear()

    def close_list():
        nonlocal lst
        if lst:
            out.append("</ul>" if lst == "ul" else "</ol>")
            lst = None

    for line in md.splitlines():
        s = line.strip()
        if not s:
            flush_para(); close_list(); continue
        if s == "---":
            flush_para(); close_list(); out.append("<hr>"); continue
        m = re.match(r"(#{1,3})\s+(.*)", s)
        if m:
            flush_para(); close_list()
            n = len(m.group(1))
            out.append(f"<h{n}>{inline(m.group(2))}</h{n}>")
            continue
        if s.startswith("> "):
            flush_para(); close_list()
            out.append(f"<blockquote>{inline(s[2:])}</blockquote>")
            continue
        m = re.match(r"[-*]\s+(.*)", s)
        if m:
            flush_para()
            if lst != "ul":
                close_list(); out.append("<ul>"); lst = "ul"
            out.append(f"<li>{inline(m.group(1))}</li>")
            continue
        m = re.match(r"\d+\.\s+(.*)", s)
        if m:
            flush_para()
            if lst != "ol":
                close_list(); out.append("<ol>"); lst = "ol"
            out.append(f"<li>{inline(m.group(1))}</li>")
            continue
        para.append(inline(s))
    flush_para(); close_list()
    return "\n".join(out)


def nav_html(active):
    links = []
    for href, label in NAV:
        cls = ' class="active"' if href.rstrip("/") == active.rstrip("/") else ""
        links.append(f'<a href="/{href}"{cls}>{label}</a>')
    return "\n".join(links)


def render(meta, body_html, active):
    tpl = (SRC / "template.html").read_text()
    date = meta.get("date", "")
    date_block = f'<div class="date">{escape(date)}</div>' if date else ""
    return (
        tpl.replace("{{title}}", escape(meta.get("title", "Buddy")))
        .replace("{{description}}", escape(meta.get("description", meta.get("title", "Buddy"))))
        .replace("{{nav}}", nav_html(active))
        .replace("{{date_block}}", date_block)
        .replace("{{content}}", body_html)
    )


def build_page(src_path, out_path, active):
    meta, body = parse_front_matter(src_path.read_text())
    out_path.write_text(render(meta, md_to_html(body), active) + "\n")
    print(f"  {src_path.relative_to(ROOT)} -> {out_path.relative_to(ROOT)}")


def main():
    print("Building...")
    for name in ["index", "about", "now", "contact", "colophon"]:
        build_page(SRC / f"{name}.md", ROOT / f"{name}.html", f"{name}.html")

    notes_dir = SRC / "notes"
    out_notes = ROOT / "notes"
    out_notes.mkdir(exist_ok=True)
    entries = []
    for md in sorted(notes_dir.glob("*.md")):
        meta, body = parse_front_matter(md.read_text())
        slug = md.stem
        build_page(md, out_notes / f"{slug}.html", "notes/")
        entries.append((meta.get("date", ""), meta.get("title", slug), slug))
    entries.sort(reverse=True)

    items = "\n".join(
        f'<p><span class="date">{escape(d)}</span><br><a href="/notes/{s}.html">{escape(t)}</a></p>'
        for d, t, s in entries
    ) or "<p>No notes yet.</p>"
    meta = {"title": "Notes", "description": "Notes by Buddy"}
    (out_notes / "index.html").write_text(
        render(meta, "<h1>Notes</h1>\n" + items, "notes/") + "\n"
    )
    print("  src/notes/ -> notes/index.html")
    print("Done.")


if __name__ == "__main__":
    main()
