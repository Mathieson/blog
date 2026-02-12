#!/usr/bin/env python3
"""
Migrate exported WordPress markdown posts to Hugo.

Source:      export/posts/<year>/<month>/<slug>/index.md
Destination: site/content/posts/<slug>/index.md
Images:      site/content/posts/<slug>/images/  (Hugo page bundle)

Skips _drafts directories and pages.
Idempotent: skips files that already exist with matching content.
"""

import re
import shutil
import sys
from pathlib import Path

import yaml

EXPORT_DIR = Path("export/posts")
HUGO_POSTS_DIR = Path("site/content/posts")


def yaml_to_toml(data: dict, slug: str) -> str:
    lines = []
    for key, value in data.items():
        if key == "date":
            # date object from PyYAML → RFC 3339 string, no quotes in TOML
            lines.append(f"date = {value}T00:00:00Z")
        elif key == "draft":
            lines.append(f"draft = {str(value).lower()}")
        elif key == "coverImage":
            lines.append(f'[cover]\n  image = "images/{value}"')
        elif isinstance(value, list):
            items = ", ".join(f'"{v}"' for v in value)
            lines.append(f"{key} = [{items}]")
        else:
            escaped = str(value).replace('"', '\\"')
            lines.append(f'{key} = "{escaped}"')
    return "\n".join(lines)


def rewrite_image_refs(body: str, slug: str) -> str:
    """Keep relative image refs as-is — they're already images/<file> which Hugo resolves in page bundles."""
    return body


def migrate_post(post_dir: Path, slug: str) -> bool:
    src_index = post_dir / "index.md"
    src_images_dir = post_dir / "images"

    dst_post_dir = HUGO_POSTS_DIR / slug
    dst_index = dst_post_dir / "index.md"
    dst_images_dir = dst_post_dir / "images"

    raw = src_index.read_text(encoding="utf-8")

    # Parse YAML frontmatter (between --- delimiters)
    if not raw.startswith("---"):
        print(f"  WARNING: no YAML frontmatter in {src_index}, skipping")
        return False

    end = raw.find("\n---", 3)
    if end == -1:
        print(f"  WARNING: unclosed frontmatter in {src_index}, skipping")
        return False

    yaml_text = raw[3:end]
    body = raw[end + 4:]

    try:
        fm = yaml.safe_load(yaml_text) or {}
    except yaml.YAMLError as e:
        print(f"  WARNING: YAML parse error in {src_index}: {e}, skipping")
        return False

    toml_text = yaml_to_toml(fm, slug)
    body = rewrite_image_refs(body, slug)
    new_content = f"+++\n{toml_text}\n+++\n{body}"

    # Idempotency: skip if destination exists with identical content
    dst_post_dir.mkdir(parents=True, exist_ok=True)
    if dst_index.exists() and dst_index.read_text(encoding="utf-8") == new_content:
        return True  # already up to date, count as success

    dst_index.write_text(new_content, encoding="utf-8")

    # Copy images
    if src_images_dir.exists():
        dst_images_dir.mkdir(parents=True, exist_ok=True)
        for img in src_images_dir.iterdir():
            dst_img = dst_images_dir / img.name
            if not dst_img.exists():
                shutil.copy2(img, dst_img)

    return True


def main():
    if not EXPORT_DIR.exists():
        print("ERROR: export/posts/ not found. Run the WordPress export first.")
        sys.exit(1)

    HUGO_POSTS_DIR.mkdir(parents=True, exist_ok=True)

    slugs_seen: dict[str, int] = {}
    warnings: list[str] = []
    migrated = 0

    for year_dir in sorted(EXPORT_DIR.iterdir()):
        if year_dir.name == "_drafts" or not year_dir.is_dir():
            continue
        for month_dir in sorted(year_dir.iterdir()):
            if not month_dir.is_dir():
                continue
            for post_dir in sorted(month_dir.iterdir()):
                if not post_dir.is_dir():
                    continue

                slug = post_dir.name

                # Slug collision detection
                if slug in slugs_seen:
                    new_slug = f"{slug}-{slugs_seen[slug]}"
                    warnings.append(f"Slug collision: '{slug}' → renamed to '{new_slug}'")
                    slugs_seen[slug] += 1
                    slug = new_slug
                else:
                    slugs_seen[slug] = 1

                if migrate_post(post_dir, slug):
                    print(f"  ✓ {slug}")
                    migrated += 1

    print(f"\nMigrated {migrated} posts to site/content/posts/")

    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  ⚠ {w}")


if __name__ == "__main__":
    main()
