# repatch

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