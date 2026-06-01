"""Scope contracts, CSS injection, and marked-scope restriction."""

from __future__ import annotations

import re
from typing import Any

from .marked_context import (
    _TAG_OPEN_RE,
    _id_candidates,
    _logical_id,
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

DASHBOARD_KINDS = frozenset(
    {"dashboard", "monitor", "ecosystem", "api", "mcp", "frontend", "slice"}
)

SCOPE_STYLE_ID = "nexu-scope-variant"

# kind -> ordered scope ids shown in Cinema player
IMPORTED_KINDS = frozenset({"imported", "web"})

SCOPE_IDS_BY_KIND: dict[str, tuple[str, ...]] = {
    "imported": ("functions", "display", "colors", "shapes", "orientation"),
    "web": ("functions", "display", "colors", "shapes", "orientation"),
    "dashboard": ("functions", "display", "colors", "shapes", "orientation"),
    "monitor": ("functions", "display", "colors", "shapes", "orientation"),
    "ecosystem": ("functions", "display", "colors", "shapes", "orientation"),
    "api": ("functions", "display", "colors", "shapes"),
    "mcp": ("functions", "display", "colors", "shapes"),
    "frontend": ("functions", "display", "colors", "shapes", "orientation"),
    "slice": ("functions", "display", "colors", "shapes"),
    "calculator": (
        "functions",
        "keypad",
        "display",
        "colors",
        "shapes",
        "orientation",
    ),
}

DEFAULT_SCOPE_BY_KIND: dict[str, str] = {
    "dashboard": "functions",
    "monitor": "functions",
    "ecosystem": "functions",
    "api": "functions",
    "imported": "functions",
    "web": "functions",
    "calculator": "keypad",
}

# Visual scopes handled by cinema_offline_options + inject_scope_style (~10–50ms).
OFFLINE_FAST_SCOPES_CALCULATOR = frozenset(
    {"colors", "shapes", "display", "orientation", "keypad"}
)
OFFLINE_FAST_SCOPES_DASHBOARD = frozenset(
    {"colors", "shapes", "display", "orientation"}
)

# Visual scopes where DELETE marks mean restyle (not DOM removal).
VISUAL_REDESIGN_SCOPES = frozenset(
    {"colors", "shapes", "display", "orientation", "keypad"}
)

_COLUMN_GOAL_RE = re.compile(
    r"\b("
    r"kolumn\w*|column\w*|"
    r"dwie\s+kolumny|two\s+columns?|"
    r"split|podziel\w*|"
    r"column\s+layout|two\s+column"
    r")\b",
    re.I,
)

_CONTENT_LAYOUT_SELECTORS = (
    ".entry-content",
    ".wp-block-kadence-rowlayout",
    ".kb-row-layout-wrap",
    "main",
    ".site-content",
    ".content-area",
    ".kt-row-column-wrap",
    ".wp-block-columns",
    ".hero-section",
    "section.hero",
)


def goal_requests_column_layout(user_goal: str) -> bool:
    """True when the user goal asks for a multi-column page layout."""
    text = (user_goal or "").strip()
    if not text:
        return False
    return bool(_COLUMN_GOAL_RE.search(text))

# Project kinds that must not receive full-page LLM regeneration when marks exist.
MARKED_PATCH_KINDS = frozenset(
    IMPORTED_KINDS
    | DASHBOARD_KINDS
    | frozenset({"web", "frontend"})
)


def ui_type_for_kind(kind: str, *, html_hint: str = "") -> str:
    k = (kind or "").strip().lower()
    if k in IMPORTED_KINDS:
        return "web"
    if k in DASHBOARD_KINDS:
        return "dashboard"
    if k == "calculator":
        return "calculator"
    text = re.sub(r"<script\b[^>]*>[\s\S]*?</script>", "", html_hint or "", flags=re.I).lower()
    if "calc-body" in text or "btn-eq" in text:
        return "calculator"
    if "app-shell" in text or "kpi-card" in text or "kpi-grid" in text:
        return "dashboard"
    return "web"


def allowed_scope_ids(project_kind: str) -> tuple[str, ...]:
    k = (project_kind or "").strip().lower()
    return SCOPE_IDS_BY_KIND.get(k, SCOPE_IDS_BY_KIND["web"])


def default_scope_for_kind(project_kind: str) -> str:
    k = (project_kind or "").strip().lower()
    ids = allowed_scope_ids(k)
    return DEFAULT_SCOPE_BY_KIND.get(k, ids[0] if ids else "functions")


def normalize_focus_scope(scope: str, project_kind: str) -> str:
    allowed = set(allowed_scope_ids(project_kind))
    s = (scope or "").strip().lower()
    if s in allowed:
        return s
    return default_scope_for_kind(project_kind)


def offline_fast_scopes_for_kind(project_kind: str) -> frozenset[str]:
    """Scopes that may use the offline A–C path on /iterate (not functions)."""
    k = (project_kind or "").strip().lower()
    if k in DASHBOARD_KINDS or k in IMPORTED_KINDS:
        return OFFLINE_FAST_SCOPES_DASHBOARD
    if k == "calculator":
        return OFFLINE_FAST_SCOPES_CALCULATOR
    return OFFLINE_FAST_SCOPES_DASHBOARD


def scope_supports_offline_fast_path(scope: str, project_kind: str) -> bool:
    """True when focus_scope can be patched locally without a full LLM HTML call."""
    normalized = normalize_focus_scope(scope, project_kind)
    return normalized in offline_fast_scopes_for_kind(project_kind)


def strip_scope_style(html: str) -> str:
    if not html:
        return html
    return re.sub(
        rf'<style\s+id="{SCOPE_STYLE_ID}"[^>]*>[\s\S]*?</style>\s*',
        "",
        html,
        flags=re.I,
    )


def _scope_css(scope: str, variant: str) -> str:
    """Dashboard/web-safe CSS patches for offline scope previews."""
    v = variant if variant in ("a", "b", "c") else "b"
    if scope == "colors":
        palettes = {
            "a": (
                ".app-shell,.dashboard-shell{background:#0b1224!important;}"
                ".kpi-card strong,.brand{color:#38bdf8!important;}"
                ".status-pill{background:rgba(56,189,248,0.18)!important;}"
            ),
            "b": (
                ".app-shell,.dashboard-shell{background:#020617!important;}"
                ".kpi-card,.chart-card,.table-card{border-color:rgba(248,250,252,0.35)!important;}"
                "h1,h2,.kpi-card strong{color:#f8fafc!important;}"
            ),
            "c": (
                ".app-shell,.dashboard-shell{background:#1e1033!important;}"
                ".kpi-card strong,.bar-chart span{background:linear-gradient(180deg,#a78bfa,#f472b6)!important;}"
                ".brand{color:#e879f9!important;}"
            ),
        }
        return palettes[v]
    if scope == "shapes":
        radii = {
            "a": (
                ".kpi-card,.chart-card,.table-card,.nav-item,button,[role='button']"
                "{border-radius:4px!important;}"
            ),
            "b": (
                ".kpi-card,.chart-card,.table-card,.nav-item,button,[role='button']"
                "{border-radius:10px!important;}"
            ),
            "c": (
                ".kpi-card,.chart-card,.table-card,.nav-item,button,[role='button']"
                "{border-radius:999px!important;}"
            ),
        }
        return radii[v]
    if scope == "display":
        scales = {
            "a": ".kpi-card strong{font-size:1rem!important;}.chart-card h2{font-size:0.8rem!important;}",
            "b": ".kpi-card strong{font-size:1.25rem!important;}.chart-card{min-height:140px!important;}",
            "c": (
                ".kpi-card strong{font-size:1.45rem!important;}"
                ".chart-card h2{font-size:1rem!important;}.bar-chart{height:180px!important;}"
            ),
        }
        return scales[v]
    if scope == "orientation":
        layouts = {
            "a": ".content-grid{grid-template-columns:1fr!important;}",
            "b": ".content-grid{grid-template-columns:minmax(0,1.6fr) minmax(200px,0.7fr)!important;}",
            "c": ".app-shell{grid-template-columns:140px 1fr!important;}.kpi-grid{grid-template-columns:repeat(2,1fr)!important;}",
        }
        return layouts[v]
    return ""


def _calc_scope_css(scope: str, variant: str) -> str:
    """Palette / layout overrides for calculator HTML (.calc-body, .screen, .btn-*)."""
    v = variant if variant in ("a", "b", "c") else "a"
    if scope == "colors":
        palettes = {
            "a": (
                "html,body{background:#0a1628!important;color:#e2e8f0!important;}"
                ".calc-body{background:#1e293b!important;border-color:#38bdf8!important;}"
                ".calc-title,.screen{color:#38bdf8!important;}"
                ".screen{background:#0f172a!important;}"
                ".btn{background:rgba(255,255,255,0.08)!important;color:#fff!important;}"
                ".btn-sci{background:#38bdf8!important;color:#0f172a!important;}"
                ".btn-chem{background:#34d399!important;color:#064e3b!important;}"
                ".btn-chem-heavy{background:#a78bfa!important;color:#1e1b4b!important;}"
                "[style*='e67e22']{background:#0ea5e9!important;}"
                "[style*='2ecc71']{background:#22c55e!important;}"
            ),
            "b": (
                "html,body{background:#000!important;color:#fff!important;}"
                ".calc-body{background:#111!important;border:2px solid #facc15!important;}"
                ".calc-title,.screen{color:#facc15!important;}"
                ".screen{background:#1a1a1a!important;}"
                ".btn{background:#262626!important;color:#fff!important;border:1px solid #525252!important;}"
                ".btn-sci{background:#facc15!important;color:#000!important;}"
                ".btn-chem{background:#fff!important;color:#000!important;}"
                ".btn-chem-heavy{background:#d4d4d4!important;color:#000!important;}"
                "[style*='e67e22']{background:#f97316!important;color:#000!important;}"
                "[style*='2ecc71']{background:#22c55e!important;color:#000!important;}"
            ),
            "c": (
                "html,body{background:linear-gradient(160deg,#1e1b4b,#831843)!important;color:#fce7f3!important;}"
                ".calc-body{background:rgba(30,27,75,0.85)!important;border-color:#f472b6!important;}"
                ".calc-title,.screen{color:#f9a8d4!important;}"
                ".screen{background:rgba(15,23,42,0.6)!important;}"
                ".btn{background:rgba(244,114,182,0.25)!important;color:#fff!important;}"
                ".btn-sci{background:#c084fc!important;color:#1e1b4b!important;}"
                ".btn-chem{background:#fb7185!important;color:#500724!important;}"
                ".btn-chem-heavy{background:#e879f9!important;color:#4a044e!important;}"
                "[style*='e67e22']{background:#f472b6!important;}"
                "[style*='2ecc71']{background:#a3e635!important;color:#14532d!important;}"
            ),
        }
        return palettes[v]
    if scope == "shapes":
        radii = {
            "a": ".calc-body{border-radius:8px!important;}.btn,.btn-sci,.btn-chem{border-radius:4px!important;}",
            "b": ".calc-body{border-radius:12px!important;}.btn,.btn-sci,.btn-chem{border-radius:8px!important;}",
            "c": ".calc-body{border-radius:20px!important;}.btn,.btn-sci,.btn-chem{border-radius:50%!important;}",
        }
        return radii[v]
    if scope == "display":
        sizes = {
            "a": ".screen{font-size:calc(6px + 1.2vh)!important;min-height:1.8em!important;}",
            "b": ".screen{font-size:calc(7px + 1.6vh)!important;min-height:2.2em!important;}",
            "c": ".screen{font-size:calc(9px + 2vh)!important;min-height:2.8em!important;font-weight:700!important;}",
        }
        return sizes[v]
    if scope == "orientation":
        layouts = {
            "a": ".calc-body{aspect-ratio:3/5!important;max-width:70vh!important;}",
            "b": ".calc-body{aspect-ratio:4/5!important;max-width:75vh!important;}",
            "c": ".calc-body{aspect-ratio:5/4!important;max-width:95vw!important;max-height:80vh!important;}",
        }
        return layouts[v]
    if scope == "keypad":
        gaps = {
            "a": ".grid{gap:4px!important;grid-template-columns:repeat(3,1fr)!important;}",
            "b": ".grid{gap:6px!important;grid-template-columns:repeat(4,1fr)!important;}",
            "c": ".grid{gap:8px!important;grid-template-columns:repeat(5,1fr)!important;}",
        }
        return gaps[v]
    return ""


def _uses_web_scope_css(inferred: str, html: str) -> bool:
    """True when inject_scope_style should use imported-web page-level CSS."""
    if inferred in IMPORTED_KINDS:
        return True
    lowered = (html or "").lower()
    if inferred == "calculator" or "calc-body" in lowered:
        return False
    if inferred in DASHBOARD_KINDS or "kpi-grid" in lowered:
        return False
    return True


def _web_display_scope_css(variant: str) -> str:
    """Typography on content regions for imported web HTML (not mark-narrowed)."""
    v = variant if variant in ("a", "b", "c") else "b"
    heads = ", ".join([*(f"{base} h1" for base in _CONTENT_LAYOUT_SELECTORS), "main h1", "h1"])
    h2s = ", ".join([*(f"{base} h2" for base in _CONTENT_LAYOUT_SELECTORS), "main h2", "h2"])
    ps = ", ".join([*(f"{base} p" for base in _CONTENT_LAYOUT_SELECTORS), "main p", "p"])
    scales = {
        "a": (
            f"{heads}{{font-size:1.35rem!important;}}"
            f"{h2s}{{font-size:1rem!important;}}"
            f"{ps}{{font-size:0.9rem!important;}}"
        ),
        "b": (
            f"{heads}{{font-size:1.65rem!important;}}"
            f"{h2s}{{font-size:1.15rem!important;}}"
            f"{ps}{{font-size:1rem!important;}}"
        ),
        "c": (
            f"{heads}{{font-size:1.9rem!important;font-weight:700!important;}}"
            f"{h2s}{{font-size:1.25rem!important;}}"
        ),
    }
    return scales[v]


def _web_shapes_scope_css(variant: str) -> str:
    """Corner radii on content wrappers and controls for imported web HTML."""
    v = variant if variant in ("a", "b", "c") else "b"
    wrapped_parts: list[str] = []
    for base in _CONTENT_LAYOUT_SELECTORS:
        wrapped_parts.extend(
            (
                f"{base} button",
                f"{base} [role='button']",
                f"{base} input",
                f"{base} section",
                f"{base} article",
            )
        )
    wrapped = ", ".join(wrapped_parts)
    global_targets = (
        "button,[role='button'],input,select,textarea,section,article,nav,header,footer"
    )
    radii = {
        "a": f"{wrapped},{global_targets}{{border-radius:4px!important;}}",
        "b": f"{wrapped},{global_targets}{{border-radius:10px!important;}}",
        "c": f"{wrapped},{global_targets}{{border-radius:999px!important;}}",
    }
    return radii[v]


def _web_orientation_scope_css(variant: str, *, user_goal: str = "") -> str:
    """WordPress/Kadence-aware layout patches for imported web HTML."""
    v = variant if variant in ("a", "b", "c") else "b"
    content = ", ".join(_CONTENT_LAYOUT_SELECTORS)
    column_goal = goal_requests_column_layout(user_goal)
    if v == "a":
        return (
            f"{content}{{display:flex!important;flex-direction:column!important;"
            f"gap:12px!important;}}"
            "body{display:flex!important;flex-direction:column!important;"
            "gap:12px!important;}"
        )
    if v == "b":
        cols = "1fr 1fr" if column_goal else "minmax(0,1fr) minmax(0,1fr)"
        return (
            f"{content}{{display:grid!important;grid-template-columns:{cols}!important;"
            f"gap:16px!important;align-items:start!important;}}"
            f"body{{display:grid!important;grid-template-columns:{cols}!important;"
            f"gap:16px!important;}}"
        )
    if column_goal:
        cols = "1fr 1.2fr"
        return (
            f"{content}{{display:grid!important;grid-template-columns:{cols}!important;"
            f"gap:14px!important;align-items:start!important;}}"
            f"@media(max-width:768px){{{content}{{grid-template-columns:1fr!important;"
            f"gap:12px!important;}}}}"
            "body{display:grid!important;grid-template-columns:1fr 1.2fr!important;"
            "gap:14px!important;}"
        )
    return (
        "main,section{display:grid!important;"
        "grid-template-columns:repeat(auto-fit,minmax(220px,1fr))!important;"
        "gap:14px!important;}"
    )


def _web_scope_css(scope: str, variant: str, *, user_goal: str = "") -> str:
    """Generic palette / layout patches for imported or arbitrary web HTML."""
    v = variant if variant in ("a", "b", "c") else "b"
    if scope == "colors":
        palettes = {
            "a": (
                "html,body{background:#0b1224!important;color:#e2e8f0!important;}"
                "a,button,[role='button']{color:#38bdf8!important;}"
                "h1,h2,h3,header,.brand{color:#38bdf8!important;}"
            ),
            "b": (
                "html,body{background:#020617!important;color:#f8fafc!important;}"
                "a,button,[role='button']{color:#facc15!important;}"
                "h1,h2,h3,header{border-color:rgba(248,250,252,0.35)!important;}"
            ),
            "c": (
                "html,body{background:linear-gradient(160deg,#1e1033,#312e81)!important;color:#fce7f3!important;}"
                "a,button,[role='button']{color:#e879f9!important;}"
                "h1,h2,h3,header{color:#f9a8d4!important;}"
            ),
        }
        return palettes[v]
    if scope == "shapes":
        return _web_shapes_scope_css(v)
    if scope == "display":
        return _web_display_scope_css(v)
    if scope == "orientation":
        return _web_orientation_scope_css(v, user_goal=user_goal)
    return ""


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
    
    matches = list(_TAG_OPEN_RE.finditer(text))
    matched_ranges: list[tuple[int, int, str]] = []
    seen_elements = set()
    
    for match in matches:
        tag = match.group(1).lower()
        if tag in ("html", "head", "body", "style", "script", "link", "meta"):
            continue
        attrs_text = match.group(2)
        attrs = _parse_attrs(attrs_text)
        
        raw_id = str(attrs.get("id") or "").strip()
        candidates = _id_candidates(raw_id) if raw_id else set()
        target = str(attrs.get("data-nexu-target") or "").strip()
        if target:
            candidates |= _id_candidates(target)
        logical = _logical_id(tag, attrs)
        if logical:
            candidates |= _id_candidates(logical)
            
        hit = wanted & candidates
        if not hit and tag not in ("html", "head", "body", "style", "script", "link", "meta"):
            if raw_id or target:
                continue
            inner_start = match.end()
            inner_end = text.lower().find(f"</{tag}>", inner_start)
            if inner_end >= 0:
                inner_content = text[inner_start:inner_end]
                label = re.sub(r"<[^>]+>", "", inner_content)
                label = re.sub(r"\s+", " ", label).strip()
                logical = _logical_id(tag, attrs, text=label)
                if logical:
                    hit = wanted & _id_candidates(logical)
                    
        if not hit:
            continue
            
        matched_id = list(hit)[0]
        if matched_id in seen_elements:
            continue
        seen_elements.add(matched_id)
        
        if "data-nexu-target" in attrs:
            continue
            
        new_tag = f"<{tag} data-nexu-target=\"{matched_id}\" {attrs_text}>"
        matched_ranges.append((match.start(), match.end(), new_tag))
        
    if not matched_ranges:
        return html
        
    parts: list[str] = []
    last_idx = 0
    for start, end, replacement in matched_ranges:
        parts.append(text[last_idx:start])
        parts.append(replacement)
        last_idx = end
    parts.append(text[last_idx:])
    return "".join(parts)


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


def _inject_css_block(html: str, css: str) -> str:
    if not css:
        return html
    block = f'<style id="{SCOPE_STYLE_ID}">\n{css}\n</style>'
    lower = html.lower()
    if "</head>" in lower:
        idx = lower.rfind("</head>")
        return html[:idx] + block + html[idx:]
    if "<body" in lower:
        match = re.search(r"<body[^>]*>", html, flags=re.I)
        if match:
            pos = match.start()
            return html[:pos] + block + html[pos:]
    return block + html


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
        selectors = resolve_marked_selectors(
            cleaned,
            effective_delete,
            keep_ids=keep_list,
            narrow=(scope == "colors"),
        )
        if scope == "colors" and selectors:
            css = marked_scope_colors_css(selectors, variant)
        elif scope == "orientation" and selectors:
            css = marked_scope_orientation_css(selectors, variant)
            if _uses_web_scope_css(inferred, cleaned) and goal_requests_column_layout(
                user_goal
            ):
                page_css = _web_orientation_scope_css(variant, user_goal=user_goal)
                if page_css:
                    css = f"{page_css}\n{css}"
        elif scope == "display" and selectors and _uses_web_scope_css(inferred, cleaned):
            css = _web_display_scope_css(variant)
            extra = marked_scope_display_css(selectors, variant)
            if extra:
                css = f"{css}\n{extra}"
        elif scope == "shapes" and selectors and _uses_web_scope_css(inferred, cleaned):
            css = _web_shapes_scope_css(variant)
            extra = marked_scope_shapes_css(selectors, variant)
            if extra:
                css = f"{css}\n{extra}"
        else:
            css = restrict_scope_css_to_marks(
                css,
                effective_delete,
                html=cleaned,
                keep_ids=keep_list,
            )
    return _inject_css_block(cleaned, css)


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
        match = re.search(pattern, text, flags=re.I)
        if match and len(match.group(1)) >= 40:
            return (
                f"<!-- scoped DOM fragment for #{scope}; regenerate full page from baseline -->\n"
                + match.group(1)
            )
    return None
