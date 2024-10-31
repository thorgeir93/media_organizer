from pathlib import Path

import pytest

from media_organizer import media_organizer
from tests.create_img import create_mock_image


class TestMediaOrganizer:
    """Test media organizer."""

    @pytest.mark.parametrize(
        "overwrite, delete_original, media_exif_date, extension, organized_dir_path",
        [
            (True, True, "2024:10:21 17:56:55", "jpg", Path("photos/2024/2024_10_21")),
            (True, False, "2024:09:03 17:56:55", "jpg", Path("photos/2024/2024_09_03")),
            (
                False,
                False,
                "2023:02:11 11:11:11",
                "jpg",
                Path("photos/2023/2023_02_11"),
            ),
            # (False, True),
            # (True, False),
            # (False, False),
        ],
    )
    def test_media_organizer(
        self,
        overwrite: bool,
        delete_original: bool,
        media_exif_date: str,
        extension: str,
        organized_dir_path: Path,
        tmpdir: Path,
    ) -> None:
        """Test media organizer interface."""
        media_filename: str = f"media.{extension}"
        format: str = "JPEG"

        source_dir: Path = Path(tmpdir.mkdir("source_dir"))
        dest_dir: Path = Path(tmpdir.mkdir("dest_dir"))

        # Create the media test file.
        original_media_path: Path = source_dir / media_filename
        create_mock_image(str(original_media_path), media_exif_date, format=format)

        # Perform the logic.
        media_organizer.move_from_source(
            source_dir=source_dir,
            dest_dir=dest_dir,
            dry_run=False,
            overwrite=overwrite,
            delete_original=delete_original,
        )

        expected_new_image_path: Path = dest_dir / organized_dir_path / media_filename
        assert expected_new_image_path.exists()
        assert not original_media_path.exists()

    @pytest.mark.parametrize(
        "overwrite, delete_original, media_exif_date, extension, organized_dir_path",
        [
            (True, True, "2024:10:21 17:56:55", "jpg", Path("photos/2024/2024_10_21")),
            (True, False, "2024:10:21 17:56:55", "jpg", Path("photos/2024/2024_10_21")),
        ],
    )
    def test_media_organizer_already_in_destination(
        self,
        overwrite: bool,
        delete_original: bool,
        media_exif_date: str,
        extension: str,
        organized_dir_path: Path,
        tmpdir: Path,
    ) -> None:
        """Test media organizer when media file already exists in the destination."""
        media_filename: str = f"media.{extension}"
        format: str = "JPEG"

        source_dir: Path = Path(tmpdir.mkdir("source_dir"))
        dest_dir: Path = Path(tmpdir.mkdir("dest_dir"))

        # Create the media test file.
        original_media_path: Path = source_dir / media_filename
        destination_media_dir: Path = dest_dir / organized_dir_path
        destination_media_dir.mkdir(parents=True, exist_ok=False)
        destination_media_path: Path = destination_media_dir / media_filename
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
            overwrite=overwrite,
            delete_original=delete_original,
        )

        expected_new_image_path: Path = dest_dir / organized_dir_path / media_filename
        assert expected_new_image_path.exists()
        assert not original_media_path.exists()

    # TODO: fix delete_original, it does not do what it should do,
    #  that is delete the original files even though it is not
    #  moved to the destination directory. Reconcider this.
