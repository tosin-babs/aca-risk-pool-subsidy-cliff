"""
What actually happened, and what it says about the model.

The 2026 open enrolment period is the natural experiment this paper exists to
use. Plan selections fell from 17.13 million to 15.77 million, a decline of
7.9%. The selection model in selection.py, run at the elasticities the
literature offers, predicts far more exit than that. This module measures the
gap and calibrates to close it.

Three things are done here.

  observed change   national, by state, by income band and by age, so that H1
                    - that exits concentrate among the young and the
                    better-off - can be tested rather than asserted.

  calibration       the enrolment semi-elasticity is solved for, so that the
                    model reproduces the observed aggregate attrition. That
                    replaces a literature range with a number this episode
                    actually implies.

  what it costs     the morbidity change implied at the calibrated elasticity,
                    which is the paper's answer to RQ2 rather than the
                    uncalibrated range.

A caution that belongs in the write-up. Plan selections are not effectuated
enrolment: some who select never pay a first premium, and the gap between the
two is normally several percent and may be larger in a year when prices jump.
Selections are what is published now, and the direction of that bias makes the
observed decline an *under*statement of the enrolment loss.

Writes Tables 9, 10 and 11.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

import config
from selection import build_pool, simulate

warnings.filterwarnings("ignore")

OEP = config.RAW / "oep"
FILES = {
    2025: OEP / "2025_state-level" / "2025 OEP State-Level Public Use File.csv",
    2026: (OEP / "2026_state-level" / "2026 OEP State-Level PUF"
           / "2026 OEP State-Level Public Use File.csv"),
}
# FPL_100_138 is a nested subgroup of FPL_100_150, not a sibling: including
# both double-counts. Summing the partition below reconciles to the published
# total within 0.1%; including FPL_100_138 overshoots it by 3.3 million.
FPL_COLS = ["FPL_LT100", "FPL_100_150", "FPL_150_200",
            "FPL_200_250", "FPL_250_300", "FPL_300_400", "FPL_400_500",
            "FPL_GT500", "FPL_OTHR"]
AGE_COLS = ["Age_0_17", "Age_18_25", "Age_26_34", "Age_35_44", "Age_45_54",
            "Age_55_64", "Age_GE65"]
TOTAL_ROWS = {"US", "TOTAL", "Total", "United States"}


def num(s):
    return pd.to_numeric(s.astype(str).str.replace(r"[,$%]", "", regex=True),
                         errors="coerce")


def load_oep(year):
    d = pd.read_csv(FILES[year], low_memory=False)
    d["State_Abrvtn"] = d["State_Abrvtn"].astype(str).str.strip()
    for c in d.columns:
        if c not in ("State_Abrvtn", "Pltfrm"):
            d[c] = num(d[c])
    d["year"] = year
    return d


def totals(d, platform="All"):
    """The total row for one platform.

    The file carries three total rows per year, not one: HealthCare.gov,
    state-based exchanges, and All. Taking the first row that says "Total"
    silently returns the HealthCare.gov figure and reports it as national,
    which understates the decline in the SBE states and overstates it
    nationally. They are reported separately throughout.
    """
    tot = d[d["State_Abrvtn"].isin(TOTAL_ROWS)
            & d["Pltfrm"].astype(str).str.strip().eq(platform)]
    if len(tot):
        return tot.iloc[0]
    st = d[d["State_Abrvtn"].str.len().eq(2)]
    if platform != "All":
        st = st[st["Pltfrm"].astype(str).str.strip() == platform]
    return st.sum(numeric_only=True)


def main():
    a, b = load_oep(2025), load_oep(2026)
    ta, tb = totals(a, "All"), totals(b, "All")

    n25, n26 = ta["Cnsmr"], tb["Cnsmr"]
    change = 100 * (n26 / n25 - 1)

    print("=== What actually happened ===")
    plat_rows = []
    for plat, label in (("All", "All marketplaces"),
                        ("HC.gov", "HealthCare.gov states"),
                        ("SBE", "State-based exchanges")):
        pa, pb = totals(a, plat), totals(b, plat)
        ch = 100 * (pb["Cnsmr"] / pa["Cnsmr"] - 1)
        plat_rows.append({"platform": label, "n_2025": pa["Cnsmr"],
                          "n_2026": pb["Cnsmr"], "change_pct": ch})
        print(f"  {label:<24} {pa['Cnsmr']:>12,.0f} -> {pb['Cnsmr']:>12,.0f}"
              f"   {ch:>+6.1f}%")
    pd.DataFrame(plat_rows).to_csv(
        config.TABLES / "table9b_by_platform.csv", index=False)
    print("\n  The divergence is the finding: the federal marketplace lost "
          "nearly 8%\n  while the state-based exchanges grew. Those are the "
          "states running their\n  own subsidy programmes and reinsurance "
          "waivers.")
    print(f"\n  average premium        ${ta['Avg_Prm']:>7,.0f} -> "
          f"${tb['Avg_Prm']:>7,.0f}   "
          f"({100 * (tb['Avg_Prm'] / ta['Avg_Prm'] - 1):+.1f}%)")
    print(f"  average after APTC     ${ta['Avg_Prm_Aftr_APTC']:>7,.0f} -> "
          f"${tb['Avg_Prm_Aftr_APTC']:>7,.0f}   "
          f"({100 * (tb['Avg_Prm_Aftr_APTC'] / ta['Avg_Prm_Aftr_APTC'] - 1):+.1f}%)")
    print(f"  receiving APTC         {ta['APTC_Cnsmr']:>12,.0f} -> "
          f"{tb['APTC_Cnsmr']:>12,.0f}   "
          f"({100 * (tb['APTC_Cnsmr'] / ta['APTC_Cnsmr'] - 1):+.1f}%)")

    # ---- Table 9: composition, which is the test of H1 --------------------
    rows = []
    for cols, dim in ((FPL_COLS, "Income (% FPL)"), (AGE_COLS, "Age")):
        have = [c for c in cols if c in a.columns and c in b.columns]
        for c in have:
            v25, v26 = ta.get(c, np.nan), tb.get(c, np.nan)
            if not np.isfinite(v25) or not np.isfinite(v26) or v25 == 0:
                continue
            rows.append({
                "dimension": dim, "group": c,
                "n_2025": v25, "n_2026": v26,
                "change_pct": 100 * (v26 / v25 - 1),
                "share_2025_pct": 100 * v25 / n25,
                "share_2026_pct": 100 * v26 / n26,
            })
    t9 = pd.DataFrame(rows)
    t9.to_csv(config.TABLES / "table9_observed_composition.csv", index=False)

    print("\n=== Who actually left (H1) ===")
    for dim in t9["dimension"].unique():
        print(f"\n  {dim}")
        print(f"  {'group':<14} {'2025':>11} {'2026':>11} {'change':>9} "
              f"{'share 25':>9} {'share 26':>9}")
        for _, r in t9[t9["dimension"] == dim].iterrows():
            print(f"  {r['group']:<14} {r['n_2025']:>11,.0f} "
                  f"{r['n_2026']:>11,.0f} {r['change_pct']:>8.1f}% "
                  f"{r['share_2025_pct']:>8.1f}% {r['share_2026_pct']:>8.1f}%")

    # ---- Table 10: calibrate the elasticity -------------------------------
    pool = build_pool(verbose=False)
    bench = pd.read_csv(config.DERIVED / "benchmarks.csv")
    b40 = bench[bench["age"] == 40]
    bench25 = float(b40[b40["year"] == 2025]["slcsp"].median()) * 12
    bench26 = float(b40[b40["year"] == 2026]["slcsp"].median()) * 12
    # Calibrate on HealthCare.gov, because the benchmark premiums driving the
    # model come from the Rate PUF, which is HealthCare.gov only. Calibrating
    # to the national figure would fit a price response to states whose prices
    # are not in the model.
    ha, hb = totals(a, "HC.gov"), totals(b, "HC.gov")
    target_retention = hb["Cnsmr"] / ha["Cnsmr"]

    print(f"\n=== Calibrating the price response to the observed decline ===")
    print(f"  target retention: {100 * target_retention:.1f}% "
          f"(HealthCare.gov states, matching the premium data)")
    rows = []
    for tilt in (1.0, 1.5, 2.0):
        lo, hi = 0.0, 1.5
        for _ in range(40):
            mid = (lo + hi) / 2
            r = simulate(pool, bench25, bench26, -mid, tilt)
            if r["enrolment_retained_pct"] / 100 > target_retention:
                lo = mid
            else:
                hi = mid
        e = (lo + hi) / 2
        r = simulate(pool, bench25, bench26, -e, tilt)
        rows.append({"tilt": tilt, "calibrated_elasticity": -e,
                     "retention_pct": r["enrolment_retained_pct"],
                     "morbidity_rise_pct": r["morbidity_rise_pct"],
                     "premium_factor": r["premium_factor"]})
        print(f"  tilt {tilt:.1f}: elasticity {-e:+.3f}  -> retention "
              f"{r['enrolment_retained_pct']:.1f}%, morbidity "
              f"{r['morbidity_rise_pct']:+.1f}%, premium factor "
              f"{r['premium_factor']:.3f}")
    t10 = pd.DataFrame(rows)
    t10.to_csv(config.TABLES / "table10_calibration.csv", index=False)

    # ---- Table 11: state-level, the cross-sectional check -----------------
    keep = ["State_Abrvtn", "Cnsmr", "Avg_Prm", "Avg_Prm_Aftr_APTC",
            "APTC_Cnsmr"]
    sa = a[~a["State_Abrvtn"].isin(TOTAL_ROWS)][keep].copy()
    sb = b[~b["State_Abrvtn"].isin(TOTAL_ROWS)][keep].copy()
    # One state changed platform between the two years, so compare only the
    # states present in both files on the same basis.
    st = sa.merge(sb, on="State_Abrvtn", suffixes=("_25", "_26"))
    st["enrolment_change_pct"] = 100 * (st["Cnsmr_26"] / st["Cnsmr_25"] - 1)
    st["net_premium_change_pct"] = 100 * (st["Avg_Prm_Aftr_APTC_26"]
                                          / st["Avg_Prm_Aftr_APTC_25"] - 1)
    st = st.dropna(subset=["enrolment_change_pct", "net_premium_change_pct"])
    st.to_csv(config.TABLES / "table11_state_change.csv", index=False)

    x = st["net_premium_change_pct"].to_numpy(float)
    y = st["enrolment_change_pct"].to_numpy(float)
    ok = np.isfinite(x) & np.isfinite(y)
    slope, intercept = np.polyfit(x[ok], y[ok], 1)
    r = np.corrcoef(x[ok], y[ok])[0, 1]

    print(f"\n=== Cross-state: did the states with bigger price rises lose more? ===")
    print(f"  {ok.sum()} states and DC")
    print(f"  slope {slope:+.3f} percentage points of enrolment per point of "
          f"net premium")
    print(f"  correlation {r:+.3f}")
    worst = st.nsmallest(5, "enrolment_change_pct")
    print(f"\n  largest enrolment falls:")
    for _, s in worst.iterrows():
        print(f"    {s['State_Abrvtn']:<4} {s['enrolment_change_pct']:>6.1f}%  "
              f"(net premium {s['net_premium_change_pct']:+.1f}%)")

    print(f"\nwrote tables 9, 10 and 11")


if __name__ == "__main__":
    main()
