"""
Loading the CMS Open Enrollment Period public use files, once and consistently.

Four traps in these files are handled here and nowhere else:

  * Each state-level file carries three national total rows (HealthCare.gov,
    state-based exchanges, all) and the 2026 file adds footnote rows with no
    state. Only two-letter state rows are used; totals are summed from them.
  * FPL_100_138 is a subgroup of FPL_100_150 and is never added to it.
  * States change platform: Georgia left HealthCare.gov for 2025 and Illinois
    for 2026. A platform total from each year's own file therefore compares
    different states. Platform groups here use one reference year's
    assignment for every year.
  * In 2026 Connecticut, Minnesota and New York reported known incomes above
    400% FPL as "other", and the District of Columbia suppressed most income
    cells. Band-level work excludes those four (config.OEP_INCOME_RECODE_STATES).

Suppressed cells ("*") are read as missing, not zero.
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd

import config


def _num(s):
    return pd.to_numeric(s.astype(str).str.replace(r"[,$%\s]", "", regex=True),
                         errors="coerce")


@lru_cache(maxsize=None)
def state_file(year):
    """State rows of one year's state-level file, numeric, indexed by state."""
    d = pd.read_csv(config.OEP_STATE_FILES[year], dtype=str, low_memory=False)
    d = d[d["State_Abrvtn"].astype(str).str.strip().str.fullmatch(r"[A-Z]{2}")]
    d["State_Abrvtn"] = d["State_Abrvtn"].str.strip()
    d["Pltfrm"] = d["Pltfrm"].str.strip().replace({"SBM": "SBE"})
    for c in d.columns:
        if c not in ("State_Abrvtn", "Pltfrm"):
            d[c] = _num(d[c])
    d = d.loc[:, ~d.columns.str.startswith("Unnamed")]
    return d.set_index("State_Abrvtn")


@lru_cache(maxsize=None)
def county_file(year):
    d = pd.read_csv(config.OEP_COUNTY_FILES[year], dtype=str, low_memory=False)
    d = d[d["State_Abrvtn"].astype(str).str.strip().str.fullmatch(r"[A-Z]{2}")]
    d["State_Abrvtn"] = d["State_Abrvtn"].str.strip()
    for c in d.columns:
        if c != "State_Abrvtn":
            d[c] = _num(d[c])
    d["County_FIPS_Cd"] = d["County_FIPS_Cd"].astype("Int64")
    return d


def platform_states(platform, reference_year=None):
    """States on a platform ("HC.gov" or "SBE") in the reference year."""
    ref = reference_year or config.PLATFORM_REFERENCE_YEAR
    s = state_file(ref)
    return tuple(sorted(s.index[s["Pltfrm"] == platform]))


def hcgov_states():
    """The HealthCare.gov states whose premiums are in the 2026 Rate PUF."""
    return platform_states("HC.gov")


def band_sample_states(sample="hcgov"):
    """States usable for income-band comparisons.

    hcgov  the HealthCare.gov states of the reference year (the primary sample:
           the premium data describe exactly these states)
    all    every state and DC except those whose 2026 income reporting changed
    """
    every = tuple(sorted(state_file(config.PLATFORM_REFERENCE_YEAR).index))
    if sample == "hcgov":
        keep = hcgov_states()
    elif sample == "all":
        keep = every
    elif sample == "sbe":
        keep = platform_states("SBE")
    else:
        raise ValueError(sample)
    return tuple(s for s in keep if s not in config.OEP_INCOME_RECODE_STATES)


def total(year, states, cols):
    """Sum of columns over a set of states for one year."""
    d = state_file(year)
    return d.loc[list(states), cols].sum(min_count=1)


def published_total(year, platform="All"):
    """The published total row, for reconciliation only."""
    d = pd.read_csv(config.OEP_STATE_FILES[year], dtype=str, low_memory=False)
    d["State_Abrvtn"] = d["State_Abrvtn"].astype(str).str.strip()
    plat = d["Pltfrm"].astype(str).str.strip().replace({"SBM": "SBE"})
    row = d[d["State_Abrvtn"].eq("Total") & plat.eq(platform)]
    return row.iloc[0].drop(["State_Abrvtn", "Pltfrm"]).pipe(_num)


def band_panel(states=None, years=config.OEP_YEARS):
    """Long panel: state x year x income band count."""
    cols = config.OEP_BANDS + ["FPL_LT100", "FPL_OTHR", "Cnsmr"]
    rows = []
    for y in years:
        d = state_file(y)
        s = d if states is None else d.loc[[x for x in states if x in d.index]]
        long = (s[cols].reset_index()
                .melt(id_vars="State_Abrvtn", var_name="band", value_name="n"))
        long["year"] = y
        rows.append(long)
    return pd.concat(rows, ignore_index=True)


def age_weights(year, states):
    """Adult age mix of plan selections, as shares over the five adult bands."""
    t = total(year, states, config.OEP_AGE_COLS)
    return (t / t.sum()).to_dict()
