import subprocess

import cv2
import numpy as np


def create_test_video(file_path: str, duration_seconds: int = 1):
    # Define the codec using VideoWriter_fourcc
    fourcc = cv2.VideoWriter_fourcc(*"XVID")

    # Create a VideoWriter object
    out = cv2.VideoWriter(file_path, fourcc, 20.0, (640, 480))

    for _ in range(20 * duration_seconds):  # 20 frames per second
        # Create a random frame (640x480x3)
        frame = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
        out.write(frame)

    # Release the VideoWriter object
    out.release()


# def create_test_video(file_path: str):
#    fourcc = cv2.VideoWriter_fourcc(*'XVID')
#    out = cv2.VideoWriter(file_path, fourcc, 20.0, (640, 480))
#
#    for _ in range(10):
#        frame = np.random.randint(0, 255, (480, 640, 3)).astype('uint8')
#        out.write(frame)
#    out.release()


def add_creation_date_to_video(video_path: str, date_str: str) -> str:
    # This uses ffmpeg to add metadata to the video
    new_video_file_path: str = f"{video_path}_with_date.mp4"
    cmd = [
        "ffmpeg",
        "-i",
        video_path,
        "-metadata",
        f"creation_time={date_str}",
        "-codec",
        "copy",
        new_video_file_path,
    ]
    subprocess.run(cmd)
    return new_video_file_path


# def create_test_video_with_date(file_path: str, date_str: str):
#    create_test_video(file_path)
#    add_creation_date_to_video(file_path, date_str)
