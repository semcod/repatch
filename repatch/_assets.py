"""Extract and relocate inline CSS/JS assets during HTML organization."""

from __future__ import annotations

import re

from .web_preprocess import (
    _SCRIPT_BLOCK_RE,
    _STYLE_BLOCK_RE,
    _should_remove_preview_script,
)

EXTRACTED_CSS_NAME = "nexu-extracted.css"
EXTRACTED_JS_NAME = "nexu-extracted.js"
MIN_STYLE_EXTRACT_CHARS = 80
MIN_SCRIPT_EXTRACT_CHARS = 40

_STYLE_BLOCK_FULL_RE = re.compile(r"<style\b[^>]*>[\s\S]*?</style>", re.IGNORECASE)


def _extract_inline_styles(html: str) -> tuple[str, int]:
    bodies = [block.strip() for block in _STYLE_BLOCK_RE.findall(html or "") if block.strip()]
    combined = "\n\n".join(bodies)
    return combined, len(bodies)


def _inject_head_link(html: str, *, href: str, rel: str = "stylesheet") -> str:
    link = f'<link rel="{rel}" href="{href}">'
    head_match = re.search(r"(<head\b[^>]*>)", html, re.IGNORECASE)
    if head_match:
        insert_at = head_match.end()
        return html[:insert_at] + "\n  " + link + html[insert_at:]
    html_match = re.search(r"(<html\b[^>]*>)", html, re.IGNORECASE)
    if html_match:
        insert_at = html_match.end()
        return html[:insert_at] + f"\n<head>{link}</head>" + html[insert_at:]
    return link + "\n" + html


def _inject_head_script(html: str, *, src: str) -> str:
    tag = f'<script src="{src}"></script>'
    head_match = re.search(r"(<head\b[^>]*>)", html, re.IGNORECASE)
    if head_match:
        insert_at = head_match.end()
        return html[:insert_at] + "\n  " + tag + html[insert_at:]
    html_match = re.search(r"(<html\b[^>]*>)", html, re.IGNORECASE)
    if html_match:
        insert_at = html_match.end()
        return html[:insert_at] + f"\n<head>{tag}</head>" + html[insert_at:]
    return tag + "\n" + html


def analyze_inline_scripts(html: str) -> tuple[list[str], int, list[tuple[str, str]]]:
    """Return (script_chunks, scripts_removed, script_edits) for inline scripts."""
    script_chunks: list[str] = []
    scripts_removed = 0
    script_edits: list[tuple[str, str]] = []

    for match in _SCRIPT_BLOCK_RE.finditer(html):
        block = match.group(0)
        if _should_remove_preview_script(block):
            scripts_removed += 1
            script_edits.append((block, "<!-- repatch: preview script removed -->"))
            continue
        script_body = re.sub(r"^<script\b[^>]*>|</script>$", "", block, flags=re.IGNORECASE | re.DOTALL)
        script_text = script_body.strip()
        if len(script_text) >= MIN_SCRIPT_EXTRACT_CHARS:
            script_chunks.append(script_text)
            script_edits.append((block, ""))
            continue
        scripts_removed += 1
        script_edits.append((block, "<!-- repatch: inline script removed -->"))

    return script_chunks, scripts_removed, script_edits
