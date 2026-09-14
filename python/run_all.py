"""
Run the whole analysis, in order.

    .venv/bin/python python/run_all.py

Seeded from config.SEED. The MEPS load in costmodel.py and selection.py is the
slow step; everything downstream of the CMS files is fast.
"""

from __future__ import annotations

import importlib
import json
import platform
import time

import config

STEPS = [
    ("Benchmark premiums from the CMS Rate PUFs", "benchmarks"),
    ("Net premiums and the subsidy schedules", "subsidy"),
    ("The cliff by age and place", "cliff"),
    ("The non-group population", "population"),
    ("Cost structure of the private market", "costmodel"),
    ("What happened in the 2026 open enrolment", "validation"),
    ("Exit, morbidity and repricing, calibrated to 2026", "selection"),
    ("RQ3: the unsubsidised segment", "unsubsidised"),
    ("Placebo, difference-in-differences and reinsurance", "did"),
    ("RQ4: loss ratios and the MLR floor", "lossratio"),
    ("RQ5: cost per person-year of coverage", "policycost"),
    ("Figures", "exhibits"),
    ("Calculator payload", "export_tool_data"),
]


def main():
    started, timings = time.time(), []
    for title, module in STEPS:
        print("\n" + "=" * 78)
        print(title)
        print("=" * 78)
        t0 = time.time()
        importlib.import_module(module).main()
        dt = time.time() - t0
        timings.append({"step": title, "module": module, "seconds": round(dt, 1)})
        print(f"[{title}: {dt:.1f}s]")

    import numpy, pandas, scipy, statsmodels, matplotlib
    params = {k: v for k, v in vars(config).items()
              if k.isupper() and isinstance(v, (int, float, str, bool, tuple,
                                                list, dict, type(None)))}
    (config.ROOT / "output" / "params_used.json").write_text(json.dumps({
        "params": {k: (str(v) if isinstance(v, (tuple, list, dict)) else v)
                   for k, v in params.items()},
        "versions": {"python": platform.python_version(),
                     "numpy": numpy.__version__, "pandas": pandas.__version__,
                     "scipy": scipy.__version__,
                     "statsmodels": statsmodels.__version__,
                     "matplotlib": matplotlib.__version__},
        "timings": timings,
    }, indent=2, default=str))

    print("\n" + "=" * 78)
    print(f"Done in {time.time() - started:.0f}s. Tables in "
          f"{config.TABLES.relative_to(config.ROOT)}.")


if __name__ == "__main__":
    main()
