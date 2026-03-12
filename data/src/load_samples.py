import sys
import os

sys.path.append(os.path.dirname(__file__))

from io_utils import read_json, setup_logging

if __name__ == "__main__":
    setup_logging("pipeline.log")

    # Read recall data for each vehicle (equivalent to movie_11.json in the lab)
    audi     = read_json("data/raw/nhtsa/recall_audi_a4.json")
    vw       = read_json("data/raw/nhtsa/recall_volkswagen_golf.json")
    skoda    = read_json("data/raw/nhtsa/recall_skoda_octavia.json")
    cupra    = read_json("data/raw/nhtsa/recall_cupra_formentor.json")

    # Print summary for each vehicle
    if audi:
        print(f"Audi A4 recalls: {audi['Count']}")
        if audi["Count"] > 0:
            print(f"  First recall: {audi['results'][0]['Component']}")

    if vw:
        print(f"Volkswagen Golf recalls: {vw['Count']}")

    if skoda:
        print(f"Skoda Octavia recalls: {skoda['Count']}")

    if cupra:
        print(f"Cupra Formentor recalls: {cupra['Count']}")
