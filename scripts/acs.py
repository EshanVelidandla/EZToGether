"""Download Census ACS 2018-2022 county income and poverty, check it, and clean it."""
import json

import pandas as pd

from utils import PROCESSED, clean_fips, download, drop_territories, save_checks

URL = "https://api.census.gov/data/2022/acs/acs5"
PARAMS = {
    "get": "NAME,B19013_001E,B19013_001M,B17001_001E,B17001_002E",
    "for": "county:*",
    "in": "state:*",
}
COLUMNS = {
    "B19013_001E": "median_hh_income",
    "B19013_001M": "median_hh_income_moe",
    "B17001_001E": "poverty_universe",
    "B17001_002E": "below_poverty",
}
VALUES = list(COLUMNS.values())

# Raw API response: a list of rows with the header first
path = download(URL, "acs/acs5_2022_county.json", PARAMS)
rows = json.loads(path.read_text(encoding="utf-8"))
raw = pd.DataFrame(rows[1:], columns=rows[0])

df = pd.DataFrame({
    "fips": clean_fips(raw["state"] + raw["county"]),
    "acs_county_name": raw["NAME"],
})
for code, name in COLUMNS.items():
    df[name] = pd.to_numeric(raw[code], errors="coerce")

# Census marks suppressed or unavailable values with large negative codes
sentinels = df[VALUES] < 0
df[VALUES] = df[VALUES].mask(sentinels)

territory_rows = int(df["fips"].str[:2].isin({"60", "66", "69", "72", "78"}).sum())
df = drop_territories(df).copy()
df["poverty_rate_pct"] = (df["below_poverty"] / df["poverty_universe"] * 100).round(2)

wide_moe = (df["median_hh_income_moe"] / df["median_hh_income"]) > 0.10
checks = [
    ("completeness", "rows returned by the API", len(raw), ""),
    ("completeness", "territory rows dropped", territory_rows, "Puerto Rico (72)"),
    ("completeness", "suppressed values (negative Census codes)", int(sentinels.to_numpy().sum()), ""),
    ("completeness", "missing median_hh_income", int(df["median_hh_income"].isna().sum()), ""),
    ("completeness", "missing poverty_rate_pct", int(df["poverty_rate_pct"].isna().sum()), ""),
    ("accuracy", "below_poverty greater than poverty_universe",
     int((df["below_poverty"] > df["poverty_universe"]).sum()), ""),
    ("accuracy", "poverty rate outside 0-100",
     int((~df["poverty_rate_pct"].dropna().between(0, 100)).sum()), ""),
    ("accuracy", "income margin of error over 10% of estimate", int(wide_moe.sum()),
     df.loc[wide_moe, "acs_county_name"].iloc[0] if wide_moe.any() else ""),
    ("consistency", "duplicate FIPS", int(df["fips"].duplicated().sum()), ""),
    ("consistency", "FIPS not 5 digits", int((~df["fips"].str.fullmatch(r"\d{5}")).sum()), ""),
    ("timeliness", "reference period", "", "ACS 5-year 2018-2022"),
]
save_checks(checks, "pre_acs")

clean = df[["fips", "acs_county_name"] + VALUES + ["poverty_rate_pct"]]
clean.to_csv(PROCESSED / "acs_clean.csv", index=False)
print(f"Wrote data/processed/acs_clean.csv with {len(clean)} counties")
