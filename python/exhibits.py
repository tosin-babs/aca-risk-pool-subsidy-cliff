"""
Figures, in a plain journal style.

Everything is drawn from the CSVs the analysis wrote, so a figure cannot
disagree with the table it belongs to. The figures carry no "Figure N" label
of their own; the manuscript numbers them in reading order.
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import pandas as pd

import config

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.22, "grid.linewidth": 0.5,
    "axes.axisbelow": True, "figure.dpi": 110,
    "legend.frameon": False, "axes.titlesize": 10, "axes.titleweight": "bold",
})
P = config.PALETTE
T = config.TABLES


def _save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(config.FIGURES / f"{name}.{ext}", dpi=config.FIG_DPI,
                    bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {name}.png / .pdf")


def figure_cliff():
    """Net premium against income for a 40-year-old, both schedules."""
    net = pd.read_csv(config.DERIVED / "net_premiums.csv")
    n = net[net["age"] == 40]
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    for year, colour, label in ((2025, P["y2025"], "2025 schedule (enhanced)"),
                                (2026, P["y2026"], "2026 schedule (original)")):
        s = n[n["year"] == year].sort_values("fpl_pct")
        ax.plot(s["fpl_pct"], s["net_premium_median"], color=colour,
                linewidth=2.2, marker="o", markersize=3.5, label=label)
    s26 = n[n["year"] == 2026].sort_values("fpl_pct")
    lo = float(s26[s26["fpl_pct"] == 400]["net_premium_median"].iloc[0])
    hi = float(s26[s26["fpl_pct"] == 401]["net_premium_median"].iloc[0])
    ax.annotate("", xy=(401, hi), xytext=(400, lo),
                arrowprops=dict(arrowstyle="->", color=P["warn"], linewidth=1.8))
    ax.annotate(f"one dollar of income,\n${hi - lo:,.0f} of premium",
                xy=(402, (lo + hi) / 2), xytext=(430, (lo + hi) / 2),
                fontsize=8, color=P["warn"], va="center",
                arrowprops=dict(arrowstyle="-", color=P["warn"], linewidth=0.8))
    ax.axvline(400, color=P["rule"], linewidth=1.0, zorder=0)
    ax.set_xlabel("Household income (% of the federal poverty level)")
    ax.set_ylabel("Net annual premium for the benchmark plan ($)")
    ax.set_title("Net benchmark premium by income, single adult aged 40")
    ax.legend(loc="upper left")
    _save(fig, "fig_cliff")


def figure_who_left():
    """Change by income band, 2025-26 against the 2024-25 placebo."""
    t = pd.read_csv(T / "table14_segment_observed.csv")
    t = t[t["band"] != "group"]
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    y = np.arange(len(t))
    ax.barh(y - 0.19, t["change_2024_25_pct"], height=0.36, color=P["muted"],
            label="2024 to 2025 (enhanced schedule both years)")
    colours = [P["y2025"] if s else P["y2026"] for s in t["subsidised_in_2026"]]
    ax.barh(y + 0.19, t["change_pct"], height=0.36, color=colours,
            label="2025 to 2026")
    for i, v in enumerate(t["change_pct"]):
        ax.text(v + (0.8 if v >= 0 else -0.8), i + 0.19, f"{v:+.1f}%",
                va="center", ha="left" if v >= 0 else "right", fontsize=8)
    ax.set_yticks(y, t["segment"])
    ax.invert_yaxis()
    ax.axvline(0, color=P["ink"], linewidth=0.9)
    ax.set_xlabel("Change in plan selections (%)")
    ax.set_title("Plan selections by income band, 30 HealthCare.gov states")
    lo, hi = float(t["change_pct"].min()), float(t["change_2024_25_pct"].max())
    ax.set_xlim(lo * 1.25, hi * 2.2)
    handles = [plt.Rectangle((0, 0), 1, 1, color=P["muted"]),
               plt.Rectangle((0, 0), 1, 1, color=P["y2025"]),
               plt.Rectangle((0, 0), 1, 1, color=P["y2026"])]
    ax.legend(handles, ["2024 to 2025", "2025 to 2026, kept a credit",
                        "2025 to 2026, lost the credit"], loc="upper right",
              fontsize=8, bbox_to_anchor=(1.0, 0.72))
    _save(fig, "fig_who_left")


def figure_one_or_two():
    """Observed change by segment against the model with one response and
    with two."""
    t = pd.read_csv(T / "table10_calibration.csv")
    one = t[t["specification"].str.startswith("Primary") & (t["tilt"] == 1.5)].iloc[0]
    two = t[t["specification"].str.startswith("Two") & (t["tilt"] == 1.5)].iloc[0]
    labels = ["Observed", "One response\n(fits the total)",
              "Two responses\n(one per segment)"]
    above = [one["observed_change_above_400_pct"],
             one["model_change_above_400_pct"], two["model_change_above_400_pct"]]
    below = [one["observed_change_below_400_pct"],
             one["model_change_below_400_pct"], two["model_change_below_400_pct"]]
    fig, ax = plt.subplots(figsize=(7.0, 3.9))
    x = np.arange(3)
    ax.bar(x - 0.18, below, width=0.36, color=P["y2025"], label="Kept a credit (100-400% FPL)")
    ax.bar(x + 0.18, above, width=0.36, color=P["y2026"], label="Lost the credit (above 400%)")
    for xi, (b, a) in enumerate(zip(below, above)):
        ax.text(xi - 0.18, b - 1.2, f"{b:+.1f}%", ha="center", va="top", fontsize=8)
        ax.text(xi + 0.18, a - 1.2, f"{a:+.1f}%", ha="center", va="top", fontsize=8)
    ax.axhline(0, color=P["ink"], linewidth=0.9)
    ax.set_xticks(x, labels)
    ax.set_ylabel("Change in enrollment, 2025 to 2026 (%)")
    ax.set_ylim(min(above) * 1.25, 6)
    ax.set_title("A single price response cannot reproduce both segments")
    ax.legend(loc="lower left", fontsize=8)
    _save(fig, "fig_one_or_two")


def figure_age_gradient():
    """Rise in the household's own payment by age, three household types."""
    t = pd.read_csv(T / "table13_segment_dynamics.csv")
    t = t[t["response_multiple"] == 1]
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    styles = {"Subsidised, 250% FPL": P["y2025"],
              "Subsidised, 390% FPL": P["gain"],
              "Unsubsidised, 450% FPL": P["y2026"]}
    for seg, colour in styles.items():
        s = t[t["segment"] == seg].sort_values("age")
        ax.plot(s["age"], s["shock_dollars"], color=colour, linewidth=2.2,
                marker="o", markersize=4, label=seg.replace("Subsidised", "Subsidized")
                .replace("Unsubsidized", "Unsubsidized"))
    ax.yaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda v, _: f"${v:,.0f}"))
    ax.set_xlabel("Age of the enrollee")
    ax.set_ylabel("Rise in the household's own annual payment ($)")
    ax.set_title("The size of the shock depends on age above the threshold")
    ax.legend(loc="upper left")
    _save(fig, "fig_age_gradient")


def figure_bunching():
    """Selections either side of the threshold, with the counterfactual."""
    t14 = pd.read_csv(T / "table14_segment_observed.csv")
    t14 = t14[t14["band"] != "group"].reset_index(drop=True)
    t16 = pd.read_csv(T / "table16_bunching.csv")
    r = t16[t16["sample"].str.startswith("HealthCare")
            & (t16["control"] == "100-300% pooled")].iloc[0]
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    y = np.arange(len(t14))
    ax.barh(y - 0.19, t14["n_2025"] / 1e6, height=0.36, color=P["y2025"], label="2025")
    ax.barh(y + 0.19, t14["n_2026"] / 1e6, height=0.36, color=P["y2026"], label="2026")
    i = int(t14.index[t14["band"] == config.BELOW_NOTCH_BAND][0])
    cf = r["counterfactual_300_400"] / 1e6
    ax.plot([cf], [i + 0.19], marker="|", markersize=18, color=P["ink"], zorder=5)
    ax.annotate(f"counterfactual at the 100-300% rate: {cf:.2f}m\n"
                f"excess {r['excess'] / 1e3:,.0f}k "
                f"({r['excess_as_pct_of_400_500_loss']:.0f}% of the 400-500% loss)",
                xy=(cf, i + 0.19), xytext=(cf + 1.2, i + 1.0), fontsize=8,
                color=P["ink"],
                arrowprops=dict(arrowstyle="->", color=P["ink"], linewidth=0.9))
    ax.set_yticks(y, t14["segment"])
    ax.invert_yaxis()
    ax.set_xlabel("Plan selections (millions), 30 HealthCare.gov states")
    ax.set_title("Growth immediately below the threshold, loss immediately above")
    ax.legend(loc="lower right")
    _save(fig, "fig_bunching")


def figure_cross_state():
    """Exposed-segment change against burden: 2025-26 and the placebo."""
    j = pd.read_csv(T / "table17_cliff_vs_loss.csv")
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.1), sharex=True, sharey=True)
    x = j["gross_pct_income"].to_numpy(float)
    size = 12 + 130 * (j["exposed_25"] / j["exposed_25"].max())
    for ax, col, fit, title in (
            (axes[0], "exposed_change_placebo_pct", "fitted_exposed_placebo",
             "2024 to 2025 (no cliff in either year)"),
            (axes[1], "exposed_change_pct", "fitted_exposed",
             "2025 to 2026 (cliff restored)")):
        yv = j[col].to_numpy(float)
        ax.scatter(x, yv, s=size, color=P["y2026"], alpha=0.55, edgecolor="none")
        s = j.sort_values("gross_pct_income")
        ax.plot(s["gross_pct_income"], s[fit], color=P["ink"], linewidth=1.6)
        ax.axhline(0, color=P["rule"], linewidth=0.9)
        ax.set_title(title)
        ax.set_xlabel("Unsubsidized benchmark at age 60,\n% of income at 401% FPL")
        for _, r in j.iterrows():
            if r["StateCode"] in ("WV", "WY", "FL", "TX", "NH"):
                ax.annotate(r["StateCode"], (r["gross_pct_income"], r[col]),
                            fontsize=7, color=P["muted"], xytext=(4, 3),
                            textcoords="offset points")
    axes[0].set_ylabel("Change in plan selections above 400% FPL (%)")
    axes[1].annotate("marker area: size of the segment in 2025",
                     xy=(0.97, 0.05), xycoords="axes fraction", ha="right",
                     fontsize=8, color=P["muted"])
    fig.suptitle("Loss above 400% FPL against the burden of unsubsidized cover, "
                 "30 HealthCare.gov states", fontsize=10, fontweight="bold", y=1.0)
    _save(fig, "fig_cross_state")


def figure_cost_per_year():
    """Cost per person-year by band under full restoration, and by scenario."""
    t = pd.read_csv(T / "table21_policy_cost.csv")
    s = t[t["sample"].str.startswith("HealthCare") & (t["scenario"] == "full")]
    s = s[s["cost_per_person_year_gained"].notna()].sort_values(
        "cost_per_person_year_gained")
    fig, ax = plt.subplots(figsize=(7.4, 4.0))
    y = np.arange(len(s))
    colours = [P["y2026"] if b in config.EXPOSED_BANDS else P["y2025"] for b in s["band"]]
    ax.barh(y, s["cost_per_person_year_gained"] / 1e3, color=colours, height=0.62)
    ax.set_yticks(y, s["segment"])
    ax.invert_yaxis()
    for i, v in enumerate(s["cost_per_person_year_gained"]):
        ax.text(v / 1e3 + 0.7, i, f"${v:,.0f}", va="center", fontsize=8.5)
    ax.set_xlabel("Cost per additional person-year of coverage ($ thousands)")
    ax.set_title("Restoring the enhanced schedule: cost per person-year by income band")
    ax.set_xlim(0, s["cost_per_person_year_gained"].max() / 1e3 * 1.22)
    handles = [plt.Rectangle((0, 0), 1, 1, color=P["y2026"]),
               plt.Rectangle((0, 0), 1, 1, color=P["y2025"])]
    ax.legend(handles, ["lost the credit in 2026", "kept a credit"], loc="lower right")
    _save(fig, "fig_cost_per_year")


def main():
    print("=== figures ===")
    for f in (figure_cliff, figure_who_left, figure_one_or_two,
              figure_age_gradient, figure_bunching, figure_cross_state,
              figure_cost_per_year):
        try:
            f()
        except FileNotFoundError as e:
            print(f"  skipped {f.__name__}: {e.filename} not built yet")


if __name__ == "__main__":
    main()
