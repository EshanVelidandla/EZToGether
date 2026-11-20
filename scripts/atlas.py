
from pathlib import Path
import zipfile
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw/atlas/food_environment_atlas_csv.zip"
PROCESSED = ROOT / "data/processed"
QUALITY = ROOT / "outputs/quality"

PROCESSED.mkdir(parents=True, exist_ok=True)
QUALITY.mkdir(parents=True, exist_ok=True)

# Atlas grocery store variables (2016)
MEMBER = "GROC16"
RATE = "GROCPTH16"
COUNT = "GROC16"

with zipfile.ZipFile(RAW) as z:
    df = pd.read_csv(
        z.open("StateAndCountyData.csv"),
        dtype={"FIPS": str}
    )

df["fips"] = df["FIPS"].str.zfill(5)
df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
df.loc[df["Value"] == -9999, "Value"] = float("nan")

# Keep the grocery store measures
selected = df[df["Variable_Code"].isin([MEMBER, RATE, COUNT])].copy()

# Check completeness and duplicates
checks = []

for variable in [MEMBER, RATE]:
    subset = selected[selected["Variable_Code"] == variable]
    valid = subset["Value"].notna().sum()
    total = len(subset)

    checks.append({
        "dimension": "completeness",
        "check": variable,
        "count": total - valid,
        "example": f"{valid}/{total} valid values"
    })

checks.append({
    "dimension": "consistency",
    "check": "duplicate county-variable rows",
    "count": int(selected.duplicated(["fips", "Variable_Code"]).sum()),
    "example": ""
})

# Convert to one row per county
clean = selected.pivot_table(
    index="fips",
    columns="Variable_Code",
    values="Value",
    aggfunc="first",
    dropna=False
).reset_index()

clean.columns.name = None

clean = clean.rename(columns={
    "GROC16": "grocery_store_count",
    "GROCPTH16": "grocery_stores_per_1000"
})

clean["fips"] = clean["fips"].astype(str).str.zfill(5)

# Save outputs
clean.to_csv(PROCESSED / "atlas_clean.csv", index=False)

pd.DataFrame(
    checks,
    columns=["dimension", "check", "count", "example"]
).to_csv(QUALITY / "pre_atlas_checks.csv", index=False)

print("Atlas cleaning complete!")
print("Counties:", len(clean))
print("Missing values:")
print(clean.isna().sum())
print("Saved data/processed/atlas_clean.csv")
print("Saved outputs/quality/pre_atlas_checks.csv")

