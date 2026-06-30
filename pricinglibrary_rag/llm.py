from __future__ import annotations

import json
import urllib.error
import urllib.request
from abc import ABC, abstractmethod


class LocalLLM(ABC):
    """Abstract writer. Every backend takes the structured prompt and returns
    prose. It is ONLY a pedagogical writer — it never computes anything; the
    numbers come from the deterministic calculators and are guarded after
    generation (see validation.validate_generated_exercise)."""

    name: str

    @abstractmethod
    def generate(self, prompt: str, *, max_tokens: int = 2200) -> str:
        raise NotImplementedError


# Spec-facing alias: the abstract base is the same object under a clearer name.
BaseLLM = LocalLLM


class TemplateLLM(LocalLLM):
    """Deterministic fallback.

    It does not pretend to be a full LLM. It returns the prompt payload section
    that the generators already structure from retrieved sources.
    """

    name = "template"

    def generate(self, prompt: str, *, max_tokens: int = 2200) -> str:
        marker = "[TEMPLATE_OUTPUT]"
        if marker in prompt:
            return prompt.split(marker, 1)[1].strip()
        return prompt[: max_tokens * 4].strip()


class OpenAIChatLLM(LocalLLM):
    def __init__(
        self,
        *,
        api_key: str | None,
        model: str = "gpt-4o-mini",
        base_url: str | None = None,
        timeout_seconds: float = 90,
        max_retries: int = 1,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.name = f"openai:{model}"

    def generate(self, prompt: str, *, max_tokens: int = 2200) -> str:
        if not self.api_key:
            raise RuntimeError(
                "OpenAI API key missing. Set TPL_OPENAI_API_KEY or OPENAI_API_KEY."
            )
        try:
            from openai import OpenAI
        except Exception as exc:
            raise RuntimeError("The openai package is not installed.") from exc

        client_kwargs = {
            "api_key": self.api_key,
            "timeout": self.timeout_seconds,
            "max_retries": self.max_retries,
        }
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
        client = OpenAI(**client_kwargs)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You create rigorous, practice-first market finance "
                        "learning material grounded in retrieved source excerpts."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.35,
            max_tokens=max_tokens,
        )
        message = response.choices[0].message.content
        return (message or "").strip()


# Spec-facing alias.
OpenAILLM = OpenAIChatLLM


class OllamaLLM(LocalLLM):
    def __init__(self, url: str, model: str) -> None:
        self.url = url.rstrip("/")
        self.model = model
        self.name = f"ollama:{model}"

    def generate(self, prompt: str, *, max_tokens: int = 2200) -> str:
        payload = json.dumps(
            {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.35,
                },
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            f"{self.url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return str(data.get("response", "")).strip()
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Ollama generation failed: {exc}") from exc


class TransformersLLM(LocalLLM):
    def __init__(self, model_path: str) -> None:
        try:
            from transformers import pipeline  # type: ignore
        except Exception as exc:
            raise RuntimeError("transformers is not installed") from exc
        self.name = f"transformers:{model_path}"
        self._pipe = pipeline(
            "text-generation",
            model=model_path,
            tokenizer=model_path,
            device_map="auto",
        )

    def generate(self, prompt: str, *, max_tokens: int = 2200) -> str:
        output = self._pipe(
            prompt,
            max_new_tokens=max_tokens,
            do_sample=True,
            temperature=0.35,
            return_full_text=False,
        )
        if isinstance(output, list) and output:
            return str(output[0].get("generated_text", "")).strip()
        return ""


def build_llm(
    provider: str,
    *,
    openai_api_key: str | None = None,
    openai_model: str = "gpt-4o-mini",
    openai_base_url: str | None = None,
    openai_timeout_seconds: float = 90,
    openai_max_retries: int = 1,
    ollama_url: str,
    ollama_model: str,
    transformers_model_path: str | None,
) -> LocalLLM:
    if provider == "template":
        return TemplateLLM()
    if provider == "openai":
        return OpenAIChatLLM(
            api_key=openai_api_key,
            model=openai_model,
            base_url=openai_base_url,
            timeout_seconds=openai_timeout_seconds,
            max_retries=openai_max_retries,
        )
    if provider == "ollama":
        return OllamaLLM(ollama_url, ollama_model)
    if provider == "transformers":
        if not transformers_model_path:
            raise RuntimeError("TPL_TRANSFORMERS_MODEL_PATH must point to a local model.")
        return TransformersLLM(transformers_model_path)
    raise ValueError(f"Unknown local LLM provider: {provider}")
