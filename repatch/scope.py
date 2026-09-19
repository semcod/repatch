"""Scope pipeline: bind marked annotations, resolve kind, and inject scope CSS."""

from __future__ import annotations

import re

from ._scope_css import (
    SCOPE_STYLE_ID,
    _calc_scope_css,
    _scope_css,
    _uses_web_scope_css,
    _web_display_scope_css,
    _web_orientation_scope_css,
    _web_scope_css,
    _web_shapes_scope_css,
    strip_scope_style,
)
from ._scope_kinds import (
    DASHBOARD_KINDS,
    IMPORTED_KINDS,
    MARKED_PATCH_KINDS,
    VISUAL_REDESIGN_SCOPES,
    allowed_scope_ids,
    default_scope_for_kind,
    goal_requests_column_layout,
    normalize_focus_scope,
    offline_fast_scopes_for_kind,
    scope_supports_offline_fast_path,
    ui_type_for_kind,
)
from .marked_context import (
    _TAG_OPEN_RE,
    _id_candidates,
    _logical_id,
    _normalize_label_text,
    _parse_attrs,
    effective_delete_ids,
    has_ui_marks,
    marked_scope_colors_css,
    marked_scope_display_css,
    marked_scope_orientation_css,
    marked_scope_shapes_css,
    resolve_marked_selectors,
    restrict_scope_css_to_marks,
)

__all__ = [
    "DASHBOARD_KINDS",
    "IMPORTED_KINDS",
    "MARKED_PATCH_KINDS",
    "SCOPE_STYLE_ID",
    "VISUAL_REDESIGN_SCOPES",
    "allowed_scope_ids",
    "default_scope_for_kind",
    "goal_requests_column_layout",
    "inject_scope_style",
    "normalize_focus_scope",
    "offline_fast_scopes_for_kind",
    "scope_supports_offline_fast_path",
    "scoped_html_fragment",
    "should_block_full_html_iterate",
    "strip_scope_style",
    "ui_type_for_kind",
]


def _resolve_scope_kind(project_kind: str, html: str) -> str:
    kind = (project_kind or "").strip().lower()
    if kind in IMPORTED_KINDS or kind in DASHBOARD_KINDS or kind == "calculator":
        return kind
    lowered = (html or "").lower()
    if "calc-body" in lowered or "btn-eq" in lowered:
        return "calculator"
    if "kpi-grid" in lowered or "app-shell" in lowered:
        return "dashboard"
    return "web"


def should_block_full_html_iterate(
    project_kind: str,
    keep_els: list[str] | None,
    delete_els: list[str] | None,
    *,
    focus_scope: str = "",
) -> bool:
    """True when marks exist on imported/web/dashboard projects — force patch paths only."""
    if not has_ui_marks(keep_els, delete_els):
        return False
    kind = (project_kind or "").strip().lower()
    return kind in MARKED_PATCH_KINDS


_SKIP_TAGS = ("html", "head", "body", "style", "script", "link", "meta")


def _element_candidates(tag: str, attrs: dict[str, str]) -> tuple[set[str], str, str]:
    """Collect candidate ids from id, data-nexu-target and logical id."""
    raw_id = str(attrs.get("id") or "").strip()
    target = str(attrs.get("data-nexu-target") or "").strip()
    candidates = _id_candidates(raw_id) if raw_id else set()
    if target:
        candidates |= _id_candidates(target)
    logical = _logical_id(tag, attrs)
    if logical:
        candidates |= _id_candidates(logical)
    return candidates, raw_id, target


def _label_probe_hit(
    text: str,
    match: "re.Match[str]",
    tag: str,
    attrs: dict[str, str],
    wanted: set[str],
) -> set[str]:
    """Probe inner text label for a logical id when the tag has no id attrs."""
    inner_start = match.end()
    inner_end = text.lower().find(f"</{tag}>", inner_start)
    if inner_end < 0:
        return set()
    label = _normalize_label_text(re.sub(r"<[^>]+>", "", text[inner_start:inner_end]))
    logical = _logical_id(tag, attrs, text=label)
    return wanted & _id_candidates(logical) if logical else set()


def _splice_replacements(text: str, matched_ranges: list[tuple[int, int, str]]) -> str:
    parts: list[str] = []
    last_idx = 0
    for start, end, replacement in matched_ranges:
        parts.append(text[last_idx:start])
        parts.append(replacement)
        last_idx = end
    parts.append(text[last_idx:])
    return "".join(parts)


def _bind_annotations_to_html(
    html: str,
    keep_ids: list[str] | None,
    delete_ids: list[str] | None,
) -> str:
    keep = [str(x).strip() for x in (keep_ids or []) if str(x).strip()]
    delete = [str(x).strip() for x in (delete_ids or []) if str(x).strip()]
    marked_ids = keep + [x for x in delete if x not in keep]
    if not marked_ids:
        return html

    wanted = set(marked_ids)
    text = str(html or "")

    matched_ranges: list[tuple[int, int, str]] = []
    seen_elements = set()

    for match in _TAG_OPEN_RE.finditer(text):
        target_range = _annotation_target(text, match, wanted, seen_elements)
        if target_range:
            matched_ranges.append(target_range)

    if not matched_ranges:
        return html
    return _splice_replacements(text, matched_ranges)


def _annotation_target(
    text: str,
    match: "re.Match[str]",
    wanted: set[str],
    seen_elements: set,
) -> tuple[int, int, str] | None:
    """Return the replacement range for a matched element, or None to skip."""
    tag = match.group(1).lower()
    if tag in _SKIP_TAGS:
        return None
    attrs_text = match.group(2)
    attrs = _parse_attrs(attrs_text)

    candidates, raw_id, target = _element_candidates(tag, attrs)
    hit = wanted & candidates
    if not hit and not raw_id and not target:
        hit = _label_probe_hit(text, match, tag, attrs, wanted)
    if not hit:
        return None

    matched_id = list(hit)[0]
    if matched_id in seen_elements:
        return None
    seen_elements.add(matched_id)

    if "data-nexu-target" in attrs:
        return None

    new_tag = f"<{tag} data-nexu-target=\"{matched_id}\" {attrs_text}>"
    return (match.start(), match.end(), new_tag)


def _get_scope_css(
    inferred: str,
    html: str,
    scope: str,
    variant: str,
    *,
    user_goal: str = "",
) -> str:
    if inferred == "calculator" or (
        inferred not in IMPORTED_KINDS.union(DASHBOARD_KINDS) and "calc-body" in html.lower()
    ):
        return _calc_scope_css(scope, variant)
    if inferred in DASHBOARD_KINDS or "kpi-grid" in html.lower():
        return _scope_css(scope, variant)
    return _web_scope_css(scope, variant, user_goal=user_goal) or _scope_css(scope, variant)


def inject_css_block(html: str, css: str) -> str:
    """Inject a `<style>` block before `</head>` or at `<body>`, else prepend."""
    if not css:
        return html
    style_tag = f'<style id="{SCOPE_STYLE_ID}">\n{css}\n</style>'
    lower = html.lower()
    if "</head>" in lower:
        idx = lower.rfind("</head>")
        return html[:idx] + style_tag + html[idx:]
    if "<body" in lower:
        match = re.search(r"<body[^>]*>", html, flags=re.IGNORECASE)
        if match:
            pos = match.start()
            return html[:pos] + style_tag + html[pos:]
    return style_tag + html


_inject_css_block = inject_css_block



def _marked_scope_css(
    scope: str,
    variant: str,
    css: str,
    cleaned: str,
    inferred: str,
    effective_delete: list[str],
    keep_list: list[str],
    user_goal: str,
) -> str:
    """Restrict or replace scope CSS using resolved marked selectors."""
    selectors = resolve_marked_selectors(
        cleaned,
        effective_delete,
        keep_ids=keep_list,
        narrow=(scope == "colors"),
    )
    web_scope = _uses_web_scope_css(inferred, cleaned)
    if scope == "colors" and selectors:
        return marked_scope_colors_css(selectors, variant)
    if scope == "orientation" and selectors:
        return _orientation_marked_css(selectors, variant, web_scope, user_goal)
    if scope == "display" and selectors and web_scope:
        return _composed_css(_web_display_scope_css(variant), marked_scope_display_css(selectors, variant))
    if scope == "shapes" and selectors and web_scope:
        return _composed_css(_web_shapes_scope_css(variant), marked_scope_shapes_css(selectors, variant))
    return restrict_scope_css_to_marks(
        css,
        effective_delete,
        html=cleaned,
        keep_ids=keep_list,
    )


def _composed_css(base: str, extra: str) -> str:
    return f"{base}\n{extra}" if extra else base


def _orientation_marked_css(
    selectors: list,
    variant: str,
    web_scope: bool,
    user_goal: str,
) -> str:
    marked = marked_scope_orientation_css(selectors, variant)
    if web_scope and goal_requests_column_layout(user_goal):
        page_css = _web_orientation_scope_css(variant, user_goal=user_goal)
        if page_css:
            return f"{page_css}\n{marked}"
    return marked


def inject_scope_style(
    html: str,
    scope: str,
    variant: str,
    *,
    project_kind: str = "",
    delete_ids: list[str] | None = None,
    keep_ids: list[str] | None = None,
    user_goal: str = "",
) -> str:
    html = _bind_annotations_to_html(html, keep_ids, delete_ids)
    inferred = _resolve_scope_kind(project_kind, html)
    scope = normalize_focus_scope(scope, inferred)
    delete_list = [str(x).strip() for x in (delete_ids or []) if str(x).strip()]
    keep_list = [str(x).strip() for x in (keep_ids or []) if str(x).strip()]
    effective_delete = effective_delete_ids(delete_list, keep_list)
    if scope in VISUAL_REDESIGN_SCOPES and keep_list and not effective_delete:
        return strip_scope_style(html)
    css = _get_scope_css(inferred, html, scope, variant, user_goal=user_goal)
    cleaned = strip_scope_style(html)
    if scope in VISUAL_REDESIGN_SCOPES and effective_delete:
        css = _marked_scope_css(
            scope, variant, css, cleaned, inferred,
            effective_delete, keep_list, user_goal,
        )
    return inject_css_block(cleaned, css)


def scoped_html_fragment(html: str, focus_scope: str, project_kind: str) -> str | None:
    """Smaller HTML slice for scoped LLM prompts when the scope is visual-only."""
    if not scope_supports_offline_fast_path(focus_scope, project_kind):
        return None
    text = str(html or "")
    scope = normalize_focus_scope(focus_scope, project_kind)
    patterns = (
        r'(<div[^>]*class=[\'"][^\'"]*calc-body[^\'"]*[\'"][\s\S]*?</div>\s*</div>)',
        r'(<div[^>]*class=[\'"][^\'"]*app-shell[^\'"]*[\'"][\s\S]*?</div>\s*</div>)',
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match and len(match.group(1)) >= 40:
            return (
                f"<!-- scoped DOM fragment for #{scope}; regenerate full page from baseline -->\n"
                + match.group(1)
            )
    return None
