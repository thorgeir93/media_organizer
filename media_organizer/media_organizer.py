from typing import Set, Final
from pathlib import Path
import argparse
from argparse import Namespace
from datetime import datetime
from imohash import hashfile

from date_fetcher import get_fast_date, get_accurate_media_date

# How the folder name is 
FOLDER_NAME_FORMAT: Final[str] = "%Y_%m_%d"

PHOTOS_FOLDER_NAME = "photos"
VIDOES_FOLDER_NAME = "videos"


PHOTOS_SUPPORTED_EXTENSIONS: Set[str] = {
    # Standard format
    ".JPG", ".jpg",

    # Raw image format
    ".CR2", ".DNG", ".ARW", ".NEF",

    # Darktable config file
    ".xmp",
}

VIDEOS_SUPPORTED_EXTENSIONS: Set[str] = {
    # Video format
    ".MP4", ".MOV",
}


DARKTABLE_EXT_FORMAT = ".xmp"


def move_media(media_path: Path, dest_dir: Path, fast: bool = False, dry_run: bool = True, overwrite: bool = False, delete_original: bool = False) -> None:
    """
    Move media from to relevant folder in given destintion directory.

    :param media_path: The path to a image.
    :param dest_dir: The destination directory to move the media to.
    :param fast: Whether to use the fast method to fetch dates.
    """

    # Get the image date based on the mode (fast or accurate)
    media_datetime = get_fast_date(media_path) if fast else get_accurate_media_date(media_path)

    # If we have a valid datetime object, format it accordingly
    if media_datetime:
        media_year = media_datetime.strftime("%Y")
        media_date = media_datetime.strftime(FOLDER_NAME_FORMAT)
    
        dest_folder = dest_dir / media_year / media_date
        dest_endpoint = dest_folder / media_path.name

        if not overwrite and dest_endpoint.exists():
 
            if delete_original:
                # Triggered when you do not want to overwrite the destition,
                # but still want to delete the original media file, we only
                # delete the original one if the destinition file and original
                # media file are equal.
                # - if we have used the overwrite flag, we do not do anything to
                # the original file, since it will already be move instead of
                # destinition file.
                media_path_hash: str = hashfile(media_path, hexdigest=True)
                dest_endpoint_hash: str = hashfile(dest_endpoint, hexdigest=True)


                if media_path_hash == dest_endpoint_hash:
                    if media_path.exists() and media_path.is_file():
                        print(f"[ VERBOSE ] rm {media_path} ({media_path_hash}) / ({dest_endpoint_hash}):{dest_endpoint}")
                        if not dry_run:
                            media_path.unlink()
                else:
                    # TODO unittest this!
                    print(f"[ WARNING ] original media and destintion media does not match but have same name! {media_path}:{media_path_hash} / {dest_endpoint}:{dest_endpoint_hash} ?")
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
        print(f"SKIP {media_path}, does not have EXIF date time.")


def main() -> None:
    """
    Organize photos by their date, either using a fast or accurate method.
    
    Images are moved into folders structured as <destination>/<year>/<date>.
    The script supports command-line arguments to specify the source and destination directories,
    and whether to use the fast method or perform a dry run.
    """
    default_destination: str = str(Path.home() / f"media")

    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Organize photos by date.")
    parser.add_argument("source_dir", help="Source directory containing images.")
    parser.add_argument(
        "dest_dir",
        nargs="?",
        default=default_destination,
        help="Destination directory."
    )
    parser.add_argument(
        "--fast", action="store_true", help="Use fast mode. Less accurate but faster."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without actual moving. Only print out the action that would be taken."
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Use this flag to overwrite files in destinition folder, be careful! default is False."
    )
    parser.add_argument(
        "--delete-original",
        action="store_true",
        help="Use this flag if you want to delete the original file if the destitiona file is same as the original one."
    )

    args: Namespace = parser.parse_args()

    source_dir: Path = Path(args.source_dir)
    dest_dir: Path = Path(args.dest_dir)

    #for media_path in source_dir.iterdir():
    for media_path in source_dir.rglob("*"):
        if media_path.suffix in PHOTOS_SUPPORTED_EXTENSIONS:
            move_media(media_path, dest_dir / PHOTOS_FOLDER_NAME, args.fast, args.dry_run, args.overwrite, args.delete_original)
            continue

        if media_path.suffix in VIDEOS_SUPPORTED_EXTENSIONS:
            move_media(media_path, dest_dir / VIDOES_FOLDER_NAME, args.fast, args.dry_run, args.overwrite, args.delete_original)
            continue

        print(f"[ VERBOSE ][ SKIP ] {media_path} NOT SUPPORTED")


if __name__ == "__main__":
    main()
