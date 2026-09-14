"""
Where the cliff bites: the 400% FPL discontinuity by age and place.

The cliff is not one number. It is the benchmark premium less what the
household would have contributed at 400% of the poverty level, and the
benchmark varies by a factor of three across the federal marketplace and by
the statutory 3:1 age band on top of that. A 64-year-old in a high-premium
rural rating area faces a cliff several times the size of a 27-year-old's in a
competitive urban one.

Two quantities are computed for every rating area and age:

  cliff_dollars    the jump in annual net premium between 400% and just over
                   400% of the poverty level, in 2026
  cliff_pct_income the same jump as a share of income at that point

and, because a cliff only matters if it is survivable, the share of income the
full unsubsidised premium takes at several points above the threshold.

Writes Tables 2 and 3.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config
from subsidy import applicable_pct, income_at


def cliff_table(bench, year=2026):
    """Annual net-premium jump at the 400% FPL threshold, by area and age."""
    b = bench[bench["year"] == year].copy()
    b = b[b["slcsp"].notna()]

    # Income at 400% FPL is state-specific: Alaska and Hawaii have their own
    # poverty guidelines.
    income_400 = b["StateCode"].map(lambda s: income_at(400, year, state=s))
    pct_400 = applicable_pct(400, year)
    contribution_400 = income_400 * pct_400
    b["income_400"] = income_400

    b["gross_annual"] = b["slcsp"] * 12.0
    b["net_at_400"] = np.minimum(b["gross_annual"], contribution_400)
    b["net_above_400"] = b["gross_annual"]          # no credit past the cliff
    b["cliff_dollars"] = b["net_above_400"] - b["net_at_400"]
    b["cliff_pct_income"] = 100 * b["cliff_dollars"] / income_400
    b["gross_pct_income_400"] = 100 * b["gross_annual"] / income_400
    return b


def main():
    bench = pd.read_csv(config.DERIVED / "benchmarks.csv")
    c = cliff_table(bench)
    c.to_csv(config.DERIVED / "cliff.csv", index=False)

    # ---- Table 2: by age ---------------------------------------------------
    rows = []
    for age in config.AGE_GRID:
        s = c[c["age"] == age]
        if s.empty:
            continue
        rows.append({
            "age": age,
            "n_rating_areas": len(s),
            "gross_median": s["gross_annual"].median(),
            "cliff_median": s["cliff_dollars"].median(),
            "cliff_p90": s["cliff_dollars"].quantile(0.90),
            "cliff_max": s["cliff_dollars"].max(),
            "cliff_pct_income_median": s["cliff_pct_income"].median(),
            "gross_pct_income_median": s["gross_pct_income_400"].median(),
        })
    t2 = pd.DataFrame(rows)
    t2.to_csv(config.TABLES / "table2_cliff_by_age.csv", index=False)

    inc = income_at(400, 2026)
    print(f"=== The 400% FPL cliff in 2026 (income ${inc:,.0f}) ===")
    print(f"  {'age':>4} {'gross':>9} {'cliff':>9} {'cliff p90':>10} "
          f"{'cliff max':>10} {'cliff % inc':>12} {'gross % inc':>12}")
    for _, r in t2.iterrows():
        print(f"  {int(r['age']):>4} {r['gross_median']:>9,.0f} "
              f"{r['cliff_median']:>9,.0f} {r['cliff_p90']:>10,.0f} "
              f"{r['cliff_max']:>10,.0f} {r['cliff_pct_income_median']:>11.1f}% "
              f"{r['gross_pct_income_median']:>11.1f}%")

    # ---- Table 3: by state, age 60 (where the cliff is largest) ------------
    s60 = c[c["age"] == 60]
    st = (s60.groupby("StateCode")
          .agg(n_rating_areas=("RatingAreaId", "nunique"),
               gross_median=("gross_annual", "median"),
               cliff_median=("cliff_dollars", "median"),
               cliff_pct_income=("cliff_pct_income", "median"),
               gross_pct_income=("gross_pct_income_400", "median"))
          .sort_values("cliff_median", ascending=False).reset_index())
    st.to_csv(config.TABLES / "table3_cliff_by_state.csv", index=False)

    print(f"\n=== Age 60, by state: the ten largest cliffs ===")
    print(f"  {'state':>5} {'areas':>6} {'gross':>9} {'cliff':>9} "
          f"{'cliff % inc':>12} {'gross % inc':>12}")
    for _, r in st.head(10).iterrows():
        print(f"  {r['StateCode']:>5} {int(r['n_rating_areas']):>6} "
              f"{r['gross_median']:>9,.0f} {r['cliff_median']:>9,.0f} "
              f"{r['cliff_pct_income']:>11.1f}% {r['gross_pct_income']:>11.1f}%")
    print("  ...")
    for _, r in st.tail(3).iterrows():
        print(f"  {r['StateCode']:>5} {int(r['n_rating_areas']):>6} "
              f"{r['gross_median']:>9,.0f} {r['cliff_median']:>9,.0f} "
              f"{r['cliff_pct_income']:>11.1f}% {r['gross_pct_income']:>11.1f}%")

    # ---- how unaffordable is unsubsidised cover just above the cliff? ------
    print(f"\n=== Just above the cliff, the full premium as a share of income ===")
    for age in (27, 40, 60, 64):
        s = c[c["age"] == age]
        if s.empty:
            continue
        share = s["gross_pct_income_400"]
        over = 100 * (share > 20).mean()
        print(f"  age {age:>2}: median {share.median():5.1f}% of income, "
              f"{over:5.1f}% of rating areas above 20%")

    print(f"\nwrote tables 2 and 3")


if __name__ == "__main__":
    main()
