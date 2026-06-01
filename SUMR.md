# repatch

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Dependencies](#dependencies)
- [Source Map](#source-map)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `repatch`
- **version**: `0.2.10`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, testql(2), app.doql.less, goal.yaml, .env.example, src(10 mod), project/(5 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: repatch;
  version: 0.2.10;
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
  sdks.js.repatch-sdk.RepatchSDK.apply
    CC=12  in:3  out:14  total:17
  repatch.options.sync_option_previews_from_workspace
    CC=10  in:0  out:17  total:17
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
  repatch.ui_patch.supports_llm_patch_scope → repatch.scope.normalize_focus_scope
  repatch.ui_patch.build_ui_patch_prompt → repatch.scope.normalize_focus_scope
  repatch.ui_patch.build_ui_patch_prompt → repatch.ui_patch._patch_scope_rules
  repatch.ui_patch.build_ui_patch_prompt → repatch.scope.scoped_html_fragment
  repatch.ui_patch.build_ui_patch_prompt → repatch.ui_patch._compact_html
  repatch.ui_patch.parse_ui_patch_response → repatch.ui_patch._strip_json_fence
  repatch.ui_patch._safe_css → repatch.css.validate_css_safety
  repatch.ui_patch._css_for → repatch.ui_patch._safe_css
  repatch.ui_patch.apply_ui_patch_options → repatch.scope.strip_scope_style
  repatch.ui_patch.apply_ui_patch_options → repatch.scope.normalize_focus_scope
  repatch.ui_patch.apply_ui_patch_options → repatch.ui_patch._css_for
  repatch.options.html_files_distinct → repatch.options.normalize_html_body
  repatch.options.sync_option_previews_from_workspace → repatch.spatial.apply_spatial_deletes_to_html
  repatch.options.enforce_deletes_on_option_previews → repatch.spatial.apply_spatial_deletes_to_html
  repatch.css.validate_css_safety → repatch.css._strip_css_comments
  repatch.css.validate_css_safety → repatch.css._selector_is_runtime_only
  repatch.spatial._element_delete_candidates → repatch.spatial._delete_match_keys
  repatch.spatial.apply_spatial_deletes_to_html → repatch.spatial._delete_match_keys
  repatch.spatial.apply_spatial_deletes_to_html → repatch.spatial._element_delete_candidates
  sdks.js.repatch-sdk.RepatchSDK.connect → sdks.js.repatch-sdk.RepatchSDK._connectSSE
  sdks.js.repatch-sdk.RepatchSDK.connect → sdks.js.repatch-sdk.RepatchSDK._connectWS
  sdks.js.repatch-sdk.RepatchSDK._connectWS → sdks.js.repatch-sdk.RepatchSDK.apply
  sdks.js.repatch-sdk.RepatchSDK._connectWS → sdks.js.repatch-sdk.RepatchSDK.setTimeout
  sdks.js.repatch-sdk.RepatchSDK.payload → sdks.js.repatch-sdk.RepatchSDK.apply
  sdks.js.repatch-sdk.RepatchSDK.setTimeout → sdks.js.repatch-sdk.RepatchSDK._connectSSE
  sdks.js.repatch-sdk.RepatchSDK._connectSSE → sdks.js.repatch-sdk.RepatchSDK.apply
  sdks.python.repatch_sdk.RepatchClient._trigger_listeners → sdks.js.repatch-sdk.RepatchSDK.cb
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
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Cli (1)

**`CLI Command Tests`**

### Integration (1)

**`Auto-generated from Python Tests`**

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

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
  sdks.js.repatch-sdk.RepatchSDK.apply
    CC=12  in:3  out:14  total:17
  repatch.options.sync_option_previews_from_workspace
    CC=10  in:0  out:17  total:17
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
  repatch.ui_patch.supports_llm_patch_scope → repatch.scope.normalize_focus_scope
  repatch.ui_patch.build_ui_patch_prompt → repatch.scope.normalize_focus_scope
  repatch.ui_patch.build_ui_patch_prompt → repatch.ui_patch._patch_scope_rules
  repatch.ui_patch.build_ui_patch_prompt → repatch.scope.scoped_html_fragment
  repatch.ui_patch.build_ui_patch_prompt → repatch.ui_patch._compact_html
  repatch.ui_patch.parse_ui_patch_response → repatch.ui_patch._strip_json_fence
  repatch.ui_patch._safe_css → repatch.css.validate_css_safety
  repatch.ui_patch._css_for → repatch.ui_patch._safe_css
  repatch.ui_patch.apply_ui_patch_options → repatch.scope.strip_scope_style
  repatch.ui_patch.apply_ui_patch_options → repatch.scope.normalize_focus_scope
  repatch.ui_patch.apply_ui_patch_options → repatch.ui_patch._css_for
  repatch.options.html_files_distinct → repatch.options.normalize_html_body
  repatch.options.sync_option_previews_from_workspace → repatch.spatial.apply_spatial_deletes_to_html
  repatch.options.enforce_deletes_on_option_previews → repatch.spatial.apply_spatial_deletes_to_html
  repatch.css.validate_css_safety → repatch.css._strip_css_comments
  repatch.css.validate_css_safety → repatch.css._selector_is_runtime_only
  repatch.spatial._element_delete_candidates → repatch.spatial._delete_match_keys
  repatch.spatial.apply_spatial_deletes_to_html → repatch.spatial._delete_match_keys
  repatch.spatial.apply_spatial_deletes_to_html → repatch.spatial._element_delete_candidates
  sdks.js.repatch-sdk.RepatchSDK.connect → sdks.js.repatch-sdk.RepatchSDK._connectSSE
  sdks.js.repatch-sdk.RepatchSDK.connect → sdks.js.repatch-sdk.RepatchSDK._connectWS
  sdks.js.repatch-sdk.RepatchSDK._connectWS → sdks.js.repatch-sdk.RepatchSDK.apply
  sdks.js.repatch-sdk.RepatchSDK._connectWS → sdks.js.repatch-sdk.RepatchSDK.setTimeout
  sdks.js.repatch-sdk.RepatchSDK.payload → sdks.js.repatch-sdk.RepatchSDK.apply
  sdks.js.repatch-sdk.RepatchSDK.setTimeout → sdks.js.repatch-sdk.RepatchSDK._connectSSE
  sdks.js.repatch-sdk.RepatchSDK._connectSSE → sdks.js.repatch-sdk.RepatchSDK.apply
  sdks.python.repatch_sdk.RepatchClient._trigger_listeners → sdks.js.repatch-sdk.RepatchSDK.cb
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
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 21f 7502L | python:12,yaml:4,json:1,txt:1,shell:1,javascript:1,toml:1 | 2026-06-01
# generated in 0.01s
# CC̅=5.2 | critical:5/156 | dups:0 | cycles:0

HEALTH[5]:
  🟡 CC    apply_ui_patch_options CC=25 (limit:15)
  🟡 CC    _bind_annotations_to_html CC=29 (limit:15)
  🟡 CC    inject_scope_style CC=27 (limit:15)
  🟡 CC    resolve_marked_selectors CC=16 (limit:15)
  🟡 CC    _find_marked_subtrees CC=17 (limit:15)

REFACTOR[1]:
  1. split 5 high-CC methods  (CC>15)

PIPELINES[54]:
  [1] Src [__init__]: __init__
      PURITY: 100% pure
  [2] Src [handle_starttag]: handle_starttag
      PURITY: 100% pure
  [3] Src [_classify_node]: _classify_node → _clean_text
      PURITY: 100% pure
  [4] Src [handle_endtag]: handle_endtag → _clean_text
      PURITY: 100% pure
  [5] Src [handle_data]: handle_data → _clean_text
      PURITY: 100% pure
  [6] Src [supports_llm_patch_scope]: supports_llm_patch_scope → normalize_focus_scope → default_scope_for_kind → allowed_scope_ids
      PURITY: 100% pure
  [7] Src [build_ui_patch_prompt]: build_ui_patch_prompt → normalize_focus_scope → default_scope_for_kind → allowed_scope_ids
      PURITY: 100% pure
  [8] Src [parse_ui_patch_response]: parse_ui_patch_response → _strip_json_fence
      PURITY: 100% pure
  [9] Src [apply_ui_patch_options]: apply_ui_patch_options → strip_scope_style
      PURITY: 100% pure
  [10] Src [html_files_distinct]: html_files_distinct → normalize_html_body
      PURITY: 100% pure
  [11] Src [sync_option_previews_from_workspace]: sync_option_previews_from_workspace → apply_spatial_deletes_to_html → _delete_match_keys
      PURITY: 100% pure
  [12] Src [enforce_deletes_on_option_previews]: enforce_deletes_on_option_previews → apply_spatial_deletes_to_html → _delete_match_keys
      PURITY: 100% pure
  [13] Src [generate_patch_suggestions]: generate_patch_suggestions
      PURITY: 100% pure
  [14] Src [_normalize_scopes]: _normalize_scopes
      PURITY: 100% pure
  [15] Src [_build_user_prompt]: _build_user_prompt
      PURITY: 100% pure
  [16] Src [_parse_choice]: _parse_choice
      PURITY: 100% pure
  [17] Src [_choice_content]: _choice_content
      PURITY: 100% pure
  [18] Src [_default_completion]: _default_completion
      PURITY: 100% pure
  [19] Src [connect]: connect → _connectSSE → apply → cb
      PURITY: 100% pure
  [20] Src [payload]: payload → apply → cb
      PURITY: 100% pure
  [21] Src [onPatch]: onPatch
      PURITY: 100% pure
  [22] Src [dslClean]: dslClean
      PURITY: 100% pure
  [23] Src [addMatch]: addMatch
      PURITY: 100% pure
  [24] Src [replaceMatch]: replaceMatch
      PURITY: 100% pure
  [25] Src [styleMatch]: styleMatch
      PURITY: 100% pure
  [26] Src [removeMatch]: removeMatch → cb
      PURITY: 100% pure
  [27] Src [html]: html
      PURITY: 100% pure
  [28] Src [target]: target
      PURITY: 100% pure
  [29] Src [css]: css
      PURITY: 100% pure
  [30] Src [styleEl]: styleEl
      PURITY: 100% pure
  [31] Src [sendPatchRequest]: sendPatchRequest
      PURITY: 100% pure
  [32] Src [on_patch]: on_patch
      PURITY: 100% pure
  [33] Src [start]: start
      PURITY: 100% pure
  [34] Src [_run_event_loop]: _run_event_loop
      PURITY: 100% pure
  [35] Src [_connect_and_listen]: _connect_and_listen
      PURITY: 100% pure
  [36] Src [_trigger_listeners]: _trigger_listeners → cb
      PURITY: 100% pure
  [37] Src [send_patch]: send_patch
      PURITY: 100% pure
  [38] Src [ui_type_for_kind]: ui_type_for_kind
      PURITY: 100% pure
  [39] Src [should_block_full_html_iterate]: should_block_full_html_iterate → has_ui_marks
      PURITY: 100% pure
  [40] Src [inject_scope_style]: inject_scope_style → _bind_annotations_to_html → _parse_attrs → _normalize_label_text
      PURITY: 100% pure
  [41] Src [build_function_patch_context]: build_function_patch_context → build_project_ir
      PURITY: 100% pure
  [42] Src [_default_prepare_html]: _default_prepare_html
      PURITY: 100% pure
  [43] Src [build_function_option_patches]: build_function_option_patches → _strip_existing_patch
      PURITY: 100% pure
  [44] Src [resolve_marked_llm_context]: resolve_marked_llm_context → build_marked_element_context → _assemble_marked_subtrees → _find_marked_subtrees → ...(2 more)
      PURITY: 100% pure
  [45] Src [extract_visual_css]: extract_visual_css → extract_inline_css
      PURITY: 100% pure
  [46] Src [__init__]: __init__
      PURITY: 100% pure
  [47] Src [_keep_attr]: _keep_attr
      PURITY: 100% pure
  [48] Src [handle_starttag]: handle_starttag
      PURITY: 100% pure
  [49] Src [handle_endtag]: handle_endtag
      PURITY: 100% pure
  [50] Src [handle_data]: handle_data
      PURITY: 100% pure

LAYERS:
  repatch/                        CC̄=5.7    ←in:0  →out:0
  │ !! marked_context             696L  0C   32m  CC=17     ←3
  │ !! scope                      647L  0C   22m  CC=29     ←2
  │ web_preprocess             397L  1C   20m  CC=9      ←0
  │ dom_patch                  315L  0C   19m  CC=12     ←0
  │ !! ui_patch                   267L  0C   10m  CC=25     ←0
  │ options                    140L  0C    5m  CC=10     ←0
  │ project_ir                 132L  1C    8m  CC=12     ←1
  │ spatial                    108L  0C    4m  CC=6      ←1
  │ service                    105L  2C    7m  CC=6      ←0
  │ __init__                   105L  0C    0m  CC=0.0    ←0
  │ css                         70L  0C    4m  CC=14     ←3
  │
  sdks/                           CC̄=2.7    ←in:0  →out:0
  │ repatch-sdk.js             186L  1C   18m  CC=12     ←1
  │ repatch_sdk                 73L  1C    7m  CC=7      ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! deps.json                 3394L  0C    0m  CC=0.0    ←0
  │ !! goal.yaml                  511L  0C    0m  CC=0.0    ←0
  │ wup.yaml                   134L  0C    0m  CC=0.0    ←0
  │ tree.txt                    87L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              55L  0C    0m  CC=0.0    ←0
  │ project.sh                  50L  0C    0m  CC=0.0    ←0
  │
  testql-scenarios/               CC̄=0.0    ←in:0  →out:0
  │ generated-cli-tests.testql.toon.yaml    20L  0C    0m  CC=0.0    ←0
  │ generated-from-pytests.testql.toon.yaml    10L  0C    0m  CC=0.0    ←0
  │

COUPLING:
                   sdks.js  sdks.python
      sdks.js           ──           ←1
  sdks.python            1           ──
  CYCLES: none

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 1 groups | 11f 2982L | 2026-06-01

SUMMARY:
  files_scanned: 11
  total_lines:   2982
  dup_groups:    1
  dup_fragments: 2
  saved_lines:   12
  scan_ms:       2512

HOTSPOTS[1] (files with most duplication):
  repatch/marked_context.py  dup=24L  groups=1  frags=2  (0.8%)

DUPLICATES[1] (ranked by impact):
  [1576f29b2f19a9f4]   STRU  marked_scope_display_css  L=12 N=2 saved=12 sim=1.00
      repatch/marked_context.py:216-227  (marked_scope_display_css)
      repatch/marked_context.py:230-241  (marked_scope_shapes_css)

REFACTOR[1] (ranked by priority):
  [1] ○ extract_function   → repatch/utils/marked_scope_display_css.py
      WHY: 2 occurrences of 12-line block across 1 files — saves 12 lines
      FILES: repatch/marked_context.py

QUICK_WINS[1] (low risk, high savings — do first):
  [1] extract_function   saved=12L  → repatch/utils/marked_scope_display_css.py
      FILES: marked_context.py

EFFORT_ESTIMATE (total ≈ 0.4h):
  easy   marked_scope_display_css            saved=12L  ~24min

METRICS-TARGET:
  dup_groups:  1 → 0
  saved_lines: 12 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 156 func | 12f | 2026-06-01
# generated in 0.00s

NEXT[8] (ranked by impact):
  [1] !! SPLIT           repatch/scope.py
      WHY: 647L, 0 classes, max CC=29
      EFFORT: ~4h  IMPACT: 18763

  [2] !! SPLIT           repatch/marked_context.py
      WHY: 696L, 0 classes, max CC=17
      EFFORT: ~4h  IMPACT: 11832

  [3] !! SPLIT-FUNC      _bind_annotations_to_html  CC=29  fan=21
      WHY: CC=29 exceeds 15
      EFFORT: ~1h  IMPACT: 609

  [4] !! SPLIT-FUNC      inject_scope_style  CC=27  fan=20
      WHY: CC=27 exceeds 15
      EFFORT: ~1h  IMPACT: 540

  [5] !! SPLIT-FUNC      apply_ui_patch_options  CC=25  fan=21
      WHY: CC=25 exceeds 15
      EFFORT: ~1h  IMPACT: 525

  [6] !  SPLIT-FUNC      resolve_marked_selectors  CC=16  fan=15
      WHY: CC=16 exceeds 15
      EFFORT: ~1h  IMPACT: 240

  [7] !  SPLIT-FUNC      _find_marked_subtrees  CC=17  fan=13
      WHY: CC=17 exceeds 15
      EFFORT: ~1h  IMPACT: 221

  [8] !! SPLIT           deps.json
      WHY: 3394L, 0 classes, max CC=0
      EFFORT: ~4h  IMPACT: 0


RISKS[3]:
  ⚠ Splitting deps.json may break 0 import paths
  ⚠ Splitting repatch/marked_context.py may break 32 import paths
  ⚠ Splitting repatch/scope.py may break 22 import paths

METRICS-TARGET:
  CC̄:          5.2 → ≤3.6
  max-CC:      29 → ≤14
  god-modules: 4 → 0
  high-CC(≥15): 5 → ≤2
  hub-types:   0 → ≤0

PATTERNS (language parser shared logic):
  _extract_declarations() in base.py — unified extraction for:
    - TypeScript: interfaces, types, classes, functions, arrow funcs
    - PHP: namespaces, traits, classes, functions, includes
    - Ruby: modules, classes, methods, requires
    - C++: classes, structs, functions, #includes
    - C#: classes, interfaces, methods, usings
    - Java: classes, interfaces, methods, imports
    - Go: packages, functions, structs
    - Rust: modules, functions, traits, use statements

  Shared regex patterns per language:
    - import: language-specific import/require/using patterns
    - class: class/struct/trait declarations with inheritance
    - function: function/method signatures with visibility
    - brace_tracking: for C-family languages ({ })
    - end_keyword_tracking: for Ruby (module/class/def...end)

  Benefits:
    - Consistent extraction logic across all languages
    - Reduced code duplication (~70% reduction in parser LOC)
    - Easier maintenance: fix once, apply everywhere
    - Standardized FunctionInfo/ClassInfo models

HISTORY:
  prev CC̄=5.4 → now CC̄=5.2
```

## Intent

Scope-based HTML/CSS/DOM patch utilities and LLM patch helpers
