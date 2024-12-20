# pylint: disable=too-few-public-methods
"""Test retrieving creation date from files."""

from datetime import datetime
from pathlib import Path

import piexif

from media_organizer.date_fetcher import (
    extract_creation_date,
    get_accurate_img_date,
    get_accurate_media_date,
    get_fast_date,
)

from .create_img import create_mock_image
from .create_video import add_creation_date_to_video, create_test_video


def create_test_files(tmpdir):
    """Generate dummy test files on the filesystem."""
    # Create test image and video files
    image_file = tmpdir.join("test_image.jpg")
    video_file = tmpdir.join("test_video.mp4")

    image_file.write("fake_image_data")
    video_file.write("fake_video_data")

    return image_file, video_file


def test_extract_creation_date(monkeypatch, tmpdir):
    """Test extract creation date."""

    def mock_run(*args, **kwargs):  # pylint: disable=unused-argument
        """Mock subprocess call."""

        class MockResult:
            """Mocked result with fixed date."""

            stdout = "2023:05:20 15:45:50"
            stderr = ""

        return MockResult()

    monkeypatch.setattr("subprocess.run", mock_run)

    _, video_file = create_test_files(tmpdir)
    result = extract_creation_date(video_file)

    assert result == datetime(2023, 5, 20, 15, 45, 50)


def test_get_fast_date(tmpdir):
    """Test extract date from files using fast mode."""
    image_file, _ = create_test_files(tmpdir)
    result_date: datetime | None = get_fast_date(Path(image_file))

    assert result_date

    # Here, we're asserting against the current date.
    # This will be true because the file was just created.
    current_date = datetime.now().strftime("%Y%m%d")
    test_date = result_date.strftime("%Y%m%d")
    assert current_date == test_date


def test_get_accurate_img_date_with_exif(monkeypatch, tmpdir):
    """Test extract creation date from a file using accurate method."""
    # Simulated EXIF data
    mocked_exif_data = {
        "0th": {},
        "Exif": {piexif.ExifIFD.DateTimeOriginal: b"2023:05:20 15:45:50"},
        "GPS": {},
        "1st": {},
        "thumbnail": None,
    }

    # Mock piexif.load to return the simulated EXIF data
    monkeypatch.setattr(piexif, "load", lambda x: mocked_exif_data)

    image_file, _ = create_test_files(tmpdir)
    result = get_accurate_img_date(Path(image_file))

    assert result == datetime(2023, 5, 20, 15, 45, 50)

    result = get_accurate_media_date(Path(image_file))
    assert result == datetime(2023, 5, 20, 15, 45, 50)


def test_image_creation_date_extraction(tmpdir):
    """Test extract creation date from a image using accurate method."""
    # Create test image with a creation date
    image_path = tmpdir.join("test_image.jpg")
    create_mock_image(image_path, "2023:05:20 15:45:50")

    # Extract the date using your function
    extracted_date = get_accurate_img_date(Path(image_path))

    # Assert that the extracted date matches
    assert extracted_date == datetime(2023, 5, 20, 15, 45, 50)


def test_video_creation_date_extraction(tmpdir):
    """Test extract creation date from a video using accurate method."""
    video_path = tmpdir.join("test_video.mp4")
    create_test_video(str(video_path))
    new_video_path: str = add_creation_date_to_video(video_path, "2023-05-20T15:45:50")

    # Extract the date using your function
    extracted_date = get_accurate_media_date(Path(new_video_path))
    assert extracted_date == datetime(2023, 5, 20, 15, 45, 50)
