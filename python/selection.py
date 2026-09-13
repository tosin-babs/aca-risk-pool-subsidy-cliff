"""
Who leaves, and what that does to the cost of everyone who stays.

The mechanism the paper is about. A premium rise makes some people drop
coverage. The people who drop are not a random sample: coverage is worth less
to someone who expects to use little care, so the price-sensitive leavers are
disproportionately the cheap ones. Their departure raises the average cost of
the pool that remains, which raises next year's premium, which prompts more
exits. Whether that converges or runs away is the question.

Three components, each a lever:

  price response   a semi-elasticity of enrolment with respect to the net
                   premium the enrollee actually pays. The literature for the
                   individual market clusters between -0.2 and -1.0; CBO has
                   used values near the middle of that. Reported across the
                   range because the answer is sensitive to it.

  selection tilt   how much more likely a low-cost person is to leave than a
                   high-cost one facing the same price change. Expressed as
                   the ratio of exit odds per standard deviation of predicted
                   log cost. A tilt of 1 is random exit and is reported as the
                   floor case.

  iteration        the insurer reprices to the new pool, which prompts more
                   exit. Run to convergence or to a declared spiral.

The population is the MEPS under-65 privately insured sample reweighted to the
subsidised and unsubsidised shares of marketplace enrolment, with expected cost
from costmodel.py. Levels are not from MEPS; the pool's starting average cost
is calibrated so that the baseline premium equals the observed 2025 benchmark.

Writes Tables 7 and 8.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

import config
from costmodel import AGE_BANDS, FPL_BANDS, band, load
from subsidy import applicable_pct, income_at

warnings.filterwarnings("ignore")

ELASTICITIES = (-0.2, -0.4, -0.6, -1.0)
TILTS = (1.0, 1.5, 2.0)
MAX_ROUNDS = 25
SPIRAL_THRESHOLD = 3.0      # premium tripling is called a spiral, not a level


def build_pool(verbose=True):
    """The individual market: private-market cost structure, non-group mix.

    costmodel.py establishes that non-group members are not distinguishable
    from the rest of the private market on cost once age, income, sex, region
    and health are controlled for, so the large sample carries the cost
    structure. It does not carry the *composition*: the individual market is
    older and poorer than employer coverage, and applying a marketplace
    subsidy schedule to a population that mostly has employer coverage would
    answer a question nobody asked.

    So the large sample is post-stratified onto the non-group age-by-income
    distribution. Cell means come from tens of thousands of observations; only
    the cell weights come from the thin non-group sample.

    [VERIFY] These marginals should be replaced by the CMS Open Enrolment
    Period distribution when that file is in hand. MEPS undercounts the
    marketplace by about four to one, and if the undercount is selective
    within cells the composition inherits that.
    """
    d = load()
    m = d[(d["age"].between(18, 64)) & (d["inscov"] == 1)
          & (d["weight"] > 0) & (d["povlev"] > 0)].copy()
    m["age_band"] = band(m["age"], AGE_BANDS)
    m["fpl_band"] = band(m["povlev"], FPL_BANDS)
    m = m[m["age_band"].notna() & m["fpl_band"].notna()].copy()
    m["cost"] = m["cost"].clip(lower=0)

    ng = m[m["nongroup"] == 1]
    target = (ng.groupby(["age_band", "fpl_band"], observed=True)["weight"]
              .sum())
    target = target / target.sum()
    current = (m.groupby(["age_band", "fpl_band"], observed=True)["weight"]
               .sum())
    current = current / current.sum()
    factor = (target / current).replace([np.inf, -np.inf], np.nan).fillna(0.0)

    key = list(zip(m["age_band"], m["fpl_band"]))
    m["poststrat"] = [factor.get(k, 0.0) for k in key]
    m["weight"] = m["weight"] * m["poststrat"]
    m = m[m["weight"] > 0].copy()

    if verbose:
        print("Post-stratified the private-market sample onto the non-group "
              "age-by-income mix.")
        print(f"  cells with no non-group support, dropped: "
              f"{int((factor == 0).sum())} of {len(factor)}")
        print(f"  reweighting factor: {m['poststrat'].min():.2f} to "
              f"{m['poststrat'].max():.2f}")

    # Predicted cost: the group mean is enough here, because what drives the
    # result is the *ordering* of expected cost, not a precise level.
    grp = m.groupby(["age_band", "fpl_band"], observed=True)
    m["pred_cost"] = grp["cost"].transform(
        lambda s: np.average(s, weights=m.loc[s.index, "weight"]))
    # Within-cell variation matters too: community rating cannot price it, so
    # it is part of what a healthy leaver walks away from.
    m["pred_cost"] = 0.5 * m["pred_cost"] + 0.5 * m["cost"]
    return m


def net_premium_for(row, bench_annual, year):
    """What this person pays after any credit, at their income."""
    fpl = row["povlev"]
    pct = applicable_pct(fpl, year)
    income = income_at(fpl, year)
    if pct is None or (isinstance(pct, float) and np.isnan(pct)):
        return bench_annual
    return min(bench_annual, income * pct)


def simulate(pool, bench25, bench26, elasticity, tilt,
             max_rounds=MAX_ROUNDS):
    """Iterate exit and repricing until the pool's average cost settles."""
    w = pool["weight"].to_numpy(float).copy()
    cost = pool["pred_cost"].to_numpy(float)
    fpl = pool["povlev"].to_numpy(float)

    # Selection tilt on predicted cost, as in Paper 2's take-up model.
    z = np.log(np.maximum(cost, 1.0))
    z = (z - z.mean()) / (z.std() if z.std() > 0 else 1.0)
    stay_odds = np.exp(np.log(tilt) * z) if tilt > 1 else np.ones_like(z)

    base_cost = np.average(cost, weights=w)
    premium_factor = 1.0
    history = []

    net25 = np.array([min(bench25, income_at(f, 2025) * (applicable_pct(f, 2025) or 0))
                      if applicable_pct(f, 2025) is not None else bench25
                      for f in fpl])

    for rnd in range(max_rounds):
        bench = bench26 * premium_factor
        net26 = np.array([
            bench if applicable_pct(f, 2026) is None
            else min(bench, income_at(f, 2026) * applicable_pct(f, 2026))
            for f in fpl])

        # Proportional rise in what the enrollee pays, floored at zero.
        rise = np.where(net25 > 0, net26 / np.maximum(net25, 1.0) - 1.0,
                        np.where(net26 > 0, 1.0, 0.0))
        rise = np.clip(rise, 0, 5)

        # Exit share from the semi-elasticity, tilted toward the cheap.
        p_exit = np.clip(-elasticity * rise, 0, 0.95)
        p_exit = np.clip(p_exit / np.maximum(stay_odds, 1e-6), 0, 0.95)

        w_new = w * (1 - p_exit)
        if w_new.sum() <= 0:
            break
        new_cost = np.average(cost, weights=w_new)
        new_factor = new_cost / base_cost

        history.append({"round": rnd, "enrolment_index": w_new.sum() / w.sum(),
                        "mean_cost": new_cost,
                        "premium_factor": new_factor})

        if abs(new_factor - premium_factor) < 1e-4:
            premium_factor = new_factor
            break
        if new_factor > SPIRAL_THRESHOLD:
            premium_factor = new_factor
            break
        premium_factor = new_factor

    final = history[-1] if history else {
        "enrolment_index": 1.0, "mean_cost": base_cost, "premium_factor": 1.0}
    return {
        "baseline_mean_cost": base_cost,
        "final_mean_cost": final["mean_cost"],
        "morbidity_rise_pct": 100 * (final["mean_cost"] / base_cost - 1),
        "enrolment_retained_pct": 100 * final["enrolment_index"],
        "premium_factor": final["premium_factor"],
        "rounds": len(history),
        "spiral": bool(final["premium_factor"] > SPIRAL_THRESHOLD),
    }


def main():
    pool = build_pool()
    bench = pd.read_csv(config.DERIVED / "benchmarks.csv")
    b40 = bench[bench["age"] == 40]
    bench25 = float(b40[b40["year"] == 2025]["slcsp"].median()) * 12
    bench26 = float(b40[b40["year"] == 2026]["slcsp"].median()) * 12

    print(f"\nPool: {len(pool):,} person-years carrying the cost structure, "
          f"reweighted\n  to the individual market's composition. "
          f"Enrolment levels are indexed, not\n  absolute: MEPS cannot supply "
          f"the headcount and CMS does.")
    print(f"Benchmark, age 40, national median: ${bench25:,.0f} (2025) -> "
          f"${bench26:,.0f} (2026)\n")

    rows = []
    for e in ELASTICITIES:
        for t in TILTS:
            r = simulate(pool, bench25, bench26, e, t)
            r.update(elasticity=e, tilt=t)
            rows.append(r)
    t7 = pd.DataFrame(rows)
    t7.to_csv(config.TABLES / "table7_selection.csv", index=False)

    print("=== Exit, morbidity and repricing ===")
    print(f"  {'elast':>6} {'tilt':>5} {'enrolment kept':>15} "
          f"{'morbidity rise':>15} {'premium factor':>15} {'rounds':>7}")
    for _, r in t7.iterrows():
        flag = "  SPIRAL" if r["spiral"] else ""
        print(f"  {r['elasticity']:>6.1f} {r['tilt']:>5.1f} "
              f"{r['enrolment_retained_pct']:>14.1f}% "
              f"{r['morbidity_rise_pct']:>14.1f}% "
              f"{r['premium_factor']:>15.3f} {int(r['rounds']):>7}{flag}")

    # ---- Table 8: who leaves --------------------------------------------
    e, t = -0.4, 1.5
    w = pool["weight"].to_numpy(float)
    cost = pool["pred_cost"].to_numpy(float)
    fpl = pool["povlev"].to_numpy(float)
    z = np.log(np.maximum(cost, 1.0)); z = (z - z.mean()) / z.std()
    stay = np.exp(np.log(t) * z)
    net25 = np.array([bench25 if applicable_pct(f, 2025) is None
                      else min(bench25, income_at(f, 2025) * applicable_pct(f, 2025))
                      for f in fpl])
    net26 = np.array([bench26 if applicable_pct(f, 2026) is None
                      else min(bench26, income_at(f, 2026) * applicable_pct(f, 2026))
                      for f in fpl])
    rise = np.clip(np.where(net25 > 0, net26 / np.maximum(net25, 1) - 1, 1), 0, 5)
    p_exit = np.clip(np.clip(-e * rise, 0, .95) / np.maximum(stay, 1e-6), 0, .95)

    pool = pool.assign(p_exit=p_exit, net25=net25, net26=net26,
                       exit_weight=w * p_exit)
    rows = []
    for col in ("fpl_band", "age_band"):
        for g, s in pool.groupby(col, observed=True):
            rows.append({
                "dimension": col, "group": str(g),
                "share_of_pool_pct": 100 * s["weight"].sum() / w.sum(),
                "mean_net_2025": np.average(s["net25"], weights=s["weight"]),
                "mean_net_2026": np.average(s["net26"], weights=s["weight"]),
                "exit_rate_pct": 100 * np.average(s["p_exit"],
                                                  weights=s["weight"]),
                "mean_cost_of_leavers":
                    (np.average(s["pred_cost"], weights=s["exit_weight"])
                     if s["exit_weight"].sum() > 0 else np.nan),
                "mean_cost_of_stayers":
                    np.average(s["pred_cost"],
                               weights=s["weight"] * (1 - s["p_exit"])),
            })
    t8 = pd.DataFrame(rows)
    t8.to_csv(config.TABLES / "table8_who_leaves.csv", index=False)

    print(f"\n=== Who leaves, at elasticity {e} and tilt {t} ===")
    for dim in ("fpl_band", "age_band"):
        print(f"\n  {'group':<10} {'share':>7} {'net 25':>9} {'net 26':>9} "
              f"{'exit':>7} {'cost, leavers':>14} {'cost, stayers':>14}")
        for _, r in t8[t8["dimension"] == dim].iterrows():
            print(f"  {r['group']:<10} {r['share_of_pool_pct']:>6.1f}% "
                  f"${r['mean_net_2025']:>8,.0f} ${r['mean_net_2026']:>8,.0f} "
                  f"{r['exit_rate_pct']:>6.1f}% "
                  f"${r['mean_cost_of_leavers']:>13,.0f} "
                  f"${r['mean_cost_of_stayers']:>13,.0f}")

    lv = np.average(pool["pred_cost"], weights=pool["exit_weight"])
    sv = np.average(pool["pred_cost"], weights=w * (1 - p_exit))
    print(f"\n  Leavers cost ${lv:,.0f} on average; stayers ${sv:,.0f}. "
          f"Leavers are\n  {100 * (1 - lv / sv):.0f}% cheaper than the people "
          f"they leave behind, which is\n  what moves the pool average.")
    print(f"\nwrote tables 7 and 8")


if __name__ == "__main__":
    main()
