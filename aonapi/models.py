from sqlmodel import Field, SQLModel, create_engine, PickleType, Column
from typing import List, Dict, Any
from aonapi import enums
from aonapi.settings import database_url
from datetime import datetime


class NethysData(SQLModel):
    """
    Base model for all data fetched rom Archives of Nethys.
    Stores common metadata like UUID and timestamp.
    """

    # What uuid_group this item was registered under.
    uuid_group_id: int | None = Field(foreign_key="uuid_group.id")
    # The time the data was last updated from the aon api.
    last_fetched: datetime


class Category(SQLModel, table=True):
    """
    Represents a category of items, such as "ancestry", "class", or "action".

    When we create an item for a category, we will attempt to put it in the correct table.
    For example, if we have an item with the category "ancestry", we will put it in the "ancestry" table.
    If we don't have a table for the category, we will put it in a generic table called "item".
    """

    __tablename__ = "category"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)


class UUID_Group(SQLModel, table=True):
    """
    Represents a group of UUIDs that are associated with a category.

    For example, the "action" category might have 3 UUID groups associated with it: "6ab...", "7cd...", and "8ef...".
    AoN doesn't expose what each UUID_Group represents, but we can infer that they are different types of actions.

    After looking into them we might see that "6ab..." is a list of exemplar actions, "7cd..." is a list of champion reactions, and "8ef..." is a list of free actions.
    Once we know what each UUID_Group represents, we can give them a name like "exemplar actions", "champion reactions", and "free actions".
    """

    __tablename__ = "uuid_group"

    id: int | None = Field(default=None, primary_key=True)
    uuid: str = Field(unique=True, index=True)
    category_id: int = Field(foreign_key="category.id")
    label: str | None


class Ancestry(NethysData, table=True):
    """
    Data model for the 'ancestry' category.
    """

    __tablename__ = "ancestry"

    # The 'id' field is retrieved from the index aon api and is structured like 'ancestry-1234'. We extract the number and use it as the primary key.
    id: int = Field(primary_key=True)

    name: str
    hp: int | None
    size: List[enums.Size] = Field(sa_column=Column(PickleType))
    speed: int
    ability_boost: List[enums.AbilityBoost] = Field(sa_column=Column(PickleType))
    ability_flaw: enums.Ability | None
    language: List[str] = Field(sa_column=Column(PickleType))
    vision: enums.Vision | None
    rarity: enums.Rarity


class Class(NethysData, table=True):
    """
    Data model for the 'class' category.
    """

    __tablename__ = "class"

    # The 'id' field is retrieved from the index aon api and is structured like 'class-1234'. We extract the number and use it as the primary key.
    id: int = Field(primary_key=True)

    name: str
    ability: List[enums.Ability] = Field(sa_column=Column(PickleType))
    hp: int
    tradition: enums.SpellcastingTradition | None

    attack_proficiency: Dict[enums.AttackProficiency, enums.Proficiency] = Field(
        sa_column=Column(PickleType)
    )
    defense_proficiency: Dict[enums.DefenseProficiency, enums.Proficiency] = Field(
        sa_column=Column(PickleType)
    )

    fortitude_save_proficiency: enums.Proficiency
    reflex_save_proficiency: enums.Proficiency
    will_save_proficiency: enums.Proficiency

    perception_proficiency: enums.Proficiency
    skill_proficiency: Dict[enums.Skill | str, enums.Proficiency] = Field(
        sa_column=Column(PickleType)
    )

    rarity: enums.Rarity


class Item(NethysData, table=True):
    """
    Data model for the 'item' category.

    This is a generic model that can be used for any item that doesn't have a specific model.
    """

    # The 'id' field is a primary key and is autmoatically generated by the database unlike our other models.
    # We get all the ids from the api for other models, because the ids are strucutred like 'class-1234' or 'ancestry-5678'.
    # For other models we can split the id on the '-' and use the first part as the category.
    # For the 'item' category, we don't have that luxury.
    # Instead, we will store the 'api id' as the category_id and the category as the category_name.
    id: int = Field(default=None, primary_key=True)
    category_id: str
    category_name: str
    data: dict[str, Any] = Field(sa_column=Column(PickleType))


# This dictionary maps category names to their respective models.
MODEL_MAP = {
    "ancestry": Ancestry,
    "class": Class,
}
DefaultNethysDataModel = Item

engine = create_engine(database_url)
SQLModel.metadata.create_all(engine)
