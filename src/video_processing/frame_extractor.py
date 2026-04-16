import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import cv2
from utils.logger import logging as logger



def save_frame(video_path, t_seconds, output_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.warning(f"Could not open video: {video_path}")
        return None

    try:
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_number = int(t_seconds * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        if not ret:
            logger.warning(f"Could not read frame at {t_seconds}s from {video_path}")
            return None

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, frame)
        logger.info(f"Saved frame at {t_seconds}s to {output_path}")
        return output_path
    finally:
        cap.release()

def extract_keyframes(video_path, output_dir, interval_seconds=10):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.warning(f"Could not open video: {video_path}")
        return []

    try:
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration_sec = total_frames / fps if fps > 0 else 0

        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(video_path))[0]

        saved_frames = []
        t = 0
        while t < duration_sec:
            frame_number = int(t * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()
            if not ret:
                logger.warning(f"Could not read frame at {t}s")
                t += interval_seconds
                continue

            output_path = os.path.join(output_dir, f"{base_name}_frame_{int(t):04d}s.png")
            cv2.imwrite(output_path, frame)
            logger.info(f"Saved keyframe at {t}s -> {output_path}")
            saved_frames.append({
                "timestamp_sec": t,
                "frame_path": output_path
            })
            t += interval_seconds

        logger.info(f"Extracted {len(saved_frames)} keyframes from {video_path}")
        return saved_frames
    finally:
        cap.release()


if __name__ == "__main__":
    video_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "video"))
    frames_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "frames"))

    supported = [".mp4", ".avi", ".mov", ".mkv", ".webm"]
    video_files = [f for f in os.listdir(video_dir) if os.path.splitext(f)[1].lower() in supported]

    if not video_files:
        print("No video files found in data/raw/video/")
    else:
        for video_file in video_files:
            video_path = os.path.join(video_dir, video_file)
            base_name = os.path.splitext(video_file)[0]
            output_dir = os.path.join(frames_dir, base_name)

            print(f"\nExtracting keyframes from: {video_file}")
            frames = extract_keyframes(video_path, output_dir, interval_seconds=10)
            print(f"  Extracted {len(frames)} frames to {output_dir}")
            for f in frames:
                print(f"    t={f['timestamp_sec']}s -> {os.path.basename(f['frame_path'])}")