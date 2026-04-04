"""
Database operations for the ``products`` table.
"""
from __future__ import annotations

from typing import Any

from src.database.supabase_client import get_client


def upsert_product(
    fb_product_id: str,
    catalog_id: str,
    name: str,
    description: str = "",
    price: float = 0.0,
    currency: str = "USD",
    availability: str = "in stock",
    image_url: str = "",
    product_url: str = "",
) -> dict[str, Any]:
    """
    Insert or update a product record.

    Returns the upserted row.
    """
    client = get_client()
    result = (
        client.table("products")
        .upsert(
            {
                "fb_product_id": fb_product_id,
                "catalog_id": catalog_id,
                "name": name,
                "description": description,
                "price": price,
                "currency": currency.upper(),
                "availability": availability,
                "image_url": image_url,
                "product_url": product_url,
            },
            on_conflict="fb_product_id",
        )
        .execute()
    )
    return result.data[0] if result.data else {}


def get_product_by_fb_id(fb_product_id: str) -> dict[str, Any] | None:
    """Return a product row by its Facebook product ID, or None."""
    client = get_client()
    result = (
        client.table("products")
        .select("*")
        .eq("fb_product_id", fb_product_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def list_products_by_catalog(catalog_id: str) -> list[dict[str, Any]]:
    """Return all products for a given catalog ID."""
    client = get_client()
    result = (
        client.table("products")
        .select("*")
        .eq("catalog_id", catalog_id)
        .order("created_at")
        .execute()
    )
    return result.data or []


def is_product_sold_in_db(fb_product_id: str) -> bool:
    """
    Check the order_items table to see whether the product has been purchased.
    Returns True if at least one completed order contains this product.
    """
    client = get_client()
    result = (
        client.table("order_items")
        .select("id, orders(status)")
        .eq("fb_product_id", fb_product_id)
        .execute()
    )

    for item in result.data or []:
        order = item.get("orders", {})
        if isinstance(order, dict) and order.get("status") == "COMPLETED":
            return True
        if isinstance(order, list):
            for o in order:
                if o.get("status") == "COMPLETED":
                    return True

    return False
