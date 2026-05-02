"""
structural_analysis.py
----------------------
Structural load analysis of the hybrid VTOL wing spar under flight loads.

Models the wing semi-span as a cantilever beam fixed at the root.
Distributed aerodynamic lift load decreases from root to tip (elliptic
approximation). Bending moment and shear force are integrated spanwise.
Bending stress is computed via the flexure formula at each station.

Physics:
    Shear force  V(x) = integral from x to b of w(s) ds
    Bending moment M(x) = integral from x to b of w(s)*(s-x) ds
    Bending stress sigma(x) = M(x) * y(x) / I(x)

Load case: 2.5g manoeuvre (CS-23 limit load factor for small aircraft)
Material:  Al 7075-T6  (Ftu = 572 MPa, Fty = 503 MPa)

Inputs : data/Structural_Analysis_data.csv
Outputs: results/structural_stress_bending_shear.png

Usage:
    python src/structural_analysis.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Constants ─────────────────────────────────────────────────────────────────
LOAD_FACTOR    = 2.5      # CS-23 manoeuvre limit load factor
GRAVITY        = 9.81     # m/s^2
FTU_AL7075     = 572.0    # Al 7075-T6 ultimate tensile strength, MPa
FTY_AL7075     = 503.0    # Al 7075-T6 yield strength, MPa
RESULTS_DIR    = os.path.join(os.path.dirname(__file__), "..", "results")
DATA_PATH      = os.path.join(os.path.dirname(__file__), "..", "data",
                              "Structural_Analysis_data.csv")


# ── Functions ─────────────────────────────────────────────────────────────────

def integrate_shear(span_m, load_Nm):
    """
    Shear force at each spanwise station by integrating load from tip inward.
    V(x) = sum of loads outboard of x * dx  (N)
    """
    n   = len(span_m)
    V   = np.zeros(n)
    dx  = np.gradient(span_m)
    for i in range(n - 2, -1, -1):
        V[i] = V[i + 1] + load_Nm[i + 1] * abs(dx[i + 1])
    return V * LOAD_FACTOR


def integrate_bending_moment(span_m, shear_N):
    """
    Bending moment by integrating shear force from tip inward.
    M(x) = sum of V * dx  (N·m)
    """
    n   = len(span_m)
    M   = np.zeros(n)
    dx  = np.gradient(span_m)
    for i in range(n - 2, -1, -1):
        M[i] = M[i + 1] + shear_N[i + 1] * abs(dx[i + 1])
    return M


def bending_stress(moment_Nm, I_mm4, y_mm):
    """
    Flexure formula: sigma = M * y / I
    M in N·m, I in mm^4, y in mm → sigma in MPa
    Note: 1 N·m = 1000 N·mm, so multiply M by 1000.
    """
    return (moment_Nm * 1000.0 * y_mm) / I_mm4


def plot_distributions(span, stress, shear, moment, output_path):
    """Three-panel spanwise distribution plot."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(
        "Wing Spar Structural Distributions — 2.5g Manoeuvre Load Case\n"
        "Al 7075-T6 Box Spar  ·  Semi-span = 1.2 m  ·  CS-23 Load Factor",
        fontsize=12, fontweight="bold"
    )

    datasets = [
        (stress,  "Bending Stress (MPa)",  "Bending Stress",         "#E24B4A", "//"),
        (moment,  "Bending Moment (N·m)",  "Bending Moment",         "#378ADD", "\\\\"),
        (shear,   "Shear Force (N)",        "Shear Force",            "#1D9E75", ""),
    ]

    for ax, (values, ylabel, title, color, hatch) in zip(axes, datasets):
        ax.fill_between(span, values, alpha=0.20, color=color, hatch=hatch)
        ax.plot(span, values, color=color, linewidth=2.2)
        ax.set_xlabel("Spanwise Position (m)", fontsize=10)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.grid(True, alpha=0.25)
        ax.set_facecolor("#FAFAFA")
        ax.invert_xaxis()   # root at right, tip at left — aero convention

        peak_idx = values.argmax()
        ax.annotate(
            f"Peak: {values[peak_idx]:.2f}",
            xy=(span[peak_idx], values[peak_idx]),
            xytext=(span[peak_idx] + 0.15, values[peak_idx] * 0.85),
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

    data   = pd.read_csv(DATA_PATH)
    span   = data["Spanwise_Station_m"].values
    w      = data["Distributed_Load_Nm"].values
    I      = data["Moment_of_Inertia_mm4"].values
    y      = data["Half_Depth_mm"].values

    shear  = integrate_shear(span, w)
    moment = integrate_bending_moment(span, shear)
    stress = bending_stress(moment, I, y)

    peak_stress = stress.max()
    peak_moment = moment.max()
    peak_shear  = shear.max()
    sf_ultimate = FTU_AL7075 / peak_stress
    sf_yield    = FTY_AL7075 / peak_stress

    print("Structural Analysis Results — 2.5g manoeuvre load case:")
    print(f"  Semi-span            : {span.max():.2f} m")
    print(f"  Peak shear force     : {peak_shear:.2f} N   (at root)")
    print(f"  Peak bending moment  : {peak_moment:.2f} N·m  (at root)")
    print(f"  Peak bending stress  : {peak_stress:.2f} MPa  (at root)")
    print(f"  Safety factor (Ftu)  : {sf_ultimate:.2f}  [CS-23 requires > 1.5]")
    print(f"  Safety factor (Fty)  : {sf_yield:.2f}  [yield margin]")

    if sf_ultimate >= 1.5:
        print("  → Spar PASSES ultimate load check")
    else:
        print("  → Spar FAILS ultimate load check — increase I or reduce y")

    plot_distributions(
        span, stress, shear, moment,
        os.path.join(RESULTS_DIR, "structural_stress_bending_shear.png")
    )

    print("\nStructural analysis complete.")


if __name__ == "__main__":
    main()