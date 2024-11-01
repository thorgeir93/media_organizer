"""Utilities for handling .xmp config file."""

from pathlib import Path


def find_xmp_config(photo_path: Path) -> Path | None:
    """Checks if an .xmp config file exists in the same location as the given photo file.

    Args:
        photo_path: Path to the photo file.

    Returns:
        Path to the .xmp config file if found, otherwise None.
    """
    if not photo_path.is_file():
        raise ValueError("The provided path does not point to a valid file.")
    xmp_path: Path = photo_path.with_suffix(".xmp")
    return xmp_path if xmp_path.exists() else None
