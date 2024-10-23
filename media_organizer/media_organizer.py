from typing import Set, Final
from pathlib import Path

import click
from imohash import hashfile

from media_organizer.date_fetcher import get_fast_date, get_accurate_media_date

# How the folder name is
FOLDER_NAME_FORMAT: Final[str] = "%Y_%m_%d"

ARCHIVES_FOLDER_NAME: Final[str] = "archives"
PHOTOS_FOLDER_NAME: Final[str] = "photos"
VIDOES_FOLDER_NAME: Final[str] = "videos"
EXPORT_FOLDER_NAME: Final[str] = "export"
UNSORT_FOLDER_NAME: Final[str] = "unsort"
AUDIO_FOLDER_NAME: Final[str] = "audio"
DOCS_FOLDER_NAME: Final[str] = "docs"

MEDIA_FOLDER_NAME: Final = "media"


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
    # Darktable config file
    ".xmp",
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
}

ARCHIVE_SUPPORTED_EXTENSIONS: Set[str] = {
    ".gz",
    ".zip",
}

DARKTABLE_EXT_FORMAT: Final[str] = ".xmp"


def move_file(
    file_path: Path,
    dest_dir: Path,
    file_extension: str,
    dry_run: bool = True,
) -> None:
    """TODO

    Args:
        file_path:
        dest_dir:
        file_extension:
        dry_run:

    Returns:

    """
    dest_folder: Path = dest_dir / file_extension
    dest_endpoint = dest_folder / file_path.name
    print(f"mv {file_path} {dest_endpoint}")
    if not dry_run:
        dest_folder.mkdir(parents=True, exist_ok=True)
        file_path.rename(dest_endpoint)


def move_media(
    media_path: Path,
    dest_dir: Path,
    fast: bool = False,
    dry_run: bool = True,
    overwrite: bool = False,
    delete_original: bool = False,
) -> None:
    """
    Move media from to relevant folder in given destintion directory.

    :param media_path: The path to a image.
    :param dest_dir: The destination directory to move the media to.
    :param fast: Whether to use the fast method to fetch dates.
    """

    # Get the image date based on the mode (fast or accurate)
    media_datetime = (
        get_fast_date(media_path) if fast else get_accurate_media_date(media_path)
    )

    # If we have a valid datetime object, format it accordingly
    if media_datetime:
        media_year = media_datetime.strftime("%Y")
        media_date = media_datetime.strftime(FOLDER_NAME_FORMAT)

        date_folder: str = f"{media_year}/{media_date}"

        # dest_folder = dest_dir / media_year / media_date
        dest_folder = dest_dir / date_folder
        dest_endpoint = dest_folder / media_path.name

        if not overwrite and dest_endpoint.exists():

            if delete_original:
                # Triggered when you do not want to overwrite the destition,
                # but still want to delete the original media file, we only
                # delete the original one if the destinition file and original
                # media file are equal.
                # - if we have used the overwrite flag, we do not do anything to
                # the source file, since it will already be move instead of
                # destinition file.
                media_path_hash: str = hashfile(media_path, hexdigest=True)
                dest_endpoint_hash: str = hashfile(dest_endpoint, hexdigest=True)

                if media_path_hash == dest_endpoint_hash:
                    if media_path.exists() and media_path.is_file():
                        print(
                            f"[ VERBOSE ] rm {media_path} ({media_path_hash}) / ({dest_endpoint_hash}):{dest_endpoint}"
                        )
                        if not dry_run:
                            media_path.unlink()
                else:
                    # TODO: unittest this section!

                    # Case when destintion media already exists but does
                    # not have the same hash value as the source media.
                    # the source media is probably a exported image.
                    # By checking the file size of the source image
                    # could tell us that the image have been exported
                    # only if the source media file size is smaller than
                    # the destitinition one.
                    media_path_size: int = media_path.stat().st_size
                    dest_endpoint_size: int = dest_endpoint.stat().st_size

                    if media_path_size < dest_endpoint_size:
                        # TODO: find if it is a photo or a vido and put to relevant cateogry folder
                        # This is not the right folder
                        dest_folder = get_default_destinition() / EXPORT_FOLDER_NAME
                        dest_endpoint = dest_folder / date_folder / media_path.name
                        print(f"mv {media_path} {dest_endpoint}")
                        if not dry_run:
                            dest_folder.mkdir(parents=True, exist_ok=True)
                            media_path.rename(dest_endpoint)
                        return
                    elif media_path_size == dest_endpoint_size:
                        print(
                            f"[ REMOVE ] Original media path {media_path} can be delete"
                        )
                    else:
                        # Case when source media is bigger than destition media
                        # The destinition media must be in category exported,
                        # we should then move the destintion path to export folder
                        # and move the source media path when it belongs to.
                        print(
                            f"[ WARNING ] source media path {media_path} can be delete"
                        )

                        # TODO: move destitniont endpoint to exported location

                        # TODO: return for now, but we want to move the source
                        # media to destinition endpoint.

                    # TODO unittest this!
                    print(
                        f"[ WARNING ] source media and dest_endpoint media does not match but have same name!"
                    )
                    # print({media_path}:{media_path_hash} / {dest_endpoint}:{dest_endpoint_hash} ?")
            else:
                print(f"[ SKIP ] {media_path} -> {dest_endpoint} Already exists!")

            return

        print(f"[ VERBOSE ]: mv {media_path} {dest_endpoint}")

        if dry_run:
            return

        dest_folder.mkdir(parents=True, exist_ok=True)
        media_path.rename(dest_endpoint)

        # TODO:
        #   * If already exists, same sha1, delete the original image

    elif media_path.suffix == DARKTABLE_EXT_FORMAT and delete_original:
        # Case when .xmp darktable cfg file does not have any image file
        # to be part of. That is why we can delete that config file.
        if media_path.exists() and media_path.is_file():
            print(f"[ VERBOSE ] rm {media_path}")
            if not dry_run:
                media_path.unlink()

    else:
        # Date not readable from the Exif data of the source media
        # TODO:
        #   * do better unsort mechanism to avoid duplicates
        #   * detect if media is video or not
        #       * create method category_detector, or first, filetype detector.
        dest_folder = dest_dir / UNSORT_FOLDER_NAME
        dest_endpoint = dest_folder / media_path.name
        print(f"mv {media_path} {dest_endpoint}")
        if dry_run:
            return

        dest_folder.mkdir(parents=True, exist_ok=True)
        media_path.rename(dest_endpoint)


def move_from_source(
    source_dir: Path,
    dest_dir: Path,
    fast: bool = False,
    dry_run: bool = True,
    overwrite: bool = False,
    delete_original: bool = False,
) -> None:
    """Move media from given source directory to the given destination directory."""
    for media_path in source_dir.rglob("*"):
        if media_path.suffix.lower() in PHOTOS_SUPPORTED_EXTENSIONS:
            move_media(
                media_path,
                dest_dir / PHOTOS_FOLDER_NAME,
                fast,
                dry_run,
                overwrite,
                delete_original,
            )
            continue

        if media_path.suffix.lower() in VIDEOS_SUPPORTED_EXTENSIONS:
            move_media(
                media_path,
                dest_dir / VIDOES_FOLDER_NAME,
                fast,
                dry_run,
                overwrite,
                delete_original,
            )
            continue

        if media_path.suffix.lower() in TEXT_SUPPORTED_EXTENSIONS:
            # TODO: change the media_path to filepath since we are working with other files than media as well.
            move_file(
                media_path,
                dest_dir / DOCS_FOLDER_NAME,
                media_path.suffix.strip("."),
                dry_run,
            )
            continue

        if media_path.suffix.lower() in AUDIO_SUPPORTED_EXTENSIONS:
            # TODO: change the media_path to filepath since we are working with other files than media as well.
            move_file(
                media_path,
                dest_dir / AUDIO_FOLDER_NAME,
                media_path.suffix.strip("."),
                dry_run,
            )
            continue

        if media_path.suffix.lower() in ARCHIVE_SUPPORTED_EXTENSIONS:
            # TODO: change the media_path to filepath since we are working with other files than media as well.
            move_file(
                media_path,
                dest_dir / ARCHIVES_FOLDER_NAME,
                media_path.suffix.strip("."),
                dry_run,
            )
            continue

        if media_path.is_dir():
            print(f"[ VERBOSE ][ SKIP ] is folder: {media_path}")
            continue

        print(f"[ WARNING ] {media_path} Unknown type")
        move_file(
            media_path,
            dest_dir / UNSORT_FOLDER_NAME,
            # TODO: unitest file path without extension.
            media_path.suffix.strip("."),
            dry_run,
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
    "--overwrite",
    is_flag=True,
    help="Overwrite files in the destination folder. Be careful!",
)
@click.option(
    "--delete-original",
    is_flag=True,
    help="Delete the original file if the destination file is the same.",
)
def main(
    source_dir: str,
    dest_dir: str,
    fast: bool,
    dry_run: bool,
    overwrite: bool,
    delete_original: bool,
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
        source_dir_path, dest_dir_path, fast, dry_run, overwrite, delete_original
    )


if __name__ == "__main__":
    main()
