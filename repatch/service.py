from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable, Iterable, List

SUPPORTED_SCOPES = {"functions", "display", "colors", "shapes", "orientation"}
NUM_SUGGESTIONS = 3
MAX_ERROR_PREVIEW_LENGTH = 120


@dataclass(frozen=True)
class PatchSuggestion:
    keep: List[str]
    change: List[str]
    patched_fragment: str


class RepatchService:
    def __init__(self, model: str, completion_fn: Callable | None = None) -> None:
        self.model = model
        self._completion_fn = completion_fn

    def generate_patch_suggestions(
        self,
        fragment: str,
        scopes: Iterable[str],
        temperature: float = 0.6,
    ) -> List[PatchSuggestion]:
        normalized_scopes = self._normalize_scopes(scopes)
        completion_fn = self._completion_fn or self._default_completion

        response = completion_fn(
            model=self.model,
            temperature=temperature,
            n=NUM_SUGGESTIONS,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You generate frontend patch suggestions for selected snippets. "
                        "Return valid JSON with this shape: "
                        '{"keep": [...], "change": [...], "patched_fragment": "..."}'
                    ),
                },
                {
                    "role": "user",
                    "content": self._build_user_prompt(fragment, normalized_scopes),
                },
            ],
        )

        suggestions = [self._parse_choice(choice) for choice in response.choices]
        if len(suggestions) != NUM_SUGGESTIONS:
            raise ValueError(
                f"Expected {NUM_SUGGESTIONS} suggestions but received {len(suggestions)}."
            )
        return suggestions

    def _normalize_scopes(self, scopes: Iterable[str]) -> List[str]:
        normalized = [scope.strip().lower() for scope in scopes if scope and scope.strip()]
        if not normalized:
            raise ValueError("At least one scope must be provided.")
        invalid = sorted(set(normalized) - SUPPORTED_SCOPES)
        if invalid:
            raise ValueError(f"Unsupported scopes: {', '.join(invalid)}")
        return sorted(set(normalized))

    @staticmethod
    def _build_user_prompt(fragment: str, scopes: List[str]) -> str:
        scopes_text = ", ".join(scopes)
        return (
            f"Selected scopes: {scopes_text}\n\n"
            "For the selected HTML/CSS/JS fragment, return what should stay (keep), "
            "what should be changed (change), and full patched fragment.\n"
            "The output must be JSON only.\n\n"
            f"Fragment:\n{fragment}"
        )

    @staticmethod
    def _parse_choice(choice: object) -> PatchSuggestion:
        content = RepatchService._choice_content(choice)
        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid JSON in LLM suggestion: {content[:MAX_ERROR_PREVIEW_LENGTH]}"
            ) from exc
        return PatchSuggestion(
            keep=list(payload.get("keep", [])),
            change=list(payload.get("change", [])),
            patched_fragment=str(payload.get("patched_fragment", "")),
        )

    @staticmethod
    def _choice_content(choice: object) -> str:
        if isinstance(choice, dict):
            return choice["message"]["content"]
        return choice.message.content

    @staticmethod
    def _default_completion(**kwargs):
        """Lazily import litellm completion to avoid hard dependency at import time."""
        from litellm import completion

        return completion(**kwargs)
