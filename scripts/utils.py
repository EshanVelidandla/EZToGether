"""Shared paths and helpers for every script."""
import hashlib
import json
from datetime import date
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
QUALITY = ROOT / "outputs" / "quality"
TABLES = ROOT / "outputs" / "tables"
FIGURES = ROOT / "outputs" / "figures"
for folder in (RAW, PROCESSED, QUALITY, TABLES, FIGURES):
    folder.mkdir(parents=True, exist_ok=True)

TERRITORIES = {"60", "66", "69", "72", "78"}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def download(url, dest, params=None):
    """Download once to data/raw/<dest>; record or verify its SHA-256 in manifest.json."""
    dest = RAW / dest
    manifest = dest.parent / "manifest.json"
    old = json.loads(manifest.read_text()) if manifest.exists() else None
    fresh = not dest.exists()
    if fresh:
        dest.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=300)
        r.raise_for_status()
        dest.write_bytes(r.content)
    digest = sha256(dest)
    if old and old["sha256"] != digest:
        print(f"WARNING: {dest.name} does not match its recorded checksum")
    if fresh or not old:
        public = {k: v for k, v in (params or {}).items() if k != "key"}
        record = {"url": url, "params": public, "file": dest.name,
                  "accessed": date.today().isoformat(), "sha256": digest}
        manifest.write_text(json.dumps(record, indent=2))
    return dest


def clean_fips(values):
    """FIPS as 5-character zero-padded strings."""
    return pd.Series(values).astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)


def drop_territories(df):
    keep = ~df["fips"].str[:2].isin(TERRITORIES)
    print(f"Dropped {(~keep).sum()} territory rows")
    return df[keep]


def save_checks(rows, name):
    """Write (dimension, check, count, example) rows to outputs/quality/<name>_checks.csv."""
    path = QUALITY / f"{name}_checks.csv"
    pd.DataFrame(rows, columns=["dimension", "check", "count", "example"]).to_csv(path, index=False)
    print(f"Wrote {path.relative_to(ROOT)}")
