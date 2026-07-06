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
    keep = [str(x).strip() for x in (keep_els or []) if str(x).strip()]
    delete = [str(x).strip() for x in (delete_els or []) if str(x).strip()]
    return bool(keep or delete)


def effective_delete_ids(delete_els: list[str], keep_els: list[str]) -> list[str]:
    """Return DELETE ids that are not overridden by current KEEP marks."""
    kept = {str(x).strip().lower().removeprefix("btn-") for x in keep_els if str(x).strip()}
    kept |= {f"btn-{x}" for x in kept}
    out: list[str] = []
    for item in delete_els:
        raw = str(item).strip()
        if not raw:
            continue
        norm = raw.lower()
        alt = norm[4:] if norm.startswith("btn-") else f"btn-{norm}"
        if norm not in kept and alt not in kept:
            out.append(raw)
    return out


def _normalize_label_text(text: str) -> str:
    """Normalize visible UI labels copied from browser DOM or imported HTML."""
    value = unescape(str(text or ""))
    value = value.replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value).strip()
    return value


def _parse_attrs(attr_text: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for match in _ATTR_RE.finditer(attr_text or ""):
        key = match.group(1).lower()
        value = _normalize_label_text(match.group(3))
        attrs[key] = value
    return attrs


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
    raw = str(element_id or "").strip()
    if not raw:
        return set()
    normalized = _normalize_label_text(raw)
    out = {raw, raw.lower(), normalized, normalized.lower()}
    if raw.startswith("btn-"):
        out.add(raw[4:])
        out.add(raw[4:].lower())
    else:
        prefixed = f"btn-{raw}"
        out.add(prefixed)
        out.add(prefixed.lower())
    return out


def _css_id_selector(token: str) -> str | None:
    """Return a valid ``#id`` selector or None when the token is not a safe id."""
    raw = str(token or "").strip()
    if not raw or not _ID_SELECTOR_RE.match(raw):
        return None
    return f"#{raw}"


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
