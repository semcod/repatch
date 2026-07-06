"""Balanced HTML subtree extraction for marked elements.

Given a page and a set of logical element ids, find the outerHTML of each
matched element (id, ``data-nexu-target``, or visible-text label) and compact
it into a fragment small enough to embed in LLM context.
"""

from __future__ import annotations

import re
from typing import Any

from ._ids import (
    _id_candidates,
    _logical_id,
    _normalize_label_text,
    _parse_attrs,
)

MAX_FRAGMENT_BYTES = 2_500

_VOID_TAGS = frozenset(
    {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }
)
_TAG_OPEN_RE = re.compile(r"<\s*([a-zA-Z][\w:-]*)\b([^>]*)>", re.DOTALL)

__all__ = [
    "MAX_FRAGMENT_BYTES",
    "_TAG_OPEN_RE",
    "_VOID_TAGS",
    "_assemble_marked_subtrees",
    "_client_fragment_html",
    "_collect_button_candidates",
    "_collect_match_candidates",
    "_extract_and_format_fragment",
    "_extract_balanced_html",
    "_find_marked_subtrees",
]


def _extract_balanced_html(html: str, start: int) -> tuple[str, int] | None:
    """Return outerHTML starting at ``start`` and the index after it."""
    open_match = _TAG_OPEN_RE.match(html, start)
    if not open_match:
        return None
    tag = open_match.group(1).lower()
    open_end = open_match.end()
    if open_match.group(0).rstrip().endswith("/>"):
        return html[start:open_end], open_end
    if tag in _VOID_TAGS:
        return html[start:open_end], open_end
    depth = 1
    pos = open_end
    length = len(html)
    open_pat = re.compile(rf"<\s*{re.escape(tag)}\b", re.IGNORECASE)
    close_pat = re.compile(rf"<\s*/\s*{re.escape(tag)}\s*>", re.IGNORECASE)
    while pos < length and depth > 0:
        next_open = open_pat.search(html, pos)
        next_close = close_pat.search(html, pos)
        if next_close is None:
            break
        if next_open is not None and next_open.start() < next_close.start():
            depth += 1
            pos = next_open.end()
            continue
        depth -= 1
        pos = next_close.end()
    if depth != 0:
        return None
    return html[start:pos], pos


def _collect_match_candidates(tag: str, attrs: dict[str, str]) -> set[str]:
    raw_id = str(attrs.get("id") or "").strip()
    candidates = _id_candidates(raw_id) if raw_id else set()
    target = str(attrs.get("data-nexu-target") or "").strip()
    if target:
        candidates |= _id_candidates(target)
    logical = _logical_id(tag, attrs)
    if logical:
        candidates |= _id_candidates(logical)
    return candidates


def _collect_button_candidates(tag: str, attrs: dict[str, str], match, raw_html: str) -> set[str]:
    inner_start = match.end()
    inner_end = raw_html.lower().find(f"</{tag}>", inner_start)
    inner = raw_html[inner_start:inner_end if inner_end >= 0 else inner_start]
    label = _normalize_label_text(re.sub(r"<[^>]+>", "", inner))
    logical = _logical_id(tag, attrs, text=label)
    if logical:
        return _id_candidates(logical)
    return set()


def _extract_and_format_fragment(text: str, start: int) -> str | None:
    extracted = _extract_balanced_html(text, start)
    if not extracted:
        return None
    fragment, _ = extracted
    compact = re.sub(r"\s+", " ", fragment).strip()
    if len(compact.encode("utf-8")) > MAX_FRAGMENT_BYTES:
        compact = compact[: MAX_FRAGMENT_BYTES - 32].rstrip() + " <!-- truncated -->"
    return compact


def _find_marked_subtrees(html: str, marked_ids: set[str]) -> dict[str, str]:
    """Map logical element id → compact outerHTML fragment."""
    if not marked_ids:
        return {}
    wanted = {str(item).strip() for item in marked_ids if str(item).strip()}
    found: dict[str, str] = {}
    text = str(html or "")
    for match in _TAG_OPEN_RE.finditer(text):
        tag = match.group(1).lower()
        attrs = _parse_attrs(match.group(2))
        raw_id = str(attrs.get("id") or "").strip()
        target = str(attrs.get("data-nexu-target") or "").strip()
        candidates = _collect_match_candidates(tag, attrs)
        hit = wanted & candidates
        if not hit and tag not in _VOID_TAGS and tag not in (
            "html",
            "head",
            "body",
            "style",
            "script",
            "link",
            "meta",
        ):
            if not raw_id and not target:
                btn_candidates = _collect_button_candidates(tag, attrs, match, text)
                hit = wanted & btn_candidates
        if not hit:
            continue
        compact = _extract_and_format_fragment(text, match.start())
        if not compact:
            continue
        for element_id in hit:
            found.setdefault(element_id, compact)
        if len(found) >= len(wanted):
            break
    return found


def _client_fragment_html(client_fragments: list[Any] | None, element_id: str) -> str | None:
    for item in client_fragments or []:
        if not isinstance(item, dict):
            continue
        ident = str(item.get("id") or "").strip()
        if ident != element_id:
            continue
        frag = item.get("fragment")
        if isinstance(frag, dict):
            html = re.sub(r"\s+", " ", str(frag.get("html") or "")).strip()
            if html:
                return html
    return None


def _assemble_marked_subtrees(
    html: str,
    marked_ids: list[str],
    client_fragments: list[Any] | None,
) -> dict[str, str]:
    subtrees = _find_marked_subtrees(html, set(marked_ids))
    for element_id in marked_ids:
        if element_id in subtrees:
            continue
        client_html = _client_fragment_html(client_fragments, element_id)
        if client_html:
            subtrees[element_id] = client_html
    return subtrees
