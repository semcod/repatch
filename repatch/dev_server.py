"""FastAPI development server exposing repatch utilities with OpenAPI docs.

Run locally (single command)::

    make dev            # seeds fixtures + uvicorn --reload on :8000

or via Docker (single command)::

    docker compose up   # build + run the dev server with hot-reload

Interactive API docs are served automatically at ``/docs`` (Swagger UI) and
``/redoc`` (ReDoc) thanks to FastAPI's OpenAPI generation.
"""

from __future__ import annotations

import importlib.metadata
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from . import (
    apply_spatial_deletes_to_html,
    build_ui_patch_prompt,
    inject_scope_style,
    organize_html,
    parse_ui_patch_response,
    scoped_html_fragment,
    split_css_rules,
    strip_scope_style,
    validate_css_safety,
)
from .seeds import get_seed, list_seeds, seed_kind

try:
    __version__ = importlib.metadata.version("repatch")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0+dev"


app = FastAPI(
    title="repatch dev server",
    description="Local developer API for the repatch HTML/CSS/DOM patch utilities.",
    version=__version__,
)


# --- Request models ---------------------------------------------------------


class CSSInput(BaseModel):
    css: str = Field(..., description="Raw CSS text to process.")
    source: str = Field("css", description="Optional source label for safety validation.")


class HTMLInput(BaseModel):
    html: str = Field(..., description="HTML fragment or full document.")


class SpatialDeletesInput(BaseModel):
    html: str = Field(..., description="HTML to apply spatial deletes to.")
    delete_ids: list[str] = Field(..., description="Element ids / keys to delete.")


class ScopeStripInput(BaseModel):
    html: str = Field(..., description="HTML to strip injected scope styles from.")


class ScopeInjectInput(BaseModel):
    html: str = Field(..., description="HTML to inject a scope style into.")
    scope: str = Field(..., description="Focus scope id, e.g. 'colors', 'display', 'shapes'.")
    variant: str = Field(..., description="Scope variant, e.g. 'a', 'b', 'c'.")
    project_kind: str = Field("", description="Optional project kind hint.")
    delete_ids: list[str] | None = Field(None, description="Optional delete element ids.")
    keep_ids: list[str] | None = Field(None, description="Optional keep element ids.")
    user_goal: str = Field("", description="Optional user goal description.")


class OrganizeInput(BaseModel):
    html: str = Field(..., description="HTML to organize (inline CSS/JS extraction, markable targets).")


class OptionVariant(BaseModel):
    filename: str = Field(..., description="Variant filename, e.g. 'alt_a.html'.")
    label: str = Field("", description="Short label for the variant.")
    direction: str = Field("", description="Direction note for the variant.")


class UIPatchPromptInput(BaseModel):
    html: str = Field(..., description="HTML to build a UI patch prompt for.")
    focus_scope: str = Field(..., description="Focus scope id.")
    project_kind: str = Field(..., description="Project kind hint.")
    option_variants: list[OptionVariant] = Field(default_factory=list, description="A/B/C option variants.")
    user_goal: str = Field("", description="Optional user goal description.")
    keep_els: list[str] | None = Field(None, description="Optional keep element ids.")
    delete_els: list[str] | None = Field(None, description="Optional delete element ids.")
    context_fragment: str | None = Field(None, description="Optional pre-computed context fragment.")


class UIPatchParseInput(BaseModel):
    text: str = Field(..., description="Raw UI patch response text (JSON, possibly fenced).")


class FragmentInput(BaseModel):
    html: str = Field(..., description="HTML to derive a scoped fragment from.")
    focus_scope: str = Field(..., description="Focus scope id.")
    project_kind: str = Field(..., description="Project kind hint.")


# --- Routes -----------------------------------------------------------------


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    """Redirect to the interactive OpenAPI docs."""
    return RedirectResponse(url="/docs")


@app.get("/health")
def health() -> dict[str, Any]:
    """Basic liveness and version probe."""
    return {"status": "ok", "version": __version__, "seeds": len(list_seeds())}


@app.post("/css/split")
def css_split(body: CSSInput) -> dict[str, Any]:
    """Split raw CSS into individual rules."""
    return {"rules": split_css_rules(body.css)}


@app.post("/css/validate")
def css_validate(body: CSSInput) -> dict[str, Any]:
    """Validate CSS safety and return detected issues."""
    ok, issues = validate_css_safety(body.css, source=body.source)
    return {"ok": ok, "issues": issues}


@app.post("/spatial/deletes")
def spatial_deletes(body: SpatialDeletesInput) -> dict[str, Any]:
    """Apply spatial deletes to an HTML fragment."""
    patched_html, removed = apply_spatial_deletes_to_html(body.html, body.delete_ids)
    return {"html": patched_html, "removed": removed}


@app.post("/scope/strip")
def scope_strip(body: ScopeStripInput) -> dict[str, Any]:
    """Remove injected scope styles from HTML."""
    return {"html": strip_scope_style(body.html)}


@app.post("/scope/inject")
def scope_inject(body: ScopeInjectInput) -> dict[str, Any]:
    """Inject a scope style into HTML."""
    patched_html = inject_scope_style(
        body.html,
        body.scope,
        body.variant,
        project_kind=body.project_kind,
        delete_ids=body.delete_ids,
        keep_ids=body.keep_ids,
        user_goal=body.user_goal,
    )
    return {"html": patched_html}


@app.post("/organize")
def organize(body: OrganizeInput) -> dict[str, Any]:
    """Organize HTML: extract inline CSS/JS and tag markable nodes."""
    result = organize_html(body.html)
    return {"html": result.html, "meta": result.meta}


@app.post("/ui-patch/prompt")
def ui_patch_prompt(body: UIPatchPromptInput) -> dict[str, Any]:
    """Build a JSON-only UI patch prompt for scoped A-C options."""
    variants = [(v.filename, v.label, v.direction) for v in body.option_variants]
    prompt = build_ui_patch_prompt(
        body.html,
        focus_scope=body.focus_scope,
        project_kind=body.project_kind,
        option_variants=variants,
        user_goal=body.user_goal,
        keep_els=body.keep_els,
        delete_els=body.delete_els,
        context_fragment=body.context_fragment,
    )
    return {"prompt": prompt}


@app.post("/ui-patch/parse")
def ui_patch_parse(body: UIPatchParseInput) -> dict[str, Any]:
    """Parse a UI patch response into a structured payload."""
    return parse_ui_patch_response(body.text)


@app.post("/fragment")
def fragment(body: FragmentInput) -> dict[str, Any]:
    """Derive a scoped HTML fragment for a focus scope."""
    result = scoped_html_fragment(body.html, body.focus_scope, body.project_kind)
    return {"fragment": result}


@app.get("/seeds")
def seeds() -> dict[str, Any]:
    """List available seed fixtures."""
    return {"seeds": [{"name": name, "kind": seed_kind(name)} for name in list_seeds()]}


@app.get("/seeds/{name}")
def seed(name: str) -> dict[str, Any]:
    """Return a single seed fixture by name."""
    try:
        content = get_seed(name)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"name": name, "kind": seed_kind(name), "content": content}
