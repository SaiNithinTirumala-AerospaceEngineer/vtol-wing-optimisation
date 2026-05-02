"""
structural_analysis.py
----------------------
Structural load analysis of the hybrid VTOL wing spar under flight loads.

Computes bending stress, bending moment, and shear force distributions
along the wing span using Euler-Bernoulli beam theory:
    sigma = M * y / I
    M(x)  = F * x
    V(x)  = F  (constant for tip-loaded cantilever)

Inputs : data/Structural_Analysis_data.csv
Outputs: results/structural_stress_bending_shear.png
         results/structural_summary.png

Usage:
    python src/structural_analysis.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Constants ─────────────────────────────────────────────────────────────────
LOAD_FACTOR   = 2.5          # CS-25 manoeuvre load factor
GRAVITY       = 9.81         # m/s^2
RESULTS_DIR   = os.path.join(os.path.dirname(__file__), "..", "results")
DATA_PATH     = os.path.join(os.path.dirname(__file__), "..", "data",
                             "Structural_Analysis_data.csv")

# ── Functions ─────────────────────────────────────────────────────────────────

def calculate_stress(load, moment_of_inertia, distance_from_neutral_axis):
    """
    Bending stress via flexure formula: sigma = M*y / I
    Units: load [N], I [mm^4], y [mm] -> stress [MPa]
    """
    return (load / moment_of_inertia) * distance_from_neutral_axis


def calculate_bending_moment(load, distance):
    """Bending moment for a cantilever with tip load: M = F * x"""
    return load * distance


def calculate_shear_force(load):
    """Constant shear force along span for a tip-loaded cantilever."""
    return np.full_like(load, float(load.mean()), dtype=float)


def plot_distributions(data, stress, bending_moment, shear_force, output_path):
    """Three-panel distribution plot — the core structural output."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle(
        "Wing Structural Load Distributions — 2.5g Manoeuvre Condition",
        fontsize=13, fontweight="bold"
    )

    span = data["Distance"].values

    plots = [
        (stress,         "Bending Stress (MPa)",   "Stress Distribution",
         "#E24B4A", "//"),
        (bending_moment, "Bending Moment (N·m)",   "Bending Moment Distribution",
         "#378ADD", "\\\\"),
        (shear_force,    "Shear Force (N)",         "Shear Force Distribution",
         "#1D9E75", ""),
    ]

    for ax, (values, ylabel, title, color, hatch) in zip(axes, plots):
        ax.fill_between(span, values, alpha=0.25, color=color, hatch=hatch)
        ax.plot(span, values, color=color, linewidth=2)
        ax.set_xlabel("Spanwise Distance (m)", fontsize=10)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.grid(True, alpha=0.3)
        ax.annotate(
            f"Peak: {values.max():.1f}",
            xy=(span[values.argmax()], values.max()),
            xytext=(span[values.argmax()] + 0.3, values.max() * 0.9),
            fontsize=9, color=color,
            arrowprops=dict(arrowstyle="->", color=color, lw=1.2)
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    data = pd.read_csv(DATA_PATH)

    # Apply load factor to simulate manoeuvre condition
    data["Load"] = data["Load"] * LOAD_FACTOR

    stress         = calculate_stress(
                         data["Load"],
                         data["Moment_of_Inertia"],
                         data["Distance_from_Neutral_Axis"])
    bending_moment = calculate_bending_moment(data["Load"], data["Distance"])
    shear_force    = calculate_shear_force(data["Load"])

    print("Structural Analysis Results (2.5g manoeuvre load):")
    print(f"  Peak bending stress  : {stress.max():.2f} MPa")
    print(f"  Peak bending moment  : {bending_moment.max():.2f} N·m")
    print(f"  Peak shear force     : {shear_force.max():.2f} N")
    print(f"  Safety factor (Al 7075 Ftu=572MPa): {572 / stress.max():.2f}")

    plot_distributions(
        data, stress, bending_moment, shear_force,
        os.path.join(RESULTS_DIR, "structural_stress_bending_shear.png")
    )

    print("\nStructural analysis complete.")


if __name__ == "__main__":
    main()
