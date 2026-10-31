from pathlib import Path
import json
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "dataset.csv"
OUTPUT_PATH = ROOT / "data" / "cleaned_spotify_tracks.csv"
REPORT_PATH = ROOT / "data" / "data_quality.json"
TEXT_COLUMNS = ["artists", "album_name", "track_name"]


def clean_dataset(input_path: Path = INPUT_PATH, output_path: Path = OUTPUT_PATH) -> tuple[pd.DataFrame, dict]:
    df = pd.read_csv(input_path)
    initial_rows = len(df)
    missing_before = df.isna().sum().to_dict()
    exact_duplicates = int(df.duplicated().sum())
    if exact_duplicates:
        df = df.drop_duplicates()

    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])
    for column in TEXT_COLUMNS:
        if column in df.columns:
            df[column] = df[column].fillna("Unknown")

    numeric_columns = df.select_dtypes(include=np.number).columns
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors="coerce")
    df = df.dropna(subset=numeric_columns)

    duplicate_track_ids = int(df["track_id"].duplicated().sum())
    # Keep the most popular occurrence of a track; identical popularity ties are resolved
    # by row completeness and source order, avoiding arbitrary genre loss.
    df["_completeness"] = df.notna().sum(axis=1)
    df = df.sort_values(["popularity", "_completeness"], ascending=[False, False], kind="stable")
    df = df.drop_duplicates("track_id", keep="first")
    df = df.drop(columns=["_completeness"])
    df["duration_min"] = df["duration_ms"] / 60000

    audio_ranges = {
        "popularity": (0, 100), "danceability": (0, 1), "energy": (0, 1),
        "speechiness": (0, 1), "acousticness": (0, 1),
        "instrumentalness": (0, 1), "liveness": (0, 1), "valence": (0, 1),
        "mode": (0, 1), "time_signature": (1, 5), "duration_ms": (0, None),
    }
    invalid_ranges = 0
    for column, (low, high) in audio_ranges.items():
        if column not in df:
            continue
        mask = df[column] < low
        if high is not None:
            mask |= df[column] > high
        invalid_ranges += int(mask.sum())
        df.loc[mask, column] = np.nan
    df = df.dropna(subset=[column for column in audio_ranges if column in df])

    df = df.sort_index()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    report = {
        "initial_rows": initial_rows, "exact_duplicates_removed": exact_duplicates,
        "duplicate_track_ids_removed": duplicate_track_ids,
        "invalid_numeric_values_removed_or_repaired": invalid_ranges,
        "final_rows": len(df), "missing_values_before": missing_before,
        "missing_values_after": df.isna().sum().to_dict(),
        "deduplication_rule": "One row per track_id; retained highest popularity, then most complete row.",
        "text_missing_rule": "Missing artists, album_name, and track_name filled with Unknown.",
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return df, report


if __name__ == "__main__":
    cleaned, summary = clean_dataset()
    print(json.dumps(summary, indent=2))
