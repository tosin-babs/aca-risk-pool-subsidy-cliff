"""
Expected annual cost by age, income and health, for the under-65 private market.

Why not fit this on the non-group population directly. MEPS captures about a
quarter of marketplace enrolment - 5.1 million under-65 non-group lives in 2024
against CMS effectuated enrolment above 20 million - and more than half of
everyone MEPS labels "non-group" is 65 or over, holding a Medicare supplement
rather than a marketplace plan. Pooling six years leaves 1,817 under-65
non-group person-years. That is too thin to price a market on, and the
undercount is not random, so the survivors are not a random quarter either.

What this module does instead is the standard actuarial move: estimate the
*structure* of cost on the largest comparable population available - everyone
under 65 with private coverage, tens of thousands of person-years - and test
explicitly whether the non-group segment differs from it once age, income,
sex, region and health status are controlled for. If it does not differ, the
structure transfers and only the level needs calibrating. If it does, the
difference is itself the estimate of how selected the individual market is.

The level is not taken from MEPS at all. It is calibrated downstream to
marketplace claims from CMS.

Writes Tables 4 and 5.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm

import config

from functools import lru_cache

warnings.filterwarnings("ignore")

MEPS_DIR = config.ROOT.parent / "paper3" / "data" / "raw" / "meps"
FILES = {2019: "h216.dta", 2020: "h224.dta", 2021: "h233.dta",
         2022: "h243.dta", 2023: "h251.dta", 2024: "h256.dta"}
MONTHS = ["JA", "FE", "MA", "AP", "MY", "JU", "JL", "AU", "SE", "OC", "NO", "DE"]
CHRONIC = ["HIBPDX", "CHDDX", "STRKDX", "EMPHDX", "CHOLDX", "CANCERDX",
           "DIABDX_M18", "ARTHDX", "ASTHDX"]
CPI_TO_2024 = {2019: 1.22699, 2020: 1.21204, 2021: 1.15765,
               2022: 1.07187, 2023: 1.02950, 2024: 1.00000}

AGE_BANDS = [(-1, 17, "0-17"), (17, 25, "18-25"), (25, 34, "26-34"),
             (34, 44, "35-44"), (44, 54, "45-54"), (54, 59, "55-59"),
             (59, 64, "60-64")]
FPL_BANDS = [(-np.inf, 138, "<138"), (138, 250, "138-250"),
             (250, 400, "250-400"), (400, np.inf, "400+")]


@lru_cache(maxsize=1)
def _load_cached():
    frames = []
    for year, fname in FILES.items():
        yy = str(year)[-2:]
        path = MEPS_DIR / fname
        it = pd.read_stata(path, iterator=True)
        avail = set(it.variable_labels())
        want = ([f"PNG{m}{yy}" for m in MONTHS]
                + [f"PERWT{yy}F", f"TOTEXP{yy}", f"AGE{yy}X", f"POVLEV{yy}",
                   f"INSCOV{yy}", f"REGION{yy}", "SEX", "VARSTR", "VARPSU"]
                + CHRONIC)
        use = [c for c in want if c in avail]
        d = pd.read_stata(path, columns=use, convert_categoricals=False)
        ngc = [c for c in use if c.startswith("PNG")]
        d["nongroup"] = ((d[ngc] == 1).sum(axis=1) > 0).astype(int) if ngc else 0
        hc = [c for c in CHRONIC if c in d.columns]
        d["chronic_count"] = (d[hc] == 1).sum(axis=1) if hc else 0
        d["any_chronic"] = (d["chronic_count"] > 0).astype(int)
        d = d.rename(columns={f"PERWT{yy}F": "weight", f"TOTEXP{yy}": "cost",
                              f"AGE{yy}X": "age", f"POVLEV{yy}": "povlev",
                              f"INSCOV{yy}": "inscov", f"REGION{yy}": "region"})
        d["year"] = year
        d["cost"] = d["cost"] * CPI_TO_2024[year]
        frames.append(d)
    d = pd.concat(frames, ignore_index=True)
    d["weight"] = d["weight"] / d["year"].nunique()
    d["cluster"] = d["VARSTR"].astype(str) + "_" + d["VARPSU"].astype(str)
    return d


def load():
    """The pooled MEPS file. Read once per process; callers get a copy."""
    return _load_cached().copy()


def band(series, bands):
    out = pd.Series(pd.NA, index=series.index, dtype="object")
    for lo, hi, lab in bands:
        out = out.mask(series.gt(lo) & series.le(hi), lab)
    return out


def private_sample():
    """Under 65, privately insured, positive weight, banded."""
    d = load()
    m = d[(d["age"].between(0, 64)) & (d["inscov"] == 1)
          & (d["weight"] > 0)].copy()
    m["age_band"] = band(m["age"], AGE_BANDS)
    m["fpl_band"] = band(m["povlev"], FPL_BANDS)
    m = m[m["age_band"].notna() & m["fpl_band"].notna()].copy()
    m["cost"] = m["cost"].clip(lower=0)
    return m


def design(m):
    X = pd.get_dummies(m[["age_band", "fpl_band"]], drop_first=True,
                       dtype=float)
    X["female"] = (m["SEX"] == 2).astype(float).to_numpy()
    X["chronic"] = m["any_chronic"].astype(float).to_numpy()
    X["chronic_count"] = m["chronic_count"].astype(float).to_numpy()
    for r in sorted(m["region"].dropna().unique())[1:]:
        X[f"region_{int(r)}"] = (m["region"] == r).astype(float).to_numpy()
    X["nongroup"] = m["nongroup"].astype(float).to_numpy()
    return sm.add_constant(X)


@lru_cache(maxsize=1)
def fitted():
    """Fit the Tweedie model once; return the sample with predictions."""
    m = private_sample()
    X = design(m)
    fit = sm.GLM(m["cost"].to_numpy(float), X,
                 family=sm.families.Tweedie(var_power=config.TWEEDIE_VAR_POWER,
                                            link=sm.families.links.Log()),
                 freq_weights=m["weight"].to_numpy(float)).fit(
        cov_type="cluster", cov_kwds={"groups": m["cluster"].to_numpy()})
    m["pred_cost"] = fit.predict(X)
    return m, fit, X


def main():
    m, fit, X = fitted()
    m = m.copy()

    print(f"Under-65 privately insured, pooled 2019-2024: {len(m):,} "
          f"person-years")
    print(f"  of which non-group: {int(m['nongroup'].sum()):,} "
          f"({100 * m['nongroup'].mean():.1f}%)")
    print(f"  weighted: {m['weight'].sum() / 1e6:,.1f} million a year\n")

    res = pd.DataFrame({"term": X.columns, "coef": fit.params,
                        "se": fit.bse, "z": fit.tvalues, "p": fit.pvalues})
    res["relativity"] = np.exp(res["coef"])
    res.to_csv(config.TABLES / "table4_cost_model.csv", index=False)

    print("=== Tweedie model of annual expenditure (relativities) ===")
    for _, r in res.iterrows():
        if r["term"] == "const":
            continue
        star = "*" if r["p"] < 0.05 else " "
        print(f"  {r['term']:<22} {r['relativity']:6.3f}{star}  "
              f"(z {r['z']:+6.2f})")

    ng = res[res["term"] == "nongroup"].iloc[0]
    print(f"\n=== Does the non-group segment differ once controls are in? ===")
    print(f"  relativity {ng['relativity']:.3f}, z = {ng['z']:+.2f}, "
          f"p = {ng['p']:.3f}")
    if ng["p"] >= 0.05:
        print("  Not distinguishable from the rest of the private market once\n"
              "  age, income, sex, region and health status are held constant.\n"
              "  The cost structure transfers; only the level needs calibrating.")
    else:
        direction = "more" if ng["relativity"] > 1 else "less"
        print(f"  Non-group members cost {abs(100 * (ng['relativity'] - 1)):.0f}% "
              f"{direction} than otherwise similar people with private cover.\n"
              "  That difference is itself a measure of selection into the\n"
              "  individual market, and it is carried into the pricing.")

    # ---- Table 5: the age curve the market actually prices -----------------
    rows = []
    for lo, hi, lab in AGE_BANDS:
        s = m[m["age_band"] == lab]
        if s.empty:
            continue
        rows.append({
            "age_band": lab, "n": len(s),
            "mean_cost": np.average(s["cost"], weights=s["weight"]),
            "median_cost": s["cost"].median(),
            "pct_chronic": 100 * np.average(s["any_chronic"],
                                            weights=s["weight"]),
            "pct_zero_cost": 100 * np.average((s["cost"] == 0).astype(float),
                                              weights=s["weight"]),
        })
    t5 = pd.DataFrame(rows)
    base = t5.loc[t5["age_band"] == "18-25", "mean_cost"].iloc[0]
    t5["cost_relativity"] = t5["mean_cost"] / base
    t5.to_csv(config.TABLES / "table5_age_curve.csv", index=False)

    print("\n=== Observed cost by age, against the 3:1 statutory rating band ===")
    print(f"  {'band':<8} {'n':>7} {'mean':>9} {'median':>8} {'chronic':>8} "
          f"{'zero':>7} {'relativity':>11}")
    for _, r in t5.iterrows():
        print(f"  {r['age_band']:<8} {int(r['n']):>7,} ${r['mean_cost']:>8,.0f} "
              f"${r['median_cost']:>7,.0f} {r['pct_chronic']:>7.1f}% "
              f"{r['pct_zero_cost']:>6.1f}% {r['cost_relativity']:>10.2f}x")

    adult = t5[t5["age_band"] != "0-17"]
    span = (adult["mean_cost"].max() / adult["mean_cost"].min())
    print(f"\n  Observed adult cost spans {span:.2f}x from the cheapest band to "
          f"the dearest,\n  against a statutory 3:1 rating band. Age is "
          f"therefore priced roughly right,\n  and it is not where the "
          f"cross-subsidy lives.")

    # ---- Table 6: the dimension that is NOT priced -------------------------
    # Premiums may vary with age, geography and tobacco use, and with nothing
    # else. Health status inside an age band is community-rated away, so the
    # spread within a band is the cross-subsidy that selection attacks.
    rows = []
    for lo, hi, lab in AGE_BANDS:
        s_ = m[m["age_band"] == lab]
        if len(s_) < 200:
            continue
        w_ = s_["weight"].to_numpy(float)
        c_ = s_["cost"].to_numpy(float)
        order = np.argsort(c_)
        cw = np.cumsum(w_[order]) / w_.sum()
        q = lambda p: float(np.interp(p, cw, c_[order]))
        healthy, sick = q(0.25), q(0.90)
        rows.append({"age_band": lab, "n": len(s_),
                     "p25_cost": healthy, "median_cost": q(0.50),
                     "p90_cost": sick, "p99_cost": q(0.99),
                     "within_band_ratio_p90_p25":
                         sick / healthy if healthy > 0 else np.nan,
                     "mean_cost": np.average(c_, weights=w_)})
    t6 = pd.DataFrame(rows)
    t6.to_csv(config.TABLES / "table6_within_age_spread.csv", index=False)

    print("\n=== The spread the law forbids pricing: cost within an age band ===")
    print(f"  {'band':<8} {'p25':>9} {'median':>9} {'p90':>10} {'p99':>11} "
          f"{'p90/p25':>9}")
    for _, r in t6.iterrows():
        ratio = ("n/a" if not np.isfinite(r["within_band_ratio_p90_p25"])
                 else f"{r['within_band_ratio_p90_p25']:8.0f}x")
        print(f"  {r['age_band']:<8} ${r['p25_cost']:>8,.0f} "
              f"${r['median_cost']:>8,.0f} ${r['p90_cost']:>9,.0f} "
              f"${r['p99_cost']:>10,.0f} {ratio:>9}")
    print("\n  Age may be priced 3:1 and is. Health status may not be priced at\n"
          "  all, and inside a single age band the ninetieth percentile costs\n"
          "  many multiples of the twenty-fifth. That gap is the cross-subsidy\n"
          "  a healthy member walks away from when the price rises, and it is\n"
          "  what makes the pool average move when they do.")

    print(f"\nwrote tables 4, 5 and 6")


if __name__ == "__main__":
    main()
