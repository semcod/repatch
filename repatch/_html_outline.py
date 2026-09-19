"""Build a compact HTML skeleton from imported web pages."""

from __future__ import annotations

import re
from html.parser import HTMLParser
from typing import Any

OUTLINE_TEXT_PLACEHOLDER = "…"


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
    comment_free_html = re.sub(r"<!--[\s\S]*?-->", "", str(html or ""))
    parser = _OutlineParser()
    parser.feed(comment_free_html)
    parser.close()
    outline = "\n".join(parser.parts).strip()
    if not outline.lower().startswith("<!doctype"):
        outline = f"<!DOCTYPE html>\n{outline}"
    outline_stats = {"outline_node_count": parser.node_count, "outline_bytes": len(outline.encode("utf-8"))}
    return outline, outline_stats
