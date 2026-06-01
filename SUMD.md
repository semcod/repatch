# repatch

Scope-based HTML/CSS/DOM patch utilities and LLM patch helpers

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Interfaces](#interfaces)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Environment Variables (`.env.example`)](#environment-variables-envexample)
- [Release Management (`goal.yaml`)](#release-management-goalyaml)
- [Code Analysis](#code-analysis)
- [Source Map](#source-map)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Intent](#intent)

## Metadata

- **name**: `repatch`
- **version**: `0.2.12`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, testql(2), app.doql.less, goal.yaml, .env.example, src(10 mod), project/(3 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: repatch;
  version: 0.2.12;
}

dependencies {
  runtime: litellm>=1.40.0;
  dev: "pytest>=7.0, goal>=2.1.0, costs>=0.1.20, pfix>=0.1.60";
}

deploy {
  target: pip;
}

environment[name="local"] {
  runtime: python;
  env_file: .env;
  python_version: >=3.10;
}
```

### Source Modules

- `repatch.css`
- `repatch.dom_patch`
- `repatch.marked_context`
- `repatch.options`
- `repatch.project_ir`
- `repatch.scope`
- `repatch.service`
- `repatch.spatial`
- `repatch.ui_patch`
- `repatch.web_preprocess`

## Interfaces

### testql Scenarios

#### `testql-scenarios/generated-cli-tests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-cli-tests.testql.toon.yaml
# SCENARIO: CLI Command Tests
# TYPE: cli
# GENERATED: true

CONFIG[2]{key, value}:
  cli_command, python -m repatch
  timeout_ms, 10000

# Test 1: CLI help command
SHELL "python -m repatch --help" 5000
ASSERT_EXIT_CODE 0
ASSERT_STDOUT_CONTAINS "usage"

# Test 2: CLI version command
SHELL "python -m repatch --version" 5000
ASSERT_EXIT_CODE 0

# Test 3: CLI main workflow (dry-run)
SHELL "python -m repatch --help" 10000
ASSERT_EXIT_CODE 0
```

#### `testql-scenarios/generated-from-pytests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-from-pytests.testql.toon.yaml
# SCENARIO: Auto-generated from Python Tests
# TYPE: integration
# GENERATED: true

CONFIG[2]{key, value}:
  base_url, ${api_url:-http://localhost:8101}
  timeout_ms, 10000

# NOTE: Python pytest files were detected but no convertible HTTP calls or assertions were found.
# To run pytest tests directly, use: pytest <test_file>
```

## Configuration

```yaml
project:
  name: repatch
  version: 0.2.12
  env: local
```

## Dependencies

### Runtime

```text markpact:deps python
litellm>=1.40.0
```

### Development

```text markpact:deps python scope=dev
pytest>=7.0
goal>=2.1.0
costs>=0.1.20
pfix>=0.1.60
```

## Deployment

```bash markpact:run
pip install repatch

# development install
pip install -e .[dev]
```

## Environment Variables (`.env.example`)

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | `*(not set)*` | Required: OpenRouter API key (https://openrouter.ai/keys) |
| `LLM_MODEL` | `openrouter/qwen/qwen3-coder-next` | Model (default: openrouter/qwen/qwen3-coder-next) |
| `PFIX_AUTO_APPLY` | `true` | true = apply fixes without asking |
| `PFIX_AUTO_INSTALL_DEPS` | `true` | true = auto pip/uv install |
| `PFIX_AUTO_RESTART` | `false` | true = os.execv restart after fix |
| `PFIX_MAX_RETRIES` | `3` |  |
| `PFIX_DRY_RUN` | `false` |  |
| `PFIX_ENABLED` | `true` |  |
| `PFIX_GIT_COMMIT` | `false` | true = auto-commit fixes |
| `PFIX_GIT_PREFIX` | `pfix:` | commit message prefix |
| `PFIX_CREATE_BACKUPS` | `false` | false = disable .pfix_backups/ directory |

## Release Management (`goal.yaml`)

- **versioning**: `semver`
- **commits**: `conventional` scope=`repatch`
- **changelog**: `keep-a-changelog`
- **build strategies**: `python`, `nodejs`, `rust`
- **version files**: `VERSION`, `pyproject.toml:version`, `venv/lib/python3.13/site-packages/cryptography/__init__.py:__version__`

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# repatch | 23f 4248L | python:19,shell:2,less:1,javascript:1 | 2026-06-01
# stats: 159 func | 6 cls | 23 mod | CC̄=5.6 | critical:17 | cycles:0
# alerts[5]: CC _bind_annotations_to_html=29; CC inject_scope_style=27; CC apply_ui_patch_options=25; CC _find_marked_subtrees=17; CC resolve_marked_selectors=16
# hotspots[5]: inject_scope_style fan=20; _bind_annotations_to_html fan=19; apply_ui_patch_options fan=19; _patch_function_targets fan=18; validate_css_safety fan=15
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[23]:
  app.doql.less,22
  project.sh,50
  repatch/__init__.py,124
  repatch/css.py,71
  repatch/dom_patch.py,316
  repatch/marked_context.py,697
  repatch/options.py,141
  repatch/project_ir.py,133
  repatch/scope.py,648
  repatch/service.py,106
  repatch/spatial.py,109
  repatch/ui_patch.py,268
  repatch/web_preprocess.py,398
  sdks/js/repatch-sdk.js,187
  sdks/python/repatch_sdk.py,74
  tests/test_dom_patch.py,74
  tests/test_marked_context.py,442
  tests/test_options.py,81
  tests/test_service.py,54
  tests/test_spatial.py,30
  tests/test_ui_patch.py,157
  tests/test_web_preprocess.py,64
  tree.sh,2
D:
  repatch/__init__.py:
  repatch/css.py:
    e: _strip_css_comments,_selector_is_runtime_only,split_css_rules,validate_css_safety
    _strip_css_comments(css)
    _selector_is_runtime_only(selector)
    split_css_rules(css)
    validate_css_safety(css)
  repatch/dom_patch.py:
    e: supports_function_patch,build_function_patch_context,_strip_existing_patch,_goal_label,_variant_section,_patch_style,_inject_into_head,_inject_into_body,_target_candidates,_strip_tags,_set_attr,_attrs_from_open_tag,_matches_target,_variant_target_label,_variant_href,_patch_function_targets,_default_prepare_html,_default_finalize_html,build_function_option_patches
    supports_function_patch(scope;project_kind)
    build_function_patch_context(html_text)
    _strip_existing_patch(text)
    _goal_label(user_goal)
    _variant_section(variant;user_goal;ir)
    _patch_style()
    _inject_into_head(text;style)
    _inject_into_body(text;section)
    _target_candidates(element_id)
    _strip_tags(text)
    _set_attr(open_tag;attr;value)
    _attrs_from_open_tag(open_tag)
    _matches_target(open_tag;inner;wanted)
    _variant_target_label(variant;user_goal)
    _variant_href(variant;original_href)
    _patch_function_targets(html_text;delete_els;variant;user_goal)
    _default_prepare_html(html)
    _default_finalize_html(html)
    build_function_option_patches(html_text)
  repatch/marked_context.py:
    e: has_ui_marks,effective_delete_ids,_css_id_selector,marked_css_selectors,_fragment_class_names,_collect_keep_selectors,resolve_marked_selectors,marked_scope_colors_css,marked_scope_display_css,marked_scope_shapes_css,marked_scope_orientation_css,restrict_scope_css_to_marks,_id_candidates,_normalize_label_text,_parse_attrs,_logical_id,_extract_balanced_html,_collect_match_candidates,_collect_button_candidates,_extract_and_format_fragment,_find_marked_subtrees,_selector_tokens,_filter_css_for_tokens,_collect_css_sources,_scope_semantics,_cap_text,_client_fragment_html,_assemble_marked_subtrees,_get_relevant_css,_format_context_body,build_marked_element_context,resolve_marked_llm_context
    has_ui_marks(keep_els;delete_els)
    effective_delete_ids(delete_els;keep_els)
    _css_id_selector(token)
    marked_css_selectors(element_ids)
    _fragment_class_names(fragment)
    _collect_keep_selectors(html;keep_ids)
    resolve_marked_selectors(html;element_ids)
    marked_scope_colors_css(selectors;variant)
    marked_scope_display_css(selectors;variant)
    marked_scope_shapes_css(selectors;variant)
    marked_scope_orientation_css(selectors;variant)
    restrict_scope_css_to_marks(css;delete_ids)
    _id_candidates(element_id)
    _normalize_label_text(text)
    _parse_attrs(attr_text)
    _logical_id(tag;attrs)
    _extract_balanced_html(html;start)
    _collect_match_candidates(tag;attrs)
    _collect_button_candidates(tag;attrs;match;raw_html)
    _extract_and_format_fragment(text;start)
    _find_marked_subtrees(html;marked_ids)
    _selector_tokens(subtrees)
    _filter_css_for_tokens(css;tokens)
    _collect_css_sources(html;ui_profile)
    _scope_semantics(scope)
    _cap_text(text;limit)
    _client_fragment_html(client_fragments;element_id)
    _assemble_marked_subtrees(html;marked_ids;client_fragments)
    _get_relevant_css(html;subtrees;ui_profile)
    _format_context_body(keep;delete;marked_ids;subtrees;css;scope;ui_profile)
    build_marked_element_context(html)
    resolve_marked_llm_context(html)
  repatch/options.py:
    e: replace_html_title,normalize_html_body,html_files_distinct,sync_option_previews_from_workspace,enforce_deletes_on_option_previews
    replace_html_title(html;title)
    normalize_html_body(html)
    html_files_distinct(base_dir;names)
    sync_option_previews_from_workspace(cinema_dir)
    enforce_deletes_on_option_previews(cinema_dir;delete_ids)
  repatch/project_ir.py:
    e: _clean_text,build_project_ir,summarize_project_ir,_ProjectIRParser
    _ProjectIRParser: __init__(0),handle_starttag(2),_classify_node(4),handle_endtag(1),handle_data(1)
    _clean_text(text)
    build_project_ir(html)
    summarize_project_ir(ir)
  repatch/scope.py:
    e: goal_requests_column_layout,ui_type_for_kind,allowed_scope_ids,default_scope_for_kind,normalize_focus_scope,offline_fast_scopes_for_kind,scope_supports_offline_fast_path,strip_scope_style,_scope_css,_calc_scope_css,_uses_web_scope_css,_web_display_scope_css,_web_shapes_scope_css,_web_orientation_scope_css,_web_scope_css,_resolve_scope_kind,should_block_full_html_iterate,_bind_annotations_to_html,_get_scope_css,_inject_css_block,inject_scope_style,scoped_html_fragment
    goal_requests_column_layout(user_goal)
    ui_type_for_kind(kind)
    allowed_scope_ids(project_kind)
    default_scope_for_kind(project_kind)
    normalize_focus_scope(scope;project_kind)
    offline_fast_scopes_for_kind(project_kind)
    scope_supports_offline_fast_path(scope;project_kind)
    strip_scope_style(html)
    _scope_css(scope;variant)
    _calc_scope_css(scope;variant)
    _uses_web_scope_css(inferred;html)
    _web_display_scope_css(variant)
    _web_shapes_scope_css(variant)
    _web_orientation_scope_css(variant)
    _web_scope_css(scope;variant)
    _resolve_scope_kind(project_kind;html)
    should_block_full_html_iterate(project_kind;keep_els;delete_els)
    _bind_annotations_to_html(html;keep_ids;delete_ids)
    _get_scope_css(inferred;html;scope;variant)
    _inject_css_block(html;css)
    inject_scope_style(html;scope;variant)
    scoped_html_fragment(html;focus_scope;project_kind)
  repatch/service.py:
    e: PatchSuggestion,RepatchService
    PatchSuggestion:
    RepatchService: __init__(2),generate_patch_suggestions(3),_normalize_scopes(1),_build_user_prompt(2),_parse_choice(1),_choice_content(1),_default_completion(0)
  repatch/spatial.py:
    e: _delete_match_keys,_selectable_block_attrs,_element_delete_candidates,apply_spatial_deletes_to_html
    _delete_match_keys(element_id)
    _selectable_block_attrs(attrs)
    _element_delete_candidates(attrs;inner_text)
    apply_spatial_deletes_to_html(html;delete_ids)
  repatch/ui_patch.py:
    e: supports_llm_patch_scope,_compact_html,_patch_scope_rules,build_ui_patch_prompt,_strip_json_fence,parse_ui_patch_response,_safe_css,_label_for,_css_for,apply_ui_patch_options
    supports_llm_patch_scope(scope;project_kind)
    _compact_html(html)
    _patch_scope_rules(scope)
    build_ui_patch_prompt(html)
    _strip_json_fence(text)
    parse_ui_patch_response(text)
    _safe_css(css)
    _label_for(filename;item;fallback)
    _css_for(item)
    apply_ui_patch_options(html;patch)
  repatch/web_preprocess.py:
    e: safe_read_under,extract_inline_css,extract_stylesheet_hrefs,normalize_linked_paths,_rule_is_visual,filter_visual_css,extract_visual_css,build_html_outline,_script_src_allowed_for_preview,_should_remove_preview_script,sanitize_http_preview_html,inject_http_preview_shim,prepare_http_preview_html,build_http_llm_context,http_patch_llm_rules,_OutlineParser
    _OutlineParser: __init__(0),_keep_attr(1),handle_starttag(2),handle_endtag(1),handle_data(1)
    safe_read_under(base_dir;rel_path)
    extract_inline_css(html)
    extract_stylesheet_hrefs(html)
    normalize_linked_paths(linked_css_paths;html)
    _rule_is_visual(rule)
    filter_visual_css(css)
    extract_visual_css(html;linked_css_paths;source_dir)
    build_html_outline(html)
    _script_src_allowed_for_preview(src)
    _should_remove_preview_script(tag)
    sanitize_http_preview_html(html)
    inject_http_preview_shim(html)
    prepare_http_preview_html(html)
    build_http_llm_context(artifacts)
    http_patch_llm_rules()
  sdks/python/repatch_sdk.py:
    e: RepatchClient
    RepatchClient: __init__(1),on_patch(1),start(0),_run_event_loop(0),_connect_and_listen(0),_trigger_listeners(1),send_patch(1)  # Repatch Python Client SDK (v1.0.0)
  tests/test_dom_patch.py:
    e: test_build_function_option_patches_returns_valid_abc,test_build_function_option_patches_xpatches_delete_marks,test_function_patch_context_is_compact_ir,test_supports_function_patch_only_for_web_like_projects
    test_build_function_option_patches_returns_valid_abc()
    test_build_function_option_patches_xpatches_delete_marks()
    test_function_patch_context_is_compact_ir()
    test_supports_function_patch_only_for_web_like_projects()
  tests/test_marked_context.py:
    e: test_build_marked_element_context_extracts_subtree_and_css,test_build_marked_element_context_uses_client_fragment_fallback,test_build_marked_element_context_returns_none_without_marks,test_build_marked_element_context_patch_mode_note,test_ui_patch_prompt_uses_marked_context_fragment,test_has_ui_marks,test_restrict_scope_css_to_marks_targets_delete_only,test_inject_scope_style_skips_global_css_for_keep_only_marks,test_inject_scope_style_scopes_css_to_delete_marks,test_resolve_marked_selectors_includes_classes,test_resolve_marked_selectors_narrow_excludes_keep_and_generic_classes,test_inject_scope_style_colors_mixed_keep_delete,test_marked_scope_colors_css_differs_by_variant,test_marked_scope_colors_css_overrides_all_descendants,test_resolve_marked_selectors_heading_text_id,test_resolve_marked_selectors_heading_text_entities,test_inject_scope_style_colors_overrides_inline_heading_color,test_inject_scope_style_colors_overrides_multiple_marked_headings,test_should_block_full_html_for_imported_marks,test_marked_css_selectors_includes_btn_prefix,test_goal_requests_column_layout_detects_polish_and_english,test_inject_scope_style_display_keeps_entry_content_typography,test_inject_scope_style_shapes_keeps_content_wrapper_radii,test_inject_scope_style_orientation_column_goal_keeps_layout_css
    test_build_marked_element_context_extracts_subtree_and_css()
    test_build_marked_element_context_uses_client_fragment_fallback()
    test_build_marked_element_context_returns_none_without_marks()
    test_build_marked_element_context_patch_mode_note()
    test_ui_patch_prompt_uses_marked_context_fragment()
    test_has_ui_marks()
    test_restrict_scope_css_to_marks_targets_delete_only()
    test_inject_scope_style_skips_global_css_for_keep_only_marks()
    test_inject_scope_style_scopes_css_to_delete_marks()
    test_resolve_marked_selectors_includes_classes()
    test_resolve_marked_selectors_narrow_excludes_keep_and_generic_classes()
    test_inject_scope_style_colors_mixed_keep_delete()
    test_marked_scope_colors_css_differs_by_variant()
    test_marked_scope_colors_css_overrides_all_descendants()
    test_resolve_marked_selectors_heading_text_id()
    test_resolve_marked_selectors_heading_text_entities()
    test_inject_scope_style_colors_overrides_inline_heading_color()
    test_inject_scope_style_colors_overrides_multiple_marked_headings()
    test_should_block_full_html_for_imported_marks()
    test_marked_css_selectors_includes_btn_prefix()
    test_goal_requests_column_layout_detects_polish_and_english()
    test_inject_scope_style_display_keeps_entry_content_typography()
    test_inject_scope_style_shapes_keeps_content_wrapper_radii()
    test_inject_scope_style_orientation_column_goal_keeps_layout_css()
  tests/test_options.py:
    e: test_replace_html_title_preserves_body,test_sync_option_previews_from_workspace_applies_delete_ids,test_sync_option_previews_uses_delete_resolver_only_for_none,test_enforce_deletes_on_option_previews,test_html_files_distinct_ignores_title
    test_replace_html_title_preserves_body()
    test_sync_option_previews_from_workspace_applies_delete_ids(tmp_path)
    test_sync_option_previews_uses_delete_resolver_only_for_none(tmp_path)
    test_enforce_deletes_on_option_previews(tmp_path)
    test_html_files_distinct_ignores_title(tmp_path)
  tests/test_service.py:
    e: RepatchServiceTests
    RepatchServiceTests: test_rejects_invalid_scope(0),test_returns_three_variants_from_completion(0)
  tests/test_spatial.py:
    e: test_apply_spatial_deletes_removes_dashboard_kpi_card,test_apply_spatial_deletes_removes_only_marked_buttons
    test_apply_spatial_deletes_removes_dashboard_kpi_card()
    test_apply_spatial_deletes_removes_only_marked_buttons()
  tests/test_ui_patch.py:
    e: test_build_ui_patch_prompt_is_json_contract,test_parse_and_apply_ui_patch_response,test_apply_ui_patch_restricts_visual_scope_to_red_marks,test_apply_ui_patch_noops_visual_scope_with_keep_only_marks,test_apply_ui_patch_rejects_unsafe_css,test_apply_ui_patch_rejects_flow_breaking_css,test_supports_llm_patch_scope
    test_build_ui_patch_prompt_is_json_contract()
    test_parse_and_apply_ui_patch_response()
    test_apply_ui_patch_restricts_visual_scope_to_red_marks()
    test_apply_ui_patch_noops_visual_scope_with_keep_only_marks()
    test_apply_ui_patch_rejects_unsafe_css()
    test_apply_ui_patch_rejects_flow_breaking_css()
    test_supports_llm_patch_scope()
  tests/test_web_preprocess.py:
    e: test_extract_visual_css_keeps_patch_relevant_rules,test_build_html_outline_strips_scripts_and_text,test_prepare_http_preview_html_blocks_cross_origin_runtime
    test_extract_visual_css_keeps_patch_relevant_rules(tmp_path)
    test_build_html_outline_strips_scripts_and_text()
    test_prepare_http_preview_html_blocks_cross_origin_runtime()
```

### `project/logic.pl`

```prolog markpact:analysis path=project/logic.pl
% ── Project Metadata ─────────────────────────────────────
project_metadata('repatch', '0.2.12', 'python').

% ── Project Files ────────────────────────────────────────
project_file('app.doql.less', 22, 'less').
project_file('project.sh', 50, 'shell').
project_file('repatch/__init__.py', 124, 'python').
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
project_file('tests/test_web_preprocess.py', 64, 'python').
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
python_function('tests/test_web_preprocess.py', 'test_extract_visual_css_keeps_patch_relevant_rules', 1, 5, 3).
python_function('tests/test_web_preprocess.py', 'test_build_html_outline_strips_scripts_and_text', 0, 5, 2).
python_function('tests/test_web_preprocess.py', 'test_prepare_http_preview_html_blocks_cross_origin_runtime', 0, 5, 2).

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
```

## Source Map

*Top 5 modules by symbol density — signatures for LLM orientation.*

### `repatch.marked_context` (`repatch/marked_context.py`)

```python
def has_ui_marks(keep_els, delete_els)  # CC=8, fan=3
def effective_delete_ids(delete_els, keep_els)  # CC=9, fan=6
def _css_id_selector(token)  # CC=4, fan=3
def marked_css_selectors(element_ids)  # CC=6, fan=5
def _fragment_class_names(fragment)  # CC=5, fan=7
def _collect_keep_selectors(html, keep_ids)  # CC=11, fan=12 ⚠
def resolve_marked_selectors(html, element_ids)  # CC=16, fan=14 ⚠
def marked_scope_colors_css(selectors, variant)  # CC=12, fan=7 ⚠
def marked_scope_display_css(selectors, variant)  # CC=6, fan=3
def marked_scope_shapes_css(selectors, variant)  # CC=6, fan=3
def marked_scope_orientation_css(selectors, variant)  # CC=8, fan=6
def restrict_scope_css_to_marks(css, delete_ids)  # CC=14, fan=11 ⚠
def _id_candidates(element_id)  # CC=4, fan=7
def _normalize_label_text(text)  # CC=2, fan=5
def _parse_attrs(attr_text)  # CC=3, fan=4
def _logical_id(tag, attrs)  # CC=8, fan=6
def _extract_balanced_html(html, start)  # CC=10, fan=11 ⚠
def _collect_match_candidates(tag, attrs)  # CC=6, fan=6
def _collect_button_candidates(tag, attrs, match, raw_html)  # CC=3, fan=8
def _extract_and_format_fragment(text, start)  # CC=3, fan=6
def _find_marked_subtrees(html, marked_ids)  # CC=17, fan=13 ⚠
def _selector_tokens(subtrees)  # CC=9, fan=9
def _filter_css_for_tokens(css, tokens)  # CC=6, fan=6
def _collect_css_sources(html, ui_profile)  # CC=7, fan=8
def _scope_semantics(scope)  # CC=4, fan=2
def _cap_text(text, limit)  # CC=2, fan=4
def _client_fragment_html(client_fragments, element_id)  # CC=9, fan=5
def _assemble_marked_subtrees(html, marked_ids, client_fragments)  # CC=4, fan=3
def _get_relevant_css(html, subtrees, ui_profile)  # CC=2, fan=6
def _format_context_body(keep, delete, marked_ids, subtrees, css, scope, ui_profile)  # CC=14, fan=7 ⚠
def build_marked_element_context(html)  # CC=11, fan=7 ⚠
def resolve_marked_llm_context(html)  # CC=5, fan=2
```

### `repatch.scope` (`repatch/scope.py`)

```python
def goal_requests_column_layout(user_goal)  # CC=3, fan=3
def ui_type_for_kind(kind)  # CC=11, fan=3 ⚠
def allowed_scope_ids(project_kind)  # CC=2, fan=3
def default_scope_for_kind(project_kind)  # CC=3, fan=4
def normalize_focus_scope(scope, project_kind)  # CC=3, fan=5
def offline_fast_scopes_for_kind(project_kind)  # CC=5, fan=2
def scope_supports_offline_fast_path(scope, project_kind)  # CC=1, fan=2
def strip_scope_style(html)  # CC=2, fan=1
def _scope_css(scope, variant)  # CC=6, fan=0
def _calc_scope_css(scope, variant)  # CC=7, fan=0
def _uses_web_scope_css(inferred, html)  # CC=7, fan=1
def _web_display_scope_css(variant)  # CC=5, fan=1
def _web_shapes_scope_css(variant)  # CC=3, fan=2
def _web_orientation_scope_css(variant)  # CC=6, fan=2
def _web_scope_css(scope, variant)  # CC=6, fan=3
def _resolve_scope_kind(project_kind, html)  # CC=10, fan=2 ⚠
def should_block_full_html_iterate(project_kind, keep_els, delete_els)  # CC=3, fan=3
def _bind_annotations_to_html(html, keep_ids, delete_ids)  # CC=29, fan=19 ⚠
def _get_scope_css(inferred, html, scope, variant)  # CC=7, fan=5
def _inject_css_block(html, css)  # CC=5, fan=4
def inject_scope_style(html, scope, variant)  # CC=27, fan=20 ⚠
def scoped_html_fragment(html, focus_scope, project_kind)  # CC=6, fan=6
```

### `repatch.web_preprocess` (`repatch/web_preprocess.py`)

```python
def safe_read_under(base_dir, rel_path)  # CC=5, fan=5
def extract_inline_css(html)  # CC=4, fan=3
def extract_stylesheet_hrefs(html)  # CC=7, fan=4
def normalize_linked_paths(linked_css_paths, html)  # CC=9, fan=6
def _rule_is_visual(rule)  # CC=6, fan=4
def filter_visual_css(css)  # CC=3, fan=4
def extract_visual_css(html, linked_css_paths, source_dir)  # CC=8, fan=12
def build_html_outline(html)  # CC=3, fan=11
def _script_src_allowed_for_preview(src)  # CC=4, fan=4
def _should_remove_preview_script(tag)  # CC=2, fan=3
def sanitize_http_preview_html(html)  # CC=2, fan=4
def inject_http_preview_shim(html)  # CC=4, fan=2
def prepare_http_preview_html(html)  # CC=1, fan=2
def build_http_llm_context(artifacts)  # CC=7, fan=5
def http_patch_llm_rules()  # CC=1, fan=1
class _OutlineParser:
    def __init__()  # CC=1
    def _keep_attr(name)  # CC=2
    def handle_starttag(tag, attrs)  # CC=8
    def handle_endtag(tag)  # CC=4
    def handle_data(data)  # CC=4
```

### `repatch.dom_patch` (`repatch/dom_patch.py`)

```python
def supports_function_patch(scope, project_kind)  # CC=4, fan=2
def build_function_patch_context(html_text)  # CC=2, fan=3
def _strip_existing_patch(text)  # CC=2, fan=2
def _goal_label(user_goal)  # CC=3, fan=2
def _variant_section(variant, user_goal, ir)  # CC=3, fan=5
def _patch_style()  # CC=1, fan=0
def _inject_into_head(text, style)  # CC=4, fan=4
def _inject_into_body(text, section)  # CC=2, fan=2
def _target_candidates(element_id)  # CC=4, fan=6
def _strip_tags(text)  # CC=2, fan=2
def _set_attr(open_tag, attr, value)  # CC=2, fan=4
def _attrs_from_open_tag(open_tag)  # CC=2, fan=5
def _matches_target(open_tag, inner, wanted)  # CC=4, fan=6
def _variant_target_label(variant, user_goal)  # CC=3, fan=1
def _variant_href(variant, original_href)  # CC=4, fan=4
def _patch_function_targets(html_text, delete_els, variant, user_goal)  # CC=6, fan=18
def _default_prepare_html(html)  # CC=3, fan=2
def _default_finalize_html(html)  # CC=1, fan=0
def build_function_option_patches(html_text)  # CC=12, fan=15 ⚠
```

### `repatch.ui_patch` (`repatch/ui_patch.py`)

```python
def supports_llm_patch_scope(scope, project_kind)  # CC=3, fan=1
def _compact_html(html)  # CC=3, fan=4
def _patch_scope_rules(scope)  # CC=7, fan=4
def build_ui_patch_prompt(html)  # CC=9, fan=5
def _strip_json_fence(text)  # CC=3, fan=4
def parse_ui_patch_response(text)  # CC=6, fan=7
def _safe_css(css)  # CC=9, fan=7
def _label_for(filename, item, fallback)  # CC=4, fan=4
def _css_for(item)  # CC=2, fan=3
def apply_ui_patch_options(html, patch)  # CC=25, fan=19 ⚠
```

## Call Graph

*107 nodes · 116 edges · 11 modules · CC̄=5.2*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `_bind_annotations_to_html` *(in repatch.scope)* | 29 ⚠ | 1 | 44 | **45** |
| `apply_spatial_deletes_to_html` *(in repatch.spatial)* | 4 | 2 | 29 | **31** |
| `apply_ui_patch_options` *(in repatch.ui_patch)* | 25 ⚠ | 0 | 31 | **31** |
| `inject_scope_style` *(in repatch.scope)* | 27 ⚠ | 0 | 29 | **29** |
| `validate_css_safety` *(in repatch.css)* | 14 ⚠ | 1 | 26 | **27** |
| `resolve_marked_selectors` *(in repatch.marked_context)* | 16 ⚠ | 3 | 23 | **26** |
| `_find_marked_subtrees` *(in repatch.marked_context)* | 17 ⚠ | 3 | 23 | **26** |
| `_patch_function_targets` *(in repatch.dom_patch)* | 6 | 1 | 24 | **25** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/repatch
# generated in 0.05s
# nodes: 107 | edges: 116 | modules: 11
# CC̄=5.2

HUBS[20]:
  repatch.scope._bind_annotations_to_html
    CC=29  in:1  out:44  total:45
  repatch.spatial.apply_spatial_deletes_to_html
    CC=4  in:2  out:29  total:31
  repatch.ui_patch.apply_ui_patch_options
    CC=25  in:0  out:31  total:31
  repatch.scope.inject_scope_style
    CC=27  in:0  out:29  total:29
  repatch.css.validate_css_safety
    CC=14  in:1  out:26  total:27
  repatch.marked_context.resolve_marked_selectors
    CC=16  in:3  out:23  total:26
  repatch.marked_context._find_marked_subtrees
    CC=17  in:3  out:23  total:26
  repatch.dom_patch._patch_function_targets
    CC=6  in:1  out:24  total:25
  repatch.marked_context._id_candidates
    CC=4  in:10  out:13  total:23
  repatch.project_ir.summarize_project_ir
    CC=12  in:1  out:21  total:22
  repatch.marked_context._collect_keep_selectors
    CC=11  in:1  out:19  total:20
  repatch.web_preprocess.extract_visual_css
    CC=8  in:0  out:19  total:19
  repatch.marked_context.restrict_scope_css_to_marks
    CC=14  in:2  out:17  total:19
  repatch.marked_context._extract_balanced_html
    CC=10  in:1  out:18  total:19
  repatch.options.sync_option_previews_from_workspace
    CC=10  in:0  out:17  total:17
  sdks.js.repatch-sdk.RepatchSDK.apply
    CC=12  in:3  out:14  total:17
  repatch.dom_patch.build_function_option_patches
    CC=12  in:0  out:16  total:16
  repatch.marked_context._format_context_body
    CC=14  in:1  out:15  total:16
  repatch.marked_context._selector_tokens
    CC=9  in:1  out:14  total:15
  repatch.marked_context.build_marked_element_context
    CC=11  in:1  out:13  total:14

MODULES:
  repatch.css  [4 funcs]
    _selector_is_runtime_only  CC=2  out:2
    _strip_css_comments  CC=2  out:2
    split_css_rules  CC=9  out:6
    validate_css_safety  CC=14  out:26
  repatch.dom_patch  [14 funcs]
    _attrs_from_open_tag  CC=2  out:6
    _goal_label  CC=3  out:2
    _inject_into_body  CC=2  out:3
    _inject_into_head  CC=4  out:5
    _matches_target  CC=4  out:7
    _patch_function_targets  CC=6  out:24
    _strip_existing_patch  CC=2  out:3
    _strip_tags  CC=2  out:3
    _target_candidates  CC=4  out:9
    _variant_section  CC=3  out:11
  repatch.marked_context  [27 funcs]
    _assemble_marked_subtrees  CC=4  out:3
    _cap_text  CC=2  out:4
    _client_fragment_html  CC=9  out:10
    _collect_button_candidates  CC=3  out:8
    _collect_css_sources  CC=7  out:10
    _collect_keep_selectors  CC=11  out:19
    _collect_match_candidates  CC=6  out:11
    _css_id_selector  CC=4  out:3
    _extract_and_format_fragment  CC=3  out:6
    _extract_balanced_html  CC=10  out:18
  repatch.options  [4 funcs]
    enforce_deletes_on_option_previews  CC=9  out:14
    html_files_distinct  CC=3  out:7
    normalize_html_body  CC=2  out:3
    sync_option_previews_from_workspace  CC=10  out:17
  repatch.project_ir  [6 funcs]
    _classify_node  CC=12  out:10
    handle_data  CC=4  out:2
    handle_endtag  CC=8  out:11
    _clean_text  CC=2  out:3
    build_project_ir  CC=2  out:8
    summarize_project_ir  CC=12  out:21
  repatch.scope  [20 funcs]
    _bind_annotations_to_html  CC=29  out:44
    _calc_scope_css  CC=7  out:0
    _get_scope_css  CC=7  out:7
    _inject_css_block  CC=5  out:4
    _resolve_scope_kind  CC=10  out:3
    _scope_css  CC=6  out:0
    _web_display_scope_css  CC=5  out:3
    _web_orientation_scope_css  CC=6  out:2
    _web_scope_css  CC=6  out:3
    _web_shapes_scope_css  CC=3  out:2
  repatch.spatial  [3 funcs]
    _delete_match_keys  CC=4  out:11
    _element_delete_candidates  CC=6  out:8
    apply_spatial_deletes_to_html  CC=4  out:29
  repatch.ui_patch  [9 funcs]
    _compact_html  CC=3  out:4
    _css_for  CC=2  out:4
    _patch_scope_rules  CC=7  out:9
    _safe_css  CC=9  out:11
    _strip_json_fence  CC=3  out:5
    apply_ui_patch_options  CC=25  out:31
    build_ui_patch_prompt  CC=9  out:5
    parse_ui_patch_response  CC=6  out:11
    supports_llm_patch_scope  CC=3  out:1
  repatch.web_preprocess  [12 funcs]
    _rule_is_visual  CC=6  out:8
    _script_src_allowed_for_preview  CC=4  out:5
    _should_remove_preview_script  CC=2  out:3
    extract_inline_css  CC=4  out:4
    extract_stylesheet_hrefs  CC=7  out:4
    extract_visual_css  CC=8  out:19
    filter_visual_css  CC=3  out:4
    inject_http_preview_shim  CC=4  out:4
    normalize_linked_paths  CC=9  out:9
    prepare_http_preview_html  CC=1  out:2
  sdks.js.repatch-sdk  [7 funcs]
    _connectSSE  CC=3  out:5
    _connectWS  CC=3  out:7
    apply  CC=12  out:14
    cb  CC=1  out:0
    connect  CC=2  out:3
    payload  CC=2  out:1
    setTimeout  CC=1  out:1
  sdks.python.repatch_sdk  [1 funcs]
    _trigger_listeners  CC=3  out:2

EDGES:
  repatch.project_ir._ProjectIRParser._classify_node → repatch.project_ir._clean_text
  repatch.project_ir._ProjectIRParser.handle_endtag → repatch.project_ir._clean_text
  repatch.project_ir._ProjectIRParser.handle_data → repatch.project_ir._clean_text
  repatch.scope.default_scope_for_kind → repatch.scope.allowed_scope_ids
  repatch.scope.normalize_focus_scope → repatch.scope.default_scope_for_kind
  repatch.scope.normalize_focus_scope → repatch.scope.allowed_scope_ids
  repatch.scope.scope_supports_offline_fast_path → repatch.scope.normalize_focus_scope
  repatch.scope.scope_supports_offline_fast_path → repatch.scope.offline_fast_scopes_for_kind
  repatch.scope._web_orientation_scope_css → repatch.scope.goal_requests_column_layout
  repatch.scope._web_scope_css → repatch.scope._web_shapes_scope_css
  repatch.scope._web_scope_css → repatch.scope._web_display_scope_css
  repatch.scope._web_scope_css → repatch.scope._web_orientation_scope_css
  repatch.scope.should_block_full_html_iterate → repatch.marked_context.has_ui_marks
  repatch.scope._get_scope_css → repatch.scope._calc_scope_css
  repatch.scope._get_scope_css → repatch.scope._scope_css
  repatch.scope._get_scope_css → repatch.scope._web_scope_css
  repatch.scope.inject_scope_style → repatch.scope._bind_annotations_to_html
  repatch.scope.inject_scope_style → repatch.scope._resolve_scope_kind
  repatch.scope.inject_scope_style → repatch.scope.normalize_focus_scope
  repatch.scope.inject_scope_style → repatch.marked_context.effective_delete_ids
  repatch.scope.inject_scope_style → repatch.scope._get_scope_css
  repatch.scope.inject_scope_style → repatch.scope.strip_scope_style
  repatch.scope.inject_scope_style → repatch.scope._inject_css_block
  repatch.scope.scoped_html_fragment → repatch.scope.normalize_focus_scope
  repatch.scope.scoped_html_fragment → repatch.scope.scope_supports_offline_fast_path
  repatch.dom_patch.build_function_patch_context → repatch.project_ir.build_project_ir
  repatch.dom_patch.build_function_patch_context → repatch.project_ir.summarize_project_ir
  repatch.dom_patch._variant_section → repatch.dom_patch._goal_label
  repatch.dom_patch._matches_target → repatch.dom_patch._attrs_from_open_tag
  repatch.dom_patch._matches_target → repatch.dom_patch._strip_tags
  repatch.dom_patch._matches_target → repatch.dom_patch._target_candidates
  repatch.dom_patch._variant_target_label → repatch.dom_patch._goal_label
  repatch.dom_patch._patch_function_targets → repatch.dom_patch._target_candidates
  repatch.dom_patch._patch_function_targets → repatch.dom_patch._variant_target_label
  repatch.dom_patch.build_function_option_patches → repatch.dom_patch._strip_existing_patch
  repatch.dom_patch.build_function_option_patches → repatch.project_ir.build_project_ir
  repatch.dom_patch.build_function_option_patches → repatch.marked_context.effective_delete_ids
  repatch.dom_patch.build_function_option_patches → repatch.dom_patch.supports_function_patch
  repatch.dom_patch.build_function_option_patches → repatch.dom_patch._patch_function_targets
  repatch.dom_patch.build_function_option_patches → repatch.dom_patch._inject_into_head
  repatch.dom_patch.build_function_option_patches → repatch.dom_patch._inject_into_body
  repatch.marked_context.marked_css_selectors → repatch.marked_context._id_candidates
  repatch.marked_context.marked_css_selectors → repatch.marked_context._css_id_selector
  repatch.marked_context._collect_keep_selectors → repatch.marked_context._fragment_class_names
  repatch.marked_context._collect_keep_selectors → repatch.marked_context.marked_css_selectors
  repatch.marked_context._collect_keep_selectors → repatch.marked_context._find_marked_subtrees
  repatch.marked_context.resolve_marked_selectors → repatch.marked_context._find_marked_subtrees
  repatch.marked_context.resolve_marked_selectors → repatch.marked_context._collect_keep_selectors
  repatch.marked_context.resolve_marked_selectors → repatch.marked_context.marked_css_selectors
  repatch.marked_context.restrict_scope_css_to_marks → repatch.css.split_css_rules
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Cli (1)

**`CLI Command Tests`**

### Integration (1)

**`Auto-generated from Python Tests`**

## Intent

Scope-based HTML/CSS/DOM patch utilities and LLM patch helpers
