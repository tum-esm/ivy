from __future__ import annotations
import os
import re
import sys
import shutil
import json
from typing import Any
import jsonref

PROJECT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(PROJECT_DIR)
import src

INDEX_SRC = os.path.join(PROJECT_DIR, "README.md")
INDEX_DST = os.path.join(PROJECT_DIR, "docs", "pages", "index.md")
API_DST = os.path.join(PROJECT_DIR, "docs", "pages", "api-reference.md")

# ---------------------------------------------------------
# copy index file to docs folder

with open(INDEX_SRC, "r") as f:
    index_file_content = f.read()

with open(INDEX_DST, "w") as f:
    f.write("\n".join([
        "---",
        "title: Overview",
        "---",
        "",
        "",
    ]))
    f.write(index_file_content)

# generate automatic API reference and prettify output

SRC_DIR = os.path.join(PROJECT_DIR, "src")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "docs", "pages", "api-reference")

if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
    os.mkdir(OUTPUT_DIR)


def render_module(relative_path: str) -> None:
    basename = os.path.basename(relative_path)
    if basename.startswith("__") and basename != "__init__.py":
        return
    absolute_path = os.path.join(PROJECT_DIR, relative_path)
    if os.path.isdir(absolute_path):
        os.mkdir(os.path.join(OUTPUT_DIR, relative_path))
        for f1 in os.listdir(absolute_path):
            render_module(os.path.join(relative_path, f1))

    if os.path.isfile(absolute_path):
        if basename.endswith(".py"):
            print(f"Rendering {relative_path}")
            file_content = src.utils.functions.run_shell_command(
                f"pydoc-markdown --package {relative_path[:-3]}"
            ).strip("\n\t ")
            target_file = f"{OUTPUT_DIR}/{relative_path.replace('__init__.py', 'init.py')[:-3]}.md"
            file_content_lines = [
                l for l in file_content.split("\n")
                if not l.startswith(f'<a id="{relative_path[:-3]}')
            ]
            file_content_lines = [
                "---",
                f"title: {basename}",
                "---",
                "",
                f"# `{relative_path.replace('/', '.')[:-3]}`\n",
            ] + file_content_lines[3 :]
            with open(target_file, "w") as f2:
                f2.write("\n".join(file_content_lines))


render_module("run.py")
render_module("src")

# ---------------------------------------------------------
# Copy example config file to docs page

CONFIG_TEMPLATE_FILE_TARGET = os.path.join(
    PROJECT_DIR, "docs", "pages", "file-interfaces", "configuration.mdx"
)

print(f"Updating config example files in {CONFIG_TEMPLATE_FILE_TARGET}")

with open(CONFIG_TEMPLATE_FILE_TARGET) as f:
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

with open(CONFIG_TEMPLATE_FILE_TARGET, "w") as f:
    f.write(md_file_content)

# ---------------------------------------------------------
# export json schemas


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
