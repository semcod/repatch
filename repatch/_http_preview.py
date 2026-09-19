"""Sanitize live-site HTML and inject a cross-origin isolation shim for previews."""

from __future__ import annotations

import re
from typing import Any

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


def _script_src_allowed_for_preview(src: str) -> bool:
    src_value = str(src or "").strip()
    if not src_value:
        return False
    if src_value.startswith(("http://", "https://", "//", "data:")):
        return False
    return src_value.lower().startswith("imported_projects/")


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

    sanitized_html = _SCRIPT_BLOCK_RE.sub(replace_script, str(html or ""))
    return sanitized_html, {"preview_scripts_removed": removed}


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
        return html[:insert_at] + "\n" + HTTP_PREVIEW_NETWORK_SHIM + html[insert_at:]
    return HTTP_PREVIEW_NETWORK_SHIM + "\n" + html


def prepare_http_preview_html(html: str) -> tuple[str, dict[str, Any]]:
    """Sanitize scripts and inject network isolation shim for preview iframes."""
    sanitized_html, meta = sanitize_http_preview_html(html)
    shimmed_html = inject_http_preview_shim(sanitized_html)
    meta["preview_shim_injected"] = _NEXU_PREVIEW_SHIM_MARKER in shimmed_html
    return shimmed_html, meta
