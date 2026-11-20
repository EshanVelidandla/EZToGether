"""Summary stats, Spearman correlations and one combined quality-check table."""
import pandas as pd

from utils import PROCESSED, QUALITY, TABLES

VARS = ["diabetes_pct", "obesity_pct", "median_hh_income", "poverty_rate_pct", "grocery_per_1k"]

merged = pd.read_csv(PROCESSED / "county_merged.csv", dtype={"fips": str})
merged[VARS].describe().T.round(3).to_csv(TABLES / "summary_stats.csv")
merged[VARS].corr(method="spearman").round(3).to_csv(TABLES / "correlations_spearman.csv")

# stack every *_checks.csv except all_checks itself
frames = []
for path in sorted(QUALITY.glob("*_checks.csv")):
    if path.name == "all_checks.csv":
        continue
    checks = pd.read_csv(path, dtype=str, keep_default_na=False)
    checks.insert(0, "source", path.stem.removesuffix("_checks"))
    frames.append(checks)
pd.concat(frames).to_csv(QUALITY / "all_checks.csv", index=False)
print(f"Wrote summary tables and all_checks.csv ({len(frames)} check files)")
