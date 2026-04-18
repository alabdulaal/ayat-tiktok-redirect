#!/usr/bin/env python3
"""
Automated script to process all XML files.
Drop your downloaded XML files into the root of the repo or a 'xml_translations' folder, 
and run this script. It will:
1. Convert all XML files to JSON
2. Remove footprints from all of them
3. Automatically generate the manifest.json
"""

import os
import sys
import glob
import convert_xml_to_json
import remove_footnotes
import build_manifest

def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    translations_dir = os.path.join(repo_root, "translations")
    raw_xml_dir = os.path.join(repo_root, "xml_translations")

    # Make directories if they don't exist
    os.makedirs(translations_dir, exist_ok=True)
    os.makedirs(raw_xml_dir, exist_ok=True)

    # 1. Find all XML files in repo root AND xml_translations folder
    xml_files = glob.glob(os.path.join(repo_root, "*.xml"))
    xml_files.extend(glob.glob(os.path.join(raw_xml_dir, "*.xml")))

    if not xml_files:
        print(f"No XML files found.\nPlease drop your QuranEnc XML files into the repo root or the 'xml_translations' folder, then run this script.")
        sys.exit(0)

    print(f"Found {len(xml_files)} XML file(s) to process.\n")
    processed_jsons = []

    # 2. Process each XML file
    for xml_path in xml_files:
        print(f"=== Processing: {os.path.basename(xml_path)} ===")
        
        # Override sys.argv momentarily so convert_xml_to_json main() works without failing 
        # (Alternatively, we can directly call its utility functions, which we will do here)
        try:
            # Convert XML to JSON Data
            data = convert_xml_to_json.parse_translation_xml(xml_path)
            translation_id = data["meta"]["id"]
            output_json_path = os.path.join(translations_dir, f"{translation_id}.json")
            
            # Write JSON file
            import json
            with open(output_json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            print(f"  ✓ Converted to JSON: {os.path.basename(output_json_path)}")
            
            # Remove footnotes
            remove_footnotes.process_file(output_json_path)
            processed_jsons.append(output_json_path)
            
        except Exception as e:
            print(f"  ✗ Error processing {os.path.basename(xml_path)}: {e}")
        
        print("")

    # 3. Generate the Manifest
    print("=== Rebuilding Manifest ===")
    build_manifest.generate_manifest(translations_dir)
    print("\nAll tasks completed successfully!")

if __name__ == "__main__":
    main()
