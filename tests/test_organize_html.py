from __future__ import annotations

from pathlib import Path

from repatch import organize_html, organize_html_project_dir
from repatch.organize_html import is_lazy_placeholder_img_tag, organize_result_manifest


INLINE_STYLE_HTML = """<!DOCTYPE html>
<html><head>
<style>
.hero { color: #112233; padding: 2rem; margin: 1rem; border-radius: 8px; }
.card { background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,.1); }
</style>
</head><body><h1>Hi</h1></body></html>
"""

LAZY_IMG = (
    '<img class="wp-image-12" data-lazyloaded="1" '
    'src="data:image/svg+xml;base64,PHN2Zy8+" alt="" width="10" height="10" />'
)
REAL_IMG = '<img class="wp-image-99" alt="Hero" src="/photo.jpg" />'


def test_organize_extracts_substantial_inline_css(tmp_path: Path) -> None:
    result = organize_html(INLINE_STYLE_HTML, base_dir=tmp_path)

    assert result.meta["styles_extracted"] is True
    assert (tmp_path / "nexu-extracted.css").is_file()
    assert ".hero" in (tmp_path / "nexu-extracted.css").read_text(encoding="utf-8")
    assert "<style" not in result.html.lower()
    assert 'href="nexu-extracted.css"' in result.html


def test_organize_strips_preview_scripts_and_lazy_imgs() -> None:
    html = f"""<!DOCTYPE html><html><body>
    {LAZY_IMG}
    {REAL_IMG}
    <script>fetch('https://cdn.example/x')</script>
    </body></html>"""
    result = organize_html(html)

    assert result.meta["lazy_imgs_removed"] == 1
    assert result.meta["scripts_removed"] >= 1
    assert "data-lazyloaded" not in result.html
    assert 'src="/photo.jpg"' in result.html
    assert "cdn.example" not in result.html


def test_is_lazy_placeholder_img_tag() -> None:
    assert is_lazy_placeholder_img_tag(LAZY_IMG) is True
    assert is_lazy_placeholder_img_tag(REAL_IMG) is False


def test_organize_html_project_dir_writes_index(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    index = source / "index.html"
    index.write_text(INLINE_STYLE_HTML, encoding="utf-8")

    result = organize_html_project_dir(source)

    assert result is not None
    assert result.meta["styles_extracted"] is True
    assert "<style" not in index.read_text(encoding="utf-8").lower()
    assert (source / "nexu-extracted.css").is_file()


def test_organize_noop_for_minimal_html() -> None:
    html = "<!DOCTYPE html><html><body><p>ok</p></body></html>"
    result = organize_html(html)

    assert result.meta["styles_extracted"] is False
    assert result.meta["organized"] is False


def test_organize_result_manifest_summarizes_extracted_files(tmp_path: Path) -> None:
    result = organize_html(INLINE_STYLE_HTML, base_dir=tmp_path)
    manifest = organize_result_manifest(result)

    assert manifest["extracted_files"] == ["nexu-extracted.css"]
    assert manifest["stripped_lazy_img_count"] == 0
    assert manifest["tagged_targets_count"] >= 0
    assert manifest["styles_extracted"] is True
