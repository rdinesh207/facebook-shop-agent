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
    return _client
