from __future__ import annotations

from repatch._assets import (
    _extract_inline_styles,
    _inject_head_link,
    _inject_head_script,
)
from repatch._images import (
    _attr_map,
    _strip_lazy_placeholder_imgs,
    is_lazy_placeholder_img_tag,
)
from repatch._targets import MAX_TARGETS_ADDED, _add_markable_targets, _slug_piece


def test_attr_map_parses_key_value_pairs() -> None:
    assert _attr_map('class="hero" id="main" data-x=\'1\'') == {
        "class": "hero",
        "id": "main",
        "data-x": "1",
    }


def test_attr_map_lowercases_names_and_handles_empty() -> None:
    assert _attr_map('SRC="/img.png"') == {"src": "/img.png"}
    assert _attr_map("") == {}
    assert _attr_map(None) == {}


def test_is_lazy_placeholder_img_tag_edge_cases() -> None:
    assert is_lazy_placeholder_img_tag(
        '<img data-src="/real.jpg" src="#" alt="x" />'
    ) is True
    assert is_lazy_placeholder_img_tag('<img src="" class="lazy" alt="x" />') is True
    assert is_lazy_placeholder_img_tag('<img src="/real.jpg" alt="x" />') is False
    assert is_lazy_placeholder_img_tag('<div class="lazy"></div>') is False


def test_strip_lazy_placeholder_imgs_keeps_real_imgs() -> None:
    lazy = '<img data-lazyloaded="1" src="data:image/svg+xml;base64,PHN2Zy8+" alt="" />'
    real = '<img src="/photo.jpg" alt="Hero" />'
    html = f"<body>{lazy}{real}</body>"
    out, removed = _strip_lazy_placeholder_imgs(html)

    assert removed == 1
    assert "data-lazyloaded" not in out
    assert 'src="/photo.jpg"' in out
    assert "lazy placeholder img removed" in out


def test_extract_inline_styles_combines_block_bodies() -> None:
    html = "<style>.a{color:red}</style><style>.b{color:blue}</style>"
    text, count = _extract_inline_styles(html)

    assert count == 2
    assert ".a{color:red}" in text
    assert ".b{color:blue}" in text
    assert "<style" not in text


def test_extract_inline_styles_ignores_empty_blocks() -> None:
    text, count = _extract_inline_styles("<style>  </style>")
    assert count == 0
    assert text == ""


def test_inject_head_link_into_existing_head() -> None:
    html = '<html><head><meta charset="utf-8"></head><body></body></html>'
    out = _inject_head_link(html, href="nexu-extracted.css")

    assert '<link rel="stylesheet" href="nexu-extracted.css">' in out
    assert '<head>\n  <link rel="stylesheet" href="nexu-extracted.css"><meta' in out


def test_inject_head_link_creates_head_when_absent() -> None:
    html = "<html><body></body></html>"
    out = _inject_head_link(html, href="nexu-extracted.css")

    assert '<html>\n<head><link rel="stylesheet" href="nexu-extracted.css"></head><body>' in out


def test_inject_head_script_into_existing_head() -> None:
    html = "<html><head></head><body></body></html>"
    out = _inject_head_script(html, src="nexu-extracted.js")

    assert '<script src="nexu-extracted.js"></script>' in out
    assert out.startswith('<html><head>\n  <script src="nexu-extracted.js">')


def test_slug_piece_normalizes_and_truncates() -> None:
    assert _slug_piece("hero-section") == "hero-section"
    assert _slug_piece("hero section") == "hero-section"
    assert _slug_piece("") == "node"
    assert _slug_piece("a" * 40) == "a" * 32


def test_add_markable_targets_tags_nodes_in_order() -> None:
    html = '<section class="hero"><h1>Title</h1><a href="#">Link</a></section>'
    out, added = _add_markable_targets(html)

    assert added == 3
    assert 'data-nexu-target="nexu-hero-1"' in out
    assert 'data-nexu-target="nexu-h1-2"' in out
    assert 'data-nexu-target="nexu-a-3"' in out


def test_add_markable_targets_skips_id_and_existing_targets() -> None:
    html = '<button id="submit">Go</button><article data-nexu-target="nexu-x-1">y</article>'
    out, added = _add_markable_targets(html)

    assert added == 0
    assert out == html


def test_add_markable_targets_respects_cap() -> None:
    html = "".join(f'<a class="l{i}" href="#">x</a>' for i in range(MAX_TARGETS_ADDED + 20))
    out, added = _add_markable_targets(html)

    assert added == MAX_TARGETS_ADDED
    assert out.count("data-nexu-target=") == MAX_TARGETS_ADDED
