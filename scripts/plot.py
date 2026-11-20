"""County scatter plots for the interim report."""
import matplotlib.pyplot as plt
import pandas as pd

from utils import FIGURES, PROCESSED


def scatter(x, y, xlabel, ylabel, title, filename):
    fig, ax = plt.subplots(figsize=(6, 4.5))
    ax.scatter(x, y, s=8, alpha=0.3)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(FIGURES / filename, dpi=150)
    plt.close(fig)


merged = pd.read_csv(PROCESSED / "county_merged.csv", dtype={"fips": str})
scatter(merged["median_hh_income"] / 1000, merged["diabetes_pct"], "Median household income ($1,000s)",
        "Diabetes, age-adjusted (%)", "Median household income vs. diabetes prevalence by county",
        "fig1_income_diabetes.png")
scatter(merged["poverty_rate_pct"], merged["obesity_pct"], "Poverty rate (%)",
        "Obesity, age-adjusted (%)", "Poverty rate vs. obesity prevalence by county",
        "fig2_poverty_obesity.png")
scatter(merged["grocery_per_1k"], merged["diabetes_pct"], "Grocery stores per 1,000 residents",
        "Diabetes, age-adjusted (%)", "Grocery store availability vs. diabetes prevalence by county",
        "fig3_grocery_diabetes.png")
print("Wrote 3 figures")
