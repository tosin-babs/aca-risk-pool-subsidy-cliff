"""
Placebo and difference-in-differences tests of the income-band findings.

The 2024 open enrollment file is a pre-period in which there was no cliff:
the enhanced schedule applied in both 2024 and 2025. If the bands above 400%
of poverty were already shrinking relative to the bands below, or the
300-400% band already outgrowing its neighbours, the 2026 pattern would not be
evidence of a response to the notch. This module measures both.

  Table 16   bunching below the threshold, 2025-26 against 2024-25, under
             three choices of comparison band
  Table 23   state x band x period regressions of the log change in plan
             selections, with state-by-period and band fixed effects:
             exposed x post (the difference in differences), 300-400% x post
             (bunching), a dose interaction with the state's unsubsidised
             burden, and an interaction with a Section 1332 reinsurance waiver
  Table 24   the same design on counties in the HealthCare.gov states, with
             county-by-period fixed effects (the county file publishes one band
             above 400%)
  Table 25   benchmark premium growth, 2025-26, by reinsurance waiver status

The log change is 100 * ln(N_t / N_{t-1}), so coefficients are in log points.
Cells are weighted by N_{t-1}; standard errors are clustered by state.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm

import config
import oep
from benchmarks import load_benchmarks

warnings.filterwarnings("ignore")

PERIODS = ((2024, 2025, 0), (2025, 2026, 1))


# ------------------------------------------------------------ bunching ----
def bunching(states):
    rows = []
    controls = {"100-300% pooled": list(config.PEER_BANDS),
                "250-300% only": ["FPL_250_300"],
                "200-300% pooled": ["FPL_200_250", "FPL_250_300"]}
    for label, ctrl in controls.items():
        for y0, y1, post in PERIODS:
            a = oep.total(y0, states, config.OEP_BANDS)
            b = oep.total(y1, states, config.OEP_BANDS)
            rate = b[ctrl].sum() / a[ctrl].sum() - 1
            cf = a[config.BELOW_NOTCH_BAND] * (1 + rate)
            excess = b[config.BELOW_NOTCH_BAND] - cf
            lost_450 = a["FPL_400_500"] - b["FPL_400_500"]
            ex = list(config.EXPOSED_BANDS)
            lost_all = a[ex].sum() - b[ex].sum()
            rows.append({"control": label, "period": f"{y0}-{str(y1)[2:]}",
                         "post": post, "control_change_pct": 100 * rate,
                         "n_300_400_start": a[config.BELOW_NOTCH_BAND],
                         "n_300_400_end": b[config.BELOW_NOTCH_BAND],
                         "counterfactual_300_400": cf, "excess": excess,
                         "lost_400_500": lost_450, "lost_above_400": lost_all})
    t = pd.DataFrame(rows)
    # Placebo-adjusted excess: the 2026 excess less the excess the band would
    # show if its 2024-25 gap to the control band carried forward.
    out = []
    for label, g in t.groupby("control", sort=False):
        pre, post = g[g["post"] == 0].iloc[0], g[g["post"] == 1].iloc[0]
        pre_gap = pre["n_300_400_end"] / pre["counterfactual_300_400"] - 1
        adj_cf = post["counterfactual_300_400"] * (1 + pre_gap)
        adj_excess = post["n_300_400_end"] - adj_cf
        out.append({**post.to_dict(), "pre_gap_pct": 100 * pre_gap,
                    "placebo_excess": pre["excess"],
                    "adjusted_excess": adj_excess,
                    "excess_as_pct_of_400_500_loss":
                        100 * post["excess"] / post["lost_400_500"],
                    "adjusted_as_pct_of_400_500_loss":
                        100 * adj_excess / post["lost_400_500"],
                    "excess_as_pct_of_all_loss":
                        100 * post["excess"] / post["lost_above_400"]})
    return t, pd.DataFrame(out)


# --------------------------------------------------------- regressions ----
def absorb(df, cols, group, weight):
    """Weighted within-transformation: subtract group means."""
    w = df[weight]
    out = df.copy()
    for c in cols:
        m = (df[c] * w).groupby(df[group]).transform("sum") \
            / w.groupby(df[group]).transform("sum")
        out[c] = df[c] - m
    return out


def fe_regression(df, y, x, group, weight, cluster):
    """WLS of y on x after absorbing `group` fixed effects; band dummies are
    among x. Clustered standard errors; the within transformation's lost
    degrees of freedom are not added back, which is standard for clustered
    errors when groups nest within clusters."""
    d = absorb(df, [y] + x, group, weight)
    X = d[x].to_numpy(float)
    keep = np.abs(X).sum(axis=0) > 1e-12
    xs = [c for c, k in zip(x, keep) if k]
    fit = sm.WLS(d[y].to_numpy(float), d[xs].to_numpy(float),
                 weights=d[weight].to_numpy(float)).fit(
        cov_type="cluster", cov_kwds={"groups": pd.factorize(d[cluster])[0]})
    return pd.DataFrame({"term": xs, "coef": fit.params, "se": fit.bse,
                         "t": fit.tvalues, "p": fit.pvalues}), fit


def state_panel(states, bands, burden=None):
    rows = []
    for y0, y1, post in PERIODS:
        a, b = oep.state_file(y0), oep.state_file(y1)
        for st in states:
            for band in bands:
                n0, n1 = a.at[st, band], b.at[st, band]
                if not (np.isfinite(n0) and np.isfinite(n1)) or n0 <= 0 or n1 <= 0:
                    continue
                rows.append({"state": st, "band": band, "post": post,
                             "y": 100 * np.log(n1 / n0), "w": n0})
    d = pd.DataFrame(rows)
    d["exposed"] = d["band"].isin(config.EXPOSED_BANDS).astype(float)
    d["notch"] = (d["band"] == config.BELOW_NOTCH_BAND).astype(float)
    d["exposed_post"] = d["exposed"] * d["post"]
    d["notch_post"] = d["notch"] * d["post"]
    d["reins"] = d["state"].isin(config.REINSURANCE_1332_STATES).astype(float)
    d["exposed_reins"] = d["exposed"] * d["reins"]
    d["exposed_post_reins"] = d["exposed_post"] * d["reins"]
    if burden is not None:
        bc = d["state"].map(burden)
        d["burden_c"] = bc - np.average(burden.reindex(states).dropna())
        for c in ("exposed", "exposed_post", "notch", "notch_post"):
            d[f"{c}_burden"] = d[c] * d["burden_c"]
    d["state_period"] = d["state"] + "_" + d["post"].astype(str)
    for band in bands[1:]:
        d[f"b_{band}"] = (d["band"] == band).astype(float)
    return d


def main():
    hc = oep.band_sample_states("hcgov")
    allst = oep.band_sample_states("all")

    # ---- Table 16 -----------------------------------------------------------
    long, t16 = bunching(hc)
    long_all, t16_all = bunching(allst)
    t16["sample"], t16_all["sample"] = "HealthCare.gov (30)", \
        f"All consistent-reporting states ({len(allst)})"
    t16 = pd.concat([t16, t16_all], ignore_index=True)
    t16.to_csv(config.TABLES / "table16_bunching.csv", index=False)
    print("=== Bunching below 400% FPL, with the 2024-25 placebo ===")
    print(t16[["sample", "control", "control_change_pct", "excess",
               "placebo_excess", "pre_gap_pct", "adjusted_excess",
               "excess_as_pct_of_400_500_loss",
               "adjusted_as_pct_of_400_500_loss"]].round(1).to_string(index=False))

    # ---- Table 23 -----------------------------------------------------------
    cliff = pd.read_csv(config.TABLES / "table3_cliff_by_state.csv") \
        .set_index("StateCode")["gross_pct_income"]
    bands = config.OEP_BANDS
    bdum = [f"b_{b}" for b in bands[1:]]
    results = []

    def run(label, sample, states, x, burden=None):
        d = state_panel(states, bands, burden)
        res, fit = fe_regression(d, "y", bdum + x, "state_period", "w", "state")
        res = res[~res["term"].str.startswith("b_")]
        res.insert(0, "model", label)
        res.insert(1, "sample", sample)
        res["n_cells"] = len(d)
        res["n_states"] = d["state"].nunique()
        results.append(res)
        return d

    base_x = ["exposed_post", "notch_post"]
    run("A. Difference in differences", f"All consistent ({len(allst)})",
        allst, base_x)
    run("A. Difference in differences", "HealthCare.gov (30)", hc, base_x)
    run("B. Dose: unsubsidised burden at age 60",
        "HealthCare.gov (30)", hc,
        base_x + ["exposed_burden", "exposed_post_burden",
                  "notch_burden", "notch_post_burden"], burden=cliff)
    run("C. Section 1332 reinsurance", f"All consistent ({len(allst)})",
        allst, base_x + ["exposed_reins", "exposed_post_reins"])
    run("C. Section 1332 reinsurance", "HealthCare.gov (30)", hc,
        base_x + ["exposed_reins", "exposed_post_reins"])
    run("D. Reinsurance, holding burden constant", "HealthCare.gov (30)", hc,
        base_x + ["exposed_reins", "exposed_post_reins",
                  "exposed_burden", "exposed_post_burden"], burden=cliff)
    t23 = pd.concat(results, ignore_index=True)
    t23.to_csv(config.TABLES / "table23_did.csv", index=False)
    print("\n=== State x band x period regressions ===")
    print(t23.round(3).to_string(index=False))

    # ---- Table 24: counties ---------------------------------------------------
    cb = ["FPL_100_150", "FPL_150_200", "FPL_200_250", "FPL_250_300",
          "FPL_300_400", "FPL_GT400"]
    rows = []
    for y0, y1, post in PERIODS:
        a = oep.county_file(y0).set_index(["State_Abrvtn", "County_FIPS_Cd"])
        b = oep.county_file(y1).set_index(["State_Abrvtn", "County_FIPS_Cd"])
        a = a[a.index.get_level_values(0).isin(hc)]
        common = a.index.intersection(b.index)
        prem = oep.county_file(2025).set_index(
            ["State_Abrvtn", "County_FIPS_Cd"])["Avg_Prm"]
        for band in cb:
            n0, n1 = a.loc[common, band], b.loc[common, band]
            ok = (n0 > 0) & (n1 > 0)
            rows.append(pd.DataFrame({
                "state": common[ok.to_numpy()].get_level_values(0),
                "county": common[ok.to_numpy()].get_level_values(1).astype(str),
                "band": band, "post": post,
                "y": 100 * np.log((n1[ok] / n0[ok]).to_numpy(float)),
                "w": n0[ok].to_numpy(float),
                "prem25": prem.reindex(common[ok.to_numpy()]).to_numpy(float)}))
    c = pd.concat(rows, ignore_index=True)
    c = c[np.isfinite(c["prem25"])]
    c["exposed"] = (c["band"] == "FPL_GT400").astype(float)
    c["notch"] = (c["band"] == "FPL_300_400").astype(float)
    c["exposed_post"] = c["exposed"] * c["post"]
    c["notch_post"] = c["notch"] * c["post"]
    lp = np.log(c["prem25"])
    c["lprem_c"] = lp - np.average(lp, weights=c["w"])
    c["exposed_lprem"] = c["exposed"] * c["lprem_c"]
    c["exposed_post_lprem"] = c["exposed_post"] * c["lprem_c"]
    c["county_period"] = c["county"] + "_" + c["post"].astype(str)
    cdum = []
    for band in cb[1:]:
        c[f"b_{band}"] = (c["band"] == band).astype(float)
        cdum.append(f"b_{band}")
    res = []
    for label, x in (("County difference in differences",
                      ["exposed_post", "notch_post"]),
                     ("County, by 2025 average premium",
                      ["exposed_post", "notch_post", "exposed_lprem",
                       "exposed_post_lprem"])):
        r, _ = fe_regression(c, "y", cdum + x, "county_period", "w", "state")
        r = r[~r["term"].str.startswith("b_")]
        r.insert(0, "model", label)
        r["n_cells"] = len(c)
        r["n_counties"] = c["county"].nunique()
        r["n_states"] = c["state"].nunique()
        res.append(r)
    t24 = pd.concat(res, ignore_index=True)
    t24.to_csv(config.TABLES / "table24_county_did.csv", index=False)
    print("\n=== Counties ===")
    print(t24.round(3).to_string(index=False))

    # ---- Table 25: benchmark growth by reinsurance status -------------------
    bench = load_benchmarks(states=oep.hcgov_states())
    b40 = bench[bench["age"] == 40].pivot_table(
        index=["StateCode", "RatingAreaId"], columns="year", values="slcsp")
    b40["growth_pct"] = 100 * (b40[2026] / b40[2025] - 1)
    st = b40.groupby("StateCode")["growth_pct"].median().rename("median_growth_pct")
    st = st.reset_index()
    st["reinsurance_1332"] = st["StateCode"].isin(config.REINSURANCE_1332_STATES)
    st = st.merge(cliff.rename("burden_age60_pct").reset_index(), on="StateCode")
    rows = []
    for flag, g in st.groupby("reinsurance_1332"):
        rows.append({"group": "1332 reinsurance" if flag else "No waiver",
                     "n_states": len(g), "states": " ".join(sorted(g["StateCode"])),
                     "mean_state_median_growth_pct": g["median_growth_pct"].mean(),
                     "mean_burden_age60_pct": g["burden_age60_pct"].mean()})
    m = sm.OLS(st["median_growth_pct"],
               sm.add_constant(st["reinsurance_1332"].astype(float))).fit(cov_type="HC1")
    rows.append({"group": "Difference (HC1 SE)", "n_states": len(st),
                 "states": f"se {m.bse.iloc[1]:.2f}, p {m.pvalues.iloc[1]:.3f}",
                 "mean_state_median_growth_pct": m.params.iloc[1],
                 "mean_burden_age60_pct": np.nan})
    t25 = pd.DataFrame(rows)
    t25.to_csv(config.TABLES / "table25_reinsurance_premiums.csv", index=False)
    print("\n=== Benchmark growth by reinsurance status ===")
    print(t25.round(2).to_string(index=False))
    print("\nwrote tables 16, 23, 24 and 25")


if __name__ == "__main__":
    main()
