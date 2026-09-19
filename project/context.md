# System Architecture Analysis
<!-- generated in 0.00s -->

## Overview

- **Project**: /home/tom/github/semcod/repatch
- **Primary Language**: python
- **Languages**: python: 33, yaml: 6, txt: 2, json: 1, yml: 1
- **Analysis Mode**: static
- **Total Functions**: 230
- **Total Classes**: 23
- **Modules**: 48
- **Entry Points**: 74

## Architecture by Module

### sdks.js.repatch-sdk
- **Functions**: 23
- **Classes**: 1
- **File**: `repatch-sdk.js`

### repatch.web_fetch
- **Functions**: 21
- **Classes**: 6
- **File**: `web_fetch.py`

### dom_patch
- **Functions**: 20
- **File**: `dom_patch.py`

### repatch.scope
- **Functions**: 14
- **File**: `scope.py`

### repatch.dev_server
- **Functions**: 13
- **Classes**: 10
- **File**: `dev_server.py`

### repatch.project_ir
- **Functions**: 8
- **Classes**: 1
- **File**: `project_ir.py`

### repatch._scope_css
- **Functions**: 8
- **File**: `_scope_css.py`

### repatch.spatial
- **Functions**: 8
- **File**: `spatial.py`

### marked_context._ids
- **Functions**: 8
- **File**: `_ids.py`

### repatch.marked_context._html
- **Functions**: 8
- **File**: `_html.py`

### repatch.organize_html
- **Functions**: 7
- **Classes**: 1
- **File**: `organize_html.py`

### repatch._web_css
- **Functions**: 7
- **File**: `_web_css.py`

### repatch._scope_kinds
- **Functions**: 7
- **File**: `_scope_kinds.py`

### repatch.service
- **Functions**: 7
- **Classes**: 2
- **File**: `service.py`

### marked_context._selectors
- **Functions**: 7
- **File**: `_selectors.py`

### repatch.marked_context._context
- **Functions**: 7
- **File**: `_context.py`

### sdks.python.repatch_sdk
- **Functions**: 7
- **Classes**: 1
- **File**: `repatch_sdk.py`

### _http_llm_context
- **Functions**: 6
- **File**: `_http_llm_context.py`

### repatch._html_outline
- **Functions**: 6
- **Classes**: 1
- **File**: `_html_outline.py`

### repatch.marked_context._scope_css
- **Functions**: 6
- **File**: `_scope_css.py`

## Key Entry Points

Main execution flows into the system:

### repatch._ui_patch_apply.apply_ui_patch_options
> Apply validated CSS patches to one baseline HTML document.
- **Calls**: patch.get, repatch._scope_css.strip_scope_style, isinstance, ValueError, str, repatch._scope_kinds.normalize_focus_scope, None.strip, None.strip

### _http_llm_context.build_http_llm_context
> Combine visual CSS + HTML outline (+ organize manifest) for compact LLM patch prompts.
- **Calls**: None.strip, None.strip, _http_llm_context._cap_patch_text, _http_llm_context._cap_patch_text, _http_llm_context._context_parts, None.join, isinstance, artifacts.get

### repatch.options.sync_option_previews_from_workspace
> Refresh Options A-C from the active workspace HTML.

``delete_ids=None`` means resolve current policy DELETE ids through
``delete_resolver``. ``delete
- **Calls**: Path, stage_file.read_text, repatch.spatial.apply_spatial_deletes_to_html, stage_file.exists, list, list, finalize_html, None.write_text

### repatch._web_css.extract_visual_css
> Extract color/shape/layout CSS from inline styles and linked sheets.
- **Calls**: repatch._web_css.extract_inline_css, repatch._web_css.normalize_linked_paths, repatch._web_css.filter_visual_css, filtered.encode, chunks.append, local.startswith, repatch._web_css.safe_read_under, None.join

### repatch.options.enforce_deletes_on_option_previews
> Apply DELETE ids to existing Option A-C preview files.
- **Calls**: Path, None.strip, path.read_text, repatch.spatial.apply_spatial_deletes_to_html, path.write_text, touched.append, all_removed.extend, sorted

### sdks.js.repatch-sdk.RepatchSDK.removeMatch
- **Calls**: sdks.js.repatch-sdk.querySelector, sdks.js.repatch-sdk.insertAdjacentHTML, sdks.js.repatch-sdk.log, sdks.js.repatch-sdk.Error, sdks.js.repatch-sdk.trim, sdks.js.repatch-sdk.replace, sdks.js.repatch-sdk.getElementById, sdks.js.repatch-sdk.createElement

### repatch.project_ir._ProjectIRParser.handle_endtag
- **Calls**: tag.lower, self._stack.pop, repatch.project_ir._clean_text, self._classify_node, max, None.extend, None.join, attrs.get

### repatch._html_outline.build_html_outline
> Build a compact HTML skeleton without scripts or full text content.
- **Calls**: re.sub, _OutlineParser, parser.feed, parser.close, None.strip, str, None.startswith, len

### repatch.project_ir._ProjectIRParser._classify_node
- **Calls**: self.cards.append, self.headings.append, None.lower, self.actions.append, attrs.get, attrs.get, attrs.get, repatch.project_ir._clean_text

### dom_patch.build_function_option_patches
> Create A-C function variants by patching the current HTML locally.
- **Calls**: dom_patch._strip_existing_patch, repatch.project_ir.build_project_ir, marked_context._ids.effective_delete_ids, dom_patch.supports_function_patch, None.lower, list, list, dom_patch._build_variant_doc

### repatch.service.RepatchService._normalize_scopes
- **Calls**: sorted, sorted, None.lower, ValueError, ValueError, set, set, scope.strip

### repatch.service.RepatchService._parse_choice
- **Calls**: RepatchService._choice_content, PatchSuggestion, json.loads, ValueError, list, list, str, payload.get

### repatch.organize_html.organize_result_manifest
> Serialize ``OrganizeResult`` for ``project.json`` → ``organize`` metadata.
- **Calls**: dict, None.strip, int, int, extracted_files.append, str, manifest_meta.get, manifest_meta.get

### repatch.options.html_files_distinct
> True when all named HTML files exist and at least two have different bodies.
- **Calls**: Path, bodies.append, len, path.exists, repatch.options.normalize_html_body, set, path.read_text

### repatch.service.RepatchService.generate_patch_suggestions
- **Calls**: self._normalize_scopes, completion_fn, self._parse_choice, len, ValueError, self._build_user_prompt, len

### sdks.python.repatch_sdk.RepatchClient._connect_and_listen
- **Calls**: logging.error, websockets.connect, logging.info, logging.warning, asyncio.sleep, json.loads, self._trigger_listeners

### repatch.organize_html.organize_html_project_dir
> Read index.html under source_dir, organize in place, return result or None if missing.
- **Calls**: Path, repatch.organize_html.organize_html, candidate.is_file, index_path.read_text, result.meta.get, index_path.write_text

### repatch.dev_server.seed
> Return a single seed fixture by name.
- **Calls**: app.get, repatch.seeds.get_seed, repatch.seeds.seed_kind, HTTPException, str

### repatch.web_fetch._SSRFSafeRedirectHandler.redirect_request
- **Calls**: repatch.web_fetch._validate_http_url, None.redirect_request, URLError, super

### repatch.web_fetch.fetch_complete_web_page
> Fetch one page, optionally render JS with Playwright, and mirror core assets locally.
- **Calls**: repatch.web_fetch._fetch_page_source, WebFetchResult, repatch.web_fetch._mirror_page_assets, source.content_type.lower

### repatch._scope_kinds.ui_type_for_kind
- **Calls**: None.lower, None.lower, None.strip, re.sub

### repatch._html_outline._OutlineParser.handle_starttag
- **Calls**: None.join, self.parts.append, self.parts.append, self._keep_attr

### sdks.python.repatch_sdk.RepatchClient._run_event_loop
- **Calls**: asyncio.new_event_loop, asyncio.set_event_loop, self._loop.run_until_complete, self._connect_and_listen

### sdks.python.repatch_sdk.RepatchClient.send_patch
> Surgically send a Repatch DSL command to the stream.
- **Calls**: asyncio.run_coroutine_threadsafe, logging.error, self._ws.send, json.dumps

### repatch.project_ir._ProjectIRParser.handle_starttag
- **Calls**: tag.lower, self._stack.append, k.lower

### repatch.scope.should_block_full_html_iterate
> True when marks exist on imported/web/dashboard projects — force patch paths only.
- **Calls**: None.lower, marked_context._ids.has_ui_marks, None.strip

### dom_patch.build_function_patch_context
- **Calls**: repatch.project_ir.build_project_ir, user_goal.strip, repatch.project_ir.summarize_project_ir

### repatch.dev_server.health
> Basic liveness and version probe.
- **Calls**: app.get, len, repatch.seeds.list_seeds

### repatch.dev_server.seeds
> List available seed fixtures.
- **Calls**: app.get, repatch.seeds.seed_kind, repatch.seeds.list_seeds

### repatch.web_fetch._AssetMirror.mirror
> Return the local URL for one asset, or None to keep the original.
- **Calls**: repatch.web_fetch._save_asset, self.assets.append, self.errors.append

## Process Flows

Key execution flows identified:

### Flow 1: apply_ui_patch_options
```
apply_ui_patch_options [repatch._ui_patch_apply]
  └─ →> strip_scope_style
```

### Flow 2: build_http_llm_context
```
build_http_llm_context [_http_llm_context]
  └─> _cap_patch_text
  └─> _cap_patch_text
```

### Flow 3: sync_option_previews_from_workspace
```
sync_option_previews_from_workspace [repatch.options]
  └─ →> apply_spatial_deletes_to_html
      └─> _apply_block_deletes
          └─> _find_matching_close
          └─> _is_deletable_block
```

### Flow 4: extract_visual_css
```
extract_visual_css [repatch._web_css]
  └─> extract_inline_css
  └─> normalize_linked_paths
      └─> extract_stylesheet_hrefs
```

### Flow 5: enforce_deletes_on_option_previews
```
enforce_deletes_on_option_previews [repatch.options]
  └─ →> apply_spatial_deletes_to_html
      └─> _apply_block_deletes
          └─> _find_matching_close
          └─> _is_deletable_block
```

### Flow 6: removeMatch
```
removeMatch [sdks.js.repatch-sdk.RepatchSDK]
```

### Flow 7: handle_endtag
```
handle_endtag [repatch.project_ir._ProjectIRParser]
  └─ →> _clean_text
```

### Flow 8: build_html_outline
```
build_html_outline [repatch._html_outline]
```

### Flow 9: _classify_node
```
_classify_node [repatch.project_ir._ProjectIRParser]
```

### Flow 10: build_function_option_patches
```
build_function_option_patches [dom_patch]
  └─> _strip_existing_patch
  └─> supports_function_patch
  └─ →> build_project_ir
```

## Key Classes

### sdks.js.repatch-sdk.RepatchSDK
- **Methods**: 23
- **Key Methods**: sdks.js.repatch-sdk.RepatchSDK.connect, sdks.js.repatch-sdk.RepatchSDK._connectWS, sdks.js.repatch-sdk.RepatchSDK.payload, sdks.js.repatch-sdk.RepatchSDK.setTimeout, sdks.js.repatch-sdk.RepatchSDK._connectSSE, sdks.js.repatch-sdk.RepatchSDK.payload, sdks.js.repatch-sdk.RepatchSDK.onPatch, sdks.js.repatch-sdk.RepatchSDK.apply, sdks.js.repatch-sdk.RepatchSDK.dslClean, sdks.js.repatch-sdk.RepatchSDK.addMatch

### repatch.service.RepatchService
- **Methods**: 7
- **Key Methods**: repatch.service.RepatchService.__init__, repatch.service.RepatchService.generate_patch_suggestions, repatch.service.RepatchService._normalize_scopes, repatch.service.RepatchService._build_user_prompt, repatch.service.RepatchService._parse_choice, repatch.service.RepatchService._choice_content, repatch.service.RepatchService._default_completion

### sdks.python.repatch_sdk.RepatchClient
> Repatch Python Client SDK (v1.0.0)
Allows other Python services, agents, or CLI tools to connect to 
- **Methods**: 7
- **Key Methods**: sdks.python.repatch_sdk.RepatchClient.__init__, sdks.python.repatch_sdk.RepatchClient.on_patch, sdks.python.repatch_sdk.RepatchClient.start, sdks.python.repatch_sdk.RepatchClient._run_event_loop, sdks.python.repatch_sdk.RepatchClient._connect_and_listen, sdks.python.repatch_sdk.RepatchClient._trigger_listeners, sdks.python.repatch_sdk.RepatchClient.send_patch

### repatch.project_ir._ProjectIRParser
- **Methods**: 5
- **Key Methods**: repatch.project_ir._ProjectIRParser.__init__, repatch.project_ir._ProjectIRParser.handle_starttag, repatch.project_ir._ProjectIRParser._classify_node, repatch.project_ir._ProjectIRParser.handle_endtag, repatch.project_ir._ProjectIRParser.handle_data
- **Inherits**: HTMLParser

### repatch._html_outline._OutlineParser
- **Methods**: 5
- **Key Methods**: repatch._html_outline._OutlineParser.__init__, repatch._html_outline._OutlineParser._keep_attr, repatch._html_outline._OutlineParser.handle_starttag, repatch._html_outline._OutlineParser.handle_endtag, repatch._html_outline._OutlineParser.handle_data
- **Inherits**: HTMLParser

### repatch.web_fetch._AssetMirror
> Own mirrored-asset bookkeeping: dedup, attempt cap, naming, errors.
- **Methods**: 2
- **Key Methods**: repatch.web_fetch._AssetMirror.__init__, repatch.web_fetch._AssetMirror.mirror

### repatch.web_fetch._SSRFSafeRedirectHandler
> Re-validate each redirect target before following it.

Without this, an initially-valid public URL c
- **Methods**: 1
- **Key Methods**: repatch.web_fetch._SSRFSafeRedirectHandler.redirect_request
- **Inherits**: HTTPRedirectHandler

### repatch.organize_html.OrganizeResult
> HTML after organization plus counters for import metadata.
- **Methods**: 0

### repatch.dev_server.CSSInput
- **Methods**: 0
- **Inherits**: BaseModel

### repatch.dev_server.HTMLInput
- **Methods**: 0
- **Inherits**: BaseModel

### repatch.dev_server.SpatialDeletesInput
- **Methods**: 0
- **Inherits**: BaseModel

### repatch.dev_server.ScopeStripInput
- **Methods**: 0
- **Inherits**: BaseModel

### repatch.dev_server.ScopeInjectInput
- **Methods**: 0
- **Inherits**: BaseModel

### repatch.dev_server.OrganizeInput
- **Methods**: 0
- **Inherits**: BaseModel

### repatch.dev_server.OptionVariant
- **Methods**: 0
- **Inherits**: BaseModel

### repatch.dev_server.UIPatchPromptInput
- **Methods**: 0
- **Inherits**: BaseModel

### repatch.dev_server.UIPatchParseInput
- **Methods**: 0
- **Inherits**: BaseModel

### repatch.dev_server.FragmentInput
- **Methods**: 0
- **Inherits**: BaseModel

### repatch.web_fetch.WebAsset
> One mirrored page asset.
- **Methods**: 0

### repatch.web_fetch.WebFetchResult
> Fetched page HTML plus mirrored assets and diagnostics.
- **Methods**: 0

## Data Transformation Functions

Key functions that process and transform data:

### repatch.dev_server.css_validate
> Validate CSS safety and return detected issues.
- **Output to**: app.post, repatch.css.validate_css_safety

### repatch.dev_server.ui_patch_parse
> Parse a UI patch response into a structured payload.
- **Output to**: app.post, _ui_patch_parse.parse_ui_patch_response

### repatch.web_fetch._validate_http_url
> Reject non-http(s) URLs and hosts that resolve to private/internal
addresses (SSRF guard) — Cinema f
- **Output to**: urlparse, url.strip, socket.getaddrinfo, repatch.web_fetch._non_public_ip_reason

### repatch.web_fetch._decode_http_bytes
- **Output to**: repatch.web_fetch._charset_from_content_type, body.decode, body.decode

### repatch.web_fetch._parse_srcset
- **Output to**: None.split, item.strip, piece.split, None.join, pairs.append

### repatch.web_fetch._format_srcset
- **Output to**: None.join, chunks.append, None.strip

### _ui_patch_parse.parse_ui_patch_response
> Parse JSON object from an LLM patch response.
- **Output to**: _ui_patch_parse._strip_json_fence, data.get, json.loads, isinstance, ValueError

### repatch.css.validate_css_safety
> Reject CSS patterns that commonly break HTML/CSS patch previews.
- **Output to**: repatch.css._strip_css_comments, re.search, _RULE_RE.finditer, text.strip, violations.append

### repatch.service.RepatchService._parse_choice
- **Output to**: RepatchService._choice_content, PatchSuggestion, json.loads, ValueError, list

### marked_context._ids._parse_attrs
- **Output to**: _ATTR_RE.finditer, None.lower, marked_context._ids._normalize_label_text, match.group, match.group

### repatch.marked_context._context._format_context_body
- **Output to**: None.strip, body_blocks.append, None.join, isinstance, str

### repatch.marked_context._html._extract_and_format_fragment
- **Output to**: repatch.marked_context._html._extract_balanced_html, None.strip, len, re.sub, compact.encode

## Behavioral Patterns

### state_machine_RepatchSDK
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: sdks.js.repatch-sdk.RepatchSDK.connect, sdks.js.repatch-sdk.RepatchSDK._connectWS, sdks.js.repatch-sdk.RepatchSDK.payload, sdks.js.repatch-sdk.RepatchSDK.setTimeout, sdks.js.repatch-sdk.RepatchSDK._connectSSE

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `repatch.css.validate_css_safety` - 26 calls
- `repatch.project_ir.summarize_project_ir` - 21 calls
- `repatch._ui_patch_apply.apply_ui_patch_options` - 20 calls
- `_http_llm_context.build_http_llm_context` - 20 calls
- `repatch.options.sync_option_previews_from_workspace` - 19 calls
- `repatch._web_css.extract_visual_css` - 19 calls
- `repatch.scope.inject_scope_style` - 17 calls
- `marked_context._selectors.restrict_scope_css_to_marks` - 17 calls
- `repatch.options.enforce_deletes_on_option_previews` - 14 calls
- `repatch._images.is_lazy_placeholder_img_tag` - 14 calls
- `repatch.spatial.apply_spatial_deletes_to_html` - 14 calls
- `sdks.js.repatch-sdk.RepatchSDK.apply` - 14 calls
- `marked_context._selectors.resolve_marked_selectors` - 13 calls
- `repatch.marked_context._context.build_marked_element_context` - 13 calls
- `sdks.js.repatch-sdk.RepatchSDK.removeMatch` - 13 calls
- `repatch.organize_html.organize_html` - 12 calls
- `repatch.project_ir._ProjectIRParser.handle_endtag` - 11 calls
- `_ui_patch_parse.parse_ui_patch_response` - 11 calls
- `repatch._html_outline.build_html_outline` - 11 calls
- `marked_context._ids.effective_delete_ids` - 11 calls
- `dom_patch.build_function_option_patches` - 10 calls
- `repatch._assets.analyze_inline_scripts` - 10 calls
- `repatch.organize_html.organize_result_manifest` - 9 calls
- `repatch._web_css.normalize_linked_paths` - 9 calls
- `marked_context._ids.has_ui_marks` - 9 calls
- `repatch.marked_context._scope_css.marked_scope_colors_css` - 9 calls
- `repatch.marked_context._scope_css.marked_scope_orientation_css` - 9 calls
- `repatch.project_ir.build_project_ir` - 8 calls
- `repatch.scope.scoped_html_fragment` - 7 calls
- `repatch.options.html_files_distinct` - 7 calls
- `repatch._web_css.safe_read_under` - 7 calls
- `repatch.service.RepatchService.generate_patch_suggestions` - 7 calls
- `repatch.organize_html.organize_html_project_dir` - 6 calls
- `repatch.css.split_css_rules` - 6 calls
- `repatch._ui_patch_prompt.build_ui_patch_prompt` - 5 calls
- `repatch.dev_server.seed` - 5 calls
- `repatch._scope_kinds.normalize_focus_scope` - 5 calls
- `marked_context._ids.marked_css_selectors` - 5 calls
- `repatch.scope.inject_css_block` - 4 calls
- `dom_patch.supports_function_patch` - 4 calls

## System Interactions

How components interact:

```mermaid
graph TD
    apply_ui_patch_optio --> get
    apply_ui_patch_optio --> strip_scope_style
    apply_ui_patch_optio --> isinstance
    apply_ui_patch_optio --> ValueError
    apply_ui_patch_optio --> str
    build_http_llm_conte --> strip
    build_http_llm_conte --> _cap_patch_text
    build_http_llm_conte --> _context_parts
    sync_option_previews --> Path
    sync_option_previews --> read_text
    sync_option_previews --> apply_spatial_delete
    sync_option_previews --> exists
    sync_option_previews --> list
    extract_visual_css --> extract_inline_css
    extract_visual_css --> normalize_linked_pat
    extract_visual_css --> filter_visual_css
    extract_visual_css --> encode
    extract_visual_css --> append
    enforce_deletes_on_o --> Path
    enforce_deletes_on_o --> strip
    enforce_deletes_on_o --> read_text
    enforce_deletes_on_o --> apply_spatial_delete
    enforce_deletes_on_o --> write_text
    removeMatch --> querySelector
    removeMatch --> insertAdjacentHTML
    removeMatch --> log
    removeMatch --> Error
    removeMatch --> trim
    handle_endtag --> lower
    handle_endtag --> pop
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.