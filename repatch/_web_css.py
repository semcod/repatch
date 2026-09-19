"""Extract and filter visual CSS from imported web pages."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .css import split_css_rules

MAX_VISUAL_CSS_BYTES = 65_536

_STYLE_BLOCK_RE = re.compile(r"<style\b[^>]*>([\s\S]*?)</style>", re.IGNORECASE)
_LINK_HREF_RE = re.compile(
    r"""<link\b[^>]*\brel\s*=\s*(['"])[^'"]*stylesheet[^'"]*\1[^>]*\bhref\s*=\s*(['"])(.*?)\2""",
    re.IGNORECASE,
)
_LINK_HREF_ALT_RE = re.compile(
    r"""<link\b[^>]*\bhref\s*=\s*(['"])(.*?)\1[^>]*\brel\s*=\s*(['"])[^'"]*stylesheet[^'"]*\3""",
    re.IGNORECASE,
)
_SKIP_AT_RULE_RE = re.compile(r"@(font-face|keyframes)\b", re.IGNORECASE)
_PRINT_MEDIA_RE = re.compile(r"@media\s+print\b", re.IGNORECASE)

_VISUAL_PROPS = frozenset(
    {
        "color",
        "background",
        "background-color",
        "background-image",
        "border",
        "border-color",
        "border-radius",
        "border-width",
        "border-style",
        "box-shadow",
        "font",
        "font-family",
        "font-size",
        "font-weight",
        "fill",
        "stroke",
        "width",
        "height",
        "min-width",
        "min-height",
        "max-width",
        "max-height",
        "aspect-ratio",
        "display",
        "flex",
        "flex-direction",
        "flex-wrap",
        "grid",
        "grid-template",
        "grid-template-columns",
        "grid-template-rows",
        "gap",
        "padding",
        "margin",
        "opacity",
        "transform",
        "clip-path",
        "outline",
        "outline-color",
        "outline-width",
    }
)
_PROP_PATTERN = re.compile(
    r"(?<![\w-])("
    + "|".join(re.escape(p) for p in sorted(_VISUAL_PROPS, key=len, reverse=True))
    + r")\s*:",
    re.IGNORECASE,
)
_VAR_PATTERN = re.compile(r"--[\w-]+\s*:", re.IGNORECASE)


def safe_read_under(base_dir: Path, rel_path: str) -> str | None:
    """Read a file only when it resolves under base_dir."""
    try:
        resolved_base = base_dir.resolve()
        candidate = (base_dir / rel_path).resolve()
        if not str(candidate).startswith(str(resolved_base) + "/") and candidate != resolved_base:
            return None
        if not candidate.is_file():
            return None
        return candidate.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def extract_inline_css(html: str) -> str:
    blocks = _STYLE_BLOCK_RE.findall(html or "")
    return "\n\n".join(block.strip() for block in blocks if block.strip())


def extract_stylesheet_hrefs(html: str) -> list[str]:
    hrefs: list[str] = []
    for pattern in (_LINK_HREF_RE, _LINK_HREF_ALT_RE):
        for match in pattern.finditer(html or ""):
            href = match.group(3 if pattern is _LINK_HREF_RE else 2).strip()
            if href and href not in hrefs:
                hrefs.append(href)
    return hrefs


def normalize_linked_paths(linked_css_paths: list[str] | None, html: str) -> list[str]:
    paths: list[str] = []
    for item in linked_css_paths or []:
        rel = str(item).strip().lstrip("/")
        if rel and rel not in paths:
            paths.append(rel)
    for href in extract_stylesheet_hrefs(html):
        rel = href.strip()
        if rel.startswith(("http://", "https://", "//", "data:")):
            continue
        rel = rel.lstrip("/")
        if rel and rel not in paths:
            paths.append(rel)
    return paths


def _rule_is_visual(rule: str) -> bool:
    body = rule.strip()
    if not body:
        return False
    if _SKIP_AT_RULE_RE.search(body):
        return False
    if _PRINT_MEDIA_RE.search(body):
        return False
    if _VAR_PATTERN.search(body):
        return True
    if _PROP_PATTERN.search(body):
        return True
    selector = body.split("{", 1)[0].strip().lower()
    return selector in {":root", "html", "body"}


def filter_visual_css(css: str) -> str:
    kept: list[str] = []
    for rule in split_css_rules(css):
        if _rule_is_visual(rule):
            kept.append(rule)
    return "\n\n".join(kept)


def extract_visual_css(
    html: str,
    linked_css_paths: list[str] | None,
    source_dir: Path,
) -> tuple[str, dict[str, Any]]:
    """Extract color/shape/layout CSS from inline styles and linked sheets."""
    chunks: list[str] = []
    inline = extract_inline_css(html)
    if inline:
        chunks.append(inline)
    for rel in normalize_linked_paths(linked_css_paths, html):
        local = rel
        if local.startswith("assets/"):
            pass
        elif local.startswith("source/"):
            local = local[len("source/") :]
        text = safe_read_under(source_dir, local)
        if text:
            chunks.append(f"/* from {rel} */\n{text}")
    filtered = filter_visual_css("\n\n".join(chunks))
    visual_css_stats: dict[str, Any] = {
        "visual_css_bytes": len(filtered.encode("utf-8")),
        "visual_css_truncated": False,
    }
    encoded = filtered.encode("utf-8")
    if len(encoded) > MAX_VISUAL_CSS_BYTES:
        truncated = encoded[:MAX_VISUAL_CSS_BYTES].decode("utf-8", errors="ignore").rstrip()
        if not truncated.endswith("}"):
            truncated += "\n/* repatch: visual CSS truncated at 64KB */"
        filtered = truncated
        visual_css_stats["visual_css_bytes"] = len(filtered.encode("utf-8"))
        visual_css_stats["visual_css_truncated"] = True
    return filtered, visual_css_stats
