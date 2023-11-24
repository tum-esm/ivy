from __future__ import annotations
import os
import sys
import shutil

PROJECT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(PROJECT_DIR)
import src

INDEX_SRC = os.path.join(PROJECT_DIR, "README.md")
INDEX_DST = os.path.join(PROJECT_DIR, "docs", "pages", "index.md")
API_DST = os.path.join(PROJECT_DIR, "docs", "pages", "api-reference.md")

# copy index file to docs folder

with open(INDEX_SRC, "r") as f:
    index_file_content = f.read()

with open(INDEX_DST, "w") as f:
    f.write("\n".join([
        "---",
        "title: Introduction",
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
    if basename.startswith("__"):
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
            target_file = f"{OUTPUT_DIR}/{relative_path[:-3]}.md"
            file_content_lines = [
                l for l in file_content.split("\n") if
                not l.startswith(f'<a id="{relative_path[:-3]}') and len(l) > 0
            ]
            file_content_lines = [
                "---",
                f"title: {basename}",
                "---",
                "",
                f"# `{relative_path}`",
            ] + file_content_lines[1 :]
            with open(target_file, "w") as f2:
                f2.write("\n".join(file_content_lines))


render_module("run.py")
render_module("src")
