from typing import Any
import json
import os
import sys
import jsonref

PROJECT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
MD_FILE_TARGET = os.path.join(
    PROJECT_DIR, "docs", "pages", "guides", "configuration.mdx"
)
sys.path.append(PROJECT_DIR)

import src


def _remove_allof_wrapping(o: dict[str, Any]) -> dict[str, Any]:
    if "properties" in o.keys():
        return {
            **o,
            "properties": {
                k: _remove_allof_wrapping(v)
                for k, v in o["properties"].items()
            },
        }
    elif "allOf" in o.keys():
        assert len(o["allOf"]) == 1
        return {
            **{k: v
               for k, v in o.items() if k != "allOf"},
            **o["allOf"][0],
        }
    else:
        return o


def export_schema(src_object: Any, dst_filepath: str, label: str) -> None:
    print(f"Exporting schema object to {dst_filepath}")

    # remove $ref usages
    schema_without_refs = jsonref.loads(
        json.dumps(src_object.model_json_schema(by_alias=False))
    )

    # remove $defs section
    schema_without_defs = json.loads(
        jsonref.dumps(schema_without_refs, indent=4)
    )
    if "$defs" in schema_without_defs.keys():
        del schema_without_defs["$defs"]

    # convert weird "allOf" wrapping to normal wrapping
    schema_without_allofs = _remove_allof_wrapping(schema_without_defs)

    # write out file
    with open(dst_filepath, "w") as f:
        f.write(
            f"/* prettier-ignore */\nconst {label}: any = " +
            json.dumps(schema_without_allofs, indent=4) +
            f";\n\nexport default {label};"
        )


# ---------------------------------------------------------
# Update the config schema object in the documentation

export_schema(
    src.types.Config,
    os.path.join(PROJECT_DIR, "docs", "components", "config-schema.ts"),
    "CONFIG_SCHEMA",
)
export_schema(
    src.types.ForeignConfig,
    os.path.join(PROJECT_DIR, "docs", "components", "foreign-config-schema.ts"),
    "FOREIGN_CONFIG_SCHEMA",
)
export_schema(
    src.types.State,
    os.path.join(PROJECT_DIR, "docs", "components", "state-schema.ts"),
    "STATE_SCHEMA",
)
export_schema(
    src.types.MessageArchiveItem,
    os.path.join(
        PROJECT_DIR, "docs", "components", "message-archive-item-schema.ts"
    ),
    "MESSAGE_ARCHIVE_ITEM_SCHEMA",
)
