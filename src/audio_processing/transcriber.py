import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from faster_whisper import WhisperModel
from pydub import AudioSegment
from utils.logger import logging as logger



_model = None

def get_model(model_size="base", device="cpu", compute_type="int8"):
    global _model
    if _model is None:
        logger.info(f"Loading Whisper model: {model_size}")
        _model = WhisperModel(model_size, device=device, compute_type=compute_type)
        logger.info("Whisper model loaded.")
    return _model

def transcribe_audio(file_path, model_size="base"):
    model = get_model(model_size)
    logger.info(f"Transcribing: {file_path}")

    segments_generator, info = model.transcribe(file_path, word_timestamps=True)
    segments = list(segments_generator)

    result = {
        "source_file": file_path,
        "language": info.language,
        "language_probability": round(info.language_probability, 4),
        "duration": round(info.duration, 2),
        "model": model_size,
        "segments": []
    }

    for seg in segments:
        segment_data = {
            "start": round(seg.start, 2),
            "end": round(seg.end, 2),
            "text": seg.text.strip(),
            "words": []
        }
        if seg.words:
            for word in seg.words:
                segment_data["words"].append({
                    "word": word.word,
                    "start": round(word.start, 2),
                    "end": round(word.end, 2),
                    "probability": round(word.probability, 4)
                })
        result["segments"].append(segment_data)

    logger.info(f"Transcription complete. Language: {info.language}, Segments: {len(result['segments'])}")
    return result

def save_transcript_json(result, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    logger.info(f"Transcript saved as JSON: {output_path}")

def save_transcript_txt(result, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for seg in result["segments"]:
            f.write(f"[{seg['start']}s - {seg['end']}s] {seg['text']}\n")
    logger.info(f"Transcript saved as TXT: {output_path}")

def save_transcript_srt(result, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    def format_time(seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"

    with open(output_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(result["segments"], 1):
            f.write(f"{i}\n")
            f.write(f"{format_time(seg['start'])} --> {format_time(seg['end'])}\n")
            f.write(f"{seg['text']}\n\n")
    logger.info(f"Transcript saved as SRT: {output_path}")

def chunked_transcribe(file_path, model_size="base", chunk_duration_ms=300000):
    logger.info(f"Starting chunked transcription: {file_path}")
    audio = AudioSegment.from_file(file_path)
    total_duration_ms = len(audio)
    chunks = []
    start = 0
    index = 0

    transcripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "transcripts"))
    os.makedirs(transcripts_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(file_path))[0]
    all_segments = []

    while start < total_duration_ms:
        end = min(start + chunk_duration_ms, total_duration_ms)
        chunk = audio[start:end]
        chunk_path = os.path.join(transcripts_dir, f"{base_name}_chunk_{index}.wav")

        chunk_result_path = os.path.join(transcripts_dir, f"{base_name}_chunk_{index}.json")

        if os.path.exists(chunk_result_path):
            logger.info(f"Chunk {index} already transcribed, loading from cache.")
            with open(chunk_result_path, "r", encoding="utf-8") as f:
                chunk_result = json.load(f)
        else:
            chunk.export(chunk_path, format="wav")
            logger.info(f"Transcribing chunk {index} ({start}ms - {end}ms)")
            chunk_result = transcribe_audio(chunk_path, model_size=model_size)

            offset_sec = start / 1000.0
            for seg in chunk_result["segments"]:
                seg["start"] = round(seg["start"] + offset_sec, 2)
                seg["end"] = round(seg["end"] + offset_sec, 2)
                for word in seg.get("words", []):
                    word["start"] = round(word["start"] + offset_sec, 2)
                    word["end"] = round(word["end"] + offset_sec, 2)

            save_transcript_json(chunk_result, chunk_result_path)

        all_segments.extend(chunk_result["segments"])
        chunks.append(chunk_result)
        start = end
        index += 1

    combined_result = {
        "source_file": file_path,
        "language": chunks[0]["language"] if chunks else "unknown",
        "duration": round(total_duration_ms / 1000.0, 2),
        "model": model_size,
        "segments": all_segments
    }

    combined_path = os.path.join(transcripts_dir, f"{base_name}_combined.json")
    save_transcript_json(combined_result, combined_path)
    logger.info(f"Chunked transcription complete. Total segments: {len(all_segments)}")
    return combined_result


if __name__ == "__main__":
    audio_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "audio"))
    transcripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "transcripts"))

    audio_files = [f for f in os.listdir(audio_dir) if f.endswith((".mp3", ".wav", ".flac", ".ogg"))]

    if not audio_files:
        print("No audio files found.")
        sys.exit(1)

    # Part 9 - Short audio transcription
    sample_file = os.path.join(audio_dir, audio_files[0])
    print(f"\nTranscribing: {audio_files[0]}")
    result = transcribe_audio(sample_file)

    print(f"  Language      : {result['language']} ({result['language_probability']})")
    print(f"  Duration      : {result['duration']}s")
    print(f"  Segments      : {len(result['segments'])}")
    print(f"  Text preview  : {result['segments'][0]['text'] if result['segments'] else 'N/A'}")

    base_name = os.path.splitext(audio_files[0])[0]
    save_transcript_json(result, os.path.join(transcripts_dir, f"{base_name}.json"))
    save_transcript_txt(result, os.path.join(transcripts_dir, f"{base_name}.txt"))
    save_transcript_srt(result, os.path.join(transcripts_dir, f"{base_name}.srt"))
    print("Transcripts saved in JSON, TXT, SRT formats.")

    # Part 10 - Chunked transcription
    if len(audio_files) >= 2:
        long_file = os.path.join(audio_dir, audio_files[1])
    else:
        long_file = sample_file

    print(f"\nChunked transcription: {os.path.basename(long_file)}")
    chunked_result = chunked_transcribe(long_file, chunk_duration_ms=300000)
    print(f"  Total segments: {len(chunked_result['segments'])}")
    print("Chunked transcription complete.")