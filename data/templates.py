from functools import partial
from string.templatelib import Template

from character.info_classes import (
    Element,
    Immunity,
    Language,
    Position,
    Tag,
    Usage,
)
from character.translates import translate


def apply_translate(tmpl: Template, lang: Language) -> str:
    tl = partial(translate, lang=lang)

    ret: str = ""
    for item in tmpl:
        if isinstance(item, str):
            ret += item
        elif isinstance(item.value, Element | Position | Immunity | Usage | Tag):
            ret += tl(item.value)
        else:
            raise TypeError(f"Unsupported type {type(item.value)} found")
    return ret


base_template: Template = t"""filters:
  and:
    - file.inFolder("characters")
formulas:
  icon: image(file.name + ".webp")
properties:
  note.is_limited:
    displayName: LTD
  note.cooldown:
    displayName: CD
  note.element:
    displayName: E
  note.immunity:
    displayName: IMU
  note.requirement:
    displayName: REQ
  note.skill_level:
    displayName: LV
views:
  - type: table
    name: query
    filters:
      and:
        - rarity == ["SSR"]
        - immunity.contains("{Immunity.PARALYSIS}")
        - and:
            - leader_tags.contains("{Tag.hp_up}")
            - leader_tags.contains("{Tag.r_dmg_up_light}")
        - or:
            - ability_tags.contains("{Tag.dmg_up}")
            - ability_tags.contains("{Tag.dmg_up_skill}")
            - ability_tags.contains("{Tag.dmg_up_attacker}")
            - ability_tags.contains("{Tag.dmg_up_skill_self}")
            - ability_tags.contains("{Tag.dmg_up_1}")
            - ability_tags.contains("{Tag.dmg_up_2}")
            - ability_tags.contains("{Tag.dmg_up_3}")
            - ability_tags.contains("{Tag.dmg_up_4}")
            - ability_tags.contains("{Tag.dmg_up_5}")
    order:
      - owned
      - skill_level
      - formula.icon
      - file.name
      - element
      - type
      - aliases
      - is_limited
      - cooldown
      - ability_tags
      - immunity
      - requirement
    sort:
      - property: id
        direction: ASC
    rowHeight: tall
"""

dataview_template: Template = t"""
## Query

```dataview
table
	embed(link("icons/" + file.name + ".webp")) as icon,
	alias as "alias",
	element as "ELM",
	type as "POS",
	cooldown as "CD",
	immunity as "IMU",
	ability_tags as "ABL"
from
	"characters"
where
	rarity = "SSR"
	and
	any(contains([leader_tags, ability_tags], "{Tag.dot}"))
flatten
	choice(aliases[0], aliases[0], "\\-") as alias
sort
	release_date
	desc
```

### Basic syntax
```sql
table
	embed(link("icons/" + file.name + ".webp")) as icon,
	alias,
	property_1 as name_1,
	property_2 as name_2
from
	location
where
	conditions
flatten
	choice(aliases[0], aliases[0], file.name) as alias
```

### Conditions
AND
```sql
where
	type = "{Position.OBSTRUCTER}"
	and
	all(contains(ability_tags, ["{Tag.dmg_up}", "{Tag.r_dmg_up}"]))
```

OR
```sql
where
	type = "{Position.SUPPORTER}"
	or
	any(contains([leader_tags, ability_tags], ["{Tag.dmg_up}", "{Tag.r_dmg_up}"]))
```

## List
```dataview
list
	length(rows)
from
	"characters"
where
	any(ability_tags)
flatten
	ability_tags as tags
group by
	tags
sort
	key asc
```
"""
