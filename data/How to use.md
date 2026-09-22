
## Query with BASE

**BASE** is a built-in tool to query notes inside an obsidian vault, and reperesents the result in a table. It also allowed you to modify **note properties** from the table. You can move the base to directory that is relavent to its filter, or insert it directly into other notes.

### Enabling BASE

To enable **BASE** functionality, you'll need to enable it with the following steps:

1. Go to `settings`
2. Go to `core plugins`
3. Enable `database`

After which, you can click on the [[Character search.base]], which is the example included to demonstrate how to filter, sort, choose diaplayed properties, etc. Play around the example included to see who it works and can do.

### Views

Views are essentially the table you see when you open the **BASE**, it funtions likes tables in excel.  

- On the top left corner of the **BASE**, you will see the "query" button, which is the name of current view.
- Clicking on it will show you all the views you have in this **BASE**. You can add new view by clicking the `add new view`, or modify current view information by clicking `>`. You can then click on `⋮` to copy select view (very handy).

You can also paste the result to clipboard or dump the result as `.csv` file, by clicking the **N results** next to the **view name**.

### Properties

On the top right of the **BASE**, you will see **properties**. It allows you to:

- Choose which properties is displayed
- Change the displayed of the properties (i.e. `is_limited` is displayed as `LTD`)
- Applies functions to properties to do change how it behaves (i.e. the `icons` you see is done with `image(file.name + ".webp")`)

### Filtering

On the top right of the **BASE** page, you will see **filter**. Inside it, there's two section, **global view** and **this view**. (see [[#Views]])

- **Global view** contains filter applies accros all views.
- **This view** contians filters applies only to current view.

For our purpose, the **global view** will set to `files in folder character`. In **this view** you can set up filtering conditions for **this view**. The filtering follows simple logics and grouping, which should be fairly easy to get your hands on.  

### Sorting

By clicking on individual property label in the **BASE** view, you can change between:

- Sort by the property (descend)
- Sort by the property (ascend)
- Unsorted (not sort by this property)

If you want to primary sort with "type" then by "element", you need to do it in reverse order:

1. Click on `type` to sort by `type`
2. Click on `E` to sort by `element`

### Insert BASE into a note

To insert a **BASE** into your note, put the following inside:

```md
![[base_name]]
```

For example, to inseart `Character search`, you need:

```md
![[Character search.base]]
```

To specify specific **view** from the **BASE**, use:

```md
![[base_name#view_name]]
```

For example, to inseart `query` from `Character search`, you need:

```md
![[Character search.base#query]]
```

## Query with dataview

For how to use **dataview** within a note, please check [[Dataview example]] for examples. Most actions can be done with **BASE** so **dataview** is less engouraged as it requires a thrid party plugin. The common use case is when you only need a list there, or when you don't wnat to modify any of the view.
 
### Enabling dataview

Before you start using **dataview**, you need to follow the steps to enable **dataview**:

1. Open `settings`
2. Go to `third party plugins`
3. Click `view` in the `community plugins`
4. Search for `dataview`
5. Click install and close the window
6. Scroll down and enable `dataview`

## Ownership data

To modify your ownership information, please first read [[#Enabling BASE]] and enable BASE plugin.

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

To update character data, simply go into `tkfm-obsidian` project dirctory, run the following command, and you're done.

```sh
# shell
python main.py -o <OUTDIR>
# uv
uv run main.py -o <OUTDIR>
```

`OUTDIR` is the path to your vault.

The ownership information is automatically gathered and transfered into new notes. It will also create a new `.json` inside `archive` and dump your ownership information in it as a backup.

### Load ownership data from archive

In case you lost the record of your ownership information somehow, you can load your old ownership information from archive. To do so, simply goes to the `tkfm-obsidian` project directory and run the python command:

```sh
# shell
python main.py -o <OUTDIR> -j <JSON>
# uv
uv run main.py -o <OUTDIR> -j <JSON>
```

`OUTDIR` is the path to your vault, and `JSON` is the path to the specific `.json` file inside your `archive`.

This will load the ownership information from the `.json` and use it to update the vault. Note that loading from `.json` will not create a new `.json` inside `archive`.

----
 
> [!NOTE] Source
> - This project: [tkfm-obsidian](https://github.com/MirroNight/tkfm-obsidian.git)
> - Basic info：[TKFM-Data-Room](https://github.com/hinorpio/TKFM-Data-Room.git) `/static/data/unit/general/`
> - Skills：[TKFM-Data-Room](https://github.com/hinorpio/TKFM-Data-Room.git) `/static/data/unit/skillset/`
> - Liberate：[TKFM-Data-Room](https://github.com/hinorpio/TKFM-Data-Room.git) `/static/data/unit/liberate/`
> - Icons：[tenkaassist](https://github.com/inittt/tenkaassist.git) `/images/characters/`
