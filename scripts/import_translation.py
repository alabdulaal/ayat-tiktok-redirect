#!/usr/bin/env python3
"""
Orchestrator script to import a new translation XML file.
Steps:
1. Converts XML to JSON
2. Removes footnotes
3. Regenerates the manifest.json
"""
import os
import sys
import argparse
import convert_xml_to_json
import remove_footnotes
import build_manifest

def main():
    parser = argparse.ArgumentParser(description="Fully process a QuranEnc XML translation file.")
    parser.add_argument("xml_file", help="Path to the input XML file")
    args = parser.parse_args()

    xml_path = args.xml_file
    if not os.path.exists(xml_path):
        print(f"Error: {xml_path} does not exist.")
        sys.exit(1)

    # Calculate paths
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    translations_dir = os.path.join(repo_root, "translations")

    # Step 1: Convert XML to JSON
    print("\n--- Step 1: Converting XML to JSON ---")
    output_json_path = convert_xml_to_json.parse_translation_xml(xml_path)
    
    # We need to restructure the import differently since convert_xml_to_json.main() expects sys.argv
    # Let's override sys.argv temporarily
    original_argv = sys.argv
    sys.argv = ["convert_xml_to_json.py", xml_path, translations_dir]
    try:
        # Instead of calling main() which might not return the path easily, 
        # let's write a direct logic here for step 1 using the imported module.
        data = convert_xml_to_json.parse_translation_xml(xml_path)
        translation_id = data["meta"]["id"]
        output_json_path = os.path.join(translations_dir, f"{translation_id}.json")
        
        with open(output_json_path, "w", encoding="utf-8") as f:
            import json
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"Saved initial JSON to {output_json_path}")
    finally:
        sys.argv = original_argv

    # Step 2: Remove footprints
    print("\n--- Step 2: Removing footnotes ---")
    remove_footnotes.process_file(output_json_path)

    # Step 3: Regenerate manifest
    print("\n--- Step 3: Regenerating Manifest ---")
    build_manifest.generate_manifest(translations_dir)

    print("\nAll done! You can now commit the new files.")

if __name__ == "__main__":
    main()
