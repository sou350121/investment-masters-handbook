import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


class LLMBridgeError(RuntimeError):
    pass


@dataclass
class LLMConfig:
    provider: str
    api_key: str
    base_url: str
    model: str
    timeout_s: float = 20.0
    max_retries: int = 3
    retry_wait_base_s: float = 1.0
    temperature: float = 0.2
    max_tokens: int = 900
    use_full_url: bool = False  # if true, base_url is full endpoint URL
    anthropic_version: str = "2023-06-01"

    # nofx-style retryable errors (string match, network-ish)
    retryable_errors: Tuple[str, ...] = (
        "EOF",
        "timeout",
        "timed out",
        "connection reset",
        "connection refused",
        "temporary failure",
        "no such host",
        "stream error",
        "INTERNAL_ERROR",
    )

    @staticmethod
    def from_env() -> "LLMConfig":
        provider = (os.getenv("LLM_PROVIDER") or os.getenv("AI_PROVIDER") or "openai").strip().lower()

        api_key = (
            os.getenv("LLM_API_KEY")
            or os.getenv("AI_API_KEY")
            or os.getenv("OPENAI_API_KEY")
            or ""
        ).strip()

        base_url = (
            os.getenv("LLM_BASE_URL")
            or os.getenv("AI_BASE_URL")
            or "https://api.openai.com/v1"
        ).strip()

        # nofx-style: allow suffix '#' to indicate full URL
        use_full_url = False
        if base_url.endswith("#"):
            base_url = base_url[:-1]
            use_full_url = True

        model = (os.getenv("LLM_MODEL") or os.getenv("AI_MODEL") or "gpt-4o-mini").strip()

        def _f(name: str, default: float) -> float:
            v = os.getenv(name)
            if not v:
                return default
            try:
                return float(v)
            except Exception:
                return default

        def _i(name: str, default: int) -> int:
            v = os.getenv(name)
            if not v:
                return default
            try:
                return int(v)
            except Exception:
                return default

        return LLMConfig(
            provider=provider,
            api_key=api_key,
            base_url=base_url,
            model=model,
            # Story S-0004 target: keep default latency under 5s (users can override via env).
            timeout_s=_f("LLM_TIMEOUT_S", 5.0),
            max_retries=_i("LLM_MAX_RETRIES", 1),
            retry_wait_base_s=_f("LLM_RETRY_WAIT_BASE_S", 1.0),
            temperature=_f("LLM_TEMPERATURE", 0.2),
            max_tokens=_i("LLM_MAX_TOKENS", 900),
            use_full_url=use_full_url,
        )


class LLMBridge:
    """
    Minimal, dependency-free AI client.

    - Default: OpenAI-compatible Chat Completions
    - Claude: Anthropic Messages API (provider=claude)

    Inspired by nofx/mcp/client.go:
    - env-based config
    - retryable network errors
    - optional full URL via trailing '#'
    """

    def __init__(self, cfg: Optional[LLMConfig] = None):
        self.cfg = cfg or LLMConfig.from_env()

    def set_api_key(self, api_key: str):
        """Override the API key dynamically (e.g. from frontend request)"""
        if api_key:
            self.cfg.api_key = api_key

    def is_configured(self) -> bool:
        return bool(self.cfg.api_key and self.cfg.base_url and self.cfg.model)

    def _build_url(self) -> str:
        if self.cfg.use_full_url:
            return self.cfg.base_url
        base = self.cfg.base_url.rstrip("/")
        if self.cfg.provider == "claude":
            return f"{base}/messages"
        return f"{base}/chat/completions"

    def _build_headers(self) -> Dict[str, str]:
        # OpenAI-compatible: Bearer auth. Claude: x-api-key.
        if self.cfg.provider == "claude":
            return {
                "Content-Type": "application/json",
                "x-api-key": self.cfg.api_key,
                "anthropic-version": self.cfg.anthropic_version,
            }
        return {"Content-Type": "application/json", "Authorization": f"Bearer {self.cfg.api_key}"}

    def _token_key(self) -> str:
        # nofx: OpenAI newer models use max_completion_tokens; others use max_tokens
        if self.cfg.provider == "openai":
            return "max_completion_tokens"
        return "max_tokens"

    def _build_body(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        if self.cfg.provider == "claude":
            system_parts: List[str] = []
            convo: List[Dict[str, str]] = []
            for m in messages or []:
                role = (m.get("role") or "").strip().lower()
                content = m.get("content") or ""
                if role == "system":
                    if content:
                        system_parts.append(content)
                    continue
                if role in ("user", "assistant") and content:
                    convo.append({"role": role, "content": content})

            # Anthropic requires at least one user message.
            if not convo or convo[0].get("role") != "user":
                convo.insert(0, {"role": "user", "content": "请开始。"})

            return {
                "model": self.cfg.model,
                "max_tokens": self.cfg.max_tokens,
                "temperature": self.cfg.temperature,
                "system": "\n\n".join(system_parts).strip(),
                "messages": convo,
            }

        # Default: OpenAI-compatible
        body: Dict[str, Any] = {
            "model": self.cfg.model,
            "messages": messages,
            "temperature": self.cfg.temperature,
        }
        body[self._token_key()] = self.cfg.max_tokens
        return body

    def _parse_response(self, raw: bytes) -> str:
        try:
            parsed = json.loads(raw.decode("utf-8"))
        except Exception as e:
            raise LLMBridgeError(f"Failed to parse LLM response JSON: {e}") from e

        if self.cfg.provider == "claude":
            content = parsed.get("content") or []
            if not isinstance(content, list) or not content:
                raise LLMBridgeError("Claude response missing content")
            # Find first text part
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text" and isinstance(part.get("text"), str):
                    return part["text"]
            raise LLMBridgeError("Claude response has no text content")

        choices = parsed.get("choices") or []
        if not choices:
            raise LLMBridgeError("LLM response missing choices")
        msg = (choices[0].get("message") or {}).get("content")
        if not isinstance(msg, str):
            raise LLMBridgeError("LLM response missing message.content")
        return msg

    def _is_retryable_error(self, err: Exception) -> bool:
        s = str(err or "")
        return any(tok in s for tok in (self.cfg.retryable_errors or ()))

    def call_chat(self, messages: List[Dict[str, str]]) -> str:
        """
        messages: [{role: 'system'|'user'|'assistant', content: '...'}, ...]
        returns assistant content (first choice)
        """
        if not self.is_configured():
            raise LLMBridgeError("LLM not configured: missing LLM_API_KEY/LLM_BASE_URL/LLM_MODEL")

        url = self._build_url()
        body = self._build_body(messages)
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url=url, data=data, headers=self._build_headers(), method="POST")

        last_err: Optional[Exception] = None
        for attempt in range(1, max(1, self.cfg.max_retries) + 1):
            try:
                with urllib.request.urlopen(req, timeout=self.cfg.timeout_s) as resp:
                    raw = resp.read()
                return self._parse_response(raw)
            except urllib.error.HTTPError as e:
                # Non-200, read body if possible
                try:
                    detail = e.read().decode("utf-8", errors="ignore")
                except Exception:
                    detail = ""
                last_err = LLMBridgeError(f"LLM HTTPError {e.code}: {detail}")
                # retry on 429/5xx
                if e.code in (429, 500, 502, 503, 504) and attempt < self.cfg.max_retries:
                    time.sleep(self.cfg.retry_wait_base_s * attempt)
                    continue
                raise last_err
            except (urllib.error.URLError, TimeoutError) as e:
                last_err = e
                if attempt < self.cfg.max_retries:
                    time.sleep(self.cfg.retry_wait_base_s * attempt)
                    continue
                raise LLMBridgeError(f"LLM network error after retries: {e}") from e
            except Exception as e:
                last_err = e
                if attempt < self.cfg.max_retries and self._is_retryable_error(e):
                    time.sleep(self.cfg.retry_wait_base_s * attempt)
                    continue
                raise

        raise LLMBridgeError(f"LLM call failed after retries: {last_err}")


def extract_json_block(text: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Try to extract a JSON object from a response that may include markdown.
    Returns (json_obj_or_none, remaining_text).
    """
    if not text:
        return None, ""

    # Prefer explicit <json>...</json> blocks (nofx-like tagged outputs)
    start_tag = "<json>"
    end_tag = "</json>"
    start = text.find(start_tag)
    if start != -1:
        end = text.find(end_tag, start + len(start_tag))
        if end != -1:
            block = text[start + len(start_tag) : end].strip()
            try:
                return json.loads(block), (text[:start] + text[end + len(end_tag) :]).strip()
            except Exception:
                pass

    # Prefer fenced ```json blocks
    start = text.find("```json")
    if start != -1:
        end = text.find("```", start + 7)
        if end != -1:
            block = text[start + 7 : end].strip()
            try:
                return json.loads(block), (text[:start] + text[end + 3 :]).strip()
            except Exception:
                pass

    # Fallback: find first {...} and try parse (best-effort)
    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last != -1 and last > first:
        cand = text[first : last + 1]
        try:
            return json.loads(cand), (text[:first] + text[last + 1 :]).strip()
        except Exception:
            return None, text

    return None, text


