"""
Who leaves, what that does to the pool's expected cost, and whether one price
response can describe 2026.

The pool. MEPS adults aged 18-64 with private coverage and income at or above
100% of poverty carry the cost structure (costmodel.py shows the non-group
segment is not distinguishable from the rest of the private market once
observables are held constant). Their weights are raked to the 2025 open
enrollment age and income marginals of the HealthCare.gov states, the
platform the premium data describe. An earlier version post-stratified onto
MEPS's own non-group mix, which put 55% of the pool above 400% FPL against 7%
of actual plan selections.

Premiums. Each person is priced at the median benchmark for their own age in
each year. An earlier version priced everyone at the 40-year-old benchmark,
although the 3:1 age band applies to the gross premium and so decides the size
of the cliff.

Price response. The default metric is the rise in the household's own payment
for the benchmark, in percentage points of income; the response parameter is
the share exiting per point. It is defined for households that paid nothing in
2025, who are about 45% of plan selections. The proportional metric used
earlier (exit per unit proportional rise, with a rise from zero set by rule)
is kept as a sensitivity.

Selection tilt. Exit probability is divided by tilt**z, z being standardised
log expected cost, so at tilt > 1 lower-cost enrollees leave more readily.

Repricing. The benchmark is scaled by stayers' mean expected cost over the
baseline mean; net payments and exits are recomputed from the baseline pool
until the factor settles.

Writes Tables 7 (grid), 8 (who leaves) and 10 (calibration and sensitivity).
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

import config
import oep
from benchmarks import load_benchmarks, median_gross_by_age
from costmodel import band, fitted
from subsidy import applicable_pct, income_at

warnings.filterwarnings("ignore")

AGE_BANDS_OEP = [(17, 25, "Age_18_25"), (25, 34, "Age_26_34"),
                 (34, 44, "Age_35_44"), (44, 54, "Age_45_54"),
                 (54, 64, "Age_55_64")]
FPL_BANDS_OEP = [(99.999, 150, "FPL_100_150"), (150, 200, "FPL_150_200"),
                 (200, 250, "FPL_200_250"), (250, 300, "FPL_250_300"),
                 (300, 400, "FPL_300_400"), (400, 500, "FPL_400_500"),
                 (500, np.inf, "FPL_GT500")]


def rake(w, groups, targets, iters=200, tol=1e-10):
    """Iterative proportional fitting of weights onto several marginals."""
    w = w.copy()
    for _ in range(iters):
        worst = 0.0
        for g, t in zip(groups, targets):
            cur = pd.Series(w).groupby(g.to_numpy()).sum()
            cur = cur / cur.sum()
            f = (t / cur).reindex(cur.index).fillna(1.0)
            w = w * g.map(f).to_numpy(float)
            worst = max(worst, float((f - 1).abs().max()))
        if worst < tol:
            break
    return w


def build_pool(composition="oep", verbose=True):
    """The marketplace-like pool with expected cost.

    composition "oep"     raked to 2025 HealthCare.gov OEP age and income
    composition "nongroup" post-stratified to MEPS non-group age x income
                           (the earlier method, for sensitivity)
    """
    m, _, _ = fitted()
    p = m[m["age"].between(config.SEL_AGE_MIN, config.SEL_AGE_MAX)
          & (m["povlev"] >= 100)].copy()
    p["age_band_oep"] = band(p["age"], AGE_BANDS_OEP)
    p["fpl_band_oep"] = band(p["povlev"], FPL_BANDS_OEP)
    p = p[p["age_band_oep"].notna() & p["fpl_band_oep"].notna()].copy()
    w0 = p["weight"].to_numpy(float)

    if composition == "oep":
        states = oep.hcgov_states()
        age_t = oep.total(2025, states, config.OEP_AGE_COLS)
        fpl_t = oep.total(2025, states, config.OEP_BANDS)
        w = rake(w0, [p["age_band_oep"], p["fpl_band_oep"]],
                 [age_t / age_t.sum(), fpl_t / fpl_t.sum()])
    elif composition == "nongroup":
        key = p["age_band_oep"].astype(str) + "|" + p["fpl_band_oep"].astype(str)
        ng = pd.Series(w0).groupby(key.where(p["nongroup"] == 1).to_numpy()).sum()
        cur = pd.Series(w0).groupby(key.to_numpy()).sum()
        f = ((ng / ng.sum()) / (cur / cur.sum())).fillna(0.0)
        w = w0 * key.map(f).fillna(0.0).to_numpy(float)
    else:
        raise ValueError(composition)
    p["weight"] = w
    p["rake_factor"] = w / w0 * (w0.sum() / w.sum())
    p = p[p["weight"] > 0].copy()
    if verbose:
        print(f"Pool ({composition}): {len(p):,} person-years; weight factor "
              f"{p['rake_factor'].min():.2f} to {p['rake_factor'].max():.2f}; "
              f"share above 400% FPL "
              f"{100 * p.loc[p['povlev'] > 400, 'weight'].sum() / p['weight'].sum():.1f}%")
    return p


def expected_cost(pool, basis=None, blend=0.0):
    basis = basis or config.SEL_COST_BASIS
    if basis == "tweedie":
        return (1 - blend) * pool["pred_cost"].to_numpy(float) \
            + blend * pool["cost"].to_numpy(float)
    if basis == "cellmean":            # the earlier construction
        g = pool.groupby(["age_band_oep", "fpl_band_oep"], observed=True)
        cm = g.apply(lambda s: np.average(s["cost"], weights=s["weight"]))
        cell = pd.MultiIndex.from_frame(pool[["age_band_oep", "fpl_band_oep"]])
        cm = cm.reindex(cell).to_numpy(float)
        return (1 - blend) * cm + blend * pool["cost"].to_numpy(float)
    raise ValueError(basis)


class Market:
    """Everything about the pool that does not change with the parameters."""

    def __init__(self, pool, bench, cost, pricing="age"):
        self.w = pool["weight"].to_numpy(float)
        self.cost = cost
        self.fpl = pool["povlev"].to_numpy(float)
        self.age = pool["age"].to_numpy(int)
        g25, g26 = median_gross_by_age(bench, 2025), median_gross_by_age(bench, 2026)
        if pricing == "age40":
            self.gross25 = np.full(len(self.w), g25[40])
            self.gross26 = np.full(len(self.w), g26[40])
        else:
            self.gross25 = np.array([g25[a] for a in self.age])
            self.gross26 = np.array([g26[a] for a in self.age])
        self.inc25 = income_at(self.fpl, 2025)
        self.inc26 = income_at(self.fpl, 2026)
        uniq = np.unique(self.fpl)
        k25 = dict(zip(uniq, [applicable_pct(f, 2025) for f in uniq]))
        k26 = dict(zip(uniq, [applicable_pct(f, 2026) for f in uniq]))
        self.k25 = np.array([k25[f] for f in self.fpl])
        self.k26 = np.array([k26[f] for f in self.fpl])
        self.net25 = self.pay(self.gross25, self.k25, self.inc25)
        lc = np.log(np.maximum(cost, 1.0))
        mu = np.average(lc, weights=self.w)
        sd = np.sqrt(np.average((lc - mu) ** 2, weights=self.w))
        self.z = (lc - mu) / sd
        self.base_cost = np.average(cost, weights=self.w)
        self.exposed = self.fpl > 400

    @staticmethod
    def pay(gross, k, inc):
        """Payment after credit; NaN applicable percentage means no credit."""
        return np.where(np.isfinite(k), np.minimum(gross, inc * k), gross)

    def shock(self, net26, metric):
        if metric == "pp_income":
            return np.maximum(100 * (net26 / self.inc26 - self.net25 / self.inc25), 0)
        rise = np.where(self.net25 > 0,
                        net26 / np.maximum(self.net25, 1.0) - 1.0,
                        np.where(net26 > 0, config.SEL_ZERO_BASE_RISE, 0.0))
        return np.clip(rise, 0, 5)

    def simulate(self, response, tilt, metric=None):
        metric = metric or config.SEL_RESPONSE_METRIC
        tilt_div = tilt ** self.z
        factor, hist = 1.0, []
        for rnd in range(config.SEL_MAX_ROUNDS):
            net26 = self.pay(self.gross26 * factor, self.k26, self.inc26)
            p_exit = np.clip(response * self.shock(net26, metric) / tilt_div,
                             0, 0.95)
            w1 = self.w * (1 - p_exit)
            new_factor = np.average(self.cost, weights=w1) / self.base_cost
            hist.append(new_factor)
            done = abs(new_factor - factor) < 1e-5
            factor = new_factor
            if done or factor > config.SEL_SPIRAL_THRESHOLD:
                break
        ex, sub = self.exposed, ~self.exposed
        return {
            "retention_pct": 100 * w1.sum() / self.w.sum(),
            "morbidity_rise_pct": 100 * (factor - 1),
            "rounds": len(hist),
            "spiral": bool(factor > config.SEL_SPIRAL_THRESHOLD),
            "retention_above_400_pct": 100 * w1[ex].sum() / self.w[ex].sum(),
            "retention_below_400_pct": 100 * w1[sub].sum() / self.w[sub].sum(),
            "p_exit": p_exit, "net26": net26,
        }

    def calibrate(self, target, tilt, metric=None):
        lo, hi = 0.0, 1.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if self.simulate(mid, tilt, metric)["retention_pct"] / 100 > target:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    def calibrate_segments(self, target_above, target_below, tilt, metric=None):
        """One response for households above 400% FPL and another below,
        solved jointly so that each segment's retention matches."""
        ra, rb = 0.02, 0.02
        for _ in range(30):
            for seg in ("above", "below"):
                lo, hi = 0.0, 2.0
                for _ in range(40):
                    mid = (lo + hi) / 2
                    resp = np.where(self.exposed, mid if seg == "above" else ra,
                                    mid if seg == "below" else rb)
                    r = self.simulate(resp, tilt, metric)
                    got = (r["retention_above_400_pct"] if seg == "above"
                           else r["retention_below_400_pct"]) / 100
                    tgt = target_above if seg == "above" else target_below
                    if got > tgt:
                        lo = mid
                    else:
                        hi = mid
                if seg == "above":
                    ra = (lo + hi) / 2
                else:
                    rb = (lo + hi) / 2
        resp = np.where(self.exposed, ra, rb)
        return ra, rb, self.simulate(resp, tilt, metric)


def target_retention():
    """2026 over 2025 selections in the income bands the pool represents,
    HealthCare.gov states of 2026."""
    s = oep.hcgov_states()
    a = oep.total(2025, s, config.OEP_BANDS).sum()
    b = oep.total(2026, s, config.OEP_BANDS).sum()
    ex = list(config.EXPOSED_BANDS)
    sub = [c for c in config.OEP_BANDS if c not in ex]
    obs_ex = oep.total(2026, s, ex).sum() / oep.total(2025, s, ex).sum()
    obs_sub = oep.total(2026, s, sub).sum() / oep.total(2025, s, sub).sum()
    return b / a, obs_ex, obs_sub


def main():
    bench = load_benchmarks(states=oep.hcgov_states())
    pool = build_pool("oep")
    metric = config.SEL_RESPONSE_METRIC
    mk = Market(pool, bench, expected_cost(pool))
    target, obs_ex, obs_sub = target_retention()
    print(f"Target retention, HealthCare.gov bands 100%+: {100 * target:.2f}% "
          f"(above 400%: {100 * obs_ex:.1f}%, below: {100 * obs_sub:.1f}%)")

    # ---- Table 7: the grid -------------------------------------------------
    rows = []
    for e in config.SEL_RESPONSE_GRID[metric]:
        for t in config.SEL_TILTS:
            r = mk.simulate(e, t)
            rows.append({"metric": metric, "response": e, "tilt": t,
                         **{k: v for k, v in r.items()
                            if k not in ("p_exit", "net26")}})
    t7 = pd.DataFrame(rows)
    t7.to_csv(config.TABLES / "table7_selection.csv", index=False)
    print("\n=== Grid ===")
    print(t7[["response", "tilt", "retention_pct", "morbidity_rise_pct",
              "retention_above_400_pct", "retention_below_400_pct",
              "rounds"]].round(2).to_string(index=False))

    # ---- Table 10: calibration, primary and sensitivity --------------------
    specs = [("Primary: raked to OEP, own-age benchmark, Tweedie cost",
              dict(composition="oep", pricing="age", basis="tweedie",
                   blend=0.0, metric=metric))]
    for bw in config.SEL_COST_BLEND_SENSITIVITY:
        specs.append((f"Cost {int(100 * (1 - bw))}/{int(100 * bw)} blend of "
                      f"prediction and realised cost",
                      dict(composition="oep", pricing="age", basis="tweedie",
                           blend=bw, metric=metric)))
    other = "proportional" if metric == "pp_income" else "pp_income"
    specs += [
        ("Proportional price metric",
         dict(composition="oep", pricing="age", basis="tweedie", blend=0.0,
              metric=other)),
        ("Everyone priced at the age-40 benchmark",
         dict(composition="oep", pricing="age40", basis="tweedie", blend=0.0,
              metric=metric)),
        ("Earlier specification: MEPS non-group mix, age-40 benchmark, "
         "50/50 cell-mean blend, proportional metric",
         dict(composition="nongroup", pricing="age40", basis="cellmean",
              blend=0.5, metric="proportional")),
    ]
    pools = {"oep": pool}
    rows = []
    for label, s in specs:
        if s["composition"] not in pools:
            pools[s["composition"]] = build_pool(s["composition"])
        pl = pools[s["composition"]]
        m_ = Market(pl, bench, expected_cost(pl, s["basis"], s["blend"]),
                    pricing=s["pricing"])
        for t in config.SEL_TILTS:
            e = m_.calibrate(target, t, s["metric"])
            r = m_.simulate(e, t, s["metric"])
            rows.append({"specification": label, "metric": s["metric"],
                         "tilt": t, "calibrated_response": e,
                         "retention_pct": r["retention_pct"],
                         "morbidity_rise_pct": r["morbidity_rise_pct"],
                         "model_change_above_400_pct":
                             r["retention_above_400_pct"] - 100,
                         "model_change_below_400_pct":
                             r["retention_below_400_pct"] - 100,
                         "observed_change_above_400_pct": 100 * (obs_ex - 1),
                         "observed_change_below_400_pct": 100 * (obs_sub - 1),
                         "rounds": r["rounds"]})
    # Two responses, one per segment, fitted to both observed moments.
    for t in config.SEL_TILTS:
        ra, rb, r = mk.calibrate_segments(obs_ex, obs_sub, t)
        rows.append({"specification": "Two responses: above and below 400% FPL",
                     "metric": metric, "tilt": t,
                     "calibrated_response": rb,
                     "calibrated_response_above_400": ra,
                     "response_ratio_above_to_below": ra / rb,
                     "retention_pct": r["retention_pct"],
                     "morbidity_rise_pct": r["morbidity_rise_pct"],
                     "model_change_above_400_pct": r["retention_above_400_pct"] - 100,
                     "model_change_below_400_pct": r["retention_below_400_pct"] - 100,
                     "observed_change_above_400_pct": 100 * (obs_ex - 1),
                     "observed_change_below_400_pct": 100 * (obs_sub - 1),
                     "rounds": r["rounds"]})
    t10 = pd.DataFrame(rows)
    t10.to_csv(config.TABLES / "table10_calibration.csv", index=False)
    print("\n=== Calibration ===")
    print(t10.drop(columns=["specification"]).round(3).to_string(index=False))
    print("  specs:", *[f"\n   {i}: {s[0]}" for i, s in enumerate(specs)])

    # ---- Table 8: who leaves at the calibrated primary, tilt 1.5 ------------
    t_ill = 1.5
    e_ill = float(t10[(t10["specification"] == specs[0][0])
                      & (t10["tilt"] == t_ill)]["calibrated_response"].iloc[0])
    r = mk.simulate(e_ill, t_ill)
    p_exit = r["p_exit"]
    pool = pool.assign(p_exit=p_exit, net25=mk.net25, net26=r["net26"],
                       exp_cost=mk.cost, exit_weight=mk.w * p_exit)
    rows = []
    for col in ("fpl_band_oep", "age_band_oep", None):
        groups = pool.groupby(col, observed=True) if col else [("All", pool)]
        for g, s in groups:
            sw = s["weight"]
            rows.append({
                "dimension": {"fpl_band_oep": "Income", "age_band_oep": "Age",
                              None: "All"}[col],
                "group": str(g), "response": e_ill, "tilt": t_ill,
                "share_of_pool_pct": 100 * sw.sum() / mk.w.sum(),
                "mean_net_2025": np.average(s["net25"], weights=sw),
                "mean_net_2026": np.average(s["net26"], weights=sw),
                "exit_rate_pct": 100 * np.average(s["p_exit"], weights=sw),
                "mean_cost_of_leavers":
                    np.average(s["exp_cost"], weights=s["exit_weight"])
                    if s["exit_weight"].sum() > 0 else np.nan,
                "mean_cost_of_stayers":
                    np.average(s["exp_cost"], weights=sw * (1 - s["p_exit"])),
            })
    t8 = pd.DataFrame(rows)
    t8["leaver_cost_discount_pct"] = 100 * (1 - t8["mean_cost_of_leavers"]
                                            / t8["mean_cost_of_stayers"])
    t8.to_csv(config.TABLES / "table8_who_leaves.csv", index=False)
    print("\n=== Who leaves (calibrated primary, tilt 1.5) ===")
    print(t8.round(2).to_string(index=False))
    print("\nwrote tables 7, 8 and 10")


if __name__ == "__main__":
    main()
