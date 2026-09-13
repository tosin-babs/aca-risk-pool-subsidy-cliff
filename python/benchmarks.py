"""
Benchmark and lowest-cost premiums by rating area and age, 2025 and 2026.

The premium tax credit is defined against the second-lowest-cost silver plan
available to the enrollee - the benchmark. Everything downstream of the
subsidy schedule depends on getting that one number right for each rating
area and age, in each year, so it is computed here and nowhere else.

Three details do the work:

  * The Rate PUF lists every plan-age-rating-area-tobacco combination, but
    issuers file a large sentinel rate for combinations they do not sell.
    Those are screened before any ordering is taken.
  * A benchmark is the *second* lowest silver premium, not the lowest. Where
    only one silver plan is offered, that plan is the benchmark, which is the
    rule CMS applies.
  * Child-only plans cannot be an adult's benchmark, and SHOP plans are not in
    the individual market at all. Both are excluded via the Plan Attributes
    PUF.

Writes data/derived/benchmarks.csv.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

import config

warnings.filterwarnings("ignore")

RATE_COLS = ["BusinessYear", "StateCode", "PlanId", "RatingAreaId", "Tobacco",
             "Age", "IndividualRate"]
PLAN_COLS = ["BusinessYear", "StateCode", "StandardComponentId", "MetalLevel",
             "MarketCoverage", "ChildOnlyOffering"]


def parse_age(series):
    """Rate PUF ages are strings with a label at each end of the band."""
    s = series.astype(str).str.strip()
    out = pd.to_numeric(s, errors="coerce")
    out = out.where(~s.eq(config.AGE_MIN_LABEL), config.AGE_MIN_VALUE)
    out = out.where(~s.str.startswith("64"), config.AGE_MAX_VALUE)
    return out


def load_plans(year):
    """Individual-market, adult-eligible plans with their metal level."""
    d = pd.read_csv(config.PLAN_PUF[year], usecols=lambda c: c in PLAN_COLS,
                    low_memory=False)
    d = d[d["MarketCoverage"] == "Individual"]
    # "Allows Adult and Child-Only" is fine; a child-only *plan* is not.
    d = d[~d["ChildOnlyOffering"].astype(str).str.strip()
          .eq("Allows Child-Only")]
    d = d[["StateCode", "StandardComponentId", "MetalLevel"]].drop_duplicates()
    return d


def load_rates(year):
    d = pd.read_csv(config.RATE_PUF[year], usecols=RATE_COLS, low_memory=False)
    # Non-tobacco is the rate the benchmark is defined on.
    tob = d["Tobacco"].astype(str).str.strip().str.lower()
    d = d[tob.str.startswith("no preference") | tob.str.startswith("tobacco user/non")]
    d["age"] = parse_age(d["Age"])
    d = d[d["age"].notna()]
    d["rate"] = pd.to_numeric(d["IndividualRate"], errors="coerce")
    d = d[(d["rate"] > 0) & (d["rate"] < config.RATE_SENTINEL)]
    # PlanId in the Rate PUF is the 14-character standard component id.
    d["StandardComponentId"] = d["PlanId"].astype(str).str.strip().str[:14]
    return d[["StateCode", "StandardComponentId", "RatingAreaId", "age", "rate"]]


def benchmark_for(year):
    plans = load_plans(year)
    rates = load_rates(year)
    d = rates.merge(plans, on=["StateCode", "StandardComponentId"], how="inner")
    print(f"  {year}: {len(rates):,} priced rows -> {len(d):,} matched to a "
          f"metal level")

    key = ["StateCode", "RatingAreaId", "age"]

    silver = d[d["MetalLevel"] == config.BENCHMARK_METAL]
    g = silver.groupby(key)["rate"]
    # Second lowest where two or more exist, otherwise the only one.
    slcsp = g.apply(lambda s: s.nsmallest(2).iloc[-1] if len(s) else np.nan)
    n_silver = g.size()

    bronze = d[d["MetalLevel"].isin(config.LOWEST_COST_METAL)]
    lcbp = bronze.groupby(key)["rate"].min()

    out = pd.DataFrame({"slcsp": slcsp, "n_silver_plans": n_silver,
                        "lowest_bronze": lcbp}).reset_index()
    out["year"] = year
    return out


def main():
    print("Computing benchmark premiums from the CMS Rate PUFs ...")
    frames = [benchmark_for(y) for y in config.YEARS]
    b = pd.concat(frames, ignore_index=True)

    out = config.DERIVED / "benchmarks.csv"
    b.to_csv(out, index=False)

    print(f"\n  {len(b):,} rating-area x age x year cells")
    print(f"  states: {b['StateCode'].nunique()}   "
          f"rating areas: {b.groupby(['StateCode', 'RatingAreaId']).ngroups}")

    # --- the headline: how much did the benchmark move? ---------------------
    a40 = b[b["age"] == 40].pivot_table(index=["StateCode", "RatingAreaId"],
                                        columns="year", values="slcsp")
    a40 = a40.dropna()
    a40["pct_change"] = 100 * (a40[2026] / a40[2025] - 1)
    print(f"\n=== Benchmark silver premium, age 40, {len(a40):,} rating areas ===")
    print(f"  2025 median  ${a40[2025].median():,.0f}")
    print(f"  2026 median  ${a40[2026].median():,.0f}")
    print(f"  median change  {a40['pct_change'].median():+.1f}%")
    print(f"  interquartile  {a40['pct_change'].quantile(.25):+.1f}% to "
          f"{a40['pct_change'].quantile(.75):+.1f}%")

    st = (a40.reset_index().groupby("StateCode")["pct_change"].median()
          .sort_values())
    print("\n  smallest increases:")
    for s, v in st.head(5).items():
        print(f"    {s}  {v:+6.1f}%")
    print("  largest increases:")
    for s, v in st.tail(5).items():
        print(f"    {s}  {v:+6.1f}%")

    print(f"\nwrote {out.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
