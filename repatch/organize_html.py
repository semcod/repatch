"""Normalize imported HTML before visual preprocess and patch iteration."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ._assets import (
    _STYLE_BLOCK_FULL_RE,
    EXTRACTED_CSS_NAME,
    EXTRACTED_JS_NAME,
    MIN_STYLE_EXTRACT_CHARS,
    _extract_inline_styles,
    _inject_head_link,
    _inject_head_script,
    analyze_inline_scripts,
)
from ._images import _strip_lazy_placeholder_imgs
from ._targets import _add_markable_targets


@dataclass(frozen=True)
class OrganizeResult:
    """HTML after organization plus counters for import metadata."""

    html: str
    meta: dict[str, Any] = field(default_factory=dict)


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

    script_chunks, scripts_removed, script_edits = analyze_inline_scripts(out)
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
