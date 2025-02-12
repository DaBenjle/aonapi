# These are functions that interpret raw aon data and create model instances from it. They are used in the route handlers to fetch and store data from the aon api.
from aonapi.models import Ancestry, Class, DefaultNethysDataModel
from datetime import datetime


def parse_aon_languages(raw_language: str) -> list[str]:
    """Parses AoN language data into a list of strings."""
    languages = raw_language.split(", ")
    parsed_languages = [lang.split("]")[0].strip("[").strip() for lang in languages]
    return parsed_languages


def parse_ancestry_data(aon_data: dict, uuid_group_id: int) -> Ancestry:
    """Parses AoN data into an Ancestry model instance."""
    aon_hp = aon_data.get("hp_raw")
    cast_hp = int(aon_hp) if aon_hp else None

    aon_speed = aon_data.get("speed")
    cast_speed = aon_speed.get("max") if aon_speed else 0

    return Ancestry(
        id=int(aon_data["id"].split("-")[1]),  # Extract numeric ID
        uuid_group_id=uuid_group_id,
        last_fetched=datetime.now(),
        name=aon_data["name"],
        hp=cast_hp,
        size=aon_data.get("size", []),
        speed=cast_speed,
        ability_boost=aon_data.get("attribute", []),
        ability_flaw=aon_data.get("attribute_flaw"),
        language=parse_aon_languages(aon_data.get("language", [])),
        vision=aon_data.get("vision", "").lower(),
        rarity=aon_data.get("rarity").lower(),
    )


def parse_class_data(aon_data: dict, uuid_group_id: int) -> Class:
    """Parses AoN data into a Class model instance."""
    return Class(
        id=int(aon_data["id"].split("-")[1]),
        uuid_group_id=uuid_group_id,
        last_fetched=datetime.utcnow(),
        name=aon_data["name"],
        ability=aon_data.get("ability", []),
        hp=aon_data.get("hp", 0),
        tradition=aon_data.get("tradition"),
        attack_proficiency=aon_data.get("attack_proficiency", {}),
        defense_proficiency=aon_data.get("defense_proficiency", {}),
        fortitude_save_proficiency=aon_data.get("fortitude_save_proficiency"),
        reflex_save_proficiency=aon_data.get("reflex_save_proficiency"),
        will_save_proficiency=aon_data.get("will_save_proficiency"),
        perception_proficiency=aon_data.get("perception_proficiency"),
        skill_proficiency=aon_data.get("skill_proficiency", {}),
        rarity=aon_data.get("rarity"),
    )


def default_nethys_data_serializer(
    aon_data: dict, uuid_group_id: int
) -> DefaultNethysDataModel:
    """Default serializer for Nethys data."""
    return DefaultNethysDataModel(
        category_id=aon_data["id"],
        category_name=aon_data["category"],
        data=aon_data,
        uuid_group_id=uuid_group_id,
        last_fetched=datetime.now(),
    )


# This dictionary maps category names to the appropriate serializer function.
SERIALIZER_MAP = {
    "ancestry": parse_ancestry_data,
    "class": parse_class_data,
}
