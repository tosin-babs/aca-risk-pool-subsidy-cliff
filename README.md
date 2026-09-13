# The Subsidy Cliff and the Risk Pool: An Actuarial Model of Adverse Selection and Premium Stability in the ACA Individual Market

Paper 4 of the *Health-Cost Risk and Financial Protection* research programme.

The enhanced premium tax credits enacted by ARPA in 2021 and extended by the IRA
in 2022 expired on 31 December 2025. The 2026 plan year was priced and enrolled
without them. This paper models what that did to net premiums, to who stays in
the risk pool, and to whether the unsubsidised segment of the market prices
stably.

## Policy status

Read this before quoting anything. As of **13 September 2026**:

- The enhanced credits **expired 31 December 2025**; subsidies reverted to the
  original ACA schedule on 1 January 2026.
- On **8 January 2026** the House passed a three-year extension, 230–196, with
  17 Republicans in support.
- The **Senate had not acted**. A bipartisan *Consumer Affordability and
  Responsibility Enhancement (CARE) Act*, restoring the credits for two years
  with minimum premium payments and income caps, was reported to be in drafting.

The 2026 pricing is now fixed and a retroactive restoration would not undo it,
but it would change what the 2026 enrolment counterfactual means. Re-check the
legislative position before submission.

## Interactive calculator

**https://aca-subsidy-cliff.vercel.app**

Enter an age, a state and an income and see what the expiry did to your
premium, how far you are from the 400% cliff, and what crossing it would cost.
It runs the paper's own subsidy calculation in the browser on the CMS benchmark
premiums; nothing typed into it is sent anywhere.

Build it with `python/export_tool_data.py` then `python/build_tool.py`. The
export prints the reference values the page must reproduce, so a drift between
the paper and the tool shows up at build time.

## Status

In progress. Benchmark premiums and the subsidy calculator are built and
answer RQ1.

**Validated against what actually happened.** The 2026 open enrolment period
is now in: plan selections fell from 24.32 million to 23.13 million nationally,
−4.9%. The federal marketplace lost 7.9% while state-based exchanges *grew*
2.3%. Average premium after tax credit rose 57.5%, from $113 to $178 a month.

The income gradient is the paper's thesis in one column: enrolment at
400–500% of poverty — the group that lost its credit entirely — fell **44.3%**,
while the 300–400% group just below the cliff *grew* 7.4%.

Calibrating the model to the observed federal-marketplace decline implies a
price semi-elasticity of **−0.08 to −0.11**, far below the −0.2 to −1.0 the
literature offers, and a first-year morbidity rise of only 0.8% to 4.1%.

**First result.** For a single 40-year-old at the median federal-marketplace
rating area, the annual net benchmark premium:

| Income | 2025 | 2026 | Change |
|---|---:|---:|---:|
| 150% FPL | $0 | $967 | new |
| 200% FPL | $602 | $2,038 | +238% |
| 300% FPL | $2,711 | $4,596 | +70% |
| 400% FPL | $5,120 | $6,129 | +20% |
| 401% FPL | $5,133 | $7,722 | +50% |

**The cliff.** At 401% of the poverty level one extra dollar of income now costs
**$1,593** in lost credit. In 2025 the same dollar cost $13.

The benchmark silver premium itself rose a median of **24.3%** for a 40-year-old
(interquartile range +17.5% to +32.8%), from −1.9% in Alaska to +69.1% in
Arkansas, where the number of silver plans fell from 21 to 17.

## Data

| Source | What | Access |
|---|---|---|
| CMS Exchange Rate PUF, 2025 and 2026 | Plan-level premiums by age and rating area | [download.cms.gov](https://download.cms.gov/marketplace-puf/2026/rate-puf.zip) — direct, no registration |
| CMS Plan Attributes PUF, 2025 and 2026 | Metal level, market, child-only flags | Same |
| MEPS FYC 2019–2024 | Individual expected-cost model | AHRQ, direct download (shared with Paper 3) |
| IRS applicable-percentage tables | Expected contribution by FPL | Revenue procedures |
| HHS poverty guidelines | FPL thresholds | aspe.hhs.gov |

```bash
cd data/raw/cms
for y in 2025 2026; do
  for f in rate-puf plan-attributes-puf; do
    curl -sSL -o "${y}_${f}.zip" "https://download.cms.gov/marketplace-puf/$y/$f.zip"
  done
done
for z in *.zip; do unzip -qo "$z" -d "${z%.zip}"; done
```

## A limitation to state up front

The Rate PUF covers the **31 states using HealthCare.gov**, 362 rating areas.
State-based exchanges — California, New York, Colorado and others — file their
own rates and are absent. Those states are disproportionately the ones with
their own subsidy programmes and reinsurance waivers, so the federal-marketplace
picture is not the national one, and the paper cannot speak to the states most
likely to have cushioned the change.

## Three details that decide the benchmark

The premium tax credit is defined against the second-lowest-cost silver plan, so
the whole paper rests on computing it correctly.

- Issuers file a large **sentinel rate** for age–plan combinations they do not
  sell. Screened before any ordering is taken.
- The benchmark is the **second** lowest silver premium, not the lowest; where
  only one silver plan is offered, that plan is the benchmark.
- **Child-only and SHOP plans** cannot be an adult's benchmark and are excluded
  through the Plan Attributes PUF.

## Reproducing

```bash
python3 -m venv .venv
.venv/bin/pip install numpy pandas scipy statsmodels matplotlib
.venv/bin/python python/benchmarks.py    # -> data/derived/benchmarks.csv
.venv/bin/python python/subsidy.py       # -> Table 1
```

## Author

Oluwatosin Dorcas Babalola — Georgia State University — obabalola4@student.gsu.edu

## Licence

Code is MIT-licensed. CMS public use files are in the public domain; MEPS is
governed by AHRQ's data-use agreement. Neither is redistributed here.
