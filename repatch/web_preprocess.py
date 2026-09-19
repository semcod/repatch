"""Prepare imported web pages for fast patching and LLM-safe iteration.

This module is a thin facade over focused submodules split from the original
single-file implementation:

- ``_web_css``: inline/linked CSS extraction and visual filtering
- ``_html_outline``: compact HTML skeleton builder
- ``_http_preview``: preview sanitization and network isolation shim
- ``_http_llm_context``: LLM patch prompt context assembly

The public surface is re-exported here so existing imports keep working
unchanged. The private ``_SCRIPT_BLOCK_RE`` / ``_STYLE_BLOCK_RE`` /
``_should_remove_preview_script`` symbols are also re-exported because
:mod:`repatch.organize_html` reaches into them directly.
"""

from __future__ import annotations

from ._html_outline import OUTLINE_TEXT_PLACEHOLDER, build_html_outline
from ._http_llm_context import (
    MAX_EXTRACTED_PATCH_BYTES,
    build_http_llm_context,
    http_patch_llm_rules,
)
from ._http_preview import (
    _SCRIPT_BLOCK_RE,  # noqa: F401
    HTTP_PREVIEW_NETWORK_SHIM,
    _should_remove_preview_script,  # noqa: F401
    inject_http_preview_shim,
    prepare_http_preview_html,
    sanitize_http_preview_html,
)
from ._web_css import (
    _STYLE_BLOCK_RE,  # noqa: F401
    MAX_VISUAL_CSS_BYTES,
    extract_inline_css,
    extract_stylesheet_hrefs,
    extract_visual_css,
    filter_visual_css,
    normalize_linked_paths,
    safe_read_under,
)

__all__ = [
    "HTTP_PREVIEW_NETWORK_SHIM",
    "MAX_EXTRACTED_PATCH_BYTES",
    "MAX_VISUAL_CSS_BYTES",
    "OUTLINE_TEXT_PLACEHOLDER",
    "build_html_outline",
    "build_http_llm_context",
    "extract_inline_css",
    "extract_stylesheet_hrefs",
    "extract_visual_css",
    "filter_visual_css",
    "http_patch_llm_rules",
    "inject_http_preview_shim",
    "normalize_linked_paths",
    "prepare_http_preview_html",
    "safe_read_under",
    "sanitize_http_preview_html",
]
