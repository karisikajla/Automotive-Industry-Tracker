import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from moviepy import VideoFileClip
from src.logger import get_logger

logger = get_logger()

def load_video(file_path):
    if not os.path.exists(file_path):
        logger.warning(f"Video file not found: {file_path}")
        return None
    clip = VideoFileClip(file_path)
    logger.info(f"Loaded video file: {file_path}")
    return clip

def inspect_video(file_path):
    clip = load_video(file_path)
    if clip is None:
        return None

    try:
        info = {
            "filename": os.path.basename(file_path),
            "duration_sec": round(clip.duration, 2),
            "fps": clip.fps,
            "resolution": f"{clip.w}x{clip.h}",
            "width": clip.w,
            "height": clip.h,
            "has_audio": clip.audio is not None,
            "file_size_kb": round(os.path.getsize(file_path) / 1024, 1)
        }
        logger.info(f"Inspected video: {info}")
        return info
    finally:
        clip.close()

def print_video_info(info):
    if info is None:
        print("No video info available.")
        return
    print(f"  filename      : {info['filename']}")
    print(f"  duration_sec  : {info['duration_sec']}")
    print(f"  fps           : {info['fps']}")
    print(f"  resolution    : {info['resolution']}")
    print(f"  has_audio     : {info['has_audio']}")
    print(f"  file_size_kb  : {info['file_size_kb']}")

def extract_audio_from_video(file_path, output_path):
    clip = load_video(file_path)
    if clip is None:
        return None

    try:
        if clip.audio is None:
            logger.warning(f"No audio track found in video: {file_path}")
            return None

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        clip.audio.write_audiofile(output_path)
        logger.info(f"Extracted audio from video: {file_path} -> {output_path}")
        return output_path
    finally:
        clip.close()

def load_all_videos(video_dir):
    if not os.path.exists(video_dir):
        logger.warning(f"Video directory not found: {video_dir}")
        return []

    supported = [".mp4", ".avi", ".mov", ".mkv", ".webm"]
    results = []
    for fname in os.listdir(video_dir):
        ext = os.path.splitext(fname)[1].lower()
        if ext in supported:
            full_path = os.path.join(video_dir, fname)
            info = inspect_video(full_path)
            if info:
                results.append(info)
    return results


if __name__ == "__main__":
    video_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "video"))
    processed_audio_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "audio"))

    videos = load_all_videos(video_dir)

    if not videos:
        print("No video files found in data/raw/video/")
    else:
        for info in videos:
            print_video_info(info)
            print()

        # Extract audio from first video
        first_video = os.path.join(video_dir, videos[0]["filename"])
        output_audio = os.path.join(processed_audio_dir, "extracted_from_video.mp3")
        result = extract_audio_from_video(first_video, output_audio)
        if result:
            print(f"Audio extracted to: {result}")