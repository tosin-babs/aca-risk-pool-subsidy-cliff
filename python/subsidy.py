"""
Net premiums under the 2025 and 2026 subsidy schedules.

The premium tax credit is the benchmark premium less what the household is
expected to contribute, and the expected contribution is a percentage of
household income that rises with income as a multiple of the federal poverty
level. Two things changed between 2025 and 2026 and they compound:

  * the benchmark premium rose, by a median of 24% for a 40-year-old; and
  * the applicable-percentage schedule reverted from the enhanced version to
    the original one, which contributes nothing below 150% FPL under the
    enhanced schedule but 2-4% under the original, caps at 8.5% under the
    enhanced schedule but at 9.79% under the original, and - the change that
    dominates everything else - reinstates the cliff at 400% FPL, above which
    no credit is paid at all.

Someone at 401% of the poverty level went from paying 8.5% of income to
paying the entire premium. That is the subsidy cliff, and this module measures
it for every rating area and age in the federal marketplace.

This is a single-person calculation. A family's benchmark is the sum of
member-level rates and its FPL threshold rises with size, so the *rate* of
change is similar but the levels are not; extending to families needs the
household composition that comes with the ACS build.

Writes Table 1 and data/derived/net_premiums.csv.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config


def applicable_pct(fpl_pct, year):
    """Expected contribution as a share of income, interpolated in bracket.

    Returns NaN where no credit is payable, which under the 2026 schedule is
    everything above 400% of the poverty level.
    """
    schedule = config.APPLICABLE_PCT[year]
    lower = 0.0
    for upper, start, end in schedule:
        if fpl_pct <= upper:
            if start is None:
                return np.nan                    # the cliff
            if upper == float("inf") or end == start:
                return start
            frac = (fpl_pct - lower) / (upper - lower)
            return start + frac * (end - start)
        lower = upper
    return np.nan


def income_at(fpl_pct, year, household_size=1):
    fpl = (config.FPL_BASE[year]
           + config.FPL_INCREMENT[year] * (household_size - 1))
    return fpl * fpl_pct / 100.0


def net_premium_table(bench):
    """Net benchmark premium by rating area, age, FPL and year."""
    rows = []
    for year in config.YEARS:
        b = bench[bench["year"] == year]
        for fpl in config.FPL_GRID:
            pct = applicable_pct(fpl, year)
            income = income_at(fpl, year)
            expected = np.nan if np.isnan(pct) else income * pct
            for age in config.AGE_GRID:
                sub = b[b["age"] == age]
                if sub.empty:
                    continue
                gross = sub["slcsp"].to_numpy(float) * 12.0   # annualised
                if np.isnan(expected):
                    aptc = np.zeros_like(gross)
                    net = gross
                else:
                    aptc = np.maximum(gross - expected, 0.0)
                    net = gross - aptc
                rows.append({
                    "year": year, "fpl_pct": fpl, "age": age,
                    "income": income,
                    "applicable_pct": pct,
                    "expected_contribution": expected,
                    "gross_benchmark_median": float(np.median(gross)),
                    "aptc_median": float(np.median(aptc)),
                    "net_premium_median": float(np.median(net)),
                    "net_premium_p25": float(np.percentile(net, 25)),
                    "net_premium_p75": float(np.percentile(net, 75)),
                    "net_as_pct_of_income": float(np.median(net)) / income * 100,
                    "n_rating_areas": int(sub["slcsp"].notna().sum()),
                })
    return pd.DataFrame(rows)


def main():
    bench = pd.read_csv(config.DERIVED / "benchmarks.csv")
    t = net_premium_table(bench)
    t.to_csv(config.DERIVED / "net_premiums.csv", index=False)

    # ---- Table 1: the change, for a single 40-year-old ---------------------
    a = t[t["age"] == 40].pivot_table(index="fpl_pct", columns="year",
                                      values=["net_premium_median",
                                              "gross_benchmark_median",
                                              "net_as_pct_of_income"])
    # Each year is measured against its own poverty guidelines: the same
    # percentage of the poverty level is a different income in 2025 and 2026,
    # and comparing a 2025 premium with a 2026 income would overstate the
    # burden change.
    out = pd.DataFrame({
        "fpl_pct": a.index,
        "income_2025": [income_at(f, 2025) for f in a.index],
        "income_2026": [income_at(f, 2026) for f in a.index],
        "gross_2025": a[("gross_benchmark_median", 2025)].values,
        "gross_2026": a[("gross_benchmark_median", 2026)].values,
        "net_2025": a[("net_premium_median", 2025)].values,
        "net_2026": a[("net_premium_median", 2026)].values,
    })
    out["net_change_dollars"] = out["net_2026"] - out["net_2025"]
    out["net_change_pct"] = np.where(
        out["net_2025"] > 0, 100 * (out["net_2026"] / out["net_2025"] - 1),
        np.inf)
    out["net_pct_income_2025"] = 100 * out["net_2025"] / out["income_2025"]
    out["net_pct_income_2026"] = 100 * out["net_2026"] / out["income_2026"]
    out.to_csv(config.TABLES / "table1_net_premiums.csv", index=False)

    print("=== Annual net benchmark premium, single 40-year-old, "
          "median rating area ===")
    print(f"  {'FPL':>5} {'inc 25':>8} {'inc 26':>8} {'net 25':>8} "
          f"{'net 26':>8} {'change':>9} {'% of own-year income':>22}")
    for _, r in out.iterrows():
        chg = ("  +inf" if not np.isfinite(r['net_change_pct'])
               else f"{r['net_change_pct']:+6.0f}%")
        print(f"  {int(r['fpl_pct']):>4}% {r['income_2025']:>8,.0f} "
              f"{r['income_2026']:>8,.0f} {r['net_2025']:>8,.0f} "
              f"{r['net_2026']:>8,.0f} {r['net_change_dollars']:>+8,.0f} {chg:>7}  "
              f"{r['net_pct_income_2025']:>5.1f}% -> {r['net_pct_income_2026']:>5.1f}%")

    cliff = out[out["fpl_pct"].isin([400, 401])]
    if len(cliff) == 2:
        lo, hi = cliff.iloc[0], cliff.iloc[1]
        print(f"\n=== The cliff ===")
        print(f"  at 400% FPL the net premium is ${lo['net_2026']:,.0f}")
        print(f"  at 401% FPL it is ${hi['net_2026']:,.0f}")
        print(f"  one extra dollar of income costs "
              f"${hi['net_2026'] - lo['net_2026']:,.0f}")
        print(f"  in 2025 the same step cost "
              f"${hi['net_2025'] - lo['net_2025']:,.0f}")

    print(f"\nwrote table 1 and net_premiums.csv")


if __name__ == "__main__":
    main()
