from enum import StrEnum
from typing import Set, Final
from pathlib import Path

import click
from imohash import hashfile

from media_organizer.date_fetcher import get_fast_date, get_accurate_media_date

# How the folder name is
FOLDER_NAME_FORMAT: Final[str] = "%Y_%m_%d"
YEAR_FORMAT: Final[str] = "%Y"

ARCHIVES_FOLDER_NAME: Final[str] = "archives"
PHOTOS_FOLDER_NAME: Final[str] = "photos"
VIDOES_FOLDER_NAME: Final[str] = "videos"
EXPORT_FOLDER_NAME: Final[str] = "export"
UNSORT_FOLDER_NAME: Final[str] = "unsort"
AUDIO_FOLDER_NAME: Final[str] = "audio"
DOCS_FOLDER_NAME: Final[str] = "docs"

MEDIA_FOLDER_NAME: Final = "media"


class OnDuplicate(StrEnum):
    """Enum class containing options when destination already have the same filename."""

    CREATE_UNIQ_FILENAME: Final[str] = "create-uniq-filename"
    """Create unique filename for the source file in the destination directory."""
    CREATE_UNIQ_FILENAME_IF_CONTENT_MISMATCH: Final[str] = (
        "create-uniq-filename-if-content-mismatch"
    )
    """Create unique filename if content in the source and destination dirs are not equal.
    
    This is slower than just CREATE_UNIQ_FILENAME since this settings requires
    the code to generate hashes of two files to compare if they are equal or not.
    The benefit of this settings is that we are not creating extra files in the
    destination if it already have content.
    """
    OVERWRITE: Final[str] = "overwrite"
    """Overwrite the destination file with the source file."""
    SKIP: Final[str] = "skip"
    """Leave the source filepath untouched if the same filename exists in the destination."""


PHOTOS_SUPPORTED_EXTENSIONS: Set[str] = {
    # Standard format
    ".jpg",
    # Unsorted
    ".png",  # Limited date information
    ".gif",  # Limited date information
    # Raw image format
    ".cr2",
    ".dng",
    ".arw",
    ".nef",
}


VIDEOS_SUPPORTED_EXTENSIONS: Set[str] = {
    # Video format
    ".mp4",
    ".mov",
}

AUDIO_SUPPORTED_EXTENSIONS: Set[str] = {
    ".woff",
    ".wav",
    ".mp3",
}


TEXT_SUPPORTED_EXTENSIONS: Set[str] = {
    # Normal text
    ".txt",
    # Data formats
    ".xml",
    ".csv",
    ".svg",
    # Script
    ".py",
    ".java",
    ".sh",
    ".dll",
    ".h",
    ".c",
    ".f",  # Found javascript
    # Templates
    ".html",
    # Darktable config file
    # TODO: unittest .xmp configs alongside .jpg or raw file. See if they will follow.
    ".xmp",
}

ARCHIVE_SUPPORTED_EXTENSIONS: Set[str] = {
    ".gz",
    ".zip",
}

DARKTABLE_EXT_FORMAT: Final[str] = ".xmp"
"""Config files for image editing.

Darktable is an application to process images in batches.
For each image, the application creates an config file with extension `.xmp`.
These config files contains a xml template that incdlues how the image has been editing.
This allows us to keep the raw image untouched, still showing the raw file in the darktable
application like it have been edit.

The trick is to move the config file with the image it belongs.
"""


# Case when .xmp darktable cfg file does not have any image file
# to be part of. That is why we can delete that config file.


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


def find_xmp_config(photo_path: Path) -> Path | None:
    """Checks if an .xmp config file exists in the same location as the given photo file.

    Args:
        photo_path: Path to the photo file.

    Returns:
        Path to the .xmp config file if found, otherwise None.
    """
    # TODO: unittest this method.
    if not photo_path.is_file():
        raise ValueError("The provided path does not point to a valid file.")
    xmp_path: Path = photo_path.with_suffix(".xmp")
    return xmp_path if xmp_path.exists() else None


def is_files_equal(src_path: Path, dst_path: Path) -> bool:
    """Return True if the given two files are equal otherwise False."""
    # Compare file sizes first (cheap check)
    if src_path.stat().st_size != dst_path.stat().st_size:
        return True
    return hashfile(src_path, hexdigest=True) != hashfile(dst_path, hexdigest=True)


def move_file(
    src_filepath: Path,
    dest_dir: Path,
    dry_run: bool = True,
    on_duplicate: OnDuplicate = OnDuplicate.CREATE_UNIQ_FILENAME_IF_CONTENT_MISMATCH,
) -> None:
    """Move the given source file to the given destination folder.

    Args:
        src_filepath: The source file to move.
        dest_dir: The destination folder to move the source file into.
        dry_run: Does not move the file unless this flag is set to False.
        on_duplicate: Which strategy to follow when moving a file that
            already exists in the destination folder.
    """
    # TODO: unitest source file path without extension.
    file_extension: str = src_filepath.suffix.strip(".")
    dest_folder: Path = dest_dir / file_extension
    dest_filepath = dest_folder / src_filepath.name

    if dest_filepath.exists():
        print(
            "[ WARNING ] duplicate: Found file with same name in the destination folder. "
            f"{src_filepath} == {dest_filepath}"
        )
        match on_duplicate:
            case OnDuplicate.CREATE_UNIQ_FILENAME_IF_CONTENT_MISMATCH:
                # TODO: unittest this functionality.
                if is_files_equal(src_path=src_filepath, dst_path=dest_filepath):
                    print(f"[ DEBUG ] rm {src_filepath}")
                    if not dry_run:
                        src_filepath.unlink()
                    return
                dest_filepath = create_unique_filepath(dest_filepath)
            case OnDuplicate.CREATE_UNIQ_FILENAME:
                dest_filepath = create_unique_filepath(dest_filepath)
            case OnDuplicate.SKIP:
                print(f"[ SKIP ] {src_filepath} {dest_filepath}")
                return
            case OnDuplicate.OVERWRITE:
                print(f"[ OVERWRITE ] {src_filepath} -> {dest_filepath}")
            case _:
                raise ValueError(f"{on_duplicate=} did not match any configured value.")

    print(f"mv {src_filepath} {dest_filepath}")

    if not dry_run:
        dest_folder.mkdir(parents=True, exist_ok=True)
        src_filepath.rename(dest_filepath)


def move_media(
    media_path: Path,
    dest_dir: Path,
    fast: bool = False,
    dry_run: bool = True,
    on_duplicate: OnDuplicate = OnDuplicate.CREATE_UNIQ_FILENAME_IF_CONTENT_MISMATCH,
) -> None:
    """
    Move media from to relevant folder in given destintion directory.

    :param media_path: The path to a image.
    :param dest_dir: The destination directory to move the media to.
    :param fast: Whether to use the fast method to fetch dates.
    """
    media_datetime = (
        get_fast_date(media_path) if fast else get_accurate_media_date(media_path)
    )

    if media_datetime:
        media_year: str = media_datetime.strftime(YEAR_FORMAT)
        media_date: str = media_datetime.strftime(FOLDER_NAME_FORMAT)
        date_folder: str = f"{media_year}/{media_date}"
        dest_dir = dest_dir / date_folder

    move_file(
        src_filepath=media_path,
        dest_dir=dest_dir,
        dry_run=dry_run,
        on_duplicate=on_duplicate,
    )

    if media_path.suffix in PHOTOS_SUPPORTED_EXTENSIONS:
        if xmp_path := find_xmp_config(photo_path=media_path):
            print(f"[ DEBUG ] Found config {xmp_path} for {media_path}")
            move_file(
                src_filepath=xmp_path,
                dest_dir=dest_dir,
                dry_run=dry_run,
                on_duplicate=on_duplicate,
            )

    #     if not overwrite and dest_endpoint.exists():
    #         if delete_original:
    #             # Triggered when you do not want to overwrite the destition,
    #             # but still want to delete the original media file, we only
    #             # delete the original one if the destinition file and original
    #             # media file are equal.
    #             # - if we have used the overwrite flag, we do not do anything to
    #             # the source file, since it will already be move instead of
    #             # destinition file.
    #             media_path_hash: str = hashfile(media_path, hexdigest=True)
    #             dest_endpoint_hash: str = hashfile(dest_endpoint, hexdigest=True)

    #             if media_path_hash == dest_endpoint_hash:
    #                 if media_path.exists() and media_path.is_file():
    #                     print(
    #                         f"[ VERBOSE ] rm {media_path} ({media_path_hash}) / ({dest_endpoint_hash}):{dest_endpoint}"
    #                     )
    #                     if not dry_run:
    #                         media_path.unlink()
    #             else:
    #                 # TODO: unittest this section!

    #                 # Case when destintion media already exists but does
    #                 # not have the same hash value as the source media.
    #                 # the source media is probably a exported image.
    #                 # By checking the file size of the source image
    #                 # could tell us that the image have been exported
    #                 # only if the source media file size is smaller than
    #                 # the destitinition one.
    #                 media_path_size: int = media_path.stat().st_size
    #                 dest_endpoint_size: int = dest_endpoint.stat().st_size

    #                 if media_path_size < dest_endpoint_size:
    #                     # TODO: find if it is a photo or a vido and put to relevant cateogry folder
    #                     # This is not the right folder
    #                     dest_folder = get_default_destinition() / EXPORT_FOLDER_NAME
    #                     dest_endpoint = dest_folder / date_folder / media_path.name
    #                     print(f"mv {media_path} {dest_endpoint}")
    #                     if not dry_run:
    #                         dest_folder.mkdir(parents=True, exist_ok=True)
    #                         media_path.rename(dest_endpoint)
    #                     return
    #                 elif media_path_size == dest_endpoint_size:
    #                     print(
    #                         f"[ REMOVE ] Original media path {media_path} can be delete"
    #                     )
    #                 else:
    #                     # Case when source media is bigger than destition media
    #                     # The destinition media must be in category exported,
    #                     # we should then move the destintion path to export folder
    #                     # and move the source media path when it belongs to.
    #                     print(
    #                         f"[ WARNING ] source media path {media_path} can be delete"
    #                     )

    #                     # TODO: move destitniont endpoint to exported location

    #                     # TODO: return for now, but we want to move the source
    #                     # media to destinition endpoint.

    #                 # TODO unittest this!
    #                 print(
    #                     f"[ WARNING ] source media and dest_endpoint media does not match but have same name!"
    #                 )
    #                 # print({media_path}:{media_path_hash} / {dest_endpoint}:{dest_endpoint_hash} ?")
    #         else:
    #             print(f"[ SKIP ] {media_path} -> {dest_endpoint} Already exists!")

    #         return

    #     print(f"[ VERBOSE ]: mv {media_path} {dest_endpoint}")

    #     if dry_run:
    #         return

    #     dest_folder.mkdir(parents=True, exist_ok=True)
    #     media_path.rename(dest_endpoint)

    # TODO:
    #   * If already exists, same sha1, delete the original image

    # elif media_path.suffix == DARKTABLE_EXT_FORMAT and delete_original:
    #     # Case when .xmp darktable cfg file does not have any image file
    #     # to be part of. That is why we can delete that config file.
    #     if media_path.exists() and media_path.is_file():
    #         print(f"[ VERBOSE ] rm {media_path}")
    #         if not dry_run:
    #             media_path.unlink()

    # else:
    #     # Date not readable from the Exif data of the source media
    #     # TODO:
    #     #   * do better unsort mechanism to avoid duplicates
    #     #   * detect if media is video or not
    #     #       * create method category_detector, or first, filetype detector.
    #     dest_folder = dest_dir / UNSORT_FOLDER_NAME
    #     dest_endpoint = dest_folder / media_path.name
    #     print(f"mv {media_path} {dest_endpoint}")
    #     if dry_run:
    #         return

    #     dest_folder.mkdir(parents=True, exist_ok=True)
    #     media_path.rename(dest_endpoint)


def move_from_source(
    source_dir: Path,
    dest_dir: Path,
    fast: bool = False,
    dry_run: bool = True,
    on_duplicate: OnDuplicate = OnDuplicate.CREATE_UNIQ_FILENAME_IF_CONTENT_MISMATCH,
) -> None:
    """Move media from given source directory to the given destination directory."""
    for media_path in source_dir.rglob("*"):
        if not media_path.exists():
            print(
                f"[ WARNING ] file path {media_path} does not exists anymore, "
                "it might have been moved alongside other related files."
            )
            continue

        if media_path.is_dir():
            print(f"[ VERBOSE ][ SKIP ] is folder: {media_path}")
            continue

        if media_path.suffix.lower() in PHOTOS_SUPPORTED_EXTENSIONS:
            move_media(
                media_path,
                dest_dir / PHOTOS_FOLDER_NAME,
                fast,
                dry_run,
                on_duplicate=on_duplicate,
            )
            continue

        if media_path.suffix.lower() in VIDEOS_SUPPORTED_EXTENSIONS:
            move_media(
                media_path,
                dest_dir / VIDOES_FOLDER_NAME,
                fast,
                dry_run,
                on_duplicate=on_duplicate,
            )
            continue

        if media_path.suffix.lower() in TEXT_SUPPORTED_EXTENSIONS:
            # TODO: change the media_path to filepath since we are working with other files than media as well.
            move_file(
                media_path,
                dest_dir / DOCS_FOLDER_NAME,
                dry_run,
                on_duplicate=on_duplicate,
            )
            continue

        if media_path.suffix.lower() in AUDIO_SUPPORTED_EXTENSIONS:
            # TODO: change the media_path to filepath since we are working with other files than media as well.
            move_file(
                media_path,
                dest_dir / AUDIO_FOLDER_NAME,
                dry_run,
                on_duplicate=on_duplicate,
            )
            continue

        if media_path.suffix.lower() in ARCHIVE_SUPPORTED_EXTENSIONS:
            # TODO: change the media_path to filepath since we are working with other files than media as well.
            move_file(
                media_path,
                dest_dir / ARCHIVES_FOLDER_NAME,
                dry_run,
                on_duplicate=on_duplicate,
            )
            continue

        print(f"[ WARNING ] {media_path} Unknown type")

        move_file(
            media_path,
            dest_dir / UNSORT_FOLDER_NAME,
            dry_run,
            on_duplicate=on_duplicate,
        )


def get_default_destinition() -> Path:
    return Path.home() / MEDIA_FOLDER_NAME


@click.command()
@click.argument(
    "source_dir", type=click.Path(exists=True, file_okay=False, dir_okay=True)
)
@click.argument(
    "dest_dir",
    type=click.Path(file_okay=False, dir_okay=True),
    default=lambda: str(get_default_destinition()),
)
@click.option("--fast", is_flag=True, help="Use fast mode. Less accurate but faster.")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Perform a dry run without actual moving. Only print out the action that would be taken.",
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
    help="What to do when file with same name already exists. ",
)
# TODO: add flag
def main(
    source_dir: str,
    dest_dir: str,
    fast: bool,
    dry_run: bool,
    on_duplicate: OnDuplicate = OnDuplicate.CREATE_UNIQ_FILENAME_IF_CONTENT_MISMATCH,
) -> None:
    """
    Organize photos by their date, either using a fast or accurate method.

    Media files are moved into folders structured as <destination>/<year>/<date>.
    Files that do not have creation date in the exif metadata are either moved to
    relevant category folder alongside the file extension. For example document called
    foo.pdf will be organized into <destination dir>/docs/pdf/file.pdf path.
    Some files are moved to the unsort folder, the extension haven't been found or other issue encountered.

    # TODO: define <destination dir>/unsort folder.
    #   -   if media file like bar.mp3 does not contain creation date, or malfunction date. It should go to
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

if __name__ == "__main__":
    main()
