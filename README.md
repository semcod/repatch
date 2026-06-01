# repatch

Reusable HTML/CSS/DOM patch utilities extracted from Nexu Cinema: marked-element context,
scope-restricted CSS, spatial deletes, LLM UI patch prompts, and local function DOM patches.

Also includes the original `RepatchService` for scope-based LLM fragment suggestions.

## Install

```bash
pip install -e .
# Nexu: repatch @ file:///path/to/repatch in pyproject.toml
```

## Public API (`repatch`)

| Module | Key symbols |
|--------|-------------|
| `marked_context` | `build_marked_element_context`, `resolve_marked_llm_context`, `restrict_scope_css_to_marks`, `marked_css_selectors`, `has_ui_marks` |
| `scope` | `inject_scope_style`, `strip_scope_style`, `normalize_focus_scope`, `should_block_full_html_iterate`, `scoped_html_fragment` |
| `ui_patch` | `build_ui_patch_prompt`, `parse_ui_patch_response`, `apply_ui_patch_options`, `supports_llm_patch_scope` |
| `spatial` | `apply_spatial_deletes_to_html` |
| `dom_patch` | `build_function_option_patches`, `build_function_patch_context`, `supports_function_patch` |
| `options` | `sync_option_previews_from_workspace`, `enforce_deletes_on_option_previews`, `replace_html_title`, `html_files_distinct` |
| `css` | `split_css_rules`, `validate_css_safety` |
| `project_ir` | `build_project_ir`, `summarize_project_ir` |
| `service` | `RepatchService`, `PatchSuggestion` |

## Multi-Language Client SDKs

The `repatch` repository provides official client-side and process SDKs under the `sdks/` directory to simplify surgical real-time UI mutations across different languages and platforms:

### 1. JavaScript SDK (`sdks/js/repatch-sdk.js`)
A client-side library to be included in browsers. It connects to the Repatch WebSocket/SSE stream and executes surgical updates:
- `ADD <selector> <html_content>`: Appends child element.
- `REPLACE <selector> <html_content>`: Replaces content.
- `STYLE <selector> { css }`: Scopes CSS to element.
- `REMOVE <selector>`: Deletes element.

### 2. Python Client SDK (`sdks/python/repatch_sdk.py`)
A thread-safe client that allows other python services, test harnesses, or CLI agents to subscribe or broadcast patches:
```python
from repatch_sdk import RepatchClient

client = RepatchClient("ws://localhost:8083/repatch")

@client.on_patch
def handle_patch(data):
    print("Received patch DSL:", data["dsl"])

client.start()
client.send_patch("STYLE #btn-eq { background: red; }")
```

---

## Example: marked context + UI patch prompt

```python
from repatch import build_marked_element_context
from repatch.ui_patch import build_ui_patch_prompt

ctx = build_marked_element_context(html, keep_ids=["7"], delete_ids=["tan"], focus_scope="colors", project_kind="calculator")
prompt = build_ui_patch_prompt(html, focus_scope="colors", project_kind="calculator", option_variants=variants, context_fragment=ctx)
```

## Example: file-level option previews

```python
from repatch import enforce_deletes_on_option_previews, sync_option_previews_from_workspace

sync_option_previews_from_workspace(
    "capsule/cinema",
    stage=0,
    delete_ids=["old-cta"],
    finalize_html=my_finalize_html,
)

enforce_deletes_on_option_previews(
    "capsule/cinema",
    ["old-cta"],
    finalize_html=my_finalize_html,
)
```

## Original RepatchService (v0)

```python
from repatch import RepatchService

service = RepatchService(model="gpt-4o-mini")

fragment = """
<section>
  <h1>Pracownia Malort Gdynia – przestrzeń dla kreatywności Twojego dziecka</h1>
  <p>Zapraszamy do wyjątkowego miejsca...</p>

## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.2.5-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$1.38-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-3.7h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $1.3837 (8 commits)
- 👤 **Human dev:** ~$375 (3.7h @ $100/h, 30min dedup)

Generated on 2026-06-01 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

  <button>Zapisz dziecko</button>
</section>
"""

suggestions = service.generate_patch_suggestions(
    fragment=fragment,
    scopes=["display", "colors"],
)

for idx, item in enumerate(suggestions, start=1):
    print(f"Wariant {idx}:")
    print("KEEP:", item.keep)
    print("CHANGE:", item.change)
    print(item.patched_fragment)
```

## License

Licensed under Apache-2.0.
