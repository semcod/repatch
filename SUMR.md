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
- **version**: `0.2.1`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, testql(2), app.doql.less, goal.yaml, .env.example, src(8 mod), project/(5 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: repatch;
  version: 0.2.1;
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
- `repatch.project_ir`
- `repatch.scope`
- `repatch.service`
- `repatch.spatial`
- `repatch.ui_patch`

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
def resolve_marked_selectors(html, element_ids)  # CC=14, fan=13 ⚠
def marked_scope_colors_css(selectors, variant)  # CC=4, fan=2
def restrict_scope_css_to_marks(css, delete_ids)  # CC=14, fan=11 ⚠
def _id_candidates(element_id)  # CC=4, fan=6
def _parse_attrs(attr_text)  # CC=3, fan=5
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
def build_function_option_patches(html_text)  # CC=10, fan=13 ⚠
```

### `repatch.scope` (`repatch/scope.py`)

```python
def ui_type_for_kind(kind)  # CC=11, fan=3 ⚠
def allowed_scope_ids(project_kind)  # CC=2, fan=3
def default_scope_for_kind(project_kind)  # CC=3, fan=4
def normalize_focus_scope(scope, project_kind)  # CC=3, fan=5
def offline_fast_scopes_for_kind(project_kind)  # CC=5, fan=2
def scope_supports_offline_fast_path(scope, project_kind)  # CC=1, fan=2
def strip_scope_style(html)  # CC=2, fan=1
def _scope_css(scope, variant)  # CC=6, fan=0
def _calc_scope_css(scope, variant)  # CC=7, fan=0
def _web_scope_css(scope, variant)  # CC=6, fan=0
def _resolve_scope_kind(project_kind, html)  # CC=10, fan=2 ⚠
def should_block_full_html_iterate(project_kind, keep_els, delete_els)  # CC=3, fan=3
def _bind_annotations_to_html(html, keep_ids, delete_ids)  # CC=29, fan=18 ⚠
def _get_scope_css(inferred, html, scope, variant)  # CC=7, fan=5
def _inject_css_block(html, css)  # CC=5, fan=4
def inject_scope_style(html, scope, variant)  # CC=14, fan=11 ⚠
def scoped_html_fragment(html, focus_scope, project_kind)  # CC=6, fan=6
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

### `repatch.project_ir` (`repatch/project_ir.py`)

```python
def _clean_text(text)  # CC=2, fan=3
def build_project_ir(html)  # CC=2, fan=5
def summarize_project_ir(ir)  # CC=12, fan=7 ⚠
class _ProjectIRParser:
    def __init__()  # CC=1
    def handle_starttag(tag, attrs)  # CC=5
    def _classify_node(tag, text, attrs, item)  # CC=12 ⚠
    def handle_endtag(tag)  # CC=8
    def handle_data(data)  # CC=4
```

## Call Graph

*76 nodes · 82 edges · 7 modules · CC̄=5.8*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `_bind_annotations_to_html` *(in repatch.scope)* | 29 ⚠ | 1 | 45 | **46** |
| `apply_ui_patch_options` *(in repatch.ui_patch)* | 25 ⚠ | 0 | 31 | **31** |
| `apply_spatial_deletes_to_html` *(in repatch.spatial)* | 4 | 0 | 29 | **29** |
| `resolve_marked_selectors` *(in repatch.marked_context)* | 14 ⚠ | 3 | 24 | **27** |
| `validate_css_safety` *(in repatch.css)* | 14 ⚠ | 1 | 26 | **27** |
| `_patch_function_targets` *(in repatch.dom_patch)* | 6 | 1 | 24 | **25** |
| `_find_marked_subtrees` *(in repatch.marked_context)* | 17 ⚠ | 2 | 23 | **25** |
| `summarize_project_ir` *(in repatch.project_ir)* | 12 ⚠ | 1 | 21 | **22** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/repatch
# generated in 0.04s
# nodes: 76 | edges: 82 | modules: 7
# CC̄=5.8

HUBS[20]:
  repatch.scope._bind_annotations_to_html
    CC=29  in:1  out:45  total:46
  repatch.ui_patch.apply_ui_patch_options
    CC=25  in:0  out:31  total:31
  repatch.spatial.apply_spatial_deletes_to_html
    CC=4  in:0  out:29  total:29
  repatch.marked_context.resolve_marked_selectors
    CC=14  in:3  out:24  total:27
  repatch.css.validate_css_safety
    CC=14  in:1  out:26  total:27
  repatch.dom_patch._patch_function_targets
    CC=6  in:1  out:24  total:25
  repatch.marked_context._find_marked_subtrees
    CC=17  in:2  out:23  total:25
  repatch.project_ir.summarize_project_ir
    CC=12  in:1  out:21  total:22
  repatch.marked_context._id_candidates
    CC=4  in:10  out:11  total:21
  repatch.marked_context.restrict_scope_css_to_marks
    CC=14  in:2  out:17  total:19
  repatch.marked_context._extract_balanced_html
    CC=10  in:1  out:18  total:19
  repatch.scope.inject_scope_style
    CC=14  in:0  out:18  total:18
  repatch.marked_context._format_context_body
    CC=14  in:1  out:15  total:16
  repatch.marked_context._selector_tokens
    CC=9  in:1  out:14  total:15
  repatch.marked_context._logical_id
    CC=8  in:4  out:10  total:14
  repatch.marked_context.build_marked_element_context
    CC=11  in:1  out:13  total:14
  repatch.dom_patch.build_function_option_patches
    CC=10  in:0  out:14  total:14
  repatch.spatial._delete_match_keys
    CC=4  in:2  out:11  total:13
  repatch.ui_patch._safe_css
    CC=9  in:2  out:11  total:13
  repatch.marked_context._collect_match_candidates
    CC=6  in:1  out:11  total:12

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
  repatch.marked_context  [24 funcs]
    _assemble_marked_subtrees  CC=4  out:3
    _cap_text  CC=2  out:4
    _client_fragment_html  CC=9  out:10
    _collect_button_candidates  CC=3  out:8
    _collect_css_sources  CC=7  out:10
    _collect_match_candidates  CC=6  out:11
    _css_id_selector  CC=4  out:3
    _extract_and_format_fragment  CC=3  out:6
    _extract_balanced_html  CC=10  out:18
    _filter_css_for_tokens  CC=6  out:7
  repatch.project_ir  [6 funcs]
    _classify_node  CC=12  out:10
    handle_data  CC=4  out:2
    handle_endtag  CC=8  out:11
    _clean_text  CC=2  out:3
    build_project_ir  CC=2  out:8
    summarize_project_ir  CC=12  out:21
  repatch.scope  [16 funcs]
    _bind_annotations_to_html  CC=29  out:45
    _calc_scope_css  CC=7  out:0
    _get_scope_css  CC=7  out:7
    _inject_css_block  CC=5  out:4
    _resolve_scope_kind  CC=10  out:3
    _scope_css  CC=6  out:0
    _web_scope_css  CC=6  out:0
    allowed_scope_ids  CC=2  out:3
    default_scope_for_kind  CC=3  out:4
    inject_scope_style  CC=14  out:18
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

EDGES:
  repatch.project_ir._ProjectIRParser._classify_node → repatch.project_ir._clean_text
  repatch.project_ir._ProjectIRParser.handle_endtag → repatch.project_ir._clean_text
  repatch.project_ir._ProjectIRParser.handle_data → repatch.project_ir._clean_text
  repatch.scope.default_scope_for_kind → repatch.scope.allowed_scope_ids
  repatch.scope.normalize_focus_scope → repatch.scope.default_scope_for_kind
  repatch.scope.normalize_focus_scope → repatch.scope.allowed_scope_ids
  repatch.scope.scope_supports_offline_fast_path → repatch.scope.normalize_focus_scope
  repatch.scope.scope_supports_offline_fast_path → repatch.scope.offline_fast_scopes_for_kind
  repatch.scope.should_block_full_html_iterate → repatch.marked_context.has_ui_marks
  repatch.scope._get_scope_css → repatch.scope._calc_scope_css
  repatch.scope._get_scope_css → repatch.scope._scope_css
  repatch.scope._get_scope_css → repatch.scope._web_scope_css
  repatch.scope.inject_scope_style → repatch.scope._bind_annotations_to_html
  repatch.scope.inject_scope_style → repatch.scope._resolve_scope_kind
  repatch.scope.inject_scope_style → repatch.scope.normalize_focus_scope
  repatch.scope.inject_scope_style → repatch.scope._get_scope_css
  repatch.scope.inject_scope_style → repatch.scope.strip_scope_style
  repatch.scope.inject_scope_style → repatch.scope._inject_css_block
  repatch.scope.inject_scope_style → repatch.marked_context.resolve_marked_selectors
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
  repatch.marked_context.resolve_marked_selectors → repatch.marked_context._find_marked_subtrees
  repatch.marked_context.resolve_marked_selectors → repatch.marked_context.marked_css_selectors
  repatch.marked_context.restrict_scope_css_to_marks → repatch.css.split_css_rules
  repatch.marked_context.restrict_scope_css_to_marks → repatch.marked_context.resolve_marked_selectors
  repatch.marked_context.restrict_scope_css_to_marks → repatch.marked_context.marked_css_selectors
  repatch.marked_context._collect_match_candidates → repatch.marked_context._logical_id
  repatch.marked_context._collect_match_candidates → repatch.marked_context._id_candidates
  repatch.marked_context._collect_button_candidates → repatch.marked_context._logical_id
  repatch.marked_context._collect_button_candidates → repatch.marked_context._id_candidates
  repatch.marked_context._extract_and_format_fragment → repatch.marked_context._extract_balanced_html
  repatch.marked_context._find_marked_subtrees → repatch.marked_context._parse_attrs
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
# generated in 0.04s
# nodes: 76 | edges: 82 | modules: 7
# CC̄=5.8

HUBS[20]:
  repatch.scope._bind_annotations_to_html
    CC=29  in:1  out:45  total:46
  repatch.ui_patch.apply_ui_patch_options
    CC=25  in:0  out:31  total:31
  repatch.spatial.apply_spatial_deletes_to_html
    CC=4  in:0  out:29  total:29
  repatch.marked_context.resolve_marked_selectors
    CC=14  in:3  out:24  total:27
  repatch.css.validate_css_safety
    CC=14  in:1  out:26  total:27
  repatch.dom_patch._patch_function_targets
    CC=6  in:1  out:24  total:25
  repatch.marked_context._find_marked_subtrees
    CC=17  in:2  out:23  total:25
  repatch.project_ir.summarize_project_ir
    CC=12  in:1  out:21  total:22
  repatch.marked_context._id_candidates
    CC=4  in:10  out:11  total:21
  repatch.marked_context.restrict_scope_css_to_marks
    CC=14  in:2  out:17  total:19
  repatch.marked_context._extract_balanced_html
    CC=10  in:1  out:18  total:19
  repatch.scope.inject_scope_style
    CC=14  in:0  out:18  total:18
  repatch.marked_context._format_context_body
    CC=14  in:1  out:15  total:16
  repatch.marked_context._selector_tokens
    CC=9  in:1  out:14  total:15
  repatch.marked_context._logical_id
    CC=8  in:4  out:10  total:14
  repatch.marked_context.build_marked_element_context
    CC=11  in:1  out:13  total:14
  repatch.dom_patch.build_function_option_patches
    CC=10  in:0  out:14  total:14
  repatch.spatial._delete_match_keys
    CC=4  in:2  out:11  total:13
  repatch.ui_patch._safe_css
    CC=9  in:2  out:11  total:13
  repatch.marked_context._collect_match_candidates
    CC=6  in:1  out:11  total:12

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
  repatch.marked_context  [24 funcs]
    _assemble_marked_subtrees  CC=4  out:3
    _cap_text  CC=2  out:4
    _client_fragment_html  CC=9  out:10
    _collect_button_candidates  CC=3  out:8
    _collect_css_sources  CC=7  out:10
    _collect_match_candidates  CC=6  out:11
    _css_id_selector  CC=4  out:3
    _extract_and_format_fragment  CC=3  out:6
    _extract_balanced_html  CC=10  out:18
    _filter_css_for_tokens  CC=6  out:7
  repatch.project_ir  [6 funcs]
    _classify_node  CC=12  out:10
    handle_data  CC=4  out:2
    handle_endtag  CC=8  out:11
    _clean_text  CC=2  out:3
    build_project_ir  CC=2  out:8
    summarize_project_ir  CC=12  out:21
  repatch.scope  [16 funcs]
    _bind_annotations_to_html  CC=29  out:45
    _calc_scope_css  CC=7  out:0
    _get_scope_css  CC=7  out:7
    _inject_css_block  CC=5  out:4
    _resolve_scope_kind  CC=10  out:3
    _scope_css  CC=6  out:0
    _web_scope_css  CC=6  out:0
    allowed_scope_ids  CC=2  out:3
    default_scope_for_kind  CC=3  out:4
    inject_scope_style  CC=14  out:18
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

EDGES:
  repatch.project_ir._ProjectIRParser._classify_node → repatch.project_ir._clean_text
  repatch.project_ir._ProjectIRParser.handle_endtag → repatch.project_ir._clean_text
  repatch.project_ir._ProjectIRParser.handle_data → repatch.project_ir._clean_text
  repatch.scope.default_scope_for_kind → repatch.scope.allowed_scope_ids
  repatch.scope.normalize_focus_scope → repatch.scope.default_scope_for_kind
  repatch.scope.normalize_focus_scope → repatch.scope.allowed_scope_ids
  repatch.scope.scope_supports_offline_fast_path → repatch.scope.normalize_focus_scope
  repatch.scope.scope_supports_offline_fast_path → repatch.scope.offline_fast_scopes_for_kind
  repatch.scope.should_block_full_html_iterate → repatch.marked_context.has_ui_marks
  repatch.scope._get_scope_css → repatch.scope._calc_scope_css
  repatch.scope._get_scope_css → repatch.scope._scope_css
  repatch.scope._get_scope_css → repatch.scope._web_scope_css
  repatch.scope.inject_scope_style → repatch.scope._bind_annotations_to_html
  repatch.scope.inject_scope_style → repatch.scope._resolve_scope_kind
  repatch.scope.inject_scope_style → repatch.scope.normalize_focus_scope
  repatch.scope.inject_scope_style → repatch.scope._get_scope_css
  repatch.scope.inject_scope_style → repatch.scope.strip_scope_style
  repatch.scope.inject_scope_style → repatch.scope._inject_css_block
  repatch.scope.inject_scope_style → repatch.marked_context.resolve_marked_selectors
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
  repatch.marked_context.resolve_marked_selectors → repatch.marked_context._find_marked_subtrees
  repatch.marked_context.resolve_marked_selectors → repatch.marked_context.marked_css_selectors
  repatch.marked_context.restrict_scope_css_to_marks → repatch.css.split_css_rules
  repatch.marked_context.restrict_scope_css_to_marks → repatch.marked_context.resolve_marked_selectors
  repatch.marked_context.restrict_scope_css_to_marks → repatch.marked_context.marked_css_selectors
  repatch.marked_context._collect_match_candidates → repatch.marked_context._logical_id
  repatch.marked_context._collect_match_candidates → repatch.marked_context._id_candidates
  repatch.marked_context._collect_button_candidates → repatch.marked_context._logical_id
  repatch.marked_context._collect_button_candidates → repatch.marked_context._id_candidates
  repatch.marked_context._extract_and_format_fragment → repatch.marked_context._extract_balanced_html
  repatch.marked_context._find_marked_subtrees → repatch.marked_context._parse_attrs
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 13f 2713L | python:9,shell:2,yaml:1,toml:1 | 2026-06-01
# generated in 0.01s
# CC̅=5.8 | critical:3/95 | dups:0 | cycles:0

HEALTH[3]:
  🟡 CC    _bind_annotations_to_html CC=29 (limit:15)
  🟡 CC    _find_marked_subtrees CC=17 (limit:15)
  🟡 CC    apply_ui_patch_options CC=25 (limit:15)

REFACTOR[1]:
  1. split 3 high-CC methods  (CC>15)

PIPELINES[23]:
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
  [6] Src [ui_type_for_kind]: ui_type_for_kind
      PURITY: 100% pure
  [7] Src [should_block_full_html_iterate]: should_block_full_html_iterate → has_ui_marks
      PURITY: 100% pure
  [8] Src [inject_scope_style]: inject_scope_style → _bind_annotations_to_html → _parse_attrs
      PURITY: 100% pure
  [9] Src [build_function_patch_context]: build_function_patch_context → build_project_ir
      PURITY: 100% pure
  [10] Src [_default_prepare_html]: _default_prepare_html
      PURITY: 100% pure
  [11] Src [build_function_option_patches]: build_function_option_patches → _strip_existing_patch
      PURITY: 100% pure
  [12] Src [resolve_marked_llm_context]: resolve_marked_llm_context → build_marked_element_context → _assemble_marked_subtrees → _find_marked_subtrees → ...(1 more)
      PURITY: 100% pure
  [13] Src [supports_llm_patch_scope]: supports_llm_patch_scope → normalize_focus_scope → default_scope_for_kind → allowed_scope_ids
      PURITY: 100% pure
  [14] Src [build_ui_patch_prompt]: build_ui_patch_prompt → normalize_focus_scope → default_scope_for_kind → allowed_scope_ids
      PURITY: 100% pure
  [15] Src [parse_ui_patch_response]: parse_ui_patch_response → _strip_json_fence
      PURITY: 100% pure
  [16] Src [apply_ui_patch_options]: apply_ui_patch_options → strip_scope_style
      PURITY: 100% pure
  [17] Src [apply_spatial_deletes_to_html]: apply_spatial_deletes_to_html → _delete_match_keys
      PURITY: 100% pure
  [18] Src [generate_patch_suggestions]: generate_patch_suggestions
      PURITY: 100% pure
  [19] Src [_normalize_scopes]: _normalize_scopes
      PURITY: 100% pure
  [20] Src [_build_user_prompt]: _build_user_prompt
      PURITY: 100% pure
  [21] Src [_parse_choice]: _parse_choice
      PURITY: 100% pure
  [22] Src [_choice_content]: _choice_content
      PURITY: 100% pure
  [23] Src [_default_completion]: _default_completion
      PURITY: 100% pure

LAYERS:
  repatch/                        CC̄=5.8    ←in:0  →out:0
  │ !! marked_context             519L  0C   26m  CC=17     ←3
  │ !! scope                      494L  0C   17m  CC=29     ←2
  │ dom_patch                  314L  0C   19m  CC=10     ←0
  │ !! ui_patch                   267L  0C   10m  CC=25     ←0
  │ project_ir                 132L  1C    8m  CC=12     ←1
  │ spatial                    108L  0C    4m  CC=6      ←0
  │ service                    105L  2C    7m  CC=6      ←0
  │ __init__                    87L  0C    0m  CC=0.0    ←0
  │ css                         70L  0C    4m  CC=14     ←2
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! goal.yaml                  511L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              55L  0C    0m  CC=0.0    ←0
  │ project.sh                  50L  0C    0m  CC=0.0    ←0
  │ tree.sh                      1L  0C    0m  CC=0.0    ←0
  │

COUPLING: no cross-package imports detected

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 1 groups | 9f 2096L | 2026-06-01

SUMMARY:
  files_scanned: 9
  total_lines:   2096
  dup_groups:    1
  dup_fragments: 2
  saved_lines:   56
  scan_ms:       2747

HOTSPOTS[1] (files with most duplication):
  repatch/scope.py  dup=103L  groups=1  frags=2  (4.9%)

DUPLICATES[1] (ranked by impact):
  [ee82f654639dd9b7] ! STRU  _scope_css  L=56 N=2 saved=56 sim=1.00
      repatch/scope.py:141-196  (_scope_css)
      repatch/scope.py:273-319  (_web_scope_css)

REFACTOR[1] (ranked by priority):
  [1] ○ extract_module     → repatch/utils/_scope_css.py
      WHY: 2 occurrences of 56-line block across 1 files — saves 56 lines
      FILES: repatch/scope.py

QUICK_WINS[1] (low risk, high savings — do first):
  [1] extract_module     saved=56L  → repatch/utils/_scope_css.py
      FILES: scope.py

EFFORT_ESTIMATE (total ≈ 2.8h):
  hard   _scope_css                          saved=56L  ~168min

METRICS-TARGET:
  dup_groups:  1 → 0
  saved_lines: 56 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 95 func | 8f | 2026-06-01
# generated in 0.00s

NEXT[5] (ranked by impact):
  [1] !! SPLIT           repatch/marked_context.py
      WHY: 519L, 0 classes, max CC=17
      EFFORT: ~4h  IMPACT: 8823

  [2] !! SPLIT-FUNC      _bind_annotations_to_html  CC=29  fan=20
      WHY: CC=29 exceeds 15
      EFFORT: ~1h  IMPACT: 580

  [3] !! SPLIT-FUNC      apply_ui_patch_options  CC=25  fan=21
      WHY: CC=25 exceeds 15
      EFFORT: ~1h  IMPACT: 525

  [4] !  SPLIT-FUNC      _find_marked_subtrees  CC=17  fan=13
      WHY: CC=17 exceeds 15
      EFFORT: ~1h  IMPACT: 221

  [5] !! SPLIT           goal.yaml
      WHY: 511L, 0 classes, max CC=0
      EFFORT: ~4h  IMPACT: 0


RISKS[2]:
  ⚠ Splitting repatch/marked_context.py may break 26 import paths
  ⚠ Splitting goal.yaml may break 0 import paths

METRICS-TARGET:
  CC̄:          5.8 → ≤4.1
  max-CC:      29 → ≤14
  god-modules: 2 → 0
  high-CC(≥15): 3 → ≤1
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
  (first run — no previous data)
```

## Intent

Scope-based HTML/CSS/DOM patch utilities and LLM patch helpers
