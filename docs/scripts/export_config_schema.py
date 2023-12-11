from typing import Any
import json
import os
import sys
import jsonref
import re
import pydantic

PROJECT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
CONFIG_JSON_TARGET = os.path.join(
    PROJECT_DIR, "docs", "components", "config-schema-object.ts"
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


def generate_readable_schema(o: Any) -> str:
    # remove $ref usages
    schema_without_refs = jsonref.loads(
        json.dumps(o.model_json_schema(by_alias=False))
    )

    # remove $defs section
    schema_without_defs = json.loads(
        jsonref.dumps(schema_without_refs, indent=4)
    )
    del schema_without_defs["$defs"]

    # convert weird "allOf" wrapping to normal wrapping
    schema_without_allofs = _remove_allof_wrapping(schema_without_defs)

    return json.dumps(schema_without_allofs, indent=4)


# ---------------------------------------------------------
# Update the config schema object in the documentation

print(f"Exporting config schema object to {CONFIG_JSON_TARGET}")
with open(CONFIG_JSON_TARGET, "w") as f:
    f.write(
        "/* prettier-ignore */\n" + "const CONFIG_SCHEMA_OBJECT: any = " +
        generate_readable_schema(src.types.Config) +
        ";\n\nexport default CONFIG_SCHEMA_OBJECT;"
    )

# ---------------------------------------------------------
# Update the example files in the documentation

print(f"Updating example files in {MD_FILE_TARGET}")

with open(MD_FILE_TARGET) as f:
    md_file_content = f.read()

example_file_blocks = re.findall(
    r"Example File\n\n```[\s\S]*?```", md_file_content
)
assert len(example_file_blocks) == 1

with open(os.path.join(PROJECT_DIR, "config", "config.template.json")) as f:
    config_template_content = f.read()

md_file_content = md_file_content.replace(
    example_file_blocks[0],
    f"Example File\n\n```json\n{config_template_content.strip()}\n```",
)

with open(MD_FILE_TARGET, "w") as f:
    f.write(md_file_content)
