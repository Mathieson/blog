#!/usr/bin/env python3
"""Normalise the optical size of post cover logos.

Every cover shares a 1200x1000 canvas, but the artwork inside them arrives at
whatever size the source logo happened to be — VS Code's mark filled 48% of its
canvas while PyTorch's filled 25%, so in the post list one looked twice the
weight of the other. This rescales the artwork so each logo carries a
comparable amount of visual weight, leaving the canvas untouched.

Sizing is by the geometric mean of the ink bounding box, not by width or
height alone: that treats a square icon, a tall stack and a wide wordmark
fairly, where fitting everything to a common height would blow the wordmark up.
Two caps stop extreme aspect ratios from running away.

Ink is measured at alpha >= 128 so soft drop shadows don't inflate the box, but
the full artwork (shadows included) is what gets scaled and recentred.

Idempotent — re-running on an already-normalised file is a no-op.

This is for cover art only. Screenshots and diagrams inside a post body are
sized by their content, not their optical weight, so don't point it at them —
prefer --all, which reads cover paths out of each post's frontmatter.

Usage:
    python3 scripts/normalize-cover.py --all            # every post cover
    python3 scripts/normalize-cover.py --all --check    # report, write nothing
    python3 scripts/normalize-cover.py <cover>.png      # one specific file
"""

import argparse
import glob
import math
import os
import re
import sys

from PIL import Image

POSTS = "site/content/posts"

TARGET = 660  # geometric mean of the ink bbox, in canvas pixels
MAX_W = 860   # caps, so a wide wordmark or tall stack can't dominate
MAX_H = 720


def measure(im):
    """Return (ink_bbox, full_bbox) — solid artwork, and artwork incl. shadows."""
    alpha = im.getchannel("A")
    ink = alpha.point(lambda v: 255 if v >= 128 else 0).getbbox()
    full = alpha.point(lambda v: 255 if v > 8 else 0).getbbox()
    return ink, full


def scale_for(ink):
    w, h = ink[2] - ink[0], ink[3] - ink[1]
    s = TARGET / math.sqrt(w * h)
    if w * s > MAX_W:
        s = MAX_W / w
    if h * s > MAX_H:
        s = MAX_H / h
    return s


def normalize(path, check_only=False):
    im = Image.open(path).convert("RGBA")
    W, H = im.size
    ink, full = measure(im)
    if ink is None or full is None:
        print(f"{path}: no artwork found, skipped")
        return True

    s = scale_for(ink)
    if abs(s - 1) < 0.01:
        print(f"{path}: already normalised")
        return True
    if check_only:
        print(f"{path}: needs {s:.3f}x")
        return False

    art = im.crop(full).resize(
        (max(1, round((full[2] - full[0]) * s)), max(1, round((full[3] - full[1]) * s))),
        Image.LANCZOS,
    )
    # Centre on the ink, not the full box, so a one-sided shadow doesn't
    # push the logo off centre.
    cx = ((ink[0] + ink[2]) / 2 - full[0]) * s
    cy = ((ink[1] + ink[3]) / 2 - full[1]) * s

    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(art, (round(W / 2 - cx), round(H / 2 - cy)))
    out.save(path)
    print(f"{path}: scaled {s:.3f}x")
    return True


def discover_covers(root):
    """Cover images named in post frontmatter, resolved relative to the post."""
    covers = []
    for index in sorted(glob.glob(os.path.join(root, "*", "index.md"))):
        m = re.search(r'^\s*image\s*=\s*"([^"]+)"', open(index).read(), re.M)
        if not m:
            continue
        path = os.path.join(os.path.dirname(index), m.group(1))
        if os.path.exists(path):
            covers.append(path)
    return covers


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("images", nargs="*",
                    help="cover images to normalise (omit with --all)")
    ap.add_argument("--all", action="store_true",
                    help=f"normalise every cover named in {POSTS}/*/index.md")
    ap.add_argument("--check", action="store_true",
                    help="report what would change without writing")
    args = ap.parse_args()

    images = args.images
    if args.all:
        images = discover_covers(POSTS) + images
    if not images:
        ap.error("give one or more images, or --all")

    ok = all([normalize(p, args.check) for p in images])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
