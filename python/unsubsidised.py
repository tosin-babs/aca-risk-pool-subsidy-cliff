"""
RQ3: the segment that pays the full premium, against the segment that does not.

A subsidised enrollee's payment for the benchmark is capped at a share of
income, so a rise in the gross premium is absorbed by the credit. Above 400% of
poverty in 2026 there is no credit, and every dollar of a rate increase is
paid by the enrollee.

Writes:
  Table 12   the unsubsidised premium as a share of income, by age and FPL
  Table 13   repricing dynamics by segment and age
  Table 14   selections by band, HealthCare.gov states, 2024-25 and 2025-26
  Table 15   observed change per percentage point of income, by band
  Table 17   cross-state inputs; 17b the regressions, with a placebo period

Enrollment is from the 30 HealthCare.gov states of 2026 (oep.py explains the
sample), the states the premium data describe.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm

import config
import oep
from benchmarks import band_gross, load_benchmarks, median_gross_by_age
from subsidy import applicable_pct, income_at, net_payment

warnings.filterwarnings("ignore")

BURDEN_MARKS = (0.10, 0.20, 0.30)
UNSUB_FPL = (401, 450, 500, 600)
SEGMENTS = (("Subsidised, 250% FPL", 250),
            ("Subsidised, 390% FPL", 390),
            ("Unsubsidised, 450% FPL", 450))


def exposure_table(bench):
    rows = []
    b26 = bench[bench["year"] == 2026]
    for fpl in UNSUB_FPL:
        for age in config.AGE_GRID:
            s = b26[b26["age"] == age]
            gross = s["slcsp"].to_numpy(float) * 12.0
            income = s["StateCode"].map(
                lambda st: income_at(fpl, 2026, state=st)).to_numpy(float)
            share = gross / income
            row = {"fpl_pct": fpl, "age": age,
                   "income": income_at(fpl, 2026),
                   "n_rating_areas": len(s),
                   "gross_median": float(np.median(gross)),
                   "burden_median_pct": 100 * float(np.median(share))}
            for mark in BURDEN_MARKS:
                row[f"pct_areas_above_{int(100 * mark)}"] = \
                    100 * float((share > mark).mean())
            rows.append(row)
    return pd.DataFrame(rows)


def one_net(gross, fpl, year):
    return float(net_payment(np.array([gross]), fpl, year)[0])


def spiral(gross25, gross26, fpl, response, discount, tilt=1.5, rounds=40):
    """Repricing loop for one representative household type.

    Exit responds to the increment in payment (points of income) since the
    previous round, with the bounded form 1 - exp(-response * rise / tilt),
    which is linear in the response for small rises and never exceeds one.
    If leavers cost (1 - discount) times what stayers cost, the stayers' mean
    over the original mean after a cumulative exit share x is 1 / (1 - d x),
    which is bounded by 1 / (1 - d). An earlier version used 1 + d x / (1 - x),
    which is unbounded and produced spurious divergence at high exit.
    """
    inc = income_at(fpl, 2026)
    net25 = one_net(gross25, fpl, 2025)
    share_prev = net25 / income_at(fpl, 2025)
    factor, cum_exit, hist = 1.0, 0.0, []
    for _ in range(rounds):
        net = one_net(gross26 * factor, fpl, 2026)
        rise_pp = max(100 * (net / inc - share_prev), 0.0)
        exit_now = 1.0 - float(np.exp(-response * rise_pp / tilt))
        cum_exit = 1 - (1 - cum_exit) * (1 - exit_now)
        new = 1.0 / (1.0 - discount * cum_exit)
        hist.append((new, cum_exit, net))
        share_prev = net / inc
        done = abs(new - factor) < 1e-6
        factor = new
        if done or factor > config.SEL_SPIRAL_THRESHOLD:
            break
    new, cum_exit, net = hist[-1]
    return {"net_2025": net25, "net_2026_initial": one_net(gross26, fpl, 2026),
            "net_final": net, "premium_factor": new,
            "first_round_exit_pct": 100 * hist[0][1],
            "cumulative_exit_pct": 100 * cum_exit, "rounds": len(hist),
            "diverged": bool(new > config.SEL_SPIRAL_THRESHOLD)}


def ols(x, y, w=None):
    """Slope with HC1 standard errors; weighted if w is given."""
    ok = np.isfinite(x) & np.isfinite(y)
    X = sm.add_constant(np.asarray(x, float)[ok])
    yy = np.asarray(y, float)[ok]
    m = (sm.WLS(yy, X, weights=np.asarray(w, float)[ok]) if w is not None
         else sm.OLS(yy, X)).fit(cov_type="HC1")
    return {"slope": float(m.params[1]), "intercept": float(m.params[0]),
            "se": float(m.bse[1]), "t": float(m.tvalues[1]),
            "p": float(m.pvalues[1]), "n": int(ok.sum())}


def main():
    states = oep.hcgov_states()
    bench = load_benchmarks(states=states)

    # ---- Table 12 -----------------------------------------------------------
    t12 = exposure_table(bench)
    t12.to_csv(config.TABLES / "table12_unsubsidised_exposure.csv", index=False)
    print("=== Unsubsidised premium as a share of income, 2026 ===")
    print(t12[t12["age"].isin([27, 40, 60, 64])].round(1).to_string(index=False))

    # ---- Table 13 -----------------------------------------------------------
    t10 = pd.read_csv(config.TABLES / "table10_calibration.csv")
    t8 = pd.read_csv(config.TABLES / "table8_who_leaves.csv")
    two = t10[t10["specification"].str.startswith("Two") & (t10["tilt"] == 1.5)]
    resp_below = float(two["calibrated_response"].iloc[0])
    resp_above = float(two["calibrated_response_above_400"].iloc[0])
    discount = float(t8[t8["dimension"] == "All"]["leaver_cost_discount_pct"]
                     .iloc[0]) / 100
    g25, g26 = median_gross_by_age(bench, 2025), median_gross_by_age(bench, 2026)
    rows = []
    for mult in (1, 2, 4):
        for age in config.AGE_GRID:
            for seg, fpl in SEGMENTS:
                base_resp = resp_above if fpl > 400 else resp_below
                r = spiral(g25[age], g26[age], fpl, base_resp * mult, discount)
                rows.append({"response_multiple": mult,
                             "response": base_resp * mult, "segment": seg,
                             "fpl_pct": fpl, "age": age,
                             "shock_dollars": r["net_2026_initial"] - r["net_2025"],
                             "shock_pct": 100 * (r["net_2026_initial"]
                                                 / r["net_2025"] - 1), **r})
    t13 = pd.DataFrame(rows)
    t13.to_csv(config.TABLES / "table13_segment_dynamics.csv", index=False)
    print(f"\n=== Segment dynamics (responses {resp_below:.4f} below and "
          f"{resp_above:.4f} above 400% FPL, leaver discount {discount:.2f}) ===")
    print(t13[t13["response_multiple"] == 1][["segment", "age", "net_2025",
          "net_2026_initial", "first_round_exit_pct", "cumulative_exit_pct",
          "premium_factor", "rounds", "diverged"]].round(2).to_string(index=False))
    print(f"  any cell diverges at 4x: {bool(t13['diverged'].any())}")

    # ---- Table 14 -----------------------------------------------------------
    n = {y: oep.total(y, states, config.OEP_BANDS) for y in config.OEP_YEARS}
    rows = []
    for col in config.OEP_BANDS:
        rows.append({"band": col, "segment": config.OEP_BAND_LABELS[col],
                     "subsidised_in_2026": col not in config.EXPOSED_BANDS,
                     "n_2024": n[2024][col], "n_2025": n[2025][col],
                     "n_2026": n[2026][col],
                     "change_2024_25_pct": 100 * (n[2025][col] / n[2024][col] - 1),
                     "change_pct": 100 * (n[2026][col] / n[2025][col] - 1)})
    t14 = pd.DataFrame(rows)
    bands_only = t14.copy()
    for lab, flag in (("Kept a credit (100-400%)", True),
                      ("Lost the credit (above 400%)", False)):
        s = bands_only[bands_only["subsidised_in_2026"] == flag]
        t14 = pd.concat([t14, pd.DataFrame([{
            "band": "group", "segment": lab,
            "subsidised_in_2026": flag,
            "n_2024": s["n_2024"].sum(), "n_2025": s["n_2025"].sum(),
            "n_2026": s["n_2026"].sum(),
            "change_2024_25_pct": 100 * (s["n_2025"].sum() / s["n_2024"].sum() - 1),
            "change_pct": 100 * (s["n_2026"].sum() / s["n_2025"].sum() - 1)}])],
            ignore_index=True)
    t14.to_csv(config.TABLES / "table14_segment_observed.csv", index=False)
    print("\n=== Selections by band, 30 HealthCare.gov states ===")
    print(t14.round(1).to_string(index=False))

    # ---- Table 15: change per point of income ------------------------------
    aw = oep.age_weights(2025, states)
    gb25, gb26 = band_gross(bench, 2025), band_gross(bench, 2026)
    rows = []
    for _, r in t14[t14["band"] != "group"].iterrows():
        pts = config.BAND_MIDPOINTS[r["band"]]
        rise_pp, rise_usd = [], []
        for f in pts:
            d = [aw[c] * (one_net(gb26[c], f, 2026) / income_at(f, 2026)
                          - one_net(gb25[c], f, 2025) / income_at(f, 2025))
                 for c in config.OEP_AGE_COLS]
            rise_pp.append(100 * sum(d))
            rise_usd.append(sum(aw[c] * (one_net(gb26[c], f, 2026)
                                         - one_net(gb25[c], f, 2025))
                                for c in config.OEP_AGE_COLS))
        shock = float(np.mean(rise_pp))
        rows.append({"band": r["band"], "segment": r["segment"],
                     "subsidised_in_2026": r["subsidised_in_2026"],
                     "fpl_points": "/".join(str(p) for p in pts),
                     "mean_payment_rise": float(np.mean(rise_usd)),
                     "shock_pp_of_income": shock,
                     "observed_change_pct": r["change_pct"],
                     "placebo_change_pct": r["change_2024_25_pct"],
                     "pct_lost_per_pp_income":
                         r["change_pct"] / shock if shock > 0 else np.nan})
    t15 = pd.DataFrame(rows)
    t15.to_csv(config.TABLES / "table15_segment_elasticity.csv", index=False)
    print("\n=== Change per point of income ===")
    print(t15.round(2).to_string(index=False))

    # ---- Table 17: across states, with a placebo period --------------------
    cliff = pd.read_csv(config.TABLES / "table3_cliff_by_state.csv")
    cliff = cliff[cliff["StateCode"].isin(states)]
    ex, sub = list(config.EXPOSED_BANDS), [c for c in config.OEP_BANDS
                                           if c not in config.EXPOSED_BANDS]
    rows = []
    for st in states:
        v = {y: oep.state_file(y).loc[st] for y in config.OEP_YEARS}
        e = {y: v[y][ex].sum() for y in v}
        s = {y: v[y][sub].sum() for y in v}
        rows.append({"StateCode": st,
                     "exposed_24": e[2024], "exposed_25": e[2025],
                     "exposed_26": e[2026],
                     "exposed_change_pct": 100 * (e[2026] / e[2025] - 1),
                     "exposed_change_placebo_pct": 100 * (e[2025] / e[2024] - 1),
                     "subsidised_change_pct": 100 * (s[2026] / s[2025] - 1),
                     "subsidised_change_placebo_pct": 100 * (s[2025] / s[2024] - 1),
                     "enrolment_change_pct":
                         100 * (v[2026]["Cnsmr"] / v[2025]["Cnsmr"] - 1),
                     "enrolment_change_placebo_pct":
                         100 * (v[2025]["Cnsmr"] / v[2024]["Cnsmr"] - 1),
                     "reinsurance_1332": st in config.REINSURANCE_1332_STATES})
    j = cliff.merge(pd.DataFrame(rows), on="StateCode")
    j["gap_change_pp"] = j["exposed_change_pct"] - j["subsidised_change_pct"]
    j["gap_change_placebo_pp"] = (j["exposed_change_placebo_pct"]
                                  - j["subsidised_change_placebo_pct"])
    x = j["gross_pct_income"].to_numpy(float)
    fits = [
        ("Whole-state enrollment change", "2025-26", False,
         ols(x, j["enrolment_change_pct"])),
        ("Change above 400% FPL", "2025-26", True,
         ols(x, j["exposed_change_pct"], j["exposed_25"])),
        ("Change above 400% FPL", "2024-25 (placebo)", True,
         ols(x, j["exposed_change_placebo_pct"], j["exposed_24"])),
        ("Above-400% change less 100-400% change", "2025-26", True,
         ols(x, j["gap_change_pp"], j["exposed_25"])),
        ("Above-400% change less 100-400% change", "2024-25 (placebo)", True,
         ols(x, j["gap_change_placebo_pp"], j["exposed_24"])),
        ("Change above 400% FPL, unweighted", "2025-26", False,
         ols(x, j["exposed_change_pct"])),
    ]
    t17b = pd.DataFrame([{"outcome": o, "period": p, "weighted": w, **f}
                         for o, p, w, f in fits])
    t17b.to_csv(config.TABLES / "table17b_cross_state_fit.csv", index=False)
    j["fitted_exposed"] = fits[1][3]["intercept"] + fits[1][3]["slope"] * x
    j["fitted_exposed_placebo"] = fits[2][3]["intercept"] + fits[2][3]["slope"] * x
    j.to_csv(config.TABLES / "table17_cliff_vs_loss.csv", index=False)
    print("\n=== Cross-state regressions (HC1 standard errors) ===")
    print(t17b.round(3).to_string(index=False))
    print("\nwrote tables 12 to 17")


if __name__ == "__main__":
    main()
