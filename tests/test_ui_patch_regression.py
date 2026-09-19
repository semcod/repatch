"""Focused regression tests for the ui_patch workflow split.

These pin the stable responsibilities of ``repatch.ui_patch`` (prompt
construction, response parsing, CSS validation, and patch application) so the
module can be split into cohesive submodules without changing behaviour.
"""

from __future__ import annotations

import pytest

from repatch._ui_patch_apply import _css_for, _label_for, _safe_css
from repatch._ui_patch_parse import _strip_json_fence
from repatch._ui_patch_prompt import _compact_html, _patch_scope_rules
from repatch.ui_patch import (
    apply_ui_patch_options,
    build_ui_patch_prompt,
    parse_ui_patch_response,
    supports_llm_patch_scope,
)

VARIANTS = [
    ("alt_a.html", "Option A", "cool"),
    ("alt_b.html", "Option B", "contrast"),
    ("alt_c.html", "Option C", "expressive"),
]

BODY_HTML = "<!DOCTYPE html><html><body><div id=\"screen\">0</div></body></html>"


# --- prompt construction -----------------------------------------------------


def test_compact_html_returns_short_text_whitespace_collapsed() -> None:
    assert _compact_html("  <div>  a  </div>  ") == "<div> a </div>"


def test_compact_html_truncates_long_text_with_marker() -> None:
    result = _compact_html("x" * 7000, limit=100)
    assert "middle omitted for compact LLM patch prompt" in result
    assert len(result) < 7000


def test_patch_scope_rules_functions_scope() -> None:
    rules = _patch_scope_rules("functions")
    assert any("must be removed or fully redesigned" in r for r in rules)
    assert any("KEEP-marked elements are mandatory" in r for r in rules)


def test_patch_scope_rules_visual_scope_targets_delete_marks() -> None:
    rules = _patch_scope_rules("colors")
    assert any("primarily to DELETE-marked elements" in r for r in rules)
    assert any("hard constraints" in r for r in rules)


def test_patch_scope_rules_default_scope() -> None:
    rules = _patch_scope_rules("bogus")
    assert any("primary redesign targets" in r for r in rules)


def test_patch_scope_rules_appends_keep_and_delete_ids() -> None:
    rules = _patch_scope_rules("colors", keep_els=["a", "b"], delete_els=["c"])
    assert "KEEP ids: a, b." in rules
    assert "DELETE ids: c." in rules


def test_supports_llm_patch_scope_functions_with_marks_is_blocked() -> None:
    assert supports_llm_patch_scope("functions", "imported", has_marks=True) is False
    assert supports_llm_patch_scope("colors", "imported", has_marks=True) is True


def test_build_ui_patch_prompt_filters_non_alt_variants() -> None:
    variants = VARIANTS + [("alt_d.html", "Option D", "extra")]
    prompt = build_ui_patch_prompt(
        BODY_HTML,
        focus_scope="colors",
        project_kind="calculator",
        option_variants=variants,
    )
    assert '"alt_d.html"' not in prompt
    assert '"alt_c.html"' in prompt


def test_build_ui_patch_prompt_uses_supplied_context_fragment() -> None:
    fragment = "<!-- scoped DOM fragment --><div>x</div>"
    prompt = build_ui_patch_prompt(
        BODY_HTML,
        focus_scope="colors",
        project_kind="calculator",
        option_variants=VARIANTS,
        context_fragment=fragment,
    )
    assert fragment in prompt


# --- response parsing --------------------------------------------------------


def test_strip_json_fence_removes_fence() -> None:
    assert _strip_json_fence("```json\n{\"a\": 1}\n```") == "{\"a\": 1}"


def test_strip_json_fence_uppercase_and_bare() -> None:
    assert _strip_json_fence("```JSON\n{\"a\": 1}\n```") == "{\"a\": 1}"
    assert _strip_json_fence("  {\"a\": 1}  ") == "{\"a\": 1}"


def test_parse_ui_patch_response_extracts_embedded_json() -> None:
    data = parse_ui_patch_response(
        'Here is the result {"variants": {"alt_a.html": {"css": ".x{color:red}"}}} thanks'
    )
    assert data["variants"]["alt_a.html"]["css"] == ".x{color:red}"


def test_parse_ui_patch_response_rejects_missing_json_object() -> None:
    with pytest.raises(ValueError, match="did not contain a JSON object"):
        parse_ui_patch_response("no braces here")


def test_parse_ui_patch_response_rejects_non_object_root() -> None:
    with pytest.raises(ValueError, match="root must be an object"):
        parse_ui_patch_response("[1, 2, 3]")


def test_parse_ui_patch_response_rejects_missing_variants() -> None:
    with pytest.raises(ValueError, match="must contain variants"):
        parse_ui_patch_response("{\"alt_a.html\": {}}")


# --- CSS validation ----------------------------------------------------------


def test_safe_css_rejects_empty() -> None:
    with pytest.raises(ValueError, match="empty CSS patch"):
        _safe_css("")
    with pytest.raises(ValueError, match="empty CSS patch"):
        _safe_css("   ")


def test_safe_css_rejects_oversized() -> None:
    with pytest.raises(ValueError, match="too large"):
        _safe_css("a" * 5001)


def test_safe_css_rejects_unsafe_token() -> None:
    with pytest.raises(ValueError, match="unsafe CSS token"):
        _safe_css(".x{background:url(https://example.test/a.png);}")


def test_safe_css_rejects_missing_braces() -> None:
    with pytest.raises(ValueError, match="must contain CSS rules"):
        _safe_css("color:red")


def test_safe_css_accepts_valid_rule() -> None:
    assert _safe_css(".x{color:red;}") == ".x{color:red;}"


def test_css_for_accepts_dict_and_string() -> None:
    assert _css_for({"css": ".x{color:red;}"}) == ".x{color:red;}"
    assert _css_for(".x{color:blue;}") == ".x{color:blue;}"


# --- patch application -------------------------------------------------------


def test_label_for_uses_item_label() -> None:
    fallback = {"alt_a.html": "Fallback A"}
    assert _label_for("alt_a.html", {"label": "Real A"}, fallback) == "Real A"


def test_label_for_falls_back_when_label_missing() -> None:
    fallback = {"alt_a.html": "Fallback A"}
    assert _label_for("alt_a.html", {"label": "  "}, fallback) == "Fallback A"
    assert _label_for("alt_a.html", "not-a-dict", fallback) == "Fallback A"
    assert _label_for("alt_x.html", {}, {}) == "alt_x.html"


def test_label_for_truncates_long_label() -> None:
    assert _label_for("alt_a.html", {"label": "x" * 200}, {}) == "x" * 120


def test_apply_ui_patch_injects_before_body_without_head() -> None:
    patch = {
        "variants": {
            "alt_a.html": {"label": "A", "css": ".screen{color:#38bdf8;}"},
            "alt_b.html": {"label": "B", "css": ".screen{color:#fff;}"},
            "alt_c.html": {"label": "C", "css": ".screen{color:#f47;}"},
        }
    }
    files, _ = apply_ui_patch_options(BODY_HTML, patch, option_variants=VARIANTS)
    out = files["alt_a.html"]
    assert out.index('id="nexu-scope-variant"') < out.index("<body")
    assert ".screen{color:#38bdf8;}" in out


def test_apply_ui_patch_prepends_when_no_head_or_body() -> None:
    patch = {
        "variants": {
            "alt_a.html": {"css": ".x{color:red;}"},
            "alt_b.html": {"css": ".x{color:red;}"},
            "alt_c.html": {"css": ".x{color:red;}"},
        }
    }
    files, _ = apply_ui_patch_options("<div>x</div>", patch, option_variants=VARIANTS)
    assert files["alt_a.html"].startswith('<style id="nexu-scope-variant">')


def test_apply_ui_patch_rejects_missing_variant_file() -> None:
    patch = {"variants": {"alt_a.html": {"css": ".x{color:red;}"}}}
    with pytest.raises(ValueError, match="missing alt_b.html"):
        apply_ui_patch_options(BODY_HTML, patch, option_variants=VARIANTS)
