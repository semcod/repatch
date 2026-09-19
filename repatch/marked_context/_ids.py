"""Element id / attribute normalization and CSS selector derivation.

Cinema marks arrive as logical element ids copied from the browser DOM or
imported HTML. They may be raw ids (``tan``), ``btn-`` prefixed (``btn-tan``),
``data-nexu-target`` values, or the visible text of a labelled tag. This
module owns the normalization of those signals into a stable set of id
candidates and the ``#id`` / ``[data-nexu-target]`` CSS selectors built from
them.
"""

from __future__ import annotations

import re
from html import unescape

_ATTR_RE = re.compile(
    r"""([\w:-]+)\s*=\s*(['"])(.*?)\2""",
    re.DOTALL,
)
_ID_SELECTOR_RE = re.compile(r"^[A-Za-z_][\w:-]*$")

# Tags whose visible text can serve as the Cinema mark id (HTTP import headings, etc.).
_TEXT_LABEL_TAGS = frozenset(
    {"button", "a", "span", "div", "h1", "h2", "h3", "p"}
)

__all__ = [
    "_ATTR_RE",
    "_ID_SELECTOR_RE",
    "_TEXT_LABEL_TAGS",
    "_css_id_selector",
    "_id_candidates",
    "_logical_id",
    "_normalize_label_text",
    "_parse_attrs",
    "effective_delete_ids",
    "has_ui_marks",
    "marked_css_selectors",
]


def has_ui_marks(
    keep_els: list[str] | None = None,
    delete_els: list[str] | None = None,
) -> bool:
    """True when the session or ledger sent KEEP/DELETE element ids."""
    keep_marks = [str(x).strip() for x in (keep_els or []) if str(x).strip()]
    delete = [str(x).strip() for x in (delete_els or []) if str(x).strip()]
    return bool(keep_marks or delete)


def effective_delete_ids(delete_els: list[str], keep_els: list[str]) -> list[str]:
    """Return DELETE ids that are not overridden by current KEEP marks."""
    kept = {str(x).strip().lower().removeprefix("btn-") for x in keep_els if str(x).strip()}
    kept |= {f"btn-{x}" for x in kept}
    effective_deletes: list[str] = []
    for item in delete_els:
        delete_value = str(item).strip()
        if not delete_value:
            continue
        norm = delete_value.lower()
        alt = norm[4:] if norm.startswith("btn-") else f"btn-{norm}"
        if norm not in kept and alt not in kept:
            effective_deletes.append(delete_value)
    return effective_deletes


def _normalize_label_text(text: str) -> str:
    """Normalize visible UI labels copied from browser DOM or imported HTML."""
    value = unescape(str(text or ""))
    value = value.replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value).strip()
    return value


def _parse_attrs(attr_text: str) -> dict[str, str]:
    parsed_map: dict[str, str] = {}
    for match in _ATTR_RE.finditer(attr_text or ""):
        key = match.group(1).lower()
        value = _normalize_label_text(match.group(3))
        parsed_map[key] = value
    return parsed_map


def _logical_id(tag: str, attrs: dict[str, str], *, text: str = "") -> str | None:
    raw_id = str(attrs.get("id") or "").strip()
    if raw_id:
        return raw_id[4:] if raw_id.startswith("btn-") else raw_id
    target = str(attrs.get("data-nexu-target") or "").strip()
    if target:
        return target
    if tag.lower() in _TEXT_LABEL_TAGS:
        label = _normalize_label_text(text)
        if label:
            return label
    return None


def _id_candidates(element_id: str) -> set[str]:
    mark_id = str(element_id or "").strip()
    if not mark_id:
        return set()
    normalized_label = _normalize_label_text(mark_id)
    aliases = {mark_id, mark_id.lower(), normalized_label, normalized_label.lower()}
    if mark_id.startswith("btn-"):
        aliases.add(mark_id[4:])
        aliases.add(mark_id[4:].lower())
    else:
        prefixed = f"btn-{mark_id}"
        aliases.add(prefixed)
        aliases.add(prefixed.lower())
    return aliases


def _css_id_selector(token: str) -> str | None:
    """Return a valid ``#id`` selector or None when the token is not a safe id."""
    id_token = str(token or "").strip()
    if not id_token or not _ID_SELECTOR_RE.match(id_token):
        return None
    return f"#{id_token}"


def marked_css_selectors(element_ids: list[str]) -> list[str]:
    """CSS selectors for marked logical element ids (id, btn- prefix, data-nexu-target)."""
    selectors: list[str] = []
    seen: set[str] = set()
    for element_id in element_ids:
        for token in _id_candidates(element_id):
            id_sel = _css_id_selector(token)
            for sel in (id_sel, f'[data-nexu-target="{token}"]'):
                if sel and sel not in seen:
                    seen.add(sel)
                    selectors.append(sel)
    return selectors
