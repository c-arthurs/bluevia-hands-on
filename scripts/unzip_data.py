"""
Unzip the synthetic 1K patient dataset into data/raw/.

Usage:
    python scripts/unzip_data.py

Expects: data/synthetic_1k.zip
Outputs: data/raw/*.csv
"""
import shutil
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ZIP_PATH = REPO_ROOT / "data" / "synthetic_1k.zip"
RAW_DIR = REPO_ROOT / "data" / "raw"


def main():
    if not ZIP_PATH.exists():
        raise FileNotFoundError(
            f"{ZIP_PATH} not found. Place the zip in data/ first."
        )

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Extracting {ZIP_PATH} → {RAW_DIR}/")
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        zf.extractall(RAW_DIR)

    # The zip may nest CSVs inside a subdirectory (e.g. csv/).
    # Move them up to RAW_DIR so downstream code finds them at data/raw/*.csv.
    for subdir in RAW_DIR.iterdir():
        if subdir.is_dir():
            for f in subdir.iterdir():
                dest = RAW_DIR / f.name
                shutil.move(str(f), str(dest))
            subdir.rmdir()

    csvs = sorted(RAW_DIR.glob("*.csv"))
    print(f"Done. {len(csvs)} CSV files extracted:")
    for f in csvs:
        mb = f.stat().st_size / 1e6
        print(f"  {f.name:30s}  {mb:>7.1f} MB")


if __name__ == "__main__":
    main()
