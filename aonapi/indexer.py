import requests
from typing import Dict, List
from aonapi.settings import index_path
from aonapi.utils import SingletonMeta
from aonapi.models import Category, UUID_Group, engine
from sqlmodel import Session, select
from cachetools import TTLCache


class UUIDIndexCache(metaclass=SingletonMeta):
    """
    Creates a singleton cache for the UUID index.

    The UUID index is a JSON object that maps UUIDs to items.
    For example {"6ab...": ["action1", "action2"], "7cd...": ["action3", "action4"], "8ef...": ["ancestry1", "ancestry2"]}.
    """

    def __init__(self):
        self._cache_duration = 3600  # Cache duration in seconds (1 hour)

    def _refresh_cache(self) -> Dict[str, List[str]]:
        response = requests.get(index_path)
        if response.status_code != 200:
            raise Exception(
                f"Failed to get UUIDs from index. Status code: {response.status_code}"
            )
        return response.json()

    def get_uuid_index(self) -> Dict[str, List[str]]:
        return SingletonMeta.get_cached_value(self, self._refresh_cache)

    def invalidate_cache(self):
        SingletonMeta.invalidate_cache(self)


def get_uuid_index():
    cache = UUIDIndexCache()
    return cache.get_uuid_index()


def invalidate_uuid_index_cache():
    cache = UUIDIndexCache()
    cache.invalidate_cache()


def process_uuids(uuid_data: Dict[str, List[str]]):
    """
    Processes UUID mappings and stores them in the database.
    Expected input:
    {
        "uuid1": ["feat-123", "feat-456"],
        "uuid2": ["ancestry-789", "ancestry-101"]
    }
    """
    with Session(engine) as session:
        for uuid, items in uuid_data.items():
            # Extract the category from the first item (e.g., "feat-123" → "feat")
            category_name = items[0].split("-")[0] if items else "unknown"
            category_id = get_or_create_category(category_name)

            # Check if UUID already exists
            existing = session.exec(
                select(UUID_Group).where(UUID_Group.uuid == uuid)
            ).first()
            if not existing:
                session.add(UUID_Group(uuid=uuid, category_id=category_id))

        session.commit()  # Save changes


category_cache = TTLCache(maxsize=100, ttl=300)  # Cache duration in seconds (5 minutes)


def fetch_categories():
    """Fetch the categories from the cache (or update the cache if it's empty)."""

    if "categories" in category_cache:
        return category_cache["categories"]

    with Session(engine) as session:
        categories = session.exec(select(Category)).all()
        category_mappings = {category.name: category.id for category in categories}

    category_cache["categories"] = category_mappings
    return category_mappings


def get_or_create_category(name: str) -> int:
    categories = fetch_categories()
    if name in categories:
        return categories[name]

    with Session(engine) as session:
        new_category = Category(name=name)
        session.add(new_category)
        session.commit()
        session.refresh(new_category)  # Refresh the object to get the ID

        category_cache["categories"][
            name
        ] = new_category.id  # Update the cache rather than invalidating it
        return new_category.id


def update_categories_and_uuids():
    """
    Periodically update the categories and UUIDs.
    """
    print("Updating database with UUIDs and categories...")  # TODO Logging
    uuid_data = get_uuid_index()

    # Process UUIDs
    process_uuids(uuid_data)
    print("Database updated with UUIDs and categories.")  # TODO Logging
