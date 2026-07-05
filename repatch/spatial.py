"""Spatial DELETE patches: remove marked controls/blocks from HTML."""

from __future__ import annotations

import re

_BTN_DIV_RE = re.compile(
    r'<div\b([^>]*\bclass="[^"]*\bbtn[^"]*"[^>]*)>([^<]*)</div>',
    re.IGNORECASE,
)
_BLOCK_OPEN_TAG_RE = re.compile(r"<(section|div|aside|nav)\b([^>]*)>", re.IGNORECASE)
_ANY_TAG_RE = re.compile(r"<(/?)(section|div|aside|nav)\b[^>]*>", re.IGNORECASE)


def _find_matching_close(html: str, tag_name: str, content_start: int) -> tuple[int, int] | None:
    """Find the ``(start, end)`` span of the closing tag that matches an
    opening ``<tag_name ...>`` whose content begins at ``content_start``,
    tracking nesting depth so a same-named tag nested inside (e.g. a plain
    ``<div>`` wrapper inside a ``<div class="kpi-card">``) doesn't fool a
    naive non-greedy ``.*?</tag>`` match into stopping at the *inner*
    closing tag. Returns ``None`` if the tags are unbalanced.
    """
    depth = 1
    tag_lower = tag_name.lower()
    for match in _ANY_TAG_RE.finditer(html, content_start):
        if match.group(2).lower() != tag_lower:
            continue
        if match.group(1):  # closing tag: "</...>"
            depth -= 1
            if depth == 0:
                return match.start(), match.end()
        else:
            depth += 1
    return None


def _delete_match_keys(element_id: str) -> set[str]:
    raw = (element_id or "").strip()
    if not raw:
        return set()
    keys = {raw, raw.lower()}
    if raw.lower().startswith("btn-"):
        keys.add(raw[4:])
        keys.add(raw[4:].lower())
    else:
        keys.add(f"btn-{raw}")
        keys.add(f"btn-{raw.lower()}")
    return keys


def _selectable_block_attrs(attrs: str) -> bool:
    lower = attrs.lower()
    if "nexu-selectable" in lower:
        return True
    for token in (
        "kpi-card",
        "chart-card",
        "table-card",
        "workflow-panel",
        "detail-panel",
        "nav-item",
        "service-card",
        "project-card",
    ):
        if token in lower:
            return True
    if re.search(r'\bid="btn-', lower):
        return True
    # A .btn element with nested markup (e.g. a <span> label) never matches
    # _BTN_DIV_RE (which requires no nested tags), so without this it silently
    # falls through with no delete candidate at all.
    return bool(re.search(r'\bclass="[^"]*\bbtn\b', lower))


def _element_delete_candidates(attrs: str, inner_text: str) -> set[str]:
    id_match = re.search(r'\bid="([^"]*)"', attrs, re.IGNORECASE)
    el_id = id_match.group(1) if id_match else ""
    target_match = re.search(r'data-nexu-target="([^"]*)"', attrs, re.IGNORECASE)
    target = target_match.group(1) if target_match else ""
    label = re.sub(r"<[^>]+>", "", inner_text or "").strip()
    candidates: set[str] = set()
    for raw in (el_id, target, label):
        if raw:
            candidates |= _delete_match_keys(raw)
    return candidates


def apply_spatial_deletes_to_html(html: str, delete_ids: list[str]) -> tuple[str, list[str]]:
    """
    Remove only annotated DELETE controls from calculator/dashboard HTML (no LLM rewrite).

    Matches calculator .btn rows and dashboard .kpi-card / chart / nav targets by id,
    data-nexu-target, or visible label.
    """
    if not html or not delete_ids:
        return html, []

    delete_keys: set[str] = set()
    for element_id in delete_ids:
        delete_keys |= _delete_match_keys(str(element_id))

    removed: list[str] = []

    def _btn_replacer(match: re.Match[str]) -> str:
        attrs, label = match.group(1), match.group(2).strip()
        candidates = _element_delete_candidates(attrs, label)
        if delete_keys.intersection(candidates):
            id_match = re.search(r'\bid="([^"]*)"', attrs, re.IGNORECASE)
            el_id = id_match.group(1) if id_match else ""
            removed.append(label or el_id or "unknown")
            return ""
        return match.group(0)

    patched = _BTN_DIV_RE.sub(_btn_replacer, html)
    patched = _apply_block_deletes(patched, delete_keys, removed)
    return patched, removed


def _apply_block_deletes(html: str, delete_keys: set[str], removed: list[str]) -> str:
    """Remove selectable section/div/aside/nav blocks matched by id, target, or
    label — using nesting-depth tracking so a block containing a same-named
    nested tag (e.g. a plain ``<div>`` wrapper inside a ``kpi-card`` div) is
    matched to its true closing tag instead of the first inner one."""
    parts: list[str] = []
    emitted_to = 0
    search_from = 0
    while True:
        open_match = _BLOCK_OPEN_TAG_RE.search(html, search_from)
        if not open_match:
            break
        tag_name, attrs = open_match.group(1), open_match.group(2)
        close = _find_matching_close(html, tag_name, open_match.end())
        if close is None:
            # Unbalanced/malformed markup for this tag — leave it alone and
            # keep scanning after the opening tag rather than risk mis-parsing.
            search_from = open_match.end()
            continue
        close_start, close_end = close
        inner = html[open_match.end() : close_start]
        if _selectable_block_attrs(attrs) and delete_keys.intersection(
            _element_delete_candidates(attrs, inner)
        ):
            parts.append(html[emitted_to : open_match.start()])
            id_match = re.search(r'\bid="([^"]*)"', attrs, re.IGNORECASE)
            target_match = re.search(r'data-nexu-target="([^"]*)"', attrs, re.IGNORECASE)
            removed.append(
                (id_match.group(1) if id_match else "")
                or (target_match.group(1) if target_match else "")
                or re.sub(r"<[^>]+>", "", inner).strip()
                or "unknown"
            )
            emitted_to = close_end
            search_from = close_end
        else:
            # Not deleted: keep scanning *inside* this block too, so a
            # deletable element nested inside a kept block is still found.
            search_from = open_match.end()
    parts.append(html[emitted_to:])
    return "".join(parts)
