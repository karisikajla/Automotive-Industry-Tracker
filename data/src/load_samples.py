import sys
import os

sys.path.append(os.path.dirname(__file__))

from io_utils import read_json, read_text, read_image, read_srt, setup_logging

if __name__ == "__main__":
    setup_logging("pipeline.log")

    audi  = read_json("data/raw/nhtsa/recall_audi_a4.json")
    if audi:
        print("Audi A4 recalls:", audi["Count"])
        if audi["Count"] > 0:
            print("First recall component:", audi["results"][0]["Component"])

    vw = read_json("data/raw/nhtsa/recall_volkswagen_golf.json")
    if vw:
        print("Volkswagen Golf recalls:", vw["Count"])

    skoda = read_json("data/raw/nhtsa/recall_skoda_octavia.json")
    if skoda:
        print("Skoda Octavia recalls:", skoda["Count"])

    cupra = read_json("data/raw/nhtsa/recall_cupra_formentor.json")
    if cupra:
        print("Cupra Formentor recalls:", cupra["Count"])

    complaint_text = read_text("data/raw/nhtsa/complaint_audi_a4.txt")
    if complaint_text:
        print("\nFirst 100 characters of complaint:")
        print(complaint_text[:100])

    image_data = read_image("data/raw/listings/audi_a4.jpg")
    if image_data:
        print(f"\nImage loaded: {len(image_data)} bytes")

    srt_text = read_srt("data/raw/subtitles/complaint_audi_a4.srt")
    if srt_text:
        print("\nFirst 100 characters of SRT:")
        print(srt_text[:100])