from .info_classes import Language, Tag, Usage

tag_overwrite: dict[str, dict[str, dict[Language, str] | list[Usage] | list[Tag]]] = {
    # "meta": {
    #     "requirement": {},  # Language: str
    #     "usages": [],  # Usage
    #     "l_tags": [],  # Tag
    #     "s_tags": [],  # Tag
    #     "x_tags": [],  # Tag
    # }
}
