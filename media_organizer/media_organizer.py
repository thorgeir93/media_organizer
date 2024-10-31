from pathlib import Path
from typing import Final

import click

from media_organizer import config
from media_organizer.date_fetcher import get_accurate_media_date, get_fast_date
from media_organizer.enums import OnDuplicate
from media_organizer.file_utils import (
    add_path_extension,
    create_unique_filepath,
    is_files_equal,
)
from media_organizer.xmp_utils import find_xmp_config

# How the folder name is
FOLDER_NAME_FORMAT: Final[str] = "%Y_%m_%d"
YEAR_FORMAT: Final[str] = "%Y"


def move_file(
    src_filepath: Path,
    dst_filepath: Path,
    dry_run: bool = True,
    on_duplicate: OnDuplicate = OnDuplicate.CREATE_UNIQ_FILENAME_IF_CONTENT_MISMATCH,
) -> None:
    """Move the given source file to the given destination folder.

    Args:
        src_filepath: The source file to move.
        dst_filepath: The destination folder to move the source file into.
        dry_run: Does not move the file unless this flag is set to False.
        on_duplicate: Which strategy to follow when moving a file that
            already exists in the destination folder.
    """
    # TODO: unitest source file path without extension specifically.
    # TODO: cover all statements in unittest.

    if dst_filepath.exists():
        print(
            "[ WARNING ] duplicate: Found file with same name in the destination folder. "
            f"{src_filepath} == {dst_filepath}"
        )
        match on_duplicate:
            case OnDuplicate.CREATE_UNIQ_FILENAME_IF_CONTENT_MISMATCH:
                # TODO: unittest this functionality.
                if is_files_equal(src_path=src_filepath, dst_path=dst_filepath):
                    print(f"[ DEBUG ] rm {src_filepath}")
                    if not dry_run:
                        src_filepath.unlink()
                    return
                dst_filepath = create_unique_filepath(dst_filepath)
            case OnDuplicate.CREATE_UNIQ_FILENAME:
                dst_filepath = create_unique_filepath(dst_filepath)
            case OnDuplicate.SKIP:
                print(f"[ SKIP ] {src_filepath} {dst_filepath}")
                return
            case OnDuplicate.OVERWRITE:
                print(f"[ OVERWRITE ] {src_filepath} -> {dst_filepath}")
            case _:
                raise ValueError(f"{on_duplicate=} did not match any configured value.")

    print(f"mv {src_filepath} {dst_filepath}")

    if not dry_run:
        dst_filepath.parent.mkdir(parents=True, exist_ok=True)
        src_filepath.rename(dst_filepath)


def move_media(
    media_path: Path,
    dest_dir: Path,
    fast: bool = False,
    dry_run: bool = True,
    on_duplicate: OnDuplicate = OnDuplicate.CREATE_UNIQ_FILENAME_IF_CONTENT_MISMATCH,
) -> None:
    """Move media from source folder to the given destinationn directory.

    Args:
        media_path: The path to a image.
        dest_dir: The destination directory to move the media to.
        fast: Whether to use the fast method to fetch dates.
        dry_run: Does not move the media unless this flag is set to False.
        on_duplicate: Which strategy to follow when moving a file that
            already exists in the destination folder.
    """
    media_datetime = (
        get_fast_date(media_path) if fast else get_accurate_media_date(media_path)
    )

    if media_datetime:
        media_year: str = media_datetime.strftime(YEAR_FORMAT)
        media_date: str = media_datetime.strftime(FOLDER_NAME_FORMAT)
        date_folder: str = f"{media_year}/{media_date}"
        dest_dir = dest_dir / date_folder

    if media_path.suffix in config.PHOTOS_SUPPORTED_EXTENSIONS:
        if xmp_path := find_xmp_config(photo_path=media_path):
            print(f"[ INFO ] Found config {xmp_path} for {media_path}")
            move_file(
                src_filepath=xmp_path,
                dst_filepath=dest_dir / xmp_path.name,
                dry_run=dry_run,
                on_duplicate=on_duplicate,
            )

    move_file(
        src_filepath=media_path,
        dst_filepath=dest_dir / media_path.name,
        dry_run=dry_run,
        on_duplicate=on_duplicate,
    )


def move_from_source(
    source_dir: Path,
    dest_dir: Path,
    fast: bool = False,
    dry_run: bool = True,
    on_duplicate: OnDuplicate = OnDuplicate.CREATE_UNIQ_FILENAME_IF_CONTENT_MISMATCH,
) -> None:
    """Move media from given source directory to the given destination directory."""
    dst_path: Path
    """The target destination filepath to move the source filepath to.

    By default, we move the source file to unsorted folder if we cannot
    categorize the file.
    """
    for src_path in source_dir.rglob("*"):
        if not src_path.exists():
            print(
                f"[ WARNING ] file path {src_path} does not exists anymore, "
                "it might have been moved alongside other related files."
            )
            continue

        if src_path.is_dir():
            print(f"[ VERBOSE ][ SKIP ] is folder: {src_path}")
            continue

        dst_path = dest_dir / config.UNSORT_FOLDER_NAME / src_path.name

        if src_path.suffix.lower() in config.PHOTOS_SUPPORTED_EXTENSIONS:
            move_media(
                media_path=src_path,
                dest_dir=dest_dir / config.PHOTOS_FOLDER_NAME,
                fast=fast,
                dry_run=dry_run,
                on_duplicate=on_duplicate,
            )
            continue

        if src_path.suffix.lower() in config.VIDEOS_SUPPORTED_EXTENSIONS:
            move_media(
                media_path=src_path,
                dest_dir=dest_dir / config.VIDEOS_FOLDER_NAME,
                fast=fast,
                dry_run=dry_run,
                on_duplicate=on_duplicate,
            )
            continue

        if src_path.suffix.lower() in config.TEXT_SUPPORTED_EXTENSIONS:
            dst_path = add_path_extension(
                src_path, base_dir=dest_dir / config.DOCS_FOLDER_NAME
            )
            move_file(
                src_filepath=src_path,
                dst_filepath=dst_path,
                dry_run=dry_run,
                on_duplicate=on_duplicate,
            )
            continue

        if src_path.suffix.lower() in config.AUDIO_SUPPORTED_EXTENSIONS:
            dst_path = add_path_extension(
                src_path, base_dir=dest_dir / config.AUDIO_FOLDER_NAME
            )
            move_file(
                src_filepath=src_path,
                dst_filepath=dst_path,
                dry_run=dry_run,
                on_duplicate=on_duplicate,
            )
            continue

        if src_path.suffix.lower() in config.ARCHIVE_SUPPORTED_EXTENSIONS:
            dst_path = add_path_extension(
                src_path, base_dir=dest_dir / config.ARCHIVES_FOLDER_NAME
            )
            move_file(
                src_filepath=src_path,
                dst_filepath=dst_path,
                dry_run=dry_run,
                on_duplicate=on_duplicate,
            )
            continue

        print(f"[ WARNING ] {src_path} Unknown type.")

        if src_path.suffix:
            dst_path = add_path_extension(
                src_path, base_dir=dest_dir / config.UNSORT_FOLDER_NAME
            )
        move_file(
            src_filepath=src_path,
            dst_filepath=dst_path,
            dry_run=dry_run,
            on_duplicate=on_duplicate,
        )


@click.command()
@click.argument(
    "source_dir", type=click.Path(exists=True, file_okay=False, dir_okay=True)
)
@click.argument(
    "dest_dir",
    type=click.Path(file_okay=False, dir_okay=True),
    default=lambda: str(config.get_default_destinition()),
)
@click.option("--fast", is_flag=True, help="Use fast mode. Less accurate but faster.")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Perform a dry run without actual moving. "
    "Only print out the action that would be taken.",
)
@click.option(
    "--on-duplicate",
    type=click.Choice(
        [
            OnDuplicate.CREATE_UNIQ_FILENAME_IF_CONTENT_MISMATCH,
            OnDuplicate.CREATE_UNIQ_FILENAME,
            OnDuplicate.OVERWRITE,
            OnDuplicate.SKIP,
        ],
        case_sensitive=True,
    ),
    default=OnDuplicate.CREATE_UNIQ_FILENAME_IF_CONTENT_MISMATCH,
    help="What to do when file with same name already exists.",
)
def main(
    source_dir: str, dest_dir: str, fast: bool, dry_run: bool, on_duplicate: OnDuplicate
) -> None:
    """Organize files by type of file, file extension or creation date.

    Folder structure:
        Media files are moved into folders structured as
        <destination>/<year>/<date>. Files that do not
        have creation date in the exif metadata are either
        moved to relevant category folder alongside the
        file extension. For example document called foo.pdf
        will be organized into <destination dir>/docs/pdf/file.pdf
        path. Some files are moved to the unsort folder, the
        extension haven't been found or other issue encountered.

    on_duplicate flag:
        In case the source file already exists in the destination path,
        the on duplicate flag comes handy. You can specify which
        strategy to go for in these cases. For example
        CREATE_UNIQ_FILENAME_IF_CONTENT_MISMATCH strategy will copy
        the source file to the destination folder with uniq name only
        if the content of those two files are not the same. If they
        were the same there is no need to move the file to the destination
        folder with a new file name. Then you have two identical files
        with different name. Which is waste of space.

    # TODO: define <destination dir>/unsort folder.
    #   -   if media file like bar.mp3 does not contain creation date, or malfunction
    #       date. It should go to
    #       <destination dir>/audio/mp3/bar.mp3
    """
    source_dir_path: Path = Path(source_dir)
    dest_dir_path: Path = Path(dest_dir)

    move_from_source(
        source_dir_path,
        dest_dir_path,
        fast,
        dry_run,
        on_duplicate,
    )


# TODO: Allow the script to work in threads or multi processes.
# TODO: check if on duplicate file has the same content.
#   If so, we can skip move it and just delete the original file
# TODO: split the file into interface and logic.

if __name__ == "__main__":
    main()
