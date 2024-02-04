from typing import Optional
import re
import click


def replace_json_block_in_file(
    json_src_file_path: str,
    mdx_file_path: str,
    json_block_index: int,
) -> None:

    with open(json_src_file_path) as f:
        json_template = f.read()

    with open(mdx_file_path) as f:
        mdx_page = f.read()

    matches = list(
        re.finditer(
            r'```json\n(.|\n)*\n```\n', mdx_page, re.MULTILINE & re.DOTALL
        )
    )
    assert len(
        matches
    ) >= json_block_index + 1, f"Did not find enough one JSON blocks in mdx page. Matches = {matches}"

    with open(mdx_file_path, "w") as f:
        f.write(
            mdx_page.replace(
                matches[0].group(0),
                f"```json\n{json_template}\n```\n",
            )
        )


# credits to https://stackoverflow.com/a/58018765/8255842


def generate_recursive_help(
    command: click.Group | click.Command,
    parent_context: Optional[click.core.Context] = None,
) -> str:
    output: str = ""
    context = click.core.Context(
        command, info_name=command.name, parent=parent_context
    )
    if isinstance(command, click.Group):
        for sub_command in command.commands.values():
            output += generate_recursive_help(
                sub_command, parent_context=context
            )
    else:
        output += f"## `{context.command_path[4:]}`\n\n"
        output += command.get_help(context).replace(
            "\n  ",
            "\n",
        ).replace(
            f"Usage: {context.command_path}",
            f"**Usage: python cli.py {context.command_path[4:]}",
        ).replace(
            "[OPTIONS]",
            "[OPTIONS]**",
        ).replace(
            "Options:\n",
            "**Options:**\n\n",
        ) + "\n\n"
    return output
