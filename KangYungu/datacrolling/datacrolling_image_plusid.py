import pandas as pd
import pathlib

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent  # KANGYUNGU/
INPUT_CSV = BASE_DIR / "dataset" / "perfume_for_image.csv"
OUTPUT_CSV = BASE_DIR / "dataset" / "perfume_for_image_with_id.csv"

df = pd.read_csv(INPUT_CSV, encoding="utf-8")

df.insert(0, "id", range(1, len(df) + 1))

df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

print(f"id 추가 {OUTPUT_CSV.resolve()}")
