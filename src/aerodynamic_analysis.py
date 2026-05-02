"""
aerodynamic_analysis.py
-----------------------
Aerodynamic performance analysis for a hybrid VTOL transition wing.

Computes lift and drag forces across an airspeed range for three NACA
airfoil profiles (0012, 2415, 4412) using simplified aerodynamic theory:
    L = 0.5 * rho * Cl * V^2 * S
    D = 0.5 * rho * Cd * V^2 * S

Inputs : data/Lift_Drag_data.csv
Outputs: results/aerodynamic_lift_drag.png
         results/aerodynamic_ld_ratio.png

Usage:
    python src/aerodynamic_analysis.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Constants ────────────────────────────────────────────────────────────────
RHO = 1.225          # Air density at sea level, kg/m^3
WING_AREA = 0.48     # Reference wing area, m^2
# Cl and Cd at cruise AoA = 4°, Re ≈ 500,000
# Source: NACA Technical Report 824 (Abbott & Von Doenhoff, 1959)
AIRFOIL_LABELS = {
    "NACA 0012": {"Cl": 0.430, "Cd": 0.0098, "color": "#378ADD"},
    "NACA 2415": {"Cl": 0.620, "Cd": 0.0112, "color": "#1D9E75"},
    "NACA 4412": {"Cl": 0.820, "Cd": 0.0148, "color": "#D85A30"},
}
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
DATA_PATH   = os.path.join(os.path.dirname(__file__), "..", "data", "Lift_Drag_data.csv")

# ── Functions ─────────────────────────────────────────────────────────────────

def calculate_lift(Cl, airspeed, rho=RHO, S=WING_AREA):
    """Return lift force in Newtons using thin-aerofoil theory."""
    return 0.5 * rho * Cl * airspeed**2 * S


def calculate_drag(Cd, airspeed, rho=RHO, S=WING_AREA):
    """Return drag force in Newtons."""
    return 0.5 * rho * Cd * airspeed**2 * S


def calculate_ld_ratio(Cl, Cd):
    """Return lift-to-drag ratio."""
    return Cl / Cd


def plot_lift_drag(airspeeds, results, output_path):
    """Plot lift and drag vs airspeed for all three airfoils."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(
        "Lift and Drag vs Airspeed — Hybrid VTOL Wing\n"
        "NACA 0012 | NACA 2415 | NACA 4412",
        fontsize=13, fontweight="bold"
    )

    for name, vals in results.items():
        color = AIRFOIL_LABELS[name]["color"]
        axes[0].plot(airspeeds, vals["lift"], label=name, color=color, linewidth=2)
        axes[1].plot(airspeeds, vals["drag"], label=name, color=color,
                     linewidth=2, linestyle="--")

    for ax, ylabel, title in zip(
        axes,
        ["Lift Force (N)", "Drag Force (N)"],
        ["Lift vs Airspeed", "Drag vs Airspeed"]
    ):
        ax.set_xlabel("Airspeed (m/s)", fontsize=11)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.set_title(title, fontsize=12)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


def plot_ld_ratio(results, output_path):
    """Bar chart of L/D ratio per airfoil — key cruise efficiency metric."""
    names  = list(results.keys())
    ratios = [calculate_ld_ratio(
                  AIRFOIL_LABELS[n]["Cl"],
                  AIRFOIL_LABELS[n]["Cd"]) for n in names]
    colors = [AIRFOIL_LABELS[n]["color"] for n in names]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(names, ratios, color=colors, width=0.5, edgecolor="white")
    ax.bar_label(bars, fmt="%.1f", padding=4, fontsize=11, fontweight="bold")
    ax.set_title("Lift-to-Drag Ratio by Airfoil Profile", fontsize=13, fontweight="bold")
    ax.set_ylabel("L/D Ratio", fontsize=11)
    ax.set_ylim(0, max(ratios) * 1.2)
    ax.grid(axis="y", alpha=0.3)
    ax.set_facecolor("#FAFAFA")
    fig.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # Load CSV — use for airspeed range
    data = pd.read_csv(DATA_PATH)
    airspeeds = np.linspace(
    float(data["Airspeed_ms"].min()),
    float(data["Airspeed_ms"].max()),
    100
)

    # Compute lift and drag for each airfoil profile
    results = {}
    for name, props in AIRFOIL_LABELS.items():
        lift = calculate_lift(props["Cl"], airspeeds)
        drag = calculate_drag(props["Cd"], airspeeds)
        results[name] = {"lift": lift, "drag": drag}
        ld = calculate_ld_ratio(props["Cl"], props["Cd"])
        print(f"{name}: Cl={props['Cl']:.2f}  Cd={props['Cd']:.3f}  "
              f"L/D={ld:.1f}  Peak lift @ {airspeeds[-1]:.0f} m/s = {lift[-1]:.1f} N")

    plot_lift_drag(airspeeds, results,
                   os.path.join(RESULTS_DIR, "aerodynamic_lift_drag.png"))
    plot_ld_ratio(results,
                  os.path.join(RESULTS_DIR, "aerodynamic_ld_ratio.png"))

    print("\nAerodynamic analysis complete.")
    print(f"Best cruise L/D: NACA 4412 @ "
          f"{calculate_ld_ratio(AIRFOIL_LABELS['NACA 4412']['Cl'], AIRFOIL_LABELS['NACA 4412']['Cd']):.1f}")


if __name__ == "__main__":
    main()
