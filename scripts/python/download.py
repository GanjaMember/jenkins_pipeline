import re
import os

import pandas as pd
import numpy as np

import kagglehub
from kagglehub import KaggleDatasetAdapter


# -----------------------
# data loading
# -----------------------
def download_data(output_path: str) -> None:
    file_path = "Mobile-Phones.csv"
    df = kagglehub.dataset_load(
        KaggleDatasetAdapter.PANDAS,
        "redpen12/mobile-phone-market-in-ghana",
        file_path
    )
    # Ensure output_path exists
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(output_path, index=False)


# -----------------------
# utils
# -----------------------
def parse_resolution(res_str: str) -> tuple[float, float, float]:
    """Returns width, height, megapixels (float)"""
    if pd.isna(res_str):
        return np.nan, np.nan, np.nan

    max_w, max_h = 0, 0
    sum_mp = .0
    for res in res_str.split(" / "):
        w, h = map(int, res.split(" x "))
        sum_mp += (w * h) / 1e6
        max_w, max_h = max(max_w, w), max(max_h, h)

    return max_w, max_h, sum_mp


def parse_main_camera(cam_str: str) -> tuple[int, float, float, float]:
    """
    Extracts list of MP-values. Returns:
    cam_count, cam_max_mp, cam_mean_mp, cam_min_mp
    """
    if pd.isna(cam_str):
        return 0, np.nan, np.nan, np.nan
    s = str(cam_str)
    # Find templates like "12 MP" and etc.
    mps = [int(x) for x in re.findall(r"(\d+)\s*MP", s, flags=re.IGNORECASE)]
    if not mps:
        # Extracting values after colons or commas
        nums = re.findall(r"(\d+)", s)
        # Filter noisy values (like year) and leave only reasonable MP (<500)
        mps = [int(n) for n in nums if 0 < int(n) < 500]
    if not mps:
        return 0, np.nan, np.nan, np.nan
    return len(mps), min(mps), max(mps), float(sum(mps)) / len(mps)


# -----------------------
# feature engineering
# -----------------------
def clear_data(input_path: str, output_path: str) -> None:
    df = pd.read_csv(input_path)

    # Rename columns
    rename_map = {}
    for col in df.columns:
        new = col.strip()
        new = new.replace(" ", "_").replace("(", "_").replace(")", "")
        rename_map[col] = new.lower()
    df = df.rename(columns=rename_map)
    df = df.rename(columns={"price_¢": "price_c"})
    df["price_c"] = pd.to_numeric(df["price_c"], errors="coerce")

    # ---- Parse main_camera ----
    cams = df["main_camera"].apply(parse_main_camera)
    df[["cam_count", "cam_max_mp", "cam_mean_mp", "cam_min_mp"]] = pd.DataFrame(
        cams.tolist(), index=df.index
    )

    # ---- Parse resolution ----
    res = df["resolution"].apply(parse_resolution)
    df[["res_max_w", "res_max_h", "res_sum_mp"]] = pd.DataFrame(
        res.tolist(), index=df.index
    )

    # ---- sd_card (yes/no) -> binary ----
    df["sd_card_flag"] = (
        df["sd_card"]
        .astype(str)
        .str.lower()
        .map(lambda s: 1 if "yes" in s else (0 if "no" in s else np.nan))
    )

    # Coerce to numeric for known numeric columns
    numeric_cols = []
    for c in [
        "screen_size_inch",
        "battery_mah",
        "storage_gb",
        "ram_gb",
        "selfie_camera_mp",
        "cam_count",
        "cam_max_mp",
        "cam_mean_mp",
        "cam_min_mp",
        "res_max_w",
        "res_max_h",
        "res_sum_mp",
        "sd_card_flag",
    ]:
        if c == "screen_size":
            pass
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
            numeric_cols.append(c)

    # ---- categorical columns: frequency encoding (count) ----
    cat_cols = [
        "brand",
        "model",
        "display",
        "os",
        "color",
        "region",
        "location",
        "sim_card",
    ]

    for c in cat_cols:
        df[c] = df[c].fillna("missing").astype(str)
        freq = df[c].value_counts(dropna=False)
        df[c + "_freq"] = df[c].map(freq).astype(float)
        numeric_cols.append(c + "_freq")

    # ---- filling missing values in numeric columns with median ----
    for c in numeric_cols:
        if c in df.columns:
            median = df[c].median(skipna=True)
            df[c] = df[c].fillna(median)

    # Ensure, that column price_c doesn't have NaNs left
    df = df.dropna(subset=["price_c"]).reset_index(drop=True)

    # --- Leave only numeric features + price_c ---
    final_num_cols = [c for c in numeric_cols if c in df.columns]
    final_df = df[final_num_cols + ["price_c"]].copy()

    # Ensure output_path exists
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    final_df.to_csv(output_path, index=False)


download_data("./data/phones.csv")
clear_data("./data/phones.csv", "./data/phones_cleaned.csv")
