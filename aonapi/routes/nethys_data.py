# Routes pertaining to the Nethys data
from fastapi import Depends, APIRouter
from sqlmodel import Session, select

from datetime import datetime, timedelta
import requests
import logging

from aonapi.models import (
    Category,
    UUID_Group,
    DefaultNethysDataModel,
    NethysData,
    MODEL_MAP,
)
from aonapi import aon_serializers
from aonapi.utils import get_db
from aonapi.settings import search_url

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    """
    Returns all available categories.
    """
    categories = db.exec(select(Category)).all()
    return [{"id": cat.id, "name": cat.name} for cat in categories]


@router.get("/category/{category_id}/uuids")
def get_uuids(category_id: int, db: Session = Depends(get_db)):
    """
    Returns all UUIDs associated with a category.
    """
    uuid_groups = db.exec(
        select(UUID_Group).where(UUID_Group.category_id == category_id)
    ).all()
    return [{"uuid": group.uuid, "label": group.label} for group in uuid_groups]


FETCH_THRESHOLD_SECONDS = (
    7200  # Don't fetch data if it was fetched within the last 2 hours
)


@router.get("/fetch/{uuid}")
def get_data_by_uuid(uuid: str, db: Session = Depends(get_db)):
    """API endpoint to retrieve data by UUID. Declared route seperately to allow for programmatic access to fetch function."""
    return fetch_data_by_uuid(uuid, db)


def fetch_data_by_uuid(uuid: str, db: Session = Depends(get_db)):
    """
    Fetches data from Archives of Nethys for the given UUID.
    If the data is already 'cached' in the database (last fetched within the last 2 hours), it returns the existing data.
    """
    # Fetch the uuid group from the database
    uuid_group = db.exec(select(UUID_Group).where(UUID_Group.uuid == uuid)).first()
    if not uuid_group:
        return {"error": "UUID not found."}, 404

    # The name of the category for this UUID
    category_name = (
        db.exec(select(Category).where(Category.id == uuid_group.category_id))
        .first()
        .name
    )

    # The model for this category
    model = MODEL_MAP.get(category_name, DefaultNethysDataModel)

    # Fetch the data from the database
    data = db.exec(select(model).where(model.uuid_group_id == uuid_group.id)).all()

    # If the data isn't stale, return it
    now = datetime.now()
    if data and all(
        item.last_fetched > now - timedelta(seconds=FETCH_THRESHOLD_SECONDS)
        for item in data
    ):
        return data

    # If the data is missing or stale, fetch it from the API
    aon_data = fetch_data_from_aon(uuid)
    if not aon_data:
        return {"error": "Data not found."}, 404

    # Parse and store data
    parsed_data = store_fetched_data(uuid_group, model, category_name, aon_data, db)
    return parsed_data


def fetch_data_from_aon(uuid: str):
    """
    Fetches data from Archives of Nethys for the given UUID.
    """
    url = f"{search_url}/{uuid}.json"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()


def store_fetched_data(
    uuid_group: UUID_Group,
    model: NethysData,
    category_name: str,
    aon_data_list,
    db: Session,
):
    """
    Parses and stores the fetched data in the appropriate table.
    """

    serializer = aon_serializers.SERIALIZER_MAP.get(
        category_name, aon_serializers.default_nethys_data_serializer
    )

    logger.info(
        f"Storing data for UUID Group: {uuid_group}, Category: {category_name}, using serializer: {serializer}"
    )

    stored_entries = []
    failed_entries = 0

    # Get the initial count of entries in the database
    initial_count = (
        db.exec(select(model).where(model.uuid_group_id == uuid_group.id))
        .all()
        .__len__()
    )

    for aon_data in aon_data_list:
        try:
            new_entry = serializer(aon_data, uuid_group.id)
            db.add(new_entry)
            stored_entries.append(new_entry)
        except Exception as e:
            failed_entries += 1
            logger.error(
                f"Failed to serialize data with ID {aon_data['id'].split('-')[1]}: {e}"
            )

    db.commit()

    # Refresh the entries to get their IDs
    for entry in stored_entries:
        db.refresh(entry)

    # Get the final count of entries in the database
    final_count = (
        db.exec(select(model).where(model.uuid_group_id == uuid_group.id))
        .all()
        .__len__()
    )

    logger.info(
        f"Created {len(stored_entries)} new entries, {failed_entries} entries failed to serialize."
    )
    logger.info(
        f"Initial count of entries: {initial_count}, Final count of entries: {final_count}"
    )

    # Check for any entries in the database that weren't included in the fresh data
    fresh_data_ids = {aon_data["id"].split("-")[1] for aon_data in aon_data_list}
    db_data_ids = {
        entry.id
        for entry in db.exec(
            select(DefaultNethysDataModel).where(
                DefaultNethysDataModel.uuid_group_id == uuid_group.id
            )
        ).all()
    }

    missing_ids = db_data_ids - fresh_data_ids
    if missing_ids:
        logger.warning(
            f"Entries in the database not included in the fresh data: {missing_ids}"
        )

    return stored_entries
