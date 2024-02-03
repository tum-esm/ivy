import os
import sys
from generate_apiref import generate_module_reference

PROJECT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(PROJECT_DIR)

import src

markdown_content = generate_module_reference(src)
with open(
    os.path.join(PROJECT_DIR, "docs", "pages", "api-reference", "src.md"), "w"
) as f:
    f.write("# API Reference of the `src` Module\n\n")
    f.write(markdown_content)
