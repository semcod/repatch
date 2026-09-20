from __future__ import annotations

from repatch._scope_css import (
    _calc_scope_css,
    _scope_css,
    _uses_web_scope_css,
    _web_display_scope_css,
    _web_orientation_scope_css,
    _web_scope_css,
    _web_shapes_scope_css,
)
from repatch._scope_kinds import (
    OFFLINE_FAST_SCOPES_CALCULATOR,
    OFFLINE_FAST_SCOPES_DASHBOARD,
)
from repatch.scope import (
    DASHBOARD_KINDS,
    IMPORTED_KINDS,
    MARKED_PATCH_KINDS,
    SCOPE_STYLE_ID,
    VISUAL_REDESIGN_SCOPES,
    _bind_annotations_to_html,
    _inject_css_block,
    _resolve_scope_kind,
    allowed_scope_ids,
    default_scope_for_kind,
    effective_focus_scope,
    goal_requests_column_layout,
    inject_scope_style,
    normalize_focus_scope,
    offline_fast_scopes_for_kind,
    scope_supports_offline_fast_path,
    scoped_html_fragment,
    should_block_full_html_iterate,
    strip_scope_style,
    ui_type_for_kind,
)


def test_goal_requests_column_layout_detects_column_goal() -> None:
    assert goal_requests_column_layout("split the page into two columns") is True
    assert goal_requests_column_layout("dwie kolumny") is True


def test_goal_requests_column_layout_rejects_empty_goal() -> None:
    assert goal_requests_column_layout("") is False
    assert goal_requests_column_layout("   ") is False


def test_ui_type_for_kind_maps_known_kinds() -> None:
    assert ui_type_for_kind("dashboard") == "dashboard"
    assert ui_type_for_kind("imported") == "web"
    assert ui_type_for_kind("calculator") == "calculator"
    assert ui_type_for_kind("unknown") == "web"


def test_ui_type_for_kind_detects_from_html_hint() -> None:
    assert ui_type_for_kind("", html_hint="<div class='calc-body'></div>") == "calculator"
    assert ui_type_for_kind("", html_hint="<div class='app-shell'></div>") == "dashboard"


def test_allowed_scope_ids_and_defaults() -> None:
    assert allowed_scope_ids("dashboard") == (
        "functions",
        "display",
        "colors",
        "shapes",
        "orientation",
    )
    assert allowed_scope_ids("unknown") == allowed_scope_ids("web")
    assert default_scope_for_kind("calculator") == "keypad"
    assert default_scope_for_kind("dashboard") == "functions"
    assert default_scope_for_kind("unknown") == "functions"


def test_normalize_focus_scope_accepts_valid_and_defaults_invalid() -> None:
    assert normalize_focus_scope("colors", "dashboard") == "colors"
    assert normalize_focus_scope("keypad", "calculator") == "keypad"
    assert normalize_focus_scope("bogus", "dashboard") == "functions"


def test_effective_focus_scope_is_single_owner_of_request_scope_resolution() -> None:
    assert effective_focus_scope("colors", "dashboard") == "colors"
    assert effective_focus_scope("bogus", "dashboard") == "functions"
    assert effective_focus_scope("", "calculator") == "keypad"


def test_effective_focus_scope_can_preserve_unset_scope() -> None:
    assert effective_focus_scope("", "calculator", default_when_unset=False) == ""
    assert effective_focus_scope(None, "calculator", default_when_unset=False) == ""
    assert effective_focus_scope("  ", "calculator", default_when_unset=False) == "keypad"


def test_offline_fast_scopes_by_kind() -> None:
    assert offline_fast_scopes_for_kind("calculator") == OFFLINE_FAST_SCOPES_CALCULATOR
    assert offline_fast_scopes_for_kind("dashboard") == OFFLINE_FAST_SCOPES_DASHBOARD
    assert "keypad" in OFFLINE_FAST_SCOPES_CALCULATOR
    assert "keypad" not in OFFLINE_FAST_SCOPES_DASHBOARD


def test_scope_supports_offline_fast_path() -> None:
    assert scope_supports_offline_fast_path("colors", "dashboard") is True
    assert scope_supports_offline_fast_path("functions", "dashboard") is False


def test_strip_scope_style_removes_injected_block() -> None:
    assert strip_scope_style("") == ""
    assert strip_scope_style("no style here") == "no style here"
    html = f'abc<style id="{SCOPE_STYLE_ID}">.x{{}}</style>def'
    assert strip_scope_style(html) == "abcdef"


def test_scope_css_returns_palette_and_defaults_variant() -> None:
    assert "background:#0b1224" in _scope_css("colors", "a")
    assert "background:#020617" in _scope_css("colors", "z")
    assert _scope_css("unknown", "a") == ""


def test_calc_scope_css_returns_calculator_overrides() -> None:
    assert ".calc-body" in _calc_scope_css("colors", "a")
    assert "repeat(3,1fr)" in _calc_scope_css("keypad", "a")
    assert _calc_scope_css("unknown", "a") == ""


def test_web_scope_css_dispatch() -> None:
    assert "html,body" in _web_scope_css("colors", "a")
    assert "border-radius:4px" in _web_scope_css("shapes", "a")
    assert _web_scope_css("keypad", "a") == ""


def test_web_scope_css_helpers_emit_selectors() -> None:
    assert "h1" in _web_display_scope_css("a")
    assert "border-radius:4px" in _web_shapes_scope_css("a")
    assert "grid-template-columns" in _web_orientation_scope_css("b")


def test_uses_web_scope_css_classification() -> None:
    assert _uses_web_scope_css("imported", "<p></p>") is True
    assert _uses_web_scope_css("calculator", "<p></p>") is False
    assert _uses_web_scope_css("dashboard", "<p></p>") is False
    assert _uses_web_scope_css("web", "<p></p>") is True


def test_resolve_scope_kind_from_kind_and_html() -> None:
    assert _resolve_scope_kind("dashboard", "<p></p>") == "dashboard"
    assert _resolve_scope_kind("", "<div class='calc-body'></div>") == "calculator"
    assert _resolve_scope_kind("", "<div class='kpi-grid'></div>") == "dashboard"
    assert _resolve_scope_kind("", "<p></p>") == "web"


def test_should_block_full_html_iterate_requires_marks() -> None:
    assert should_block_full_html_iterate("dashboard", ["a"], None) is True
    assert should_block_full_html_iterate("dashboard", None, None) is False
    assert should_block_full_html_iterate("calculator", ["a"], None) is False


def test_bind_annotations_to_html_tags_matching_ids() -> None:
    html = '<div id="hero"><p>Title</p></div>'
    out = _bind_annotations_to_html(html, ["hero"], None)
    assert 'data-nexu-target="hero"' in out


def test_bind_annotations_to_html_noop_without_marks() -> None:
    html = '<div id="hero"><p>Title</p></div>'
    assert _bind_annotations_to_html(html, None, None) == html


def test_inject_css_block_into_head() -> None:
    out = _inject_css_block("<html><head></head><body></body></html>", "x{}")
    assert out == '<html><head><style id="nexu-scope-variant">\nx{}\n</style></head><body></body></html>'


def test_inject_css_block_prepends_when_no_head_or_body() -> None:
    assert _inject_css_block("<p>x</p>", "y{}") == '<style id="nexu-scope-variant">\ny{}\n</style><p>x</p>'


def test_inject_css_block_skips_empty_css() -> None:
    assert _inject_css_block("<p>x</p>", "") == "<p>x</p>"


def test_inject_scope_style_builds_dashboard_palette() -> None:
    out = inject_scope_style(
        '<div class="app-shell"></div>', "colors", "a", project_kind="dashboard"
    )
    assert out.startswith('<style id="nexu-scope-variant">')
    assert "background:#0b1224" in out


def test_scoped_html_fragment_returns_visual_fragment() -> None:
    html = '<div class="calc-body"><div class="screen">0</div></div>'
    fragment = scoped_html_fragment(html, "colors", "calculator")
    assert fragment is not None
    assert fragment.startswith("<!-- scoped DOM fragment for #colors")


def test_scoped_html_fragment_none_for_non_fast_scope() -> None:
    html = '<div class="calc-body"><div class="screen">0</div></div>'
    assert scoped_html_fragment(html, "functions", "dashboard") is None


def test_public_constants_remain_importable() -> None:
    assert DASHBOARD_KINDS
    assert IMPORTED_KINDS
    assert MARKED_PATCH_KINDS
    assert VISUAL_REDESIGN_SCOPES
    assert SCOPE_STYLE_ID == "nexu-scope-variant"
