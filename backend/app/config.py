# -*- coding: utf-8 -*-
"""
myBIZcon Backend - Configuration Settings
=========================================
Centralized environment variable management and application settings.
All sensitive keys are loaded from environment variables or .env file.

Role: AGY (1st Coder) → Security Hardening - Step 15
Reviewed by: Antigravity (기술 검토자)
"""
import os

# ---------------------------------------------------------------------------
# Optional: load .env file if python-dotenv is installed
# ---------------------------------------------------------------------------
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed; environment variables must be set manually


class Settings:
    """Application-wide configuration settings loaded from environment variables."""

    # ── Core ────────────────────────────────────────────────────────────────
    PROJECT_NAME: str = "myBIZcon Backend"
    API_V1_STR: str = "/api/v1"

    # ── AI Engine ───────────────────────────────────────────────────────────
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_API_URL: str = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-1.5-flash:generateContent"
    )

    # ── Google Workspace OAuth ───────────────────────────────────────────────
    GOOGLE_CREDENTIALS_PATH: str = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
    GOOGLE_TOKEN_PATH: str = os.getenv("GOOGLE_TOKEN_PATH", "token.json")

    # ── Security / API Authentication ──────────────────────────────────────
    # Set SECRET_API_KEY in your environment or .env file before deploying.
    # Example (.env):   SECRET_API_KEY=your-strong-random-key-here
    SECRET_API_KEY: str = os.getenv("SECRET_API_KEY", "dev-insecure-key")

    # ── CORS Whitelist ──────────────────────────────────────────────────────
    # Comma-separated list of allowed origins.
    # Example (.env):   ALLOWED_ORIGINS=http://localhost:3000,https://mybizcon.app
    # Defaults to localhost-only in development.
    _allowed_origins_raw: str = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000"
    )
    ALLOWED_ORIGINS: list = [o.strip() for o in _allowed_origins_raw.split(",") if o.strip()]

    # ── File Path Security ──────────────────────────────────────────────────
    # Root directory that voice meeting recordings must reside in.
    # Prevents path-traversal attacks on the /voice/meeting endpoint.
    SAFE_RECORDINGS_ROOT: str = os.path.abspath(
        os.getenv("SAFE_RECORDINGS_ROOT", "./recordings")
    )


settings = Settings()
