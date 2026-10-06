# buddy.github.io source

Buddy's personal site. Markdown in `src/` becomes plain HTML at the repo root.

## Layout

- `src/index.md`, `src/about.md`, `src/now.md`, `src/contact.md`, `src/colophon.md` → same-named `.html` at root
- `src/notes/*.md` → `notes/<slug>.html`, plus an auto-generated `notes/index.html`
- `src/template.html` — the single shared template (`{{title}}`, `{{description}}`, `{{nav}}`, `{{date_block}}`, `{{content}}`)

## Building

    python3 build.py

Stdlib only. Commit the generated HTML too — GitHub Pages serves the repo root.

## Rules

- No JavaScript, no cookies, no analytics. Ever.
- Keep it boring: if a change needs a framework, the change is wrong.
