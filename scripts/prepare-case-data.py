# This script is used to clean and prepare case data from the Azure search index before uploading to Azure Blob Storage.

import json
import os
from datetime import datetime

def process_json(input_filepath, output_dir):
    """
    Reads data exported from the Case Search index, which is a file containing multiple JSON objects, one per line,
    extracts valid JSON objects, and saves them as individual files.

    Args:
        input_filepath: Path to the input file with possibly invalid JSON.
        output_dir: Path to the directory where JSON objects will be saved.
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        valid_objects = []
        
        with open(input_filepath, 'r', encoding='utf-8') as infile:
            buffer = ""
            brace_count = 0
            
            for line in infile:
                line = line.strip()
                if not line:
                    continue
                
                for char in line:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                    
                    buffer += char
                    
                    if brace_count == 0 and buffer.strip():
                        try:
                            obj = json.loads(buffer)
                            if isinstance(obj, dict):
                                valid_objects.append(obj)
                            buffer = ""  # Reset buffer
                        except json.JSONDecodeError:
                            buffer = ""  # Reset buffer on failure
                            break
        
        for i, obj in enumerate(valid_objects):
            if not isinstance(obj, dict):
                continue
            
            output_filepath = os.path.join(output_dir, f"item_{i+1}.json")
            with open(output_filepath, "w", encoding="utf-8") as outfile:
                json.dump(obj, outfile, indent=2, ensure_ascii=False)
        
        print(f"Successfully processed JSON objects and saved in: {output_dir}")
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_filepath}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Example Usage
if __name__ == "__main__":
    input_file = "data/azureblob-index-0-documents.json"
    output_directory = "data/processed-case-files"
    process_json(input_file, output_directory)
