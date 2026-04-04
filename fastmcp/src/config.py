"""
Central configuration — loads all environment variables from .env
and exposes them as typed attributes. Raises early if required vars
are missing so the server fails fast with a clear message.
"""
import os
from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(
            f"Required environment variable '{name}' is not set. "
            "Copy .env.example to .env and fill in the values."
        )
    return value


# ── Facebook / Meta ────────────────────────────────────────────────────────────
FACEBOOK_ACCESS_TOKEN: str = _require("FACEBOOK_ACCESS_TOKEN")
FACEBOOK_APP_ID: str = _require("FACEBOOK_APP_ID")
FACEBOOK_APP_SECRET: str = _require("FACEBOOK_APP_SECRET")
FACEBOOK_PAGE_ID: str = os.getenv("FACEBOOK_PAGE_ID", "")  # optional at startup; required only for order tools
FACEBOOK_BUSINESS_ID: str = _require("FACEBOOK_BUSINESS_ID")
# Optional — can be created at runtime via create_shop tool
FACEBOOK_CATALOG_ID: str = os.getenv("FACEBOOK_CATALOG_ID", "")

# ── Supabase ───────────────────────────────────────────────────────────────────
SUPABASE_URL: str = _require("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY: str = _require("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_DB_PASSWORD: str = os.getenv("SUPABASE_DB_PASSWORD", "")

# ── OpenAI ─────────────────────────────────────────────────────────────────────
OPENAI_API_KEY: str = _require("OPENAI_API_KEY")

# ── FastMCP server ─────────────────────────────────────────────────────────────
MCP_HOST: str = os.getenv("MCP_HOST", "127.0.0.1")
MCP_PORT: int = int(os.getenv("MCP_PORT", "8000"))
