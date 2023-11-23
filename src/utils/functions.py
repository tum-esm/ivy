import re


def string_is_valid_version_name(version_name: str) -> bool:
    """Check if the version name is valid. Valid version name examples `v1.2.3`,
    `v4.5.6-alpha.78`, `v7.8.9-beta.10`, `v11.12.13-rc.14`.
    
    Args:
        version_name: version name to check.
    
    Returns:
        True if the version name is valid, False otherwise."""

    return re.match(r"v\d+\.\d+\.\d+(-(alpha|beta|rc)\.\d+)",
                    version_name) is not None
