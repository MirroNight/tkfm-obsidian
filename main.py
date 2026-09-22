import argparse
import datetime as dt
import logging
from functools import partial
from pathlib import Path
# from tkinter import filedialog

from character.formatting import (
    as_md,
    build_character_map,
    collect_owned,
    copy_icons,
    load_owned,
    save_owned,
)
from character.info_classes import CharacterInfo, Element, Language, Rarity
from character.translates import translate
from data.render import get_base_example, get_dataview_example, get_tag_list
from data.update_data import Project, pull_git_repositories


# NOTE: Basic parameters

PROG_DESC = (
    "Generates obsidian vault for tkfm characters,"
    "make team building and character search easier. "
    "Creates wiki-like character notes, with auto-generated"
    "tags, and easy to mark owned characters and skill level."
)

# directory containing TKFM-Data-Room and tankaassist project
PROJECT_DIR = Path("projects/")
# output
OUTPUT_DIR = Path("tkfm/")
# log
LOGFILE = Path("process.log")
# language
LANGUAGE = Language.TC
# ownership file
OWNERSHIP_FILE = None  # Path("archive/...")
# = Path(_) if (
#     _ := filedialog.askopenfilename(
#         title="select a json file",
#         defaultextension=".json",
#         filetypes=[("Archive file", "*.json")],
#         initialdir=OUTPUT_DIR / "archive",
#     )
# ) else None


logger = logging.getLogger(__name__)
local_tz = dt.datetime.now().astimezone().tzinfo


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=PROG_DESC)
    parser.add_argument(
        "-l",
        "--language",
        action="store",
        type=lambda k: Language[k.upper()],
        choices=[_.name for _ in Language],
        default=LANGUAGE.name,
        help=f"Prefered language (default: '{LANGUAGE.name}')",
    )
    parser.add_argument(
        "-o",
        "--output",
        action="store",
        metavar="OUTDIR",
        default=OUTPUT_DIR,
        type=Path,
        help=f"Output directory (default: '{OUTPUT_DIR}')",
    )
    parser.add_argument(
        "-p",
        "--project",
        action="store",
        metavar="DIR",
        type=Path,
        default=PROJECT_DIR,
        help=f"Directory for 'tenkaassist' and 'TKFM-Data-Room' (default: '{PROJECT_DIR}')",
    )
    parser.add_argument(
        "-j",
        "--json",
        action="store",
        metavar="JSON",
        type=Path,
        help="Owned character / skill level '.json' file",
    )
    parser.add_argument(
        "-L",
        "--logfile",
        action="store",
        metavar="FILE",
        type=Path,
        default=LOGFILE,
        help=f"Logfile (default: '{LOGFILE}')",
    )
    parser.add_argument(
        "-v",
        "--verbosity",
        action="store",
        metavar="{NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL}",
        type=lambda v: logging.getLevelNamesMapping()[v.upper()],
        default=logging.INFO,
        choices=list(logging.getLevelNamesMapping()),
        help="Log level (default: 'INFO')",
    )
    parser.add_argument(
        "--use-pic-id",
        action="store_true",
        help="Name icons with ID instead of full name",
    )
    parser.add_argument("--skip-git-update", action="store_true")
    parser.add_argument("--skip-copy-icons", action="store_true")
    parser.add_argument("--force-update", action="store_true")

    return parser.parse_args()


def main(
    output_dir: Path,
    project_dir: Path,
    lang: Language,
    ownership_file: Path | None = None,
    use_pic_id: bool = False,
    verbosity: logging._Level = logging.INFO,
    logfile: Path | None = None,
    skip_git_update: bool = False,
    skip_copy_icons: bool = False,
    force_update: bool = False,
) -> int:
    # initialize utils
    logging.basicConfig(filename=logfile, level=verbosity)
    tl = partial(translate, lang=lang)
    now = dt.datetime.now(tz=local_tz)

    tenkaassist = Project(
        name="tenkaassist",
        url="https://github.com/inittt/tenkaassist.git",
        path=(project_dir / "tenkaassist"),
    )
    tkfm_data_room = Project(
        name="TKFM-Data-Room",
        url="https://github.com/hinorpio/TKFM-Data-Room.git",
        path=(project_dir / "TKFM-Data-Room"),
    )

    logger.info(
        f"Time: {now}\n"
        "Parameters:\n"
        f"language:  {lang.name}\n"
        f"output_dir:  {output_dir}\n"
        f"tenkaassist:  {tenkaassist.path} | {tenkaassist.url}\n"
        f"TKFM-Data-Room:  {tkfm_data_room.path} | {tkfm_data_room.url}\n"
        f"ownership_file:  {ownership_file}\n"
        f"use_pic_id:  {use_pic_id}\n"
        "==== Start processing ===="
    )

    # prepare direcotries
    if not output_dir.exists():
        logger.debug(f"'{output_dir}' not found")
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"'{output_dir}' created")

    characters_dir = output_dir / "characters"
    if not characters_dir.exists():
        logger.debug(f"'{characters_dir}' not found")
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"'{characters_dir}' created")

    for rarity in Rarity:
        rarity_dir = characters_dir / rarity.name
        if not rarity_dir.exists():
            logger.debug(f"'{rarity_dir}' not found")
            rarity_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"'{rarity_dir}' created")

        for element in Element:
            element_dir = rarity_dir / f"{tl(element)}"
            if not element_dir.exists():
                logger.debug(f"'{element_dir}' not found")
                element_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"'{element_dir}' created")

    archive_dir = output_dir / "archive"
    if not archive_dir.exists():
        logger.debug(f"'{archive_dir}' not found")
        archive_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"'{archive_dir}' created")

    # update all required repos
    if not skip_git_update:
        logger.info(f"Pulling '{tenkaassist.name}', url:  '{tenkaassist.url}'")
        pull_git_repositories(tenkaassist)
        logger.info(f"Pulling '{tkfm_data_room.name}', url: '{tkfm_data_room.url}'")
        pull_git_repositories(tkfm_data_room)

    # extract info
    logger.info("Start extracting character information")
    character_map: dict[str, CharacterInfo] = build_character_map(tkfm_data_room.path)

    # load owned/skill_lv from existing files
    if ownership_file and ownership_file.exists():
        character_map = load_owned(ownership_file, character_map)
        logger.info(f"Ownership loaded from '{ownership_file}'")
    else:
        logger.info("Collecting ownership from vault")
        character_map: dict[str, CharacterInfo] = collect_owned(
            character_map, characters_dir, lang
        )
        json_file = archive_dir / f"{now.strftime('%Y-%m-%d-%H-%M-%S')}.json"
        save_owned(json_file, character_map, lang)
        logger.info(f"Ownership saved to '{json_file}'")

    # copy and rename icons
    if not skip_copy_icons:
        copy_icons(
            tenkaassist.path,
            output_dir,
            lang,
            character_map,
            use_pic_id,
            forec_update=force_update,
        )

    # create output files
    logger.info("Prepareing files")
    for char in character_map.values():
        logger.info(f"Formatting '{char.full_name(lang)}'")
        md_string = "\n".join(as_md(char, character_map, lang, use_pic_id))

        outfile = (
            characters_dir
            / char.rarity.name
            / tl(char.element)
            / f"{char.full_name(lang)}.md"
        )
        with open(outfile, "w") as fd:
            fd.write(md_string)
        logger.info(f"File saved '{outfile}'")

    # create "How to use"
    how_to_use_file = output_dir / "How to use.md"
    if not how_to_use_file.exists() or force_update:
        Path("How to use.md").copy(how_to_use_file)

    # create "Character search base"
    base_example_file = output_dir / "Character search.base"
    if not base_example_file.exists() or force_update:
        with open(base_example_file, "w") as fd:
            fd.write(get_base_example(lang))

    # create "Character dataview"
    dataview_example_file = output_dir / "Dataview example.md"
    if not dataview_example_file.exists() or force_update:
        with open(dataview_example_file, "w") as fd:
            fd.write(get_dataview_example(lang))

    # create "List of tags"
    tag_list_file = output_dir / "List of tags.md"
    if not tag_list_file.exists() or force_update:
        with open(tag_list_file, "w") as fd:
            fd.write(get_tag_list(lang))

    return 0


if __name__ == "__main__":
    args = get_args()

    main(
        lang=args.language,
        output_dir=args.output,
        project_dir=args.project,
        ownership_file=args.json,
        logfile=args.logfile,
        verbosity=args.verbosity,
        use_pic_id=args.use_pic_id,
        skip_git_update=args.skip_git_update,
        skip_copy_icons=args.skip_copy_icons,
        force_update=args.force_update,
    )
