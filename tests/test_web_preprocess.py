from __future__ import annotations

from pathlib import Path

from repatch import (
    build_html_outline,
    build_http_llm_context,
    extract_visual_css,
    prepare_http_preview_html,
    sanitize_http_preview_html,
)


SAMPLE_HTML = """<!DOCTYPE html>
<html>
<head>
  <style>
    .hero { color: #112233; border-radius: 12px; }
    @font-face { font-family: x; src: url(x.woff2); }
  </style>
  <link rel="stylesheet" href="assets/theme.css">
</head>
<body data-nexu-target="root">
  <main><h1>Welcome</h1><p>Body</p></main>
  <script>console.log('skip');</script>
</body>
</html>
"""


def test_extract_visual_css_keeps_patch_relevant_rules(tmp_path: Path) -> None:
    assets = tmp_path / "assets"
    assets.mkdir()
    (assets / "theme.css").write_text(
        ".card{background:#fff;padding:12px}.print{page-break-after:always}",
        encoding="utf-8",
    )
    css, meta = extract_visual_css(SAMPLE_HTML, ["assets/theme.css"], tmp_path)

    assert ".hero" in css
    assert ".card" in css
    assert "@font-face" not in css
    assert meta["visual_css_bytes"] > 0


def test_build_html_outline_strips_scripts_and_text() -> None:
    outline, meta = build_html_outline(SAMPLE_HTML)

    assert "<script" not in outline.lower()
    assert "Welcome" not in outline
    assert 'data-nexu-target="root"' in outline
    assert meta["outline_node_count"] >= 4


def test_prepare_http_preview_html_blocks_cross_origin_runtime() -> None:
    cleaned, meta = sanitize_http_preview_html(
        '<html><head></head><body><script src="https://example.com/a.js"></script></body></html>'
    )
    assert meta["preview_scripts_removed"] == 1
    assert "example.com" not in cleaned

    prepared, meta = prepare_http_preview_html(SAMPLE_HTML)
    assert meta["preview_shim_injected"] is True
    assert "nexu preview: block cross-origin fetch" in prepared


def test_build_http_llm_context_includes_organize_manifest() -> None:
    ctx = build_http_llm_context(
        {
            "visual_css": "body { color: red; }",
            "html_outline": "<body></body>",
            "organize": {
                "extracted_files": ["nexu-extracted.css"],
                "tagged_targets_count": 2,
            },
            "extracted_css": ".hero { padding: 1rem; }",
            "source_paths": {
                "index_html": "source/index.html",
                "nexu-extracted_css": "source/nexu-extracted.css",
            },
        }
    )
    assert "organize manifest" in ctx.lower()
    assert "data-nexu-target" in ctx
    assert ".hero { padding: 1rem; }" in ctx
