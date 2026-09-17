"""Seed fixtures for the local repatch development server.

These fixtures let a developer exercise the repatch utility endpoints from
``/docs`` without writing their own inputs. They are loaded on startup by
``repatch.dev_server`` and can also be inspected from the CLI::

    python -m repatch.seeds
"""

from __future__ import annotations

SEED_KINDS: dict[str, str] = {
    "calculator.html": "html",
    "cinema.html": "html",
    "button-styles.css": "css",
    "ui-patch-response.json": "json",
}

SEEDS: dict[str, str] = {
    "calculator.html": """\
<div id="calc" data-mark-target="1">
  <button id="btn-eq" data-mark-target="1">=</button>
  <button id="btn-plus" data-mark-target="1">+</button>
  <span id="display">0</span>
</div>
""",
    "cinema.html": """\
<section id="cinema-hero" data-mark-target="1">
  <h1 id="hero-title">Pracownia Malort Gdynia</h1>
  <p id="hero-copy">Zapraszamy do wyjątkowego miejsca...</p>
  <button id="old-cta">Kup bilet</button>
</section>
""",
    "button-styles.css": """\
#btn-eq { background: red; }
#btn-plus { background: blue; padding: 8px; }
""",
    "ui-patch-response.json": """\
{"keep": ["#btn-eq"], "change": ["#btn-plus"], "patched_fragment": "<button id=\\"btn-plus\\">+</button>"}
""",
}


def list_seeds() -> list[str]:
    """Return the names of all available seed fixtures, sorted."""
    return sorted(SEEDS)


def get_seed(name: str) -> str:
    """Return the content of a seed fixture by name."""
    try:
        return SEEDS[name]
    except KeyError as exc:
        raise KeyError(f"Unknown seed: {name!r}") from exc


def seed_kind(name: str) -> str:
    """Return the content kind of a seed fixture."""
    return SEED_KINDS.get(name, "text")


if __name__ == "__main__":
    print("Available repatch seed fixtures:")
    for name in list_seeds():
        print(f"  - {name} ({seed_kind(name)})")
