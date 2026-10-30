"""
Application Configuration.
Manages environment variables, Gemini AI settings, and security toggles.
"""
import os
from pathlib import Path

# Automatically attempt to load .env from backend directory and project root
try:
    from dotenv import load_dotenv
    base_dir = Path(__file__).resolve().parent.parent
    load_dotenv(base_dir / ".env")
    load_dotenv(base_dir.parent / ".env")
except Exception:
    pass

PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "127.0.0.1")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Gemini AI Settings (Official google-genai SDK)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
AI_ENABLED = os.getenv("AI_ENABLED", "true").lower() == "true"

# Security & Sandboxing (Safe Code Execution)
# Subprocess execution alone does not provide process and filesystem isolation.
# Untrusted arbitrary execution is disabled by default unless explicitly allowed.
ALLOW_UNTRUSTED_EXECUTION = os.getenv("ALLOW_UNTRUSTED_EXECUTION", "false").lower() == "true"
