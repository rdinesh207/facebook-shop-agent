"""
Product listing operations within a Facebook Product Catalog.
"""
from __future__ import annotations

from typing import Any

from facebook_business.adobjects.productcatalog import ProductCatalog
from facebook_business.adobjects.productitem import ProductItem

from src import config
from src.facebook.client import get_api


def create_product(
    catalog_id: str,
    name: str,
    description: str,
    price: float,
    currency: str,
    image_url: str,
    product_url: str,
    availability: str = "in stock",
    retailer_id: str | None = None,
) -> dict[str, Any]:
    """
    Create a new product listing inside a catalog.

    Args:
        catalog_id:   Facebook catalog (shop) ID.
        name:         Product title.
        description:  Product description.
        price:        Price in the smallest currency unit (e.g. cents for USD).
                      Pass the full dollar amount — this function converts to cents.
        currency:     ISO 4217 currency code, e.g. "USD".
        image_url:    Publicly accessible product image URL.
        product_url:  Link to the product page.
        availability: "in stock" | "out of stock" | "preorder" | "available for order".
        retailer_id:  Your internal SKU/ID. Auto-generated from name if omitted.

    Returns:
        Dict with ``fb_product_id`` and core product fields.
    """
    get_api()

    # Facebook expects price in cents (integer)
    price_cents = int(round(price * 100))

    catalog = ProductCatalog(catalog_id)
    product = catalog.create_product(
        fields=[ProductItem.Field.id, ProductItem.Field.name],
        params={
            "retailer_id": retailer_id or name.lower().replace(" ", "_"),
            "name": name,
            "description": description,
            "price": price_cents,
            "currency": currency.upper(),
            "image_url": image_url,
            "url": product_url,
            "availability": availability,
            "condition": "new",
        },
    )

    return {
        "fb_product_id": product[ProductItem.Field.id],
        "catalog_id": catalog_id,
        "name": name,
        "description": description,
        "price": price,
        "currency": currency.upper(),
        "availability": availability,
        "image_url": image_url,
        "product_url": product_url,
    }


def list_products(catalog_id: str, limit: int = 50) -> list[dict[str, Any]]:
    """
    List products in a catalog.

    Args:
        catalog_id: Facebook catalog ID.
        limit:      Maximum number of products to return (default 50).

    Returns:
        List of product dicts.
    """
    get_api()

    catalog = ProductCatalog(catalog_id)
    items = catalog.get_products(
        fields=[
            ProductItem.Field.id,
            ProductItem.Field.name,
            ProductItem.Field.description,
            ProductItem.Field.price,
            ProductItem.Field.currency,
            ProductItem.Field.availability,
            ProductItem.Field.image_url,
            ProductItem.Field.url,
        ],
        params={"limit": limit},
    )

    results = []
    for item in items:
        results.append({
            "fb_product_id": item.get(ProductItem.Field.id, ""),
            "catalog_id": catalog_id,
            "name": item.get(ProductItem.Field.name, ""),
            "description": item.get(ProductItem.Field.description, ""),
            "price": item.get(ProductItem.Field.price, 0) / 100,
            "currency": item.get(ProductItem.Field.currency, "USD"),
            "availability": item.get(ProductItem.Field.availability, ""),
            "image_url": item.get(ProductItem.Field.image_url, ""),
            "product_url": item.get(ProductItem.Field.url, ""),
        })

    return results


def get_product(product_id: str) -> dict[str, Any]:
    """
    Fetch a single product by its Facebook product ID.

    Args:
        product_id: Facebook ProductItem ID.

    Returns:
        Product dict.
    """
    get_api()

    item = ProductItem(product_id).api_get(
        fields=[
            ProductItem.Field.id,
            ProductItem.Field.name,
            ProductItem.Field.description,
            ProductItem.Field.price,
            ProductItem.Field.currency,
            ProductItem.Field.availability,
            ProductItem.Field.image_url,
            ProductItem.Field.url,
        ]
    )

    return {
        "fb_product_id": item.get(ProductItem.Field.id, ""),
        "name": item.get(ProductItem.Field.name, ""),
        "description": item.get(ProductItem.Field.description, ""),
        "price": item.get(ProductItem.Field.price, 0) / 100,
        "currency": item.get(ProductItem.Field.currency, "USD"),
        "availability": item.get(ProductItem.Field.availability, ""),
        "image_url": item.get(ProductItem.Field.image_url, ""),
        "product_url": item.get(ProductItem.Field.url, ""),
    }
