"""Detect and strip lazy-load placeholder images from imported HTML."""

from __future__ import annotations

import re

_IMG_TAG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
_ATTR_RE = re.compile(r"""(\w[\w-]*)\s*=\s*(['"])(.*?)\2""", re.IGNORECASE | re.DOTALL)


def _attr_map(tag_attrs: str) -> dict[str, str]:
    return {m.group(1).lower(): m.group(3) for m in _ATTR_RE.finditer(tag_attrs or "")}


def is_lazy_placeholder_img_tag(tag: str) -> bool:
    """True for lazy-load placeholder imgs (blank src + lazy markers)."""
    if not _IMG_TAG_RE.match(str(tag or "").strip()):
        return False
    inner = tag[4:] if tag.lower().startswith("<img") else tag
    attrs = _attr_map(inner)
    src = (attrs.get("src") or "").strip().lower()
    cls = attrs.get("class") or ""
    lazy_attr = any(
        key in attrs
        for key in ("data-lazyloaded", "data-lazy-src", "data-src")
    ) or re.search(r"\blazy(?:load)?\b", cls, re.IGNORECASE)
    blank = not src or src == "#" or src.startswith("data:image/svg+xml")
    return bool(lazy_attr and blank)


def _strip_lazy_placeholder_imgs(html: str) -> tuple[str, int]:
    stripped_count = 0

    def _replace(match: re.Match[str]) -> str:
        nonlocal stripped_count
        tag = match.group(0)
        if is_lazy_placeholder_img_tag(tag):
            stripped_count += 1
            return "<!-- repatch: lazy placeholder img removed -->"
        return tag

    return _IMG_TAG_RE.sub(_replace, html), stripped_count
