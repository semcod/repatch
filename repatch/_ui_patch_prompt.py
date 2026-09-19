"""LLM UI patch prompt/contract construction."""

from __future__ import annotations

import json
import re

from .scope import normalize_focus_scope, scoped_html_fragment

_ALT_FILES = ("alt_a.html", "alt_b.html", "alt_c.html")
_VISUAL_PATCH_SCOPES = frozenset({"colors", "shapes", "display", "orientation", "keypad"})


def supports_llm_patch_scope(
    scope: str,
    project_kind: str,
    *,
    has_marks: bool = False,
) -> bool:
    """True when A-C options can be generated as a CSS patch instead of full HTML."""
    effective_scope = normalize_focus_scope(scope, project_kind)
    if has_marks and effective_scope == "functions":
        return False
    return effective_scope in _VISUAL_PATCH_SCOPES


def _compact_html(html: str, *, limit: int = 6000) -> str:
    text = re.sub(r"\s+", " ", str(html or "")).strip()
    if len(text) <= limit:
        return text
    head = text[: limit // 2]
    tail = text[-limit // 2 :]
    return head + "\n<!-- middle omitted for compact LLM patch prompt -->\n" + tail


def _patch_scope_rules(
    scope: str,
    *,
    keep_els: list[str] | None = None,
    delete_els: list[str] | None = None,
) -> list[str]:
    keep = list(keep_els or [])
    delete = list(delete_els or [])
    rules = [
        f"Focus only on #{scope}.",
        "Do not return HTML. Return CSS/xpatches only.",
        "This is an xpatch workflow: modify selected layers/fragments, never replace the page.",
        "Preserve DOM structure, ids, labels, workflows, and JavaScript behavior.",
        "No external assets, imports, urls, scripts, or markdown.",
    ]
    if scope == "functions":
        rules.extend(
            [
                "DELETE-marked elements must be removed or fully redesigned.",
                "KEEP-marked elements are mandatory and must stay visually usable.",
            ]
        )
    elif scope in _VISUAL_PATCH_SCOPES:
        rules.extend(
            [
                f"Apply #{scope} changes primarily to DELETE-marked elements.",
                "KEEP-marked elements are hard constraints — preserve their current CSS, "
                "text, DOM, and behavior.",
                "DELETE-marked elements mean CHANGE within the selected scope, "
                "not physical removal.",
                "Do not restyle unrelated controls outside marked fragments.",
            ]
        )
    else:
        rules.extend(
            [
                "KEEP elements are mandatory and must stay visually usable.",
                "DELETE elements are the primary redesign targets.",
            ]
        )
    if keep:
        rules.append(f"KEEP ids: {', '.join(keep[:16])}.")
    if delete:
        rules.append(f"DELETE ids: {', '.join(delete[:16])}.")
    return rules


def build_ui_patch_prompt(
    html: str,
    *,
    focus_scope: str,
    project_kind: str,
    option_variants: list[tuple[str, str, str]],
    user_goal: str = "",
    keep_els: list[str] | None = None,
    delete_els: list[str] | None = None,
    context_fragment: str | None = None,
) -> str:
    """Build a compact JSON-only prompt for scoped CSS A-C options."""
    scope = normalize_focus_scope(focus_scope, project_kind)
    if context_fragment:
        fragment = context_fragment
    else:
        fragment = scoped_html_fragment(html, scope, project_kind) or _compact_html(html)
    variants = [
        {"file": filename, "label": label, "direction": note}
        for filename, label, note in option_variants
        if filename in _ALT_FILES
    ]
    contract = {
        "task": "Generate scoped xpatch UI option patches for Nexu Cinema.",
        "output": "JSON only, no markdown fences, no prose.",
        "schema": {
            "variants": {
                "alt_a.html": {"label": "short label", "css": "CSS patch only"},
                "alt_b.html": {"label": "short label", "css": "CSS patch only"},
                "alt_c.html": {"label": "short label", "css": "CSS patch only"},
            }
        },
        "rules": _patch_scope_rules(scope, keep_els=keep_els, delete_els=delete_els),
        "project_kind": project_kind or "web",
        "user_goal": user_goal or "",
        "keep": keep_els or [],
        "delete": delete_els or [],
        "variants": variants,
    }
    return (
        "INTRACT UI PATCH CONTRACT\n"
        + json.dumps(contract, ensure_ascii=False, indent=2)
        + "\n\nCURRENT UI HTML/FRAGMENT\n"
        + fragment
        + "\n\nReturn the JSON object now."
    )
