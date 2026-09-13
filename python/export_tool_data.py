"""
Export the model payload for the public subsidy-cliff calculator.

The calculator has to answer one question for a real person: what did the
expiry of the enhanced premium tax credits do to what I pay? That needs the
benchmark premium for their state and age in both years, and both subsidy
schedules. Everything else it can compute in the browser.

The payload is the benchmark premium by state and single year of age, in both
years, with the rating-area spread carried alongside so the page can show that
a state median hides a wide range. 31 states x 51 ages x 2 years is small
enough to inline.

Writes tool/model_data.json.
"""

from __future__ import annotations

import json
from datetime import date

import numpy as np
import pandas as pd

import config

OUT = config.ROOT / "tool" / "model_data.json"

STATE_NAMES = {
    "AK": "Alaska", "AL": "Alabama", "AR": "Arkansas", "AZ": "Arizona",
    "DE": "Delaware", "FL": "Florida", "HI": "Hawaii", "IA": "Iowa",
    "IL": "Illinois", "IN": "Indiana", "KS": "Kansas", "LA": "Louisiana",
    "MI": "Michigan", "MO": "Missouri", "MS": "Mississippi", "MT": "Montana",
    "NC": "North Carolina", "ND": "North Dakota", "NE": "Nebraska",
    "NH": "New Hampshire", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon",
    "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee",
    "TX": "Texas", "UT": "Utah", "WI": "Wisconsin", "WV": "West Virginia",
    "WY": "Wyoming",
}


def main():
    b = pd.read_csv(config.DERIVED / "benchmarks.csv")
    b = b[b["slcsp"].notna()].copy()
    b["age"] = b["age"].astype(int)

    states = {}
    for (st, year), g in b.groupby(["StateCode", "year"]):
        by_age = (g.groupby("age")["slcsp"]
                  .agg(["median", "min", "max", "count"]).reset_index())
        rec = states.setdefault(st, {"name": STATE_NAMES.get(st, st),
                                     "areas": int(g["RatingAreaId"].nunique())})
        rec[str(year)] = {
            "age": by_age["age"].tolist(),
            "med": by_age["median"].round(2).tolist(),
            "lo": by_age["min"].round(2).tolist(),
            "hi": by_age["max"].round(2).tolist(),
        }

    # National medians, for the default view before a state is chosen.
    nat = {}
    for year, g in b.groupby("year"):
        by_age = g.groupby("age")["slcsp"].median().reset_index()
        nat[str(year)] = {"age": by_age["age"].tolist(),
                          "med": by_age["slcsp"].round(2).tolist()}

    payload = {
        "meta": {
            "source": "CMS Health Insurance Exchange Public Use Files, "
                      "Rate PUF and Plan Attributes PUF, plan years 2025 "
                      "and 2026",
            "states": len(states),
            "rating_areas": int(b.groupby(["StateCode", "RatingAreaId"])
                                .ngroups),
            "generated": date.today().isoformat(),
            "policy_status_as_of": config.POLICY_STATUS_AS_OF,
            "coverage_note": "HealthCare.gov states only. State-based "
                             "exchanges file their own rates and are not in "
                             "this file.",
        },
        "schedule": {
            "2025": [[u if np.isfinite(u) else None, s, e]
                     for u, s, e in config.APPLICABLE_PCT_2025],
            "2026": [[u if np.isfinite(u) else None, s, e]
                     for u, s, e in config.APPLICABLE_PCT_2026],
        },
        "fpl": {"base": config.FPL_BASE,
                "increment": config.FPL_INCREMENT},
        "national": nat,
        "states": states,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, separators=(",", ":")))
    print(f"wrote {OUT.relative_to(config.ROOT)} "
          f"({OUT.stat().st_size / 1024:,.0f} KB)")
    print(f"  {len(states)} states, {payload['meta']['rating_areas']} rating "
          f"areas, ages {b['age'].min()}-{b['age'].max()}")

    # ---- validation: the browser must reproduce the paper -------------------
    from subsidy import applicable_pct, income_at
    checks = []
    for year in (2025, 2026):
        med = np.median(b[(b["year"] == year) & (b["age"] == 40)]["slcsp"]) * 12
        for fpl in (200, 400, 401):
            pct = applicable_pct(fpl, year)
            inc = income_at(fpl, year)
            # Net premium is the smaller of the full premium and the
            # expected contribution; above the cliff there is no credit.
            net = med if np.isnan(pct) else min(med, inc * pct)
            checks.append((year, fpl, round(net)))
    print("\n  reference values the page must reproduce (age 40, national median):")
    for y, f, v in checks:
        print(f"    {y}  {f:>3}% FPL   ${v:,}")


if __name__ == "__main__":
    main()
