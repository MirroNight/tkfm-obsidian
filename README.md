
# tkfm-obsidian

This project is a script to build a obsidian vault containing tkfm characters information and icons, in the hope that ic can be used as a searchable database and note taking tools.
Specifically, this tool is aimed to help team building for special purposes.

## Usage

### Quick start

If you're already familier with command line, here's a quick overview:

```sh
python main.py -h
usage: main.py [-h] [-l {TC,SC,EN,JP,KR}] 
               [-o OUTDIR] [-p DIR] [-j JSON] [-L FILE]
               [-v {CRITICAL,FATAL,ERROR,WARN,WARNING,INFO,DEBUG,NOTSET}]
               [--use-pic-id] [--skip-git-update]
               [--skip-copy-icons] [--force-update]

Generates obsidian vault for tkfm characters,make team building and character search easier.
Creates wiki-like character notes, with auto-generatedtags, and easy to mark owned
characters and skill level.

options:
  -h, --help            show this help message and exit
  -l, --language {TC,SC,EN,JP,KR}
                        Prefered language (default: 'TC')
  -o, --output OUTDIR   Output directory (default: 'tkfm')
  -p, --project DIR     Directory for 'tenkaassist' and 'TKFM-Data-Room' (default: 'projects')
  -j, --json JSON       Owned character / skill level '.json' file
  -L, --logfile FILE    Logfile (default: 'process.log')
  -v, --verbosity {NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Log level (default: 'INFO')
  --use-pic-id          Name icons with ID instead of full name
  --skip-git-update
  --skip-copy-icons
  --force-update
```

Processing log is kept in `process.log` under this project's directory.

The output is placed inside `tkfm` directory. You can softlink/symlink it to the place to the place you keep your obsidian vaults.

Inside `tkfm` directory, you will see:

| name               | type  | description                                                                                                                                                              |
| ------------------ | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `How to use`       | .md   | A detail notes about how to use this vault, and some obsidian (markdown) intoduction.                                                                                    |
| `Dataview example` | .md   | A exmaple usage of `dataview` plugin (third party). You can ignore it if you don't want to use it. The built-in **BASE** should be enough for most use cases.            |
| `Character search` | .base | A **BASE** that shows the table of your queried/filtered characters based on their properties.                                                                           |
| `List of tags`     | .md   | List all tags that is used by `leader_tags`, `ability_tags` and `liberate_tags`, grouped by their effects, so you can get an idea which to use while querying/filtering. |
| `characters`       | /     | A directory containing notes (`.md`) of every usable character's basic information.                                                                                      |
| `icons`            | /     | A directory contianing images (`.webp`), which is the icons of every characters (along with their custume icon).                                                         |
| `archive`          | /     | A directory containing recoreds (`.json`) of your ownership data, as and backup, just in case you need it.                                                               |

### Step-by-step guide

1. Install [obsidian](https://obsidian.md/).
2. Clone this repo and go into it:

	```sh
	git clone https://github.com/MirroNight/tkfm-obsidian.git
	cd tkfm_obsidian
	```

3. Make sure you have [`python >= 3.14`](https://www.python.org/downloads/) installed before running next step. Perferably using environment control tool such as [`uv`](https://docs.astral.sh/uv/).

	```sh
	python --version
	```

4. Run `main.py` with your prefered way of runing python.  
	To change the language, output location, please check the `###Options` section.  
	To save/load and update ownership data, please check the `##Ownership data` section.

	```sh
	# raw python
	python main.py
	# with uv
	uv run main.py
	```

5. Move the `tkfm` directory to the place you store all your obsidian vault, and rename it to whatever you like.
6. Inside obsidian, go to `manage vaults` > `open directory as vault` > select the directory.
7. You will see a `How to use` file in the vault, which will guide you through some use cases.
8. The `Character search` (whic is a **BASE**) is used for querying characters, and quick modifying of charactere properties.

> The log can be found at `process.log`.

> [!NOTE]
> **BASE** is a type of database/spreadsheet representation of your notes' properties. It supports filtering and modifying of properties. Which is the function we're taking advantage of in this project.

### Options

| Option              | Value    | Desctiption                                                                                                                       | Default       |
| :------------------ | :------- | :-------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| `-h`                |          | Show help message.                                                                                                                |               |
| `-l`                | `LANG`   | Language (not translated values will default to EN). `LANG` is one of `{TC,SC,EN,JP,KR}`.                                         | `TC`          |
| `-o`                | `OUTDIR` | Output directory.                                                                                                                 | `tkfm`        |
| `-p`                | `DIR`    | Project directory, for keeping `tenkaassist` and `TKFM-Data-Room` data.                                                           | `projects`    |
| `-j`                | `JSON`   | **Optional** json file containing ownership information. See `###Ownership data` section for more informaiton.                    |               |
| `-L`                | `FILE`   | Path to log (text) file. Will create if needed.                                                                                   | `process.log` |
| `-v`                | `LEVEL`  | Log verbosity level. `LEVEL` is one of `{NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL}`                                               | `INFO`        |
| `--use-pic-id`      |          | Use id to name icon files (i.e. `cs10001_0_0.webp`) instead of name (i.e. `Archdemon Ba'al.webp`).                                |               |
| `--skip-git-update` |          | Skip updating `tenkaassist` and `TKFM-Data-Room` data.                                                                            |               |
| `--skip-copy-icons` |          | Skip copying character icons.                                                                                                     |               |
| `--force-update`    |          | Force overwrites of following files when existed: `icons/*`, `Character search`, `Dataview example`, `List of tags`, `How to use` |               |

> [!Caution]
> Log file is a plain text file. This program will only append to it. No check is performed so be careful not to overwrite important file with it.

> [!NOTE]
> Symlink your output directory can keep update easy.
> On linux: `cd <dest_dir>` then `ln -s <path-of-tkfm-obsidian/tkfm>`
> 
> Inside file explorere in obsidian, I recommand you change the sort order to `sort by creation time (old to new)`, since the characters is named by their names. This script creates each character's note in the order of their release date/ID.

## Ownership data

### Enabling BASE

To enable **BASE** functionality, you'll need to enable it with the following steps:

1. Go to `settings`
2. Go to `core plugins`
3. Enable `database`

### How to input ownership data

You might want to enter and save information about characters you owned to help you filter out options while building your teams. This vault offers two properties to do so:

- `owned`: A boolean value. It shows up in **BASE** as a checkbox.
- `skill_level`: A integer value. It shows up in **BASE** as a number (or blank if unset).

It would be a painful work if you need to go through each and every notes to modify the property value. Fortunately, obsidian offers a convenient way of modifying properties across different notes inside a **BASE**:

- You can modify `owned` (boolean) value in a **BASE** by clicking the checkbox, or pressing `enter` while selecting the cell.
- You can modify `skill_level` (integer) value in a **BASE** by selecting the cell (highlighted in purple), typing the number in or `up/down arrow` key to increment/decrement value.
- After editing, you can use `enter` to jump to cell on the right (in editing mode), or `esc` followed by `arrow` to move to cells you like, and use `enter` to go into editing mode.
- Give obsidian some time to update corresponding note's property, do not close obsidian immdediately after editing from **BASE**.

> [!NOTE] 
> While the `enter` and `up/down arrow` editing technique also works inside individual note's property section, it is not particualry useful for our use case.

You can also manually modify the `.json` file in `archive` once you run the script for the second (or more) times. But the it uses internal markers `meta` to note characters instead of `name` or `id`. You'll have to modify this script if you want to have it use `name` or `id` instead.

### Inconsistant ownership

A check is built into the processing of ownership information. And the following cases are consider **inconsistan ownership** and shows as an `WARNING` inside log.

- Property `owned` set to `true` and `skill_level` set to `0`
- Property `owned` set to `false` and `skill_level` set to `non-0`

The reasoning being:

- `unset` and `unset` is considered as "not entered"
- `unset` and `any value` is considered as "entered"
- `true` implies you own the character (which have skill level of at least `1`)
- `false` implies you don't own the character (which skill level should be `0`)

Thus, the `true` and `0`, as well as `false` and `non-0` presents a logical conflict. So is deemed as inconsistant ownership.

## Updating data

### Update character data

To update character data, simply go into this project's dirctory, run the following command, and you're done.

```sh
# shell
python main.py -o <OUTDIR>
# uv
uv run main.py -o <OUTDIR>
```

`OUTDIR` is the path to your vault.

The ownership information is automatically gathered and transfered into new notes. It will also create a new `.json` inside `archive` and dump your ownership information in it as a backup.

### Load ownership data from archive

In case you lost the record of your ownership information somehow, you can load your old ownership information from archive. To do so, simply goes to this project directory and run the python command:

```sh
# shell
python main.py -o <OUTDIR> -j <JSON>
# uv
uv run main.py -o <OUTDIR> -j <JSON>
```

`OUTDIR` is the path to your vault, and `JSON` is the path to the specific `.json` file inside your `archive`.

This will load the ownership information from the `.json` and use it to update the vault. Note that loading from `.json` will not create a new `.json` inside `archive`.

## Sources

- This project: [tkfm-obsidian](https://github.com/MirroNight/tkfm-obsidian.git)
- Basic info/skills/liberate：[TKFM-Data-Room](https://github.com/hinorpio/TKFM-Data-Room.git)
- Icons：[tenkaassist](https://github.com/inittt/tenkaassist.git)
