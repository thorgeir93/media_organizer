import tempfile
from typing import Iterator
from unittest.mock import patch

import pytest
from pathlib import Path
from media_organizer import media_organizer
from media_organizer.media_organizer import create_unique_filepath, OnDuplicate

from tests.create_img import create_mock_image


class TestMediaOrganizer:
    """Test media organizer."""

    @pytest.mark.parametrize(
        "on_duplicate, media_exif_date, filename, expected_dest_filepath",
        [
            (
                OnDuplicate.CREATE_UNIQ_FILENAME,
                "2024:10:21 17:56:55",
                "media.jpg",
                Path("photos/2024/2024_10_21/media.jpg"),
            ),
            (
                OnDuplicate.CREATE_UNIQ_FILENAME,
                "2024:09:03 17:56:55",
                "media.jpg",
                Path("photos/2024/2024_09_03/media.jpg"),
            ),
        ],
    )
    def test_media_organizer(
        self,
        on_duplicate: OnDuplicate,
        media_exif_date: str,
        filename: str,
        expected_dest_filepath: Path,
        tmpdir: Path,
    ) -> None:
        """Test media organizer interface."""
        format: str = "JPEG"

        source_dir: Path = Path(tmpdir.mkdir("source_dir"))
        dest_dir: Path = Path(tmpdir.mkdir("dest_dir"))

        # Create the media test file.
        original_media_path: Path = source_dir / filename
        create_mock_image(str(original_media_path), media_exif_date, format=format)

        # Perform the logic.
        media_organizer.move_from_source(
            source_dir=source_dir,
            dest_dir=dest_dir,
            dry_run=False,
            on_duplicate=on_duplicate,
        )

        assert not original_media_path.exists()
        assert (dest_dir / expected_dest_filepath).exists()

    @pytest.mark.parametrize(
        "on_duplicate, media_exif_date, filename, expected_dest_filepath",
        [
            (
                OnDuplicate.CREATE_UNIQ_FILENAME,
                "2024:10:21 17:56:55",
                "media.jpg",
                Path("photos/2024/2024_10_21/media_01.jpg"),
            ),
            (
                OnDuplicate.CREATE_UNIQ_FILENAME,
                "2024:10:21 17:56:55",
                "media.jpg",
                Path("photos/2024/2024_10_21/media_01.jpg"),
            ),
        ],
    )
    def test_media_organizer_already_in_destination(
        self,
        on_duplicate: OnDuplicate,
        media_exif_date: str,
        filename: str,
        expected_dest_filepath: Path,
        tmpdir: Path,
    ) -> None:
        """Test media organizer when media file already exists in the destination."""
        format: str = "JPEG"

        source_dir: Path = Path(tmpdir.mkdir("source_dir"))
        dest_dir: Path = Path(tmpdir.mkdir("dest_dir"))

        # Create the media test file.
        original_media_path: Path = source_dir / filename
        destination_media_dir: Path = dest_dir / expected_dest_filepath.parent
        destination_media_dir.mkdir(parents=True, exist_ok=False)
        destination_media_path: Path = destination_media_dir / filename

        # Create same file in both source and destination folder.
        create_mock_image(
            str(original_media_path), media_exif_date, format=format, randomize=False
        )
        create_mock_image(
            str(destination_media_path), media_exif_date, format=format, randomize=False
        )

        # Perform the logic.
        media_organizer.move_from_source(
            source_dir=source_dir,
            dest_dir=dest_dir,
            dry_run=False,
            on_duplicate=on_duplicate,
        )

        assert not original_media_path.exists()
        assert (dest_dir / expected_dest_filepath).exists()

    # TODO: fix delete_original, it does not do what it should do, that is delete the original files even
    #   though it is not moved to the destination directory. Reconcider this.
    @pytest.mark.parametrize(
        "mock_exists_side_effect, expected_result",
        [
            ([False], Path("/path/to/destination/file.txt")),  # No file conflict
            (
                [True, False],
                Path("/path/to/destination/file_01.txt"),
            ),  # Single conflict, resolves with _01
            (
                [True, True, False],
                Path("/path/to/destination/file_02.txt"),
            ),  # Multiple conflicts, resolves with _02
        ],
    )
    @patch("pathlib.Path.exists")
    def test_create_unique_filepath(
        self, mock_exists, mock_exists_side_effect, expected_result
    ):
        dest_path = Path("/path/to/destination/file.txt")
        mock_exists.side_effect = mock_exists_side_effect
        result = create_unique_filepath(dest_path)
        assert result == expected_result
