from __future__ import annotations

from pathlib import Path

from repatch import web_preprocess
from repatch._html_outline import _OutlineParser, build_html_outline
from repatch._http_llm_context import (
    _cap_patch_text,
    build_http_llm_context,
    http_patch_llm_rules,
)
from repatch._http_preview import (
    HTTP_PREVIEW_NETWORK_SHIM,
    _script_src_allowed_for_preview,
    _should_remove_preview_script,
    inject_http_preview_shim,
    prepare_http_preview_html,
    sanitize_http_preview_html,
)
from repatch._web_css import (
    MAX_VISUAL_CSS_BYTES,
    _rule_is_visual,
    extract_inline_css,
    extract_stylesheet_hrefs,
    extract_visual_css,
    filter_visual_css,
    normalize_linked_paths,
    safe_read_under,
)


def test_facade_re_exports_public_surface() -> None:
    assert web_preprocess.extract_visual_css is extract_visual_css
    assert web_preprocess.build_html_outline is build_html_outline
    assert web_preprocess.build_http_llm_context is build_http_llm_context
    assert web_preprocess.prepare_http_preview_html is prepare_http_preview_html
    assert web_preprocess.http_patch_llm_rules is http_patch_llm_rules
    assert web_preprocess.HTTP_PREVIEW_NETWORK_SHIM is HTTP_PREVIEW_NETWORK_SHIM


def test_facade_keeps_organize_html_private_imports() -> None:
    assert hasattr(web_preprocess, "_SCRIPT_BLOCK_RE")
    assert hasattr(web_preprocess, "_STYLE_BLOCK_RE")
    assert hasattr(web_preprocess, "_should_remove_preview_script")


def test_safe_read_under_reads_file_below_root(tmp_path: Path) -> None:
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "theme.css").write_text(".a{color:red}", encoding="utf-8")

    assert safe_read_under(tmp_path, "assets/theme.css") == ".a{color:red}"


def test_safe_read_under_blocks_traversal_and_missing(tmp_path: Path) -> None:
    assert safe_read_under(tmp_path, "../secret.txt") is None
    assert safe_read_under(tmp_path, "missing.css") is None


def test_extract_inline_css_combines_and_ignores_empty() -> None:
    html = "<style>.a{color:red}</style><style>  </style><style>.b{color:blue}</style>"
    assert extract_inline_css(html) == ".a{color:red}\n\n.b{color:blue}"
    assert extract_inline_css("") == ""


def test_extract_stylesheet_hrefs_both_link_orders_and_dedup() -> None:
    html = (
        '<link rel="stylesheet" href="assets/a.css">\n'
        '<link href="assets/b.css" rel="stylesheet">\n'
        '<link rel="stylesheet" href="assets/a.css">'
    )
    assert extract_stylesheet_hrefs(html) == ["assets/a.css", "assets/b.css"]


def test_normalize_linked_paths_strips_slash_and_skips_remote() -> None:
    html = '<link rel="stylesheet" href="/assets/theme.css"><link rel="stylesheet" href="https://x/a.css">'
    assert normalize_linked_paths([], html) == ["assets/theme.css"]
    assert normalize_linked_paths(["/assets/theme.css"], "") == ["assets/theme.css"]


def test_rule_is_visual_filters_at_rules_and_props() -> None:
    assert _rule_is_visual(".hero { color: red; }") is True
    assert _rule_is_visual("@font-face { font-family: x; }") is False
    assert _rule_is_visual("@media print { .x { color: red } }") is False
    assert _rule_is_visual(":root { --bg: #fff; }") is True
    assert _rule_is_visual("body { margin: 0; }") is True
    assert _rule_is_visual(".x { position: absolute; }") is False


def test_filter_visual_css_keeps_only_patch_relevant_rules() -> None:
    input_css = ".card{background:#fff;padding:12px}.hidden{position:absolute}@font-face{font-family:x;src:url(x)}"
    out = filter_visual_css(input_css)
    assert ".card{background:#fff;padding:12px}" in out
    assert "position:absolute" not in out
    assert "@font-face" not in out


def test_extract_visual_css_truncates_over_limit(tmp_path: Path) -> None:
    big = ".big{background:#" + "a" * (MAX_VISUAL_CSS_BYTES * 2) + ";}"
    html = f"<style>{big}</style>"
    visual_css, meta = extract_visual_css(html, None, tmp_path)

    assert meta["visual_css_truncated"] is True
    assert "truncated at 64KB" in visual_css
    assert len(visual_css.encode("utf-8")) < len(big.encode("utf-8"))


def test_outline_parser_skips_scripts_and_places_placeholders() -> None:
    html = "<body><script>let x = 1;</script><h1>Hello</h1></body>"
    outline, meta = build_html_outline(html)

    assert "<script" not in outline.lower()
    assert "Hello" not in outline
    assert "…" in outline
    assert meta["outline_node_count"] >= 2
    assert outline.startswith("<!DOCTYPE html>")


def test_outline_parser_keeps_whitelisted_attrs_and_void_selfclose() -> None:
    parser = _OutlineParser()
    parser.feed('<img src="/x.png" class="hero" data-nexu-x="1" style="color:red">')
    parser.close()

    assert 'class="hero"' in parser.parts[0]
    assert 'data-nexu-x="1"' in parser.parts[0]
    assert 'src="/x.png"' not in parser.parts[0]
    assert 'style="color:red"' not in parser.parts[0]
    assert parser.parts[0].endswith(" />")


def test_script_src_allowed_for_preview_rules() -> None:
    assert _script_src_allowed_for_preview("imported_projects/app.js") is True
    assert _script_src_allowed_for_preview("https://x/a.js") is False
    assert _script_src_allowed_for_preview("data:text/javascript,x") is False
    assert _script_src_allowed_for_preview("") is False


def test_should_remove_preview_script_removes_nonlocal() -> None:
    assert _should_remove_preview_script('<script src="https://x/a.js"></script>') is True
    assert _should_remove_preview_script('<script src="imported_projects/a.js"></script>') is False
    assert _should_remove_preview_script("<script>console.log(1)</script>") is True


def test_sanitize_http_preview_html_keeps_allowed_src() -> None:
    html = (
        '<script src="https://x/a.js"></script>'
        '<script src="imported_projects/a.js"></script>'
    )
    cleaned, meta = sanitize_http_preview_html(html)

    assert meta["preview_scripts_removed"] == 1
    assert "https://x/a.js" not in cleaned
    assert "imported_projects/a.js" in cleaned


def test_inject_http_preview_shim_is_idempotent_and_falls_back() -> None:
    with_head = inject_http_preview_shim("<html><head></head><body></body></html>")
    assert HTTP_PREVIEW_NETWORK_SHIM in with_head
    assert inject_http_preview_shim(with_head) == with_head

    no_html = inject_http_preview_shim("<body>hi</body>")
    assert no_html.startswith(HTTP_PREVIEW_NETWORK_SHIM)


def test_prepare_http_preview_html_sets_shim_flag() -> None:
    out, meta = prepare_http_preview_html("<html><head></head><body></body></html>")
    assert meta["preview_shim_injected"] is True
    assert "nexu preview: block cross-origin fetch" in out


def test_cap_patch_text_truncates_and_labels() -> None:
    assert _cap_patch_text("", 10, section_label="x") == ""
    assert _cap_patch_text("short", 10, section_label="x") == "short"
    out = _cap_patch_text("a" * 30, 10, section_label="extracted CSS")
    assert out.startswith("a" * 10)
    assert "truncated" in out
    assert "extracted CSS" in out


def test_build_http_llm_context_empty_and_full() -> None:
    assert build_http_llm_context({}) == ""
    ctx = build_http_llm_context(
        {
            "visual_css": "body{color:red}",
            "html_outline": "<body></body>",
            "organize": {
                "extracted_files": ["nexu-extracted.css"],
                "tagged_targets_count": 3,
                "stripped_lazy_img_count": 2,
            },
            "extracted_css": ".hero{padding:1rem}",
            "source_paths": {"index_html": "source/index.html"},
        }
    )
    assert "IMPORTED WEB PAGE" in ctx
    assert "organize manifest" in ctx.lower()
    assert "data-nexu-target" in ctx
    assert "index_html" in ctx
    assert ".hero{padding:1rem}" in ctx


def test_http_patch_llm_rules_is_stable() -> None:
    rules = http_patch_llm_rules()
    assert "PATCH MODE" in rules
    assert "Do NOT include <script>" in rules
