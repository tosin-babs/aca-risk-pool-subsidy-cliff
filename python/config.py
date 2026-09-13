"""
Paper 4 - The subsidy cliff and the ACA individual-market risk pool.

Central configuration. Every analytic choice lives here so that a reviewer can
read the whole basis in one file.

Time-sensitivity note. This paper is built on a policy change that is still
being legislated. The enhanced premium tax credits enacted by ARPA (2021) and
extended by the IRA (2022) expired on 31 December 2025. On 8 January 2026 the
House passed a three-year extension by 230-196; as of the date below the
Senate had not acted, and a bipartisan CARE Act restoring the credits for two
years was reported to be in drafting. The 2026 plan year was therefore priced
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

POLICY_STATUS_AS_OF = "2026-09-13"

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
# [VERIFY] the 2026 figures against the IRS revenue procedure before writing
# up; they are the indexed original-law percentages and the indexation is
# published annually.
APPLICABLE_PCT_2025 = [        # (upper FPL bound, start %, end %)
    (150, 0.0, 0.0),
    (200, 0.0, 0.02),
    (250, 0.02, 0.04),
    (300, 0.04, 0.06),
    (400, 0.06, 0.085),
    (float("inf"), 0.085, 0.085),
]
APPLICABLE_PCT_2026 = [
    (133, 0.0206, 0.0206),
    (150, 0.0309, 0.0412),
    (200, 0.0412, 0.0651),
    (250, 0.0651, 0.0830),
    (300, 0.0830, 0.0979),
    (400, 0.0979, 0.0979),
    (float("inf"), None, None),   # None = no credit; the cliff
]
APPLICABLE_PCT = {2025: APPLICABLE_PCT_2025, 2026: APPLICABLE_PCT_2026}

# HHS poverty guidelines for the prior year, 48 contiguous states.
# 2025 coverage uses the 2024 guidelines; 2026 coverage uses the 2025 ones.
# [VERIFY] against aspe.hhs.gov before write-up.
FPL_BASE = {2025: 15_060.0, 2026: 15_650.0}
FPL_INCREMENT = {2025: 5_380.0, 2026: 5_500.0}

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
