import os
import shutil
import sys
from generate_jsonschema import generate_jsonschema_tsfile
from generate_apiref import generate_module_reference
from utils import replace_json_block_in_file, generate_recursive_help

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_DIR)
import src, cli, run

DOCS_PAGES_PATH = os.path.join(PROJECT_DIR, "docs", "pages")
DOCS_SCHEMA_PATH = os.path.join(PROJECT_DIR, "docs", "components", "schemas")

# API REFERENCE OF CODEBASE

with open(os.path.join(DOCS_PAGES_PATH, "api-reference", "src.md"), "w") as f:
    f.write(generate_module_reference(run))
    f.write("\n\n<br/>\n\n")
    f.write(generate_module_reference(src))

# JSON SCHEMA REFERENCES

for obj, label in [
    (src.types.Config, "config"),
    (src.types.ForeignConfig, "foreign-config"),
    (src.types.State, "state"),
    (src.types.MessageArchiveItem, "message-archive-item"),
]:
    path = os.path.join(DOCS_SCHEMA_PATH, f"{label}-schema.ts")
    with open(path, "w") as f:
        variable_name = f'{label.replace("-", "_").upper()}_SCHEMA'
        f.write(generate_jsonschema_tsfile(obj, variable_name))

# CONFIG TEMPLATE

replace_json_block_in_file(
    os.path.join(PROJECT_DIR, "config", "config.template.json"),
    os.path.join(DOCS_PAGES_PATH, "api-reference", "configuration.mdx"),
    json_block_index=0,
)
replace_json_block_in_file(
    os.path.join(PROJECT_DIR, "config", "config.template.json"),
    os.path.join(DOCS_PAGES_PATH, "interfaces", "configuration.mdx"),
    json_block_index=0,
)

# README
"""with open(os.path.join(DOCS_PAGES_PATH, "index.mdx")) as _f:
    current_docs_landing_page = _f.read()

xs = current_docs_landing_page.split('##')
assert len(xs) >= 2"""

with open(os.path.join(PROJECT_DIR, "README.md")) as _f:
    readme = _f.read()

with open(os.path.join(DOCS_PAGES_PATH, "index.mdx"), "w") as _f:
    _f.write(readme.replace("🌱 ", ""))

# CLI COMMANDS

with open(os.path.join(DOCS_PAGES_PATH, "api-reference", "cli.md"), "w") as f:
    f.write("# CLI Reference\n\n")
    f.write(generate_recursive_help(cli.cli))

# CODE OF CONDUCT

shutil.copyfile(
    os.path.join(PROJECT_DIR, "CODE_OF_CONDUCT.md"),
    os.path.join(DOCS_PAGES_PATH, "contributing", "code-of-conduct.mdx"),
)
shutil.copyfile(
    os.path.join(PROJECT_DIR, "CONTRIBUTING.md"),
    os.path.join(DOCS_PAGES_PATH, "contributing", "contributing.mdx"),
)
