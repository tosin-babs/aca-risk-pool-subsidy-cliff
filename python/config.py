"""
Paper 4 - The subsidy cliff and the ACA individual-market risk pool.

Central configuration. Every analytic choice lives here so that a reviewer can
read the whole basis in one file.

Time-sensitivity note. This paper is built on a policy change that is still
being legislated. The enhanced premium tax credits enacted by ARPA (2021) and
extended by the IRA (2022) expired on 31 December 2025. Senate votes on 11 December
2025 fell short of 60. On 8 January 2026 the House passed a three-year
extension by 230-196; as of the date below no Senate passage had been found,
and a bipartisan CARE Act restoring the credits for two years was reported to
be in drafting. The 2026 plan year was therefore priced
and enrolled without the enhanced credits, which is the natural experiment
this paper uses. A retroactive restoration would not undo the 2026 pricing but
would change what the 2026 enrolment counterfactual means, and the manuscript
must be re-checked against the legislative position before submission.
"""

from pathlib import Path

# ---------------------------------------------------------------- paths ----
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
CMS = RAW / "cms"
MEPS = RAW / "meps"
DERIVED = ROOT / "data" / "derived"
TABLES = ROOT / "output" / "tables"
FIGURES = ROOT / "output" / "figures"

for _p in (DERIVED, TABLES, FIGURES):
    _p.mkdir(parents=True, exist_ok=True)

SEED = 2026
LONELY_PSU = "adjust"

POLICY_STATUS_AS_OF = "2026-09-14"

# ------------------------------------------------------------ CMS files ----
# Exchange Public Use Files, downloaded from
# https://download.cms.gov/marketplace-puf/<year>/<file>.zip
RATE_PUF = {
    2025: CMS / "2025_rate-puf" / "Rate_PUF.csv",
    2026: CMS / "2026_rate-puf" / "rate-puf.csv",
}
PLAN_PUF = {
    2025: CMS / "2025_plan-attributes-puf" / "Plan_Attributes_PUF.csv",
    2026: CMS / "2026_plan-attributes-puf" / "plan-attributes-puf.csv",
}
YEARS = (2025, 2026)

# The Rate PUF stores age as a string with two special values at the ends of
# the band. Both map to the ages the federal default curve prices them at.
AGE_MIN_LABEL = "0-14"
AGE_MAX_LABEL = "64 and over"
AGE_MIN_VALUE = 14
AGE_MAX_VALUE = 64

# Rates above this are placeholders, not prices: issuers use a large sentinel
# for age/plan combinations they do not sell. Screened out before any minimum
# is taken, because a benchmark is a *second lowest* and sentinels do not
# affect that - but they do wreck a mean.
RATE_SENTINEL = 9_000.0

# A silver plan must be offered to adults to count toward the benchmark; a
# child-only plan cannot be the second-lowest-cost silver plan for an adult.
BENCHMARK_METAL = "Silver"
LOWEST_COST_METAL = ("Bronze", "Expanded Bronze")

# ------------------------------------------------- subsidy schedule ----
# Applicable percentage of household income a household is expected to
# contribute toward the benchmark plan, by income as a percentage of the
# federal poverty level.
#
# 2025 is the enhanced schedule (ARPA/IRA): zero contribution below 150% FPL
# and an 8.5% cap with no cliff at 400%.
# 2026 reverts to the original ACA schedule, indexed: a contribution floor
# above 100% FPL and a hard cliff at 400% FPL, above which no credit is paid.
#
# 2026 is Rev. Proc. 2025-25, section 3.01 (IRS, July 2025), read from the
# published PDF. An earlier version of this file carried 2.06% to 9.79%, which
# are not the 2026 figures; every 2026 net premium was understated as a
# result, by up to 0.17% of income at the top of the schedule, and the cliff
# at 401% FPL overstated. Re-read the revenue procedure for any new plan year
# rather than adjusting these by hand.
APPLICABLE_PCT_2025 = [        # (upper FPL bound, start %, end %)
    (150, 0.0, 0.0),
    (200, 0.0, 0.02),
    (250, 0.02, 0.04),
    (300, 0.04, 0.06),
    (400, 0.06, 0.085),
    (float("inf"), 0.085, 0.085),
]
APPLICABLE_PCT_2026 = [
    (133, 0.0210, 0.0210),
    (150, 0.0314, 0.0419),
    (200, 0.0419, 0.0660),
    (250, 0.0660, 0.0844),
    (300, 0.0844, 0.0996),
    (400, 0.0996, 0.0996),
    (float("inf"), None, None),   # None = no credit; the cliff
]
APPLICABLE_PCT = {2025: APPLICABLE_PCT_2025, 2026: APPLICABLE_PCT_2026}

# HHS poverty guidelines for the prior year, 48 contiguous states.
# 2025 coverage uses the 2024 guidelines; 2026 coverage uses the 2025 ones.
# Checked against ASPE's published computations, September 2026.
FPL_BASE = {2025: 15_060.0, 2026: 15_650.0}
FPL_INCREMENT = {2025: 5_380.0, 2026: 5_500.0}
# Alaska and Hawaii have their own guidelines, and both are HealthCare.gov
# states. An earlier version applied the contiguous-state figure everywhere,
# which understated income at a given % FPL there and overstated the burden of
# unsubsidised cover. 2024: Federal Register, 17 January 2024; 2025: ASPE
# detailed guidelines PDF (AK $19,550 + $6,880; HI $17,990 + $6,330).
FPL_BASE_STATE = {"AK": {2025: 18_810.0, 2026: 19_550.0},
                  "HI": {2025: 17_310.0, 2026: 17_990.0}}
FPL_INCREMENT_STATE = {"AK": {2025: 6_730.0, 2026: 6_880.0},
                       "HI": {2025: 6_190.0, 2026: 6_330.0}}

# --------------------------------------------------------- OEP files ----
# CMS Marketplace Open Enrollment Period public use files.
OEP = RAW / "oep"
OEP_STATE_FILES = {
    2024: OEP / "2024_state-level" / "2024 OEP State-Level Public Use File.csv",
    2025: OEP / "2025_state-level" / "2025 OEP State-Level Public Use File.csv",
    2026: (OEP / "2026_state-level" / "2026 OEP State-Level PUF"
           / "2026 OEP State-Level Public Use File.csv"),
}
OEP_COUNTY_FILES = {
    2024: OEP / "2024_county-level" / "2024 OEP County-Level Public Use File.csv",
    2025: OEP / "2025_county-level" / "2025 OEP County-Level Public Use File.csv",
    2026: (OEP / "2026_county-level" / "2026 OEP County-Level PUF"
           / "2026 OEP County-Level Public Use File.csv"),
}
OEP_YEARS = (2024, 2025, 2026)

# Income bands as published. FPL_100_138 is nested inside FPL_100_150 and is
# never summed with it.
OEP_BANDS = ["FPL_100_150", "FPL_150_200", "FPL_200_250", "FPL_250_300",
             "FPL_300_400", "FPL_400_500", "FPL_GT500"]
OEP_BAND_LABELS = {"FPL_LT100": "Below 100%", "FPL_100_150": "100-150%",
                   "FPL_150_200": "150-200%", "FPL_200_250": "200-250%",
                   "FPL_250_300": "250-300%", "FPL_300_400": "300-400%",
                   "FPL_400_500": "400-500%", "FPL_GT500": "Above 500%",
                   "FPL_OTHR": "Other or unknown"}
EXPOSED_BANDS = ("FPL_400_500", "FPL_GT500")        # lost the credit in 2026
BELOW_NOTCH_BAND = "FPL_300_400"
PEER_BANDS = ("FPL_100_150", "FPL_150_200", "FPL_200_250", "FPL_250_300")
# Band midpoints used to price the schedule for a band. The open top band is
# evaluated at several points and averaged, because a single midpoint for an
# unbounded band is arbitrary; these points are an assumption.
BAND_MIDPOINTS = {"FPL_100_150": (125,), "FPL_150_200": (175,),
                  "FPL_200_250": (225,), "FPL_250_300": (275,),
                  "FPL_300_400": (350,), "FPL_400_500": (450,),
                  "FPL_GT500": (550, 650, 800)}
OEP_AGE_COLS = ["Age_18_25", "Age_26_34", "Age_35_44", "Age_45_54", "Age_55_64"]
# A band's premium is the mean of the median benchmark over every single age
# in the band, not the premium at one representative age.
AGE_BAND_RANGES = {"Age_18_25": (18, 25), "Age_26_34": (26, 34),
                   "Age_35_44": (35, 44), "Age_45_54": (45, 54),
                   "Age_55_64": (55, 64)}

# Samples. The 2026 PUF notes that Connecticut (<100% and >400% FPL), and
# Minnesota and New York (>400% FPL), reported enrollees with *known* income as
# "other household income" in 2026; all three report zero or near-zero
# selections above 400% FPL in 2026 against 45,000 in 2025. The District of
# Columbia suppresses most 2026 income cells and opened a Basic Health Program
# for 133-200% FPL on 1 January 2026. Band-level comparisons exclude them.
OEP_INCOME_RECODE_STATES = ("CT", "MN", "NY", "DC")
# Platform assignment changes between files: Georgia left HealthCare.gov for
# 2025 and Illinois for 2026. Platform comparisons use the 2026 assignment for
# every year, so that the same states are compared.
PLATFORM_REFERENCE_YEAR = 2026

# Section 1332 state reinsurance waivers. States listed as operating
# section 1332 state-based reinsurance programs in the CMS CCIIO Data Brief
# (December 2022), with approval periods covering plan years 2024-2026 on the
# CMS Section 1332 State Innovation Waivers page (accessed 14 September 2026).
# Hawaii's waiver concerns SHOP, not reinsurance, and is not included.
REINSURANCE_1332_STATES = ("AK", "CO", "DE", "GA", "ME", "MD", "MN", "MT",
                           "NH", "NJ", "ND", "OR", "PA", "RI", "WI")

# ------------------------------------------------------- selection model ----
SEL_AGE_MIN, SEL_AGE_MAX = 18, 64
# Price response. "pp_income": exit share per percentage point of income by
# which the household's own annual payment for the benchmark rose; defined
# for everyone, including those who paid nothing in 2025. "proportional":
# exit share per unit proportional rise, where a rise from a zero base is
# undefined and is set to SEL_ZERO_BASE_RISE (the earlier version's rule).
SEL_RESPONSE_METRIC = "pp_income"
SEL_ZERO_BASE_RISE = 1.0
SEL_RESPONSE_GRID = {"pp_income": (0.005, 0.01, 0.02, 0.04),
                     "proportional": (0.2, 0.4, 0.6, 1.0)}
SEL_TILTS = (1.0, 1.5, 2.0)
SEL_ILLUSTRATIVE = {"pp_income": (0.02, 1.5), "proportional": (0.4, 1.5)}
# Expected cost: "tweedie" is the prediction from the Table 4 model;
# a blend weight w gives (1 - w) * prediction + w * realised cost.
SEL_COST_BASIS = "tweedie"
SEL_COST_BLEND_SENSITIVITY = (0.25, 0.5)
SEL_MAX_ROUNDS = 25
SEL_SPIRAL_THRESHOLD = 3.0
TWEEDIE_VAR_POWER = 1.6

# -------------------------------------------------------- policy costing ----
POLICY_CONTROL_BAND = "FPL_100_150"
# Scenarios, each a schedule applied to 2026 premiums and poverty levels.
#   full        the 2025 enhanced schedule
#   below_only  the enhanced schedule up to 400% FPL, no credit above
#   cliff_only  the 2026 schedule, with its 9.96% cap extended above 400%
#   capped      the enhanced schedule up to a ceiling, no credit above it
POLICY_PARTIAL_CEILING = 600
CBO_DEFICIT_2026_2035 = 350e9         # CRS R48290, permanent extension
CBO_INSURED_2035 = 3.8e6

# ------------------------------------------------------------ loss ratio ----
MLR_EXCLUDE_STATES = ("Grand Total", "AS", "GU", "MP", "PR", "VI")
MLR_CLAIMS_TRENDS = (0.04, 0.06, 0.08, 0.10, 0.12)

# FPL points at which the subsidy schedule is evaluated.
FPL_GRID = (100, 133, 150, 200, 250, 300, 350, 400, 401, 450, 500, 600)
AGE_GRID = (21, 27, 40, 50, 60, 64)

# --------------------------------------------------------------- plotting ----
FIG_DPI = 300
PALETTE = {
    "y2025": "#1B6CA8",
    "y2026": "#B03A2E",
    "gain": "#117A65",
    "ink": "#1A1A1A",
    "muted": "#7F8C8D",
    "rule": "#D5D8DC",
    "warn": "#B7950B",
}
