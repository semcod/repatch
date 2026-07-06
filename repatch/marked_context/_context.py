"""Assemble the compact marked-element LLM context string.

Pulls extracted subtrees (``_html``) and resolved selectors/CSS
(``_selectors``) together into the single text block handed to the LLM, with
per-scope semantics and byte budgets.
"""

from __future__ import annotations

import re
from typing import Any

from ._html import _assemble_marked_subtrees
from ._selectors import _filter_css_for_tokens, _selector_tokens

MAX_MARKED_CONTEXT_BYTES = 12_000
MAX_CSS_BYTES = 6_000

_VISUAL_SCOPES = frozenset({"colors", "shapes", "display", "orientation", "keypad"})

__all__ = [
    "MAX_CSS_BYTES",
    "MAX_MARKED_CONTEXT_BYTES",
    "_VISUAL_SCOPES",
    "_cap_text",
    "_collect_css_sources",
    "_format_context_body",
    "_get_relevant_css",
    "_scope_semantics",
    "build_marked_element_context",
    "resolve_marked_llm_context",
]


def _collect_css_sources(html: str, ui_profile: dict[str, Any] | None) -> str:
    chunks: list[str] = []
    for match in re.finditer(r"<style\b[^>]*>([\s\S]*?)</style>", html or "", re.IGNORECASE):
        block = match.group(1).strip()
        if block:
            chunks.append(block)
    profile = ui_profile if isinstance(ui_profile, dict) else {}
    visual = str(profile.get("visual_css") or "").strip()
    if visual:
        chunks.append(visual)
    return "\n\n".join(chunks)


def _scope_semantics(scope: str) -> list[str]:
    normalized = (scope or "").strip().lower()
    if normalized == "functions":
        return [
            "DELETE-marked elements must be removed or fully redesigned in each variant.",
            "KEEP-marked elements must remain present and usable.",
        ]
    if normalized in _VISUAL_SCOPES:
        return [
            f"Apply #{normalized} changes primarily to DELETE-marked elements.",
            "KEEP-marked elements are hard constraints — preserve their colors/shapes/layout.",
            "Do not restyle unrelated controls outside the marked fragments.",
        ]
    return [
        "DELETE-marked elements are the primary redesign targets.",
        "KEEP-marked elements must remain present and usable.",
    ]


def _cap_text(text: str, limit: int) -> str:
    encoded = text.encode("utf-8")
    if len(encoded) <= limit:
        return text
    trimmed = encoded[: limit - 48].decode("utf-8", errors="ignore").rstrip()
    return trimmed + "\n<!-- nexu: marked context truncated -->"


def _get_relevant_css(html: str, subtrees: dict[str, str], ui_profile: dict[str, Any] | None) -> str:
    tokens = _selector_tokens(subtrees)
    css = _filter_css_for_tokens(_collect_css_sources(html, ui_profile), tokens)
    if len(css.encode("utf-8")) > MAX_CSS_BYTES:
        css = _cap_text(css, MAX_CSS_BYTES)
    return css


def _format_context_body(
    keep: list[str],
    delete: list[str],
    marked_ids: list[str],
    subtrees: dict[str, str],
    css: str,
    scope: str,
    ui_profile: dict[str, Any] | None,
) -> str:
    profile = ui_profile if isinstance(ui_profile, dict) else {}
    patch_mode = str(profile.get("llm_context_mode") or "") == "patch"
    outline = str(profile.get("html_outline") or "").strip()

    parts = [
        "MARKED ELEMENT CONTEXT (send only marked fragments — not the full page).",
        f"Focus scope: #{scope}",
        f"KEEP: {keep or ['none']}",
        f"DELETE: {delete or ['none']}",
        "Scope semantics:",
        *[f"- {line}" for line in _scope_semantics(scope)],
    ]
    if patch_mode and outline:
        parts.append(
            "Patch mode: full-page skeleton lives in nexu-outline.html; "
            "change CSS values and minimal attributes for marked fragments only."
        )
    parts.append("Marked HTML fragments:")
    for element_id in marked_ids:
        fragment = subtrees.get(element_id)
        if not fragment:
            parts.append(f"- #{element_id}: (not found in current HTML)")
            continue
        role = "KEEP" if element_id in keep else "DELETE"
        parts.append(f"- #{element_id} [{role}]:\n```html\n{fragment}\n```")
    if css:
        parts.append("Relevant CSS for marked elements:\n```css\n" + css + "\n```")
    elif patch_mode:
        parts.append(
            "Relevant CSS: use visual CSS tokens from project preprocess; "
            "target selectors matching marked ids/classes only."
        )

    return "\n\n".join(parts)


def build_marked_element_context(
    html: str,
    *,
    keep_ids: list[str] | None = None,
    delete_ids: list[str] | None = None,
    focus_scope: str = "",
    project_kind: str = "",
    ui_profile: dict[str, Any] | None = None,
    client_fragments: list[Any] | None = None,
) -> str | None:
    """Extract HTML subtrees + relevant CSS for marked ids; None when no matches."""
    keep = [str(x).strip() for x in (keep_ids or []) if str(x).strip()]
    delete = [str(x).strip() for x in (delete_ids or []) if str(x).strip()]
    marked_ids = keep + [x for x in delete if x not in keep]
    if not marked_ids:
        return None

    subtrees = _assemble_marked_subtrees(html, marked_ids, client_fragments)
    if not subtrees:
        return None

    from ..scope import normalize_focus_scope

    scope = normalize_focus_scope(focus_scope, project_kind)
    css = _get_relevant_css(html, subtrees, ui_profile)
    body = _format_context_body(keep, delete, marked_ids, subtrees, css, scope, ui_profile)
    return _cap_text(body, MAX_MARKED_CONTEXT_BYTES)


def resolve_marked_llm_context(
    html: str,
    *,
    keep_els: list[str] | None = None,
    delete_els: list[str] | None = None,
    focus_scope: str = "",
    project_kind: str = "",
    ui_profile: dict[str, Any] | None = None,
    client_fragments: list[Any] | None = None,
) -> str | None:
    """Preferred LLM context when session marks exist."""
    keep = list(keep_els or [])
    delete = list(delete_els or [])
    if not keep and not delete:
        return None
    return build_marked_element_context(
        html,
        keep_ids=keep,
        delete_ids=delete,
        focus_scope=focus_scope,
        project_kind=project_kind,
        ui_profile=ui_profile,
        client_fragments=client_fragments,
    )
