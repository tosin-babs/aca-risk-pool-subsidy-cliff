"""
Check that the manuscript's headline numbers still match the analysis output.

The prose is written by hand, so a rerun that moves an estimate leaves the text
stale unless someone notices. This reads the current tables, formats each
headline figure the way the manuscript writes it, and fails if the string is
absent. It also checks that every table cited is rendered and vice versa, that
every embedded figure exists, and that the prose carries no em dashes.

Run after run_all.py and before make_manuscript.py.
"""

from __future__ import annotations

import re
import sys

import numpy as np
import pandas as pd

import config

MS = config.ROOT / "manuscript" / "Paper4_manuscript.md"
T = config.TABLES


def load():
    t2 = pd.read_csv(T / "table2_cliff_by_age.csv").set_index("age")
    t4 = pd.read_csv(T / "table4_cost_model.csv").set_index("term")
    t5 = pd.read_csv(T / "table5_age_curve.csv").set_index("age_band")
    t9b = pd.read_csv(T / "table9b_by_platform.csv").set_index("platform")
    t10 = pd.read_csv(T / "table10_calibration.csv")
    t14 = pd.read_csv(T / "table14_segment_observed.csv").set_index("segment")
    t16 = pd.read_csv(T / "table16_bunching.csv")
    t17b = pd.read_csv(T / "table17b_cross_state_fit.csv")
    t18 = pd.read_csv(T / "table18_loss_ratios.csv").set_index("year")
    t19a = pd.read_csv(T / "table19a_mlr_distribution.csv").set_index("mlr_band")
    t20 = pd.read_csv(T / "table20_floor_bound.csv")
    t21 = pd.read_csv(T / "table21_policy_cost.csv")
    t22 = pd.read_csv(T / "table22_allocation.csv")
    t23 = pd.read_csv(T / "table23_did.csv")
    t24 = pd.read_csv(T / "table24_county_did.csv")
    t25 = pd.read_csv(T / "table25_reinsurance_premiums.csv")
    t8 = pd.read_csv(T / "table8_who_leaves.csv")

    bench = pd.read_csv(config.DERIVED / "benchmarks.csv")
    b40 = bench[bench["age"] == 40].pivot_table(
        index=["StateCode", "RatingAreaId"], columns="year",
        values="slcsp").dropna()
    bench_rise = float(np.median(100 * (b40[2026] / b40[2025] - 1)))

    prim = t10[t10["specification"].str.startswith("Primary")].set_index("tilt")
    two = t10[t10["specification"].str.startswith("Two")].set_index("tilt")
    b16 = t16[t16["sample"].str.startswith("Health")
              & (t16["control"] == "100-300% pooled")].iloc[0]
    fit = t17b.set_index(["outcome", "period"])
    exp_fit = fit.loc[("Change above 400% FPL", "2025-26")]
    plc_fit = fit.loc[("Change above 400% FPL", "2024-25 (placebo)")]
    did = t23[(t23["model"].str.startswith("A.")) & t23["sample"].str.startswith("Health")].set_index("term")
    dose = t23[t23["model"].str.startswith("B.")].set_index("term")
    cty = t24[t24["model"] == "County difference in differences"].set_index("term")
    hc21 = t21[t21["sample"].str.startswith("Health") & (t21["scenario"] == "full")].set_index("segment")
    s22 = t22.set_index(["sample", "scenario"])
    hc = [s for s in s22.index.get_level_values(0).unique() if s.startswith("Health")][0]
    al = [s for s in s22.index.get_level_values(0).unique() if s.startswith("All")][0]
    below_floor = t19a.loc[["under 70%", "70-80%"], "pct_of_market"].sum()
    disc = float(t8[t8["dimension"] == "All"]["leaver_cost_discount_pct"].iloc[0])
    reins = t25.set_index("group")

    return {
        "benchmark rise, age 40": f"{bench_rise:.1f}%",
        "cliff, age 40": f"${t2.loc[40, 'cliff_median']:,.0f}",
        "cliff, age 60": f"${t2.loc[60, 'cliff_median']:,.0f}",
        "cliff, age 64": f"${t2.loc[64, 'cliff_median']:,.0f}",
        "non-group relativity": f"{t4.loc['nongroup', 'relativity']:.3f}",
        "non-group p": f"p = {t4.loc['nongroup', 'p']:.3f}",
        "age span 60-64": f"{t5.loc['60-64', 'cost_relativity']:.2f}",
        "published HC.gov change":
            f"{abs(t9b.loc['HealthCare.gov', 'published_change_pct']):.1f}%",
        "same-state HC.gov change":
            f"{abs(t9b.loc['HealthCare.gov', 'same_states_change_pct']):.1f}%",
        "same-state SBE change":
            f"{abs(t9b.loc['State-based exchanges', 'same_states_change_pct']):.1f}%",
        "400-500% change": f"{abs(t14.loc['400-500%', 'change_pct']):.1f}%",
        "above 500% change": f"{abs(t14.loc['Above 500%', 'change_pct']):.1f}%",
        "300-400% change": f"{t14.loc['300-400%', 'change_pct']:.1f}%",
        "exposed change":
            f"{abs(t14.loc['Lost the credit (above 400%)', 'change_pct']):.1f}%",
        "subsidised change":
            f"{abs(t14.loc['Kept a credit (100-400%)', 'change_pct']):.1f}%",
        "exposed placebo":
            f"{t14.loc['Lost the credit (above 400%)', 'change_2024_25_pct']:.1f}%",
        "primary response, tilt 1.5": f"{prim.loc[1.5, 'calibrated_response']:.4f}",
        "one-response model above 400":
            f"{abs(prim.loc[1.5, 'model_change_above_400_pct']):.1f}%",
        "one-response model below 400":
            f"{abs(prim.loc[1.5, 'model_change_below_400_pct']):.1f}%",
        "morbidity, primary tilt 1.5": f"{prim.loc[1.5, 'morbidity_rise_pct']:.1f}%",
        "two-response above, tilt 1.5":
            f"{two.loc[1.5, 'calibrated_response_above_400']:.3f}",
        "two-response below, tilt 1.5": f"{two.loc[1.5, 'calibrated_response']:.4f}",
        "two-response ratio, tilt 1.5":
            f"{two.loc[1.5, 'response_ratio_above_to_below']:.0f}",
        "leaver discount": f"{disc:.0f}%",
        "bunching excess": f"{b16['excess']:,.0f}",
        "bunching share": f"{b16['excess_as_pct_of_400_500_loss']:.0f}%",
        "placebo excess": f"{b16['placebo_excess']:,.0f}",
        "adjusted bunching share":
            f"{b16['adjusted_as_pct_of_400_500_loss']:.0f}%",
        "cross-state slope": f"{exp_fit['slope']:.3f}",
        "cross-state t": f"{exp_fit['t']:.2f}",
        "placebo slope": f"{plc_fit['slope']:.3f}",
        "placebo p": f"{plc_fit['p']:.2f}",
        "DiD exposed x post": f"{did.loc['exposed_post', 'coef']:.1f}",
        "DiD exposed SE": f"{did.loc['exposed_post', 'se']:.1f}",
        "DiD notch x post": f"{did.loc['notch_post', 'coef']:.1f}",
        "dose coefficient": f"{dose.loc['exposed_post_burden', 'coef']:.2f}",
        "dose SE": f"{dose.loc['exposed_post_burden', 'se']:.2f}",
        "county exposed x post": f"{cty.loc['exposed_post', 'coef']:.1f}",
        "reinsurance premium gap":
            f"{abs(reins.loc['Difference (HC1 SE)', 'mean_state_median_growth_pct']):.1f}",
        "MLR 2024": f"{100 * t18.loc[2024, 'regulatory_mlr']:.1f}%",
        "life-years 2024": f"{t18.loc[2024, 'life_years'] / 1e6:.2f} million",
        "share below floor": f"{below_floor:.1f}%",
        "rebate at 4% trend, selected-premium path":
            f"${t20[(t20['claims_trend_pct'] == 4) & t20['premium_path'].str.startswith('Average')]['rebate_per_enrollee_year'].iloc[0]:,.0f}",
        "rebate at 4% trend, benchmark path":
            f"${t20[(t20['claims_trend_pct'] == 4) & t20['premium_path'].str.startswith('Bench')]['rebate_per_enrollee_year'].iloc[0]:,.0f}",
        "break-even trend, selected-premium path":
            f"{t20[t20['premium_path'].str.startswith('Average')]['breakeven_trend_pct'].iloc[0]:.1f}%",
        "restoration cost, HC.gov":
            f"${s22.loc[(hc, 'full'), 'annual_cost'] / 1e9:.1f} billion",
        "restoration cost, all":
            f"${s22.loc[(al, 'full'), 'annual_cost'] / 1e9:.1f} billion",
        "cost per person-year, HC.gov":
            f"${s22.loc[(hc, 'full'), 'cost_per_person_year']:,.0f}",
        "cost per person-year net of bunching, HC.gov":
            f"${s22.loc[(hc, 'full'), 'cost_per_person_year_net_of_bunching']:,.0f}",
        "cost per person-year, all":
            f"${s22.loc[(al, 'full'), 'cost_per_person_year']:,.0f}",
        "cheapest band": f"${hc21.loc['400-500%', 'cost_per_person_year_gained']:,.0f}",
        "dearest band": f"${hc21.loc['200-250%', 'cost_per_person_year_gained']:,.0f}",
        "cap-extension cost, all":
            f"${s22.loc[(al, 'cliff_only'), 'annual_cost'] / 1e9:.1f} billion",
        "cap-extension cost per person-year, all":
            f"${s22.loc[(al, 'cliff_only'), 'cost_per_person_year']:,.0f}",
        "CBO implied": f"${s22['cbo_implied_cost_per_insured'].iloc[0]:,.0f}",
    }


def cross_reference():
    tb = config.ROOT / "manuscript" / "tables.md"
    if not tb.exists():
        print("  tables.md not built yet; skipping the cross-reference check")
        return []
    rendered = set(re.findall(r"\*\*Table ([0-9A-Za-z]+)\.\*\*", tb.read_text()))
    cited = set()
    for m in re.finditer(r"Tables? ([0-9]+[a-f]?|A[0-9]+b?)"
                         r"(?:(?:,|\s+and)\s+([0-9]+[a-f]?|A[0-9]+b?))?"
                         r"(?:(?:,|\s+and)\s+([0-9]+[a-f]?|A[0-9]+b?))?",
                         MS.read_text()):
        for g in m.groups():
            if g:
                cited.add(g)
    problems = [f"Table {t} is cited in the prose but not rendered"
                for t in sorted(cited - rendered)]
    problems += [f"Table {t} is rendered but never cited"
                 for t in sorted(rendered - cited)]
    print(f"  {len(rendered)} tables rendered, {len(cited)} cited"
          + ("" if not problems else f"  <-- {len(problems)} mismatch(es)"))
    for p_ in problems:
        print(f"      {p_}")
    return problems


def figures():
    missing = [p for p in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", MS.read_text())
               if not (config.ROOT / p).exists()]
    for p in missing:
        print(f"      figure not found: {p}")
    return missing


def style():
    text = MS.read_text()
    problems = []
    if "—" in text:
        problems.append(f"{text.count(chr(0x2014))} em dash(es) in the manuscript")
    if re.search(r"\s–\s", text):
        problems.append("spaced en dash used as punctuation")
    for p_ in problems:
        print(f"      {p_}")
    return problems


def main():
    text = MS.read_text().replace("−", "-").replace("**", "")
    checks = load()
    bad = [(k, v) for k, v in checks.items() if v.replace("−", "-") not in text]
    width = max(len(k) for k in checks)
    for k, v in checks.items():
        print(f"  {'ok ' if (k, v) not in bad else 'MISSING'}  {k:<{width}}  {v}")
    xref, figs, sty = cross_reference(), figures(), style()
    if bad or xref or figs or sty:
        if bad:
            print(f"\n{len(bad)} headline figure(s) do not appear in "
                  f"{MS.name}. Update the prose, then rebuild.")
        sys.exit(1)
    print(f"\nAll {len(checks)} headline figures match the current tables.")


if __name__ == "__main__":
    main()
