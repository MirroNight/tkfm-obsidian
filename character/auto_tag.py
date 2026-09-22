import logging
from itertools import product
from re import compile, findall, search
from re import split as re_split

from .info_classes import CharacterInfo, Language, Tag
from .key_tag_maps import tag_map_dmg_buff, tag_map_general, tag_map_r_dmg_debuff

logger = logging.getLogger(__name__)

regex_src_types = compile(r"([全水火風光暗]|攻擊|守護|治療|輔助|妨礙)")
regex_dmg_type_debuff = compile(r"(普攻|觸發|必殺|持續)")
regex_dmg_type_buff = compile(r"(造成|普攻|觸發|必殺|持續)")

regex_r_dmg_debuff = compile(
    r"(?:敵方|目標|、)?(?:全體|站位(?:、?\d)+目標)?"
    r"(受到)(?:我方)?"
    r"((?:[、與和]?[全水火風光暗])+屬性的?(?:隊員|角色)?|(?:[、與和]?(?:攻擊者|守護者|治療者|輔助者|妨礙者))+)?"
    r"(普攻|必殺技?|觸發技?|持續型?)?傷害增加"
    r"(.*)"
)

regex_dmg_buff_1 = compile(r"^(造成|(?:造成)?(?:普攻|必殺|觸發|持續))[技型]?傷害增加")
regex_dmg_buff_2 = compile(
    r"(我方|自身)"
    r"(全體|站位(?:、?\d)*)?"
    r"((?:[、與和]?[全水火風光暗])+屬性的?(?:隊員|角色)?|(?:[、與和]?(?:攻擊者|守護者|治療者|輔助者|妨礙者))+)?"
    r"(?:(?!站位|受到|自身|全體|目標|位).)*?"
    r"(造成|普攻|必殺技?|觸發技?|持續型?)傷害增加"
    r"((?:(?!受到).)*)"
    # r"((?:(?!站位|受到|自身|全體|目標|位).)*)"
)
regex_dmg_buff_3 = compile(
    r"(我方|自身)?"
    r"(全體|站位(?:、?\d)*)?"
    r"((?:[、與和]?[全水火風光暗])+屬性的?(?:隊員|角色)?|(?:[、與和]?(?:攻擊者|守護者|治療者|輔助者|妨礙者))+)?"
    r"(?:(?!站位|受到|自身|全體|目標|位).)*?"
    r"(造成|普攻|必殺技?|觸發技?|持續型?)傷害增加"
    r"((?:(?!受到).)*)"
    # r"((?:(?!站位|受到|自身|全體|目標|位).)*)"
)

regex_atk_up = compile(
    r"(我方|自身)"
    r"(全體|站位(?:、?\d)*)?"
    r"((?:[、與和]?[全水火風光])+屬性的?(?:隊員|角色)?|[、與和]?(?:攻擊|守護|治療|輔助|妨礙)者)*"
    r"攻擊力增加"
)

regex_general_tags = [
    ### general buffs
    # atk_up | atk_up_self
    compile(r"(?:(我方)(?:全體|站位(?:、?\d)*)|(自身))(攻擊)力?(增加)"),
    # cd_down | cd_down_start | max_cd_down
    compile(r"(第1回合)?.*?(?:當前)?(?:必殺技?)?(最大)?(CD減少)"),
    # cc_chance_down
    compile(r"(控場機率減少)"),
    # dmg_to_def_up
    compile(r"(對防禦目標)(?:造成)?(傷害增加)"),
    # extra_hit
    compile(r"(追擊)|(追加).*(造成傷害)"),
    # hot
    compile(r"(回合).*進行(治療)"),
    # hp_up | hp_up_self
    compile(r"(?:(我方)(?:全體|站位(?:、?\d)*)|(自身))(最大HP增加)"),
    # r_dmg_down
    compile(r"(受到傷害減少)"),
    # shield
    compile(r"(?:獲得|施放|給予).*?(護盾)[^量增減效]"),
    # taunt
    compile(r"(獲得嘲諷)"),
    ### general debuffs
    # cd_up | cd_stop
    compile(r"(目標).*?(CD增加)|(停止)"),
    # dmg_down
    compile(r"(?:目標|敵方).*?(造成傷害減少)"),
    # dot
    compile(r"(每回合)(?:對目標)?(造成傷害)"),
    ### mixed
    # def_cut_up | def_cut_down
    compile(r"(防禦)時?(減傷)(?:效果)?(增加|減少)"),
    # heal_up | heal_down
    compile(r"(治療).{0,5}(增加|減少)"),
    # shield_up | shield_down
    compile(r"(護盾)[量增減效].*?(增加|減少)"),
    ## cc
    # sleep | silence | paralysis
    compile(r"(目標)(?:造成)?(睡眠|沉默|麻痺)"),
    ### remove buffs/debuffs
    # rm_def | rm_taunt | rm_shield
    compile(r"(解除防禦狀態)"),
    compile(r"(解除)[^我自站]*(嘲諷)"),
    compile(r"(解除)[^我自站]*(護盾)"),
    # rm_sleep | rm_silence | rm_paralysis
    compile(r"(解除).*(睡眠)"),
    compile(r"(解除).*(沉默)"),
    compile(r"(解除).*(麻痺)"),
    # rm_atk_down
    compile(r"(解除)[^敵目]*(攻擊)力?(減少)"),
    # rm_dmg_down | rm_auto_down |rm_proc_down | rm_skill_down
    compile(r"(解除)[^敵目]*(造成)(?:傷害)?(減少)"),
    compile(r"(解除)[^敵目]*(普攻)(?:傷害)?(減少)"),
    compile(r"(解除)[^敵目]*(觸發)技?(?:傷害)?(減少)"),
    compile(r"(解除)[^敵目]*(必殺)技?(?:傷害)?(減少)"),
    # rm_shield_down | rm_heal_down
    compile(r"(解除)[^敵目]*(護盾)(?:量|效果)?(減少)"),
    compile(r"(解除)[^敵目]*(治療)(?:量|效果)?(減少)"),
]


def get_r_dmg_debuff_tags(s: str) -> set[Tag]:
    tags: set[Tag] = set()

    while m := search(regex_r_dmg_debuff, s):
        if not any(m.groups()[:3]):
            break
        # 0: recieve  1: dmg_srcs  2: dmg_typs  3: leftover
        recieve, dmg_srcs, dmg_typs, s = m.groups()
        dmg_srcs = findall(regex_src_types, dmg_srcs) if dmg_srcs else [""]
        dmg_typs = findall(regex_dmg_type_debuff, dmg_typs) if dmg_typs else [""]

        for dmg_src, dmg_typ in product(dmg_srcs, dmg_typs):
            key = recieve + dmg_src + dmg_typ
            tags.add(tag_map_r_dmg_debuff[key])

    # print(sorted(tags, key=lambda e: e.value) if tags else "", end="")
    return tags


def get_dmg_buff_tags(s: str) -> set[Tag]:
    tags: set[Tag] = set()

    if m := search(regex_dmg_buff_1, s):
        tags.add(tag_map_dmg_buff[m.group(1)])
        # print(sorted(tags, key=lambda e: e.value) if tags else "", end="")
        return tags

    self = ""
    if m := search(regex_dmg_buff_2, s):
        # 0: self  1: crews  2: dmg_srcs  3: dmg_typs  4: leftover
        self, crews, dmg_srcs, dmg_typs, s = m.groups()
        crews = findall(r"(全體|\d)", crews) if crews else [""]
        dmg_srcs = findall(regex_src_types, dmg_srcs) if dmg_srcs else [""]
        dmg_typs = findall(regex_dmg_type_buff, dmg_typs) if dmg_typs else [""]

        for crew, dmg_src, dmg_typ in product(crews, dmg_srcs, dmg_typs):
            # self = "我方" if self == "自身" and crew else self
            crew = "" if self == "我方" and crew == "全體" else crew
            key = self + crew + dmg_src + dmg_typ
            tags.add(tag_map_dmg_buff[key])

    while m := search(regex_dmg_buff_3, s):
        if not any(m.groups()[:4]):
            break
        # 0: self  1: crews  2: dmg_srcs  3: dmg_typs  4: leftover
        new_self, crews, dmg_srcs, dmg_typs, s = m.groups()
        self = new_self if new_self else self
        crews = findall(r"(全體|\d)", crews) if crews else [""]
        dmg_srcs = findall(regex_src_types, dmg_srcs) if dmg_srcs else [""]
        dmg_typs = findall(regex_dmg_type_buff, dmg_typs) if dmg_typs else [""]

        for crew, dmg_src, dmg_typ in product(crews, dmg_srcs, dmg_typs):
            # self = "我方" if self == "自身" and crew else self
            crew = "" if self == "我方" and crew == "全體" else crew
            key = self + crew + dmg_src + dmg_typ
            tags.add(tag_map_dmg_buff[key])

    # print(sorted(tags, key=lambda e: e.value) if tags else "", end="")
    return tags


def get_general_tags(s: str) -> set[Tag]:
    tags: set[Tag] = set()
    for regex in regex_general_tags:
        if m := search(regex, s):
            key = "".join([_ if _ else "" for _ in m.groups()])
            tags.add(tag_map_general[key])
    return tags


def get_all_tags(expression: str) -> set[Tag]:
    tags: set[Tag] = set()
    # print()
    # print(expression)
    tags |= get_r_dmg_debuff_tags(expression)
    tags |= get_dmg_buff_tags(expression)
    tags |= get_general_tags(expression)
    # print()
    return tags


def tags_from_abilities(abilities: list[str]) -> set[Tag]:
    # NOTE: replace [闇閽] with [暗] before hand to make regex easier
    tags: set[Tag] = set()
    for ability in abilities:
        for expression in re_split(
            r"，再|。|\\n",
            ability.translate(str.maketrans("闇閽", "暗暗"))
            .replace("回復", "治療")
            .replace("清除", "解除"),
        ):
            tags |= get_all_tags(expression)
    return tags


def auto_tag(character: CharacterInfo) -> CharacterInfo:
    leader: list[str] = [character.leader[Language.TC][1]]
    skills: list[str] = [
        character.skill_s[Language.TC][1],
        character.attack[Language.TC][1],
        character.passive_1[Language.TC][1],
        character.passive_2[Language.TC][1],
        character.passive_3[Language.TC][1],
    ]
    liberate: list[str] = [
        *[skill[Language.TC][1] for skill in character.liberate_1.values() if skill],
        *[skill[Language.TC][1] for skill in character.liberate_2.values() if skill],
        *[skill[Language.TC][1] for skill in character.liberate_3.values() if skill],
    ]

    # print()
    # print("=====")
    # print(character.full_name(Language.TC))
    logger.debug(f"Tagging {character.meta}")

    logger.debug("Leader tags")
    character.l_tags = (
        character.l_tags if character.l_tags else tags_from_abilities(leader)
    )
    logger.debug("Skills tags")
    character.s_tags = (
        character.s_tags if character.s_tags else tags_from_abilities(skills)
    )
    logger.debug("Libert tags")
    character.x_tags = (
        character.x_tags if character.x_tags else tags_from_abilities(liberate)
    )

    # print("L: ", character.l_tags)
    # print("S: ", character.s_tags)
    # print("X: ", character.x_tags)
    return character


if __name__ == "__main__":
    from pathlib import Path

    from extract_info import extract_character_info

    st, n = 1, 180
    files: list[str] = [f"SSR-{i:03}" for i in range(st, st + n + 1)]
    base_path: Path = Path("~/projects/TKFM-Data-Room/static/data/unit/").expanduser()

    r_dmg_tags = {}
    for filename in files:
        path_general: Path = base_path / "general" / f"{filename}.ts"
        path_skillset: Path = base_path / "skillset" / f"{filename}.ts"
        path_liberate: Path = base_path / "liberate" / f"{filename}.ts"

        # this will run auto_tag inside
        character: CharacterInfo = extract_character_info(
            path_general, path_skillset, path_liberate
        )
