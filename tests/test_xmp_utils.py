from pathlib import Path
from unittest.mock import Mock

import pytest

from media_organizer.xmp_utils import find_xmp_config


class TestXmpUtils:
    """Test xmp_utils.py"""

    def test_find_xmp_config_file_exists(self):
        photo_path = Mock(spec=Path)
        photo_path.is_file.return_value = True
        xmp_path = Mock(spec=Path)
        photo_path.with_suffix.return_value = xmp_path
        xmp_path.exists.return_value = True
        assert find_xmp_config(photo_path) == xmp_path

    def test_find_xmp_config_file_not_exists(self):
        photo_path = Mock(spec=Path)
        photo_path.is_file.return_value = True
        xmp_path = Mock(spec=Path)
        photo_path.with_suffix.return_value = xmp_path
        xmp_path.exists.return_value = False
        assert find_xmp_config(photo_path) is None

    def test_find_xmp_config_invalid_photo_path(self):
        photo_path = Mock(spec=Path)
        photo_path.is_file.return_value = False
        with pytest.raises(
            ValueError, match="The provided path does not point to a valid file."
        ):
            find_xmp_config(photo_path)
