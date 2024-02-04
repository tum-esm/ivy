import re


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
