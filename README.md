# repatch

First simple Python package for scope-based HTML/CSS/JS patch suggestions via LiteLLM.

Pierwsza, prosta wersja pakietu Python do generowania propozycji patchy fragmentów
HTML/CSS/JS na podstawie scope i odpowiedzi LLM przez `litellm`.

## Zakres v0

- obsługa scope:
  - `functions`
  - `display`
  - `colors`
  - `shapes`
  - `orientation`
- wybór wielu scope naraz
- generowanie **3 wariantów** odpowiedzi z LLM
- dla każdego wariantu: co zachować (`keep`), co zmienić (`change`) i patchowany fragment (`patched_fragment`)

## Instalacja (lokalnie)

```bash
pip install -e .
```

## Szybkie użycie

```python
from repatch import RepatchService

service = RepatchService(model="gpt-4o-mini")

fragment = """
<section>
  <h1>Pracownia Malort Gdynia – przestrzeń dla kreatywności Twojego dziecka</h1>
  <p>Zapraszamy do wyjątkowego miejsca...</p>

## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.1.1-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$0.02-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-2.0h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $0.0228 (4 commits)
- 👤 **Human dev:** ~$200 (2.0h @ $100/h, 30min dedup)

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
