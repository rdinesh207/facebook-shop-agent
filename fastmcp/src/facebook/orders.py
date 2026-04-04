"""
Order and sale-status operations via the Facebook Commerce Orders API.

Requires the page access token to have the ``commerce`` permission.
"""
from __future__ import annotations

from typing import Any

import httpx

from src import config


# Facebook Graph API base URL
_GRAPH_BASE = "https://graph.facebook.com/v25.0"


def _graph_get(path: str, params: dict | None = None) -> dict[str, Any]:
    """Execute a GET request against the Graph API."""
    url = f"{_GRAPH_BASE}/{path}"
    p = {"access_token": config.FACEBOOK_ACCESS_TOKEN, **(params or {})}
    response = httpx.get(url, params=p, timeout=30)
    response.raise_for_status()
    return response.json()


def list_orders(
    page_id: str | None = None,
    state: str = "ALL",
    limit: int = 25,
) -> list[dict[str, Any]]:
    """
    Fetch orders from a Facebook Commerce Page.

    Args:
        page_id: Facebook Page ID. Defaults to FACEBOOK_PAGE_ID from config.
        state:   Filter by order state: "ALL" | "CREATED" | "IN_PROGRESS" |
                 "COMPLETED" | "CANCELLED".
        limit:   Max orders to return.

    Returns:
        List of order dicts.
    """
    pid = page_id or config.FACEBOOK_PAGE_ID
    data = _graph_get(
        f"{pid}/commerce_orders",
        params={
            "state": state,
            "limit": limit,
            "fields": "id,order_status,created,last_updated,buyer_details,channel",
        },
    )

    orders = []
    for raw in data.get("data", []):
        buyer = raw.get("buyer_details", {})
        orders.append({
            "fb_order_id": raw.get("id", ""),
            "page_id": pid,
            "status": raw.get("order_status", {}).get("state", "UNKNOWN"),
            "buyer_name": buyer.get("name", ""),
            "buyer_email": buyer.get("email", ""),
            "created_at": raw.get("created", ""),
            "updated_at": raw.get("last_updated", ""),
            "items": [],
        })

    # Fetch line items for each order
    for order in orders:
        order["items"] = _get_order_items(order["fb_order_id"])

    return orders


def get_order(order_id: str) -> dict[str, Any]:
    """
    Fetch a single order with its line items.

    Args:
        order_id: Facebook order ID.

    Returns:
        Order dict including ``items`` list.
    """
    raw = _graph_get(
        order_id,
        params={
            "fields": "id,order_status,created,last_updated,buyer_details,channel"
        },
    )
    buyer = raw.get("buyer_details", {})
    page_id = config.FACEBOOK_PAGE_ID

    return {
        "fb_order_id": raw.get("id", ""),
        "page_id": page_id,
        "status": raw.get("order_status", {}).get("state", "UNKNOWN"),
        "buyer_name": buyer.get("name", ""),
        "buyer_email": buyer.get("email", ""),
        "created_at": raw.get("created", ""),
        "updated_at": raw.get("last_updated", ""),
        "items": _get_order_items(raw.get("id", "")),
    }


def _get_order_items(order_id: str) -> list[dict[str, Any]]:
    """Return the line items for a given order ID."""
    data = _graph_get(
        f"{order_id}/items",
        params={"fields": "id,retailer_id,quantity,price_per_unit"},
    )

    items = []
    for item in data.get("data", []):
        price_info = item.get("price_per_unit", {})
        items.append({
            "fb_product_id": item.get("retailer_id", item.get("id", "")),
            "quantity": item.get("quantity", 1),
            "price_per_unit": float(price_info.get("amount", 0)),
            "currency": price_info.get("currency", "USD"),
        })

    return items


def is_product_sold(fb_product_id: str, page_id: str | None = None) -> dict[str, Any]:
    """
    Check whether a specific product has ever been purchased.

    Scans recent COMPLETED orders for the given product ID.

    Args:
        fb_product_id: Facebook ProductItem ID or retailer SKU.
        page_id:       Facebook Page ID (defaults to config value).

    Returns:
        Dict with ``is_sold`` (bool), ``order_count`` (int), and
        ``orders`` (list of matching order summaries).
    """
    completed_orders = list_orders(page_id=page_id, state="COMPLETED", limit=100)

    matching: list[dict[str, Any]] = []
    for order in completed_orders:
        for item in order.get("items", []):
            if item["fb_product_id"] == fb_product_id:
                matching.append({
                    "fb_order_id": order["fb_order_id"],
                    "status": order["status"],
                    "quantity": item["quantity"],
                    "price_per_unit": item["price_per_unit"],
                    "currency": item["currency"],
                })
                break

    return {
        "fb_product_id": fb_product_id,
        "is_sold": len(matching) > 0,
        "order_count": len(matching),
        "orders": matching,
    }
