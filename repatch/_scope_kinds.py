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
    text = re.sub(r"<script\b[^>]*>[\s\S]*?</script>", "", html_hint or "", flags=re.IGNORECASE).lower()
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
    effective_scope = normalize_focus_scope(scope, project_kind)
    return effective_scope in offline_fast_scopes_for_kind(project_kind)
