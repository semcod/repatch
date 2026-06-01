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
| `css` | `split_css_rules`, `validate_css_safety` |
| `project_ir` | `build_project_ir`, `summarize_project_ir` |
| `service` | `RepatchService`, `PatchSuggestion` |

## Example: marked context + UI patch prompt

```python
from repatch import build_marked_element_context
from repatch.ui_patch import build_ui_patch_prompt

ctx = build_marked_element_context(html, keep_ids=["7"], delete_ids=["tan"], focus_scope="colors", project_kind="calculator")
prompt = build_ui_patch_prompt(html, focus_scope="colors", project_kind="calculator", option_variants=variants, context_fragment=ctx)
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

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.2.2-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$0.75-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-3.0h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $0.7487 (6 commits)
- 👤 **Human dev:** ~$300 (3.0h @ $100/h, 30min dedup)

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
