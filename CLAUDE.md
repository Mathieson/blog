# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Local preview

```bash
./preview.sh
# equivalent to: hugo server -D --source site
```

Opens at http://localhost:1313. The `-D` flag includes draft posts.

## Creating a new post

```bash
hugo new posts/<slug> --source site
```

This creates `site/content/posts/<slug>/index.md` from `site/archetypes/posts/index.md`, pre-filled with TOML frontmatter (`+++`-delimited): title, date, `draft = true`, empty `tags`, and empty `description`. Always fill in `description` (one sentence — it feeds search-engine and social-share previews). Post images live in the post's own directory (e.g. `images/`) and are referenced relatively.

Set `draft = false` (or remove the field) to publish. Draft posts are excluded from production builds but visible locally via `./preview.sh`.

### Cover images

Covers are logos on a transparent 1200x1000 canvas. They render `contain`-fit into a fixed box in the post list, so the *artwork inside the canvas* — not the canvas — decides how big a logo looks. After adding a cover, normalise its optical weight so it doesn't out-shout its neighbours:

```bash
python3 scripts/normalize-cover.py --all          # or --check to preview
```

The script only touches covers named in post frontmatter. Leave body screenshots and diagrams alone — they're sized by their content.

## Design tokens

The site's colors are OKLCH tokens in `site/assets/css/extended/custom.css` (warm cream light / deep navy dark, steel-blue accent). Three places must stay visually in sync with those tokens:
- `site/assets/css/extended/chroma-theme.css` — code-block backgrounds use `var(--code-block-bg)` etc.
- `site/static/giscus-light.css` / `giscus-dark.css` — Giscus comment themes with token values hard-coded as hex (Giscus loads these from the live site URL, so changes only take effect after deploy).

## Architecture

- `site/` — the Hugo project root; all Hugo commands use `--source site`
- `site/hugo.toml` — site config, theme settings, Giscus comment config, menus
- `site/content/posts/` — all blog posts as `<slug>/index.md`
- `site/layouts/` — template overrides on top of PaperMod
- `site/assets/` — images and CSS referenced by layouts
- `site/static/` — files served as-is (favicons etc.)
- Theme: PaperMod, loaded as a git submodule at `site/themes/PaperMod/`

## Deployment

Pushing to `main` triggers GitHub Actions (`.github/workflows/deploy.yml`), which runs `hugo --source site` and pushes the built site to the `gh-pages` branch, which GitHub Pages serves at https://matfacer.com/.

The custom domain is set by `site/static/CNAME` (Hugo copies it into `site/public/`, so it survives every deploy). Don't rely on setting the domain in Settings → Pages alone — `peaceiris/actions-gh-pages` replaces the branch contents on each run.
