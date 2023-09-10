import subprocess
from datetime import datetime
from typing import Optional
from pathlib import Path

from PIL import Image
from PIL.ExifTags import TAGS
from PIL import UnidentifiedImageError
import piexif



DARKTABLE_EXT_FORMAT = ".xmp"

def extract_creation_date(media_path: str) -> Optional[datetime]:
    """
    Extract the creation date from media using exiftool.

    Parameters:
    - media_path (str): Path to the media file.

    Returns:
    - datetime: Datetime object representing the creation date of the media.
    """

    cmd = ["exiftool", "-CreateDate", "-s3", media_path]
    
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    raw_date = result.stdout.strip()
    
    if raw_date == "":
        return None

    try:
        return datetime.strptime(raw_date, "%Y:%m:%d %H:%M:%S")
    except ValueError as error:
        print(f"[ WARNING ] unable to parse date from {media_path}, error: {error}")



def get_fast_date(img_path: Path) -> Optional[datetime]:
    """
    Get the modified date of an image using the file system's metadata.

    Args:
        img_path (Path): The path to the image.

    Returns:
        Datetime: The year and full date (in YYYYMMDD format).
    """
    modified_time: float = img_path.stat().st_mtime
    return datetime.fromtimestamp(modified_time)


def get_accurate_img_date(img_path: Path) -> Optional[datetime]:
    """ 
    Get the creation date of an image using its EXIF metadata.

    Args:
        img_path (Path): The path to the image.

    Returns:
        Optional[datetime]: Exif creation date.
    """
    try:
        exif_data = piexif.load(str(img_path))
    except piexif._exceptions.InvalidImageDataError as error:
        #print(f"VERBOSE:piexif unable to read EXIF data from {img_path}")
        return None

    datetime_keys = [
        piexif.ExifIFD.DateTimeOriginal,
        piexif.ExifIFD.DateTimeDigitized,
        piexif.ImageIFD.DateTime
    ]
    
    img_datetime = None
    for key in datetime_keys:
        if key in exif_data["Exif"] and exif_data["Exif"][key]:
            img_datetime = exif_data["Exif"][key].decode('utf-8')
            break
    
    if not img_datetime:
        return None
    
    img_date: datetime = datetime.strptime(
        img_datetime, "%Y:%m:%d %H:%M:%S"
    )
    return img_date


#def get_accurate_img_date(img_path: Path) -> Optional[datetime]:
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



def get_accurate_media_date(media_path: Path) -> Optional[datetime]:
    """
    Get the creation date of an image using its EXIF metadata.

    Args:
        media_path (Path): The path to the image.

    Returns:
        Tuple[Optional[str], Optional[str]]: The year and full date (in YYYYMMDD format),
                                             or (None, None) if the data can't be fetched.
    """
    img_date: datetime

    # Special case for Darktable config files.
    if media_path.suffix == DARKTABLE_EXT_FORMAT:
        try:
            img_date: datetime = get_accurate_img_date(media_path.with_suffix(''))
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
