# Tables

*Generated from `output/tables/*.csv` by `python/make_tables.py`. Premiums are for a single adult at the median HealthCare.gov rating area unless stated. Enrollment is open enrollment plan selections from the CMS OEP State-Level Public Use Files, not effectuated enrollment. HealthCare.gov means the 30 states on that platform for 2026, in every year.*


**Table 1.** Net benchmark premium by income, single adult aged 40, 2025 and 2026.

*Gross is the median second-lowest-cost silver premium across the 349 rating areas with a benchmark in both years. Net is gross less the premium tax credit under that year's applicable-percentage schedule; income is at each year's own poverty guideline. A percentage change from a zero base is shown as n/a.*

| FPL | Income 2026 | Gross 2025 | Gross 2026 | Net 2025 | Net 2026 | Change $ | Change % | Net % income 2025 | Net % income 2026 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100% | $15,650 | $5,961 | $7,722 | $0 | $329 | $329 | n/a | 0.0% | 2.1% |
| 133% | $20,814 | $5,961 | $7,722 | $0 | $437 | $437 | n/a | 0.0% | 2.1% |
| 150% | $23,475 | $5,961 | $7,722 | $0 | $984 | $984 | n/a | 0.0% | 4.2% |
| 200% | $31,300 | $5,961 | $7,722 | $602 | $2,066 | $1,463 | +243% | 2.0% | 6.6% |
| 250% | $39,125 | $5,961 | $7,722 | $1,506 | $3,302 | $1,796 | +119% | 4.0% | 8.4% |
| 300% | $46,950 | $5,961 | $7,722 | $2,711 | $4,676 | $1,965 | +73% | 6.0% | 10.0% |
| 350% | $54,775 | $5,961 | $7,722 | $3,821 | $5,456 | $1,634 | +43% | 7.3% | 10.0% |
| 400% | $62,600 | $5,961 | $7,722 | $5,120 | $6,235 | $1,115 | +22% | 8.5% | 10.0% |
| 401% | $62,756 | $5,961 | $7,722 | $5,133 | $7,722 | $2,588 | +50% | 8.5% | 12.3% |
| 450% | $70,425 | $5,961 | $7,722 | $5,760 | $7,722 | $1,961 | +34% | 8.5% | 11.0% |
| 500% | $78,250 | $5,961 | $7,722 | $5,961 | $7,722 | $1,761 | +30% | 7.9% | 9.9% |
| 600% | $93,900 | $5,961 | $7,722 | $5,961 | $7,722 | $1,761 | +30% | 6.6% | 8.2% |

**Table 2.** The cliff by age: credit lost by crossing from 400% to 401% of poverty, 2026.

*The cliff is the difference in annual net premium either side of the threshold, computed rating area by rating area with each state's own poverty guideline; the median, 90th percentile and maximum are across rating areas.*

| Age | Gross premium | Cliff, median | Cliff, p90 | Cliff, max | Cliff % income | Gross % income |
|---|---:|---:|---:|---:|---:|---:|
| 21 | $6,042 | $0 | $1,152 | $5,761 | 0.0% | 9.7% |
| 27 | $6,334 | $99 | $1,866 | $6,337 | 0.2% | 10.1% |
| 40 | $7,722 | $1,487 | $3,643 | $9,096 | 2.4% | 12.3% |
| 50 | $10,791 | $4,556 | $7,570 | $15,191 | 7.3% | 17.2% |
| 60 | $16,398 | $10,163 | $14,743 | $26,323 | 16.2% | 26.2% |
| 64 | $18,126 | $11,891 | $15,925 | $29,754 | 19.0% | 29.0% |

**Table 3.** Plan selections by platform, 2025 to 2026, as published and on a constant set of states.

*Illinois moved from HealthCare.gov to a state-based exchange for 2026; the published platform totals therefore compare different states in the two years. The same-states columns assign every state its 2026 platform in both years.*

| Platform | Published 2025 | Published 2026 | Change | States | Same states 2025 | Same states 2026 | Change |
|---|---:|---:|---:|---:|---:|---:|---:|
| All marketplaces | 24,319,713 | 23,130,860 | -4.9% | 51 | 24,319,713 | 23,130,860 | -4.9% |
| HealthCare.gov | 17,128,890 | 15,771,397 | -7.9% | 30 | 16,662,905 | 15,771,397 | -5.4% |
| State-based exchanges | 7,190,823 | 7,359,463 | +2.3% | 21 | 7,656,808 | 7,359,463 | -3.9% |

**Table 3b.** Plan selections by income band, 30 HealthCare.gov states, 2024 to 2026.

*Bands below 100% FPL and with unknown income are excluded. The 2024 to 2025 column is a placebo period in which the enhanced schedule applied in both years.*

| Income band | 2024 | 2025 | 2026 | Change 2024 to 2025 | Change 2025 to 2026 |
|---|---:|---:|---:|---:|---:|
| 100-150% | 7,760,271 | 9,070,434 | 8,793,788 | +16.9% | -3.0% |
| 150-200% | 2,370,971 | 2,754,759 | 2,574,719 | +16.2% | -6.5% |
| 200-250% | 1,504,629 | 1,571,249 | 1,480,945 | +4.4% | -5.7% |
| 250-300% | 851,909 | 944,139 | 867,002 | +10.8% | -8.2% |
| 300-400% | 875,903 | 939,521 | 1,021,383 | +7.3% | +8.7% |
| 400-500% | 351,811 | 377,134 | 203,976 | +7.2% | -45.9% |
| Above 500% | 435,849 | 481,311 | 357,059 | +10.4% | -25.8% |
| Kept a credit (100-400%) | 13,363,683 | 15,280,102 | 14,737,837 | +14.3% | -3.5% |
| Lost the credit (above 400%) | 787,660 | 858,445 | 561,035 | +9.0% | -34.6% |

**Table 4.** Tweedie model of annual expenditure, under-65 privately insured, MEPS 2019 to 2024.

*Log link, variance power 1.6, person weights divided by the number of pooled years, standard errors clustered on the stratum-PSU pair. Reference categories: age 0-17, income 138-250% FPL, male, no chronic condition, Northeast. * marks p < 0.05.*

| Term | Relativity | Coefficient | SE | z | p |  |
|---|---:|---:|---:|---:|---:|---:|
| age_band_18-25 | 1.003 | 0.003 | 0.069 | 0.04 | 0.971 |  |
| age_band_26-34 | 1.330 | 0.285 | 0.058 | 4.92 | 0.000 | * |
| age_band_35-44 | 1.300 | 0.262 | 0.055 | 4.78 | 0.000 | * |
| age_band_45-54 | 1.360 | 0.307 | 0.061 | 5.02 | 0.000 | * |
| age_band_55-59 | 1.394 | 0.332 | 0.064 | 5.20 | 0.000 | * |
| age_band_60-64 | 1.500 | 0.405 | 0.066 | 6.19 | 0.000 | * |
| fpl_band_250-400 | 1.121 | 0.114 | 0.046 | 2.49 | 0.013 | * |
| fpl_band_400+ | 1.355 | 0.304 | 0.040 | 7.52 | 0.000 | * |
| fpl_band_<138 | 1.138 | 0.129 | 0.066 | 1.95 | 0.051 |  |
| female | 1.390 | 0.329 | 0.031 | 10.51 | 0.000 | * |
| chronic | 1.164 | 0.152 | 0.049 | 3.13 | 0.002 | * |
| chronic_count | 1.408 | 0.342 | 0.017 | 20.11 | 0.000 | * |
| region_2 | 1.045 | 0.044 | 0.054 | 0.82 | 0.412 |  |
| region_3 | 0.856 | -0.155 | 0.049 | -3.19 | 0.001 | * |
| region_4 | 1.035 | 0.034 | 0.054 | 0.63 | 0.526 |  |
| nongroup | 0.943 | -0.059 | 0.081 | -0.73 | 0.468 |  |

**Table 5.** Calibrated price responses and what each specification predicts for the two segments.

*The response is the share of enrollees exiting per percentage point of income by which their own annual payment for the benchmark rose (per unit proportional rise for the proportional metric). Each single-response row is solved so that total retention in the 100%+ FPL bands equals the observed 94.8%. The last three rows fit one response to each segment. Tilt is how much more readily a lower-cost enrollee exits.*

| Specification | Tilt | Response (below 400%) | Response above 400% | Morbidity rise | Model: 100-400% FPL | Model: above 400% |
|---|---:|---:|---:|---:|---:|---:|
| Primary | 1.0 | 0.0154 |  | -0.1% | -5.1% | -6.9% |
| Primary | 1.5 | 0.0143 |  | +1.2% | -5.2% | -5.1% |
| Primary | 2.0 | 0.0125 |  | +1.7% | -5.3% | -4.2% |
| Cost 75/25 blend of prediction and realised cost | 1.0 | 0.0154 |  | -0.1% | -5.1% | -6.9% |
| Cost 75/25 blend of prediction and realised cost | 1.5 | 0.0143 |  | +1.4% | -5.2% | -5.4% |
| Cost 75/25 blend of prediction and realised cost | 2.0 | 0.0126 |  | +2.1% | -5.2% | -4.5% |
| Cost 50/50 blend of prediction and realised cost | 1.0 | 0.0154 |  | -0.1% | -5.1% | -6.9% |
| Cost 50/50 blend of prediction and realised cost | 1.5 | 0.0143 |  | +1.9% | -5.2% | -5.7% |
| Cost 50/50 blend of prediction and realised cost | 2.0 | 0.0127 |  | +2.6% | -5.2% | -4.9% |
| Proportional price metric | 1.0 | 0.0342 |  | +0.2% | -5.4% | -2.2% |
| Proportional price metric | 1.5 | 0.0310 |  | +1.3% | -5.4% | -1.6% |
| Proportional price metric | 2.0 | 0.0268 |  | +1.9% | -5.4% | -1.3% |
| Everyone priced at the age-40 benchmark | 1.0 | 0.0160 |  | +0.1% | -5.3% | -3.0% |
| Everyone priced at the age-40 benchmark | 1.5 | 0.0147 |  | +1.3% | -5.3% | -2.6% |
| Everyone priced at the age-40 benchmark | 2.0 | 0.0128 |  | +1.8% | -5.4% | -2.3% |
| Earlier specification: MEPS non-group mix, age-40 benchmark, 50/50 cell-mean blend, proportional metric | 1.0 | 0.0696 |  | +0.5% | -9.5% | -2.2% |
| Earlier specification: MEPS non-group mix, age-40 benchmark, 50/50 cell-mean blend, proportional metric | 1.5 | 0.0599 |  | +2.0% | -9.7% | -2.1% |
| Earlier specification: MEPS non-group mix, age-40 benchmark, 50/50 cell-mean blend, proportional metric | 2.0 | 0.0501 |  | +2.6% | -9.9% | -1.9% |
| Two responses: above and below 400% FPL | 1.0 | 0.0107 | 0.0884 | -0.9% | -3.5% | -34.6% |
| Two responses: above and below 400% FPL | 1.5 | 0.0097 | 0.1069 | +0.3% | -3.5% | -34.6% |
| Two responses: above and below 400% FPL | 2.0 | 0.0085 | 0.1187 | +1.0% | -3.5% | -34.6% |

**Table 6.** Bunching below the threshold, 2025 to 2026, with the 2024 to 2025 placebo.

*The counterfactual moves the 300-400% band's starting count at the control bands' rate. The placebo excess is the same calculation for 2024 to 2025. The adjusted excess carries the band's 2024 to 2025 gap to the control forward before measuring the 2026 excess.*

| Sample | Control bands | Control change | Excess | Placebo excess | Adjusted excess | Excess / 400-500% loss | Adjusted / loss |
|---|---:|---:|---:|---:|---:|---:|---:|
| HealthCare.gov (30) | 100-300% pooled | -4.4% | 122,752 | -66,339 | 182,019 | 71% | 105% |
| HealthCare.gov (30) | 250-300% only | -8.2% | 158,622 | -31,210 | 186,360 | 92% | 108% |
| HealthCare.gov (30) | 200-300% pooled | -6.7% | 144,403 | 4,575 | 140,111 | 83% | 81% |
| All consistent-reporting states (47) | 100-300% pooled | -3.5% | 187,051 | -86,964 | 266,789 | 67% | 96% |
| All consistent-reporting states (47) | 250-300% only | -7.4% | 252,069 | -58,545 | 304,433 | 91% | 110% |
| All consistent-reporting states (47) | 200-300% pooled | -6.2% | 231,004 | 21,894 | 210,188 | 83% | 76% |

**Table 6b.** State by income band by period regressions of the log change in plan selections.

*Outcome: 100 times the log of the band's count in the later year over the earlier year, for 2024 to 2025 and 2025 to 2026. State-by-period and band fixed effects; cells weighted by the earlier count; standard errors clustered by state. Exposed x post is the difference in differences for the bands above 400% FPL; notch x post is the same for the 300-400% band. Burden is the state's unsubsidized benchmark at age 60 as a share of income at 401% FPL, centred, so the dose terms are per percentage point.*

| Model | Sample | Term | Coefficient | SE | t | p |
|---|---:|---:|---:|---:|---:|---:|
| A. Difference in differences | All consistent (47) | exposed_post | -36.35 | 10.50 | -3.46 | < 0.001 |
| A. Difference in differences | All consistent (47) | notch_post | 17.88 | 2.91 | 6.14 | < 0.001 |
| A. Difference in differences | HealthCare.gov (30) | exposed_post | -31.81 | 4.96 | -6.42 | < 0.001 |
| A. Difference in differences | HealthCare.gov (30) | notch_post | 22.30 | 2.96 | 7.54 | < 0.001 |
| B. Dose: unsubsidised burden at age 60 | HealthCare.gov (30) | exposed_post | -32.87 | 3.26 | -10.09 | < 0.001 |
| B. Dose: unsubsidised burden at age 60 | HealthCare.gov (30) | notch_post | 22.38 | 2.83 | 7.92 | < 0.001 |
| B. Dose: unsubsidised burden at age 60 | HealthCare.gov (30) | exposed_burden | 0.26 | 0.41 | 0.64 | 0.521 |
| B. Dose: unsubsidised burden at age 60 | HealthCare.gov (30) | exposed_post_burden | -3.25 | 0.68 | -4.82 | < 0.001 |
| B. Dose: unsubsidised burden at age 60 | HealthCare.gov (30) | notch_burden | 0.50 | 0.39 | 1.30 | 0.193 |
| B. Dose: unsubsidised burden at age 60 | HealthCare.gov (30) | notch_post_burden | -0.48 | 0.55 | -0.88 | 0.378 |

**Table 7.** Across the 30 HealthCare.gov states: enrollment change on the burden of unsubsidized cover, with the placebo period.

*Regressor: the state's median unsubsidized benchmark at age 60 as a share of income at 401% FPL. Weighted rows use the segment's count at the start of the period. HC1 standard errors. Per-state values are in Table A4.*

| Outcome | Period | Weighted | Slope | SE | t | p | States |
|---|---:|---:|---:|---:|---:|---:|---:|
| Whole-state enrollment change | 2025-26 | no | -0.061 | 0.142 | -0.43 | 0.665 | 30 |
| Change above 400% FPL | 2025-26 | yes | -1.369 | 0.208 | -6.57 | < 0.001 | 30 |
| Change above 400% FPL | 2024-25 (placebo) | yes | 0.082 | 0.153 | 0.54 | 0.590 | 30 |
| Above-400% change less 100-400% change | 2025-26 | yes | -2.012 | 0.427 | -4.71 | < 0.001 | 30 |
| Above-400% change less 100-400% change | 2024-25 (placebo) | yes | 0.256 | 0.400 | 0.64 | 0.522 | 30 |
| Change above 400% FPL, unweighted | 2025-26 | no | -1.147 | 0.218 | -5.26 | < 0.001 | 30 |

**Table 8.** Individual-market loss ratios, 2021 to 2024.

*CMS Medical Loss Ratio public use files, comprehensive individual-market columns, deduplicated to the latest submission per issuer and state, territories excluded. The simple ratio is incurred claims over earned premium; the regulatory ratio is the statutory numerator over the statutory denominator.*

| Year | Issuer-states | Life-years | Premium PMPM | Claims PMPM | Simple LR | Regulatory MLR | Rebates |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2,021 | 678 | 14.84m | $550 | $486 | 88.4% | 90.4% | $318m |
| 2,022 | 693 | 16.89m | $523 | $462 | 88.3% | 87.8% | $612m |
| 2,023 | 628 | 18.68m | $575 | $486 | 84.5% | 86.3% | $1,293m |
| 2,024 | 579 | 22.43m | $587 | $513 | 87.4% | 87.1% | $1,227m |

**Table 8b.** What the 80% floor would return in 2026 across claims trends.

*Projected MLR is the 2024 regulatory ratio times two years of claims trend, over the 2024 to 2026 premium factor. The first path uses the average premium of plans selected; the second replaces the 2025 to 2026 step with the median benchmark increase. The break-even trend is the annual claims trend at which the projected ratio is exactly 80%. An illustration of the bound, not a forecast.*

| Premium path | Claims trend | Premium factor | Projected MLR | Rebate % premium | Rebate per enrollee-year | Break-even trend |
|---|---:|---:|---:|---:|---:|---:|
| Average premium of plans selected | 4% | 1.225 | 76.9% | 3.1% | $269 | 6.1% |
| Average premium of plans selected | 6% | 1.225 | 79.9% | 0.1% | $11 | 6.1% |
| Average premium of plans selected | 8% | 1.225 | 82.9% | 0.0% | $0 | 6.1% |
| Average premium of plans selected | 10% | 1.225 | 86.0% | 0.0% | $0 | 6.1% |
| Average premium of plans selected | 12% | 1.225 | 89.2% | 0.0% | $0 | 6.1% |
| Benchmark for 2025-26 | 4% | 1.272 | 74.0% | 6.0% | $536 | 8.1% |
| Benchmark for 2025-26 | 6% | 1.272 | 76.9% | 3.1% | $279 | 8.1% |
| Benchmark for 2025-26 | 8% | 1.272 | 79.8% | 0.2% | $16 | 8.1% |
| Benchmark for 2025-26 | 10% | 1.272 | 82.8% | 0.0% | $0 | 8.1% |
| Benchmark for 2025-26 | 12% | 1.272 | 85.8% | 0.0% | $0 | 8.1% |

**Table 9.** Restoring the enhanced schedule for 2026: cost and coverage by income band, 30 HealthCare.gov states.

*Single-person schedule at the median benchmark for each age band and the 2025 age mix. Coverage gained is the gap between the band's 2025 count moved at the 100-150% band's rate and its 2026 count; that band is the control and has no effect estimated for it. Net of bunching removes the Table 6 excess from the bands above 400% pro rata. Cost is the extra credit paid to everyone the band would then contain.*

| Band | Extra credit | Coverage gained | Net of bunching | Annual cost | Cost per person-year | Marginal share |
|---|---:|---:|---:|---:|---:|---:|
| 100-150% | $411 | control | control | $3.61b |  |  |
| 150-200% | $1,204 | 96,021 | 96,021 | $3.21b | $33,479 | 3.6% |
| 200-250% | $1,592 | 42,381 | 42,381 | $2.42b | $57,208 | 2.8% |
| 250-300% | $1,808 | 48,341 | 48,341 | $1.65b | $34,227 | 5.3% |
| 300-400% | $1,484 | 0 | 0 | $1.52b |  | 0.0% |
| 400-500% | $4,007 | 161,656 | 88,494 | $1.47b | $9,064 | 44.2% |
| Above 500% | $2,159 | 109,572 | 59,982 | $1.01b | $9,196 | 23.5% |

**Table 9b.** Four schedules priced on 2026 premiums: outlay and cost per person-year of coverage.

*For schedules other than full restoration, a band recovers the share of its full-restoration coverage gain equal to the share of the full payment reduction the schedule delivers. The CBO column is the CRS-reported estimate for permanent extension, $350 billion over 2026 to 2035 and 3.8 million more insured in 2035, expressed per person-year at the end of the window.*

| Sample | Schedule | Annual cost | Coverage gained | Net of bunching | Cost per person-year | Net of bunching | Cost above 400% | Coverage above 400% | CBO implied |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| HealthCare.gov (30) | Restore the enhanced schedule | $14.9b | 457,970 | 335,219 | $32,525 | $44,435 | 17% | 59% | $9,211 |
| HealthCare.gov (30) | Enhanced schedule to 600% FPL | $14.3b | 398,125 | 302,458 | $35,884 | $47,234 | 13% | 53% | $9,211 |
| HealthCare.gov (30) | Enhanced schedule to 400% FPL only | $12.4b | 186,743 | 186,743 | $66,522 | $66,522 | 0% | 0% | $9,211 |
| HealthCare.gov (30) | 2026 schedule, 9.96% cap extended above 400% | $1.7b | 205,901 | 112,715 | $8,352 | $15,257 | 100% | 100% | $9,211 |
| All consistent (47) | Restore the enhanced schedule | $23.5b | 762,677 | 575,626 | $30,786 | $40,789 | 20% | 58% | $9,211 |
| All consistent (47) | Enhanced schedule to 600% FPL | $22.3b | 664,830 | 519,070 | $33,612 | $43,051 | 16% | 52% | $9,211 |
| All consistent (47) | Enhanced schedule to 400% FPL only | $18.9b | 319,421 | 319,421 | $59,059 | $59,059 | 0% | 0% | $9,211 |
| All consistent (47) | 2026 schedule, 9.96% cap extended above 400% | $3.3b | 338,214 | 195,490 | $9,636 | $16,672 | 100% | 100% | $9,211 |


# Appendix tables


**Table A1.** The unsubsidized premium as a share of income, 2026.

*Share of rating areas in which the full benchmark premium exceeds each share of income, with each state's own poverty guideline.*

| FPL | Age | Income | Premium | % income | Areas > 10% | Areas > 20% | Areas > 30% |
|---|---:|---:|---:|---:|---:|---:|---:|
| 401% | 21 | $62,756 | $6,042 | 9.6% | 40% | 0% | 0% |
| 401% | 27 | $62,756 | $6,334 | 10.1% | 53% | 0% | 0% |
| 401% | 40 | $62,756 | $7,722 | 12.3% | 82% | 3% | 0% |
| 401% | 50 | $62,756 | $10,791 | 17.2% | 100% | 19% | 1% |
| 401% | 60 | $62,756 | $16,398 | 26.1% | 100% | 90% | 20% |
| 401% | 64 | $62,756 | $18,126 | 28.9% | 100% | 99% | 40% |
| 450% | 21 | $70,425 | $6,042 | 8.6% | 19% | 0% | 0% |
| 450% | 27 | $70,425 | $6,334 | 9.0% | 24% | 0% | 0% |
| 450% | 40 | $70,425 | $7,722 | 11.0% | 64% | 1% | 0% |
| 450% | 50 | $70,425 | $10,791 | 15.3% | 99% | 9% | 1% |
| 450% | 60 | $70,425 | $16,398 | 23.3% | 100% | 72% | 9% |
| 450% | 64 | $70,425 | $18,126 | 25.7% | 100% | 88% | 19% |
| 500% | 21 | $78,250 | $6,042 | 7.7% | 8% | 0% | 0% |
| 500% | 27 | $78,250 | $6,334 | 8.1% | 10% | 0% | 0% |
| 500% | 40 | $78,250 | $7,722 | 9.9% | 46% | 0% | 0% |
| 500% | 50 | $78,250 | $10,791 | 13.8% | 94% | 5% | 0% |
| 500% | 60 | $78,250 | $16,398 | 21.0% | 100% | 57% | 6% |
| 500% | 64 | $78,250 | $18,126 | 23.2% | 100% | 72% | 8% |
| 600% | 21 | $93,900 | $6,042 | 6.4% | 4% | 0% | 0% |
| 600% | 27 | $93,900 | $6,334 | 6.7% | 5% | 0% | 0% |
| 600% | 40 | $93,900 | $7,722 | 8.2% | 11% | 0% | 0% |
| 600% | 50 | $93,900 | $10,791 | 11.5% | 70% | 1% | 0% |
| 600% | 60 | $93,900 | $16,398 | 17.5% | 100% | 20% | 1% |
| 600% | 64 | $93,900 | $18,126 | 19.3% | 100% | 41% | 4% |

**Table A2.** Repricing dynamics by segment and age at the segment-specific calibrated responses and multiples of them.

*Exit responds to the increment in the household's payment, in points of income, since the previous repricing, with the bounded form 1 - exp(-response x rise / tilt). Leavers cost 22% less than stayers, from Table A5, so the premium factor after a cumulative exit share x is 1 / (1 - 0.22 x). No cell reaches the spiral threshold of 3.*

| Response multiple | Segment | Age | Paid 2025 | Paid 2026 | First-round exit | Cumulative exit | Premium factor | Rounds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Subsidised, 250% FPL | 21 | $1,506 | $3,302 | 2.8% | 2.8% | 1.006 | 2 |
| 1 | Subsidised, 390% FPL | 21 | $4,649 | $6,042 | 1.3% | 1.3% | 1.003 | 3 |
| 1 | Unsubsidised, 450% FPL | 21 | $4,649 | $6,042 | 11.5% | 13.2% | 1.030 | 6 |
| 1 | Subsidised, 250% FPL | 27 | $1,506 | $3,302 | 2.8% | 2.8% | 1.006 | 2 |
| 1 | Subsidised, 390% FPL | 27 | $4,846 | $6,079 | 1.1% | 1.1% | 1.002 | 2 |
| 1 | Unsubsidised, 450% FPL | 27 | $4,879 | $6,334 | 12.0% | 13.8% | 1.032 | 7 |
| 1 | Subsidised, 250% FPL | 40 | $1,506 | $3,302 | 2.8% | 2.8% | 1.006 | 2 |
| 1 | Subsidised, 390% FPL | 40 | $4,846 | $6,079 | 1.1% | 1.1% | 1.002 | 2 |
| 1 | Unsubsidised, 450% FPL | 40 | $5,760 | $7,722 | 16.1% | 19.0% | 1.044 | 7 |
| 1 | Subsidised, 250% FPL | 50 | $1,506 | $3,302 | 2.8% | 2.8% | 1.006 | 2 |
| 1 | Subsidised, 390% FPL | 50 | $4,846 | $6,079 | 1.1% | 1.1% | 1.002 | 2 |
| 1 | Unsubsidised, 450% FPL | 50 | $5,760 | $10,791 | 38.5% | 45.7% | 1.114 | 8 |
| 1 | Subsidised, 250% FPL | 60 | $1,506 | $3,302 | 2.8% | 2.8% | 1.006 | 2 |
| 1 | Subsidised, 390% FPL | 60 | $4,846 | $6,079 | 1.1% | 1.1% | 1.002 | 2 |
| 1 | Unsubsidised, 450% FPL | 60 | $5,760 | $16,398 | 65.1% | 75.1% | 1.202 | 8 |
| 1 | Subsidised, 250% FPL | 64 | $1,506 | $3,302 | 2.8% | 2.8% | 1.006 | 2 |
| 1 | Subsidised, 390% FPL | 64 | $4,846 | $6,079 | 1.1% | 1.1% | 1.002 | 2 |
| 1 | Unsubsidised, 450% FPL | 64 | $5,760 | $18,126 | 70.7% | 80.4% | 1.220 | 7 |
| 2 | Subsidised, 250% FPL | 21 | $1,506 | $3,302 | 5.6% | 5.6% | 1.013 | 2 |
| 2 | Subsidised, 390% FPL | 21 | $4,649 | $6,042 | 2.5% | 2.6% | 1.006 | 4 |
| 2 | Unsubsidised, 450% FPL | 21 | $4,649 | $6,042 | 21.7% | 27.9% | 1.067 | 9 |
| 2 | Subsidised, 250% FPL | 27 | $1,506 | $3,302 | 5.6% | 5.6% | 1.013 | 2 |
| 2 | Subsidised, 390% FPL | 27 | $4,846 | $6,079 | 2.2% | 2.2% | 1.005 | 2 |
| 2 | Unsubsidised, 450% FPL | 27 | $4,879 | $6,334 | 22.6% | 29.2% | 1.070 | 9 |
| 2 | Subsidised, 250% FPL | 40 | $1,506 | $3,302 | 5.6% | 5.6% | 1.013 | 2 |
| 2 | Subsidised, 390% FPL | 40 | $4,846 | $6,079 | 2.2% | 2.2% | 1.005 | 2 |
| 2 | Unsubsidised, 450% FPL | 40 | $5,760 | $7,722 | 29.6% | 39.5% | 1.097 | 10 |
| 2 | Subsidised, 250% FPL | 50 | $1,506 | $3,302 | 5.6% | 5.6% | 1.013 | 2 |
| 2 | Subsidised, 390% FPL | 50 | $4,846 | $6,079 | 2.2% | 2.2% | 1.005 | 2 |
| 2 | Unsubsidised, 450% FPL | 50 | $5,760 | $10,791 | 62.2% | 75.8% | 1.204 | 8 |
| 2 | Subsidised, 250% FPL | 60 | $1,506 | $3,302 | 5.6% | 5.6% | 1.013 | 2 |
| 2 | Subsidised, 390% FPL | 60 | $4,846 | $6,079 | 2.2% | 2.2% | 1.005 | 2 |
| 2 | Unsubsidised, 450% FPL | 60 | $5,760 | $16,398 | 87.8% | 95.0% | 1.270 | 6 |
| 2 | Subsidised, 250% FPL | 64 | $1,506 | $3,302 | 5.6% | 5.6% | 1.013 | 2 |
| 2 | Subsidised, 390% FPL | 64 | $4,846 | $6,079 | 2.2% | 2.2% | 1.005 | 2 |
| 2 | Unsubsidised, 450% FPL | 64 | $5,760 | $18,126 | 91.4% | 96.9% | 1.277 | 6 |
| 4 | Subsidised, 250% FPL | 21 | $1,506 | $3,302 | 10.9% | 10.9% | 1.025 | 2 |
| 4 | Subsidised, 390% FPL | 21 | $4,649 | $6,042 | 5.0% | 5.2% | 1.012 | 3 |
| 4 | Unsubsidised, 450% FPL | 21 | $4,649 | $6,042 | 38.8% | 57.2% | 1.147 | 11 |
| 4 | Subsidised, 250% FPL | 27 | $1,506 | $3,302 | 10.9% | 10.9% | 1.025 | 2 |
| 4 | Subsidised, 390% FPL | 27 | $4,846 | $6,079 | 4.3% | 4.3% | 1.010 | 2 |
| 4 | Unsubsidised, 450% FPL | 27 | $4,879 | $6,334 | 40.1% | 59.6% | 1.154 | 12 |
| 4 | Subsidised, 250% FPL | 40 | $1,506 | $3,302 | 10.9% | 10.9% | 1.025 | 2 |
| 4 | Subsidised, 390% FPL | 40 | $4,846 | $6,079 | 4.3% | 4.3% | 1.010 | 2 |
| 4 | Unsubsidised, 450% FPL | 40 | $5,760 | $7,722 | 50.5% | 73.1% | 1.196 | 11 |
| 4 | Subsidised, 250% FPL | 50 | $1,506 | $3,302 | 10.9% | 10.9% | 1.025 | 2 |
| 4 | Subsidised, 390% FPL | 50 | $4,846 | $6,079 | 4.3% | 4.3% | 1.010 | 2 |
| 4 | Unsubsidised, 450% FPL | 50 | $5,760 | $10,791 | 85.7% | 95.7% | 1.273 | 6 |
| 4 | Subsidised, 250% FPL | 60 | $1,506 | $3,302 | 10.9% | 10.9% | 1.025 | 2 |
| 4 | Subsidised, 390% FPL | 60 | $4,846 | $6,079 | 4.3% | 4.3% | 1.010 | 2 |
| 4 | Unsubsidised, 450% FPL | 60 | $5,760 | $16,398 | 98.5% | 99.8% | 1.288 | 4 |
| 4 | Subsidised, 250% FPL | 64 | $1,506 | $3,302 | 10.9% | 10.9% | 1.025 | 2 |
| 4 | Subsidised, 390% FPL | 64 | $4,846 | $6,079 | 4.3% | 4.3% | 1.010 | 2 |
| 4 | Unsubsidised, 450% FPL | 64 | $5,760 | $18,126 | 99.3% | 99.9% | 1.288 | 4 |

**Table A3.** The cliff by HealthCare.gov state, age 60.

*Median across the state's rating areas.*

| State | Rating areas | Gross premium | Cliff | Cliff % income | Gross % income |
|---|---:|---:|---:|---:|---:|
| WV | 11 | $27,878 | $21,643 | 34.6% | 44.5% |
| WY | 3 | $27,351 | $21,116 | 33.7% | 43.7% |
| AK | 3 | $26,127 | $18,338 | 23.5% | 33.4% |
| AR | 7 | $19,723 | $13,488 | 21.5% | 31.5% |
| NE | 4 | $18,336 | $12,101 | 19.3% | 29.3% |
| TN | 8 | $18,030 | $11,795 | 18.8% | 28.8% |
| UT | 6 | $17,941 | $11,706 | 18.7% | 28.7% |
| KS | 7 | $17,919 | $11,684 | 18.7% | 28.6% |
| FL | 67 | $17,814 | $11,579 | 18.5% | 28.5% |
| MT | 4 | $17,682 | $11,447 | 18.3% | 28.2% |
| DE | 1 | $17,627 | $11,392 | 18.2% | 28.2% |
| LA | 8 | $17,444 | $11,209 | 17.9% | 27.9% |
| AZ | 7 | $17,036 | $10,801 | 17.3% | 27.2% |
| TX | 27 | $17,019 | $10,784 | 17.2% | 27.2% |
| MO | 10 | $16,971 | $10,736 | 17.2% | 27.1% |
| NC | 16 | $16,435 | $10,200 | 16.3% | 26.3% |
| MS | 6 | $16,348 | $10,113 | 16.2% | 26.1% |
| AL | 13 | $16,295 | $10,060 | 16.1% | 26.0% |
| WI | 16 | $15,981 | $9,746 | 15.6% | 25.5% |
| OK | 5 | $14,507 | $8,272 | 13.2% | 23.2% |
| SC | 46 | $14,177 | $7,942 | 12.7% | 22.6% |
| SD | 4 | $13,664 | $7,429 | 11.9% | 21.8% |
| OR | 7 | $13,656 | $7,421 | 11.9% | 21.8% |
| OH | 17 | $13,383 | $7,148 | 11.4% | 21.4% |
| HI | 1 | $13,839 | $6,672 | 9.3% | 19.2% |
| ND | 4 | $12,713 | $6,478 | 10.3% | 20.3% |
| MI | 16 | $12,274 | $6,039 | 9.6% | 19.6% |
| IA | 7 | $12,166 | $5,931 | 9.5% | 19.4% |
| IN | 17 | $12,120 | $5,885 | 9.4% | 19.4% |
| NH | 1 | $9,898 | $3,663 | 5.9% | 15.8% |

**Table A4.** Per-state inputs to Table 7.

| State | Burden at 401% FPL | 1332 reinsurance | Above 400%, 2025 | Above 400%, 2024 to 2025 | Above 400%, 2025 to 2026 | 100-400%, 2025 to 2026 | All, 2025 to 2026 |
|---|---:|---:|---:|---:|---:|---:|---:|
| WV | 44.5% |  | 6,276 | +23.8% | -46.8% | -13.9% | -16.7% |
| WY | 43.7% |  | 8,378 | +8.9% | -59.7% | -0.3% | -10.9% |
| AK | 33.4% | yes | 5,787 | +11.5% | -33.2% | -3.9% | -9.2% |
| AR | 31.5% |  | 11,922 | +13.7% | -25.2% | -2.7% | -3.8% |
| NE | 29.3% |  | 16,390 | +10.6% | -48.6% | -0.7% | -6.0% |
| TN | 28.8% |  | 27,658 | +13.5% | -38.3% | -9.9% | -11.4% |
| UT | 28.7% |  | 32,168 | +8.9% | -41.7% | -4.7% | -8.2% |
| KS | 28.6% |  | 12,106 | +13.0% | -39.8% | -1.2% | -3.6% |
| FL | 28.5% |  | 142,447 | +6.7% | -42.4% | -2.0% | -4.2% |
| MT | 28.2% | yes | 12,428 | +13.4% | -24.4% | -2.2% | -5.1% |
| DE | 28.2% | yes | 7,451 | +8.0% | -31.5% | -13.5% | -15.6% |
| LA | 27.9% |  | 13,890 | +9.5% | -38.0% | +3.9% | +1.2% |
| AZ | 27.2% |  | 33,277 | +10.2% | -33.2% | -14.8% | -15.6% |
| TX | 27.2% |  | 126,158 | +8.1% | -36.5% | +7.0% | +5.2% |
| MO | 27.1% |  | 25,306 | +14.6% | -34.2% | -11.9% | -12.3% |
| NC | 26.3% |  | 68,261 | +4.8% | -36.0% | -21.6% | -21.9% |
| MS | 26.1% |  | 2,949 | +18.7% | -47.9% | -6.8% | -7.3% |
| AL | 26.0% |  | 14,610 | +6.0% | -29.0% | -4.0% | -4.6% |
| WI | 25.5% | yes | 48,246 | +12.3% | -31.4% | -4.0% | -7.1% |
| OK | 23.2% |  | 11,309 | +1.7% | -35.3% | -14.1% | -15.0% |
| SC | 22.6% |  | 34,379 | +7.4% | -32.7% | -5.8% | -7.0% |
| SD | 21.8% |  | 8,178 | +11.5% | -36.2% | -2.5% | -6.9% |
| OR | 21.8% | yes | 34,971 | +7.1% | -24.4% | -15.9% | -15.3% |
| OH | 21.4% |  | 42,499 | +12.5% | -28.5% | -19.8% | -19.5% |
| HI | 19.2% |  | 3,473 | +11.4% | -12.8% | -2.2% | -5.0% |
| ND | 20.3% | yes | 7,625 | +15.9% | -29.6% | +1.3% | -4.4% |
| MI | 19.6% |  | 43,458 | +9.8% | -24.4% | -4.6% | -6.4% |
| IA | 19.4% |  | 17,432 | +15.0% | -23.5% | -10.3% | -9.9% |
| IN | 19.4% |  | 27,188 | +5.7% | -28.8% | -15.8% | -16.5% |
| NH | 15.8% | yes | 12,225 | +7.6% | -12.7% | -11.4% | -6.1% |

**Table A5.** Who leaves in the selection model at the primary calibrated response, tilt 1.5.

| Dimension | Group | Share of pool | Net 2025 | Net 2026 | Exit rate | Cost of leavers | Cost of stayers |
|---|---:|---:|---:|---:|---:|---:|---:|
| Income | FPL_100_150 | 56.2% | $0 | $564 | 4.3% | $5,384 | $7,083 |
| Income | FPL_150_200 | 17.1% | $296 | $1,529 | 7.2% | $5,009 | $6,472 |
| Income | FPL_200_250 | 9.7% | $1,031 | $2,662 | 7.2% | $5,151 | $6,648 |
| Income | FPL_250_300 | 5.9% | $2,090 | $3,977 | 6.2% | $5,738 | $7,308 |
| Income | FPL_300_400 | 5.8% | $3,821 | $5,435 | 4.1% | $5,699 | $7,267 |
| Income | FPL_400_500 | 2.3% | $5,537 | $10,547 | 7.6% | $8,719 | $8,763 |
| Income | FPL_GT500 | 3.0% | $7,534 | $11,011 | 3.2% | $8,345 | $8,659 |
| Age | Age_18_25 | 12.8% | $532 | $1,428 | 6.9% | $3,260 | $3,592 |
| Age | Age_26_34 | 18.9% | $712 | $1,691 | 5.7% | $4,495 | $5,104 |
| Age | Age_35_44 | 22.4% | $829 | $1,856 | 5.4% | $4,873 | $5,790 |
| Age | Age_45_54 | 21.6% | $985 | $2,131 | 4.8% | $6,106 | $7,664 |
| Age | Age_55_64 | 24.4% | $1,021 | $2,396 | 4.1% | $8,565 | $10,893 |
| All | All | 100.0% | $850 | $1,961 | 5.2% | $5,471 | $7,050 |

**Table A6.** The selection model over a grid of responses and tilts.

*Response is the exit share per percentage point of income. Retention and morbidity are after repricing converges.*

| Response | Tilt | Retained | Morbidity | Retained above 400% | Retained 100-400% | Rounds |
|---|---:|---:|---:|---:|---:|---:|
| 0.005 | 1.0 | 98.3% | -0.0% | 97.8% | 98.3% | 2 |
| 0.005 | 1.5 | 98.2% | +0.4% | 98.2% | 98.2% | 2 |
| 0.005 | 2.0 | 97.9% | +0.7% | 98.4% | 97.9% | 2 |
| 0.010 | 1.0 | 96.6% | -0.0% | 95.5% | 96.7% | 2 |
| 0.010 | 1.5 | 96.4% | +0.8% | 96.4% | 96.4% | 2 |
| 0.010 | 2.0 | 95.8% | +1.4% | 96.7% | 95.8% | 2 |
| 0.020 | 1.0 | 93.2% | -0.1% | 91.1% | 93.4% | 2 |
| 0.020 | 1.5 | 92.7% | +1.7% | 92.7% | 92.7% | 3 |
| 0.020 | 2.0 | 91.7% | +2.9% | 93.1% | 91.6% | 3 |
| 0.040 | 1.0 | 86.5% | -0.2% | 82.2% | 86.7% | 3 |
| 0.040 | 1.5 | 85.4% | +3.7% | 84.7% | 85.4% | 3 |
| 0.040 | 2.0 | 83.3% | +6.3% | 85.0% | 83.2% | 3 |

**Table A7.** Observed change per percentage point of income by which the band's payment rose.

*The shock is the age-weighted rise in the household's own annual payment, in points of income, at the band midpoint (three points for the open top band) with each age band priced at its own benchmark.*

| Band | FPL points | Payment rise | Shock | Change 2025 to 2026 | Change 2024 to 2025 | Change per pp |
|---|---:|---:|---:|---:|---:|---:|
| 100-150% | 125 | $411 | +2.1 pp | -3.0% | +16.9% | -1.45 |
| 150-200% | 175 | $1,214 | +4.4 pp | -6.5% | +16.2% | -1.49 |
| 200-250% | 225 | $1,631 | +4.5 pp | -5.7% | +4.4% | -1.27 |
| 250-300% | 275 | $1,889 | +4.2 pp | -8.2% | +10.8% | -1.95 |
| 300-400% | 350 | $1,634 | +2.7 pp | +8.7% | +7.3% | 3.22 |
| 400-500% | 450 | $4,472 | +6.0 pp | -45.9% | +7.2% | -7.60 |
| Above 500% | 550/650/800 | $3,302 | +3.0 pp | -25.8% | +10.4% | -8.47 |

**Table A8.** Section 1332 reinsurance interactions in the state by band by period regressions.

*Specification as in Table 6b. Reinsurance states are those operating a Section 1332 state-based reinsurance program in 2025 and 2026 per CMS.*

| Model | Sample | Term | Coefficient | SE | t | p |
|---|---:|---:|---:|---:|---:|---:|
| C. Section 1332 reinsurance | All consistent (47) | exposed_post | -27.24 | 5.77 | -4.72 | < 0.001 |
| C. Section 1332 reinsurance | All consistent (47) | notch_post | 17.43 | 2.70 | 6.46 | < 0.001 |
| C. Section 1332 reinsurance | All consistent (47) | exposed_reins | 0.24 | 2.97 | 0.08 | 0.937 |
| C. Section 1332 reinsurance | All consistent (47) | exposed_post_reins | -40.98 | 39.93 | -1.03 | 0.305 |
| C. Section 1332 reinsurance | HealthCare.gov (30) | exposed_post | -33.22 | 5.36 | -6.20 | < 0.001 |
| C. Section 1332 reinsurance | HealthCare.gov (30) | notch_post | 22.47 | 2.92 | 7.69 | < 0.001 |
| C. Section 1332 reinsurance | HealthCare.gov (30) | exposed_reins | 6.23 | 5.86 | 1.06 | 0.288 |
| C. Section 1332 reinsurance | HealthCare.gov (30) | exposed_post_reins | 10.82 | 5.85 | 1.85 | 0.064 |
| D. Reinsurance, holding burden constant | HealthCare.gov (30) | exposed_post | -33.40 | 3.51 | -9.51 | < 0.001 |
| D. Reinsurance, holding burden constant | HealthCare.gov (30) | notch_post | 22.57 | 2.94 | 7.68 | < 0.001 |
| D. Reinsurance, holding burden constant | HealthCare.gov (30) | exposed_reins | 6.90 | 6.09 | 1.13 | 0.258 |
| D. Reinsurance, holding burden constant | HealthCare.gov (30) | exposed_post_reins | 4.05 | 5.00 | 0.81 | 0.417 |
| D. Reinsurance, holding burden constant | HealthCare.gov (30) | exposed_burden | 0.29 | 0.28 | 1.04 | 0.297 |
| D. Reinsurance, holding burden constant | HealthCare.gov (30) | exposed_post_burden | -3.13 | 0.63 | -4.98 | < 0.001 |

**Table A8b.** Benchmark premium growth 2025 to 2026, age 40, by reinsurance status, HealthCare.gov states.

| Group | States | Members | Mean of state median growth | Mean burden at age 60 |
|---|---:|---:|---:|---:|
| No waiver | 23 | AL AR AZ FL HI IA IN KS LA MI MO MS NC NE OH OK SC SD TN TX UT WV WY | +25.2% | 26.9% |
| 1332 reinsurance | 7 | AK DE MT ND NH OR WI | +14.7% | 24.8% |
| Difference (HC1 SE) | 30 | se 5.00, p 0.036 | -10.5% |  |

**Table A9.** County by band by period regressions, 30 HealthCare.gov states.

*As Table 6b with county-by-period fixed effects. The county file publishes one band above 400% FPL. The premium interaction uses the log of the county's 2025 average premium of plans selected, centred.*

| Model | Term | Coefficient | SE | t | p | Counties |
|---|---:|---:|---:|---:|---:|---:|
| County difference in differences | exposed_post | -31.35 | 4.52 | -6.94 | < 0.001 | 2,048 |
| County difference in differences | notch_post | 22.32 | 2.64 | 8.44 | < 0.001 | 2,048 |
| County, by 2025 average premium | exposed_post | -30.58 | 4.36 | -7.02 | < 0.001 | 2,048 |
| County, by 2025 average premium | notch_post | 22.12 | 2.64 | 8.38 | < 0.001 | 2,048 |
| County, by 2025 average premium | exposed_lprem | 11.97 | 5.43 | 2.20 | 0.028 | 2,048 |
| County, by 2025 average premium | exposed_post_lprem | -72.29 | 13.88 | -5.21 | < 0.001 | 2,048 |

**Table A10.** Issuers against the 80% floor, 2024.

| Regulatory MLR | Issuer-states | Life-years | Share of market | Rebates |
|---|---:|---:|---:|---:|
| under 70% | 98 | 0.45m | 2.0% | $441m |
| 70-80% | 65 | 2.25m | 10.0% | $729m |
| 80-90% | 155 | 11.88m | 53.0% | $31m |
| 90-100% | 119 | 5.93m | 26.4% | $0m |
| over 100% | 104 | 1.81m | 8.1% | $0m |

**Table A11.** Observed annual cost by age band, MEPS.

*Relativity is to the 18-25 band.*

| Age band | n | Mean | Median | Any chronic | Zero cost | Relativity |
|---|---:|---:|---:|---:|---:|---:|
| 0-17 | 14,804 | $3,439 | $940 | 8.8% | 10.3% | 0.85x |
| 18-25 | 6,808 | $4,031 | $773 | 22.9% | 20.1% | 1.00x |
| 26-34 | 9,537 | $5,740 | $1,209 | 32.0% | 17.0% | 1.42x |
| 35-44 | 11,872 | $6,453 | $1,455 | 44.4% | 13.4% | 1.60x |
| 45-54 | 11,709 | $8,293 | $2,070 | 61.4% | 10.4% | 2.06x |
| 55-59 | 6,616 | $10,403 | $2,857 | 75.2% | 6.5% | 2.58x |
| 60-64 | 6,773 | $12,580 | $3,689 | 83.1% | 5.4% | 3.12x |
