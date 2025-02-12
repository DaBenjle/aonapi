from sqlmodel import Field, SQLModel, create_engine, PickleType, Column
from typing import List, Dict, Any
from aonapi import enums
from aonapi.settings import database_url, debug


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


class Ancestry(SQLModel, table=True):
    """
    Data model for the 'ancestry' category.
    """

    __tablename__ = "ancestry"

    id: int | None = Field(default=None, primary_key=True)
    name: str
    hp: int | None
    size: List[enums.Size] = Field(sa_column=Column(PickleType))
    speed: int
    ability_boost: List[enums.AbilityBoost] = Field(sa_column=Column(PickleType))
    ability_flaw: enums.Ability | None
    language: List[str] = Field(sa_column=Column(PickleType))
    vision: enums.Vision | None
    rarity: enums.Rarity


class Class(SQLModel, table=True):
    """
    Data model for the 'class' category.
    """

    __tablename__ = "class"

    id: int | None = Field(default=None, primary_key=True)
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


class Item(SQLModel, table=True):
    """
    Data model for the 'item' category.

    This is a generic model that can be used for any item that doesn't have a specific model.
    """

    # The 'id' field is a primary key and is not automatically generated.
    # We get it from the api.
    # We get all the ids from the api for other models as well, but ids are strucutred like 'class-1234' or 'ancestry-5678'.
    # For other models we can split the id on the '-' and use the first part as the category.
    # For the 'item' category, we don't have that luxury.
    id: str | None = Field(default=None, primary_key=True)
    data: dict[str, Any] = Field(sa_column=Column(PickleType))


engine = create_engine(database_url, echo=debug)
SQLModel.metadata.create_all(engine)
