from pathlib import Path

from imohash import hashfile


def create_unique_filepath(filepath: Path) -> Path:
    """Create a unique file path if filepath exists by appending a number to the file name.

    Args:
        filepath: The destination file path.

    Returns:
        A unique file path in the destination directory.
    """
    base_name: str = filepath.stem
    extension: str = filepath.suffix
    counter: int = 1
    new_dest_path: Path = filepath
    while new_dest_path.exists():
        new_dest_path = filepath.with_name(
            f"{base_name}_{str(counter).zfill(2)}{extension}"
        )
        counter += 1
    return new_dest_path


def is_files_equal(src_path: Path, dst_path: Path) -> bool:
    """Return True if the given two files are equal otherwise False."""
    # TODO: unittest this method.
    # Compare file sizes first (cheap check)
    if src_path.stat().st_size != dst_path.stat().st_size:
        return True
    return hashfile(src_path, hexdigest=True) != hashfile(dst_path, hexdigest=True)


def add_path_extension(src_filepath: Path, base_dir: Path) -> Path:
    file_extension: str = src_filepath.suffix.strip(".")
    dest_filepath: Path = base_dir / file_extension / src_filepath.name
    return dest_filepath
