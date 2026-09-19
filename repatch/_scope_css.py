"""CSS generation for offline scope previews and marked-scope restriction."""

from __future__ import annotations

import re

from ._scope_kinds import (
    DASHBOARD_KINDS,
    IMPORTED_KINDS,
    goal_requests_column_layout,
)

SCOPE_STYLE_ID = "nexu-scope-variant"

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


def strip_scope_style(html: str) -> str:
    if not html:
        return html
    return re.sub(
        rf'<style\s+id="{SCOPE_STYLE_ID}"[^>]*>[\s\S]*?</style>\s*',
        "",
        html,
        flags=re.IGNORECASE,
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
