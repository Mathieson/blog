# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Local preview

```bash
./preview.sh
# equivalent to: hugo server -D --source site
```

Opens at http://localhost:1313. The `-D` flag includes draft posts.

## Creating a new post

Posts live under `site/content/posts/`. Each post is a directory containing a single `index.md` file:

```
site/content/posts/<slug>/index.md
```

Frontmatter uses TOML (delimited by `+++`):

```toml
+++
title = "Post Title"
date = 2026-04-02
draft = true
tags = ["tag1", "tag2"]
+++
```

Set `draft = false` (or remove the field) to publish. Draft posts are excluded from production builds but visible locally via `./preview.sh`.

## Architecture

- `site/` — the Hugo project root; all Hugo commands use `--source site`
- `site/hugo.toml` — site config, theme settings, Giscus comment config, menus
- `site/content/posts/` — all blog posts as `<slug>/index.md`
- `site/layouts/` — template overrides on top of PaperMod
- `site/assets/` — images and CSS referenced by layouts
- `site/static/` — files served as-is (favicons etc.)
- Theme: PaperMod, loaded as a git submodule at `site/themes/PaperMod/`

## Deployment

Pushing to `main` triggers GitHub Actions (`.github/workflows/deploy.yml`), which runs `hugo --source site` and publishes to GitHub Pages at https://mathieson.github.io/blog/.
