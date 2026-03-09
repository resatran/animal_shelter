from pathlib import Path
import pandas as pd


# project directories
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
EXCEPTIONS_DIR = DATA_DIR / "exceptions"


# ensure folders exist
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
EXCEPTIONS_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------
# helper functions
# -----------------------------

def load_csv(folder: Path, filename: str, **kwargs) -> pd.DataFrame:
    path = folder / filename
    if not path.exists():
        raise FileNotFoundError(f"{filename} not found in {folder}")
    return pd.read_csv(path, **kwargs)


def save_csv(df: pd.DataFrame, folder: Path, filename: str, index: bool = False, **kwargs):
    folder.mkdir(parents=True, exist_ok=True)
    out_path = folder / filename
    df.to_csv(out_path, index=index, **kwargs)
    return out_path


def standardize_column(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )
    return df


def drop_columns(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    df = df.copy()
    return df.drop(columns=[c for c in cols if c in df.columns])


def split_datetime_intake(df: pd.DataFrame, datetime_col: str) -> pd.DataFrame:
    df = df.copy()
    dt = pd.to_datetime(df[datetime_col], errors="coerce")
    df["date"] = dt.dt.date
    df["time"] = dt.dt.time
    return df.drop(columns=[datetime_col])


def split_datetime_outcome(df: pd.DataFrame, datetime_col: str) -> pd.DataFrame:
    df = df.copy()

    idx_iso = df.index[0:2372]
    idx_mdy = df.index[2372:]

    dt = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns, UTC]")

    dt.loc[idx_iso] = pd.to_datetime(
        df.loc[idx_iso, datetime_col],
        errors="coerce",
        utc=True
    )

    dt.loc[idx_mdy] = pd.to_datetime(
        df.loc[idx_mdy, datetime_col],
        errors="coerce",
        utc=True
    )

    df["date"] = dt.dt.date
    df["time"] = dt.dt.time

    return df.drop(columns=[datetime_col])


def main():

    intake_raw = load_csv(RAW_DIR, "raw_data_intake_20260112.csv")
    outcome_raw = load_csv(RAW_DIR, "raw_data_outcome_20260112.csv")

    # -----------------------------
    # Block 2 — Merge intake/outcome
    # -----------------------------
    intake_raw = standardize_column(intake_raw)
    outcome_raw = standardize_column(outcome_raw)

    COLS_TO_DROP = ["found_location", "monthyear"]

    intake_clean = drop_columns(intake_raw, COLS_TO_DROP)
    outcome_clean = drop_columns(outcome_raw, COLS_TO_DROP)

    KEY = "animal_id"

    matched_table = intake_clean.merge(
        outcome_clean,
        on=KEY,
        how="inner",
        suffixes=("_intake", "_outcome")
    )

    intake_only_ids = set(intake_clean[KEY]) - set(outcome_clean[KEY])
    intake_unmatched = intake_clean[intake_clean[KEY].isin(intake_only_ids)].copy()

    outcome_only_ids = set(outcome_clean[KEY]) - set(intake_clean[KEY])
    outcome_unmatched = outcome_clean[outcome_clean[KEY].isin(outcome_only_ids)].copy()

    matched_table = matched_table.sort_values(KEY).reset_index(drop=True)

    print("Merged intake and outcome tables.")

    # -----------------------------
    # Block 3 — Standardize datetimes
    # -----------------------------
    intake_split_data = split_datetime_intake(intake_clean, "datetime")
    outcome_split_data = split_datetime_outcome(outcome_clean, "datetime")

    print("Datetime columns split.")

    # -----------------------------
    # Block 4 — Fix inflated merges
    # -----------------------------
    matched_side_by_side = intake_split_data.merge(
        outcome_split_data,
        on=KEY,
        how="inner",
        suffixes=("_intake", "_outcome")
    )

    matched_side_by_side["dt_intake"] = pd.to_datetime(
        matched_side_by_side["date_intake"].astype(str) + " " +
        matched_side_by_side["time_intake"].astype(str),
        errors="coerce"
    )

    matched_side_by_side["dt_outcome"] = pd.to_datetime(
        matched_side_by_side["date_outcome"].astype(str) + " " +
        matched_side_by_side["time_outcome"].astype(str),
        errors="coerce"
    )

    matched_side_by_side["dt_diff"] = (
        matched_side_by_side["dt_outcome"] -
        matched_side_by_side["dt_intake"]
    )

    valid_mask = (
        matched_side_by_side["dt_intake"].notna() &
        matched_side_by_side["dt_outcome"].notna() &
        (matched_side_by_side["dt_diff"] >= pd.Timedelta(0))
    )

    candidates = matched_side_by_side[valid_mask].copy()

    candidates = candidates.sort_values(
        [KEY, "dt_intake", "dt_diff"]
    )

    matched_side_by_side_paired = candidates.drop_duplicates(
        subset=[KEY, "dt_intake"],
        keep="first"
    ).copy()

    bad_timestamp_pairs = matched_side_by_side[~valid_mask].copy()

    matched_side_by_side_paired = matched_side_by_side_paired.sort_values(
        [KEY, "dt_intake", "dt_outcome"]
    ).reset_index(drop=True)

    print("Timestamp pairing complete.")

    # -----------------------------
    # Block 5 — Derived columns
    # -----------------------------
    matched_df = matched_side_by_side_paired.copy()

    if "date_of_birth" in matched_df.columns:
        matched_df["date_of_birth"] = pd.to_datetime(
            matched_df["date_of_birth"],
            errors="coerce"
        )

    matched_df["age_intake_years"] = (
        (matched_df["dt_intake"] - matched_df["date_of_birth"])
        .dt.total_seconds() / (365.25 * 24 * 60 * 60)
    )

    matched_df["date_diff_days"] = (
        (matched_df["dt_outcome"] - matched_df["dt_intake"])
        .dt.total_seconds() / (24 * 60 * 60)
    )

    print("Derived columns created.")

    # -----------------------------
    # Block 6 — Drop unnecessary columns
    # -----------------------------
    cols_to_drop = [
        "name_intake",
        "animal_type_intake",
        "breed_intake",
        "color_intake",
        "color_outcome",
        "age_upon_intake",
        "age_upon_outcome",
        "sex_upon_intake",
        "outcome_subtype",
        "dt_intake",
        "dt_outcome",
        "dt_diff"
    ]

    matched_df = matched_df.drop(
        columns=[c for c in cols_to_drop if c in matched_df.columns]
    )

    print("Unnecessary columns removed.")

    # -----------------------------
    # Block 7 — Rename + reorder columns
    # -----------------------------
    rename_dict = {
        "name_outcome": "name",
        "animal_type_outcome": "animal_type",
        "breed_outcome": "breed",
        "condition_intake": "intake_condition",
        "intake_type_intake": "intake_type",
        "outcome_type_outcome": "outcome_type"
    }

    matched_df = matched_df.rename(
        columns={k: v for k, v in rename_dict.items() if k in matched_df.columns}
    )

    preferred_order = [
        "animal_id",
        "name",
        "date_intake",
        "date_outcome",
        "time_intake",
        "time_outcome",
        "date_diff_days",
        "animal_type",
        "breed",
        "age_intake_years",
        "intake_type",
        "outcome_type",
        "sex_upon_outcome",
        "intake_condition",
        "date_of_birth"
    ]

    preferred_existing = [c for c in preferred_order if c in matched_df.columns]
    remaining_cols = [c for c in matched_df.columns if c not in preferred_existing]

    matched_df = matched_df[preferred_existing + remaining_cols]

    print("Columns renamed and reordered.")

    # -----------------------------
    # Block 8 — Save final CSV
    # -----------------------------
    save_csv(
        matched_df,
        PROCESSED_DIR,
        "final_matched_animals.csv"
    )

    print("Final matched CSV saved.")

    # -----------------------------
    # Block 9 — Save exception tables separately
    # -----------------------------
    save_csv(
        intake_unmatched,
        EXCEPTIONS_DIR,
        "intake_unmatched.csv"
    )

    save_csv(
        outcome_unmatched,
        EXCEPTIONS_DIR,
        "outcome_unmatched.csv"
    )

    save_csv(
        bad_timestamp_pairs,
        EXCEPTIONS_DIR,
        "bad_timestamp_pairs.csv"
    )

    print("Exception tables saved.")


if __name__ == "__main__":
    main()


