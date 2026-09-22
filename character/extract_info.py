import logging
from collections.abc import Iterable
from dataclasses import asdict
from enum import Enum
from functools import partial
from io import TextIOWrapper
from pathlib import Path
from re import findall, search
from re import match as re_match
from typing import Any

from .auto_tag import auto_tag
from .info_classes import (
    CharacterInfo,
    Element,
    Immunity,
    Language,
    Position,
    Rarity,
)
from .tag_overwrite import tag_overwrite

logger = logging.getLogger(__name__)


# for matching attr
def match_until(fd: TextIOWrapper, pattern: str) -> str:
    for line in fd:
        if m := re_match(pattern, line.strip()):
            try:
                return m.group(1)
            except IndexError:
                return m.group(0)
    return ""


def get_enum_attr(
    fd: TextIOWrapper, attr_cls: type[Rarity | Element | Position]
) -> Any:
    if m := match_until(
        fd, rf"{attr_cls.__name__.lower()}: {attr_cls.__name__.capitalize()}\.(.*),"
    ):
        try:
            return attr_cls[m]
        except KeyError:
            raise ValueError(f"'{m}' is not a valid {attr_cls.__name__}")
    raise ValueError(f"No {attr_cls.__name__} found")


def get_general_info(file: Path) -> dict[str, Any]:
    # extract general info from character_info_file

    def get_info_w_lang(
        fd: TextIOWrapper, attr: str, pattern: str
    ) -> dict[Language, str]:
        _ = match_until(fd, rf"{attr}: {{")
        attr_d = {}
        for line, language in zip(fd, Language):
            if m := search(pattern, line.strip()):
                attr_d[language] = m.group(1)
            else:
                attr_d[language] = ""
        return attr_d

    def get_id(fd: TextIOWrapper) -> int:
        return int(match_until(fd, r'ID: "([0-9]+)",'))

    def get_prefix(fd: TextIOWrapper) -> dict[Language, str]:
        pref = get_info_w_lang(fd, "prefix", r'"(.*)",?')
        return {lang: pref[lang] for lang in Language}

    def get_name(fd: TextIOWrapper) -> dict[Language, str]:
        name = get_info_w_lang(fd, "name", r'"(.*)",?')
        return {lang: name[lang] for lang in Language}

    def get_abbrv(fd: TextIOWrapper) -> dict[Language, list[str]]:
        abbrvs = get_info_w_lang(fd, "abbreviation", r": \[ (.*?) \],")
        return {lang: findall(r'"(.*?)",', abbrvs[lang]) for lang in Language}

    def get_is_limited(fd: TextIOWrapper) -> bool:
        m = match_until(fd, r"isLimited: (.*),")
        return m == "true"

    def get_other_version(fd: TextIOWrapper) -> list[str]:
        m = match_until(fd, r"otherVersion: \[ (.*) \],")
        return findall(r"UnitCode\.(\w*)", m)

    info_extraction_map = {
        "id": get_id,
        "meta": partial(match_until, pattern=r'metaCode: "(.*)",?'),
        "prefix": get_prefix,
        "name": get_name,
        "abbreviation": get_abbrv,
        "background": partial(get_info_w_lang, attr="background", pattern=r"`(.*?)`,?"),
        "rarity": partial(get_enum_attr, attr_cls=Rarity),
        "element": partial(get_enum_attr, attr_cls=Element),
        "position": partial(get_enum_attr, attr_cls=Position),
        "is_limited": get_is_limited,
        "release_date": partial(match_until, pattern=r'releaseDate: "(.*)",?'),
        "other_version": get_other_version,
    }

    general_d = None
    with open(file, "r") as fd:
        general_d = {attr: fn(fd) for attr, fn in info_extraction_map.items()}

    return general_d


def get_skill_info(file: Path) -> dict[str, dict[Language, tuple[str, str]]]:
    # extract info from character_skill_file
    # -> {skill_type: {language: (name, desc)}}
    def get_skill_in_lang(
        fd: TextIOWrapper, skill_types: Iterable[str], lang: Language
    ) -> dict[str, tuple[str, str]]:
        # -> {skill_type: (name, desc)}
        skill_set = {}
        _ = match_until(fd, rf"\[Locale\.{lang.name.lower()}\]: {{")
        for skill_type in skill_types:
            _ = match_until(fd, rf"\[SkillType\.{skill_type.upper()}\]: {{")
            skill_set[skill_type] = (
                match_until(fd, r"name: `(.*?)`,"),
                # load stored tags
                match_until(fd, r"description: `(.*?)`"),
            )
        return skill_set

    skill_d: dict[str, Any] = {
        "skill_s": {},
        "attack": {},
        "leader": {},
        "passive_1": {},
        "passive_2": {},
        "passive_3": {},
        "general_1": {},
        "general_2": {},
    }

    with open(file, "r") as fd:
        _ = match_until(fd, r"skill: {")
        for lang in Language:
            for skill_type, skill in get_skill_in_lang(
                fd, skill_d.keys(), lang
            ).items():
                skill_d[skill_type][lang] = skill

    skill_d["immunity"] = [
        debuff
        for debuff in Immunity
        if debuff.name.title() in skill_d["general_2"][Language.EN][1]
    ]

    if m := findall(r"CD\s?[:：]\s{0,2}(\d+)", skill_d["skill_s"][Language.TC][1]):
        cds = m
    elif m := search(
        r"CD\s?[:：]\s{0,2}\[((?:\d+/?)+)\]", skill_d["skill_s"][Language.TC][1]
    ):
        cds = m.group(1).split("/")
    else:
        cds = []

    skill_d["cooldown"] = sorted({int(cd) for cd in cds})

    return skill_d


def get_liberate_info(
    file: Path,
) -> dict[str, dict[str, dict[Language, tuple[str, str]]]]:
    # extract liberate info from character_liberate_file
    # -> {liberation_stage: {skill_type: {language: (name, desc)}}}

    def get_liberate_stage(
        fd: TextIOWrapper,
    ) -> dict[str, dict[Language, tuple[str, str]]]:
        # -> {skill_type: {language: (name, desc)}
        stage = {}
        lang = Language.TC
        while marker := match_until(
            fd, r"\[((?:LiberationStage|Locale|SkillType)\..*?)\]: ?{"
        ):
            if not marker:
                break
            marker_type, value = marker.split(".")
            if marker_type == "LiberationStage":
                break
            if marker_type == "Locale":
                lang = Language[value.upper()]
                continue
            if re_match(r"SKILL_\d", value):
                continue

            skill_type = value.lower()
            if skill_type in stage:
                stage[value.lower()][lang] = (
                    match_until(fd, r"name: `(.*?)`,"),
                    match_until(fd, r"description: `(.*?)`"),
                )
            else:
                stage[value.lower()] = {
                    lang: (
                        match_until(fd, r"name: `(.*?)`,"),
                        match_until(fd, r"description: `(.*?)`"),
                    )
                }
        return stage

    liberate_d: dict[str, dict[str, dict[Language, tuple[str, str]]]] = {
        "liberate_1": {},
        "liberate_2": {},
        "liberate_3": {},
    }

    if not file.exists():
        return liberate_d
    with open(file, "r") as fd:
        _ = match_until(fd, r"\[LiberationStage\..*?\]: ?{")
        liberate_d = {
            "liberate_1": get_liberate_stage(fd),
            "liberate_2": get_liberate_stage(fd),
            "liberate_3": get_liberate_stage(fd),
        }
    return liberate_d


def get_existed_tags(meta: str) -> dict[str, Any]:
    tags = {
        "requirement": {},
        "usages": [],  # usages
        "l_tags": set(),  # for leader
        "s_tags": set(),  # not leader
        "x_tags": set(),  # Liberate tags
    }

    if not (existing_tags := tag_overwrite.get(meta)):
        return tags

    for key, value in tags.items():
        tags[key] = existing_tags.get(key, value)

    return tags


def get_owned_info(file: Path) -> tuple[bool | None, int | None]:
    if not file.exists():
        return (None, None)

    with open(file, "r") as fd:
        owned = match_until(fd, r"owned: (.*)").lower()
        skill_lv = match_until(fd, r"skill_level: [+-]?(\d+)}")

    return (
        True if owned == "true" else False if owned == "false" else None,
        int(skill_lv) if skill_lv else None,
    )


def extract_character_info(
    character_info_file: Path,
    character_skill_file: Path,
    character_liberate_file: Path,
) -> CharacterInfo:
    # populates generic info
    logger.debug(f"Extracting from '{character_info_file.name}'")
    general_info: dict[str, Any] = get_general_info(character_info_file)

    # populates skill info
    # -> {skill_type: {language: (name, desc)}}
    logger.debug(f"Extracting from '{character_skill_file.name}'")
    skill_info: dict[str, dict[Language, tuple[str, str]]] = get_skill_info(
        character_skill_file
    )

    # process liberate info when possible
    # -> {liberation_stage: {skill_type: {language: (name, desc)}}}
    logger.debug(f"Extracting from '{character_liberate_file.name}'")
    liberate_info: dict[str, dict[str, dict[Language, tuple[str, str]]]] = (
        get_liberate_info(character_liberate_file)
    )

    # apply existed tags
    logger.debug("Load tag overwrite")
    tags: dict[str, Any] = get_existed_tags(general_info["meta"])

    character_info: dict[str, Any] = general_info | skill_info | liberate_info | tags
    return auto_tag(CharacterInfo(**character_info))


def _main():
    def enum_dict_factory(data):
        def convert(obj):
            if isinstance(obj, Enum):
                return obj.name.lower()
            elif isinstance(obj, dict):
                return {convert(k): convert(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple, set)):
                return [convert(item) for item in obj]
            return obj

        return {k: convert(v) for k, v in data}

    filename: str = "SSR-001"
    base_path: Path = Path("~/projects/TKFM-Data-Room/static/data/unit/").expanduser()
    path_general: Path = base_path / "general" / f"{filename}.ts"
    path_skillset: Path = base_path / "skillset" / f"{filename}.ts"
    path_liberate: Path = base_path / "liberate" / f"{filename}.ts"

    character = extract_character_info(path_general, path_skillset, path_liberate)

    """
    import json
    print(
        json.dumps(
            asdict(character, dict_factory=enum_dict_factory),
            indent=2,
            ensure_ascii=False,
        )
    )
    """

    import yaml

    print(
        yaml.dump(
            data=asdict(character, dict_factory=enum_dict_factory),
            indent=2,
            allow_unicode=True,
            # ensure_ascii=False,
            sort_keys=False,
        )
    )


if __name__ == "__main__":
    _main()
