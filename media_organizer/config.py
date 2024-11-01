"""Contains media organizer configs.

Configs like the name of the directories to store the files and more.
"""

from pathlib import Path
from typing import Final, Set

ARCHIVES_FOLDER_NAME: Final[str] = "archives"
PHOTOS_FOLDER_NAME: Final[str] = "photos"
VIDEOS_FOLDER_NAME: Final[str] = "videos"
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
For each image, the application creates an config file
with extension `.xmp`. These config files contains a XML
template that includes how the image has been editing.
This allows us to keep the raw image untouched, still
showing the raw file in the darktable application like
it have been edit.

The trick is to move the config file with the image it belongs.
"""


def get_default_destinition() -> Path:
    """Return the default folder for the media file destination."""
    return Path.home() / MEDIA_FOLDER_NAME
