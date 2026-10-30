"""
AI Provider Interface: Supports Google Gemini via official google-genai SDK,
with graceful fallback to Heuristic Expert Engine (Offline).
"""
import os
import time
from typing import Optional, Dict, Any, Tuple
from ..config import GEMINI_API_KEY, GEMINI_MODEL, AI_ENABLED

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class AIProvider:
    """Configurable AI provider integrating Google GenAI SDK (Gemini 2.5 Flash)."""

    def __init__(self):
        self.api_key = (os.getenv("GEMINI_API_KEY") or GEMINI_API_KEY).strip()
        self.model_name = (os.getenv("GEMINI_MODEL") or GEMINI_MODEL).strip() or "gemini-2.5-flash"
        self.ai_enabled = AI_ENABLED and bool(self.api_key) and GENAI_AVAILABLE
        self._client: Optional[Any] = None
        if self.ai_enabled:
            try:
                self._client = genai.Client(api_key=self.api_key)
            except Exception:
                self._client = None
                self.ai_enabled = False

    def is_configured(self) -> bool:
        """Returns True only if an active API key is set and GenAI SDK client is initialized."""
        return self.ai_enabled and self._client is not None

    def get_provider_name(self) -> str:
        """Reports the active AI provider and model description."""
        if self.is_configured():
            return f"Google Gemini ({self.model_name})"
        return "Heuristic Expert Engine (Offline)"

    def get_status_info(self) -> Dict[str, Any]:
        """Provides status metadata for frontend badges and diagnostics (never exposing secret values)."""
        return {
            "configured": self.is_configured(),
            "provider": self.get_provider_name(),
            "model": self.model_name if self.is_configured() else "Offline Heuristics",
            "has_api_key": bool(self.api_key),
            "sdk_available": GENAI_AVAILABLE
        }

    def query_model(
        self,
        prompt: str,
        system_prompt: str = ""
    ) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Calls Gemini 2.5 Flash using official google-genai SDK.
        Returns:
            (generated_text, telemetry_dict)
        """
        telemetry = {
            "provider": self.get_provider_name(),
            "model": self.model_name if self.is_configured() else "offline",
            "latency_ms": 0.0,
            "prompt_tokens": 0,
            "candidate_tokens": 0,
            "total_tokens": 0,
            "success": False,
            "error": None
        }

        if not self.is_configured():
            telemetry["error"] = "Gemini API key is not configured or AI is disabled."
            return None, telemetry

        t0 = time.perf_counter()
        try:
            full_contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=full_contents
            )
            telemetry["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            telemetry["success"] = True

            # Extract token usage if returned by SDK
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                usage = response.usage_metadata
                telemetry["prompt_tokens"] = getattr(usage, "prompt_token_count", 0) or 0
                telemetry["candidate_tokens"] = getattr(usage, "candidates_token_count", 0) or 0
                telemetry["total_tokens"] = getattr(usage, "total_token_count", 0) or 0

            return response.text, telemetry

        except Exception as e:
            telemetry["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            telemetry["error"] = f"Gemini API request failed: {type(e).__name__}"
            return None, telemetry

