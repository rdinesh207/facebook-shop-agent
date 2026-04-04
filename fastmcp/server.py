"""
Facebook Shop MCP Server
========================
Exposes Facebook Shop operations as MCP tools via FastMCP.

Run:
    python server.py                       # stdio (default, for Cursor / Claude)
    python server.py --transport streamable-http  # HTTP server mode
"""
from __future__ import annotations

from typing import Annotated, Any

from fastmcp import FastMCP

# Facebook layer
import src.facebook.shops as fb_shops
import src.facebook.products as fb_products
import src.facebook.orders as fb_orders

# Database layer
import src.database.shops_db as shops_db
import src.database.products_db as products_db
import src.database.orders_db as orders_db

mcp = FastMCP(
    name="facebook-shop-agent",
    instructions=(
        "You are a Facebook Shop assistant. "
        "Use the available tools to create shops, manage product listings, "
        "check whether products have been sold, and sync data with the database."
    ),
)


# ── Tool 1: create_shop ────────────────────────────────────────────────────────

@mcp.tool
def create_shop(
    name: Annotated[str, "Name of the Facebook Shop / product catalog"],
    description: Annotated[str, "Optional description of the shop"] = "",
) -> dict[str, Any]:
    """
    Create a new Facebook Shop (product catalog) under the configured Business
    account and save it to the database.

    Returns the catalog info including the Facebook catalog ID.
    """
    catalog = fb_shops.create_catalog(name=name, description=description)
    saved = shops_db.upsert_shop(
        fb_catalog_id=catalog["fb_catalog_id"],
        fb_page_id=catalog["fb_page_id"],
        name=catalog["name"],
        description=description,
    )
    return {**catalog, "db_id": saved.get("id")}


# ── Tool 2: get_shop_info ──────────────────────────────────────────────────────

@mcp.tool
def get_shop_info(
    catalog_id: Annotated[str, "Facebook catalog / shop ID"],
) -> dict[str, Any]:
    """
    Retrieve metadata for an existing Facebook Shop, including product count.
    Also checks for any local database record.
    """
    fb_info = fb_shops.get_catalog_info(catalog_id)
    db_record = shops_db.get_shop_by_catalog_id(catalog_id)
    return {**fb_info, "db_record": db_record}


# ── Tool 3: create_product_listing ────────────────────────────────────────────

@mcp.tool
def create_product_listing(
    catalog_id: Annotated[str, "Facebook catalog ID to add the product to"],
    name: Annotated[str, "Product title"],
    description: Annotated[str, "Product description"],
    price: Annotated[float, "Price in full currency units (e.g. 29.99 for $29.99)"],
    currency: Annotated[str, "ISO 4217 currency code, e.g. USD"] = "USD",
    image_url: Annotated[str, "Publicly accessible URL of the product image"] = "",
    product_url: Annotated[str, "URL of the product page"] = "",
    availability: Annotated[
        str,
        "One of: 'in stock', 'out of stock', 'preorder', 'available for order'",
    ] = "in stock",
    retailer_id: Annotated[
        str,
        "Your internal SKU/ID. Auto-generated from name if left blank.",
    ] = "",
) -> dict[str, Any]:
    """
    Create a new product listing inside a Facebook Shop catalog
    and persist it to the Supabase database.
    """
    product = fb_products.create_product(
        catalog_id=catalog_id,
        name=name,
        description=description,
        price=price,
        currency=currency,
        image_url=image_url,
        product_url=product_url,
        availability=availability,
        retailer_id=retailer_id or None,
    )
    saved = products_db.upsert_product(
        fb_product_id=product["fb_product_id"],
        catalog_id=catalog_id,
        name=name,
        description=description,
        price=price,
        currency=currency,
        availability=availability,
        image_url=image_url,
        product_url=product_url,
    )
    return {**product, "db_id": saved.get("id")}


# ── Tool 4: list_products ──────────────────────────────────────────────────────

@mcp.tool
def list_products(
    catalog_id: Annotated[str, "Facebook catalog ID"],
    limit: Annotated[int, "Maximum number of products to return (default 50)"] = 50,
    sync_to_db: Annotated[
        bool, "If true, upsert all fetched products into the database"
    ] = True,
) -> list[dict[str, Any]]:
    """
    List products in a Facebook Shop catalog.
    Optionally syncs the results to the Supabase database.
    """
    items = fb_products.list_products(catalog_id=catalog_id, limit=limit)

    if sync_to_db:
        for p in items:
            products_db.upsert_product(
                fb_product_id=p["fb_product_id"],
                catalog_id=catalog_id,
                name=p["name"],
                description=p.get("description", ""),
                price=p.get("price", 0.0),
                currency=p.get("currency", "USD"),
                availability=p.get("availability", ""),
                image_url=p.get("image_url", ""),
                product_url=p.get("product_url", ""),
            )

    return items


# ── Tool 5: get_product ────────────────────────────────────────────────────────

@mcp.tool
def get_product(
    product_id: Annotated[str, "Facebook ProductItem ID"],
) -> dict[str, Any]:
    """
    Fetch detailed information for a single product from Facebook.
    Also returns any local database record if it exists.
    """
    fb_data = fb_products.get_product(product_id)
    db_record = products_db.get_product_by_fb_id(product_id)
    return {**fb_data, "db_record": db_record}


# ── Tool 6: list_orders ────────────────────────────────────────────────────────

@mcp.tool
def list_orders(
    page_id: Annotated[
        str,
        "Facebook Page ID. Leave blank to use the configured default.",
    ] = "",
    state: Annotated[
        str,
        "Filter by order state: ALL | CREATED | IN_PROGRESS | COMPLETED | CANCELLED",
    ] = "ALL",
    limit: Annotated[int, "Maximum number of orders to return (default 25)"] = 25,
    sync_to_db: Annotated[
        bool, "If true, upsert all fetched orders and their items into the database"
    ] = True,
) -> list[dict[str, Any]]:
    """
    List orders from a Facebook Commerce Page.
    Optionally syncs orders and line items to the Supabase database.
    """
    orders = fb_orders.list_orders(
        page_id=page_id or None,
        state=state,
        limit=limit,
    )

    if sync_to_db:
        for order in orders:
            orders_db.sync_order(order)

    return orders


# ── Tool 7: get_order ──────────────────────────────────────────────────────────

@mcp.tool
def get_order(
    order_id: Annotated[str, "Facebook order ID"],
) -> dict[str, Any]:
    """
    Fetch a single Facebook order with all its line items.
    Syncs the order to the Supabase database.
    """
    order = fb_orders.get_order(order_id)
    orders_db.sync_order(order)
    return order


# ── Tool 8: is_product_sold ────────────────────────────────────────────────────

@mcp.tool
def is_product_sold(
    fb_product_id: Annotated[str, "Facebook ProductItem ID or retailer SKU"],
    page_id: Annotated[
        str,
        "Facebook Page ID. Leave blank to use the configured default.",
    ] = "",
    use_db_cache: Annotated[
        bool,
        "If true, check the local Supabase database first (faster). "
        "Falls back to live Facebook API if not found in DB.",
    ] = False,
) -> dict[str, Any]:
    """
    Check whether a specific product has been sold on Facebook.

    Returns is_sold (bool), order_count (int), and a list of matching orders.
    """
    if use_db_cache:
        sold = products_db.is_product_sold_in_db(fb_product_id)
        db_orders = orders_db.get_orders_for_product(fb_product_id)
        return {
            "fb_product_id": fb_product_id,
            "is_sold": sold,
            "order_count": len(db_orders),
            "orders": db_orders,
            "source": "database",
        }

    result = fb_orders.is_product_sold(
        fb_product_id=fb_product_id,
        page_id=page_id or None,
    )
    result["source"] = "facebook_api"
    return result


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    transport = "stdio"
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--transport" and i + 1 < len(sys.argv) - 1:
            transport = sys.argv[i + 2]

    mcp.run(transport=transport)
