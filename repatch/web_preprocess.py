"""Prepare imported web pages for fast patching and LLM-safe iteration."""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from .css import split_css_rules

MAX_VISUAL_CSS_BYTES = 65_536
OUTLINE_TEXT_PLACEHOLDER = "…"

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
_SCRIPT_BLOCK_RE = re.compile(r"<script\b[^>]*>[\s\S]*?</script>", re.IGNORECASE)
_SCRIPT_SRC_ATTR_RE = re.compile(r"""\bsrc\s*=\s*(['"])(.*?)\1""", re.IGNORECASE)
_NEXU_PREVIEW_SHIM_MARKER = "nexu preview: block cross-origin fetch"

HTTP_PREVIEW_NETWORK_SHIM = f"""<script>/* {_NEXU_PREVIEW_SHIM_MARKER} */
(function(){{
  var previewOrigin = location.origin;
  function nexuCrossOrigin(url) {{
    try {{
      var resolved = new URL(String(url || ""), document.baseURI || location.href);
      return resolved.origin !== previewOrigin;
    }} catch (_) {{
      return true;
    }}
  }}
  var nativeFetch = window.fetch;
  if (typeof nativeFetch === "function") {{
    window.fetch = function(input, init) {{
      var url = typeof input === "string" ? input : (input && input.url) || "";
      if (nexuCrossOrigin(url)) {{
        return Promise.resolve(new Response("", {{status: 204, statusText: "nexu preview blocked"}}));
      }}
      return nativeFetch.apply(this, arguments);
    }};
  }}
  var NativeXHR = window.XMLHttpRequest;
  if (typeof NativeXHR === "function") {{
    window.XMLHttpRequest = function() {{
      var xhr = new NativeXHR();
      var nativeOpen = xhr.open;
      xhr.open = function(method, url) {{
        if (nexuCrossOrigin(url)) {{
          xhr._nexuBlocked = true;
          return;
        }}
        return nativeOpen.apply(xhr, arguments);
      }};
      var nativeSend = xhr.send;
      xhr.send = function() {{
        if (xhr._nexuBlocked) return;
        return nativeSend.apply(xhr, arguments);
      }};
      return xhr;
    }};
  }}
  window.kadenceConfig = window.kadenceConfig || {{}};
}})();
</script>"""

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
        root = base_dir.resolve()
        candidate = (base_dir / rel_path).resolve()
        if not str(candidate).startswith(str(root) + "/") and candidate != root:
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
    meta: dict[str, Any] = {
        "visual_css_bytes": len(filtered.encode("utf-8")),
        "visual_css_truncated": False,
    }
    encoded = filtered.encode("utf-8")
    if len(encoded) > MAX_VISUAL_CSS_BYTES:
        truncated = encoded[:MAX_VISUAL_CSS_BYTES].decode("utf-8", errors="ignore").rstrip()
        if not truncated.endswith("}"):
            truncated += "\n/* repatch: visual CSS truncated at 64KB */"
        filtered = truncated
        meta["visual_css_bytes"] = len(filtered.encode("utf-8"))
        meta["visual_css_truncated"] = True
    return filtered, meta


class _OutlineParser(HTMLParser):
    _SKIP_TAGS = frozenset({"script", "style", "noscript"})
    _VOID_TAGS = frozenset(
        {
            "area",
            "base",
            "br",
            "col",
            "embed",
            "hr",
            "img",
            "input",
            "link",
            "meta",
            "param",
            "source",
            "track",
            "wbr",
        }
    )
    _KEEP_ATTR_PREFIXES = ("data-nexu", "aria-")

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.node_count = 0
        self._skip_depth = 0
        self._indent = 0

    def _keep_attr(self, name: str) -> bool:
        key = name.lower()
        return key in {"id", "class", "role"} or key.startswith(self._KEEP_ATTR_PREFIXES)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self._SKIP_TAGS:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        kept = [(k, v) for k, v in attrs if v is not None and self._keep_attr(k)]
        attr_text = "".join(f' {k}="{v}"' for k, v in kept)
        indent = "  " * self._indent
        if tag in self._VOID_TAGS:
            self.parts.append(f"{indent}<{tag}{attr_text} />")
        else:
            self.parts.append(f"{indent}<{tag}{attr_text}>")
            self._indent += 1
        self.node_count += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in self._SKIP_TAGS:
            self._skip_depth = max(0, self._skip_depth - 1)
            return
        if self._skip_depth or tag in self._VOID_TAGS:
            return
        self._indent = max(0, self._indent - 1)
        indent = "  " * self._indent
        self.parts.append(f"{indent}</{tag}>")

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        text = re.sub(r"\s+", " ", data or "").strip()
        if not text:
            return
        indent = "  " * self._indent
        self.parts.append(f"{indent}{OUTLINE_TEXT_PLACEHOLDER}")


def build_html_outline(html: str) -> tuple[str, dict[str, Any]]:
    """Build a compact HTML skeleton without scripts or full text content."""
    cleaned = re.sub(r"<!--[\s\S]*?-->", "", str(html or ""))
    parser = _OutlineParser()
    parser.feed(cleaned)
    parser.close()
    outline = "\n".join(parser.parts).strip()
    if not outline.lower().startswith("<!doctype"):
        outline = f"<!DOCTYPE html>\n{outline}"
    meta = {"outline_node_count": parser.node_count, "outline_bytes": len(outline.encode("utf-8"))}
    return outline, meta


def _script_src_allowed_for_preview(src: str) -> bool:
    cleaned = str(src or "").strip()
    if not cleaned:
        return False
    if cleaned.startswith(("http://", "https://", "//", "data:")):
        return False
    return cleaned.lower().startswith("imported_projects/")


def _should_remove_preview_script(tag: str) -> bool:
    src_match = _SCRIPT_SRC_ATTR_RE.search(tag)
    if src_match:
        return not _script_src_allowed_for_preview(src_match.group(2))
    return True


def sanitize_http_preview_html(html: str) -> tuple[str, dict[str, Any]]:
    """Strip live-site scripts from HTTP preview HTML; keep CSS/layout markup."""
    removed = 0

    def replace_script(match: re.Match[str]) -> str:
        nonlocal removed
        block = match.group(0)
        if _should_remove_preview_script(block):
            removed += 1
            return "<!-- repatch: preview script removed -->"
        return block

    cleaned = _SCRIPT_BLOCK_RE.sub(replace_script, str(html or ""))
    return cleaned, {"preview_scripts_removed": removed}


def inject_http_preview_shim(html: str) -> str:
    """Inject early head shim that blocks cross-origin fetch/XHR in preview iframes."""
    if _NEXU_PREVIEW_SHIM_MARKER in html:
        return html
    head_match = re.search(r"(<head\b[^>]*>)", html, re.IGNORECASE)
    if head_match:
        insert_at = head_match.end()
        return html[:insert_at] + "\n" + HTTP_PREVIEW_NETWORK_SHIM + html[insert_at:]
    html_match = re.search(r"(<html\b[^>]*>)", html, re.IGNORECASE)
    if html_match:
        insert_at = html_match.end()
        wrapped = f"<head>{HTTP_PREVIEW_NETWORK_SHIM}</head>{html[insert_at:]}"
        return html[:insert_at] + wrapped
    return HTTP_PREVIEW_NETWORK_SHIM + html


def prepare_http_preview_html(html: str) -> tuple[str, dict[str, Any]]:
    """Sanitize scripts and inject network isolation shim for preview iframes."""
    cleaned, meta = sanitize_http_preview_html(html)
    out = inject_http_preview_shim(cleaned)
    meta["preview_shim_injected"] = _NEXU_PREVIEW_SHIM_MARKER in out
    return out, meta


def build_http_llm_context(artifacts: dict[str, Any]) -> str:
    """Combine visual CSS + HTML outline for compact LLM patch prompts."""
    css = str(artifacts.get("visual_css") or "").strip()
    outline = str(artifacts.get("html_outline") or "").strip()
    if not css and not outline:
        return ""
    parts = [
        "IMPORTED WEB PAGE (patch mode — change CSS property values and minimal HTML attributes only; "
        "do not replace the entire document).",
    ]
    if css:
        parts.append("Visual CSS (colors, shapes, layout tokens):\n```css\n" + css + "\n```")
    if outline:
        parts.append("HTML structure outline:\n```html\n" + outline + "\n```")
    return "\n\n".join(parts)


def http_patch_llm_rules() -> str:
    """Extra LLM rules when iterating imported HTTP projects in patch mode."""
    return "\n".join(
        [
            "PATCH MODE: the page was imported from the live web.",
            "Prefer editing CSS property values in the visual CSS block; avoid regenerating the full HTML document.",
            "Preserve ids, classes, data-* markers, and the HTML skeleton structure.",
            "When HTML changes are required, patch only attributes or minimal wrapper nodes — never replace the whole tree.",
            "Do NOT include <script> tags — runtime is injected by the host application after generation.",
        ]
    )
