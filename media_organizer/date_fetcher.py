import subprocess
from datetime import datetime
from pathlib import Path
from typing import Final

import piexif

DARKTABLE_EXT_FORMAT: Final[str] = ".xmp"

COMMON_DATE_FORMATS: set[str] = {
    "%Y:%m:%d %H:%M:%S",
    "%Y:%m:%d %H:%M:%SZ",
    "%Y:%m:%d %H:%M:%S%z",
}
"""Common date formats found in files metadata.

These formats with ":" seperator for year, month and day is unusual and
therefore the dateutil.parser.parse method cannot process dates in such format.
See stackoverflow discussion: https://stackoverflow.com/q/73104677
"""


def try_parse_date(raw_date: str, date_format: str) -> datetime | None:
    """Parse the given raw date string using given date format."""
    try:
        return datetime.strptime(raw_date, date_format)
    except ValueError:
        return None


def parse_raw_date(raw_date: str) -> datetime:
    """Parse the given raw date into datetime object."""
    for common_date_format in COMMON_DATE_FORMATS:
        parsed_date: datetime = try_parse_date(
            raw_date=raw_date, date_format=common_date_format
        )
        if parsed_date:
            return parsed_date
    return None


def extract_creation_date(media_path: str) -> datetime | None:
    """
    Extract the creation date from media using exiftool.

    Parameters:
    - media_path (str): Path to the media file.

    Returns:
    - datetime: Datetime object representing the creation date of the media.
    """

    cmd = ["exiftool", "-CreateDate", "-s3", media_path]

    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    raw_date = result.stdout.strip()

    if raw_date == "":
        return None

    parsed_date: datetime | None = parse_raw_date(raw_date=raw_date)

    if not parsed_date:
        print(f"[ WARNING ] Could not parse {raw_date} date from {media_path}")

    return parsed_date


def get_fast_date(img_path: Path) -> datetime | None:
    """
    Get the modified date of an image using the file system's metadata.

    Args:
        img_path (Path): The path to the image.

    Returns:
        Datetime: The year and full date (in YYYYMMDD format).
    """
    modified_time: float = img_path.stat().st_mtime
    return datetime.fromtimestamp(modified_time)


def get_accurate_img_date(img_path: Path) -> datetime | None:
    """
    Get the creation date of an image using its EXIF metadata.

    Args:
        img_path (Path): The path to the image.

    Returns:
        datetime: Exif creation date or None if loading exif fails.
    """
    try:
        exif_data = piexif.load(str(img_path))
    except (piexif._exceptions.InvalidImageDataError, ValueError) as error:
        print(
            f"[ VERBOSE ]: piexif unable to read EXIF data from {img_path}, "
            f"error: {error}"
        )
        return None

    datetime_keys = [
        piexif.ExifIFD.DateTimeOriginal,
        piexif.ExifIFD.DateTimeDigitized,
        piexif.ImageIFD.DateTime,
    ]

    img_datetime = None
    for key in datetime_keys:
        if key in exif_data["Exif"] and exif_data["Exif"][key]:
            img_datetime = exif_data["Exif"][key].decode("utf-8")
            break

    if not img_datetime:
        return None

    parsed_date: datetime | None = parse_raw_date(raw_date=img_datetime)

    if not parsed_date:
        print(f"[ WARNING ] Could not parse {img_datetime} date from {img_path}")

    return parsed_date


def get_accurate_media_date(media_path: Path) -> datetime | None:
    """
    Get the creation date of an image using its EXIF metadata.

    Args:
        media_path (Path): The path to the media.

    Returns:
        Date of the given media file path. None if date extraction fails.
    """
    img_date: datetime

    # Special case for Darktable config files.
    if media_path.suffix == DARKTABLE_EXT_FORMAT:
        try:
            img_date: datetime = get_accurate_img_date(media_path.with_suffix(""))
        except FileNotFoundError:
            print(f"[ WARNING ] {media_path} cfg file does not belongs to any file")
            return None
    else:
        img_date: datetime = get_accurate_img_date(media_path)

    if img_date:
        return img_date
    else:
        # probably a video file
        return extract_creation_date(media_path)


# def get_accurate_img_date(img_path: Path) -> Optional[datetime]:
#    """
#    Get the creation date of an image using its EXIF metadata.
#
#    Args:
#        img_path (Path): The path to the image.
#
#    Returns:
#        Optional[datetime]: Exif creation date.
#    """
#    try:
#        with Image.open(img_path) as img:
#            exif_data = img.getexif()
#            datetime_keys = [
#                TAGS_REVERSE.get("DateTimeOriginal"),
#                TAGS_REVERSE.get("DateTime")
#            ]
#
#            img_datetime = None
#            for key in datetime_keys:
#                if key in exif_data and exif_data[key]:
#                    img_datetime = exif_data[key]
#                    break
#
#            if not img_datetime:
#                return None
#
#            img_date: datetime = datetime.strptime(
#                img_datetime, "%Y:%m:%d %H:%M:%S"
#            )
#            return img_date
#
#    except UnidentifiedImageError as error:
#        print(f"Not supported media type for PIL.Image: {error}")
#
#    return None
