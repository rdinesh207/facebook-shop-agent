"""
Facebook Shop / Product Catalog operations via Meta Business SDK.

A Facebook Shop is backed by a Product Catalog in Meta's Commerce Platform.
Creating a catalog via the API is the programmatic equivalent of creating a shop.
"""
from __future__ import annotations

from typing import Any

from facebook_business.adobjects.business import Business
from facebook_business.adobjects.productcatalog import ProductCatalog

from src import config
from src.facebook.client import get_api


def create_catalog(name: str, description: str = "") -> dict[str, Any]:
    """
    Create a new product catalog (Facebook Shop) under the configured Business.

    Args:
        name:        Human-readable shop / catalog name.
        description: Optional description.

    Returns:
        Dict with ``fb_catalog_id``, ``name``, ``fb_page_id``.
    """
    get_api()

    business = Business(config.FACEBOOK_BUSINESS_ID)
    catalog = business.create_owned_product_catalog(
        fields=[
            ProductCatalog.Field.id,
            ProductCatalog.Field.name,
        ],
        params={
            "name": name,
            "da_display_settings": {"carousel_ad_show_price": True},
        },
    )

    return {
        "fb_catalog_id": catalog[ProductCatalog.Field.id],
        "name": catalog[ProductCatalog.Field.name],
        "fb_page_id": config.FACEBOOK_PAGE_ID,
        "description": description,
    }


def get_catalog_info(catalog_id: str) -> dict[str, Any]:
    """
    Fetch metadata for an existing product catalog.

    Args:
        catalog_id: Facebook catalog / shop ID.

    Returns:
        Dict with catalog metadata.
    """
    get_api()

    catalog = ProductCatalog(catalog_id).api_get(
        fields=[
            ProductCatalog.Field.id,
            ProductCatalog.Field.name,
            ProductCatalog.Field.product_count,
        ]
    )

    return {
        "fb_catalog_id": catalog[ProductCatalog.Field.id],
        "name": catalog[ProductCatalog.Field.name],
        "product_count": catalog.get(ProductCatalog.Field.product_count, 0),
    }
