"""Normalize imported HTML before visual preprocess and patch iteration."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .web_preprocess import (
    _SCRIPT_BLOCK_RE,
    _STYLE_BLOCK_RE,
    _should_remove_preview_script,
)

EXTRACTED_CSS_NAME = "nexu-extracted.css"
EXTRACTED_JS_NAME = "nexu-extracted.js"
MIN_STYLE_EXTRACT_CHARS = 80
MIN_SCRIPT_EXTRACT_CHARS = 40
MAX_TARGETS_ADDED = 48

_STYLE_BLOCK_FULL_RE = re.compile(r"<style\b[^>]*>[\s\S]*?</style>", re.IGNORECASE)
_IMG_TAG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
_MARKABLE_OPEN_RE = re.compile(
    r"<(button|a|h[1-3]|img|section|article|main|header|footer|nav|aside)\b([^>]*)>",
    re.IGNORECASE,
)
_ATTR_RE = re.compile(r"""(\w[\w-]*)\s*=\s*(['"])(.*?)\2""", re.IGNORECASE | re.DOTALL)


@dataclass(frozen=True)
class OrganizeResult:
    """HTML after organization plus counters for import metadata."""

    html: str
    meta: dict[str, Any] = field(default_factory=dict)


def _attr_map(tag_attrs: str) -> dict[str, str]:
    return {m.group(1).lower(): m.group(3) for m in _ATTR_RE.finditer(tag_attrs or "")}


def is_lazy_placeholder_img_tag(tag: str) -> bool:
    """True for lazy-load placeholder imgs (blank src + lazy markers)."""
    if not _IMG_TAG_RE.match(str(tag or "").strip()):
        return False
    inner = tag[4:] if tag.lower().startswith("<img") else tag
    attrs = _attr_map(inner)
    src = (attrs.get("src") or "").strip().lower()
    cls = attrs.get("class") or ""
    lazy_attr = any(
        key in attrs
        for key in ("data-lazyloaded", "data-lazy-src", "data-src")
    ) or re.search(r"\blazy(?:load)?\b", cls, re.IGNORECASE)
    blank = not src or src == "#" or src.startswith("data:image/svg+xml")
    return bool(lazy_attr and blank)


def _strip_lazy_placeholder_imgs(html: str) -> tuple[str, int]:
    removed = 0

    def _replace(match: re.Match[str]) -> str:
        nonlocal removed
        tag = match.group(0)
        if is_lazy_placeholder_img_tag(tag):
            removed += 1
            return "<!-- repatch: lazy placeholder img removed -->"
        return tag

    return _IMG_TAG_RE.sub(_replace, html), removed


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


def _slug_piece(value: str, *, max_len: int = 32) -> str:
    safe = re.sub(r"[^a-zA-Z0-9]+", "-", str(value or "").strip("-").lower())
    return safe[:max_len] or "node"


def _add_markable_targets(html: str) -> tuple[str, int]:
    added = 0
    counter = 0

    def _replace(match: re.Match[str]) -> str:
        nonlocal added, counter
        if added >= MAX_TARGETS_ADDED:
            return match.group(0)
        tag = match.group(1).lower()
        attrs = match.group(2) or ""
        lowered = attrs.lower()
        if re.search(r"\bid\s*=", attrs, re.IGNORECASE):
            return match.group(0)
        if "data-nexu-target" in lowered:
            return match.group(0)
        attr_map = _attr_map(attrs)
        slug_source = attr_map.get("class") or attr_map.get("role") or tag
        counter += 1
        added += 1
        target = f"nexu-{_slug_piece(slug_source)}-{counter}"
        spacer = " " if attrs and not attrs.endswith(" ") else (" " if attrs else " ")
        return f"<{tag}{attrs}{spacer}data-nexu-target=\"{target}\">"

    return _MARKABLE_OPEN_RE.sub(_replace, html), added


def organize_html(html: str, *, base_dir: Path | None = None) -> OrganizeResult:
    """
    Extract substantial inline CSS/JS, strip preview scripts and lazy imgs, tag markable nodes.

    When ``base_dir`` is set, writes ``nexu-extracted.css`` / ``nexu-extracted.js`` beside index.
    """
    source = str(html or "")
    meta: dict[str, Any] = {
        "styles_extracted": False,
        "styles_inline_blocks": 0,
        "scripts_removed": 0,
        "scripts_extracted": False,
        "lazy_imgs_removed": 0,
        "targets_added": 0,
    }
    if not source.strip():
        return OrganizeResult(html=source, meta=meta)

    out = source
    style_text, style_blocks = _extract_inline_styles(out)
    meta["styles_inline_blocks"] = style_blocks
    if len(style_text) >= MIN_STYLE_EXTRACT_CHARS:
        wrote_css = False
        if base_dir is not None:
            try:
                (base_dir / EXTRACTED_CSS_NAME).write_text(
                    style_text + ("\n" if style_text else ""),
                    encoding="utf-8",
                )
                wrote_css = True
            except OSError:
                wrote_css = False
        else:
            wrote_css = True
            meta["extracted_css_inline"] = style_text
        if wrote_css:
            out = _STYLE_BLOCK_FULL_RE.sub("", out)
            meta["styles_extracted"] = True
            if base_dir is not None:
                meta["extracted_css_path"] = EXTRACTED_CSS_NAME
                out = _inject_head_link(out, href=EXTRACTED_CSS_NAME)

    script_chunks: list[str] = []
    scripts_removed = 0
    script_edits: list[tuple[str, str]] = []

    for match in _SCRIPT_BLOCK_RE.finditer(out):
        block = match.group(0)
        if _should_remove_preview_script(block):
            scripts_removed += 1
            script_edits.append((block, "<!-- repatch: preview script removed -->"))
            continue
        inner = re.sub(r"^<script\b[^>]*>|</script>$", "", block, flags=re.IGNORECASE | re.DOTALL)
        body = inner.strip()
        if len(body) >= MIN_SCRIPT_EXTRACT_CHARS:
            script_chunks.append(body)
            script_edits.append((block, ""))
            continue
        scripts_removed += 1
        script_edits.append((block, "<!-- repatch: inline script removed -->"))

    meta["scripts_removed"] = scripts_removed
    wrote_js = False
    if script_chunks:
        combined_js = "\n\n".join(script_chunks)
        if base_dir is not None:
            try:
                (base_dir / EXTRACTED_JS_NAME).write_text(
                    combined_js + ("\n" if combined_js else ""),
                    encoding="utf-8",
                )
                wrote_js = True
            except OSError:
                wrote_js = False
        else:
            wrote_js = True
            meta["extracted_js_inline"] = combined_js
        if wrote_js:
            meta["scripts_extracted"] = True
            if base_dir is not None:
                meta["extracted_js_path"] = EXTRACTED_JS_NAME

    for original, replacement in script_edits:
        if replacement == "" and not wrote_js:
            continue
        if original not in out:
            continue
        out = out.replace(original, replacement, 1)
    if wrote_js and base_dir is not None:
        out = _inject_head_script(out, src=EXTRACTED_JS_NAME)

    out, lazy_removed = _strip_lazy_placeholder_imgs(out)
    meta["lazy_imgs_removed"] = lazy_removed

    out, targets_added = _add_markable_targets(out)
    meta["targets_added"] = targets_added

    meta["organized"] = any(
        (
            meta.get("styles_extracted"),
            meta.get("scripts_extracted"),
            meta.get("scripts_removed"),
            lazy_removed,
            targets_added,
        )
    )
    return OrganizeResult(html=out, meta=meta)


def organize_html_project_dir(source_dir: Path) -> OrganizeResult | None:
    """Read index.html under source_dir, organize in place, return result or None if missing."""
    root = Path(source_dir)
    index_path: Path | None = None
    for name in ("index.html", "index.htm"):
        candidate = root / name
        if candidate.is_file():
            index_path = candidate
            break
    if index_path is None:
        return None
    try:
        html = index_path.read_text(encoding="utf-8")
    except OSError:
        return None
    result = organize_html(html, base_dir=root)
    if result.html != html or result.meta.get("organized"):
        try:
            index_path.write_text(result.html, encoding="utf-8")
        except OSError:
            return result
    return result


def organize_html_project(html: str, *, base_dir: Path | None = None) -> OrganizeResult:
    """Organize HTML string; alias entry point matching documented repatch API name."""
    return organize_html(html, base_dir=base_dir)


def organize_result_manifest(result: OrganizeResult) -> dict[str, Any]:
    """Serialize ``OrganizeResult`` for ``project.json`` → ``organize`` metadata."""
    meta = dict(result.meta)
    extracted_files: list[str] = []
    for key in ("extracted_css_path", "extracted_js_path"):
        path = str(meta.get(key) or "").strip()
        if path:
            extracted_files.append(path)
    return {
        **meta,
        "extracted_files": extracted_files,
        "stripped_lazy_img_count": int(meta.get("lazy_imgs_removed") or 0),
        "tagged_targets_count": int(meta.get("targets_added") or 0),
    }
