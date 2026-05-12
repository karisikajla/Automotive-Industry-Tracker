import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))

from utils.logger import logging
from storage.mongo import save_to_mongo
from storage.s3 import upload_file_to_s3
from api.client import fetch_all_vehicles
from extraction.pdf_extractor import extract_all_pdfs
from extraction.word_extractor import extract_all_word_docs
from extraction.excel_extractor import extract_all_excel
from scraping.scraper import run_scraper
from scraping.dynamic_scraper import run_dynamic_scraper
from ocr.ocr_utils import run_ocr_pipeline
from image_processing.downloader import download_vehicle_images
from image_processing.batch import batch_process_images
from image_processing.exif_utils import process_exif_samples
from audio_processing.loader import load_all_audio, print_audio_info
from audio_processing.processor import trim_audio, concatenate_audio, adjust_volume, apply_fade, convert_audio, save_audio
from audio_processing.transcriber import transcribe_audio, save_transcript_json, save_transcript_txt, save_transcript_srt, chunked_transcribe
from video_processing.loader import load_all_videos, print_video_info, extract_audio_from_video
from video_processing.frame_extractor import extract_keyframes
from storage.mongo import save_transcript_to_mongo
from pydub import AudioSegment
from analytics.numpy_ops import run_numpy_analysis
from analytics.data_loader import load_from_mongodb, save_to_csv, compute_global_mean_rating, process_chunks_per_source, optimize_dtypes
from analytics.explorer import run_exploration
from analytics.selector import run_selection_demo
from analytics.regex_ops import run_regex_analysis
from analytics.quality_report import full_quality_audit, plot_missing_heatmap
from cleaning.clean_pipeline import run_cleaning_pipeline
from analytics.data_loader import load_from_csv

def run_pipeline():
    logging.info("Pipeline started")

    # Fetch data from API
    logging.info("Fetching data from NHTSA API")
    vehicles = fetch_all_vehicles(pages=3)
    logging.info(f"Fetched data for {len(vehicles)} vehicles")

    for vehicle in vehicles:
        save_to_mongo(vehicle, "nhtsa_api")
        make = vehicle["make"]
        model = vehicle["model"]
        year = vehicle["year"]
        filename = f"recalls_{make}_{model}_{year}.json"
        file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "data", "raw", "api", filename
        )
        upload_file_to_s3(file_path, filename)

    # Extract PDF documents
    logging.info("Extracting PDF documents")
    pdf_results = extract_all_pdfs()
    logging.info(f"Extracted {len(pdf_results)} PDF files")

    # Extract Word documents
    logging.info("Extracting Word documents")
    word_results = extract_all_word_docs()
    logging.info(f"Extracted {len(word_results)} Word files")

    # Extract Excel files
    logging.info("Extracting Excel files")
    excel_results = extract_all_excel()
    logging.info(f"Extracted {len(excel_results)} Excel files")

    # Web scraping
    logging.info("Running web scraper")
    scraped_results = run_scraper()
    logging.info(f"Scraped {len(scraped_results)} records")

    # Dynamic scraping
    logging.info("Running dynamic scraper")
    dynamic_results = run_dynamic_scraper()
    logging.info(f"Dynamic scraped {len(dynamic_results)} records")

    # OCR
    logging.info("Running OCR pipeline")
    ocr_results = run_ocr_pipeline()
    logging.info(f"OCR processed {len(ocr_results)} files")

    # Download vehicle images
    logging.info("Downloading vehicle images")
    downloaded = download_vehicle_images()
    logging.info(f"Downloaded {len(downloaded)} images")

    # Batch process images
    logging.info("Batch processing images")
    image_results = batch_process_images()
    logging.info(f"Processed {len(image_results)} images")

    # Process EXIF samples
    logging.info("Processing EXIF samples")
    exif_results = process_exif_samples()
    logging.info(f"Processed {len(exif_results)} EXIF samples")

    logging.info("Starting audio processing")
    audio_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "raw", "audio"))
    processed_audio_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "processed", "audio"))
    os.makedirs(processed_audio_dir, exist_ok=True)

    # Task 1 - Load and inspect all audio files
    all_audio_info = load_all_audio(audio_dir)
    logging.info(f"Loaded and inspected {len(all_audio_info)} audio files")
    for info in all_audio_info:
        print_audio_info(info)

    audio_files = [f for f in os.listdir(audio_dir) if f.endswith((".mp3", ".wav", ".flac", ".ogg"))]

    if audio_files:
        audio1 = AudioSegment.from_file(os.path.join(audio_dir, audio_files[0]))

        # Task 2 - Trim
        trimmed = trim_audio(audio1, 0, 10000)
        save_audio(trimmed, os.path.join(processed_audio_dir, "trimmed.wav"), format="wav")
        logging.info("Trimmed audio saved")

        # Task 3 - Concatenate
        if len(audio_files) >= 2:
            audio2 = AudioSegment.from_file(os.path.join(audio_dir, audio_files[1]))
            combined = concatenate_audio([trimmed, audio2[:10000]])
            save_audio(combined, os.path.join(processed_audio_dir, "concatenated.wav"), format="wav")
            logging.info("Concatenated audio saved")

        # Task 4 - Volume and fade
        louder = adjust_volume(audio1[:10000], +5)
        quieter = adjust_volume(audio1[:10000], -5)
        faded = apply_fade(audio1[:15000], fade_in_ms=2000, fade_out_ms=2000)
        save_audio(louder, os.path.join(processed_audio_dir, "louder.wav"), format="wav")
        save_audio(quieter, os.path.join(processed_audio_dir, "quieter.wav"), format="wav")
        save_audio(faded, os.path.join(processed_audio_dir, "faded.wav"), format="wav")
        logging.info("Volume and fade audio saved")

        # Task 5 - Convert format
        convert_audio(audio1, os.path.join(processed_audio_dir, "converted.mp3"), format="mp3", bitrate="192k")
        convert_audio(audio1, os.path.join(processed_audio_dir, "converted.flac"), format="flac")
        logging.info("Audio format conversion complete")

    logging.info("Starting video processing")
    video_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "raw", "video"))
    frames_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "processed", "frames"))
    os.makedirs(frames_dir, exist_ok=True)

    # Task 6 - Load and inspect videos, extract audio
    all_video_info = load_all_videos(video_dir)
    logging.info(f"Loaded and inspected {len(all_video_info)} video files")
    for info in all_video_info:
        print_video_info(info)

    video_files = [f for f in os.listdir(video_dir) if f.endswith((".mp4", ".avi", ".mov", ".mkv", ".webm"))]

    extracted_audio_path = None
    if video_files:
        first_video = os.path.join(video_dir, video_files[0])
        extracted_audio_path = os.path.join(processed_audio_dir, "extracted_from_video.mp3")
        extract_audio_from_video(first_video, extracted_audio_path)
        logging.info(f"Audio extracted from video: {extracted_audio_path}")

        # Task 7 - Extract keyframes
        for video_file in video_files:
            video_path = os.path.join(video_dir, video_file)
            base_name = os.path.splitext(video_file)[0]
            output_dir = os.path.join(frames_dir, base_name)
            frames = extract_keyframes(video_path, output_dir, interval_seconds=10)
            logging.info(f"Extracted {len(frames)} keyframes from {video_file}")

    logging.info("Starting transcription")
    transcripts_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "processed", "transcripts"))
    os.makedirs(transcripts_dir, exist_ok=True)

    if audio_files:
        # Task 8 - Transcribe short audio
        sample_file = os.path.join(audio_dir, audio_files[0])
        result = transcribe_audio(sample_file)
        base_name = os.path.splitext(audio_files[0])[0]
        save_transcript_json(result, os.path.join(transcripts_dir, f"{base_name}.json"))
        save_transcript_txt(result, os.path.join(transcripts_dir, f"{base_name}.txt"))
        save_transcript_srt(result, os.path.join(transcripts_dir, f"{base_name}.srt"))
        save_transcript_to_mongo(result)
        logging.info(f"Short audio transcription complete: {audio_files[0]}")

        # Task 9 - Transcribe audio from video
        if extracted_audio_path and os.path.exists(extracted_audio_path):
            video_transcript = transcribe_audio(extracted_audio_path)
            save_transcript_json(video_transcript, os.path.join(transcripts_dir, "video_audio_transcript.json"))
            save_transcript_txt(video_transcript, os.path.join(transcripts_dir, "video_audio_transcript.txt"))
            save_transcript_srt(video_transcript, os.path.join(transcripts_dir, "video_audio_transcript.srt"))
            save_transcript_to_mongo(video_transcript)
            logging.info("Video audio transcription complete")

        # Task 10 - Chunked transcription
        long_file = os.path.join(audio_dir, audio_files[-1])
        chunked_result = chunked_transcribe(long_file, chunk_duration_ms=300000)
        save_transcript_to_mongo(chunked_result)
        logging.info(f"Chunked transcription complete: {len(chunked_result['segments'])} segments")

    logging.info("Starting Lab 8 analytics")

    run_numpy_analysis()
    logging.info("NumPy analysis complete")

    df = load_from_mongodb()
    csv_path = save_to_csv(df)
    logging.info(f"MongoDB data exported to CSV: {csv_path}")

    mean_rating = compute_global_mean_rating()
    logging.info(f"Global mean rating: {mean_rating}")

    sources = process_chunks_per_source()
    logging.info(f"Chunk processing per source complete: {list(sources.keys())}")

    df = optimize_dtypes(df)

    df, chart_paths = run_exploration(df)
    logging.info(f"EDA complete, charts saved: {chart_paths}")

    run_selection_demo(df)
    logging.info("Selection demo complete")

    run_regex_analysis(df)
    logging.info("Regex analysis complete")

    full_quality_audit(df)
    plot_missing_heatmap(df)
    logging.info("Quality audit complete")
    
    logging.info("Starting Lab 9 cleaning pipeline")
    df_raw = load_from_csv()
    if df_raw is not None:
        df_clean = run_cleaning_pipeline(df_raw)
        logging.info(f"Cleaning pipeline complete, final shape: {df_clean.shape}")
        
        
    logging.info("Starting Lab 10 analytics pipeline")
    import pandas as pd
    import sqlalchemy
    from analytics.db_connector import populate_financials, query_financials
    from analytics.data_combiner import merge_dataframes, compare_join_types
    from analytics.aggregator import genre_summary, yearly_trends, top_n_per_group
    from analytics.pivot_builder import wide_to_long, build_pivot_table, build_crosstab
    from analytics.time_series import parse_dates, extract_date_components, monthly_time_series, rolling_averages
    from analytics.mongo_pipeline import get_mongo_collection, run_aggregation_pipeline
    from analytics.insight_reporter import run_all_questions

    analytics_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "processed", "analytics"))
    os.makedirs(analytics_dir, exist_ok=True)

    cleaned_csv = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "processed", "cleaned", "cleaned_data.csv"))
    df_analytics = pd.read_csv(cleaned_csv)
    logging.info(f"Loaded cleaned CSV: {len(df_analytics)} rows")

    populate_financials(df_analytics)
    engine = sqlalchemy.create_engine("mysql+pymysql://root:@localhost/automotive_tracker")
    df_mysql = pd.read_sql("SELECT * FROM vehicle_financials WHERE year IS NOT NULL", engine)
    logging.info(f"MySQL rows: {len(df_mysql)}")

    df_filtered = df_analytics[~df_analytics["data.make"].isin(["Unknown", "UNKNOWN"])].copy()
    df_mongo_style = df_filtered[["data.make", "data.model", "data.year", "source", "release_year"]].copy()
    df_mongo_style.columns = ["make", "model", "year", "source", "release_year"]
    df_mysql_clean = df_mysql[df_mysql["make"] != "Unknown"].copy()

    join_counts = compare_join_types(df_mongo_style, df_mysql_clean, on="make")
    logging.info(f"Join counts: {join_counts}")

    df_combined = merge_dataframes(df_mongo_style, df_mysql_clean, on="make", how="inner")

    summary = genre_summary(df_combined, group_col="make", value_col="recall_count")
    summary.to_csv(os.path.join(analytics_dir, "genre_analysis.csv"), index=False)
    logging.info("Saved genre_analysis.csv")

    trends = yearly_trends(df_combined, year_col="year_x", value_col="recall_count")
    trends.to_csv(os.path.join(analytics_dir, "yearly_trends.csv"), index=False)
    logging.info("Saved yearly_trends.csv")

    pivot = build_pivot_table(df_combined, index="make", columns="source_x", values="recall_count", aggfunc="mean", margins=True)
    pivot.to_csv(os.path.join(analytics_dir, "pivot_make_source.csv"))
    logging.info("Saved pivot_make_source.csv")

    df_combined, valid, missing = parse_dates(df_combined, date_col="fetched_at")
    df_combined = extract_date_components(df_combined, date_col="fetched_at")
    logging.info(f"Date parsing: {valid} valid, {missing} missing")

    collection = get_mongo_collection(db_name="automotive_pipeline", collection_name="raw_recalls")
    df_mongo_agg = run_aggregation_pipeline(collection)
    logging.info(f"MongoDB pipeline: {len(df_mongo_agg)} results")

    run_all_questions(df_combined, df_mongo_agg)
    logging.info("Lab 10 analytics pipeline complete")

    logging.info("Pipeline finished successfully")

run_pipeline()