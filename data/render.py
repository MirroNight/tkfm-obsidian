from functools import partial

from character.info_classes import (
    Language,
    Tag,
)
from character.tag_heirarchy import get_tag_type
from character.translates import translate

from .templates import (
    apply_translate,
    base_template,
    dataview_template,
)


def get_tag_list(lang: Language) -> str:
    tl = partial(translate, lang=lang)
    tag_grouped: dict[str, list[Tag]] = {
        "general buffs": [],
        "general debuffs": [],
        "damage up": [],
        "dot damage up": [],
        "proc damage up": [],
        "auto damage up": [],
        "skill damage up": [],
        "received damage up": [],
        "crowd control": [],
        "remove": [],
        "other": [],
    }
    for tag in Tag:
        tag_grouped[get_tag_type(tag)].append(tag)

    ret = "## Tag List\n\n"
    for group, tag_list in tag_grouped.items():
        ret += f"### {group.capitalize()}\n"
        for tag in tag_list:
            ret += f"- {tl(tag)}\n"
        ret += "\n"
    return ret


def get_base_example(lang: Language) -> str:
    return apply_translate(base_template, lang)


def get_dataview_example(lang: Language) -> str:
    return apply_translate(dataview_template, lang)
