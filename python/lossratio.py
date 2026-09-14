"""
RQ4: what the medical loss ratio floor does, and does not, bound.

Section 2718 of the Public Health Service Act requires an individual-market
issuer to spend at least 80% of premium on claims and quality improvement, and
to rebate the shortfall. That is usually described as consumer protection, and
it is, but for this paper it is something more specific: it is a bound on one
of the two channels through which a premium spiral does damage.

  the insurer-profit channel   if rates are raised beyond what claims justify,
                               the loss ratio falls, the floor binds, and the
                               excess comes back. This channel is bounded at
                               20% of premium by statute.

  the coverage channel         the household that could not pay the higher
                               premium is not in the pool to receive the
                               rebate. Nothing bounds this, and Table 14 put
                               it at a 34.7% fall above the cliff.

So the floor caps the transfer and not the loss, and the two are frequently
confused. This module measures the first so the paper can be precise about the
second.

There is a sharper implication. A rebate is triggered by a *low* loss ratio.
The morbidity rise that adverse selection produces raises claims, which raises
the loss ratio, which extinguishes the rebate. A market that is unravelling
therefore looks compliant in exactly the statistic designed to police it, and
the MLR data will be the last place the spiral shows up rather than the first.

Data: the CMS Medical Loss Ratio public use files, reporting years 2021-2024.
Each file reports the reporting year in its `cy` columns and the two prior
years in `py1` and `py2`, because the rebate is computed on a three-year
average.

One trap, and it doubles every total in the file. The submission header
carries resubmissions as separate rows - 2,194 rows for 1,711 issuer-state
pairs in 2024 - so summing it raw reports 44.98 million individual-market
life-years against a true 22.53 million. Every load here deduplicates to the
latest submission per issuer and state, and the loader asserts the result
against known enrolment.

Writes Tables 18, 19 and 20.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

import config
import oep

warnings.filterwarnings("ignore")

MLR = config.RAW / "cms"
YEARS = (2021, 2022, 2023, 2024)
IND = "cmm_individual"

# Reporting-year life-years in the individual market, for the assertion in
# load_year. These are of the order of CMS effectuated enrolment averaged over
# the year; the check is deliberately loose because it is catching a factor of
# two, not calibrating anything.
PLAUSIBLE_LIFE_YEARS = (8e6, 30e6)


def _read(path):
    """CMS switched the column headers to upper case for the 2021 and 2022
    releases and back to lower for 2023 and 2024. Normalise on the way in."""
    d = pd.read_csv(path, low_memory=False)
    d.columns = [c.strip().lower() for c in d.columns]
    return d


def _pivot(df, codes, col):
    """One row per submission, one column per row code."""
    s = df[df["row_lookup_code"].isin(codes)]
    w = s.pivot_table(index="mr_submission_template_id",
                      columns="row_lookup_code", values=col, aggfunc="first")
    return w


def load_year(year):
    base = MLR / f"mlr-{year}"
    h = _read(base / "MR_Submission_Template_Header.csv")
    p12 = _read(base / "Part1_2_Summary_Data_Premium_Claims.csv")
    p3 = _read(base / "Part3_MLR_Rebate_Calculation.csv")

    a = _pivot(p12, ["NUMBER_OF_LIFE_YEARS", "MEMBER_MONTHS",
                     "TOTAL_DIRECT_PREMIUM_EARNED",
                     "TOTAL_INCURRED_CLAIMS_PT1"], f"{IND}_yearly")
    # The regulatory numerator is incurred claims plus quality-improvement
    # expense; the denominator is premium less taxes and licensing fees. They
    # are not claims over premium and the difference is a point or two, so
    # both are carried and reported side by side.
    b = _pivot(p3, ["MLR_NUMERATOR", "MLR_DENOMINATOR",
                    "REBATE_LIABILITY_TOTAL"], f"{IND}_cy")
    d = (h[["mr_submission_template_id", "business_state", "hios_issuer_id",
            "company_name", "group_affiliation", "created_date"]]
         .merge(a, on="mr_submission_template_id", how="left")
         .merge(b, on="mr_submission_template_id", how="left"))

    d["created_date"] = pd.to_datetime(d["created_date"], errors="coerce")
    before = len(d)
    d = (d.sort_values("created_date")
          .drop_duplicates(["hios_issuer_id", "business_state"], keep="last"))
    d["year"] = year
    # The header carries a handful of "Grand Total" rows and the territories,
    # none of which are state individual markets.
    d = d[~d["business_state"].isin(config.MLR_EXCLUDE_STATES)]

    ly = d["NUMBER_OF_LIFE_YEARS"].sum()
    lo, hi = PLAUSIBLE_LIFE_YEARS
    if not lo <= ly <= hi:
        raise ValueError(
            f"{year}: {ly:,.0f} individual-market life-years is outside the "
            f"plausible range {lo:,.0f}-{hi:,.0f}. The usual cause is failing "
            f"to drop resubmissions from the header.")
    return d, before - len(d)


def collapse(d):
    """Market aggregates for one year."""
    ly = d["NUMBER_OF_LIFE_YEARS"].sum()
    mm = d["MEMBER_MONTHS"].sum()
    prem = d["TOTAL_DIRECT_PREMIUM_EARNED"].sum()
    clm = d["TOTAL_INCURRED_CLAIMS_PT1"].sum()
    num = d["MLR_NUMERATOR"].sum()
    den = d["MLR_DENOMINATOR"].sum()
    return {
        "issuer_state_pairs": int(d["NUMBER_OF_LIFE_YEARS"].gt(0).sum()),
        "life_years": ly, "member_months": mm,
        "premium_pmpm": prem / mm, "claims_pmpm": clm / mm,
        "simple_loss_ratio": clm / prem,
        "regulatory_mlr": num / den,
        "rebate_liability": d["REBATE_LIABILITY_TOTAL"].sum(),
        "rebate_per_life_year": d["REBATE_LIABILITY_TOTAL"].sum() / ly,
    }


def main():
    frames, dropped = {}, {}
    for y in YEARS:
        frames[y], dropped[y] = load_year(y)

    # ---- Table 18: the margin the market was running on -------------------
    t18 = pd.DataFrame([{"year": y, **collapse(frames[y])} for y in YEARS])
    t18.to_csv(config.TABLES / "table18_loss_ratios.csv", index=False)

    print("=== Individual-market loss ratios, 2021-2024 ===")
    print(f"  {'year':>5} {'issuers':>8} {'life-yrs':>10} {'prem pmpm':>10} "
          f"{'claims pmpm':>12} {'simple LR':>10} {'reg MLR':>9} "
          f"{'rebates':>12}")
    for _, r in t18.iterrows():
        print(f"  {int(r['year']):>5} {int(r['issuer_state_pairs']):>8,} "
              f"{r['life_years'] / 1e6:>9.2f}m ${r['premium_pmpm']:>9,.0f} "
              f"${r['claims_pmpm']:>11,.0f} "
              f"{100 * r['simple_loss_ratio']:>9.1f}% "
              f"{100 * r['regulatory_mlr']:>8.1f}% "
              f"${r['rebate_liability'] / 1e6:>10,.0f}m")
    print(f"\n  Resubmissions dropped from the header: "
          f"{', '.join(f'{y} {dropped[y]}' for y in YEARS)}.")
    print(f"  Summing the file without dropping them roughly doubles every "
          f"total.")

    lo, hi = t18["regulatory_mlr"].min(), t18["regulatory_mlr"].max()
    last = t18[t18["year"] == 2024].iloc[0]
    print(f"\n  The regulatory MLR ran between {100 * lo:.1f}% and "
          f"{100 * hi:.1f}% over the four years and\n  stood at "
          f"{100 * last['regulatory_mlr']:.1f}% in 2024, against an 80% floor. "
          f"The market went into the 2026\n  rate increase with "
          f"{100 * (last['regulatory_mlr'] - 0.80):.1f} points of loss ratio "
          f"above the floor, which is the\n  room a rate rise has to move "
          f"before the rebate mechanism starts\n  clawing it back.")

    yrs = int(last["year"] - t18.iloc[0]["year"])
    ctrend = (last["claims_pmpm"] / t18.iloc[0]["claims_pmpm"]) ** (1 / yrs) - 1
    ptrend = (last["premium_pmpm"] / t18.iloc[0]["premium_pmpm"]) ** (1 / yrs) - 1
    growth = last["life_years"] / t18.iloc[0]["life_years"] - 1
    print(f"\n  Claims per member month rose from "
          f"${t18.iloc[0]['claims_pmpm']:,.0f} in {int(t18.iloc[0]['year'])} "
          f"to ${last['claims_pmpm']:,.0f} in 2024, an annual\n  rate of "
          f"{100 * ctrend:.1f}%, against premium at {100 * ptrend:.1f}%.")
    print(f"\n  That {100 * ctrend:.1f}% is not the medical trend and must "
          f"not be read as one. The\n  market grew {100 * growth:.0f}% over "
          f"the same four years, from "
          f"{t18.iloc[0]['life_years'] / 1e6:.1f}m to "
          f"{last['life_years'] / 1e6:.1f}m life-years,\n  and the people the "
          f"enhanced credits brought in were younger and cheaper\n  than the "
          f"people already there. Cost per member month is therefore a\n"
          f"  composition series as much as a cost series, and it is falling "
          f"relative to\n  the underlying trend for the same reason the risk "
          f"pool was improving.\n  Table 20 takes the medical trend as an "
          f"assumption rather than reading it\n  off this column.")

    # ---- Table 19: who is at the floor, and how thin the market is --------
    d24 = frames[2024]
    d24 = d24[d24["MLR_DENOMINATOR"].gt(0) & d24["NUMBER_OF_LIFE_YEARS"].gt(0)]
    d24 = d24.assign(mlr=d24["MLR_NUMERATOR"] / d24["MLR_DENOMINATOR"])

    ly = d24["NUMBER_OF_LIFE_YEARS"]
    bands = [(-np.inf, 0.70, "under 70%"), (0.70, 0.80, "70-80%"),
             (0.80, 0.90, "80-90%"), (0.90, 1.00, "90-100%"),
             (1.00, np.inf, "over 100%")]
    rows = []
    for lo_, hi_, lab in bands:
        s = d24[(d24["mlr"] > lo_) & (d24["mlr"] <= hi_)]
        rows.append({"mlr_band": lab, "n_issuer_states": len(s),
                     "life_years": s["NUMBER_OF_LIFE_YEARS"].sum(),
                     "pct_of_market": 100 * s["NUMBER_OF_LIFE_YEARS"].sum() / ly.sum(),
                     "rebate_liability": s["REBATE_LIABILITY_TOTAL"].sum()})
    t19 = pd.DataFrame(rows)

    # Concentration, because issuer exit is the other way a market unravels
    # and a state with two issuers has no room for one to leave. Herfindahl on
    # life-year share within state.
    def hhi(g):
        sh = g["NUMBER_OF_LIFE_YEARS"] / g["NUMBER_OF_LIFE_YEARS"].sum()
        return float((sh ** 2).sum())

    conc = (d24.groupby("business_state")
                .apply(lambda g: pd.Series({
                    "n_issuers": int(len(g)), "hhi": hhi(g),
                    "life_years": g["NUMBER_OF_LIFE_YEARS"].sum(),
                    "largest_share_pct":
                        100 * g["NUMBER_OF_LIFE_YEARS"].max()
                        / g["NUMBER_OF_LIFE_YEARS"].sum()}))
                .reset_index())
    t19.to_csv(config.TABLES / "table19a_mlr_distribution.csv", index=False)
    conc.to_csv(config.TABLES / "table19b_concentration.csv", index=False)

    print("\n=== Where issuers sat against the floor in 2024 ===")
    print(f"  {'band':<12} {'issuer-states':>14} {'life-years':>12} "
          f"{'% market':>10} {'rebates':>12}")
    for _, r in t19.iterrows():
        print(f"  {r['mlr_band']:<12} {int(r['n_issuer_states']):>14,} "
              f"{r['life_years'] / 1e6:>11.2f}m {r['pct_of_market']:>9.1f}% "
              f"${r['rebate_liability'] / 1e6:>10,.0f}m")

    below = t19[t19["mlr_band"].isin(["under 70%", "70-80%"])]
    print(f"\n  {below['pct_of_market'].sum():.1f}% of the market sat below "
          f"the floor and owed a rebate;\n  the rest kept everything it "
          f"charged because it spent it.")

    thin = conc[conc["n_issuers"] <= 3].sort_values("n_issuers")
    print(f"\n=== How much room is there for an issuer to leave? ===")
    print(f"  median issuers per state: {conc['n_issuers'].median():.0f}, "
          f"median HHI {conc['hhi'].median():.3f}")
    print(f"  states with three issuers or fewer: {len(thin)}")
    for _, r in thin.head(8).iterrows():
        print(f"    {r['business_state']:<4} {int(r['n_issuers'])} issuers, "
              f"largest holds {r['largest_share_pct']:>5.1f}%, "
              f"{r['life_years']:>9,.0f} life-years")
    print(f"\n  An HHI above 0.25 is a concentrated market on the merger "
          f"guidelines'\n  own arithmetic, and "
          f"{100 * (conc['hhi'] > 0.25).mean():.0f}% of states are above it. "
          f"The exit of one issuer\n  from a state with three is not a "
          f"competitive event, it is a coverage one.")

    # ---- Table 20: what the floor bounds in 2026 --------------------------
    # The 2026 rate increase is known. What is not known is the claims trend
    # it was priced against, so the loss ratio is projected across a range of
    # trends and the rebate that each implies is computed. The point of the
    # exercise is the size of the bound, not the point estimate.
    # The premium path is taken entirely from the OEP series, as two
    # successive ratios within one series. An earlier version formed the
    # 2024-25 step by dividing an OEP premium by an MLR premium per member
    # month: those are different populations - the OEP figure covers
    # marketplace selections, the MLR figure the whole individual market
    # including off-exchange - and different definitions, so their ratio is a
    # measure of nothing. Only within-series ratios are used here, and the
    # 2024 loss ratio supplies the level.
    from benchmarks import load_benchmarks
    p24 = float(oep.published_total(2024)["Avg_Prm"])
    p25 = float(oep.published_total(2025)["Avg_Prm"])
    p26 = float(oep.published_total(2026)["Avg_Prm"])
    bench = load_benchmarks(states=oep.hcgov_states())
    b40 = bench[bench["age"] == 40].pivot_table(
        index=["StateCode", "RatingAreaId"], columns="year", values="slcsp")
    bench_growth = float(np.median(b40[2026] / b40[2025]))
    base_mlr = float(last["regulatory_mlr"])
    base_prem = float(last["premium_pmpm"])
    # Two premium paths. The average premium of plans selected moved with a
    # shift from silver (56% to 43% of selections) toward bronze, so it
    # understates the rate increase; the second path takes the 2025-26 step
    # from the median benchmark instead.
    paths = {"Average premium of plans selected": p26 / p24,
             "Benchmark for 2025-26": (p25 / p24) * bench_growth}
    rows = []
    for path, prem_factor in paths.items():
        breakeven = np.sqrt(0.80 * prem_factor / base_mlr) - 1
        for t in config.MLR_CLAIMS_TRENDS:
            mlr26 = base_mlr * (1 + t) ** 2 / prem_factor
            shortfall = max(0.80 - mlr26, 0.0)
            rows.append({"premium_path": path, "claims_trend_pct": 100 * t,
                         "premium_factor_2024_to_2026": prem_factor,
                         "projected_mlr_2026": mlr26,
                         "binds_floor": bool(shortfall > 0),
                         "rebate_pct_of_premium": 100 * shortfall,
                         "rebate_per_enrollee_year":
                             shortfall * base_prem * prem_factor * 12,
                         "breakeven_trend_pct": 100 * breakeven})
    t20 = pd.DataFrame(rows)
    t20.to_csv(config.TABLES / "table20_floor_bound.csv", index=False)
    prem_factor = paths["Average premium of plans selected"]

    print(f"\n=== What the floor returns in 2026 ===")
    print(f"  average premium of plans selected: ${p24:,.0f} in 2024, "
          f"${p25:,.0f} in 2025, ${p26:,.0f} in 2026")
    print(f"  a {100 * (prem_factor - 1):.1f}% rise over the two years, "
          f"against a 2024 loss ratio of {100 * base_mlr:.1f}%\n")
    print(f"  {'claims trend':>13} {'projected MLR':>14} {'rebate':>9} "
          f"{'per enrollee-year':>18}")
    for _, r in t20.iterrows():
        print(f"  {r['claims_trend_pct']:>12.0f}% "
              f"{r['projected_mlr_2026']:>13.1%} "
              f"{r['rebate_pct_of_premium']:>8.1f}% "
              f"${r['rebate_per_enrollee_year']:>17,.0f}")

    binds = t20[t20["binds_floor"]]
    if len(binds):
        w = binds.iloc[0]
        print(f"\n  The floor binds at a claims trend of "
              f"{w['claims_trend_pct']:.0f}% or below, returning up to\n"
              f"  ${binds['rebate_per_enrollee_year'].max():,.0f} an "
              f"enrollee-year. That is the whole of the protection the\n"
              f"  MLR rule offers against a rate increase that outruns "
              f"claims.")
    else:
        print(f"\n  The floor does not bind at any trend in this range: the "
              f"rate increase\n  is small enough relative to claims that the "
              f"rebate mechanism never\n  engages.")

    o25, o26 = oep.published_total(2025), oep.published_total(2026)
    cliff_loss = 100 * (1 - float(o26["FPL_400_500"])
                        / float(o25["FPL_400_500"]))
    print(f"\n  Set that against Table 14. The rebate, where it is paid at "
          f"all, reaches\n  the enrollee eighteen months later and reaches "
          f"only enrollees - and the\n  {cliff_loss:.0f}% of the 400-500% FPL "
          f"band that left in 2026 is by definition not\n  among them. The "
          f"floor bounds what an insurer keeps. It does nothing\n  whatever "
          f"about who is covered, and the two are routinely conflated in\n"
          f"  the policy discussion this paper is addressed to.")

    print(f"\n  There is a second-order point that matters more. A rebate is "
          f"triggered\n  by a low loss ratio, and the morbidity rise in "
          f"Table 13 raises claims,\n  which raises the loss ratio, which "
          f"extinguishes the rebate. A market\n  losing its healthy members "
          f"therefore reports improving compliance with\n  the very rule "
          f"meant to detect overpricing. The MLR series is the last\n  place "
          f"a spiral becomes visible, not the first.")

    print(f"\nwrote tables 18, 19a, 19b and 20")


if __name__ == "__main__":
    main()
