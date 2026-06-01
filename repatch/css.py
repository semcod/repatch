"""CSS parsing and safety checks for patch workflows."""

from __future__ import annotations

import re

_RULE_RE = re.compile(r"(?P<selectors>[^{}]+)\{(?P<body>[^{}]+)\}", re.S)
_DECL_RE = re.compile(r"(?P<name>[-a-zA-Z]+)\s*:\s*(?P<value>[^;]+)")
_NEXU_SELECTOR_RE = re.compile(r"(?:\.|#)nexu-", re.I)


def _strip_css_comments(css: str) -> str:
    return re.sub(r"/\*[\s\S]*?\*/", "", str(css or ""))


def _selector_is_runtime_only(selector: str) -> bool:
    return bool(_NEXU_SELECTOR_RE.search(selector or ""))


def split_css_rules(css: str) -> list[str]:
    """Split CSS into top-level rule blocks (best-effort, no full parser)."""
    text = str(css or "")
    rules: list[str] = []
    depth = 0
    start = 0
    for index, char in enumerate(text):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                chunk = text[start : index + 1].strip()
                if chunk:
                    rules.append(chunk)
                start = index + 1
    tail = text[start:].strip()
    if tail and depth == 0:
        rules.append(tail)
    return rules


def validate_css_safety(css: str, *, source: str = "css") -> tuple[bool, list[str]]:
    """Reject CSS patterns that commonly break HTML/CSS patch previews."""
    errors: list[str] = []
    text = _strip_css_comments(css)
    if not text.strip():
        return True, []
    if re.search(r"@import\b|url\s*\(|expression\s*\(|javascript\s*:", text, re.I):
        errors.append(f"{source}: external or executable CSS is not allowed")

    for match in _RULE_RE.finditer(text):
        selectors = " ".join(match.group("selectors").split())
        body = match.group("body")
        if _selector_is_runtime_only(selectors):
            continue
        declarations = {
            decl.group("name").strip().lower(): decl.group("value").strip().lower()
            for decl in _DECL_RE.finditer(body)
        }
        position = declarations.get("position", "")
        if position in {"absolute", "fixed"}:
            errors.append(f"{source}: {selectors} uses position:{position}")
        for name, value in declarations.items():
            if name.startswith("margin") and re.match(r"-\d", value):
                errors.append(f"{source}: {selectors} uses negative {name}")
            if name == "transform" and ":hover" not in selectors:
                errors.append(f"{source}: {selectors} uses transform outside hover state")
            if name in {"top", "left", "right", "bottom"} and position in {"absolute", "fixed"}:
                errors.append(f"{source}: {selectors} uses manual {name} offset")
    return len(errors) == 0, errors
