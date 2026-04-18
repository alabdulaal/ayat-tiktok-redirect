import os
import glob
import json
import argparse

def generate_manifest(translations_dir="translations"):
    manifest = []
    
    # Grab all json files except manifest.json
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
                manifest.append({
                    "id": meta["id"],
                    "language": meta["language"],
                    "title": meta.get("title", ""),
                    "version": meta.get("version", "v1.0.0"),
                    "fileName": filename
                })
        except Exception as e:
            print(f"Error parsing {filename}: {e}")
            
    # Sort manifest for consistency (alphabetical by language then id)
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
