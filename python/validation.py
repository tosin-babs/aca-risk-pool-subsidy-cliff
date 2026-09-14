"""
What happened in the 2026 open enrollment period.

Plan selections from the CMS OEP state-level public use files, 2024-2026.
Three corrections to how these files were read in an earlier version, each of
which moved a headline number:

  platform    Illinois left HealthCare.gov for 2026 (and Georgia for 2025), so
              each year's own platform total compares different states. The
              published totals showed HealthCare.gov -7.9% and state-based
              exchanges +2.3%; on the same states the figures are about -5%
              and -4%, which is what the CMS 2026 OEP report itself says.
  income      Connecticut, Minnesota and New York reported known incomes above
              400% FPL as "other" in 2026, and DC suppressed most income cells.
              The national count above 400% FPL therefore fell partly by
              relabelling. Band comparisons exclude those four.
  sample      The premium data cover the 30 HealthCare.gov states of 2026, so
              those states are the primary sample for anything that combines
              enrollment with premiums.

Writes Tables 9, 9b and 11. The calibration formerly here is in selection.py.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

import config
import oep

warnings.filterwarnings("ignore")


def platform_table():
    rows = []
    for plat, label in (("All", "All marketplaces"),
                        ("HC.gov", "HealthCare.gov"),
                        ("SBE", "State-based exchanges")):
        pub25 = oep.published_total(2025, plat)["Cnsmr"]
        pub26 = oep.published_total(2026, plat)["Cnsmr"]
        states = (tuple(oep.state_file(2026).index) if plat == "All"
                  else oep.platform_states(plat))
        s25 = oep.total(2025, states, ["Cnsmr"])["Cnsmr"]
        s26 = oep.total(2026, states, ["Cnsmr"])["Cnsmr"]
        rows.append({"platform": label,
                     "published_2025": pub25, "published_2026": pub26,
                     "published_change_pct": 100 * (pub26 / pub25 - 1),
                     "same_states_n": len(states),
                     "same_states_2025": s25, "same_states_2026": s26,
                     "same_states_change_pct": 100 * (s26 / s25 - 1)})
    return pd.DataFrame(rows)


def composition_table():
    """Selections by income and age band in three samples, 2025 and 2026."""
    samples = {"hcgov": oep.band_sample_states("hcgov"),
               "all": oep.band_sample_states("all"),
               "published": tuple(oep.state_file(2026).index)}
    cols = (["FPL_LT100"] + config.OEP_BANDS + ["FPL_OTHR"]
            + ["Age_0_17"] + config.OEP_AGE_COLS + ["Age_GE65"])
    rows = []
    for name, states in samples.items():
        t = {y: oep.total(y, states, cols + ["Cnsmr"])
             for y in config.OEP_YEARS}
        for c in cols:
            dim = "Income" if c.startswith("FPL") else "Age"
            rows.append({
                "sample": name, "dimension": dim, "group": c,
                "n_2024": t[2024][c], "n_2025": t[2025][c],
                "n_2026": t[2026][c],
                "change_2024_25_pct": 100 * (t[2025][c] / t[2024][c] - 1),
                "change_2025_26_pct": 100 * (t[2026][c] / t[2025][c] - 1),
                "share_2025_pct": 100 * t[2025][c] / t[2025]["Cnsmr"],
                "share_2026_pct": 100 * t[2026][c] / t[2026]["Cnsmr"],
            })
    return pd.DataFrame(rows)


def main():
    # Reconciliation: state rows sum to the published total, and the income
    # partition (without FPL_100_138) sums to the state total.
    for y in config.OEP_YEARS:
        d = oep.state_file(y)
        pub = oep.published_total(y)["Cnsmr"]
        part = d[["FPL_LT100"] + config.OEP_BANDS + ["FPL_OTHR"]].sum().sum()
        print(f"  {y}: state rows {d['Cnsmr'].sum():,.0f}, published "
              f"{pub:,.0f}, income partition {part:,.0f}")

    t9b = platform_table()
    t9b.to_csv(config.TABLES / "table9b_by_platform.csv", index=False)
    print("\n=== Plan selections by platform ===")
    for _, r in t9b.iterrows():
        print(f"  {r['platform']:<24} published {r['published_change_pct']:+6.1f}%"
              f"   same {int(r['same_states_n'])} states "
              f"{r['same_states_change_pct']:+6.1f}%")

    t9 = composition_table()
    t9.to_csv(config.TABLES / "table9_observed_composition.csv", index=False)
    print("\n=== Selections by band, HealthCare.gov sample ===")
    for _, r in t9[t9["sample"] == "hcgov"].iterrows():
        print(f"  {r['group']:<12} {r['n_2025']:>11,.0f} -> {r['n_2026']:>11,.0f}"
              f"  {r['change_2025_26_pct']:+6.1f}%  (2024-25 "
              f"{r['change_2024_25_pct']:+6.1f}%)")

    # State-level change in total selections and in average net premium.
    keep = ["Cnsmr", "Avg_Prm", "Avg_Prm_Aftr_APTC", "APTC_Cnsmr"]
    a, b = oep.state_file(2025)[keep], oep.state_file(2026)[keep]
    st = a.join(b, lsuffix="_25", rsuffix="_26", how="inner")
    st["platform_2026"] = oep.state_file(2026)["Pltfrm"]
    st["enrolment_change_pct"] = 100 * (st["Cnsmr_26"] / st["Cnsmr_25"] - 1)
    st["net_premium_change_pct"] = 100 * (st["Avg_Prm_Aftr_APTC_26"]
                                          / st["Avg_Prm_Aftr_APTC_25"] - 1)
    st = st.reset_index().rename(columns={"index": "State_Abrvtn"})
    st.to_csv(config.TABLES / "table11_state_change.csv", index=False)
    print(f"\nwrote tables 9, 9b and 11")


if __name__ == "__main__":
    main()
