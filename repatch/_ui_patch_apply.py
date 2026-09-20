"""Validate and apply LLM CSS patch options to HTML."""

from __future__ import annotations

from typing import Any

from ._ui_patch_prompt import _ALT_FILES
from .css import validate_css_safety
from .marked_context import (
    marked_scope_colors_css,
    resolve_marked_selectors,
    restrict_scope_css_to_marks,
)
from .scope import (
    VISUAL_REDESIGN_SCOPES,
    effective_focus_scope,
    inject_css_block,
    strip_scope_style,
)

_BAD_CSS_TOKENS = (
    "<",
    "</style",
    "<script",
    "@import",
    "url(",
    "expression(",
    "javascript:",
)


def _safe_css(css: object) -> str:
    text = str(css or "").strip()
    lowered = text.lower()
    if not text:
        raise ValueError("empty CSS patch")
    if len(text) > 5000:
        raise ValueError("CSS patch is too large")
    for token in _BAD_CSS_TOKENS:
        if token in lowered:
            raise ValueError(f"unsafe CSS token: {token}")
    if "{" not in text or "}" not in text:
        raise ValueError("CSS patch must contain CSS rules")
    ok, violations = validate_css_safety(text, source="LLM CSS patch")
    if not ok:
        raise ValueError("; ".join(violations[:4]))
    return text


def _label_for(filename: str, item: Any, fallback: dict[str, str]) -> str:
    if isinstance(item, dict):
        variant_label = str(item.get("label") or "").strip()
        if variant_label:
            return variant_label[:120]
    return fallback.get(filename, filename)


def _css_for(item: Any) -> str:
    if isinstance(item, dict):
        return _safe_css(item.get("css"))
    return _safe_css(item)


def _resolve_patch_css(
    item: Any,
    filename: str,
    scope: str,
    delete_ids: list[str],
    keep_ids: list[str],
    base: str,
) -> str:
    """Resolve the CSS payload for one variant, honoring marked scopes."""
    variant_css = _css_for(item)
    if scope in VISUAL_REDESIGN_SCOPES and delete_ids:
        restricted = restrict_scope_css_to_marks(variant_css, delete_ids, html=base).strip()
        if not restricted and scope == "colors":
            variant_key = filename.removeprefix("alt_").removesuffix(".html")
            restricted = marked_scope_colors_css(
                resolve_marked_selectors(base, delete_ids),
                variant_key,
            )
        variant_css = restricted or variant_css
    elif scope in VISUAL_REDESIGN_SCOPES and keep_ids and not delete_ids:
        variant_css = ""
    if not variant_css.strip():
        variant_css = "/* xpatch noop: only KEEP marks were provided */"
    return variant_css


def apply_ui_patch_options(
    html: str,
    patch: dict[str, Any],
    *,
    option_variants: list[tuple[str, str, str]],
    focus_scope: str = "",
    project_kind: str = "",
    keep_els: list[str] | None = None,
    delete_els: list[str] | None = None,
) -> tuple[dict[str, str], list[str]]:
    """Apply validated CSS patches to one baseline HTML document."""
    variants = patch.get("variants")
    if not isinstance(variants, dict):
        raise ValueError("patch variants must be an object")
    fallback_labels = {
        filename: variant_label for filename, variant_label, _note in option_variants
    }
    base = strip_scope_style(str(html or ""))
    apply_scope = effective_focus_scope(focus_scope, project_kind, default_when_unset=False)
    delete_ids = [str(x).strip() for x in (delete_els or []) if str(x).strip()]
    keep_ids = [str(x).strip() for x in (keep_els or []) if str(x).strip()]
    files: dict[str, str] = {}
    labels: list[str] = []
    for filename in _ALT_FILES:
        item = variants.get(filename)
        if item is None:
            raise ValueError(f"missing {filename} in LLM patch response")
        variant_css = _resolve_patch_css(item, filename, apply_scope, delete_ids, keep_ids, base)
        variant_label = _label_for(filename, item, fallback_labels)
        payload = f"/* llm patch: {variant_label} */\n{variant_css}"
        files[filename] = inject_css_block(base, payload)
        labels.append(variant_label)
    return files, labels
