# This script is used to clean event data and normalise date formats for Azure AI Search indexing.

import os
import json
import re
from datetime import datetime
from dateutil import parser

# Directory containing the JSON files
INPUT_DIR = "downloaded_blobs"  # Change to actual path where JSON files are stored
OUTPUT_DIR = "output_events"  # New directory for storing individual event files

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Function to normalize date format
def normalize_date(date_str):
    """Convert different date formats to ISO 8601 format for Azure AI Search."""
    if not date_str or date_str.upper() == "UNKNOWN":
        return None  # Set explicitly missing or "UNKNOWN" dates to None (null in JSON)

    # Clean and standardize delimiters
    date_str = date_str.strip().replace("\\", "/").replace("-", "/")

    # Handle UK-style dates with missing years (Assume 2024 for two-digit years)
    uk_date_match = re.match(r"(\d{1,2})/(\d{1,2})/(\d{2,4})", date_str)
    if uk_date_match:
        day, month, year = uk_date_match.groups()
        if len(year) == 2:
            year = f"20{year}"  # Assume 21st century for two-digit years
        date_str = f"{year}-{month}-{day}"  # Convert to YYYY-MM-DD

    try:
        parsed_date = parser.parse(date_str, dayfirst=True)  # UK format prioritizes day first
        return parsed_date.strftime("%Y-%m-%dT00:00:00Z")  # Normalize to ISO 8601
    except (ValueError, TypeError):
        return None  # If parsing fails, return None (null in JSON)

# Function to process a single JSON file
def process_json_file(filepath):
    """Load a JSON file, normalize dates, and split into separate files per event."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)

        for event in data:
            # Normalize event_date
            original_date = event.get("event_date", "").strip() if event.get("event_date") else None
            normalized_date = normalize_date(original_date)
            
            event["event_date"] = normalized_date if normalized_date else None  # Ensure None is explicitly set
            event["event_date_derived"] = normalized_date is None  # Mark as derived if no valid date

            # Normalize document_date (if exists)
            original_doc_date = event.get("document_date", "").strip() if event.get("document_date") else None
            normalized_doc_date = normalize_date(original_doc_date)
            
            event["document_date"] = normalized_doc_date if normalized_doc_date else None  # Ensure None is explicitly set

            # Save each event as an individual file
            event_filename = f"{event['event_id']}.json"
            event_filepath = os.path.join(OUTPUT_DIR, event_filename)

            with open(event_filepath, "w", encoding="utf-8") as file:
                json.dump(event, file, indent=2, ensure_ascii=False)

        print(f"✅ Processed & Split: {filepath}")

    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")

# Function to iterate over all JSON files in the directory
def process_directory(directory):
    """Find all JSON files in a directory, normalize their date fields, and split them."""
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            process_json_file(os.path.join(directory, filename))

# Run the script
if __name__ == "__main__":
    process_directory(INPUT_DIR)
    print("🎯 All JSON events have been processed and saved individually.")
