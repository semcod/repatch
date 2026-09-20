"""Assemble compact LLM patch context from imported-page artifacts."""

from __future__ import annotations

from typing import Any

MAX_EXTRACTED_PATCH_BYTES = 16_384


def _cap_patch_text(text: str, max_bytes: int, *, section_label: str) -> str:
    uncapped_text = str(text or "").strip()
    if not uncapped_text:
        return ""
    encoded = uncapped_text.encode("utf-8")
    if len(encoded) <= max_bytes:
        return uncapped_text
    truncated = encoded[:max_bytes].decode("utf-8", errors="ignore").rstrip()
    return truncated + f"\n/* repatch: {section_label} truncated */"


def build_http_llm_context(artifacts: dict[str, Any]) -> str:
    """Combine visual CSS + HTML outline (+ organize manifest) for compact LLM patch prompts."""
    visual_css_text = str(artifacts.get("visual_css") or "").strip()
    outline = str(artifacts.get("html_outline") or "").strip()
    organize = artifacts.get("organize") if isinstance(artifacts.get("organize"), dict) else {}
    extracted_css = _cap_patch_text(
        str(artifacts.get("extracted_css") or ""),
        MAX_EXTRACTED_PATCH_BYTES,
        section_label="extracted CSS",
    )
    extracted_js = _cap_patch_text(
        str(artifacts.get("extracted_js") or ""),
        MAX_EXTRACTED_PATCH_BYTES,
        section_label="extracted JS",
    )
    source_paths = (
        artifacts.get("source_paths") if isinstance(artifacts.get("source_paths"), dict) else {}
    )
    if (
        not visual_css_text
        and not outline
        and not organize
        and not extracted_css
        and not extracted_js
    ):
        return ""
    context_blocks = _context_parts(
        organize, source_paths, extracted_css, extracted_js, visual_css_text, outline
    )
    return "\n\n".join(context_blocks)


def _organize_manifest_lines(organize: dict[str, Any]) -> list[str]:
    """Build human-readable manifest lines from the organize metadata."""
    lines: list[str] = []
    extracted_files = organize.get("extracted_files")
    if isinstance(extracted_files, list) and extracted_files:
        lines.append(
            "Extracted inline assets: " + ", ".join(str(item) for item in extracted_files if item)
        )
    if tagged := organize.get("tagged_targets_count"):
        lines.append(
            f"Markable nodes tagged with data-nexu-target: {int(tagged)} "
            "(use these selectors when referencing unlabelled elements)."
        )
    if lazy := organize.get("stripped_lazy_img_count"):
        lines.append(f"Lazy placeholder images removed at import: {int(lazy)}")
    return lines


def _source_paths_part(source_paths: dict[str, Any]) -> str | None:
    paths = "\n".join(
        f"- {key}: {value}" for key, value in source_paths.items() if str(value).strip()
    )
    if not paths:
        return None
    return "Editable source files (prefer patching these over full stage0.html):\n" + paths


def _context_parts(
    organize: dict[str, Any],
    source_paths: dict[str, Any],
    extracted_css: str,
    extracted_js: str,
    css: str,
    outline: str,
) -> list[str]:
    prompt_sections = [
        (
            "IMPORTED WEB PAGE (patch mode — change CSS property values and minimal HTML attributes only; "
            "do not replace the entire document)."
        ),
    ]
    if organize or source_paths:
        manifest_lines = _organize_manifest_lines(organize)
        if manifest_lines:
            prompt_sections.append("Import organize manifest:\n" + "\n".join(manifest_lines))
        source_part = _source_paths_part(source_paths)
        if source_part:
            prompt_sections.append(source_part)
    if extracted_css:
        prompt_sections.append(
            "Extracted inline CSS (from source/index.html):\n```css\n" + extracted_css + "\n```"
        )
    if extracted_js:
        prompt_sections.append(
            "Extracted inline JS (reference only — do not re-add <script> tags):\n```js\n"
            + extracted_js
            + "\n```"
        )
    if css:
        prompt_sections.append("Visual CSS (colors, shapes, layout tokens):\n```css\n" + css + "\n```")
    if outline:
        prompt_sections.append("HTML structure outline:\n```html\n" + outline + "\n```")
    return prompt_sections


def http_patch_llm_rules() -> str:
    """Extra LLM rules when iterating imported HTTP projects in patch mode."""
    return (
        "PATCH MODE: the page was imported from the live web.\n"
        "Prefer editing CSS property values in the visual CSS block; avoid regenerating the full HTML document.\n"
        "Preserve ids, classes, data-* markers, and the HTML skeleton structure.\n"
        "When HTML changes are required, patch only attributes or minimal wrapper nodes — never replace the whole tree.\n"
        "Do NOT include <script> tags — runtime is injected by the host application after generation."
    )
