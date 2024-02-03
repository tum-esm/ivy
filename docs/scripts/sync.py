import os
import sys
from generate_jsonschema import generate_jsonschema_tsfile
from generate_apiref import generate_module_reference

PROJECT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(PROJECT_DIR)
import src

DOCS_PAGES_PATH = os.path.join(PROJECT_DIR, "docs", "pages", "latest")
DOCS_COMPONENTS_PATH = os.path.join(PROJECT_DIR, "docs", "components", "latest")

# API REFERENCE OF CODEBASE

with open(os.path.join(DOCS_PAGES_PATH, "api-reference", "src.md"), "w") as f:
    f.write("# API Reference of the `src` Module\n\n")
    f.write(generate_module_reference(src))

# JSON SCHEMA REFERENCES

for obj, label in [
    (src.types.Config, "config"),
    (src.types.ForeignConfig, "foreign-config"),
    (src.types.State, "state"),
    (src.types.MessageArchiveItem, "message-archive-item"),
]:
    path = os.path.join(DOCS_COMPONENTS_PATH, f"{label}-schema.ts")
    with open(path, "w") as f:
        variable_name = f'{label.replace("-", "_").upper()}_SCHEMA'
        f.write(generate_jsonschema_tsfile(obj, variable_name))

# README

# TODO
