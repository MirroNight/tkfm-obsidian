import json
import logging
from functools import partial
from itertools import product
from pathlib import Path
from re import match as re_match
from re import sub as re_sub
from types import NoneType

from .extract_info import extract_character_info, get_owned_info
from .info_classes import (
    CharacterInfo,
    Element,
    Language,
    Position,
    Rarity,
)
from .translates import translate

logger = logging.getLogger(__name__)


def build_character_map(
    path_tkfm_data_room: Path,
) -> dict[str, CharacterInfo]:
    # list paths
    gnrl_dir: Path = path_tkfm_data_room / "static" / "data" / "unit" / "general"
    skll_dir: Path = path_tkfm_data_room / "static" / "data" / "unit" / "skillset"
    lbrt_dir: Path = path_tkfm_data_room / "static" / "data" / "unit" / "liberate"

    logger.info("Searching characters")

    char_files: set[Path] = {
        Path(file.name)
        for file in gnrl_dir.iterdir()
        if re_match(r"(?:N|R|SR|SSR)-\d+.ts", file.name)
        and not logger.debug(f"  {file.name}")
    }

    logger.info(f"{len(char_files)} characters found, extracting information")

    char_list: list[CharacterInfo] = [
        extract_character_info(
            gnrl_dir / file_name, skll_dir / file_name, lbrt_dir / file_name
        )
        for file_name in char_files
        if not logger.debug(f"  '{file_name.name}'")
    ]

    logger.info("Building character map")

    char_map: dict[str, CharacterInfo] = {
        char.meta: char for char in char_list if not logger.debug(f"  {char.meta}")
    }
    return dict(sorted(char_map.items(), key=lambda item: item[1].id))


def copy_icons(
    path_tenkaassist: Path,
    output_dir: Path,
    lang: Language,
    char_map: dict[str, CharacterInfo],
    use_pic_id: bool = False,
    *,
    forec_update: bool = False,
) -> None:
    src_dir: Path = path_tenkaassist / "images" / "characters"
    dst_dir: Path = output_dir / "icons"

    logger.debug("Building icon table")
    get_name = lambda c: c.id if use_pic_id else c.full_name(lang)
    icons: dict[Path, Path] = {
        (src_dir / f"cs{char.id}_0_0.webp"): (dst_dir / f"{get_name(char)}.webp")
        for char in char_map.values()
    }

    logger.debug("Copying icons")
    for src in src_dir.iterdir():
        dst = icons[src] if src in icons else dst_dir / src.name
        logger.debug(f"  src '{src}'")
        logger.debug(f"  dst '{src}'")
        if not dst.exists() or forec_update:
            src.copy(dst)
            logger.debug("    Copied")


def collect_owned(
    char_map: dict[str, CharacterInfo], character_dir: Path, lang
) -> dict[str, CharacterInfo]:
    tl = partial(translate, lang=lang)

    # build reverse index (full_name -> meta)
    file_map = {char.full_name(lang): meta for meta, char in char_map.items()}

    for rarity, element in product(Rarity, Element):
        for file in (character_dir / rarity.name / tl(element)).iterdir():
            if file.is_file and file.suffix != ".md":
                continue
            char = char_map[file_map[file.stem]]
            char.owned, char.skill_lv = get_owned_info(file)
    return char_map


def load_owned(
    file: Path, character_map: dict[str, CharacterInfo]
) -> dict[str, CharacterInfo]:
    if file.suffix != ".json":
        raise FileExistsError(f"{file} is not a json file")
    with open(file, "r") as fd:
        owned_dict: dict[str, tuple[bool | None, int | None]] = json.load(fd)
    for meta, (owned, skill_lv) in owned_dict.items():
        if not isinstance(owned, bool | NoneType):
            raise TypeError(
                "Invalid 'owned' in {meta}({character_map[meta].full_name()})"
            )
        if not isinstance(skill_lv, int | NoneType):
            raise TypeError(
                "Invalid 'skill_lv' in {meta}({character_map[meta].full_name()})"
            )
        character_map[meta].owned = owned
        character_map[meta].skill_lv = skill_lv
    return character_map


def save_owned(
    file: Path, character_map: dict[str, CharacterInfo], lang: Language
) -> None:
    def consistent(a: bool | None, b: int | None) -> bool:
        # True when (one is missing) or (both set/missing)
        # False when (False, not 0) or (True, 0)
        if (a is None and b) or (a and b is None):
            return True
        return bool((a and b) or (not a and not b))

    owned_dict: dict[str, tuple[bool | None, int | None]] = {
        meta: (char.owned, char.skill_lv)
        for meta, char in character_map.items()
        if consistent(char.owned, char.skill_lv)
        and not logger.warning(
            f"Inconsistent ownership: {meta}({char.full_name(lang)})"
        )
    }
    with open(file, "w") as fd:
        fd.write(json.dumps(owned_dict, indent=2))


def sanitize(md: list[str]) -> list[str]:
    for i in range(md.index("## Background"), len(md)):
        md[i] = re_sub(
            r"CD\s?[:：]\s{0,2}",
            r"CD: ",
            (md[i].replace("[", "\\[").replace("]", "\\]").replace("%%", "%")),
        )
    return md


def as_md(
    char: CharacterInfo,
    char_map: dict[str, CharacterInfo],
    lang: Language = Language.TC,
    use_pic_id: bool = False,
) -> list[str]:

    tl = partial(translate, lang=lang)
    logger.debug(f"Building string for {char.full_name(lang)}")

    # character properties
    md = ["---"]
    md.extend([f"prefix: {char.prefix[lang]}"])
    md.extend([f"name: {char.name[lang]}"])
    md.extend(["aliases:"])
    if char.abbreviation.get(lang):
        md.extend([f"  - {tag}" for tag in char.abbreviation.get(lang, [])])
    md.extend([f"rarity: {char.rarity.name}"])
    md.extend([f"element: {tl(char.element)}"])
    # use "type" instead to prevent collision
    md.extend([f"type: {tl(char.position)}"])
    md.extend(["cooldown:"])
    md.extend([f'  - "{cd}"' for cd in char.cooldown])
    md.extend(["immunity:"])
    md.extend([f"  - {tl(imu)}" for imu in char.immunity])
    # tags
    md.extend(
        [
            "requirement: "
            # show req in lang, fallback to other language if lang DNE
            + char.requirement.get(
                lang, next((req for req in char.requirement.values() if req), "")
            )
        ]
    )
    md.extend(["usages:"])
    if char.usages:
        md.extend([f"  - {tl(usg)}" for usg in char.usages])
    md.extend(["leader_tags:"])
    if char.l_tags:
        md.extend([f"  - {tl(tag)}" for tag in char.l_tags])
    md.extend(["ability_tags:"])
    if char.s_tags:
        md.extend([f"  - {tl(tag)}" for tag in char.s_tags])
    md.extend(["liberate_tags:"])
    if char.x_tags:
        md.extend([f"  - {tl(tag)}" for tag in char.x_tags])
    # other less important properties
    md.extend([f"id: {char.id}"])
    md.extend([f"is_limited: {str(char.is_limited).lower()}"])
    md.extend([f"release_date: {char.release_date}"])
    md.extend(["other_version:"])
    if char.other_version:
        md.extend(
            [f'  - "[[{char_map[ver].full_name(lang)}]]"' for ver in char.other_version]
        )
    md.extend([f"owned: {char.owned}".lower() if char.skill_lv else "owned:"])
    md.extend([f"skill_level: {char.skill_lv}" if char.skill_lv else "skill_level:"])
    md.extend(["---"])

    # icon
    md.extend(
        [f"![[{char.full_name(lang)}.webp]]"]
        if not use_pic_id
        else [f"![[cs{char.id}_0_0.webp]]"],
    )

    # detail character info
    md.extend(["", "## Background"])
    md.extend(char.background[lang].split("\\n"))

    md.extend(["", "## Skill"])
    md.extend(["", f"### Ultimate: {char.skill_s[lang][0]}"])
    md.extend([f"{ult}" for ult in char.skill_s[lang][1].split("\\n")])

    md.extend(["", f"### Attack: {char.attack[lang][0]}"])
    md.extend([f"{atk}" for atk in char.attack[lang][1].split("\\n")])

    md.extend(["", f"### Leader: {char.leader[lang][0]}"])
    md.extend([f"{ldr}" for ldr in char.leader[lang][1].split("\\n")])

    md.extend(["", f"### Passive 1: {char.passive_1[lang][0]}"])
    md.extend([f"{ps1}" for ps1 in char.passive_1[lang][1].split("\\n")])

    md.extend(["", f"### Passive 2: {char.passive_2[lang][0]}"])
    md.extend([f"{ps2}" for ps2 in char.passive_2[lang][1].split("\\n")])

    md.extend(["", f"### Passive 3: {char.passive_3[lang][0]}"])
    md.extend([f"{ps3}" for ps3 in char.passive_3[lang][1].split("\\n")])

    md.extend(["", f"### General 1: {char.general_1[lang][0]}"])
    md.extend([f"{gn1}" for gn1 in char.general_1[lang][1].split("\\n")])

    md.extend(["", f"### General 2: {char.general_2[lang][0]}"])
    md.extend([f"{gn2}" for gn2 in char.general_2[lang][1].split("\\n")])

    if not any((char.liberate_1, char.liberate_2, char.liberate_3)):
        return md

    md.extend(["", "## Liberate"])
    md.extend(["", "### Stage 1"])
    for skill_type, desc in char.liberate_1.items():
        md.extend([f"- {skill_type}: {desc[lang][0]}"])
        md.extend([f"\t{ln}" for ln in desc[lang][1].split("\\n")])

    md.extend(["", "### Stage 2"])
    for skill_type, desc in char.liberate_2.items():
        md.extend([f"- {skill_type}: {desc[lang][0]}"])
        md.extend([f"\t{ln}" for ln in desc[lang][1].split("\\n")])

    md.extend(["", "### Stage 3"])
    for skill_type, desc in char.liberate_3.items():
        md.extend([f"- {skill_type}: {desc[lang][0]}"])
        md.extend([f"\t{ln}" for ln in desc[lang][1].split("\\n")])

    return sanitize(md)


# NOTE: Deprecated
def create_skill_level_table(
    char_map: dict[str, CharacterInfo],
    lang: Language,
) -> list[str]:

    def get_row(char: CharacterInfo) -> str:
        icon = f"![[{char.full_name(lang)}.webp]]"
        name = f"[[{char.full_name(lang)}]]"
        sklv = f"{char.skill_lv}" if char.skill_lv else ""
        return f"| {icon:>20} | {name:>20} | {sklv:>2} |"

    def get_header(pos: Position) -> list[str]:
        return [
            "",
            f"### {tl(pos)}",
            "",
            "| icon | name | lv |",
            "| ---- | ---- | -- |",
        ]

    tl = partial(translate, lang=lang)
    logger.debug("Creating skill level table")

    skill_lv_tbl: list[str] = []
    for element in Element:
        skill_lv_tbl.extend(["", f"## {tl(element)}"])
        for position in Position:
            cond = lambda c, e=element, p=position: c.element == e and c.position == p
            skill_lv_tbl.extend(get_header(position))
            skill_lv_tbl.extend(
                [get_row(char) for char in filter(cond, char_map.values())]
            )

    return skill_lv_tbl
