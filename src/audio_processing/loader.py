import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pydub import AudioSegment
from utils.logger import logging as logger

SUPPORTED_FORMATS = ["mp3", "wav", "flac", "ogg", "aac"]

def load_audio(file_path):
    ext = os.path.splitext(file_path)[1].lower().replace(".", "")
    if ext not in SUPPORTED_FORMATS:
        logger.warning(f"Unsupported audio format: {ext} for file {file_path}")
        return None
    audio = AudioSegment.from_file(file_path, format=ext)
    logger.info(f"Loaded audio file: {file_path}")
    return audio

def inspect_audio(file_path):
    ext = os.path.splitext(file_path)[1].lower().replace(".", "")
    audio = load_audio(file_path)
    if audio is None:
        return None

    duration_sec = len(audio) / 1000.0
    channels = audio.channels
    channel_type = "Stereo" if channels == 2 else "Mono"
    frame_rate = audio.frame_rate
    bit_depth = audio.sample_width * 8
    file_size_kb = os.path.getsize(file_path) / 1024

    info = {
        "filename": os.path.basename(file_path),
        "format": ext.upper(),
        "duration_sec": round(duration_sec, 2),
        "channels": channels,
        "channel_type": channel_type,
        "frame_rate_hz": frame_rate,
        "bit_depth": bit_depth,
        "file_size_kb": round(file_size_kb, 1)
    }

    logger.info(f"Inspected audio: {info}")
    return info

def print_audio_info(info):
    if info is None:
        print("No audio info available.")
        return
    print(f"  filename      : {info['filename']}")
    print(f"  format        : {info['format']}")
    print(f"  duration_sec  : {info['duration_sec']}")
    print(f"  channels      : {info['channels']}")
    print(f"  channel_type  : {info['channel_type']}")
    print(f"  frame_rate_hz : {info['frame_rate_hz']}")
    print(f"  bit_depth     : {info['bit_depth']}")
    print(f"  file_size_kb  : {info['file_size_kb']}")

def load_all_audio(audio_dir):
    if not os.path.exists(audio_dir):
        logger.warning(f"Audio directory not found: {audio_dir}")
        return []
    
    results = []
    for fname in os.listdir(audio_dir):
        ext = os.path.splitext(fname)[1].lower().replace(".", "")
        if ext in SUPPORTED_FORMATS:
            full_path = os.path.join(audio_dir, fname)
            info = inspect_audio(full_path)
            if info:
                results.append(info)
    return results


if __name__ == "__main__":
    audio_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "audio"))
    all_audio = load_all_audio(audio_dir)
    for info in all_audio:
        print_audio_info(info)
        print()