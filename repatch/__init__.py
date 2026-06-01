"""HTML/CSS/DOM patch utilities for scoped UI iteration."""

from __future__ import annotations

from .css import split_css_rules, validate_css_safety
from .dom_patch import (
    build_function_option_patches,
    build_function_patch_context,
    supports_function_patch,
)
from .marked_context import (
    build_marked_element_context,
    effective_delete_ids,
    has_ui_marks,
    marked_css_selectors,
    marked_scope_colors_css,
    resolve_marked_llm_context,
    resolve_marked_selectors,
    restrict_scope_css_to_marks,
)
from .project_ir import build_project_ir, summarize_project_ir
from .scope import (
    DASHBOARD_KINDS,
    IMPORTED_KINDS,
    MARKED_PATCH_KINDS,
    SCOPE_STYLE_ID,
    VISUAL_REDESIGN_SCOPES,
    allowed_scope_ids,
    default_scope_for_kind,
    inject_scope_style,
    normalize_focus_scope,
    offline_fast_scopes_for_kind,
    scope_supports_offline_fast_path,
    scoped_html_fragment,
    should_block_full_html_iterate,
    strip_scope_style,
    ui_type_for_kind,
)
from .service import PatchSuggestion, RepatchService, SUPPORTED_SCOPES
from .spatial import apply_spatial_deletes_to_html
from .ui_patch import (
    apply_ui_patch_options,
    build_ui_patch_prompt,
    parse_ui_patch_response,
    supports_llm_patch_scope,
)

__all__ = [
    "DASHBOARD_KINDS",
    "IMPORTED_KINDS",
    "MARKED_PATCH_KINDS",
    "PatchSuggestion",
    "RepatchService",
    "SCOPE_STYLE_ID",
    "SUPPORTED_SCOPES",
    "VISUAL_REDESIGN_SCOPES",
    "allowed_scope_ids",
    "apply_spatial_deletes_to_html",
    "apply_ui_patch_options",
    "build_function_option_patches",
    "build_function_patch_context",
    "build_marked_element_context",
    "build_project_ir",
    "build_ui_patch_prompt",
    "default_scope_for_kind",
    "effective_delete_ids",
    "has_ui_marks",
    "inject_scope_style",
    "marked_css_selectors",
    "marked_scope_colors_css",
    "normalize_focus_scope",
    "offline_fast_scopes_for_kind",
    "parse_ui_patch_response",
    "resolve_marked_llm_context",
    "resolve_marked_selectors",
    "restrict_scope_css_to_marks",
    "scope_supports_offline_fast_path",
    "scoped_html_fragment",
    "should_block_full_html_iterate",
    "split_css_rules",
    "strip_scope_style",
    "summarize_project_ir",
    "supports_function_patch",
    "supports_llm_patch_scope",
    "ui_type_for_kind",
    "validate_css_safety",
]
