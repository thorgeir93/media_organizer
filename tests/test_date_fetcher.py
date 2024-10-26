import pytest
import piexif
from pathlib import Path
from datetime import datetime

from media_organizer.date_fetcher import extract_creation_date
from media_organizer.date_fetcher import get_accurate_media_date
from media_organizer.date_fetcher import get_accurate_img_date
from media_organizer.date_fetcher import get_fast_date

from .create_img import create_mock_image
from .create_video import create_test_video, add_creation_date_to_video


def create_test_files(tmpdir):
    # Create test image and video files
    image_file = tmpdir.join("test_image.jpg")
    video_file = tmpdir.join("test_video.mp4")

    image_file.write("fake_image_data")
    video_file.write("fake_video_data")

    return image_file, video_file


def test_extract_creation_date(monkeypatch, tmpdir):
    # Mock subprocess call for testing purposes
    def mock_run(*args, **kwargs):
        class MockResult:
            stdout = "2023:05:20 15:45:50"
            stderr = ""

        return MockResult()

    monkeypatch.setattr("subprocess.run", mock_run)

    _, video_file = create_test_files(tmpdir)
    result = extract_creation_date(video_file)

    assert result == datetime(2023, 5, 20, 15, 45, 50)


def test_get_fast_date(tmpdir):
    image_file, _ = create_test_files(tmpdir)
    result_date = get_fast_date(Path(image_file))

    # Here, we're asserting against the current date.
    # This will be true because the file was just created.
    current_date = datetime.now().strftime("%Y%m%d")
    test_date = result_date.strftime("%Y%m%d")
    assert current_date == test_date


def test_get_accurate_img_date_with_exif(monkeypatch, tmpdir):
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
    # Create test image with a creation date
    image_path = tmpdir.join("test_image.jpg")
    create_mock_image(image_path, "2023:05:20 15:45:50")

    # Extract the date using your function
    extracted_date = get_accurate_img_date(Path(image_path))

    # Assert that the extracted date matches
    assert extracted_date == datetime(2023, 5, 20, 15, 45, 50)


def test_video_creation_date_extraction(tmpdir):
    # Create test video
    video_path = tmpdir.join("test_video.mp4")
    create_test_video(str(video_path))
    new_video_path: str = add_creation_date_to_video(video_path, "2023-05-20T15:45:50")

    # Extract the date using your function
    extracted_date = get_accurate_media_date(Path(new_video_path))
    print(extracted_date)
    assert extracted_date == datetime(2023, 5, 20, 15, 45, 50)
