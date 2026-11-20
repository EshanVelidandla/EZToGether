"""USDA Food Environment Atlas grocery stores: download, check, clean."""
import zipfile

import pandas as pd

import utils
from utils import PROCESSED, RAW, clean_fips, drop_territories, save_checks

RAW_FILE = RAW / "atlas" / "food_environment_atlas_csv.zip"
MEMBER = "StateAndCountyData.csv"
# most recent GROCPTH## with >= 90% of best real-value count (GROCPTH16 3066, GROCPTH20 2234)
RATE = "GROCPTH16"
COUNT = "GROC16"
CODES = [-9999, -8888]
COLUMNS = ["fips", "grocery_per_1k", "grocery_count", "grocery_year", "grocery_var"]


def download():
    utils.download("https://www.ers.usda.gov/media/5570/food-environment-atlas-csv-files.zip?v=71038",
                   "atlas/food_environment_atlas_csv.zip")


def check():
    with zipfile.ZipFile(RAW_FILE) as z:
        df = pd.read_csv(z.open(MEMBER), dtype={"FIPS": str})
    value = pd.to_numeric(df["Value"], errors="coerce")
    rate, count = df["Variable_Code"] == RATE, df["Variable_Code"] == COUNT
    real = value >= 0
    grocpth = sorted(df.loc[df["Variable_Code"].str.fullmatch(r"GROCPTH\d\d"), "Variable_Code"].unique())
    fips = clean_fips(df["FIPS"])
    ct = sorted(fips[fips.str.startswith("09", na=False)].unique())
    rows = [
        ("accuracy", "grocery rate below 0 (excluding -9999 and -8888)", (rate & (value < 0) & ~value.isin(CODES)).sum(), ""),
        ("completeness", f"{RATE} counties with a value", (rate & real).sum(), ""),
        ("completeness", f"{RATE} counties with -9999, -8888 or blank", (rate & ~real).sum(), ""),
        ("completeness", f"{COUNT} counties with a value", (count & real).sum(), ""),
        ("completeness", f"{COUNT} counties with -9999, -8888 or blank", (count & ~real).sum(), ""),
        ("timeliness", "GROCPTH years available", len(grocpth), ", ".join(grocpth) + "; Atlas updated 2025-07-30"),
        ("consistency", "FIPS shorter than 5 characters", (df["FIPS"].str.len() < 5).sum(), ""),
        ("consistency", "duplicate FIPS+Variable_Code", df.duplicated(["FIPS", "Variable_Code"]).sum(), ""),
        ("consistency", "Connecticut county codes", len(ct), ", ".join(ct)),
    ]
    save_checks(rows, "pre_atlas")


def clean():
    with zipfile.ZipFile(RAW_FILE) as z:
        df = pd.read_csv(z.open(MEMBER), dtype={"FIPS": str})
    df = df[df["Variable_Code"].isin([RATE, COUNT])].copy()
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
    df["Value"] = df["Value"].mask(df["Value"] < 0)
    wide = df.pivot(index="FIPS", columns="Variable_Code", values="Value").reset_index()
    wide["fips"] = clean_fips(wide["FIPS"])
    wide = wide[~wide["fips"].str.endswith("000")]
    wide = drop_territories(wide)
    wide = wide.rename(columns={RATE: "grocery_per_1k", COUNT: "grocery_count"})
    wide["grocery_year"] = 2000 + int(RATE[-2:])
    wide["grocery_var"] = RATE
    wide[COLUMNS].sort_values("fips").to_csv(PROCESSED / "atlas_clean.csv", index=False)


if __name__ == "__main__":
    download()
    check()
    clean()
