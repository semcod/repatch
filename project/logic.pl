% ── Project Metadata ─────────────────────────────────────
project_metadata('repatch', '0.2.10', 'python').

% ── Project Files ────────────────────────────────────────
project_file('app.doql.less', 22, 'less').
project_file('project.sh', 50, 'shell').
project_file('repatch/__init__.py', 106, 'python').
project_file('repatch/css.py', 71, 'python').
project_file('repatch/dom_patch.py', 316, 'python').
project_file('repatch/marked_context.py', 697, 'python').
project_file('repatch/options.py', 141, 'python').
project_file('repatch/project_ir.py', 133, 'python').
project_file('repatch/scope.py', 648, 'python').
project_file('repatch/service.py', 106, 'python').
project_file('repatch/spatial.py', 109, 'python').
project_file('repatch/ui_patch.py', 268, 'python').
project_file('repatch/web_preprocess.py', 398, 'python').
project_file('sdks/js/repatch-sdk.js', 187, 'javascript').
project_file('sdks/python/repatch_sdk.py', 74, 'python').
project_file('tests/test_dom_patch.py', 74, 'python').
project_file('tests/test_marked_context.py', 442, 'python').
project_file('tests/test_options.py', 81, 'python').
project_file('tests/test_service.py', 54, 'python').
project_file('tests/test_spatial.py', 30, 'python').
project_file('tests/test_ui_patch.py', 157, 'python').
project_file('tree.sh', 2, 'shell').

% ── Python Functions ─────────────────────────────────────
python_function('repatch/css.py', '_strip_css_comments', 1, 2, 2).
python_function('repatch/css.py', '_selector_is_runtime_only', 1, 2, 2).
python_function('repatch/css.py', 'split_css_rules', 1, 9, 4).
python_function('repatch/css.py', 'validate_css_safety', 1, 14, 15).
python_function('repatch/dom_patch.py', 'supports_function_patch', 2, 4, 2).
python_function('repatch/dom_patch.py', 'build_function_patch_context', 1, 2, 3).
python_function('repatch/dom_patch.py', '_strip_existing_patch', 1, 2, 2).
python_function('repatch/dom_patch.py', '_goal_label', 1, 3, 2).
python_function('repatch/dom_patch.py', '_variant_section', 3, 3, 5).
python_function('repatch/dom_patch.py', '_patch_style', 0, 1, 0).
python_function('repatch/dom_patch.py', '_inject_into_head', 2, 4, 4).
python_function('repatch/dom_patch.py', '_inject_into_body', 2, 2, 2).
python_function('repatch/dom_patch.py', '_target_candidates', 1, 4, 6).
python_function('repatch/dom_patch.py', '_strip_tags', 1, 2, 2).
python_function('repatch/dom_patch.py', '_set_attr', 3, 2, 4).
python_function('repatch/dom_patch.py', '_attrs_from_open_tag', 1, 2, 5).
python_function('repatch/dom_patch.py', '_matches_target', 3, 4, 6).
python_function('repatch/dom_patch.py', '_variant_target_label', 2, 3, 1).
python_function('repatch/dom_patch.py', '_variant_href', 2, 4, 4).
python_function('repatch/dom_patch.py', '_patch_function_targets', 4, 6, 18).
python_function('repatch/dom_patch.py', '_default_prepare_html', 1, 3, 2).
python_function('repatch/dom_patch.py', '_default_finalize_html', 1, 1, 0).
python_function('repatch/dom_patch.py', 'build_function_option_patches', 1, 12, 15).
python_function('repatch/marked_context.py', 'has_ui_marks', 2, 8, 3).
python_function('repatch/marked_context.py', 'effective_delete_ids', 2, 9, 6).
python_function('repatch/marked_context.py', '_css_id_selector', 1, 4, 3).
python_function('repatch/marked_context.py', 'marked_css_selectors', 1, 6, 5).
python_function('repatch/marked_context.py', '_fragment_class_names', 1, 5, 7).
python_function('repatch/marked_context.py', '_collect_keep_selectors', 2, 11, 12).
python_function('repatch/marked_context.py', 'resolve_marked_selectors', 2, 16, 14).
python_function('repatch/marked_context.py', 'marked_scope_colors_css', 2, 12, 7).
python_function('repatch/marked_context.py', 'marked_scope_display_css', 2, 6, 3).
python_function('repatch/marked_context.py', 'marked_scope_shapes_css', 2, 6, 3).
python_function('repatch/marked_context.py', 'marked_scope_orientation_css', 2, 8, 6).
python_function('repatch/marked_context.py', 'restrict_scope_css_to_marks', 2, 14, 11).
python_function('repatch/marked_context.py', '_id_candidates', 1, 4, 7).
python_function('repatch/marked_context.py', '_normalize_label_text', 1, 2, 5).
python_function('repatch/marked_context.py', '_parse_attrs', 1, 3, 4).
python_function('repatch/marked_context.py', '_logical_id', 2, 8, 6).
python_function('repatch/marked_context.py', '_extract_balanced_html', 2, 10, 11).
python_function('repatch/marked_context.py', '_collect_match_candidates', 2, 6, 6).
python_function('repatch/marked_context.py', '_collect_button_candidates', 4, 3, 8).
python_function('repatch/marked_context.py', '_extract_and_format_fragment', 2, 3, 6).
python_function('repatch/marked_context.py', '_find_marked_subtrees', 2, 17, 13).
python_function('repatch/marked_context.py', '_selector_tokens', 1, 9, 9).
python_function('repatch/marked_context.py', '_filter_css_for_tokens', 2, 6, 6).
python_function('repatch/marked_context.py', '_collect_css_sources', 2, 7, 8).
python_function('repatch/marked_context.py', '_scope_semantics', 1, 4, 2).
python_function('repatch/marked_context.py', '_cap_text', 2, 2, 4).
python_function('repatch/marked_context.py', '_client_fragment_html', 2, 9, 5).
python_function('repatch/marked_context.py', '_assemble_marked_subtrees', 3, 4, 3).
python_function('repatch/marked_context.py', '_get_relevant_css', 3, 2, 6).
python_function('repatch/marked_context.py', '_format_context_body', 7, 14, 7).
python_function('repatch/marked_context.py', 'build_marked_element_context', 1, 11, 7).
python_function('repatch/marked_context.py', 'resolve_marked_llm_context', 1, 5, 2).
python_function('repatch/options.py', 'replace_html_title', 2, 3, 3).
python_function('repatch/options.py', 'normalize_html_body', 1, 2, 3).
python_function('repatch/options.py', 'html_files_distinct', 2, 3, 7).
python_function('repatch/options.py', 'sync_option_previews_from_workspace', 1, 10, 10).
python_function('repatch/options.py', 'enforce_deletes_on_option_previews', 2, 9, 12).
python_function('repatch/project_ir.py', '_clean_text', 1, 2, 3).
python_function('repatch/project_ir.py', 'build_project_ir', 1, 2, 5).
python_function('repatch/project_ir.py', 'summarize_project_ir', 1, 12, 7).
python_function('repatch/scope.py', 'goal_requests_column_layout', 1, 3, 3).
python_function('repatch/scope.py', 'ui_type_for_kind', 1, 11, 3).
python_function('repatch/scope.py', 'allowed_scope_ids', 1, 2, 3).
python_function('repatch/scope.py', 'default_scope_for_kind', 1, 3, 4).
python_function('repatch/scope.py', 'normalize_focus_scope', 2, 3, 5).
python_function('repatch/scope.py', 'offline_fast_scopes_for_kind', 1, 5, 2).
python_function('repatch/scope.py', 'scope_supports_offline_fast_path', 2, 1, 2).
python_function('repatch/scope.py', 'strip_scope_style', 1, 2, 1).
python_function('repatch/scope.py', '_scope_css', 2, 6, 0).
python_function('repatch/scope.py', '_calc_scope_css', 2, 7, 0).
python_function('repatch/scope.py', '_uses_web_scope_css', 2, 7, 1).
python_function('repatch/scope.py', '_web_display_scope_css', 1, 5, 1).
python_function('repatch/scope.py', '_web_shapes_scope_css', 1, 3, 2).
python_function('repatch/scope.py', '_web_orientation_scope_css', 1, 6, 2).
python_function('repatch/scope.py', '_web_scope_css', 2, 6, 3).
python_function('repatch/scope.py', '_resolve_scope_kind', 2, 10, 2).
python_function('repatch/scope.py', 'should_block_full_html_iterate', 3, 3, 3).
python_function('repatch/scope.py', '_bind_annotations_to_html', 3, 29, 19).
python_function('repatch/scope.py', '_get_scope_css', 4, 7, 5).
python_function('repatch/scope.py', '_inject_css_block', 2, 5, 4).
python_function('repatch/scope.py', 'inject_scope_style', 3, 27, 20).
python_function('repatch/scope.py', 'scoped_html_fragment', 3, 6, 6).
python_function('repatch/spatial.py', '_delete_match_keys', 1, 4, 5).
python_function('repatch/spatial.py', '_selectable_block_attrs', 1, 4, 3).
python_function('repatch/spatial.py', '_element_delete_candidates', 2, 6, 6).
python_function('repatch/spatial.py', 'apply_spatial_deletes_to_html', 2, 4, 11).
python_function('repatch/ui_patch.py', 'supports_llm_patch_scope', 2, 3, 1).
python_function('repatch/ui_patch.py', '_compact_html', 1, 3, 4).
python_function('repatch/ui_patch.py', '_patch_scope_rules', 1, 7, 4).
python_function('repatch/ui_patch.py', 'build_ui_patch_prompt', 1, 9, 5).
python_function('repatch/ui_patch.py', '_strip_json_fence', 1, 3, 4).
python_function('repatch/ui_patch.py', 'parse_ui_patch_response', 1, 6, 7).
python_function('repatch/ui_patch.py', '_safe_css', 1, 9, 7).
python_function('repatch/ui_patch.py', '_label_for', 3, 4, 4).
python_function('repatch/ui_patch.py', '_css_for', 1, 2, 3).
python_function('repatch/ui_patch.py', 'apply_ui_patch_options', 2, 25, 19).
python_function('repatch/web_preprocess.py', 'safe_read_under', 2, 5, 5).
python_function('repatch/web_preprocess.py', 'extract_inline_css', 1, 4, 3).
python_function('repatch/web_preprocess.py', 'extract_stylesheet_hrefs', 1, 7, 4).
python_function('repatch/web_preprocess.py', 'normalize_linked_paths', 2, 9, 6).
python_function('repatch/web_preprocess.py', '_rule_is_visual', 1, 6, 4).
python_function('repatch/web_preprocess.py', 'filter_visual_css', 1, 3, 4).
python_function('repatch/web_preprocess.py', 'extract_visual_css', 3, 8, 12).
python_function('repatch/web_preprocess.py', 'build_html_outline', 1, 3, 11).
python_function('repatch/web_preprocess.py', '_script_src_allowed_for_preview', 1, 4, 4).
python_function('repatch/web_preprocess.py', '_should_remove_preview_script', 1, 2, 3).
python_function('repatch/web_preprocess.py', 'sanitize_http_preview_html', 1, 2, 4).
python_function('repatch/web_preprocess.py', 'inject_http_preview_shim', 1, 4, 2).
python_function('repatch/web_preprocess.py', 'prepare_http_preview_html', 1, 1, 2).
python_function('repatch/web_preprocess.py', 'build_http_llm_context', 1, 7, 5).
python_function('repatch/web_preprocess.py', 'http_patch_llm_rules', 0, 1, 1).
python_function('tests/test_dom_patch.py', 'test_build_function_option_patches_returns_valid_abc', 0, 7, 3).
python_function('tests/test_dom_patch.py', 'test_build_function_option_patches_xpatches_delete_marks', 0, 8, 3).
python_function('tests/test_dom_patch.py', 'test_function_patch_context_is_compact_ir', 0, 4, 1).
python_function('tests/test_dom_patch.py', 'test_supports_function_patch_only_for_web_like_projects', 0, 5, 1).
python_function('tests/test_marked_context.py', 'test_build_marked_element_context_extracts_subtree_and_css', 0, 9, 1).
python_function('tests/test_marked_context.py', 'test_build_marked_element_context_uses_client_fragment_fallback', 0, 3, 1).
python_function('tests/test_marked_context.py', 'test_build_marked_element_context_returns_none_without_marks', 0, 2, 1).
python_function('tests/test_marked_context.py', 'test_build_marked_element_context_patch_mode_note', 0, 4, 1).
python_function('tests/test_marked_context.py', 'test_ui_patch_prompt_uses_marked_context_fragment', 0, 5, 2).
python_function('tests/test_marked_context.py', 'test_has_ui_marks', 0, 5, 1).
python_function('tests/test_marked_context.py', 'test_restrict_scope_css_to_marks_targets_delete_only', 0, 4, 1).
python_function('tests/test_marked_context.py', 'test_inject_scope_style_skips_global_css_for_keep_only_marks', 0, 2, 1).
python_function('tests/test_marked_context.py', 'test_inject_scope_style_scopes_css_to_delete_marks', 0, 5, 1).
python_function('tests/test_marked_context.py', 'test_resolve_marked_selectors_includes_classes', 0, 5, 3).
python_function('tests/test_marked_context.py', 'test_resolve_marked_selectors_narrow_excludes_keep_and_generic_classes', 0, 6, 1).
python_function('tests/test_marked_context.py', 'test_inject_scope_style_colors_mixed_keep_delete', 0, 8, 1).
python_function('tests/test_marked_context.py', 'test_marked_scope_colors_css_differs_by_variant', 0, 6, 1).
python_function('tests/test_marked_context.py', 'test_marked_scope_colors_css_overrides_all_descendants', 0, 5, 2).
python_function('tests/test_marked_context.py', 'test_resolve_marked_selectors_heading_text_id', 0, 4, 1).
python_function('tests/test_marked_context.py', 'test_resolve_marked_selectors_heading_text_entities', 0, 3, 1).
python_function('tests/test_marked_context.py', 'test_inject_scope_style_colors_overrides_inline_heading_color', 0, 6, 1).
python_function('tests/test_marked_context.py', 'test_inject_scope_style_colors_overrides_multiple_marked_headings', 0, 7, 1).
python_function('tests/test_marked_context.py', 'test_should_block_full_html_for_imported_marks', 0, 5, 1).
python_function('tests/test_marked_context.py', 'test_marked_css_selectors_includes_btn_prefix', 0, 3, 1).
python_function('tests/test_marked_context.py', 'test_goal_requests_column_layout_detects_polish_and_english', 0, 6, 1).
python_function('tests/test_marked_context.py', 'test_inject_scope_style_display_keeps_entry_content_typography', 0, 5, 3).
python_function('tests/test_marked_context.py', 'test_inject_scope_style_shapes_keeps_content_wrapper_radii', 0, 5, 3).
python_function('tests/test_marked_context.py', 'test_inject_scope_style_orientation_column_goal_keeps_layout_css', 0, 8, 3).
python_function('tests/test_options.py', 'test_replace_html_title_preserves_body', 0, 3, 1).
python_function('tests/test_options.py', 'test_sync_option_previews_from_workspace_applies_delete_ids', 1, 6, 4).
python_function('tests/test_options.py', 'test_sync_option_previews_uses_delete_resolver_only_for_none', 1, 3, 3).
python_function('tests/test_options.py', 'test_enforce_deletes_on_option_previews', 1, 5, 3).
python_function('tests/test_options.py', 'test_html_files_distinct_ignores_title', 1, 4, 2).
python_function('tests/test_spatial.py', 'test_apply_spatial_deletes_removes_dashboard_kpi_card', 0, 4, 1).
python_function('tests/test_spatial.py', 'test_apply_spatial_deletes_removes_only_marked_buttons', 0, 4, 2).
python_function('tests/test_ui_patch.py', 'test_build_ui_patch_prompt_is_json_contract', 0, 7, 1).
python_function('tests/test_ui_patch.py', 'test_parse_and_apply_ui_patch_response', 0, 6, 4).
python_function('tests/test_ui_patch.py', 'test_apply_ui_patch_restricts_visual_scope_to_red_marks', 0, 4, 1).
python_function('tests/test_ui_patch.py', 'test_apply_ui_patch_noops_visual_scope_with_keep_only_marks', 0, 3, 1).
python_function('tests/test_ui_patch.py', 'test_apply_ui_patch_rejects_unsafe_css', 0, 1, 2).
python_function('tests/test_ui_patch.py', 'test_apply_ui_patch_rejects_flow_breaking_css', 0, 1, 2).
python_function('tests/test_ui_patch.py', 'test_supports_llm_patch_scope', 0, 6, 1).

% ── Python Classes ───────────────────────────────────────
python_class('repatch/project_ir.py', '_ProjectIRParser').
python_method('_ProjectIRParser', '__init__', 0, 1, 2).
python_method('_ProjectIRParser', 'handle_starttag', 2, 5, 2).
python_method('_ProjectIRParser', '_classify_node', 4, 12, 4).
python_method('_ProjectIRParser', 'handle_endtag', 1, 8, 9).
python_method('_ProjectIRParser', 'handle_data', 1, 4, 2).
python_class('repatch/service.py', 'PatchSuggestion').
python_class('repatch/service.py', 'RepatchService').
python_method('RepatchService', '__init__', 2, 1, 0).
python_method('RepatchService', 'generate_patch_suggestions', 3, 4, 6).
python_method('RepatchService', '_normalize_scopes', 1, 6, 6).
python_method('RepatchService', '_build_user_prompt', 2, 1, 1).
python_method('RepatchService', '_parse_choice', 1, 2, 7).
python_method('RepatchService', '_choice_content', 1, 2, 1).
python_method('RepatchService', '_default_completion', 0, 1, 1).
python_class('repatch/web_preprocess.py', '_OutlineParser').
python_method('_OutlineParser', '__init__', 0, 1, 2).
python_method('_OutlineParser', '_keep_attr', 1, 2, 2).
python_method('_OutlineParser', 'handle_starttag', 2, 8, 3).
python_method('_OutlineParser', 'handle_endtag', 1, 4, 2).
python_method('_OutlineParser', 'handle_data', 1, 4, 3).
python_class('sdks/python/repatch_sdk.py', 'RepatchClient').
python_method('RepatchClient', '__init__', 1, 1, 0).
python_method('RepatchClient', 'on_patch', 1, 1, 1).
python_method('RepatchClient', 'start', 0, 1, 2).
python_method('RepatchClient', '_run_event_loop', 0, 1, 4).
python_method('RepatchClient', '_connect_and_listen', 0, 7, 7).
python_method('RepatchClient', '_trigger_listeners', 1, 3, 2).
python_method('RepatchClient', 'send_patch', 1, 3, 4).
python_class('tests/test_service.py', 'RepatchServiceTests').
python_method('RepatchServiceTests', 'test_rejects_invalid_scope', 0, 1, 3).
python_method('RepatchServiceTests', 'test_returns_three_variants_from_completion', 0, 1, 7).

% ── Dependencies ─────────────────────────────────────────

% ── Makefile Targets ─────────────────────────────────────

% ── Taskfile Tasks ───────────────────────────────────────

% ── Environment Variables ────────────────────────────────
env_variable('OPENROUTER_API_KEY', '*(not set)*', 'Required: OpenRouter API key (https://openrouter.ai/keys)').
env_variable('LLM_MODEL', 'openrouter/qwen/qwen3-coder-next', 'Model (default: openrouter/qwen/qwen3-coder-next)').
env_variable('PFIX_AUTO_APPLY', 'true', 'true = apply fixes without asking').
env_variable('PFIX_AUTO_INSTALL_DEPS', 'true', 'true = auto pip/uv install').
env_variable('PFIX_AUTO_RESTART', 'false', 'true = os.execv restart after fix').
env_variable('PFIX_MAX_RETRIES', '3', '').
env_variable('PFIX_DRY_RUN', 'false', '').
env_variable('PFIX_ENABLED', 'true', '').
env_variable('PFIX_GIT_COMMIT', 'false', 'true = auto-commit fixes').
env_variable('PFIX_GIT_PREFIX', 'pfix:', 'commit message prefix').
env_variable('PFIX_CREATE_BACKUPS', 'false', 'false = disable .pfix_backups/ directory').

% ── TestQL Scenarios ─────────────────────────────────────
testql_scenario('generated-cli-tests.testql.toon.yaml', 'cli').
testql_scenario('generated-from-pytests.testql.toon.yaml', 'integration').

% ── Semantic Facts from SUMD.md ──────────────────────────
sumd_declared_file('app.doql.less', 'doql').
sumd_declared_file('testql-scenarios/generated-cli-tests.testql.toon.yaml', 'testql').
sumd_declared_file('testql-scenarios/generated-from-pytests.testql.toon.yaml', 'testql').
sumd_declared_file('project/map.toon.yaml', 'analysis').
sumd_declared_file('project/logic.pl', 'analysis').
sumd_declared_file('project/calls.toon.yaml', 'analysis').

