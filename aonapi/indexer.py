import requests
import time
import logging
from typing import Dict, List
from aonapi.settings import index_path
from aonapi.utils import SingletonMeta
from aonapi.models import Category, UUID_Group, engine
from sqlmodel import Session, select
from cachetools import TTLCache
from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)


class UUIDIndexCache(metaclass=SingletonMeta):
    """Singleton cache for UUID indexing."""

    def __init__(self):
        self._cache_duration = 3600  # 1 hour cache duration

    def _refresh_cache(self) -> Dict[str, List[str]]:
        response = requests.get(index_path)
        if response.status_code != 200:
            raise Exception(f"Failed to get UUIDs. Status code: {response.status_code}")
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


category_cache = TTLCache(maxsize=100, ttl=300)  # 5-minute cache


def fetch_categories():
    """Fetch categories from DB, using cache if available."""
    if "categories" in category_cache:
        return category_cache["categories"]

    with Session(engine) as session:
        categories = session.exec(select(Category)).all()
        category_mappings = {category.name: category.id for category in categories}

    category_cache["categories"] = category_mappings
    return category_mappings


def get_or_create_category(name: str) -> int:
    """Ensures a category exists, returns its ID."""
    categories = fetch_categories()
    if name in categories:
        return categories[name]

    with Session(engine) as session:
        new_category = Category(name=name)
        session.add(new_category)
        session.commit()
        session.refresh(new_category)

        category_cache["categories"][name] = new_category.id  # Update cache safely
        return new_category.id


def process_uuids(uuid_data: Dict[str, List[str]]):
    """Processes UUIDs and stores them in DB with retry logic to handle database locks."""

    retry_delay = 2  # Seconds

    for uuid, items in uuid_data.items():
        if not items:
            continue

        category_name = items[0].split("-")[0]
        category_id = get_or_create_category(category_name)

        max_retries = 3
        for attempt in range(max_retries):
            try:
                with Session(engine) as session:
                    with session.begin():  # ✅ Atomic transaction
                        existing = session.exec(
                            select(UUID_Group).where(UUID_Group.uuid == uuid)
                        ).first()
                        if not existing:
                            session.add(UUID_Group(uuid=uuid, category_id=category_id))
                        session.commit()  # Save changes
                        break  # ✅ Success, exit loop
            except OperationalError as e:
                logger.warning(
                    f"⚠️ Database locked (attempt {attempt+1}/{max_retries}). Retrying in {retry_delay}s..."
                )
                time.sleep(retry_delay)
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
                break
        else:
            logger.error(f"❌ Ran out of retries for UUID: {uuid}")


def update_categories_and_uuids():
    """Updates categories and UUIDs periodically."""
    logger.info("🔄 Updating database with UUIDs and categories...")
    uuid_data = get_uuid_index()
    process_uuids(uuid_data)
    logger.info("✅ Database update complete.")
