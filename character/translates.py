from typing import Any

from .info_classes import (
    Element,
    Immunity,
    Language,
    Position,
    Tag,
    Usage,
)


def translate(obj: Element | Position | Immunity | Usage | Tag, lang: Language) -> str:
    tl_dict: dict[Language, dict[Any, str]]
    match obj:
        case Element():
            tl_dict = ELEMENT_TRANSLATE
        case Position():
            tl_dict = POSITION_TRANSLATE
        case Immunity():
            tl_dict = IMMUNITY_TRANSLATE
        case Usage():
            tl_dict = USAGE_TRANSLATE
        case Tag():
            tl_dict = TAG_TRANSLATE
        case _:
            raise TypeError
    return tl_dict.get(lang, {}).get(obj, obj.name.lower())


ELEMENT_TRANSLATE = {
    Language.TC: {
        Element.FIRE: "火",
        Element.WATER: "水",
        Element.WIND: "風",
        Element.LIGHT: "光",
        Element.DARK: "暗",
    },
    Language.SC: {
        Element.FIRE: "火",
        Element.WATER: "水",
        Element.WIND: "风",
        Element.LIGHT: "光",
        Element.DARK: "暗",
    },
    Language.EN: {
        Element.FIRE: "Fire",
        Element.WATER: "Water",
        Element.WIND: "Wind",
        Element.LIGHT: "Light",
        Element.DARK: "Dark",
    },
    Language.JP: {
        Element.FIRE: "火",
        Element.WATER: "水",
        Element.WIND: "風",
        Element.LIGHT: "光",
        Element.DARK: "闇",
    },
    Language.KR: {
        Element.FIRE: "화",
        Element.WATER: "수",
        Element.WIND: "풍",
        Element.LIGHT: "광",
        Element.DARK: "암",
    },
}

POSITION_TRANSLATE = {
    Language.TC: {
        Position.ATTACKER: "攻擊者",
        Position.PROTECTOR: "守護者",
        Position.HEALER: "治療者",
        Position.SUPPORTER: "輔助者",
        Position.OBSTRUCTER: "妨礙者",
    },
}

IMMUNITY_TRANSLATE = {
    Language.TC: {
        Immunity.SLEEP: "睡眠",
        Immunity.SILENCE: "沉默",
        Immunity.PARALYSIS: "麻痺",
    },
}

USAGE_TRANSLATE = {
    Language.TC: {
        Usage.GENERAL_ATK: "通用攻擊",
        Usage.GENERAL_BUFF: "通用增益",
        Usage.GENERAL_DEBUFF: "通用削弱",
        Usage.GENERAL_HEAL: "通用治療",
        Usage.SKILL_ATK: "技能攻擊",
        Usage.SKILL_BUFF: "技能增益",
        Usage.SKILL_DEBUFF: "技能削弱",
        Usage.SKILL_HEAL: "技能治療",
        Usage.AUTO_ATK: "普攻攻擊",
        Usage.AUTO_BUFF: "普攻增益",
        Usage.AUTO_DEBUFF: "普攻削弱",
        Usage.AUTO_HEAL: "普攻治療",
        Usage.PROC_ATK: "觸發攻擊",
        Usage.PROC_BUFF: "觸發增益",
        Usage.PROC_DEBUFF: "觸發削弱",
        Usage.PROC_HEAL: "觸發治療",
    },
}

TAG_TRANSLATE = {
    Language.TC: {
        # damage up buffs
        Tag.dmg_up: "增傷",
        Tag.dmg_up_self: "自身增傷",
        Tag.dmg_up_1: "1號位增傷",
        Tag.dmg_up_2: "2號位增傷",
        Tag.dmg_up_3: "3號位增傷",
        Tag.dmg_up_4: "4號位增傷",
        Tag.dmg_up_5: "5號位增傷",
        Tag.dmg_up_attacker: "攻擊者增傷",
        Tag.dmg_up_protector: "保護者增傷",
        Tag.dmg_up_healer: "治療者增傷",
        Tag.dmg_up_supporter: "輔助者增傷",
        Tag.dmg_up_obstructer: "妨礙者增傷",
        Tag.dmg_up_water: "水屬性增傷",
        Tag.dmg_up_fire: "火屬性增傷",
        Tag.dmg_up_wind: "風屬性增傷",
        Tag.dmg_up_light: "光屬性增傷",
        Tag.dmg_up_dark: "暗屬性增傷",
        # -- auto
        Tag.dmg_up_auto: "普攻增傷",
        Tag.dmg_up_auto_self: "自身普攻增傷",
        Tag.dmg_up_auto_2: "2號位普攻增傷",
        Tag.dmg_up_auto_5: "5號位普攻增傷",
        Tag.dmg_up_auto_attacker: "攻擊者普攻增傷",
        Tag.dmg_up_auto_protector: "保護者普攻增傷",
        Tag.dmg_up_auto_healer: "治療者普攻增傷",
        Tag.dmg_up_auto_supporter: "輔助者普攻增傷",
        Tag.dmg_up_auto_obstructer: "妨礙者普攻增傷",
        Tag.dmg_up_auto_water: "水屬性普攻增傷",
        Tag.dmg_up_auto_fire: "火屬性普攻增傷",
        Tag.dmg_up_auto_wind: "風屬性普攻增傷",
        Tag.dmg_up_auto_light: "光屬性普攻增傷",
        Tag.dmg_up_auto_dark: "暗屬性普攻增傷",
        # -- proc
        Tag.dmg_up_proc: "觸發技增傷",
        Tag.dmg_up_proc_self: "自身觸發技增傷",
        # -- skill
        Tag.dmg_up_skill: "必殺技增傷",
        Tag.dmg_up_skill_self: "自身必殺技增傷",
        Tag.dmg_up_skill_1: "1號位必殺技增傷",
        Tag.dmg_up_skill_2: "2號位必殺技增傷",
        Tag.dmg_up_skill_3: "3號位必殺技增傷",
        Tag.dmg_up_skill_4: "4號位必殺技增傷",
        Tag.dmg_up_skill_5: "5號位必殺技增傷",
        Tag.dmg_up_skill_attacker: "攻擊者必殺技增傷",
        Tag.dmg_up_skill_protector: "保護者必殺技增傷",
        Tag.dmg_up_skill_healer: "治療者必殺技增傷",
        Tag.dmg_up_skill_supporter: "輔助者必殺技增傷",
        Tag.dmg_up_skill_obstructer: "妨礙者必殺技增傷",
        Tag.dmg_up_skill_water: "水屬性必殺技增傷",
        Tag.dmg_up_skill_fire: "火屬性必殺技增傷",
        Tag.dmg_up_skill_wind: "風屬性必殺技增傷",
        Tag.dmg_up_skill_light: "光屬性必殺技增傷",
        Tag.dmg_up_skill_dark: "暗屬性必殺技增傷",
        # -- dot
        Tag.dmg_up_dot: "持續傷害增加",
        # revieved damage debuffs
        Tag.r_dmg_up: "易傷",
        Tag.r_dmg_up_all_element: "全屬性易傷",
        Tag.r_dmg_up_fire: "火屬性易傷",
        Tag.r_dmg_up_water: "水屬性易傷",
        Tag.r_dmg_up_wind: "風性易傷",
        Tag.r_dmg_up_light: "光屬性易傷",
        Tag.r_dmg_up_dark: "暗屬性易傷",
        Tag.r_dmg_up_auto: "普攻易傷",
        Tag.r_dmg_up_proc: "觸發技易傷",
        Tag.r_dmg_up_skill: "必殺技易傷",
        Tag.r_dmg_up_attacker: "攻擊者易傷",
        Tag.r_dmg_up_protector: "保護者易傷",
        Tag.r_dmg_up_healer: "治療者易傷",
        Tag.r_dmg_up_supporter: "輔助者易傷",
        Tag.r_dmg_up_obstructer: "妨礙者易傷",
        Tag.r_dmg_up_dot: "持續傷害易傷",
        # general buffs
        Tag.atk_up: "攻擊增加",
        Tag.atk_up_self: "自身攻擊增加",
        Tag.cd_down: "當前CD減少",
        Tag.cd_down_start: "開場CD減少",
        Tag.cc_chance_down: "控場機率降低",
        Tag.def_cut_up: "防禦減傷增加",
        Tag.dmg_to_def_up: "對防禦增傷",
        Tag.extra_hit: "追加傷害",
        Tag.heal_up: "治療增加",
        Tag.hot: "持續治療",
        Tag.hp_up: "最大HP增加",
        Tag.hp_up_self: "自身最大HP增加",
        Tag.max_cd_down: "最大CD減少",
        Tag.r_dmg_down: "受到傷害減少",
        Tag.shield: "謢盾",
        Tag.shield_up: "謢盾效果增加",
        Tag.taunt: "嘲諷",
        # general debuffs
        Tag.cd_up: "當前CD增加",
        Tag.cd_stop: "停止CD倒數",
        Tag.def_cut_down: "防禦減傷減少",
        Tag.dmg_down: "造成傷害減少",
        Tag.dot: "持續傷害",
        Tag.heal_down: "治療減少",
        Tag.shield_down: "謢盾減少",
        # cc
        Tag.sleep: "睡眠",
        Tag.silence: "沉默",
        Tag.paralysis: "麻痺",
        # rm
        Tag.rm_def: "解除防禦",
        Tag.rm_taunt: "解除嘲諷",
        Tag.rm_shield: "解除謢盾",
        Tag.rm_sleep: "解除睡眠",
        Tag.rm_silence: "解除沉默",
        Tag.rm_paralysis: "解除麻痺",
        Tag.rm_atk_down: "解除攻擊減少",
        Tag.rm_dmg_down: "解除造成傷害減少",
        Tag.rm_auto_down: "解除普攻傷害減少",
        Tag.rm_proc_down: "解除觸發技傷害減少",
        Tag.rm_skill_down: "解除必殺技傷害減少",
        Tag.rm_shield_down: "解除謢盾減少",
        Tag.rm_heal_down: "解除治療減少",
    }
}
