#!/usr/bin/env python3
"""
Migrate WordPress comments to Giscus (GitHub Discussions).

Run this AFTER the blog is deployed and Giscus is fully configured.

Prerequisites
─────────────
1. Blog is live on GitHub Pages.
2. GitHub Discussions is enabled on your repo.
3. Giscus GitHub App is installed on your repo.
4. [params.giscus] in site/hugo.toml is fully filled in.
5. A GitHub personal access token with 'repo' and
   'write:discussion' scopes.
   Create one at: https://github.com/settings/tokens

How to get your WordPress XML
──────────────────────────────
Log in to your WordPress admin dashboard and go to:
  Tools → Export → All content → Download Export File

Usage
─────
    uv run --with requests migrate_comments.py \\
        --xml mat039sminddump.WordPress.2026-02-11.xml \\
        --repo mathieson/blog \\
        --category General \\
        --token ghp_xxxxxxxxxxxxxxxxxxxx

Arguments
─────────
    --xml       Path to your WordPress XML export file
    --repo      GitHub repo in owner/name format (e.g. mathieson/blog)
    --category  GitHub Discussions category name to create discussions in
                (must already exist in your repo's Discussions settings)
    --token     GitHub personal access token
    --dry-run   Print what would be created without hitting the API
"""

import argparse
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime

try:
    import requests
except ImportError:
    print("ERROR: 'requests' is required. Run with: uv run --with requests migrate_comments.py")
    sys.exit(1)


# ── WordPress XML namespaces ──────────────────────────────────────────────────

NS = {
    "wp":      "http://wordpress.org/export/1.2/",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc":      "http://purl.org/dc/elements/1.1/",
}


# ── Data classes ─────────────────────────────────────────────────────────────

@dataclass
class WPComment:
    id: str
    parent_id: str
    author: str
    date: str
    content: str
    approved: bool


@dataclass
class WPPost:
    title: str
    slug: str
    comments: list[WPComment] = field(default_factory=list)


# ── WordPress XML parsing ─────────────────────────────────────────────────────

def parse_wordpress_xml(xml_path: str) -> list[WPPost]:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    posts = []
    for item in root.iter("item"):
        post_type = item.find("wp:post_type", NS)
        if post_type is None or post_type.text != "post":
            continue

        status = item.find("wp:status", NS)
        if status is None or status.text != "publish":
            continue

        title_el = item.find("title")
        slug_el  = item.find("wp:post_name", NS)
        title = title_el.text if title_el is not None else "(no title)"
        slug  = slug_el.text  if slug_el  is not None else ""

        comments = []
        for c in item.findall("wp:comment", NS):
            approved_el = c.find("wp:comment_approved", NS)
            if approved_el is None or approved_el.text not in ("1", "approve"):
                continue  # skip unapproved / spam

            comments.append(WPComment(
                id        = (c.find("wp:comment_id",     NS) or _empty()).text or "",
                parent_id = (c.find("wp:comment_parent", NS) or _empty()).text or "0",
                author    = (c.find("wp:comment_author", NS) or _empty()).text or "Anonymous",
                date      = (c.find("wp:comment_date",   NS) or _empty()).text or "",
                content   = (c.find("wp:comment_content",NS) or _empty()).text or "",
                approved  = True,
            ))

        if comments:
            posts.append(WPPost(title=title, slug=slug, comments=comments))

    return posts


class _empty:
    text = None


# ── GitHub GraphQL helpers ────────────────────────────────────────────────────

GRAPHQL_URL = "https://api.github.com/graphql"


def graphql(token: str, query: str, variables: dict) -> dict:
    headers = {"Authorization": f"bearer {token}", "Content-Type": "application/json"}
    resp = requests.post(GRAPHQL_URL, json={"query": query, "variables": variables},
                         headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data:
        raise RuntimeError(f"GraphQL error: {data['errors']}")
    return data["data"]


def get_repo_and_category(token: str, owner: str, name: str, category_name: str) -> tuple[str, str]:
    query = """
    query($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) {
        id
        discussionCategories(first: 25) {
          nodes { id name }
        }
      }
    }
    """
    data = graphql(token, query, {"owner": owner, "name": name})
    repo_id    = data["repository"]["id"]
    categories = data["repository"]["discussionCategories"]["nodes"]
    matches    = [c for c in categories if c["name"].lower() == category_name.lower()]
    if not matches:
        names = [c["name"] for c in categories]
        raise ValueError(
            f"Category '{category_name}' not found. Available: {names}"
        )
    return repo_id, matches[0]["id"]


def create_discussion(token: str, repo_id: str, category_id: str,
                      title: str, body: str) -> str:
    mutation = """
    mutation($repoId: ID!, $categoryId: ID!, $title: String!, $body: String!) {
      createDiscussion(input: {
        repositoryId: $repoId,
        categoryId:   $categoryId,
        title:        $title,
        body:         $body
      }) {
        discussion { id url }
      }
    }
    """
    data = graphql(token, mutation, {
        "repoId": repo_id, "categoryId": category_id,
        "title": title, "body": body,
    })
    discussion = data["createDiscussion"]["discussion"]
    print(f"  Created discussion: {discussion['url']}")
    return discussion["id"]


def add_comment(token: str, discussion_id: str, body: str) -> str:
    mutation = """
    mutation($discussionId: ID!, $body: String!) {
      addDiscussionComment(input: {
        discussionId: $discussionId,
        body:         $body
      }) {
        comment { id }
      }
    }
    """
    data = graphql(token, mutation, {"discussionId": discussion_id, "body": body})
    return data["addDiscussionComment"]["comment"]["id"]


# ── Comment formatting ────────────────────────────────────────────────────────

def format_comment(comment: WPComment) -> str:
    """Format a WordPress comment as a Markdown block for GitHub Discussions."""
    date_str = ""
    try:
        dt = datetime.strptime(comment.date, "%Y-%m-%d %H:%M:%S")
        date_str = dt.strftime("%B %-d, %Y")
    except ValueError:
        date_str = comment.date

    return (
        f"**{comment.author}** · *{date_str}*\n\n"
        f"{comment.content.strip()}\n\n"
        f"---\n"
        f"*Migrated from WordPress comments*"
    )


def discussion_title_for_post(slug: str) -> str:
    """
    Giscus maps pages to discussions by pathname (default mapping).
    The pathname Hugo generates for posts is /posts/<slug>/
    """
    return f"/posts/{slug}/"


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Migrate WordPress comments to Giscus.")
    parser.add_argument("--xml",      required=True,  help="Path to WordPress XML export")
    parser.add_argument("--repo",     required=True,  help="GitHub repo (owner/name)")
    parser.add_argument("--category", required=True,  help="GitHub Discussions category name")
    parser.add_argument("--token",    required=True,  help="GitHub personal access token")
    parser.add_argument("--dry-run",  action="store_true",
                        help="Print actions without calling the API")
    args = parser.parse_args()

    owner, name = args.repo.split("/", 1)

    print(f"Parsing {args.xml}…")
    posts = parse_wordpress_xml(args.xml)

    if not posts:
        print("No published posts with approved comments found in the XML.")
        return

    print(f"Found {sum(len(p.comments) for p in posts)} comments across {len(posts)} post(s).\n")

    if args.dry_run:
        for post in posts:
            print(f"[DRY RUN] Would create discussion: {discussion_title_for_post(post.slug)}")
            for c in post.comments:
                print(f"  → Comment by {c.author} ({c.date})")
        return

    print(f"Fetching repo metadata for {args.repo}…")
    repo_id, category_id = get_repo_and_category(args.token, owner, name, args.category)

    total_comments = 0
    for post in posts:
        print(f"\nPost: {post.title}")
        title = discussion_title_for_post(post.slug)
        body  = (
            f"Comments migrated from the original WordPress post: "
            f"**{post.title}**\n\n"
            f"*(This discussion was created automatically to preserve comments "
            f"from the WordPress migration.)*"
        )
        discussion_id = create_discussion(args.token, repo_id, category_id, title, body)

        for comment in post.comments:
            formatted = format_comment(comment)
            comment_id = add_comment(args.token, discussion_id, formatted)
            print(f"  ✓ Comment by {comment.author}")
            total_comments += 1

    print(f"\nDone. Migrated {total_comments} comment(s).")


if __name__ == "__main__":
    main()
