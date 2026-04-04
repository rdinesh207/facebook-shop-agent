"""
Initialises the Meta Business SDK API session.
All Facebook modules import `get_api()` from here.
"""
from facebook_business.api import FacebookAdsApi
from src import config


_api_instance: FacebookAdsApi | None = None


def get_api() -> FacebookAdsApi:
    """Return a singleton FacebookAdsApi, initialising it on first call."""
    global _api_instance
    if _api_instance is None:
        _api_instance = FacebookAdsApi.init(
            app_id=config.FACEBOOK_APP_ID,
            app_secret=config.FACEBOOK_APP_SECRET,
            access_token=config.FACEBOOK_ACCESS_TOKEN,
        )
    return _api_instance
