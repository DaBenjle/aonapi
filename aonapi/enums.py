from enum import Enum


class Size(str, Enum):
    tiny = "tiny"
    small = "small"
    medium = "medium"
    large = "large"
    huge = "huge"


class Ability(str, Enum):
    strength = "strength"
    dexterity = "dexterity"
    constitution = "constitution"
    intelligence = "intelligence"
    wisdom = "wisdom"
    charisma = "charisma"


class AbilityBoost(str, Enum):
    strength = "strength"
    dexterity = "dexterity"
    constitution = "constitution"
    intelligence = "intelligence"
    wisdom = "wisdom"
    charisma = "charisma"
    free = "free"
    two_free_ability_boosts = "two free ability boosts"


class Vision(str, Enum):
    darkvision = "darkvision"
    low_light_vision = "low-light vision"


class Rarity(str, Enum):
    common = "common"
    uncommon = "uncommon"
    rare = "rare"
    unique = "unique"


class SpellcastingTradition(str, Enum):
    arcane = "arcane"
    divine = "divine"
    occult = "occult"
    primal = "primal"


class Proficiency(str, Enum):
    untrained = "untrained"
    trained = "trained"
    expert = "expert"
    master = "master"
    legendary = "legendary"


class AttackProficiency(str, Enum):
    simple = "simple"
    martial = "martial"
    advanced = "advanced"
    unarmed = "unarmed"
    alchemical_bombs = "alchemical bombs"
    simple_firearms_and_crossbows = "simple firearms and crossbows"
    martial_firearms_and_crossbows = "martial firearms and crossbows"
    advanced_firearms_and_crossbows = "advanced firearms and crossbows"
    diety_favored_weapon = "diety favored weapon"


class DefenseProficiency(str, Enum):
    unarmored = "unarmored"
    light = "light"
    medium = "medium"
    heavy = "heavy"


class Save(str, Enum):
    fortitude = "fortitude"
    reflex = "reflex"
    will = "will"


class Skill(str, Enum):
    acrobatics = "acrobatics"
    arcana = "arcana"
    athletics = "athletics"
    crafting = "crafting"
    deception = "deception"
    diplomacy = "diplomacy"
    intimidation = "intimidation"
    medicine = "medicine"
    nature = "nature"
    occultism = "occultism"
    performance = "performance"
    religion = "religion"
    society = "society"
    stealth = "stealth"
    survival = "survival"
    thievery = "thievery"
    lore = "lore"


class Lore(str, Enum):
    accounting = "accounting"
    architecture = "architecture"
    art = "art"
    astronomy = "astronomy"
    carpentry = "carpentry"
    circus = "circus"
    driving = "driving"
    engineering = "engineering"
    farming = "farming"
    fishing = "fishing"
    fortune = "fortune"
    games = "games"
    genealogy = "genealogy"
    gladiatorial = "gladiatorial"
    guild = "guild"
    heraldry = "heraldry"
    herbalism = "herbalism"
    hunting = "hunting"
    labor = "labor"
    legal = "legal"
    library = "library"
    specific_deity = "specific deity"
    specific_creature = "specific creature"
    specific_plane = "specific plane"
    specific_organization = "specific organization"
    specific_settlement = "specific settlement"
    specific_terrain = "specific terrain"
    specific_food_or_drink = "specific food or drink"
    mercantile = "mercantile"
    midwifery = "midwifery"
    milling = "milling"
    mining = "mining"
    piloting = "piloting"
    sailing = "sailing"
    scouting = "scouting"
    scribing = "scribing"
    stabling = "stabling"
    tanning = "tanning"
    theater = "theater"
    underworld = "underworld"
    warfare = "warfare"
