import argparse
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")))

from visualization.chart_generator import run_all_charts

def main():
    parser = argparse.ArgumentParser(description="Generate all automotive recall visualizations")
    parser.add_argument("--data", type=str, default=None, help="Path to CSV file (optional)")
    args = parser.parse_args()
    run_all_charts(csv_path=args.data)

if __name__ == "__main__":
    main()
