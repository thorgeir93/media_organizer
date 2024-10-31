from enum import StrEnum
from typing import Final


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
