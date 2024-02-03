import os
import sys
from generate_jsonschema import generate_jsonschema_tsfile
from generate_apiref import generate_module_reference

PROJECT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(PROJECT_DIR)
import src

docs_version = "v" + ".".join(src.constants.VERSION.split(".")[: 2])
"""Is equal to `v$MAJOR.$MINOR`. Patch version should just replace their predecessors, hence not require a separate documentation version."""

DOCS_PAGES_PATH = os.path.join(PROJECT_DIR, "docs", "pages", docs_version)
DOCS_COMPONENTS_PATH = os.path.join(
    PROJECT_DIR, "docs", "components", docs_version
)
print(f"Syncing documentation for version {docs_version}")

# API REFERENCE OF CODEBASE

with open(os.path.join(DOCS_PAGES_PATH, "api-reference", "src.md"), "w") as f:
    f.write("# API Reference of the `src` Module\n\n")
    f.write(generate_module_reference(src))

# JSON SCHEMA REFERENCES

for obj, label in [
    (src.types.Config, "config"),
    (src.types.ForeignConfig, "foreign-config"),
    (src.types.State, "state-schema"),
    (src.types.MessageArchiveItem, "message-archive-item"),
]:
    path = os.path.join(DOCS_COMPONENTS_PATH, f"{label}-schema.ts")
    with open(path, "w") as f:
        variable_name = f'{label.replace("-", "_").upper()}_SCHEMA'
        f.write(generate_jsonschema_tsfile(obj, variable_name))

# README

# TODO
