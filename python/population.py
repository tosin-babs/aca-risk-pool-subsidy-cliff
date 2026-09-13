"""
The individual-market population and what it costs, from MEPS.

The premium side of this paper comes from CMS filings. The risk side has to
come from a survey that observes both who buys non-group coverage and what
their care costs, and MEPS is the only public file that does both.

Three things need saying about using it for this.

MEPS undercounts the market. Its non-group weights gross to roughly 10-14
million people a year against CMS effectuated enrolment above 20 million.
Survey respondents misclassify coverage type, and the undercount is not
random. So MEPS is used for the *structure* of cost - how expected claims vary
with age, income and health - and never for the *level* or the headcount,
which are taken from CMS.

The public file has no state. Rating areas, and therefore premiums, cannot be
joined to individuals here. The cost model is estimated on national data and
applied to the premium geography separately.

Claims are total expenditure, not the insurer's share. TOTEXP is what the care
cost from all payers, which is the risk a pool carries; what the insurer pays
of it depends on the plan's actuarial value, applied downstream.

Writes data/derived/nongroup.csv.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

import config

warnings.filterwarnings("ignore")

MEPS_DIR = config.ROOT.parent / "paper3" / "data" / "raw" / "meps"
FILES = {2019: "h216.dta", 2020: "h224.dta", 2021: "h233.dta",
         2022: "h243.dta", 2023: "h251.dta", 2024: "h256.dta"}
MONTHS = ["JA", "FE", "MA", "AP", "MY", "JU", "JL", "AU", "SE", "OC", "NO", "DE"]

CHRONIC = ["HIBPDX", "CHDDX", "STRKDX", "EMPHDX", "CHOLDX", "CANCERDX",
           "DIABDX_M18", "ARTHDX", "ASTHDX"]

# CPI-U, all items, USA (World Bank FP.CPI.TOTL), to 2024 dollars.
CPI_TO_2024 = {2019: 1.22699, 2020: 1.21204, 2021: 1.15765,
               2022: 1.07187, 2023: 1.02950, 2024: 1.00000}


def load_year(year):
    yy = str(year)[-2:]
    path = MEPS_DIR / FILES[year]
    it = pd.read_stata(path, iterator=True)
    available = set(it.variable_labels())

    want = ([f"PNG{m}{yy}" for m in MONTHS]
            + [f"PRING{yy}", f"PRSTX{yy}", f"PERWT{yy}F", f"TOTEXP{yy}",
               f"TOTSLF{yy}", f"AGE{yy}X", f"POVLEV{yy}", f"POVCAT{yy}",
               f"INSCOV{yy}", f"REGION{yy}", "SEX", "RACETHX", "VARSTR",
               "VARPSU", "DUPERSID", "PANEL"]
            + CHRONIC)
    use = [c for c in want if c in available]
    d = pd.read_stata(path, columns=use, convert_categoricals=False)

    ng_cols = [c for c in use if c.startswith("PNG")]
    d["ng_months"] = (d[ng_cols] == 1).sum(axis=1) if ng_cols else 0
    d["any_nongroup"] = (d["ng_months"] > 0).astype(int)
    d["full_year_nongroup"] = (d["ng_months"] == 12).astype(int)
    d["exchange"] = ((d[f"PRSTX{yy}"] == 1).astype(int)
                     if f"PRSTX{yy}" in d else 0)

    have_chronic = [c for c in CHRONIC if c in d.columns]
    d["chronic_count"] = (d[have_chronic] == 1).sum(axis=1) if have_chronic else 0
    d["any_chronic"] = (d["chronic_count"] > 0).astype(int)

    ren = {f"PERWT{yy}F": "weight", f"TOTEXP{yy}": "total_exp",
           f"TOTSLF{yy}": "oop", f"AGE{yy}X": "age", f"POVLEV{yy}": "povlev",
           f"POVCAT{yy}": "povcat", f"INSCOV{yy}": "inscov",
           f"REGION{yy}": "region"}
    d = d.rename(columns={k: v for k, v in ren.items() if k in d.columns})
    d["year"] = year

    defl = CPI_TO_2024[year]
    for c in ("total_exp", "oop"):
        if c in d.columns:
            d[c] = d[c] * defl
    return d


def main():
    print("Loading MEPS and identifying the non-group population ...")
    frames = []
    for year in FILES:
        d = load_year(year)
        ng = int(d["any_nongroup"].sum())
        print(f"  {year}: {len(d):>7,} persons, {ng:>5,} with any non-group month")
        frames.append(d)
    allp = pd.concat(frames, ignore_index=True)

    n_years = allp["year"].nunique()
    allp["weight"] = allp["weight"] / n_years
    # Cluster on the stratum-PSU pair: MEPS numbers PSUs within strata, so the
    # label alone is not a cluster. Same trap as Paper 3's regressions.
    allp["cluster"] = (allp["VARSTR"].astype(str) + "_"
                       + allp["VARPSU"].astype(str))

    ng = allp[(allp["any_nongroup"] == 1) & (allp["weight"] > 0)].copy()
    ng = ng[ng["age"].between(0, 64)]        # Medicare age is a different market

    # The marketplace population the paper prices is the under-65 non-group
    # market. An FPL band matters more than a continuous value because the
    # subsidy schedule is a step function in it.
    ng["fpl_band"] = pd.cut(ng["povlev"],
                            [-np.inf, 100, 138, 150, 200, 250, 300, 400,
                             np.inf],
                            labels=["<100", "100-138", "138-150", "150-200",
                                    "200-250", "250-300", "300-400", "400+"])
    ng["age_band"] = pd.cut(ng["age"], [-1, 17, 25, 34, 44, 54, 59, 64],
                            labels=["0-17", "18-25", "26-34", "35-44",
                                    "45-54", "55-59", "60-64"])

    out = config.DERIVED / "nongroup.csv"
    ng.to_csv(out, index=False)

    w = ng["weight"]
    print(f"\n  pooled non-group, under 65: {len(ng):,} persons, "
          f"{w.sum() / 1e6:,.1f} million a year")
    print(f"  full-year non-group:        {int(ng['full_year_nongroup'].sum()):,}")
    print(f"  reporting exchange coverage:{int(ng['exchange'].sum()):,}")

    print("\n=== Expected annual cost, all payers, 2024 dollars ===")
    for col, label in (("age_band", "Age"), ("fpl_band", "Income (% FPL)")):
        print(f"\n  {label}")
        g = ng.groupby(col, observed=True).apply(
            lambda s: pd.Series({
                "n": len(s),
                "weighted_m": s["weight"].sum() / 1e6,
                "mean_exp": np.average(s["total_exp"], weights=s["weight"]),
                "median_exp": s["total_exp"].median(),
                "pct_chronic": 100 * np.average(s["any_chronic"],
                                                weights=s["weight"]),
            }))
        for k, r in g.iterrows():
            print(f"    {str(k):<10} n={int(r['n']):>5,}  "
                  f"{r['weighted_m']:>5.2f}m  mean ${r['mean_exp']:>8,.0f}  "
                  f"median ${r['median_exp']:>7,.0f}  "
                  f"chronic {r['pct_chronic']:>4.1f}%")

    overall = np.average(ng["total_exp"], weights=ng["weight"])
    print(f"\n  overall mean expenditure: ${overall:,.0f}")
    print(f"  ratio, oldest band to youngest adult band: "
          f"{np.average(ng[ng.age_band == '60-64']['total_exp'], weights=ng[ng.age_band == '60-64']['weight']) / np.average(ng[ng.age_band == '18-25']['total_exp'], weights=ng[ng.age_band == '18-25']['weight']):.1f}x")
    print(f"\nwrote {out.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
