"""Compact HTML/CSS context for Cinema marked workspace elements.

This package was split out of a single 696-line module (ticket PLF-004) into
focused submodules organized by responsibility:

* :mod:`._ids` — element id / attribute normalization and CSS selector derivation.
* :mod:`._html` — balanced HTML subtree extraction for marked elements.
* :mod:`._selectors` — resolve marked CSS selectors; restrict scope CSS to marks.
* :mod:`._scope_css` — per-scope, per-variant CSS declarations for DELETE marks.
* :mod:`._context` — assemble the compact marked-element LLM context string.

Everything is re-exported here so existing ``from repatch.marked_context import X``
imports (including the private helpers that ``repatch.scope`` depends on) keep
working unchanged.
"""

from __future__ import annotations

from ._context import (
    MAX_CSS_BYTES,
    MAX_MARKED_CONTEXT_BYTES,
    _VISUAL_SCOPES,
    _cap_text,
    _collect_css_sources,
    _format_context_body,
    _get_relevant_css,
    _scope_semantics,
    build_marked_element_context,
    resolve_marked_llm_context,
)
from ._html import (
    MAX_FRAGMENT_BYTES,
    _TAG_OPEN_RE,
    _VOID_TAGS,
    _assemble_marked_subtrees,
    _client_fragment_html,
    _collect_button_candidates,
    _collect_match_candidates,
    _extract_and_format_fragment,
    _extract_balanced_html,
    _find_marked_subtrees,
)
from ._ids import (
    _ATTR_RE,
    _ID_SELECTOR_RE,
    _TEXT_LABEL_TAGS,
    _css_id_selector,
    _id_candidates,
    _logical_id,
    _normalize_label_text,
    _parse_attrs,
    effective_delete_ids,
    has_ui_marks,
    marked_css_selectors,
)
from ._scope_css import (
    _MARKED_COLOR_DECL,
    marked_scope_colors_css,
    marked_scope_display_css,
    marked_scope_orientation_css,
    marked_scope_shapes_css,
)
from ._selectors import (
    _GENERIC_SHARED_CLASSES,
    _collect_keep_selectors,
    _filter_css_for_tokens,
    _fragment_class_names,
    _selector_tokens,
    resolve_marked_selectors,
    restrict_scope_css_to_marks,
)

__all__ = [
    "MAX_CSS_BYTES",
    "MAX_FRAGMENT_BYTES",
    "MAX_MARKED_CONTEXT_BYTES",
    "build_marked_element_context",
    "effective_delete_ids",
    "has_ui_marks",
    "marked_css_selectors",
    "marked_scope_colors_css",
    "marked_scope_display_css",
    "marked_scope_orientation_css",
    "marked_scope_shapes_css",
    "resolve_marked_llm_context",
    "resolve_marked_selectors",
    "restrict_scope_css_to_marks",
]
