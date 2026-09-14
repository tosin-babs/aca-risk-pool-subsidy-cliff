"""
Render the manuscript's tables from the analysis CSVs.

Manuscript numbering follows reading order and is not the CSV numbering; the
mapping is stated in each block. Nine tables in the text, the rest in the
appendix. Writes manuscript/tables.md.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config

OUT = config.ROOT / "manuscript" / "tables.md"
T = config.TABLES


def auto(d=2):
    def f(x):
        if pd.isna(x):
            return ""
        if isinstance(x, (int, float, np.integer, np.floating)):
            return "n/a" if np.isinf(x) else f"{x:,.{d}f}"
        return str(x)
    return f


def dollars(d=0):
    return lambda x: "" if pd.isna(x) else f"${x:,.{d}f}"


def pct(d=1, signed=False):
    fmt = f"{{:+,.{d}f}}%" if signed else f"{{:,.{d}f}}%"
    return lambda x: "" if pd.isna(x) else "n/a" if np.isinf(x) else fmt.format(x)


def share(d=1):
    return lambda x: "" if pd.isna(x) else f"{100 * x:.{d}f}%"


def pval(x):
    return "" if pd.isna(x) else "< 0.001" if x < 0.001 else f"{x:.3f}"


def render(df, cols, fmts, headers=None):
    out = pd.DataFrame({c: df[c].map(f) if f else df[c].astype(str)
                        for c, f in zip(cols, fmts)})
    out.columns = headers or cols
    align = ["---" if i == 0 else "---:" for i in range(len(out.columns))]
    lines = ["| " + " | ".join(out.columns) + " |",
             "|" + "|".join(align) + "|"]
    for _, r in out.iterrows():
        lines.append("| " + " | ".join(str(v) for v in r) + " |")
    return "\n".join(lines)


def caption(n, title, note=None):
    s = f"\n**Table {n}.** {title}\n"
    if note:
        s += f"\n*{note}*\n"
    return s


def main():
    parts = ["# Tables\n",
             "*Generated from `output/tables/*.csv` by `python/make_tables.py`. "
             "Premiums are for a single adult at the median HealthCare.gov "
             "rating area unless stated. Enrollment is open enrollment plan "
             "selections from the CMS OEP State-Level Public Use Files, not "
             "effectuated enrollment. HealthCare.gov means the 30 states on "
             "that platform for 2026, in every year.*\n"]

    # ---- Table 1 <- table1_net_premiums ------------------------------------
    t = pd.read_csv(T / "table1_net_premiums.csv")
    parts += [caption(1, "Net benchmark premium by income, single adult aged "
                         "40, 2025 and 2026.",
                      "Gross is the median second-lowest-cost silver premium "
                      "across the 349 rating areas with a benchmark in both "
                      "years. Net is gross less the premium tax credit under "
                      "that year's applicable-percentage schedule; income is "
                      "at each year's own poverty guideline. A percentage "
                      "change from a zero base is shown as n/a."),
              render(t, ["fpl_pct", "income_2026", "gross_2025", "gross_2026",
                         "net_2025", "net_2026", "net_change_dollars",
                         "net_change_pct", "net_pct_income_2025",
                         "net_pct_income_2026"],
                     [lambda x: f"{int(x)}%", dollars(), dollars(), dollars(),
                      dollars(), dollars(), dollars(), pct(0, True), pct(1),
                      pct(1)],
                     ["FPL", "Income 2026", "Gross 2025", "Gross 2026",
                      "Net 2025", "Net 2026", "Change $", "Change %",
                      "Net % income 2025", "Net % income 2026"])]

    # ---- Table 2 <- table2_cliff_by_age ------------------------------------
    t = pd.read_csv(T / "table2_cliff_by_age.csv")
    parts += [caption(2, "The cliff by age: credit lost by crossing from 400% "
                         "to 401% of poverty, 2026.",
                      "The cliff is the difference in annual net premium "
                      "either side of the threshold, computed rating area by "
                      "rating area with each state's own poverty guideline; "
                      "the median, 90th percentile and maximum are across "
                      "rating areas."),
              render(t, ["age", "gross_median", "cliff_median", "cliff_p90",
                         "cliff_max", "cliff_pct_income_median",
                         "gross_pct_income_median"],
                     [auto(0), dollars(), dollars(), dollars(), dollars(),
                      pct(1), pct(1)],
                     ["Age", "Gross premium", "Cliff, median", "Cliff, p90",
                      "Cliff, max", "Cliff % income", "Gross % income"])]

    # ---- Table 3 <- table9b, table14 ----------------------------------------
    t = pd.read_csv(T / "table9b_by_platform.csv")
    parts += [caption(3, "Plan selections by platform, 2025 to 2026, as "
                         "published and on a constant set of states.",
                      "Illinois moved from HealthCare.gov to a state-based "
                      "exchange for 2026; the published platform totals "
                      "therefore compare different states in the two years. "
                      "The same-states columns assign every state its 2026 "
                      "platform in both years."),
              render(t, ["platform", "published_2025", "published_2026",
                         "published_change_pct", "same_states_n",
                         "same_states_2025", "same_states_2026",
                         "same_states_change_pct"],
                     [None, auto(0), auto(0), pct(1, True), auto(0), auto(0),
                      auto(0), pct(1, True)],
                     ["Platform", "Published 2025", "Published 2026",
                      "Change", "States", "Same states 2025",
                      "Same states 2026", "Change"])]
    t = pd.read_csv(T / "table14_segment_observed.csv")
    parts += [caption("3b", "Plan selections by income band, 30 HealthCare.gov "
                            "states, 2024 to 2026.",
                      "Bands below 100% FPL and with unknown income are "
                      "excluded. The 2024 to 2025 column is a placebo period "
                      "in which the enhanced schedule applied in both years."),
              render(t, ["segment", "n_2024", "n_2025", "n_2026",
                         "change_2024_25_pct", "change_pct"],
                     [None, auto(0), auto(0), auto(0), pct(1, True),
                      pct(1, True)],
                     ["Income band", "2024", "2025", "2026",
                      "Change 2024 to 2025", "Change 2025 to 2026"])]

    # ---- Table 4 <- table4_cost_model --------------------------------------
    t = pd.read_csv(T / "table4_cost_model.csv")
    t = t[t["term"] != "const"]
    t["sig"] = t["p"].lt(0.05).map({True: "*", False: ""})
    parts += [caption(4, "Tweedie model of annual expenditure, under-65 "
                         "privately insured, MEPS 2019 to 2024.",
                      "Log link, variance power 1.6, person weights divided "
                      "by the number of pooled years, standard errors "
                      "clustered on the stratum-PSU pair. Reference "
                      "categories: age 0-17, income 138-250% FPL, male, no "
                      "chronic condition, Northeast. * marks p < 0.05."),
              render(t, ["term", "relativity", "coef", "se", "z", "p", "sig"],
                     [None, auto(3), auto(3), auto(3), auto(2), auto(3), None],
                     ["Term", "Relativity", "Coefficient", "SE", "z", "p", ""])]

    # ---- Table 5 <- table10_calibration -------------------------------------
    t = pd.read_csv(T / "table10_calibration.csv")
    t = t.copy()
    t["spec_short"] = t["specification"].str.replace(
        "Primary: raked to OEP, own-age benchmark, Tweedie cost", "Primary")
    parts += [caption(5, "Calibrated price responses and what each "
                         "specification predicts for the two segments.",
                      "The response is the share of enrollees exiting per "
                      "percentage point of income by which their own annual "
                      "payment for the benchmark rose (per unit proportional "
                      "rise for the proportional metric). Each single-"
                      "response row is solved so that total retention in the "
                      "100%+ FPL bands equals the observed 94.8%. The last "
                      "three rows fit one response to each segment. Tilt is "
                      "how much more readily a lower-cost enrollee exits."),
              render(t, ["spec_short", "tilt", "calibrated_response",
                         "calibrated_response_above_400",
                         "morbidity_rise_pct", "model_change_below_400_pct",
                         "model_change_above_400_pct"],
                     [None, auto(1), auto(4), auto(4), pct(1, True),
                      pct(1, True), pct(1, True)],
                     ["Specification", "Tilt", "Response (below 400%)",
                      "Response above 400%", "Morbidity rise",
                      "Model: 100-400% FPL", "Model: above 400%"])]

    # ---- Table 6 <- table16_bunching, table23_did ---------------------------
    t = pd.read_csv(T / "table16_bunching.csv")
    parts += [caption(6, "Bunching below the threshold, 2025 to 2026, with "
                         "the 2024 to 2025 placebo.",
                      "The counterfactual moves the 300-400% band's starting "
                      "count at the control bands' rate. The placebo excess "
                      "is the same calculation for 2024 to 2025. The adjusted "
                      "excess carries the band's 2024 to 2025 gap to the "
                      "control forward before measuring the 2026 excess."),
              render(t, ["sample", "control", "control_change_pct", "excess",
                         "placebo_excess", "adjusted_excess",
                         "excess_as_pct_of_400_500_loss",
                         "adjusted_as_pct_of_400_500_loss"],
                     [None, None, pct(1, True), auto(0), auto(0), auto(0),
                      pct(0), pct(0)],
                     ["Sample", "Control bands", "Control change", "Excess",
                      "Placebo excess", "Adjusted excess",
                      "Excess / 400-500% loss", "Adjusted / loss"])]
    t = pd.read_csv(T / "table23_did.csv")
    t = t[t["model"].str.startswith(("A.", "B."))]
    parts += [caption("6b", "State by income band by period regressions of "
                             "the log change in plan selections.",
                      "Outcome: 100 times the log of the band's count in the "
                      "later year over the earlier year, for 2024 to 2025 and "
                      "2025 to 2026. State-by-period and band fixed effects; "
                      "cells weighted by the earlier count; standard errors "
                      "clustered by state. Exposed x post is the difference "
                      "in differences for the bands above 400% FPL; notch x "
                      "post is the same for the 300-400% band. Burden is the "
                      "state's unsubsidized benchmark at age 60 as a share of "
                      "income at 401% FPL, centred, so the dose terms are per "
                      "percentage point."),
              render(t, ["model", "sample", "term", "coef", "se", "t", "p"],
                     [None, None, None, auto(2), auto(2), auto(2), pval],
                     ["Model", "Sample", "Term", "Coefficient", "SE", "t",
                      "p"])]

    # ---- Table 7 <- table17b_cross_state_fit --------------------------------
    t = pd.read_csv(T / "table17b_cross_state_fit.csv")
    parts += [caption(7, "Across the 30 HealthCare.gov states: enrollment "
                         "change on the burden of unsubsidized cover, with "
                         "the placebo period.",
                      "Regressor: the state's median unsubsidized benchmark "
                      "at age 60 as a share of income at 401% FPL. Weighted "
                      "rows use the segment's count at the start of the "
                      "period. HC1 standard errors. Per-state values are in "
                      "Table A4."),
              render(t, ["outcome", "period", "weighted", "slope", "se", "t",
                         "p", "n"],
                     [None, None, lambda x: "yes" if x else "no", auto(3),
                      auto(3), auto(2), pval, auto(0)],
                     ["Outcome", "Period", "Weighted", "Slope", "SE", "t",
                      "p", "States"])]

    # ---- Table 8 <- table18, table20 ----------------------------------------
    t = pd.read_csv(T / "table18_loss_ratios.csv")
    parts += [caption(8, "Individual-market loss ratios, 2021 to 2024.",
                      "CMS Medical Loss Ratio public use files, "
                      "comprehensive individual-market columns, "
                      "deduplicated to the latest submission per issuer and "
                      "state, territories excluded. The simple ratio is "
                      "incurred claims over earned premium; the regulatory "
                      "ratio is the statutory numerator over the statutory "
                      "denominator."),
              render(t, ["year", "issuer_state_pairs", "life_years",
                         "premium_pmpm", "claims_pmpm", "simple_loss_ratio",
                         "regulatory_mlr", "rebate_liability"],
                     [auto(0), auto(0), lambda x: f"{x / 1e6:,.2f}m",
                      dollars(), dollars(), share(), share(),
                      lambda x: f"${x / 1e6:,.0f}m"],
                     ["Year", "Issuer-states", "Life-years", "Premium PMPM",
                      "Claims PMPM", "Simple LR", "Regulatory MLR",
                      "Rebates"])]
    t = pd.read_csv(T / "table20_floor_bound.csv")
    parts += [caption("8b", "What the 80% floor would return in 2026 across "
                             "claims trends.",
                      "Projected MLR is the 2024 regulatory ratio times two "
                      "years of claims trend, over the 2024 to 2026 premium "
                      "factor. The first path uses the average premium of "
                      "plans selected; the second replaces the 2025 to 2026 "
                      "step with the median benchmark increase. The "
                      "break-even trend is the annual claims trend at which "
                      "the projected ratio is exactly 80%. An illustration "
                      "of the bound, not a forecast."),
              render(t, ["premium_path", "claims_trend_pct",
                         "premium_factor_2024_to_2026", "projected_mlr_2026",
                         "rebate_pct_of_premium", "rebate_per_enrollee_year",
                         "breakeven_trend_pct"],
                     [None, lambda x: f"{x:.0f}%", auto(3), share(), pct(1),
                      dollars(), pct(1)],
                     ["Premium path", "Claims trend", "Premium factor",
                      "Projected MLR", "Rebate % premium",
                      "Rebate per enrollee-year", "Break-even trend"])]

    # ---- Table 9 <- table21, table22 ----------------------------------------
    t = pd.read_csv(T / "table21_policy_cost.csv")
    t = t[t["sample"].str.startswith("Health") & (t["scenario"] == "full")]
    parts += [caption(9, "Restoring the enhanced schedule for 2026: cost and "
                         "coverage by income band, 30 HealthCare.gov states.",
                      "Single-person schedule at the median benchmark for "
                      "each age band and the 2025 age mix. Coverage gained "
                      "is the gap between the band's 2025 count moved at the "
                      "100-150% band's rate and its 2026 count; that band is "
                      "the control and has no effect estimated for it. Net "
                      "of bunching removes the Table 6 excess from the "
                      "bands above 400% pro rata. Cost is the extra credit "
                      "paid to everyone the band would then contain."),
              render(t, ["segment", "extra_credit_per_person",
                         "coverage_gained", "coverage_gained_net_of_bunching",
                         "annual_cost", "cost_per_person_year_gained",
                         "marginal_share_pct"],
                     [None, dollars(),
                      lambda x: "control" if pd.isna(x) else f"{x:,.0f}",
                      lambda x: "control" if pd.isna(x) else f"{x:,.0f}",
                      lambda x: f"${x / 1e9:,.2f}b",
                      lambda x: "" if pd.isna(x) else f"${x:,.0f}", pct(1)],
                     ["Band", "Extra credit", "Coverage gained",
                      "Net of bunching", "Annual cost",
                      "Cost per person-year", "Marginal share"])]
    t = pd.read_csv(T / "table22_allocation.csv")
    parts += [caption("9b", "Four schedules priced on 2026 premiums: outlay "
                             "and cost per person-year of coverage.",
                      "For schedules other than full restoration, a band "
                      "recovers the share of its full-restoration coverage "
                      "gain equal to the share of the full payment reduction "
                      "the schedule delivers. The CBO column is the CRS-"
                      "reported estimate for permanent extension, $350 "
                      "billion over 2026 to 2035 and 3.8 million more insured "
                      "in 2035, expressed per person-year at the end of the "
                      "window."),
              render(t, ["sample", "scenario_label", "annual_cost",
                         "coverage_gained", "coverage_gained_net_of_bunching",
                         "cost_per_person_year",
                         "cost_per_person_year_net_of_bunching",
                         "share_cost_above_400_pct",
                         "share_coverage_above_400_pct",
                         "cbo_implied_cost_per_insured"],
                     [None, None, lambda x: f"${x / 1e9:,.1f}b", auto(0),
                      auto(0), dollars(), dollars(), pct(0), pct(0),
                      dollars()],
                     ["Sample", "Schedule", "Annual cost", "Coverage gained",
                      "Net of bunching", "Cost per person-year",
                      "Net of bunching", "Cost above 400%",
                      "Coverage above 400%", "CBO implied"])]

    # ---- Appendix ------------------------------------------------------------
    parts += ["\n\n# Appendix tables\n"]

    t = pd.read_csv(T / "table12_unsubsidised_exposure.csv")
    parts += [caption("A1", "The unsubsidized premium as a share of income, "
                            "2026.",
                      "Share of rating areas in which the full benchmark "
                      "premium exceeds each share of income, with each "
                      "state's own poverty guideline."),
              render(t, ["fpl_pct", "age", "income", "gross_median",
                         "burden_median_pct", "pct_areas_above_10",
                         "pct_areas_above_20", "pct_areas_above_30"],
                     [lambda x: f"{int(x)}%", auto(0), dollars(), dollars(),
                      pct(1), pct(0), pct(0), pct(0)],
                     ["FPL", "Age", "Income", "Premium", "% income",
                      "Areas > 10%", "Areas > 20%", "Areas > 30%"])]

    t = pd.read_csv(T / "table13_segment_dynamics.csv")
    parts += [caption("A2", "Repricing dynamics by segment and age at the "
                            "segment-specific calibrated responses and "
                            "multiples of them.",
                      "Exit responds to the increment in the household's "
                      "payment, in points of income, since the previous "
                      "repricing, with the bounded form 1 - exp(-response x "
                      "rise / tilt). Leavers cost 22% less than stayers, "
                      "from Table A5, so the premium factor after a "
                      "cumulative exit share x is 1 / (1 - 0.22 x). No cell "
                      "reaches the spiral threshold of 3."),
              render(t, ["response_multiple", "segment", "age", "net_2025",
                         "net_2026_initial", "first_round_exit_pct",
                         "cumulative_exit_pct", "premium_factor", "rounds"],
                     [auto(0), None, auto(0), dollars(), dollars(), pct(1),
                      pct(1), auto(3), auto(0)],
                     ["Response multiple", "Segment", "Age", "Paid 2025",
                      "Paid 2026", "First-round exit", "Cumulative exit",
                      "Premium factor", "Rounds"])]

    t = pd.read_csv(T / "table3_cliff_by_state.csv")
    parts += [caption("A3", "The cliff by HealthCare.gov state, age 60.",
                      "Median across the state's rating areas."),
              render(t, ["StateCode", "n_rating_areas", "gross_median",
                         "cliff_median", "cliff_pct_income",
                         "gross_pct_income"],
                     [None, auto(0), dollars(), dollars(), pct(1), pct(1)],
                     ["State", "Rating areas", "Gross premium", "Cliff",
                      "Cliff % income", "Gross % income"])]

    t = pd.read_csv(T / "table17_cliff_vs_loss.csv")
    parts += [caption("A4", "Per-state inputs to Table 7."),
              render(t, ["StateCode", "gross_pct_income", "reinsurance_1332",
                         "exposed_25", "exposed_change_placebo_pct",
                         "exposed_change_pct", "subsidised_change_pct",
                         "enrolment_change_pct"],
                     [None, pct(1), lambda x: "yes" if x else "", auto(0),
                      pct(1, True), pct(1, True), pct(1, True), pct(1, True)],
                     ["State", "Burden at 401% FPL", "1332 reinsurance",
                      "Above 400%, 2025", "Above 400%, 2024 to 2025",
                      "Above 400%, 2025 to 2026", "100-400%, 2025 to 2026",
                      "All, 2025 to 2026"])]

    t = pd.read_csv(T / "table8_who_leaves.csv")
    parts += [caption("A5", "Who leaves in the selection model at the "
                            "primary calibrated response, tilt 1.5."),
              render(t, ["dimension", "group", "share_of_pool_pct",
                         "mean_net_2025", "mean_net_2026", "exit_rate_pct",
                         "mean_cost_of_leavers", "mean_cost_of_stayers"],
                     [None, None, pct(1), dollars(), dollars(), pct(1),
                      dollars(), dollars()],
                     ["Dimension", "Group", "Share of pool", "Net 2025",
                      "Net 2026", "Exit rate", "Cost of leavers",
                      "Cost of stayers"])]

    t = pd.read_csv(T / "table7_selection.csv")
    parts += [caption("A6", "The selection model over a grid of responses "
                            "and tilts.",
                      "Response is the exit share per percentage point of "
                      "income. Retention and morbidity are after repricing "
                      "converges."),
              render(t, ["response", "tilt", "retention_pct",
                         "morbidity_rise_pct", "retention_above_400_pct",
                         "retention_below_400_pct", "rounds"],
                     [auto(3), auto(1), pct(1), pct(1, True), pct(1), pct(1),
                      auto(0)],
                     ["Response", "Tilt", "Retained", "Morbidity",
                      "Retained above 400%", "Retained 100-400%", "Rounds"])]

    t = pd.read_csv(T / "table15_segment_elasticity.csv")
    parts += [caption("A7", "Observed change per percentage point of income "
                            "by which the band's payment rose.",
                      "The shock is the age-weighted rise in the household's "
                      "own annual payment, in points of income, at the band "
                      "midpoint (three points for the open top band) with "
                      "each age band priced at its own benchmark."),
              render(t, ["segment", "fpl_points", "mean_payment_rise",
                         "shock_pp_of_income", "observed_change_pct",
                         "placebo_change_pct", "pct_lost_per_pp_income"],
                     [None, None, dollars(), lambda x: f"{x:+.1f} pp",
                      pct(1, True), pct(1, True), auto(2)],
                     ["Band", "FPL points", "Payment rise", "Shock",
                      "Change 2025 to 2026", "Change 2024 to 2025",
                      "Change per pp"])]

    t = pd.read_csv(T / "table23_did.csv")
    t = t[t["model"].str.startswith(("C.", "D."))]
    parts += [caption("A8", "Section 1332 reinsurance interactions in the "
                            "state by band by period regressions.",
                      "Specification as in Table 6b. Reinsurance states are "
                      "those operating a Section 1332 state-based "
                      "reinsurance program in 2025 and 2026 per CMS."),
              render(t, ["model", "sample", "term", "coef", "se", "t", "p"],
                     [None, None, None, auto(2), auto(2), auto(2), pval],
                     ["Model", "Sample", "Term", "Coefficient", "SE", "t", "p"])]
    t = pd.read_csv(T / "table25_reinsurance_premiums.csv")
    parts += [caption("A8b", "Benchmark premium growth 2025 to 2026, age 40, "
                             "by reinsurance status, HealthCare.gov states."),
              render(t, ["group", "n_states", "states",
                         "mean_state_median_growth_pct",
                         "mean_burden_age60_pct"],
                     [None, auto(0), None, pct(1, True), pct(1)],
                     ["Group", "States", "Members", "Mean of state median "
                      "growth", "Mean burden at age 60"])]

    t = pd.read_csv(T / "table24_county_did.csv")
    parts += [caption("A9", "County by band by period regressions, 30 "
                            "HealthCare.gov states.",
                      "As Table 6b with county-by-period fixed effects. The "
                      "county file publishes one band above 400% FPL. The "
                      "premium interaction uses the log of the county's 2025 "
                      "average premium of plans selected, centred."),
              render(t, ["model", "term", "coef", "se", "t", "p",
                         "n_counties"],
                     [None, None, auto(2), auto(2), auto(2), pval, auto(0)],
                     ["Model", "Term", "Coefficient", "SE", "t", "p",
                      "Counties"])]

    t = pd.read_csv(T / "table19a_mlr_distribution.csv")
    parts += [caption("A10", "Issuers against the 80% floor, 2024."),
              render(t, ["mlr_band", "n_issuer_states", "life_years",
                         "pct_of_market", "rebate_liability"],
                     [None, auto(0), lambda x: f"{x / 1e6:,.2f}m", pct(1),
                      lambda x: f"${x / 1e6:,.0f}m"],
                     ["Regulatory MLR", "Issuer-states", "Life-years",
                      "Share of market", "Rebates"])]

    t = pd.read_csv(T / "table5_age_curve.csv")
    parts += [caption("A11", "Observed annual cost by age band, MEPS.",
                      "Relativity is to the 18-25 band."),
              render(t, ["age_band", "n", "mean_cost", "median_cost",
                         "pct_chronic", "pct_zero_cost", "cost_relativity"],
                     [None, auto(0), dollars(), dollars(), pct(1), pct(1),
                      lambda x: f"{x:.2f}x"],
                     ["Age band", "n", "Mean", "Median", "Any chronic",
                      "Zero cost", "Relativity"])]

    OUT.write_text("\n".join(parts) + "\n")
    n = sum(1 for line in OUT.read_text().splitlines()
            if line.startswith("**Table"))
    print(f"wrote {OUT.relative_to(config.ROOT)} with {n} tables")


if __name__ == "__main__":
    main()
