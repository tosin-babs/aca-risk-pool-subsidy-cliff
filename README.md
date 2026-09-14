# The Subsidy Cliff and the Risk Pool: An Actuarial Analysis of Adverse Selection and Premium Stability in the ACA Individual Market after the Expiration of the Enhanced Premium Tax Credits

The enhanced premium tax credits enacted by ARPA in 2021 and extended by the IRA
in 2022 expired on 31 December 2025. The 2026 plan year was priced and enrolled
without them. This repository holds the code, tables and manuscript for a paper
on what that did to net premiums, to who stayed in the risk pool, and to whether
the unsubsidized segment of the market held.

## Policy status

Checked on 14 September 2026.

- The enhanced credits expired on 31 December 2025 and the original schedule,
  indexed by Rev. Proc. 2025-25, applied from 1 January 2026.
- On 11 December 2025 the Senate voted on competing extension proposals; neither
  reached 60 votes.
- On 8 January 2026 the House passed a three-year extension, 230 to 196.
- No Senate passage was found. A bipartisan two-year bill with minimum premium
  payments and income caps was reported as near completion in January 2026.

A later restoration would not reprice 2026 but would change what the 2026
counterfactuals mean. Re-check before submission.

## Interactive calculator

https://aca-subsidy-cliff.vercel.app

Enter an age, a state and an income and see what the expiry did to the net
benchmark premium, how far the household is from the 400% cliff, and what
crossing it costs. It runs the paper's own subsidy calculation in the browser on
the CMS benchmark premiums; nothing typed into it is sent anywhere. Build it with
`python/export_tool_data.py` then `python/build_tool.py`; the export prints the
reference values the page must reproduce.

## Headline results

All enrollment figures are plan selections from the CMS Open Enrollment Period
public use files, on the 30 states that used HealthCare.gov for 2026, in every
year. Premiums are for a single adult at the median rating area.

| Quantity | Value |
|---|---:|
| Median benchmark premium rise, age 40, 349 rating areas | +24.3% (IQR +17.5% to +32.8%) |
| Cliff at 401% FPL, age 40 / 60 / 64 | $1,487 / $10,163 / $11,891 |
| Selections, bands that kept a credit (100 to 400% FPL), 2025 to 2026 | -3.5% |
| Selections, bands that lost the credit (above 400% FPL) | -34.6% (placebo year +9.0%) |
| 300 to 400% band against its counterfactual | +122,752, 71% of the 400 to 500% loss (placebo -66,339) |
| Difference in differences, exposed x post | -31.8 log points (SE 5.0) |
| Dose: exposed loss per point of unsubsidized burden at age 60 | -3.25 log points (SE 0.68); placebo slope 0.08, p = 0.59 |
| Calibrated response, one parameter | 0.0143 exits per point of income; predicts -5.1% above 400% against -34.6% observed |
| Calibrated responses, one per segment | 0.107 above 400%, 0.0097 below, ratio 11 |
| First-year morbidity rise at the calibrated response | +1.2% (range -0.1% to +2.6%) |
| Individual-market regulatory MLR, 2024 | 87.1% on 22.43 million life-years |
| Rebate floor at a 4% claims trend | $269 per enrollee-year (selected-premium path), $536 (benchmark path) |
| Restore the enhanced schedule, 47 states | $23.5 billion a year, $30,786 per person-year of coverage |
| Extend the 9.96% cap above 400% FPL only | $3.3 billion, $9,636 per person-year |

Annual net benchmark premium, single 40-year-old, median rating area:

| Income | 2025 | 2026 | Change |
|---|---:|---:|---:|
| 150% FPL | $0 | $984 | new |
| 200% FPL | $602 | $2,066 | +243% |
| 300% FPL | $2,711 | $4,676 | +72% |
| 400% FPL | $5,120 | $6,235 | +22% |
| 401% FPL | $5,133 | $7,722 | +50% |

## Data

| Source | What | Access |
|---|---|---|
| CMS Exchange Rate PUF, 2025 and 2026 | Plan-level premiums by age and rating area | download.cms.gov/marketplace-puf, no registration |
| CMS Plan Attributes PUF, 2025 and 2026 | Metal level, market, child-only flags | Same |
| CMS Marketplace OEP State-Level PUFs, 2024 to 2026 | Plan selections by state, income, age | cms.gov |
| CMS Marketplace OEP County-Level PUFs, 2024 to 2026 | Plan selections by county and income | cms.gov |
| CMS Medical Loss Ratio PUFs, 2021 to 2024 | Premium, claims, rebates by issuer and state | cms.gov `files/zip/mlr-public-use-file-YYYY.zip` |
| MEPS FYC 2019 to 2024 | Expected-cost model | AHRQ (read from `../paper3/data/raw/meps`) |
| CMS Section 1332 waiver page and December 2022 data brief | Reinsurance states | cms.gov |
| IRS Rev. Proc. 2025-25; HHS poverty guidelines 2024 and 2025 | Schedule and FPL thresholds | irs.gov, aspe.hhs.gov |

```bash
cd data/raw/cms
for y in 2025 2026; do
  for f in rate-puf plan-attributes-puf; do
    curl -sSL -o "${y}_${f}.zip" "https://download.cms.gov/marketplace-puf/$y/$f.zip"
  done
done
for z in *.zip; do unzip -qo "$z" -d "${z%.zip}"; done
```

## Details that decide the results

- The benchmark is the second-lowest silver premium in the rating area at the
  enrollee's age; sentinel rates and child-only and SHOP plans are screened out.
- Alaska and Hawaii use their own poverty guidelines.
- The OEP files carry three total rows per year, a nested 100 to 138% band, and
  platform changes (Georgia for 2025, Illinois for 2026). Platform comparisons
  hold the state set fixed. Connecticut, Minnesota, New York and DC changed how
  they reported income above 400% FPL in 2026 and are excluded from band-level
  comparisons.
- The MLR header carries resubmissions; each year is deduplicated to the latest
  submission per issuer and state, and grand-total and territory rows dropped.
- The selection pool is MEPS's privately insured sample raked to the 2025
  HealthCare.gov age and income marginals, priced at its own age.

## Reproducing

```bash
python3 -m venv .venv
.venv/bin/pip install numpy pandas scipy statsmodels matplotlib pypdf
.venv/bin/python python/run_all.py           # every table and figure, about 2 min
.venv/bin/python python/check_manuscript.py  # prose numbers against the tables
.venv/bin/python python/make_manuscript.py   # DOCX and PDF (needs pandoc)
```

`python/config.py` holds every parameter. `python/oep.py` is the single loader
for the enrollment files; `python/did.py` holds the placebo, difference in
differences and reinsurance tests.

## Author

Oluwatosin Dorcas Babalola, Georgia State University, obabalola4@student.gsu.edu

## License

Code is MIT-licensed. CMS public use files are in the public domain; MEPS is
governed by AHRQ's data-use agreement. Neither is redistributed here.
