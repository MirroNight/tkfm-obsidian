from re import compile
from re import match as re_match

from .info_classes import Tag

rm = compile(r"rm_")
r_dmg_up = compile(r"r_dmg_up")
dmg_up_dot = compile(r"dmg_up_dot")
dmg_up_skill = compile(r"dmg_up_skill")
dmg_up_proc = compile(r"dmg_up_proc")
dmg_up_auto = compile(r"dmg_up_auto")
dmg_up = compile(r"dmg_up")

general_buffs = [
    Tag.atk_up,
    Tag.atk_up_self,
    Tag.cd_down,
    Tag.cd_down_start,
    Tag.cc_chance_down,
    Tag.def_cut_up,
    Tag.dmg_to_def_up,
    Tag.extra_hit,
    Tag.heal_up,
    Tag.hot,
    Tag.hp_up,
    Tag.hp_up_self,
    Tag.max_cd_down,
    Tag.r_dmg_down,
    Tag.shield,
    Tag.shield_up,
    Tag.taunt,
]

general_debuffs = [
    Tag.cd_up,
    Tag.cd_stop,
    Tag.def_cut_down,
    Tag.dmg_down,
    Tag.dot,
    Tag.heal_down,
    Tag.shield_down,
]

cc = [
    Tag.sleep,
    Tag.silence,
    Tag.paralysis,
]


def get_tag_type(tag: Tag) -> str:
    t = tag.name
    if re_match(rm, t):
        return "remove"
    if re_match(r_dmg_up, t):
        return "received damage up"
    if re_match(dmg_up_dot, t):
        return "dot damage up"
    if re_match(dmg_up_skill, t):
        return "skill damage up"
    if re_match(dmg_up_proc, t):
        return "proc damage up"
    if re_match(dmg_up_auto, t):
        return "auto damage up"
    if re_match(dmg_up, t):
        return "damage up"
    if t in general_buffs:
        return "general buffs"
    if t in general_debuffs:
        return "general debuffs"
    if t in cc:
        return "crowd control"
    return "other"
