import json
import re
import argparse
import sys

def remove_aya_numbers_from_translations(data):
    """
    Remove leading aya numbers from translation text entries.
    
    Some translation sources prefix each aya's text with its number
    (e.g. "1. Au nom d'Allah..." or "100. Est-il possible...").
    Since the aya number is already tracked in the 'aya' field,
    this prefix is redundant and should be stripped for consistency.
    """
    # Pattern: start of string, one or more digits, a period, then a space
    pattern = re.compile(r'^\d+\.\s+')

    if "translations" not in data or not isinstance(data["translations"], list):
        return data, 0

    count = 0
    for entry in data["translations"]:
        if "text" in entry and isinstance(entry["text"], str):
            new_text = pattern.sub('', entry["text"])
            if new_text != entry["text"]:
                entry["text"] = new_text
                count += 1

    return data, count

def needs_aya_number_removal(data):
    """
    Detect whether a translation file has aya numbers prefixed in the text.
    
    Checks a sample of entries to see if texts consistently start with
    the expected aya number followed by a period and space.
    Returns True if the pattern is detected in most sampled entries.
    """
    if "translations" not in data or not isinstance(data["translations"], list):
        return False

    pattern = re.compile(r'^(\d+)\.\s+')
    matches = 0
    checked = 0
    sample_size = min(50, len(data["translations"]))

    # Sample evenly across the file to avoid false positives
    step = max(1, len(data["translations"]) // sample_size)
    for i in range(0, len(data["translations"]), step):
        entry = data["translations"][i]
        if "text" in entry and isinstance(entry["text"], str):
            checked += 1
            m = pattern.match(entry["text"])
            if m and int(m.group(1)) == entry.get("aya", -1):
                matches += 1
        if checked >= sample_size:
            break

    # If more than 80% of sampled entries match, the file needs cleanup
    return checked > 0 and (matches / checked) > 0.8

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)

        if not needs_aya_number_removal(data):
            print(f"  ℹ No aya number prefixes detected in '{filepath}', skipping.")
            return False

        cleaned_data, count = remove_aya_numbers_from_translations(data)

        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(cleaned_data, file, ensure_ascii=False, indent=2)

        print(f"Success: Removed aya number prefixes from {count} entries in '{filepath}'.")
        return True

    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: The file '{filepath}' is not a valid JSON file.")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Remove leading aya number prefixes (e.g. '1. ', '100. ') "
                    "from translation text in a JSON file, updating the file in place."
    )
    parser.add_argument("target_file", help="Path to the JSON file to be updated")
    args = parser.parse_args()

    process_file(args.target_file)
