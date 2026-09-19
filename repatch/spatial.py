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
    delete_id = (element_id or "").strip()
    if not delete_id:
        return set()
    keys = {delete_id, delete_id.lower()}
    if delete_id.lower().startswith("btn-"):
        keys.add(delete_id[4:])
        keys.add(delete_id[4:].lower())
    else:
        keys.add(f"btn-{delete_id}")
        keys.add(f"btn-{delete_id.lower()}")
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
    match_keys: set[str] = set()
    for signal in (el_id, target, label):
        if signal:
            match_keys |= _delete_match_keys(signal)
    return match_keys


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

    deleted_labels: list[str] = []

    def _btn_replacer(match: re.Match[str]) -> str:
        btn_attr_text, label = match.group(1), match.group(2).strip()
        element_keys = _element_delete_candidates(btn_attr_text, label)
        if delete_keys.intersection(element_keys):
            id_match = re.search(r'\bid="([^"]*)"', btn_attr_text, re.IGNORECASE)
            el_id = id_match.group(1) if id_match else ""
            deleted_labels.append(label or el_id or "unknown")
            return ""
        return match.group(0)

    patched = _BTN_DIV_RE.sub(_btn_replacer, html)
    patched = _apply_block_deletes(patched, delete_keys, deleted_labels)
    return patched, deleted_labels


def _apply_block_deletes(html: str, delete_keys: set[str], deleted_labels: list[str]) -> str:
    """Remove selectable section/div/aside/nav blocks matched by id, target, or
    label — using nesting-depth tracking so a block containing a same-named
    nested tag (e.g. a plain ``<div>`` wrapper inside a ``kpi-card`` div) is
    matched to its true closing tag instead of the first inner one."""
    kept_segments: list[str] = []
    emitted_to = 0
    search_from = 0
    while True:
        open_match = _BLOCK_OPEN_TAG_RE.search(html, search_from)
        if not open_match:
            break
        tag_name, block_attr_text = open_match.group(1), open_match.group(2)
        close = _find_matching_close(html, tag_name, open_match.end())
        if close is None:
            # Unbalanced/malformed markup for this tag — leave it alone and
            # keep scanning after the opening tag rather than risk mis-parsing.
            search_from = open_match.end()
            continue
        close_start, close_end = close
        inner = html[open_match.end() : close_start]
        if _is_deletable_block(block_attr_text, inner, delete_keys):
            kept_segments.append(html[emitted_to : open_match.start()])
            deleted_labels.append(_block_label(block_attr_text, inner))
            emitted_to = close_end
            search_from = close_end
        else:
            # Not deleted: keep scanning *inside* this block too, so a
            # deletable element nested inside a kept block is still found.
            search_from = open_match.end()
    kept_segments.append(html[emitted_to:])
    return "".join(kept_segments)


def _is_deletable_block(attrs: str, inner: str, delete_keys: set[str]) -> bool:
    return _selectable_block_attrs(attrs) and bool(
        delete_keys.intersection(_element_delete_candidates(attrs, inner))
    )


def _block_label(attrs: str, inner: str) -> str:
    """Best-effort human label for a removed block: id, target, or text."""
    id_match = re.search(r'\bid="([^"]*)"', attrs, re.IGNORECASE)
    target_match = re.search(r'data-nexu-target="([^"]*)"', attrs, re.IGNORECASE)
    return (
        (id_match.group(1) if id_match else "")
        or (target_match.group(1) if target_match else "")
        or re.sub(r"<[^>]+>", "", inner).strip()
        or "unknown"
    )
