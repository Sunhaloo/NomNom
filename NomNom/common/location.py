from pathlib import Path
import json

from django.conf import settings


def load_cities():
    """
    Return a sorted, de-duplicated list of city names.

    Cities are loaded from `orders/static/orders/cities.json` which is
    considered the single source of truth for the "main" cities in
    Mauritius used across checkout and signup flows.
    """

    path = Path(settings.BASE_DIR) / "orders/static/orders/cities.json"
    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as f:
            content = json.load(f)
    except Exception:
        return []

    cities = content.get("cities", [])
    return sorted(set(cities))
