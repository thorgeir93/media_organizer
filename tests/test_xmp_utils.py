"""Test handling xmp config files."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from media_organizer.xmp_utils import find_xmp_config


class TestXmpUtils:
    """Test xmp_utils.py"""

    def test_find_xmp_config_file_exists(self):
        """Test that an XMP config file is found when it exists for a valid photo path."""
        photo_path = Mock(spec=Path)
        photo_path.is_file.return_value = True
        xmp_path = Mock(spec=Path)
        photo_path.with_suffix.return_value = xmp_path
        xmp_path.exists.return_value = True
        assert find_xmp_config(photo_path) == xmp_path

    def test_find_xmp_config_file_not_exists(self):
        """Test that no XMP config file is found when it does not exist
        for a valid photo path.
        """
        photo_path = Mock(spec=Path)
        photo_path.is_file.return_value = True
        xmp_path = Mock(spec=Path)
        photo_path.with_suffix.return_value = xmp_path
        xmp_path.exists.return_value = False
        assert find_xmp_config(photo_path) is None

    def test_find_xmp_config_invalid_photo_path(self):
        """Test that a ValueError is raised when the photo path is not a valid file."""
        photo_path = Mock(spec=Path)
        photo_path.is_file.return_value = False
        with pytest.raises(
            ValueError, match="The provided path does not point to a valid file."
        ):
            find_xmp_config(photo_path)
