"""Per-scope, per-variant CSS declarations for DELETE-marked nodes.

Each visual scope (colors/shapes/display/orientation) emits a different kind
of declaration, parameterized by an a/b/c variant. These builders are pure
functions of the selector list and variant.
"""

from __future__ import annotations

_MARKED_COLOR_DECL: dict[str, str] = {
    "a": (
        "background-color:#38bdf8!important;color:#0f172a!important;"
        "border-color:#0ea5e9!important;"
    ),
    "b": (
        "background-color:#facc15!important;color:#000!important;"
        "border-color:#ca8a04!important;"
    ),
    "c": (
        "background-color:#e879f9!important;color:#1e1b4b!important;"
        "border-color:#c026d3!important;"
    ),
}

__all__ = [
    "_MARKED_COLOR_DECL",
    "marked_scope_colors_css",
    "marked_scope_display_css",
    "marked_scope_orientation_css",
    "marked_scope_shapes_css",
]


def _clean_selectors(selectors: list[str]) -> list[str]:
    return [str(sel).strip() for sel in (selectors or []) if str(sel).strip()]


def _variant_letter(variant: str) -> str:
    return variant if variant in ("a", "b", "c") else "b"


def marked_scope_colors_css(selectors: list[str], variant: str) -> str:
    """Per-variant recolor declarations for DELETE marks in #colors scope."""
    decl = _MARKED_COLOR_DECL.get(_variant_letter(variant), "")
    clean = _clean_selectors(selectors)
    if not clean or not decl:
        return ""
    base_rule = f"{', '.join(clean)} {{{decl}}}"
    color_decl = ""
    for part in decl.split(";"):
        piece = part.strip()
        if piece.startswith("color:"):
            color_decl = piece if piece.endswith("!important") else f"{piece}!important"
            break
    if not color_decl:
        return base_rule
    inline_beat = ", ".join(
        f"{sel} *, {sel} [style*='color'], {sel} [style*='Color']"
        for sel in clean
    )
    return f"{base_rule}\n{inline_beat} {{{color_decl};}}"


def marked_scope_display_css(selectors: list[str], variant: str) -> str:
    """Extra typography on DELETE-marked nodes in #display scope."""
    clean = _clean_selectors(selectors)
    if not clean:
        return ""
    decl = {
        "a": "font-size:1.1rem!important;line-height:1.35!important;",
        "b": "font-size:1.2rem!important;line-height:1.4!important;",
        "c": "font-size:1.35rem!important;font-weight:600!important;line-height:1.45!important;",
    }[_variant_letter(variant)]
    return f"{', '.join(clean[:8])} {{{decl}}}"


def marked_scope_shapes_css(selectors: list[str], variant: str) -> str:
    """Corner radii on DELETE-marked nodes in #shapes scope."""
    clean = _clean_selectors(selectors)
    if not clean:
        return ""
    decl = {
        "a": "border-radius:4px!important;",
        "b": "border-radius:12px!important;",
        "c": "border-radius:999px!important;",
    }[_variant_letter(variant)]
    return f"{', '.join(clean[:8])} {{{decl}}}"


def marked_scope_orientation_css(selectors: list[str], variant: str) -> str:
    """Layout CSS for DELETE-marked fragments in #orientation scope.

    Orientation changes need to affect the nearest content container, not only the
    marked leaf nodes. ``:has()`` lets us target those local parents while keeping
    the rest of the imported page unchanged.
    """
    clean_selectors = _clean_selectors(selectors)
    if not clean_selectors:
        return ""
    v = _variant_letter(variant)
    layouts = {
        "a": "grid-template-columns:minmax(0,1fr)!important;max-width:980px!important;",
        "b": (
            "grid-template-columns:1fr 1fr!important;"
            "max-width:1180px!important;"
        ),
        "c": (
            "grid-template-columns:repeat(auto-fit,minmax(260px,1fr))!important;"
            "max-width:1240px!important;"
        ),
    }
    parent_bases = (
        "main",
        "article",
        "section",
        ".entry-content",
        ".wp-site-blocks",
        ".wp-block-post-content",
        ".wp-block-group",
        ".site-main",
        ".page",
        ".content",
    )
    parent_selectors: list[str] = []
    body_selectors: list[str] = []
    for selector in clean_selectors[:8]:
        parent_selectors.extend(f"{base}:has({selector})" for base in parent_bases)
        body_selectors.append(f'body[data-nexu-import-preview="http"]:has({selector})')
    target_prefix = ", ".join(clean_selectors)
    parent_prefix = ", ".join(dict.fromkeys(parent_selectors))
    body_prefix = ", ".join(dict.fromkeys(body_selectors))
    return (
        f"{parent_prefix} "
        "{display:grid!important;"
        f"{layouts[v]}"
        "gap:clamp(16px,3vw,32px)!important;"
        "align-items:start!important;margin-left:auto!important;margin-right:auto!important;}"
        f"\n{body_prefix} "
        "{display:grid!important;"
        f"{layouts[v]}"
        "gap:clamp(16px,3vw,32px)!important;align-items:start!important;}"
        f"\n{target_prefix} "
        "{box-sizing:border-box!important;max-width:100%!important;width:auto!important;"
        "grid-column:auto!important;align-self:start!important;}"
        "\n@media (max-width: 760px){"
        f"{parent_prefix},{body_prefix}"
        "{grid-template-columns:1fr!important;}"
        "}"
    )
