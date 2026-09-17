"""Tag markable HTML nodes with stable data-nexu-target selectors."""

from __future__ import annotations

import re

from ._images import _attr_map

MAX_TARGETS_ADDED = 48

_MARKABLE_OPEN_RE = re.compile(
    r"<(button|a|h[1-3]|img|section|article|main|header|footer|nav|aside)\b([^>]*)>",
    re.IGNORECASE,
)


def _slug_piece(value: str, *, max_len: int = 32) -> str:
    safe = re.sub(r"[^a-zA-Z0-9]+", "-", str(value or "").strip("-").lower())
    return safe[:max_len] or "node"


def _add_markable_targets(html: str) -> tuple[str, int]:
    added = 0
    counter = 0

    def _replace(match: re.Match[str]) -> str:
        nonlocal added, counter
        if added >= MAX_TARGETS_ADDED:
            return match.group(0)
        tag = match.group(1).lower()
        attrs = match.group(2) or ""
        lowered = attrs.lower()
        if re.search(r"\bid\s*=", attrs, re.IGNORECASE):
            return match.group(0)
        if "data-nexu-target" in lowered:
            return match.group(0)
        attr_map = _attr_map(attrs)
        slug_source = attr_map.get("class") or attr_map.get("role") or tag
        counter += 1
        added += 1
        target = f"nexu-{_slug_piece(slug_source)}-{counter}"
        return f'<{tag}{attrs} data-nexu-target="{target}">'

    return _MARKABLE_OPEN_RE.sub(_replace, html), added
