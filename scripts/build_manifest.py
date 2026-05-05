import os
import glob
import json
import argparse
import re

def compare_versions(lhs, rhs):
    lhs_parts = [int(part) for part in re.findall(r"\d+", lhs or "")]
    rhs_parts = [int(part) for part in re.findall(r"\d+", rhs or "")]
    max_len = max(len(lhs_parts), len(rhs_parts))
    lhs_parts.extend([0] * (max_len - len(lhs_parts)))
    rhs_parts.extend([0] * (max_len - len(rhs_parts)))

    if lhs_parts == rhs_parts:
        return 0
    return 1 if lhs_parts > rhs_parts else -1

def is_newer_entry(candidate, existing):
    version_comparison = compare_versions(candidate["version"], existing["version"])
    if version_comparison != 0:
        return version_comparison > 0
    return candidate["fileName"] > existing["fileName"]

def generate_manifest(translations_dir="translations"):
    manifest_by_id = {}
    
    # Grab all JSON files and publish the newest version for each stable translation id.
    json_files = glob.glob(os.path.join(translations_dir, "*.json"))
    
    for file_path in json_files:
        filename = os.path.basename(file_path)
        if filename == "manifest.json":
            continue
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            if "meta" in data:
                meta = data["meta"]
                entry = {
                    "id": meta["id"],
                    "language": meta["language"],
                    "title": meta.get("title", ""),
                    "version": meta.get("version", "v1.0.0"),
                    "fileName": filename,
                    "fileSize": os.path.getsize(file_path)
                }
                existing = manifest_by_id.get(entry["id"])
                if existing is None or is_newer_entry(entry, existing):
                    manifest_by_id[entry["id"]] = entry
        except Exception as e:
            print(f"Error parsing {filename}: {e}")
            
    # Sort manifest for consistency (alphabetical by language then id)
    manifest = list(manifest_by_id.values())
    manifest.sort(key=lambda x: (x["language"], x["id"]))
    
    manifest_path = os.path.join(translations_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        
    print(f"Manifest successfully generated at '{manifest_path}' with {len(manifest)} entries.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate manifest.json from all translation JSON files.")
    parser.add_argument("--dir", default="../translations", help="Path to translations directory")
    args = parser.parse_args()
    
    generate_manifest(args.dir)
