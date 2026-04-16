import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pydub import AudioSegment
from src.logger import get_logger

logger = get_logger()

def trim_audio(audio, start_ms, end_ms):
    trimmed = audio[start_ms:end_ms]
    logger.info(f"Trimmed audio from {start_ms}ms to {end_ms}ms")
    return trimmed

def concatenate_audio(audio_list):
    combined = audio_list[0]
    for segment in audio_list[1:]:
        combined = combined + segment
    logger.info(f"Concatenated {len(audio_list)} audio segments")
    return combined

def adjust_volume(audio, db_change):
    adjusted = audio + db_change
    logger.info(f"Adjusted volume by {db_change}dB")
    return adjusted

def apply_fade(audio, fade_in_ms=1000, fade_out_ms=1000):
    faded = audio.fade_in(fade_in_ms).fade_out(fade_out_ms)
    logger.info(f"Applied fade-in {fade_in_ms}ms and fade-out {fade_out_ms}ms")
    return faded

def convert_audio(audio, output_path, format, bitrate="192k"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if format in ["mp3", "ogg", "aac"]:
        audio.export(output_path, format=format, bitrate=bitrate)
    else:
        audio.export(output_path, format=format)
    logger.info(f"Converted and saved audio to {output_path} as {format}")
    return output_path

def save_audio(audio, output_path, format="wav", bitrate="192k"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if format in ["mp3", "ogg", "aac"]:
        audio.export(output_path, format=format, bitrate=bitrate)
    else:
        audio.export(output_path, format=format)
    logger.info(f"Saved audio to {output_path}")
    return output_path


if __name__ == "__main__":
    from src.audio_processing.loader import load_audio

    audio_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "audio"))
    processed_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "audio"))
    os.makedirs(processed_dir, exist_ok=True)

    audio_files = [f for f in os.listdir(audio_dir) if f.endswith((".mp3", ".wav", ".flac", ".ogg"))]

    if len(audio_files) < 1:
        print("No audio files found in data/raw/audio/")
        sys.exit(1)

    # Task 2 - Trim
    audio1 = load_audio(os.path.join(audio_dir, audio_files[0]))
    trimmed = trim_audio(audio1, 0, 10000)
    save_audio(trimmed, os.path.join(processed_dir, "trimmed.wav"), format="wav")
    print("Trimmed audio saved.")

    # Task 3 - Concatenate
    if len(audio_files) >= 2:
        audio2 = load_audio(os.path.join(audio_dir, audio_files[1]))
        combined = concatenate_audio([trimmed, audio2[:10000]])
        save_audio(combined, os.path.join(processed_dir, "concatenated.wav"), format="wav")
        print("Concatenated audio saved.")

    # Task 4 - Volume and fade
    louder = adjust_volume(audio1[:10000], +5)
    quieter = adjust_volume(audio1[:10000], -5)
    faded = apply_fade(audio1[:15000], fade_in_ms=2000, fade_out_ms=2000)
    save_audio(louder, os.path.join(processed_dir, "louder.wav"), format="wav")
    save_audio(quieter, os.path.join(processed_dir, "quieter.wav"), format="wav")
    save_audio(faded, os.path.join(processed_dir, "faded.wav"), format="wav")
    print("Volume and fade files saved.")

    # Task 5 - Convert format
    convert_audio(audio1, os.path.join(processed_dir, "converted.mp3"), format="mp3", bitrate="192k")
    convert_audio(audio1, os.path.join(processed_dir, "converted.flac"), format="flac")
    print("Converted audio files saved.")