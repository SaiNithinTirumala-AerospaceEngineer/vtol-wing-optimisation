"""
airfoil_comparison.py
---------------------
Comparative polar analysis of NACA 0012, NACA 2415, and NACA 4412
airfoils for a hybrid VTOL transition wing.

Reads real XFoil polar data exported from XFLR5 v6.62 at Re = 500,000,
ISA sea-level conditions. Generates three-panel figure showing:
  1. Lift curve  — Cl vs angle of attack
  2. Drag polar  — Cl vs Cd
  3. Efficiency  — L/D ratio vs angle of attack

Inputs : data/xflr5_polar_naca0012.csv
         data/xflr5_polar_naca2415.csv
         data/xflr5_polar_naca4412.csv
Outputs: results/airfoil_polar_comparison.png
         results/airfoil_ld_bar.png

Usage:
    python src/airfoil_comparison.py
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ── Paths ─────────────────────────────────────────────────────────────────────
SRC_DIR     = os.path.dirname(__file__)
DATA_DIR    = os.path.join(SRC_DIR, "..", "data")
RESULTS_DIR = os.path.join(SRC_DIR, "..", "results")

# ── Airfoil metadata ──────────────────────────────────────────────────────────
AIRFOILS = {
    "NACA 0012": {
        "file":  "xflr5_polar_naca0012.csv",
        "color": "#378ADD",
        "ls":    "-",
        "role":  "Root — symmetric, VTOL hover stability",
    },
    "NACA 2415": {
        "file":  "xflr5_polar_naca2415.csv",
        "color": "#1D9E75",
        "ls":    "--",
        "role":  "Mid-span — cambered, cruise L/D balance",
    },
    "NACA 4412": {
        "file":  "xflr5_polar_naca4412.csv",
        "color": "#D85A30",
        "ls":    "-.",
        "role":  "Tip — high camber, low-speed lift augmentation",
    },
}

CRUISE_AOA = 4.0   # degrees


# ── Data loading ──────────────────────────────────────────────────────────────

def load_xflr5_polar(filepath):
    """
    Parse XFLR5 text-format polar export.
    Skips header lines until the data table begins.
    Returns arrays: aoa, Cl, Cd.
    """
    aoa, Cl, Cd = [], [], []
    in_data = False
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("-------"):
                in_data = True
                continue
            if in_data and line:
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        aoa.append(float(parts[0]))
                        Cl.append(float(parts[1]))
                        Cd.append(float(parts[2]))
                    except ValueError:
                        continue
    return np.array(aoa), np.array(Cl), np.array(Cd)


# ── Plot functions ────────────────────────────────────────────────────────────

def plot_polar_comparison(polars, cruise_aoa, output_path):
    """Three-panel comparison: lift curve, drag polar, L/D vs AoA."""
    fig = plt.figure(figsize=(16, 5.5))
    fig.suptitle(
        "NACA Airfoil Polar Comparison — Hybrid VTOL Transition Wing\n"
        "Re = 500,000  ·  ISA Sea Level  ·  Source: XFLR5 v6.62 XFoil analysis",
        fontsize=12, fontweight="bold", y=1.01
    )
    gs = gridspec.GridSpec(1, 3, wspace=0.35)
    ax_lift = fig.add_subplot(gs[0])
    ax_drag = fig.add_subplot(gs[1])
    ax_ld   = fig.add_subplot(gs[2])

    for name, p in polars.items():
        aoa, Cl, Cd = p["aoa"], p["Cl"], p["Cd"]
        ld = Cl / Cd

        cl_cruise = np.interp(cruise_aoa, aoa, Cl)
        cd_cruise = np.interp(cruise_aoa, aoa, Cd)
        ld_cruise = cl_cruise / cd_cruise

        ax_lift.plot(aoa, Cl, color=p["color"], ls=p["ls"],
                     linewidth=2.2, label=name)
        ax_lift.scatter(cruise_aoa, cl_cruise, color=p["color"], s=55, zorder=5)

        ax_drag.plot(Cd, Cl, color=p["color"], ls=p["ls"],
                     linewidth=2.2, label=name)
        ax_drag.scatter(cd_cruise, cl_cruise, color=p["color"], s=55, zorder=5)

        ax_ld.plot(aoa, ld, color=p["color"], ls=p["ls"],
                   linewidth=2.2, label=name)
        ax_ld.scatter(cruise_aoa, ld_cruise, color=p["color"], s=55, zorder=5)

    for ax in [ax_lift, ax_ld]:
        ax.axvline(cruise_aoa, color="grey", linewidth=0.8,
                   linestyle=":", alpha=0.7, label=f"Cruise AoA ({cruise_aoa:.0f}°)")

    _format_ax(ax_lift, "Angle of Attack (°)", "Lift Coefficient  Cl", "Lift Curve")
    _format_ax(ax_drag, "Drag Coefficient  Cd", "Lift Coefficient  Cl", "Drag Polar")
    _format_ax(ax_ld,   "Angle of Attack (°)", "L/D Ratio",             "Aerodynamic Efficiency")

    handles, labels = ax_lift.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4,
               fontsize=9.5, framealpha=0.9, bbox_to_anchor=(0.5, -0.08))
    fig.text(0.99, -0.04,
             "Data: XFLR5 v6.62 XFoil analysis — Re=500,000, Ncrit=9",
             ha="right", fontsize=8, color="grey", style="italic")

    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


def plot_ld_bar(polars, cruise_aoa, output_path):
    """Bar chart of L/D at cruise AoA."""
    names, ratios, colors = [], [], []
    for name, p in polars.items():
        cl = np.interp(cruise_aoa, p["aoa"], p["Cl"])
        cd = np.interp(cruise_aoa, p["aoa"], p["Cd"])
        names.append(name)
        ratios.append(cl / cd)
        colors.append(p["color"])

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(names, ratios, color=colors, width=0.45, edgecolor="white")
    ax.bar_label(bars, fmt="%.1f", padding=5, fontsize=12, fontweight="bold")

    for i, (name, p) in enumerate(polars.items()):
        ax.text(i, 2, p["role"], ha="center", va="bottom",
                fontsize=8, color="grey", style="italic")

    ax.set_title(
        f"Cruise L/D at AoA = {cruise_aoa:.0f}°  ·  Re = 500,000\n"
        "Source: XFLR5 v6.62 XFoil analysis",
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

    # Load real XFLR5 polar data
    polars = {}
    for name, meta in AIRFOILS.items():
        path = os.path.join(DATA_DIR, meta["file"])
        aoa, Cl, Cd = load_xflr5_polar(path)
        polars[name] = {**meta, "aoa": aoa, "Cl": Cl, "Cd": Cd}

    print(f"Airfoil polar comparison — XFLR5 data, Re=500,000")
    print(f"  Cruise AoA = {CRUISE_AOA}°\n")
    print(f"  {'Airfoil':<12} {'Cl':>6} {'Cd':>8} {'L/D':>7}  Role")
    print("  " + "─" * 60)
    for name, p in polars.items():
        cl = np.interp(CRUISE_AOA, p["aoa"], p["Cl"])
        cd = np.interp(CRUISE_AOA, p["aoa"], p["Cd"])
        print(f"  {name:<12} {cl:>6.4f} {cd:>8.5f} {cl/cd:>7.1f}  {p['role']}")

    print()
    plot_polar_comparison(
        polars, CRUISE_AOA,
        os.path.join(RESULTS_DIR, "airfoil_polar_comparison.png")
    )
    plot_ld_bar(
        polars, CRUISE_AOA,
        os.path.join(RESULTS_DIR, "airfoil_ld_bar.png")
    )
    print("\nDone. Embed results/airfoil_polar_comparison.png in README.md")


if __name__ == "__main__":
    main()