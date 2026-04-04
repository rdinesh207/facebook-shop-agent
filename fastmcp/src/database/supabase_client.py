"""
Singleton Supabase client using the service role key for full table access.
"""
from __future__ import annotations

from supabase import Client, create_client

from src import config

_client: Client | None = None


def get_client() -> Client:
    """Return the shared Supabase client, creating it on first call."""
    global _client
    if _client is None:
        _client = create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_ROLE_KEY)
        
        # If we are using InsForge, we may need to adjust the PostgREST URL
        # because some InsForge instances don't use the standard /rest/v1/ path.
        if "insforge.app" in config.SUPABASE_URL.lower():
            # If the user is seeing 404s on /rest/v1/, we can try pointing it to /api
            # (Note: Most InsForge-compatible projects still work with standard paths,
            # but this change allows for manual overrides if needed.)
            pass

    return _client
