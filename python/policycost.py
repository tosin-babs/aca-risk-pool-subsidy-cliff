"""
RQ5: what restoring credits would cost per person-year of coverage.

Outlay is the extra credit times everyone the band would contain. Coverage
gained is the gap between the band's 2025 count moved at the control band's
rate and its observed 2026 count. The cost per person-year is outlay over
coverage gained; the marginal share is the fraction of outlay reaching
households whose coverage it changes.

Four schedules are priced on 2026 premiums and 2026 poverty levels:

  full         the 2025 enhanced schedule
  capped       the enhanced schedule up to POLICY_PARTIAL_CEILING % FPL, no
               credit above
  below_only   the enhanced schedule up to 400% FPL, no credit above
  cliff_only   the 2026 schedule, with its 9.96% cap extended above 400%

For schedules other than full, a band recovers the share of its full-
restoration coverage gain equal to the share of the full payment reduction
the schedule delivers (age-weighted dollars). That proportionality is an
assumption, stated where it is used.

Counts are from the 30 HealthCare.gov states, matching the premium data; a
second block applies the same per-person figures to all states whose income
reporting is consistent, for comparison with CBO's national estimate.
Coverage gained above 400% is shown before and after removing the bunching
excess of Table 16, which is relabelling rather than loss of coverage.

Writes Tables 21 and 22.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

import config
import oep
from benchmarks import band_gross, load_benchmarks
from subsidy import applicable_pct, net_payment

warnings.filterwarnings("ignore")


def schedule(name):
    ceil = config.POLICY_PARTIAL_CEILING
    cap26 = applicable_pct(400, 2026)
    if name == "full":
        return lambda f: applicable_pct(f, 2025)
    if name == "capped":
        return lambda f: applicable_pct(f, 2025) if f <= ceil else np.nan
    if name == "below_only":
        return lambda f: applicable_pct(f, 2025) if f <= 400 else np.nan
    if name == "cliff_only":
        return lambda f: applicable_pct(f, 2026) if f <= 400 else cap26
    if name == "current":
        return lambda f: applicable_pct(f, 2026)
    raise ValueError(name)


SCENARIOS = {
    "full": "Restore the enhanced schedule",
    "capped": f"Enhanced schedule to {config.POLICY_PARTIAL_CEILING}% FPL",
    "below_only": "Enhanced schedule to 400% FPL only",
    "cliff_only": "2026 schedule, 9.96% cap extended above 400%",
}


def band_payment(gb26, aw, band, rule):
    """Age-weighted mean annual payment for the benchmark in a band."""
    vals = []
    for f in config.BAND_MIDPOINTS[band]:
        vals.append(sum(aw[c] * float(net_payment(np.array([gb26[c]]), f, 2026,
                                                  schedule=rule)[0])
                        for c in config.OEP_AGE_COLS))
    return float(np.mean(vals))


def price(states, gb26, aw, excess_above):
    n25 = oep.total(2025, states, config.OEP_BANDS)
    n26 = oep.total(2026, states, config.OEP_BANDS)
    ctrl = config.POLICY_CONTROL_BAND
    drift = n26[ctrl] / n25[ctrl] - 1
    pay_now = {b: band_payment(gb26, aw, b, schedule("current"))
               for b in config.OEP_BANDS}
    pay_full = {b: band_payment(gb26, aw, b, schedule("full"))
                for b in config.OEP_BANDS}
    lost_above = sum(max(n25[b] * (1 + drift) - n26[b], 0)
                     for b in config.EXPOSED_BANDS)
    rows = []
    for key, label in SCENARIOS.items():
        rule = schedule(key)
        for b in config.OEP_BANDS:
            pay = band_payment(gb26, aw, b, rule)
            extra = pay_now[b] - pay
            full_red = pay_now[b] - pay_full[b]
            phi = float(np.clip(extra / full_red, 0, 1)) if full_red > 1 else 0.0
            gained_full = (np.nan if b == ctrl
                           else max(n25[b] * (1 + drift) - n26[b], 0.0))
            gained = np.nan if b == ctrl else gained_full * phi
            # Bunching: part of the loss above 400% is relabelling into the
            # 300-400% band, allocated across the exposed bands pro rata.
            if b in config.EXPOSED_BANDS and lost_above > 0 and not np.isnan(gained):
                share = max(n25[b] * (1 + drift) - n26[b], 0) / lost_above
                gained_net = max(gained - phi * excess_above * share, 0.0)
            else:
                gained_net = gained
            covered = n26[b] + (0.0 if np.isnan(gained) else gained)
            cost = max(extra, 0.0) * covered
            rows.append({"scenario": key, "scenario_label": label, "band": b,
                         "segment": config.OEP_BAND_LABELS[b],
                         "is_control": b == ctrl, "n_2025": n25[b],
                         "n_2026": n26[b], "control_drift_pct": 100 * drift,
                         "extra_credit_per_person": extra,
                         "share_of_full_reduction": phi,
                         "coverage_gained": gained,
                         "coverage_gained_net_of_bunching": gained_net,
                         "annual_cost": cost,
                         "cost_per_person_year_gained":
                             cost / gained if gained and gained > 0 else np.nan,
                         "marginal_share_pct":
                             100 * gained / covered
                             if covered and not np.isnan(gained) else np.nan})
    return pd.DataFrame(rows)


def summarise(t, sample):
    rows = []
    for key, g in t.groupby("scenario", sort=False):
        cost, gain = g["annual_cost"].sum(), g["coverage_gained"].sum()
        gain_net = g["coverage_gained_net_of_bunching"].sum()
        ctrl_cost = g[g["is_control"]]["annual_cost"].sum()
        above = g[g["band"].isin(config.EXPOSED_BANDS)]
        rows.append({"sample": sample, "scenario": key,
                     "scenario_label": SCENARIOS[key],
                     "annual_cost": cost, "coverage_gained": gain,
                     "coverage_gained_net_of_bunching": gain_net,
                     "cost_per_person_year": cost / gain if gain else np.nan,
                     "cost_per_person_year_net_of_bunching":
                         cost / gain_net if gain_net else np.nan,
                     "cost_per_person_year_excl_control":
                         (cost - ctrl_cost) / gain if gain else np.nan,
                     "share_cost_above_400_pct": 100 * above["annual_cost"].sum() / cost
                     if cost else np.nan,
                     "share_coverage_above_400_pct":
                         100 * above["coverage_gained"].sum() / gain if gain else np.nan})
    return pd.DataFrame(rows)


def main():
    hc = oep.hcgov_states()
    allst = oep.band_sample_states("all")
    bench = load_benchmarks(states=hc)
    gb26 = band_gross(bench, 2026)
    t16 = pd.read_csv(config.TABLES / "table16_bunching.csv")

    def excess_for(sample_prefix):
        r = t16[t16["sample"].str.startswith(sample_prefix)
                & (t16["control"] == "100-300% pooled")]
        return float(r["excess"].iloc[0])

    blocks, summaries = [], []
    for sample, states, pref in (("HealthCare.gov (30)", hc, "HealthCare"),
                                 (f"All consistent ({len(allst)})", allst, "All")):
        aw = oep.age_weights(2025, states)
        t = price(states, gb26, aw, excess_for(pref))
        t.insert(0, "sample", sample)
        blocks.append(t)
        summaries.append(summarise(t, sample))
    t21 = pd.concat(blocks, ignore_index=True)
    t22 = pd.concat(summaries, ignore_index=True)
    cbo = config.CBO_DEFICIT_2026_2035 / 10 / config.CBO_INSURED_2035
    t22["cbo_implied_cost_per_insured"] = cbo
    t21.to_csv(config.TABLES / "table21_policy_cost.csv", index=False)
    t22.to_csv(config.TABLES / "table22_allocation.csv", index=False)

    pd.set_option("display.width", 220)
    print("=== Scenario summary ===")
    print(t22.round(1).to_string(index=False))
    print("\n=== Full restoration by band, HealthCare.gov ===")
    print(t21[(t21["scenario"] == "full") & t21["sample"].str.startswith("Health")]
          [["segment", "extra_credit_per_person", "coverage_gained",
            "coverage_gained_net_of_bunching", "annual_cost",
            "cost_per_person_year_gained", "marginal_share_pct"]]
          .round(1).to_string(index=False))
    print(f"\n  CBO/CRS implied: ${cbo:,.0f} per person insured in 2035")
    print("\nwrote tables 21 and 22")


if __name__ == "__main__":
    main()
