import json
import os
import sys
import jsonref
import re

PROJECT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
CONFIG_JSON_TARGET = os.path.join(
    PROJECT_DIR, "docs", "components", "config-schema-object.ts"
)
MD_FILE_TARGET = os.path.join(PROJECT_DIR, "docs", "pages", "configuration.mdx")
sys.path.append(PROJECT_DIR)

import src

# ---------------------------------------------------------
# Update the config schema object in the documentation

config_schema_str = json.dumps(src.types.Config.model_json_schema(), indent=4)
dereferenced_config_schema = jsonref.loads(config_schema_str)
with open(CONFIG_JSON_TARGET, "w") as f:
    f.write(
        "/* prettier-ignore */\n" + "const CONFIG_SCHEMA_OBJECT: any = " +
        json.dumps(dereferenced_config_schema, indent=2) +
        ";\n\nexport default CONFIG_SCHEMA_OBJECT;"
    )

# ---------------------------------------------------------
# Update the example files in the documentation

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
