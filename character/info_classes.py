from dataclasses import dataclass
from enum import Enum


class Language(Enum):
    TC = 1
    SC = 2
    EN = 3
    JP = 4
    KR = 5


class Rarity(Enum):
    SSR = 1
    SR = 2
    R = 3
    N = 4


class Element(Enum):
    FIRE = 1
    WIND = 2
    WATER = 3
    LIGHT = 4
    DARK = 5


class Position(Enum):
    ATTACKER = 1
    PROTECTOR = 2
    HEALER = 3
    SUPPORTER = 4
    OBSTRUCTER = 5


class Immunity(Enum):
    SLEEP = 1
    SILENCE = 2
    PARALYSIS = 3


class Usage(Enum):
    GENERAL_ATK = 1
    GENERAL_BUFF = 2
    GENERAL_DEBUFF = 3
    GENERAL_HEAL = 4
    SKILL_ATK = 5
    SKILL_BUFF = 6
    SKILL_DEBUFF = 7
    SKILL_HEAL = 8
    AUTO_ATK = 9
    AUTO_BUFF = 10
    AUTO_DEBUFF = 11
    AUTO_HEAL = 12
    PROC_ATK = 13
    PROC_BUFF = 14
    PROC_DEBUFF = 15
    PROC_HEAL = 16


# NOTE: lower case becuase all-caps is hard to read
Tag = Enum(
    "Tag",
    (
        # damage up buffs
        "dmg_up",
        "dmg_up_self",
        "dmg_up_1",
        "dmg_up_2",
        "dmg_up_3",
        "dmg_up_4",
        "dmg_up_5",
        "dmg_up_attacker",
        "dmg_up_protector",
        "dmg_up_healer",
        "dmg_up_supporter",
        "dmg_up_obstructer",
        "dmg_up_water",
        "dmg_up_fire",
        "dmg_up_wind",
        "dmg_up_light",
        "dmg_up_dark",
        # -- auto
        "dmg_up_auto",
        "dmg_up_auto_self",
        "dmg_up_auto_2",
        "dmg_up_auto_5",
        "dmg_up_auto_attacker",
        "dmg_up_auto_protector",
        "dmg_up_auto_healer",
        "dmg_up_auto_supporter",
        "dmg_up_auto_obstructer",
        "dmg_up_auto_water",
        "dmg_up_auto_fire",
        "dmg_up_auto_wind",
        "dmg_up_auto_light",
        "dmg_up_auto_dark",
        # -- proc
        "dmg_up_proc",
        "dmg_up_proc_self",
        # -- skill
        "dmg_up_skill",
        "dmg_up_skill_self",
        "dmg_up_skill_1",
        "dmg_up_skill_2",
        "dmg_up_skill_3",
        "dmg_up_skill_4",
        "dmg_up_skill_5",
        "dmg_up_skill_attacker",
        "dmg_up_skill_protector",
        "dmg_up_skill_healer",
        "dmg_up_skill_supporter",
        "dmg_up_skill_obstructer",
        "dmg_up_skill_water",
        "dmg_up_skill_fire",
        "dmg_up_skill_wind",
        "dmg_up_skill_light",
        "dmg_up_skill_dark",
        # -- dot
        "dmg_up_dot",
        # revieved damage debuffs
        "r_dmg_up",
        "r_dmg_up_all_element",
        "r_dmg_up_fire",
        "r_dmg_up_water",
        "r_dmg_up_wind",
        "r_dmg_up_light",
        "r_dmg_up_dark",
        "r_dmg_up_auto",
        "r_dmg_up_proc",
        "r_dmg_up_skill",
        "r_dmg_up_attacker",
        "r_dmg_up_protector",
        "r_dmg_up_healer",
        "r_dmg_up_supporter",
        "r_dmg_up_obstructer",
        "r_dmg_up_dot",
        # general buffs
        "atk_up",
        "atk_up_self",
        "cd_down",
        "cd_down_start",
        "cc_chance_down",
        "def_cut_up",
        "dmg_to_def_up",
        "extra_hit",
        "heal_up",
        "hot",
        "hp_up",
        "hp_up_self",
        "max_cd_down",
        "r_dmg_down",
        "shield",
        "shield_up",
        "taunt",
        # general debuffs
        "cd_up",
        "cd_stop",
        "def_cut_down",
        "dmg_down",
        "dot",
        "heal_down",
        "shield_down",
        # cc
        "sleep",
        "silence",
        "paralysis",
        # rm
        "rm_def",
        "rm_taunt",
        "rm_shield",
        "rm_sleep",
        "rm_silence",
        "rm_paralysis",
        "rm_atk_down",
        "rm_dmg_down",
        "rm_auto_down",
        "rm_proc_down",
        "rm_skill_down",
        "rm_shield_down",
        "rm_heal_down",
    ),
)


@dataclass
class CharacterInfo:
    # generic info
    id: int
    meta: str
    prefix: dict[Language, str]
    name: dict[Language, str]
    abbreviation: dict[Language, list[str]]
    background: dict[Language, str]
    rarity: Rarity
    element: Element
    position: Position
    is_limited: bool
    release_date: str
    other_version: list[str]
    immunity: list[Immunity]
    cooldown: set[int]

    # skill info
    skill_s: dict[Language, tuple[str, str]]
    attack: dict[Language, tuple[str, str]]
    leader: dict[Language, tuple[str, str]]
    passive_1: dict[Language, tuple[str, str]]
    passive_2: dict[Language, tuple[str, str]]
    passive_3: dict[Language, tuple[str, str]]
    general_1: dict[Language, tuple[str, str]]
    general_2: dict[Language, tuple[str, str]]
    liberate_1: dict[str, dict[Language, tuple[str, str]]]
    liberate_2: dict[str, dict[Language, tuple[str, str]]]
    liberate_3: dict[str, dict[Language, tuple[str, str]]]

    # tags
    requirement: dict[Language, str]
    usages: list[Usage]  # usages
    l_tags: set[Tag]  # for leader
    s_tags: set[Tag]  # not leader
    x_tags: set[Tag]  # liberate tags

    # user data
    owned: bool | None = None
    skill_lv: int | None = None

    def full_name(self, lang: Language) -> str:
        return f"{self.prefix[lang]} {self.name[lang]}".strip()
