"""Tests for marked-element LLM context compaction."""

from __future__ import annotations

from repatch import (
    build_marked_element_context,
    has_ui_marks,
    inject_scope_style,
    marked_css_selectors,
    marked_scope_colors_css,
    resolve_marked_llm_context,
    resolve_marked_selectors,
    restrict_scope_css_to_marks,
    should_block_full_html_iterate,
)
from repatch.ui_patch import build_ui_patch_prompt

CALC_HTML = """<!DOCTYPE html>
<html>
<head>
  <style>
    #btn-7 { background: #334155; color: #fff; border-radius: 8px; }
    #btn-tan { background: #0ea5e9; color: #fff; }
    .btn-op { min-width: 48px; }
  </style>
</head>
<body>
  <div class="calc-body">
    <button class="btn btn-op" id="btn-7">7</button>
    <button class="btn btn-op" id="btn-tan">tan</button>
  </div>
</body>
</html>
"""

VARIANTS = [
    ("alt_a.html", "Option A (colors: cool)", "cool"),
    ("alt_b.html", "Option B (colors: contrast)", "contrast"),
    ("alt_c.html", "Option C (colors: expressive)", "expressive"),
]


def test_build_marked_element_context_extracts_subtree_and_css() -> None:
    ctx = build_marked_element_context(
        CALC_HTML,
        keep_ids=["7"],
        delete_ids=["tan"],
        focus_scope="colors",
        project_kind="calculator",
    )
    assert ctx is not None
    assert "MARKED ELEMENT CONTEXT" in ctx
    assert "btn-7" in ctx or "#7" in ctx
    assert "btn-tan" in ctx or "#tan" in ctx
    assert "#btn-7" in ctx or "background" in ctx
    assert "DELETE" in ctx
    assert "KEEP" in ctx
    assert "#colors" in ctx


def test_build_marked_element_context_uses_client_fragment_fallback() -> None:
    ctx = build_marked_element_context(
        "<html><body><div id='other'>x</div></body></html>",
        delete_ids=["missing"],
        focus_scope="functions",
        project_kind="web",
        client_fragments=[
            {
                "id": "missing",
                "type": "DELETE",
                "fragment": {"html": '<button id="btn-missing">Go</button>'},
            }
        ],
    )
    assert ctx is not None
    assert "btn-missing" in ctx


def test_build_marked_element_context_returns_none_without_marks() -> None:
    assert resolve_marked_llm_context(CALC_HTML, keep_els=[], delete_els=[]) is None


def test_build_marked_element_context_patch_mode_note() -> None:
    ctx = build_marked_element_context(
        CALC_HTML,
        delete_ids=["tan"],
        focus_scope="colors",
        project_kind="imported",
        ui_profile={
            "llm_context_mode": "patch",
            "html_outline": "<html><body></body></html>",
            "visual_css": "#btn-tan { color: red; }",
        },
    )
    assert ctx is not None
    assert "Patch mode" in ctx
    assert "color: red" in ctx or "#btn-tan" in ctx


def test_ui_patch_prompt_uses_marked_context_fragment() -> None:
    marked = build_marked_element_context(
        CALC_HTML,
        delete_ids=["tan"],
        focus_scope="colors",
        project_kind="calculator",
    )
    assert marked
    prompt = build_ui_patch_prompt(
        CALC_HTML,
        focus_scope="colors",
        project_kind="calculator",
        option_variants=VARIANTS,
        delete_els=["tan"],
        context_fragment=marked,
    )
    assert marked in prompt
    assert "DELETE-marked elements" in prompt or "primary redesign" in prompt
    assert "calc-body" not in prompt


def test_has_ui_marks() -> None:
    assert not has_ui_marks([], [])
    assert has_ui_marks(["7"], [])
    assert has_ui_marks([], ["tan"])
    assert has_ui_marks(["7"], ["tan"])


def test_restrict_scope_css_to_marks_targets_delete_only() -> None:
    css = (
        "html,body{background:#000!important;}"
        ".btn{background:#fff!important;color:#000!important;}"
    )
    scoped = restrict_scope_css_to_marks(css, ["tan"])
    assert "html,body" not in scoped
    assert "#btn-tan" in scoped or "#tan" in scoped
    assert "background:#fff" in scoped


def test_inject_scope_style_skips_global_css_for_keep_only_marks() -> None:
    html = (
        "<html><head></head><body><div class='calc-body'>"
        "<button class='btn' id='btn-7'>7</button></div></body></html>"
    )
    patched = inject_scope_style(
        html,
        "colors",
        "b",
        project_kind="calculator",
        keep_ids=["7"],
        delete_ids=[],
    )
    assert "nexu-scope-variant" not in patched


def test_inject_scope_style_scopes_css_to_delete_marks() -> None:
    html = (
        "<html><head></head><body><div class='calc-body'>"
        "<button class='btn' id='btn-tan'>tan</button></div></body></html>"
    )
    patched = inject_scope_style(
        html,
        "colors",
        "a",
        project_kind="calculator",
        delete_ids=["tan"],
    )
    assert "nexu-scope-variant" in patched
    assert "#btn-tan" in patched or "#tan" in patched
    assert "background-color:#38bdf8" in patched
    assert "html,body" not in patched


def test_resolve_marked_selectors_includes_classes() -> None:
    html = (
        "<body><a class='kb-btn2_237106-a1' href='#'>Zapisz dziecko</a>"
        "<button class='kb-btn2_999'>Nasza lokalizacja</button></body>"
    )
    selectors = resolve_marked_selectors(
        html,
        ["Zapisz dziecko", "Nasza lokalizacja"],
    )
    assert ".kb-btn2_237106-a1" in selectors
    assert ".kb-btn2_999" in selectors
    assert '[data-nexu-target="Zapisz dziecko"]' in selectors
    assert not any(sel.startswith("#Zapisz ") for sel in selectors)


def test_resolve_marked_selectors_narrow_excludes_keep_and_generic_classes() -> None:
    html = (
        "<body>"
        '<button class="button header-button">Zapisz swoje dziecko</button>'
        '<a class="button kb-btn2_237106-a1" href="#">Zapisz dziecko</a>'
        '<button class="button kb-btn2_487f06-54">Nasza lokalizacja</button>'
        "</body>"
    )
    selectors = resolve_marked_selectors(
        html,
        ["Zapisz swoje dziecko"],
        keep_ids=["Zapisz dziecko", "Nasza lokalizacja"],
        narrow=True,
    )
    assert '[data-nexu-target="Zapisz swoje dziecko"]' in selectors
    assert ".button" not in selectors
    assert ".header-button" not in selectors
    assert ".kb-btn2_237106-a1" not in selectors
    assert ".kb-btn2_487f06-54" not in selectors


def test_inject_scope_style_colors_mixed_keep_delete() -> None:
    html = (
        "<html><head></head><body>"
        '<button class="button header-button">Zapisz swoje dziecko</button>'
        '<a class="button kb-btn2_237106-a1" href="#">Zapisz dziecko</a>'
        '<button class="button kb-btn2_487f06-54">Nasza lokalizacja</button>'
        "</body></html>"
    )
    patched = inject_scope_style(
        html,
        "colors",
        "a",
        project_kind="imported",
        delete_ids=["Zapisz swoje dziecko"],
        keep_ids=["Zapisz dziecko", "Nasza lokalizacja"],
    )
    assert "nexu-scope-variant" in patched
    assert "background-color:#38bdf8" in patched
    assert '[data-nexu-target="Zapisz swoje dziecko"]' in patched
    assert ".button" not in patched
    assert ".kb-btn2_237106-a1" not in patched
    assert ".kb-btn2_487f06-54" not in patched
    assert "html,body" not in patched


def test_marked_scope_colors_css_differs_by_variant() -> None:
    selectors = [".kb-btn2_237106-a1"]
    a = marked_scope_colors_css(selectors, "a")
    b = marked_scope_colors_css(selectors, "b")
    assert "background-color:#38bdf8" in a
    assert "background-color:#facc15" in b
    assert a != b
    assert ".kb-btn2_237106-a1 *" in a
    assert "color:#0f172a!important" in a


def test_marked_scope_colors_css_overrides_all_descendants() -> None:
    selectors = [f".target-{idx}" for idx in range(12)]
    css = marked_scope_colors_css(selectors, "c")
    assert ".target-0 *" in css
    assert ".target-11 *" in css
    assert "color:#1e1b4b!important" in css


def test_resolve_marked_selectors_heading_text_id() -> None:
    mark = "Pracownia Malort Gdynia – przestrzeń dla kreatywności Twojego dziecka"
    html = (
        '<h2 class="kt-adv-heading2_289857-94 wp-block-kadence-advancedheading">'
        '<strong style="color: #007D13;">Pracownia Malort Gdynia – </strong>'
        "przestrzeń dla kreatywności Twojego dziecka"
        "</h2>"
    )
    selectors = resolve_marked_selectors(html, [mark], narrow=True)
    assert ".kt-adv-heading2_289857-94" in selectors
    assert ".wp-block-kadence-advancedheading" not in selectors
    assert f'[data-nexu-target="{mark}"]' in selectors


def test_resolve_marked_selectors_heading_text_entities() -> None:
    mark = "Pracownia Malort Gdynia – przestrzeń dla kreatywności Twojego dziecka"
    html = (
        '<h2 class="kt-adv-heading2_289857-94 wp-block-kadence-advancedheading">'
        '<strong style="color: #007D13;">Pracownia Malort Gdynia&nbsp;&#8211; </strong>'
        "przestrzeń dla kreatywności Twojego dziecka"
        "</h2>"
    )
    selectors = resolve_marked_selectors(html, [mark], narrow=True)
    assert ".kt-adv-heading2_289857-94" in selectors
    assert ".wp-block-kadence-advancedheading" not in selectors


def test_inject_scope_style_colors_overrides_inline_heading_color() -> None:
    mark = "Pracownia Malort Gdynia – przestrzeń dla kreatywności Twojego dziecka"
    html = (
        "<html><head></head><body>"
        '<h2 class="kt-adv-heading2_289857-94 wp-block-kadence-advancedheading">'
        '<strong style="color: #007D13;">Pracownia Malort Gdynia – </strong>'
        "przestrzeń dla kreatywności Twojego dziecka"
        "</h2></body></html>"
    )
    patched = inject_scope_style(
        html,
        "colors",
        "a",
        project_kind="imported",
        delete_ids=[mark],
    )
    assert "nexu-scope-variant" in patched
    assert ".kt-adv-heading2_289857-94" in patched
    assert ".kt-adv-heading2_289857-94 *" in patched
    assert "color:#0f172a!important" in patched
    assert "background-color:#38bdf8" in patched


def test_inject_scope_style_colors_overrides_multiple_marked_headings() -> None:
    heading = "Pracownia Malort Gdynia – przestrzeń dla kreatywności Twojego dziecka"
    body = (
        "Zapraszamy do wyjątkowego miejsca, gdzie dzieci rozwijają wyobraźnię i "
        "pewność siebie poprzez spontaniczną twórczość artystyczną."
    )
    html = (
        "<html><head></head><body>"
        '<h2 class="kt-adv-heading2_289857-94 wp-block-kadence-advancedheading">'
        '<strong style="color: #007D13;">Pracownia Malort Gdynia&nbsp;&#8211; </strong>'
        "przestrzeń dla kreatywności Twojego dziecka"
        "</h2>"
        '<h2 class="kt-adv-heading2_79aa1a-c6 wp-block-kadence-advancedheading">'
        f"{body}"
        "</h2>"
        "</body></html>"
    )
    patched = inject_scope_style(
        html,
        "colors",
        "c",
        project_kind="imported",
        delete_ids=[body, heading],
    )
    assert "nexu-scope-variant" in patched
    assert ".kt-adv-heading2_289857-94" in patched
    assert ".kt-adv-heading2_79aa1a-c6" in patched
    assert ".kt-adv-heading2_289857-94 *" in patched
    assert ".kt-adv-heading2_79aa1a-c6 *" in patched
    assert "background-color:#e879f9" in patched


def test_should_block_full_html_for_imported_marks() -> None:
    assert should_block_full_html_iterate("imported", ["hero"], [], focus_scope="colors")
    assert should_block_full_html_iterate("dashboard", [], ["kpi"], focus_scope="functions")
    assert not should_block_full_html_iterate("imported", [], [], focus_scope="colors")
    assert not should_block_full_html_iterate("calculator", ["7"], [], focus_scope="colors")


def test_marked_css_selectors_includes_btn_prefix() -> None:
    selectors = marked_css_selectors(["tan"])
    assert "#btn-tan" in selectors
    assert "#tan" in selectors


def test_goal_requests_column_layout_detects_polish_and_english() -> None:
    from repatch import goal_requests_column_layout

    assert goal_requests_column_layout("podziel na dwie kolumny")
    assert goal_requests_column_layout("split into two columns")
    assert goal_requests_column_layout("column layout refresh")
    assert not goal_requests_column_layout("nowoczesny design strony")
    assert not goal_requests_column_layout("")


def test_inject_scope_style_display_keeps_entry_content_typography() -> None:
    import re

    html = """<!DOCTYPE html><html><head></head><body>
<main class="site-content"><div class="entry-content">
<h1>Title</h1><p>Body</p>
</div></main>
<button class="kb-btn2_237106-a1">Change me</button>
</body></html>"""
    patched = inject_scope_style(
        html,
        "display",
        "b",
        project_kind="imported",
        delete_ids=["Change me"],
    )
    style_match = re.search(
        r'<style id="nexu-scope-variant">\s*(.*?)\s*</style>',
        patched,
        flags=re.I | re.S,
    )
    assert style_match is not None
    scope_css = style_match.group(1)
    assert ".entry-content h1" in scope_css
    assert "font-size:1.65rem" in scope_css
    assert '[data-nexu-target="Change me"]' in scope_css


def test_inject_scope_style_shapes_keeps_content_wrapper_radii() -> None:
    import re

    html = """<!DOCTYPE html><html><head></head><body>
<div class="entry-content">
<button class="kb-btn2_237106-a1">Round me</button>
</div></body></html>"""
    patched = inject_scope_style(
        html,
        "shapes",
        "c",
        project_kind="imported",
        delete_ids=["Round me"],
    )
    style_match = re.search(
        r'<style id="nexu-scope-variant">\s*(.*?)\s*</style>',
        patched,
        flags=re.I | re.S,
    )
    assert style_match is not None
    scope_css = style_match.group(1)
    assert ".entry-content button" in scope_css
    assert "border-radius:999px" in scope_css
    assert '[data-nexu-target="Round me"]' in scope_css


def test_inject_scope_style_orientation_column_goal_keeps_layout_css() -> None:
    import re

    html = """<!DOCTYPE html><html><head></head><body>
<main class="site-content"><div class="entry-content">
<p>Col1</p><p>Col2</p>
</div></main>
<a class="kb-btn2_237106-a1" href="#">Move me</a>
</body></html>"""
    patched = inject_scope_style(
        html,
        "orientation",
        "b",
        project_kind="imported",
        delete_ids=["Move me"],
        user_goal="podziel na dwie kolumny",
    )
    assert "nexu-scope-variant" in patched
    style_match = re.search(
        r'<style id="nexu-scope-variant">\s*(.*?)\s*</style>',
        patched,
        flags=re.I | re.S,
    )
    assert style_match is not None
    scope_css = style_match.group(1)
    assert "grid-template-columns" in scope_css
    assert "1fr 1fr" in scope_css
    assert ":has(" in scope_css
    assert ".entry-content:has(" in scope_css or "main:has(" in scope_css
    assert '[data-nexu-target="Move me"]' in scope_css
