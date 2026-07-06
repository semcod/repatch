"""Focused regression tests for ``marked_context`` internals.

These pin the behavior of the lower-level helpers (id normalization, HTML
subtree extraction, CSS token filtering, scope semantics, per-scope variant
CSS, and byte capping) that the higher-level public-function tests exercise
only indirectly. They were added before splitting the module into submodules
(ticket PLF-004) so the extraction can be verified behavior-preserving.

Symbols are imported from ``repatch.marked_context`` (the package) on purpose:
``repatch/scope.py`` depends on several of these private helpers, so the
re-export surface itself is part of the contract under test.
"""

from __future__ import annotations

from repatch.marked_context import (
    MAX_FRAGMENT_BYTES,
    _cap_text,
    _filter_css_for_tokens,
    _find_marked_subtrees,
    _id_candidates,
    _logical_id,
    _normalize_label_text,
    _scope_semantics,
    effective_delete_ids,
    has_ui_marks,
    marked_css_selectors,
    marked_scope_colors_css,
    marked_scope_display_css,
    marked_scope_orientation_css,
    marked_scope_shapes_css,
    resolve_marked_selectors,
    restrict_scope_css_to_marks,
)

# ---------------------------------------------------------------------------
# effective_delete_ids — KEEP overrides DELETE, btn- prefix in both directions
# ---------------------------------------------------------------------------


def test_effective_delete_ids_drops_keep_overrides() -> None:
    # keep btn-7 -> kept set is {"7", "btn-7"}; "7" and "btn-7" filtered, others kept.
    assert effective_delete_ids(["btn-tan", "7", "other"], ["btn-7"]) == ["btn-tan", "other"]


def test_effective_delete_ids_unprefixed_keep_blocks_prefixed_delete() -> None:
    # keep "tan" -> kept {"tan", "btn-tan"}; both delete forms filtered.
    assert effective_delete_ids(["btn-tan", "tan", "x"], ["tan"]) == ["x"]


def test_effective_delete_ids_preserves_input_order_and_strips() -> None:
    assert effective_delete_ids([" foo ", "bar", "  "], []) == ["foo", "bar"]


def test_effective_delete_ids_empty_inputs() -> None:
    assert effective_delete_ids([], ["x"]) == []
    assert effective_delete_ids(["x"], []) == ["x"]


# ---------------------------------------------------------------------------
# _id_candidates — btn- prefix expansion
# ---------------------------------------------------------------------------


def test_id_candidates_expands_btn_prefix() -> None:
    assert _id_candidates("btn-tan") == {"btn-tan", "tan"}


def test_id_candidates_adds_btn_prefix_when_absent() -> None:
    assert _id_candidates("7") == {"7", "btn-7"}


def test_id_candidates_empty() -> None:
    assert _id_candidates("") == set()
    assert _id_candidates(None) == set()  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# _normalize_label_text — entity/whitespace normalization
# ---------------------------------------------------------------------------


def test_normalize_label_text_collapses_nbsp_and_whitespace() -> None:
    assert _normalize_label_text("a&nbsp;b") == "a b"
    assert _normalize_label_text("  a   b  ") == "a b"


def test_normalize_label_text_unescapes_entities() -> None:
    assert _normalize_label_text("x&amp;y&lt;z") == "x&y<z"


# ---------------------------------------------------------------------------
# _logical_id — id > data-nexu-target > visible-text-label fallback
# ---------------------------------------------------------------------------


def test_logical_id_prefers_id_stripping_btn_prefix() -> None:
    assert _logical_id("div", {"id": "btn-foo"}) == "foo"
    assert _logical_id("div", {"id": "bar"}) == "bar"


def test_logical_id_uses_data_nexu_target_when_no_id() -> None:
    assert _logical_id("div", {"data-nexu-target": "tgt"}) == "tgt"


def test_logical_id_falls_back_to_visible_text_for_label_tags() -> None:
    assert _logical_id("button", {}, text="Save") == "Save"
    assert _logical_id("span", {}, text="hi") == "hi"


def test_logical_id_returns_none_without_any_signal() -> None:
    assert _logical_id("div", {}, text="") is None
    # "html" is not a text-label tag, so text is ignored.
    assert _logical_id("html", {}, text="hi") is None


# ---------------------------------------------------------------------------
# _find_marked_subtrees / _extract_balanced_html — extraction edge cases
# ---------------------------------------------------------------------------


def test_find_marked_subtrees_preserves_original_tag_case() -> None:
    out = _find_marked_subtrees('<DIV id="a">x</DIV>', {"a"})
    assert out == {"a": '<DIV id="a">x</DIV>'}


def test_find_marked_subtrees_balances_nested_same_tag() -> None:
    html = '<div id="a"><div>y</div></div>'
    assert _find_marked_subtrees(html, {"a"}) == {"a": html}


def test_find_marked_subtrees_handles_void_and_self_closing() -> None:
    assert _find_marked_subtrees('<img id="a">', {"a"}) == {"a": '<img id="a">'}
    assert _find_marked_subtrees('<input id="a"/>', {"a"}) == {"a": '<input id="a"/>'}


def test_find_marked_subtrees_matches_data_nexu_target() -> None:
    html = '<div data-nexu-target="tgt">x</div>'
    assert _find_marked_subtrees(html, {"tgt"}) == {"tgt": html}


def test_find_marked_subtrees_button_text_label_fallback() -> None:
    html = "<button>Submit</button>"
    assert _find_marked_subtrees(html, {"Submit"}) == {"Submit": html}


def test_find_marked_subtrees_misses_non_matching_ids() -> None:
    assert _find_marked_subtrees('<div id="b">x</div>', {"a"}) == {}
    assert _find_marked_subtrees('<div id="a">x</div>', set()) == {}


def test_find_marked_subtrees_truncates_oversized_fragment() -> None:
    html = '<div id="a">' + ("x" * (MAX_FRAGMENT_BYTES + 500)) + "</div>"
    out = _find_marked_subtrees(html, {"a"})
    assert "a" in out
    assert out["a"].endswith("<!-- truncated -->")
    assert len(out["a"].encode("utf-8")) <= MAX_FRAGMENT_BYTES


# ---------------------------------------------------------------------------
# _cap_text — byte-aware truncation that must not split multibyte sequences
# ---------------------------------------------------------------------------


def test_cap_text_short_passthrough() -> None:
    assert _cap_text("short", 100) == "short"


def test_cap_text_ascii_boundary() -> None:
    # limit - 48 = 2 bytes kept, then the truncation marker.
    out = _cap_text("x" * 100, 50)
    assert out == "xx\n<!-- nexu: marked context truncated -->"


def test_cap_text_multibyte_safe_decode() -> None:
    # limit - 48 = 3 bytes; "é" is 2 bytes so the slice splits a char — must not raise.
    out = _cap_text("é" * 100, 51)
    assert out.endswith("<!-- nexu: marked context truncated -->")


# ---------------------------------------------------------------------------
# _filter_css_for_tokens — keep only rules whose selector matches a token
# ---------------------------------------------------------------------------


def test_filter_css_for_tokens_keeps_matching_only() -> None:
    css = "#a{color:red}\n.b{x:1}"
    assert _filter_css_for_tokens(css, {"#a"}) == "#a{color:red}"


def test_filter_css_for_tokens_empty_inputs() -> None:
    assert _filter_css_for_tokens("", {"#a"}) == ""
    assert _filter_css_for_tokens("#a{x}", set()) == ""


# ---------------------------------------------------------------------------
# _scope_semantics — functions / visual / default branches
# ---------------------------------------------------------------------------


def test_scope_semantics_functions_branch() -> None:
    lines = _scope_semantics("functions")
    assert any("must be removed or fully redesigned" in line for line in lines)


def test_scope_semantics_visual_scopes_named() -> None:
    assert "Apply #colors changes" in _scope_semantics("colors")[0]
    assert "Apply #shapes changes" in _scope_semantics("shapes")[0]


def test_scope_semantics_default_branch() -> None:
    assert "primary redesign targets" in _scope_semantics("")[0]
    assert "primary redesign targets" in _scope_semantics("unknown-scope")[0]


# ---------------------------------------------------------------------------
# per-scope variant CSS builders (non-colors scopes)
# ---------------------------------------------------------------------------


def test_marked_scope_display_css_variants() -> None:
    a = marked_scope_display_css([".a", ".b"], "a")
    c = marked_scope_display_css([".a"], "c")
    invalid = marked_scope_display_css([".a"], "z")  # falls back to "b"
    assert ".a, .b {" in a and "font-size:1.1rem" in a
    assert "font-size:1.35rem" in c and "font-weight:600" in c
    assert "font-size:1.2rem" in invalid


def test_marked_scope_shapes_css_caps_to_eight_selectors() -> None:
    many = marked_scope_shapes_css([f".s{i}" for i in range(10)], "c")
    assert "border-radius:999px" in many
    assert ".s0" in many and ".s7" in many
    assert ".s8" not in many


def test_marked_scope_shapes_css_invalid_variant_defaults_b() -> None:
    assert "border-radius:12px" in marked_scope_shapes_css([".x"], "nope")


def test_marked_scope_orientation_css_emits_has_selector() -> None:
    css = marked_scope_orientation_css([".a"], "b")
    assert "grid-template-columns:1fr 1fr" in css
    assert ":has(" in css
    assert "max-width:1180px" in css
    assert marked_scope_orientation_css([], "b") == ""


def test_marked_scope_colors_css_empty_and_invalid() -> None:
    assert marked_scope_colors_css([], "a") == ""
    assert marked_scope_colors_css([".x"], "zzz")  # invalid variant -> "b" decl, non-empty
    assert "background-color:#facc15" in marked_scope_colors_css([".x"], "zzz")


# ---------------------------------------------------------------------------
# marked_css_selectors / resolve_marked_selectors — dedup & guard clauses
# ---------------------------------------------------------------------------


def test_marked_css_selectors_dedups_repeated_ids() -> None:
    selectors = marked_css_selectors(["tan", "tan"])
    assert selectors == list(dict.fromkeys(selectors))  # no duplicates, order stable
    assert "#tan" in selectors and "#btn-tan" in selectors


def test_resolve_marked_selectors_empty_delete_returns_empty() -> None:
    assert resolve_marked_selectors("<html>x</html>", []) == []


def test_resolve_marked_selectors_falls_back_to_id_selectors_without_html_match() -> None:
    selectors = resolve_marked_selectors("no markup here", ["foo"])
    assert "#foo" in selectors and "#btn-foo" in selectors


# ---------------------------------------------------------------------------
# restrict_scope_css_to_marks — drops page-wide rules, keeps marked decls
# ---------------------------------------------------------------------------


def test_restrict_scope_css_no_delete_returns_input_unchanged() -> None:
    assert restrict_scope_css_to_marks("body{x:1}", []) == "body{x:1}"


def test_restrict_scope_css_drops_html_body_keeps_marked_decls() -> None:
    css = "html{a:1}body{b:2}.x{color:blue}"
    scoped = restrict_scope_css_to_marks(css, ["x"])
    assert "color:blue" in scoped
    assert "#x" in scoped
    assert "html{" not in scoped and "body{" not in scoped


# ---------------------------------------------------------------------------
# has_ui_marks — whitespace handling
# ---------------------------------------------------------------------------


def test_has_ui_marks_ignores_whitespace_only_entries() -> None:
    assert has_ui_marks(["  "], []) is False
    assert has_ui_marks([], ["\t"]) is False
