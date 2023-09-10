import piexif

from PIL import Image

def create_test_image_with_date(file_path: str, date_str: str):
    # Create a blank image
    img = Image.new('RGB', (60, 30), color=(73, 109, 137))

    # Prepare EXIF data
    exif_dict = {"0th": {}, "Exif": {}, "1st": {}, "thumbnail": None, "GPS": {}}
    exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = date_str.encode("utf-8")
    #exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = date_str.encode("utf-8")
    exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = date_str.encode("utf-8")
    #exif_dict["Exif"][piexif.ImageIFD.DateTime] = date_str.encode("utf-8")

    # Dump the EXIF data into bytes
    exif_bytes = piexif.dump(exif_dict)

    # Save the image with the EXIF data
    img.save(str(file_path), format="JPEG", exif=exif_bytes)
