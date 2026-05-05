import json
import re
import argparse
import sys

def remove_footnotes_from_data(data, pattern):
    """
    Recursively search through a JSON object (dict, list, or string)
    and remove the regex pattern from any strings found.
    """
    if isinstance(data, dict):
        return {key: remove_footnotes_from_data(value, pattern) for key, value in data.items()}
    elif isinstance(data, list):
        return [remove_footnotes_from_data(item, pattern) for item in data]
    elif isinstance(data, str):
        return pattern.sub('', data)
    else:
        # Return numbers, booleans, nulls as is
        return data

def process_file(filepath):
    # Regex pattern: \[ matches '[', \d+ matches 1 or more digits, \] matches ']'
    pattern = re.compile(r'\[\d+\]')

    try:
        # 1. Load the JSON data from the file
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        # 2. Clean the data
        cleaned_data = remove_footnotes_from_data(data, pattern)

        # 3. Write the cleaned data back to the SAME file, overwriting it
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(cleaned_data, file, ensure_ascii=False, indent=2)
            
        print(f"Success: Removed footnotes and updated '{filepath}' in place.")
        
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: The file '{filepath}' is not a valid JSON file.")
        sys.exit(1)

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Remove numeric footnotes like [1], [2] from all text within a JSON file, updating the file in place.")
    
    # Required positional argument for the target file
    parser.add_argument("target_file", help="Path to the JSON file to be updated")
    
    args = parser.parse_args()

    # Run the processor on the provided file
    process_file(args.target_file)
