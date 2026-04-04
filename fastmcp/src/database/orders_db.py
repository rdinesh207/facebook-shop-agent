"""
Database operations for the ``orders`` and ``order_items`` tables.
"""
from __future__ import annotations

from typing import Any

from src.database.insforge_client import get_client


def upsert_order(
    fb_order_id: str,
    page_id: str,
    status: str,
    buyer_name: str = "",
    buyer_email: str = "",
) -> dict[str, Any]:
    """
    Insert or update an order record.

    Returns the upserted row.
    """
    client = get_client()
    result = (
        client.table("orders")
        .upsert(
            {
                "fb_order_id": fb_order_id,
                "page_id": page_id,
                "status": status,
                "buyer_name": buyer_name,
                "buyer_email": buyer_email,
            },
            on_conflict="fb_order_id",
        )
        .execute()
    )
    return result.data[0] if result.data else {}


def upsert_order_items(
    order_db_id: str,
    items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Replace all order items for a given order (delete + insert).

    Args:
        order_db_id: UUID primary key from the ``orders`` table.
        items:       List of dicts with keys:
                     ``fb_product_id``, ``quantity``, ``price_per_unit``, ``currency``.

    Returns:
        List of inserted order_item rows.
    """
    client = get_client()
    client.table("order_items").delete().eq("order_id", order_db_id).execute()

    if not items:
        return []

    rows = [
        {
            "order_id": order_db_id,
            "fb_product_id": item.get("fb_product_id", ""),
            "quantity": item.get("quantity", 1),
            "price_per_unit": item.get("price_per_unit", 0.0),
            "currency": item.get("currency", "USD").upper(),
        }
        for item in items
    ]
    result = client.table("order_items").insert(rows).execute()
    return result.data or []


def sync_order(order: dict[str, Any]) -> dict[str, Any]:
    """
    Convenience helper: upsert an order and its items atomically.

    Args:
        order: Dict returned by ``src.facebook.orders.get_order`` or
               an element of ``list_orders`` — must include ``items`` key.

    Returns:
        The upserted order row.
    """
    row = upsert_order(
        fb_order_id=order["fb_order_id"],
        page_id=order["page_id"],
        status=order["status"],
        buyer_name=order.get("buyer_name", ""),
        buyer_email=order.get("buyer_email", ""),
    )
    if row.get("id") and order.get("items"):
        upsert_order_items(row["id"], order["items"])
    return row


def list_orders_by_status(status: str) -> list[dict[str, Any]]:
    """Return all orders with a specific status."""
    client = get_client()
    result = (
        client.table("orders")
        .select("*, order_items(*)")
        .eq("status", status.upper())
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []


def get_orders_for_product(fb_product_id: str) -> list[dict[str, Any]]:
    """
    Return all orders that contain a specific product.
    Uses a join through order_items.
    """
    client = get_client()
    result = (
        client.table("order_items")
        .select("*, orders(*)")
        .eq("fb_product_id", fb_product_id)
        .execute()
    )
    return result.data or []
