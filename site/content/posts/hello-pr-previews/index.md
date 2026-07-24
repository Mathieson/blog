+++
title = 'Hello PR Previews'
date = 2026-07-24
draft = true
tags = ["meta", "devops"]
description = "Testing out our shiny new PR preview environments — every pull request now gets its own live URL."
+++

This is a draft post that only exists on a feature branch. If you're reading this on the preview URL, the PR preview system is working!

## What just happened?

When this branch was pushed and a pull request opened, GitHub Actions automatically:

1. Built this Hugo site with a branch-specific base URL
2. Deployed it to a subdirectory on the `gh-pages` branch
3. Posted a comment on the PR with a link to this exact page

The main site at `https://mathieson.github.io/blog/` has no idea this post exists — it's draft-only, on a branch, and hasn't been merged.

## Pretty neat

This is the same idea as GitLab Review Apps, just wired up with GitHub Actions and a couple of community actions (`peaceiris/actions-gh-pages` and `rossjrw/pr-preview-action`).
