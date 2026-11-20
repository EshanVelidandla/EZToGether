"""CDC PLACES 2024 county diabetes + obesity: download, check, clean."""
import pandas as pd

import utils
from utils import PROCESSED, RAW, clean_fips, drop_territories, save_checks

RAW_FILE = RAW / "places" / "places_county_2024.csv"
COLUMNS = ["fips", "state_abbr", "county_name", "diabetes_pct", "obesity_pct", "total_pop", "places_data_year"]


def download():
    utils.download("https://data.cdc.gov/resource/fu4u-a9bh.csv", "places/places_county_2024.csv",
                   params={"$where": "measureid in('DIABETES','OBESITY')",
                           "$order": "locationid,measureid,datavaluetypeid", "$limit": 50000})


def check():
    df = pd.read_csv(RAW_FILE, dtype={"locationid": str})
    bad_id = df[df["locationid"].str.len() != 5]
    missing = df[df["data_value"].isna()]
    years = sorted(df["year"].unique())
    rows = [
        ("accuracy", "data_value outside 0-100", ((df["data_value"] < 0) | (df["data_value"] > 100)).sum(), ""),
        ("accuracy", "locationid not 5 characters", len(bad_id), bad_id["locationid"].iloc[0] if len(bad_id) else ""),
        ("completeness", "missing data_value", len(missing),
         f"{missing['locationname'].iloc[0]}, {missing['stateabbr'].iloc[0]}" if len(missing) else ""),
        ("completeness", "states covered", df["stateabbr"].nunique(), ""),
        ("timeliness", "data years", len(years), ", ".join(str(y) for y in years)),
        ("consistency", "duplicate locationid+measureid+datavaluetypeid",
         df.duplicated(["locationid", "measureid", "datavaluetypeid"]).sum(), ""),
    ]
    save_checks(rows, "pre_places")


def clean():
    df = pd.read_csv(RAW_FILE, dtype={"locationid": str})
    df = df[(df["datavaluetypeid"] == "AgeAdjPrv") & (df["locationid"].str.len() == 5)]
    wide = df.pivot(index=["locationid", "stateabbr", "locationname", "totalpopulation", "year"],
                    columns="measureid", values="data_value").reset_index()
    wide = wide.rename(columns={"locationid": "fips", "stateabbr": "state_abbr", "locationname": "county_name",
                                "totalpopulation": "total_pop", "year": "places_data_year",
                                "DIABETES": "diabetes_pct", "OBESITY": "obesity_pct"})
    wide["fips"] = clean_fips(wide["fips"])
    wide = drop_territories(wide)
    wide[COLUMNS].sort_values("fips").to_csv(PROCESSED / "places_clean.csv", index=False)


if __name__ == "__main__":
    download()
    check()
    clean()
