"""Resolve marked CSS selectors and restrict scope CSS to marks.

Bridges the id/attribute world (``_ids``) and the extracted HTML fragments
(``_html``) into the concrete CSS selector lists used to scope offline/LLM
CSS to DELETE-marked nodes without touching KEEP nodes or page-wide rules.
"""

from __future__ import annotations

import re

from ..css import split_css_rules
from ._html import _find_marked_subtrees
from ._ids import _css_id_selector, _id_candidates, marked_css_selectors

# Shared theme/layout classes — too broad for per-DELETE #colors recoloring.
_GENERIC_SHARED_CLASSES = frozenset(
    {
        "button",
        "btn",
        "header-button",
        "kb-button",
        "wp-block-button",
        "wp-block-kadence-advancedheading",
        "wp-element-button",
        "link",
        "nav-item",
        "menu-item",
        "cta",
    }
)

__all__ = [
    "_GENERIC_SHARED_CLASSES",
    "_collect_keep_selectors",
    "_filter_css_for_tokens",
    "_fragment_class_names",
    "_selector_tokens",
    "resolve_marked_selectors",
    "restrict_scope_css_to_marks",
]


def _fragment_class_names(fragment: str) -> set[str]:
    classes: set[str] = set()
    for match in re.finditer(
        r"""\bclass\s*=\s*(['"])(.*?)\1""", fragment, re.IGNORECASE
    ):
        for cls in re.split(r"\s+", match.group(2).strip()):
            if cls and re.match(r"^[\w-]+$", cls):
                classes.add(cls)
    return classes


def _collect_keep_selectors(html: str, keep_ids: list[str]) -> set[str]:
    """Selectors that must not receive DELETE-only scope CSS."""
    keep = [str(x).strip() for x in (keep_ids or []) if str(x).strip()]
    if not keep:
        return set()
    blocked: set[str] = set()
    for element_id in keep:
        blocked.update(marked_css_selectors([element_id]))
    for fragment in _find_marked_subtrees(str(html or ""), set(keep)).values():
        for match in re.finditer(r"""\bid\s*=\s*(['"])(.*?)\1""", fragment, re.IGNORECASE):
            id_sel = _css_id_selector(match.group(2).strip())
            if id_sel:
                blocked.add(id_sel)
        for cls in _fragment_class_names(fragment):
            blocked.add(f".{cls}")
    return blocked


def resolve_marked_selectors(
    html: str,
    element_ids: list[str],
    *,
    keep_ids: list[str] | None = None,
    narrow: bool = False,
) -> list[str]:
    """Marked selectors from ids plus class/id tokens found in matching HTML fragments."""
    delete = [str(x).strip() for x in (element_ids or []) if str(x).strip()]
    if not delete:
        return []
    selectors: list[str] = []
    seen: set[str] = set()
    blocked = _collect_keep_selectors(html, keep_ids or []) if (keep_ids or narrow) else set()

    def add(sel: str | None) -> None:
        if sel and sel not in seen and sel not in blocked:
            seen.add(sel)
            selectors.append(sel)

    for element_id in delete:
        for sel in marked_css_selectors([element_id]):
            add(sel)

    subtrees = _find_marked_subtrees(str(html or ""), set(delete))
    for fragment in subtrees.values():
        for match in re.finditer(r"""\bid\s*=\s*(['"])(.*?)\1""", fragment, re.IGNORECASE):
            add(_css_id_selector(match.group(2).strip()))
        for cls in _fragment_class_names(fragment):
            if narrow and cls.lower() in _GENERIC_SHARED_CLASSES:
                continue
            add(f".{cls}")
    return selectors


def restrict_scope_css_to_marks(
    css: str,
    delete_ids: list[str],
    *,
    html: str = "",
    keep_ids: list[str] | None = None,
) -> str:
    """Limit offline/LLM scope CSS to DELETE-marked selectors; drop page-wide rules."""
    delete = [str(x).strip() for x in (delete_ids or []) if str(x).strip()]
    if not css or not delete:
        return css
    if html:
        prefix_list = resolve_marked_selectors(
            html, delete, keep_ids=keep_ids, narrow=True
        )
    else:
        prefix_list = marked_css_selectors(delete)
    if not prefix_list:
        return css
    prefix = ", ".join(prefix_list)
    kept: list[str] = []
    for rule in split_css_rules(css):
        chunk = rule.strip()
        if not chunk or "{" not in chunk:
            continue
        selector, rest = chunk.split("{", 1)
        sel = selector.strip().lower()
        if not sel or sel.startswith(("html", "body")):
            continue
        decl = rest.rsplit("}", 1)[0].strip()
        if not decl:
            continue
        kept.append(f"{prefix} {{{decl}}}")
    return "\n".join(kept)


def _selector_tokens(subtrees: dict[str, str]) -> set[str]:
    tokens: set[str] = set()
    for element_id in subtrees:
        tokens |= {f"#{item}" for item in _id_candidates(element_id)}
    for fragment in subtrees.values():
        for match in re.finditer(r"""\bid\s*=\s*(['"])(.*?)\1""", fragment, re.IGNORECASE):
            raw = match.group(2).strip()
            if raw:
                tokens |= {f"#{raw}", f"#{raw.lower()}"}
        for match in re.finditer(r"""class\s*=\s*(['"])(.*?)\1""", fragment, re.IGNORECASE):
            for cls in re.split(r"\s+", match.group(2).strip()):
                if cls:
                    tokens.add(f".{cls}")
                    tokens.add(f".{cls.lower()}")
    return tokens


def _filter_css_for_tokens(css: str, tokens: set[str]) -> str:
    if not css or not tokens:
        return ""
    kept: list[str] = []
    for rule in split_css_rules(css):
        selector = rule.split("{", 1)[0].lower()
        if any(token.lower() in selector for token in tokens):
            kept.append(rule)
    return "\n\n".join(kept)
