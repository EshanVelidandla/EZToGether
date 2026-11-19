"""Join the three cleaned sources on FIPS, then check the result."""
import pandas as pd

from utils import PROCESSED, QUALITY, save_checks

SOURCES = ["places", "acs", "atlas"]
ALASKA_CHANGES = {"02063", "02066", "02261"}

data = {s: pd.read_csv(PROCESSED / f"{s}_clean.csv", dtype={"fips": str}) for s in SOURCES}

# Which sources each county appears in
coverage = pd.DataFrame({"fips": sorted(set().union(*(d["fips"] for d in data.values())))})
flags = []
for s in SOURCES:
    coverage[f"in_{s}"] = coverage["fips"].isin(data[s]["fips"])
    flags.append(f"in_{s}")
coverage.groupby(flags).size().reset_index(name="counties").to_csv(QUALITY / "merge_coverage.csv", index=False)


def likely_reason(fips):
    if fips.startswith("09"):
        return "Connecticut planning regions replaced counties (2022)"
    if fips in ALASKA_CHANGES:
        return "Alaska Valdez-Cordova split (2019)"
    return "not in every source"


# Counties missing from at least one source
names = pd.concat([
    data["acs"][["fips", "acs_county_name"]].rename(columns={"acs_county_name": "name"}),
    data["places"][["fips", "county_name"]].rename(columns={"county_name": "name"}),
]).drop_duplicates("fips")
unmatched = coverage[~coverage[flags].all(axis=1)].merge(names, on="fips", how="left")
unmatched["likely_reason"] = unmatched["fips"].map(likely_reason)
unmatched.to_csv(QUALITY / "unmatched_counties.csv", index=False)

# Analysis table: counties in all three sources, Connecticut excluded
merged = (data["places"]
          .merge(data["acs"], on="fips", validate="one_to_one")
          .merge(data["atlas"], on="fips", validate="one_to_one"))
merged = merged[~merged["fips"].str.startswith("09")]
merged.to_csv(PROCESSED / "county_merged.csv", index=False)

# Post-merge quality checks
pct = ["diabetes_pct", "obesity_pct", "poverty_rate_pct"]
values = pct + ["median_hh_income", "grocery_per_1k"]
mismatch = merged[[not a.startswith(p) for a, p in zip(merged["acs_county_name"], merged["county_name"])]]
years = (f"PLACES {merged['places_data_year'].unique().tolist()}, ACS 2018-2022, "
         f"Atlas {merged['grocery_year'].unique().tolist()}")

rows = [("completeness", f"{s} counties not in merged table",
         (~data[s]["fips"].isin(merged["fips"])).sum(), "") for s in SOURCES]
rows += [("completeness", f"missing {c}", merged[c].isna().sum(), "") for c in values]
rows += [
    ("accuracy", "percentages outside 0-100", (~merged[pct].stack().between(0, 100)).sum(), ""),
    ("accuracy", "income <= 0 or grocery rate < 0",
     ((merged["median_hh_income"] <= 0) | (merged["grocery_per_1k"] < 0)).sum(), ""),
    ("consistency", "duplicate FIPS", merged["fips"].duplicated().sum(), ""),
    ("consistency", "PLACES and ACS county names disagree", len(mismatch),
     "" if mismatch.empty else f"{mismatch.iloc[0]['county_name']} vs {mismatch.iloc[0]['acs_county_name']}"),
    ("timeliness", "reference years", "", years),
]
save_checks(rows, "post_merged")
merged.sample(min(5, len(merged)), random_state=477).to_csv(QUALITY / "spot_check.csv", index=False)

print(f"Merged {len(merged)} counties; {len(unmatched)} counties missing from at least one source")
