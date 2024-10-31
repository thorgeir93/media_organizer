import random

import piexif
from PIL import Image


def create_mock_image(
    file_path: str, date_str: str, format: str = "JPEG", randomize: bool = True
):
    """Create random mock image.

    Args:
        file_path: Name of the image.
        date_str: Format "YYYY:MM:DD HH:MM:SS"
        format: Format of the image, for example JPEG, PNG etc.
    """
    # Create a blank image
    color: tuple[int, int, int] = (67, 30, 11)
    if randomize:
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    img = Image.new("RGB", (60, 30), color=color)

    # Prepare EXIF data
    exif_dict = {"0th": {}, "Exif": {}, "1st": {}, "thumbnail": None, "GPS": {}}
    exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = date_str.encode("utf-8")
    exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = date_str.encode("utf-8")

    # Dump the EXIF data into bytes
    exif_bytes = piexif.dump(exif_dict)

    # Save the image with the EXIF data
    img.save(str(file_path), format=format, exif=exif_bytes)
