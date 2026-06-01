"""Spatial DELETE patches: remove marked controls/blocks from HTML."""

from __future__ import annotations

import re

_BTN_DIV_RE = re.compile(
    r'<div\b([^>]*\bclass="[^"]*\bbtn[^"]*"[^>]*)>([^<]*)</div>',
    re.IGNORECASE,
)
_SELECTABLE_BLOCK_RE = re.compile(
    r"<(section|div|aside|nav)\b([^>]*)>([\s\S]*?)</\1>",
    re.IGNORECASE,
)


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
    return bool(re.search(r'\bid="btn-', lower))


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

    def _block_replacer(match: re.Match[str]) -> str:
        _tag, attrs, inner = match.group(1), match.group(2), match.group(3)
        if not _selectable_block_attrs(attrs):
            return match.group(0)
        candidates = _element_delete_candidates(attrs, inner)
        if delete_keys.intersection(candidates):
            id_match = re.search(r'\bid="([^"]*)"', attrs, re.IGNORECASE)
            target_match = re.search(r'data-nexu-target="([^"]*)"', attrs, re.IGNORECASE)
            removed.append(
                (id_match.group(1) if id_match else "")
                or (target_match.group(1) if target_match else "")
                or re.sub(r"<[^>]+>", "", inner).strip()
                or "unknown"
            )
            return ""
        return match.group(0)

    patched = _BTN_DIV_RE.sub(_btn_replacer, html)
    patched = _SELECTABLE_BLOCK_RE.sub(_block_replacer, patched)
    return patched, removed
