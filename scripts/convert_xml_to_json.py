#!/usr/bin/env python3
"""
Converts QuranEnc XML translation files to the JSON format
expected by the Ayat app.

Usage:
    python3 convert_xml_to_json.py <input.xml> <output_dir>

Example:
    python3 convert_xml_to_json.py english_rwwad_v1.0.19-xml.1.xml ../translations/

This will produce:
    ../translations/english.json
"""

import xml.etree.ElementTree as ET
import json
import sys
import os
import re


def parse_translation_xml(xml_path: str) -> dict:
    """Parse a QuranEnc XML file and return structured translation data."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Parse metadata
    meta_elem = root.find("meta")
    translation_id = meta_elem.findtext("id", "").strip()

    # Derive human-readable language (e.g., "english_rwwad" -> "English")
    # This is a fallback in case the XML's language field isn't clear
    raw_language = meta_elem.findtext("language", "").strip()
    language_display = raw_language.capitalize()

    meta = {
        "id": translation_id,
        "language": language_display,
        "title": meta_elem.findtext("title", "").strip(),
        "source": meta_elem.findtext("source", "").strip(),
        "url": meta_elem.findtext("url", "").strip(),
        "version": extract_version(
            meta_elem.findtext("updated_at", "").strip()
        ),
    }

    # Parse translations
    translations = []
    sura_list = root.find("sura_list")
    for sura_elem in sura_list.findall("sura"):
        sura_number = int(sura_elem.get("number", 0))
        for aya_elem in sura_elem.findall("aya"):
            aya_number = int(aya_elem.get("number", 0))
            text = (aya_elem.findtext("translation") or "").strip()

            # Clean up CDATA artifacts if any
            text = clean_text(text)

            translations.append({
                "sura": sura_number,
                "aya": aya_number,
                "text": text,
            })

    return {
        "meta": meta,
        "translations": translations,
    }


def extract_version(updated_at: str) -> str:
    """Extract version string from updated_at field.
    e.g. '2026-03-12 23:45:25 (v1.0.19-xml.1)' → 'v1.0.19'
    """
    match = re.search(r"\((v[\d.]+)", updated_at)
    if match:
        return match.group(1)
    return "v1.0.0"


def clean_text(text: str) -> str:
    """Clean translation text of any artifacts."""
    # Remove footnote references like [1], [2], etc.
    # Keep the text readable
    text = text.strip()
    return text


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 convert_xml_to_json.py <input.xml> <output_dir>")
        sys.exit(1)

    xml_path = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.exists(xml_path):
        print(f"Error: File not found: {xml_path}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    print(f"Parsing {xml_path}...")
    data = parse_translation_xml(xml_path)

    translation_id = data["meta"]["id"]
    output_path = os.path.join(output_dir, f"{translation_id}.json")

    print(f"Language: {data['meta']['language']}")
    print(f"ID: {translation_id}")
    print(f"Title: {data['meta']['title']}")
    print(f"Version: {data['meta']['version']}")
    print(f"Total ayat: {len(data['translations'])}")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    file_size = os.path.getsize(output_path)
    print(f"Output: {output_path} ({file_size / 1024:.1f} KB)\n")

    return output_path

if __name__ == "__main__":
    main()
