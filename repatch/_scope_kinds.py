"""Scope registry and project-kind classification."""

from __future__ import annotations

import re

DASHBOARD_KINDS = frozenset(
    {"dashboard", "monitor", "ecosystem", "api", "mcp", "frontend", "slice"}
)

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
    re.IGNORECASE,
)


def goal_requests_column_layout(user_goal: str) -> bool:
    """True when the user goal asks for a multi-column page layout."""
    goal_query = (user_goal or "").strip()
    if not goal_query:
        return False
    return bool(_COLUMN_GOAL_RE.search(goal_query))


def normalize_scope_variant(variant: str, *, default: str = "b") -> str:
    """Single owner of offline A-C variant-letter normalization.

    Every scope-CSS builder routes its ``variant`` through this helper
    instead of re-deriving the a/b/c letter locally (calculator previews
    default to "a", everything else to "b").
    """
    return variant if variant in ("a", "b", "c") else default


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
    markup_hint = re.sub(r"<script\b[^>]*>[\s\S]*?</script>", "", html_hint or "", flags=re.IGNORECASE).lower()
    if "calc-body" in markup_hint or "btn-eq" in markup_hint:
        return "calculator"
    if "app-shell" in markup_hint or "kpi-card" in markup_hint or "kpi-grid" in markup_hint:
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


def effective_focus_scope(
    focus_scope: str,
    project_kind: str,
    *,
    default_when_unset: bool = True,
) -> str:
    """Single owner of request-level focus-scope resolution.

    Every pipeline stage (prompt build, patch apply, scope CSS injection,
    fragment extraction) resolves its effective scope here instead of
    re-deriving it locally. With ``default_when_unset=False`` an unset
    focus scope stays empty instead of falling back to the kind default.
    """
    if not focus_scope and not default_when_unset:
        return ""
    return normalize_focus_scope(focus_scope, project_kind)


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
    effective_scope = effective_focus_scope(scope, project_kind)
    return effective_scope in offline_fast_scopes_for_kind(project_kind)
