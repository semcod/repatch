"""Parse LLM UI patch JSON responses."""

from __future__ import annotations

import json
import re
from typing import Any


def _strip_json_fence(text: str) -> str:
    raw = str(text or "").strip()
    fence = re.search(r"```(?:json|JSON)?\s*([\s\S]*?)```", raw)
    if fence:
        return fence.group(1).strip()
    return raw


def parse_ui_patch_response(text: str) -> dict[str, Any]:
    """Parse JSON object from an LLM patch response."""
    raw = _strip_json_fence(text)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("LLM patch response did not contain a JSON object") from None
        data = json.loads(raw[start : end + 1])
    if not isinstance(data, dict):
        raise ValueError("LLM patch response root must be an object")
    variants = data.get("variants")
    if not isinstance(variants, dict):
        raise ValueError("LLM patch response must contain variants object")
    return data
