#!/usr/bin/env python3
"""
Script to rename all raw_*.txt files to TMT_Brief_YYYY-MM-DD_raw.txt format
in the api/static/assets/raw directory.
"""

from pathlib import Path

def rename_raw_files():
    raws_dir = Path("api/static/assets/raw")
    if not raws_dir.exists():
        print(f"❌ Directory {raws_dir} does not exist!")
        return

    raw_files = list(raws_dir.glob("raw_*.txt"))
    if not raw_files:
        print("✅ No files with 'raw_' prefix found to rename.")
        return

    print(f"📁 Found {len(raw_files)} files to rename:")
    for file_path in raw_files:
        old_name = file_path.name
        date_part = old_name.replace("raw_", "").replace(".txt", "")
        new_name = f"TMT_Brief_{date_part}_raw.txt"
        new_path = file_path.parent / new_name
        if new_path.exists():
            print(f"⚠️  Skipping {old_name} -> {new_name} (target already exists)")
            continue
        try:
            file_path.rename(new_path)
            print(f"✅ Renamed: {old_name} -> {new_name}")
        except Exception as e:
            print(f"❌ Error renaming {old_name}: {e}")

    print("\n🎉 Renaming complete!")
    print("\n📋 Final directory contents:")
    for file_path in sorted(raws_dir.glob("*.txt")):
        print(f"  - {file_path.name}")

if __name__ == "__main__":
    rename_raw_files() 