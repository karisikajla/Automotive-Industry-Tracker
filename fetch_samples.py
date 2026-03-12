import requests
import os
import re
import sys

sys.path.append("data/src")
from io_utils import setup_logging

setup_logging("pipeline.log")

os.makedirs("data/raw/nhtsa", exist_ok=True)
os.makedirs("data/raw/listings", exist_ok=True)
os.makedirs("data/raw/subtitles", exist_ok=True)

print("Fetching NHTSA complaints for AUDI A4 2020...")
response = requests.get(
    "https://api.nhtsa.gov/complaints/complaintsByVehicle",
    params={"make": "AUDI", "model": "A4", "modelYear": "2020"}
)
data = response.json()
complaint = data["results"][0]

text_content = (
    f"NHTSA Complaint Report\n"
    f"======================\n"
    f"Date Filed : {complaint.get('dateComplaintFiled', '')}\n"
    f"Vehicle    : 2020 AUDI A4\n"
    f"Component  : {complaint.get('components', '')}\n"
    f"\nSummary:\n{complaint.get('summary', '')}\n"
)

with open("data/raw/nhtsa/complaint_audi_a4.txt", "w", encoding="utf-8") as f:
    f.write(text_content)
print("Text file saved: complaint_audi_a4.txt")

print("Fetching Audi A4 image URL from Wikipedia API...")
wiki_response = requests.get(
    "https://en.wikipedia.org/api/rest_v1/page/summary/Audi_A4",
    headers={"User-Agent": "AutomotiveTracker/1.0"}
)
wiki_data = wiki_response.json()
image_url = wiki_data["thumbnail"]["source"]
print(f"Image URL from API: {image_url}")

img_response = requests.get(image_url, headers={"User-Agent": "AutomotiveTracker/1.0"})
with open("data/raw/listings/audi_a4.jpg", "wb") as f:
    f.write(img_response.content)
print("Image saved: audi_a4.jpg")


summary = complaint.get("summary", "")
sentences = re.split(r'(?<=[.!?])\s+', summary)
sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

srt_lines = []
for i, sentence in enumerate(sentences, start=1):
    start_sec = (i - 1) * 4
    end_sec = i * 4

    def fmt_time(sec):
        h = sec // 3600
        m = (sec % 3600) // 60
        s = sec % 60
        return f"{h:02}:{m:02}:{s:02},000"

    srt_lines.append(str(i))
    srt_lines.append(f"{fmt_time(start_sec)} --> {fmt_time(end_sec)}")
    srt_lines.append(sentence[:80])
    srt_lines.append("")

with open("data/raw/subtitles/complaint_audi_a4.srt", "w", encoding="utf-8") as f:
    f.write("\n".join(srt_lines))
print(f"SRT file saved: complaint_audi_a4.srt ({len(sentences)} subtitles)")

print("\nAll sample files created!")