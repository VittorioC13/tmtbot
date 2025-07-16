#!/usr/bin/env python3
"""
Script to ensure for every TMT_Brief_YYYY-MM-DD.pdf in briefs, there is a TMT_Brief_YYYY-MM-DD_raw.txt in raw.
If missing, copy any existing raw file and rename it to the missing name.
"""
from pathlib import Path
import shutil

def sync_raws_to_briefs():
    briefs_dir = Path("api/static/assets/briefs")
    raws_dir = Path("api/static/assets/raw")
    
    # Get all TMT_Brief_YYYY-MM-DD.pdf files
    brief_files = list(briefs_dir.glob("TMT_Brief_*.pdf"))
    if not brief_files:
        print("No TMT_Brief_*.pdf files found in briefs directory.")
        return
    
    # Get all TMT_Brief_YYYY-MM-DD_raw.txt files
    raw_files = list(raws_dir.glob("TMT_Brief_*_raw.txt"))
    existing_raw_names = {f.name for f in raw_files}
    
    # Use the first raw file as a template for missing ones
    template_raw = raw_files[0] if raw_files else None
    if not template_raw:
        print("No existing raw file to use as a template. Please add at least one raw file.")
        return
    
    created = 0
    for brief_file in brief_files:
        # Extract date part
        name = brief_file.stem  # e.g., TMT_Brief_2024-01-11
        if name.startswith("TMT_Brief_"):
            date_part = name.replace("TMT_Brief_", "")
            raw_name = f"TMT_Brief_{date_part}_raw.txt"
            raw_path = raws_dir / raw_name
            if raw_name not in existing_raw_names and not raw_path.exists():
                shutil.copy(template_raw, raw_path)
                print(f"✅ Created: {raw_name} (copied from {template_raw.name})")
                created += 1
    if created == 0:
        print("All raw files are already present.")
    else:
        print(f"\n🎉 {created} raw files created!")
    print("\n📋 Final raw directory contents:")
    for file_path in sorted(raws_dir.glob("*.txt")):
        print(f"  - {file_path.name}")

if __name__ == "__main__":
    sync_raws_to_briefs() 