"""
Database operations for the ``shops`` table.
"""
from __future__ import annotations

from typing import Any

from src.database.supabase_client import get_client


def upsert_shop(
    fb_catalog_id: str,
    fb_page_id: str,
    name: str,
    description: str = "",
) -> dict[str, Any]:
    """
    Insert or update a shop record.

    Returns the upserted row.
    """
    client = get_client()
    result = (
        client.table("shops")
        .upsert(
            {
                "fb_catalog_id": fb_catalog_id,
                "fb_page_id": fb_page_id,
                "name": name,
                "description": description,
            },
            on_conflict="fb_catalog_id",
        )
        .execute()
    )
    return result.data[0] if result.data else {}


def get_shop_by_catalog_id(fb_catalog_id: str) -> dict[str, Any] | None:
    """Return a shop row by its Facebook catalog ID, or None if not found."""
    client = get_client()
    result = (
        client.table("shops")
        .select("*")
        .eq("fb_catalog_id", fb_catalog_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def list_shops() -> list[dict[str, Any]]:
    """Return all shops stored in the database."""
    client = get_client()
    result = client.table("shops").select("*").order("created_at").execute()
    return result.data or []
