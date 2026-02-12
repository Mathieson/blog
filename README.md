# Mat's Mind Dump

A static blog built with [Hugo](https://gohugo.io/) and the [PaperMod](https://github.com/adityatelange/hugo-PaperMod) theme. Comments are powered by [Giscus](https://giscus.app/) (GitHub Discussions). Originally migrated from WordPress via `migrate.py`.

---

## Prerequisites

| Tool                                               | Version  | Install                      |
| -------------------------------------------------- | -------- | ---------------------------- |
| [Hugo (extended)](https://gohugo.io/installation/) | ≥ 0.120  | `brew install hugo` (macOS)  |
| [Git](https://git-scm.com/)                        | any      | Required for theme submodule |

After cloning, initialise the PaperMod theme submodule:

```bash
git submodule update --init --recursive
```

---

## Local preview

```bash
./preview.sh
# or: hugo server -D --source site
```

Open <http://localhost:1313>. The `-D` flag includes draft posts.

**Draft posts** have `draft = true` in their frontmatter. They are visible locally with `-D` but excluded from production builds. To publish a draft, change `draft = true` → `draft = false`.

---

## Before going live

Edit `site/hugo.toml` and update every line marked `# TODO`:

| Setting         | Location                  | Example                               |
| --------------- | ------------------------- | ------------------------------------- |
| `baseURL`       | top of file               | `"https://mathieson.github.io/blog/"` |
| `params.author` | `[params]` section        | `"Mat"`                               |
| Giscus values   | `[params.giscus]` section | see Giscus setup below                |

### Giscus comments setup

1. Push the blog to a **public** GitHub repository.
2. Enable Discussions: repo **Settings → Features → Discussions**.
3. Install the [Giscus GitHub App](https://github.com/apps/giscus) and grant it access to your repo.
4. Visit <https://giscus.app>, enter your repo name, and copy the generated values.
5. Paste `repo`, `repoId`, `category`, and `categoryId` into the `[params.giscus]` block in `site/hugo.toml`.

### Seed comments from WordPress (optional)

Once Giscus is configured, run `migrate_comments.py` to import the original WordPress comments as GitHub Discussion replies:

```bash
uv run --with requests migrate_comments.py \
  --repo mathieson/blog \
  --category Announcements \
  --token <your-github-pat>
```

A GitHub personal access token with `repo` and `discussions:write` scopes is required. Create one at <https://github.com/settings/tokens>.

---

## Deploy to GitHub Pages

Deployment is fully automated via **GitHub Actions** (`.github/workflows/deploy.yml`). Every push to `main` triggers a build-and-deploy pipeline:

1. Checks out the repo (including the PaperMod submodule)
2. Installs Hugo extended
3. Runs `hugo --source site`
4. Publishes the output to GitHub Pages

### One-time GitHub setup

Before the workflow can deploy, configure Pages in your repo:

1. Go to repo **Settings → Pages**
2. Under *Build and deployment → Source*, select **GitHub Actions**

After that, every push to `main` will deploy automatically. The live URL appears in the Actions run log and on the Pages settings page.
