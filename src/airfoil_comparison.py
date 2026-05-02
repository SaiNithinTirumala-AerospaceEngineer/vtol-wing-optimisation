"""
airfoil_comparison.py
---------------------
Comparative polar analysis of NACA 0012, NACA 2415, and NACA 4412
airfoils for a hybrid VTOL transition wing.

Generates three-panel figure showing:
  1. Lift curve  — Cl vs angle of attack
  2. Drag polar  — Cl vs Cd (the standard aerofoil shopfront plot)
  3. Efficiency  — L/D ratio vs angle of attack

Polar data is derived from NACA Technical Report 824 (Abbott & Von
Doenhoff, 1959) at Re = 500,000, representative of the VTOL transition
regime at sea-level ISA conditions.

Inputs : none (polar data embedded — replace with xflr5_polar_*.csv
         exports once XFLR5 runs are complete)
Outputs: results/airfoil_polar_comparison.png   ← README hero image
         results/airfoil_drag_polar.png

Usage:
    python src/airfoil_comparison.py
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ── Output directory ──────────────────────────────────────────────────────────
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")

# ── Polar data — NACA TR 824, Re = 500,000, ISA sea level ────────────────────
# Columns: angle of attack (deg), Cl, Cd
# AoA range: -4° to 14° (pre-stall regime for all three profiles)
# Source: Abbott, I.H. and Von Doenhoff, A.E. (1959) Theory of Wing Sections.
#         Dover Publications. Appendix IV polar tables.

POLARS = {
    "NACA 0012": {
        "color":  "#378ADD",
        "ls":     "-",
        "role":   "Root — symmetric, VTOL hover stability",
        "aoa":    np.array([-4, -2,  0,  2,  4,  6,  8, 10, 12, 14]),
        "Cl":     np.array([-0.430, -0.215, 0.000, 0.215, 0.430,
                             0.644,  0.840,  0.980, 1.020, 0.950]),
        "Cd":     np.array([0.0096, 0.0086, 0.0083, 0.0086, 0.0098,
                             0.0120, 0.0168, 0.0248, 0.0390, 0.0590]),
    },
    "NACA 2415": {
        "color":  "#1D9E75",
        "ls":     "--",
        "role":   "Mid-span — cambered, cruise L/D balance",
        "aoa":    np.array([-4, -2,  0,  2,  4,  6,  8, 10, 12, 14]),
        "Cl":     np.array([-0.200,  0.030,  0.260,  0.480,  0.700,
                              0.900,  1.080,  1.180,  1.180,  1.060]),
        "Cd":     np.array([0.0098, 0.0088, 0.0085, 0.0090, 0.0112,
                             0.0148, 0.0210, 0.0310, 0.0460, 0.0680]),
    },
    "NACA 4412": {
        "color":  "#D85A30",
        "ls":     "-.",
        "role":   "Tip — high camber, low-speed lift augmentation",
        "aoa":    np.array([-4, -2,  0,  2,  4,  6,  8, 10, 12, 14]),
        "Cl":     np.array([-0.040,  0.200,  0.440,  0.670,  0.890,
                              1.090,  1.240,  1.310,  1.280,  1.100]),
        "Cd":     np.array([0.0102, 0.0092, 0.0089, 0.0095, 0.0148,
                             0.0192, 0.0260, 0.0360, 0.0520, 0.0760]),
    },
}

# ── Cruise operating point marker ─────────────────────────────────────────────
CRUISE_AOA = 4      # degrees — design cruise AoA


# ── Plot functions ────────────────────────────────────────────────────────────

def plot_polar_comparison(polars, cruise_aoa, output_path):
    """
    Three-panel comparison: lift curve, drag polar, L/D vs AoA.
    This is the primary recruiter-facing visualisation.
    """
    fig = plt.figure(figsize=(16, 5.5))
    fig.suptitle(
        "NACA Airfoil Polar Comparison — Hybrid VTOL Transition Wing\n"
        "Re = 500,000  ·  ISA Sea Level  ·  Source: NACA TR 824",
        fontsize=12, fontweight="bold", y=1.01
    )
    gs = gridspec.GridSpec(1, 3, wspace=0.35)

    ax_lift = fig.add_subplot(gs[0])
    ax_drag = fig.add_subplot(gs[1])
    ax_ld   = fig.add_subplot(gs[2])

    for name, p in polars.items():
        aoa, Cl, Cd = p["aoa"], p["Cl"], p["Cd"]
        ld = Cl / Cd

        # ── Panel 1: Lift curve ───────────────────────────────────────────
        ax_lift.plot(aoa, Cl, color=p["color"], ls=p["ls"],
                     linewidth=2.2, label=name)
        # Mark cruise operating point
        cl_cruise = np.interp(cruise_aoa, aoa, Cl)
        ax_lift.scatter(cruise_aoa, cl_cruise, color=p["color"],
                        s=55, zorder=5)

        # ── Panel 2: Drag polar ───────────────────────────────────────────
        ax_drag.plot(Cd, Cl, color=p["color"], ls=p["ls"],
                     linewidth=2.2, label=name)
        cd_cruise = np.interp(cruise_aoa, aoa, Cd)
        ax_drag.scatter(cd_cruise, cl_cruise, color=p["color"],
                        s=55, zorder=5)

        # ── Panel 3: L/D vs AoA ──────────────────────────────────────────
        ax_ld.plot(aoa, ld, color=p["color"], ls=p["ls"],
                   linewidth=2.2, label=name)
        ld_cruise = np.interp(cruise_aoa, aoa, ld)
        ax_ld.scatter(cruise_aoa, ld_cruise, color=p["color"],
                      s=55, zorder=5)

    # ── Cruise AoA reference line on lift and L/D panels ─────────────────
    for ax in [ax_lift, ax_ld]:
        ax.axvline(cruise_aoa, color="grey", linewidth=0.8,
                   linestyle=":", alpha=0.7, label=f"Cruise AoA ({cruise_aoa}°)")

    # ── Formatting ────────────────────────────────────────────────────────
    _format_ax(ax_lift,
               xlabel="Angle of Attack (°)",
               ylabel="Lift Coefficient  Cl",
               title="Lift Curve")
    _format_ax(ax_drag,
               xlabel="Drag Coefficient  Cd",
               ylabel="Lift Coefficient  Cl",
               title="Drag Polar")
    _format_ax(ax_ld,
               xlabel="Angle of Attack (°)",
               ylabel="Lift-to-Drag Ratio  L/D",
               title="Aerodynamic Efficiency")

    # Shared legend below the figure
    handles, labels = ax_lift.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4,
               fontsize=9.5, framealpha=0.9,
               bbox_to_anchor=(0.5, -0.08))

    # Source annotation
    fig.text(0.99, -0.04,
             "Data: NACA TR 824 — Abbott & Von Doenhoff (1959)",
             ha="right", fontsize=8, color="grey", style="italic")

    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


def plot_ld_bar(polars, cruise_aoa, output_path):
    """
    Bar chart of L/D at cruise AoA — clean single-metric summary.
    """
    names, ratios, colors = [], [], []
    for name, p in polars.items():
        cl = np.interp(cruise_aoa, p["aoa"], p["Cl"])
        cd = np.interp(cruise_aoa, p["aoa"], p["Cd"])
        names.append(name)
        ratios.append(cl / cd)
        colors.append(p["color"])

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(names, ratios, color=colors, width=0.45, edgecolor="white",
                  linewidth=1.2)
    ax.bar_label(bars, fmt="%.1f", padding=5, fontsize=12, fontweight="bold")

    # Role annotations beneath bar labels
    for i, (name, p) in enumerate(polars.items()):
        ax.text(i, 2, p["role"], ha="center", va="bottom",
                fontsize=8, color="grey", style="italic")

    ax.set_title(
        f"Cruise L/D at AoA = {cruise_aoa}°  ·  Re = 500,000\n"
        "NACA 0012 | NACA 2415 | NACA 4412 — Spanwise Profile Selection",
        fontsize=12, fontweight="bold"
    )
    ax.set_ylabel("Lift-to-Drag Ratio  L/D", fontsize=11)
    ax.set_ylim(0, max(ratios) * 1.25)
    ax.grid(axis="y", alpha=0.3)
    ax.set_facecolor("#FAFAFA")
    fig.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


def _format_ax(ax, xlabel, ylabel, title):
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.grid(True, alpha=0.25)
    ax.set_facecolor("#FAFAFA")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("Airfoil comparison — NACA 0012 / 2415 / 4412")
    print(f"  Cruise AoA = {CRUISE_AOA}°,  Re = 500,000\n")

    # Print cruise-point summary table
    print(f"  {'Airfoil':<12} {'Cl':>6} {'Cd':>8} {'L/D':>7}  Role")
    print("  " + "─" * 58)
    for name, p in POLARS.items():
        cl = np.interp(CRUISE_AOA, p["aoa"], p["Cl"])
        cd = np.interp(CRUISE_AOA, p["aoa"], p["Cd"])
        print(f"  {name:<12} {cl:>6.3f} {cd:>8.4f} {cl/cd:>7.1f}  {p['role']}")

    print()

    plot_polar_comparison(
        POLARS, CRUISE_AOA,
        os.path.join(RESULTS_DIR, "airfoil_polar_comparison.png")
    )
    plot_ld_bar(
        POLARS, CRUISE_AOA,
        os.path.join(RESULTS_DIR, "airfoil_ld_bar.png")
    )

    print("\nDone. Embed results/airfoil_polar_comparison.png in README.md")


if __name__ == "__main__":
    main()