"""
wing_polar_analysis.py
----------------------
Full wing polar analysis for the hybrid VTOL platform.

Analyses the complete wing polar from LLT (Lifting Line Theory) results,
computing span efficiency, induced drag breakdown, and aerodynamic
performance across the full AoA envelope. Compares wing-level efficiency
against individual section polars to quantify 3D effects.

Physics:
    Induced drag    CDi = CL^2 / (pi * AR * e)
    Span efficiency e   = CDi_ideal / CDi_actual
    Oswald factor   e0  = CL^2 / (pi * AR * CD_induced)

Inputs : data/Hybrid_VTOL_Wing_Analysis.csv
Outputs: results/wing_polar_analysis.png

Usage:
    python src/wing_polar_analysis.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ── Constants ─────────────────────────────────────────────────────────────────
AR           = 6.0      # Wing aspect ratio
WING_AREA    = 0.48     # m²
CRUISE_AOA   = 4.0      # degrees
RESULTS_DIR  = os.path.join(os.path.dirname(__file__), "..", "results")
DATA_PATH    = os.path.join(os.path.dirname(__file__), "..", "data",
                            "Hybrid_VTOL_Wing_Analysis.csv")


# ── Functions ─────────────────────────────────────────────────────────────────

def induced_drag_ideal(CL, AR):
    """Ideal induced drag (elliptic distribution): CDi = CL² / (π·AR)"""
    return CL**2 / (np.pi * AR)


def oswald_efficiency(CL, CD_induced, AR):
    """
    Oswald span efficiency factor.
    e = CL² / (π · AR · CDi)
    """
    with np.errstate(divide="ignore", invalid="ignore"):
        e = np.where(CD_induced > 0,
                     CL**2 / (np.pi * AR * CD_induced),
                     np.nan)
    return e


def plot_wing_polar(df, output_path):
    """Four-panel wing polar analysis."""
    fig = plt.figure(figsize=(16, 10))
    fig.suptitle(
        "Full Wing Polar Analysis — Hybrid VTOL Wing (LLT)\n"
        f"AR = {AR}  ·  S = {WING_AREA} m²  ·  Span = 2.4 m  ·  "
        "NACA 0012/2415/4412 Spanwise",
        fontsize=12, fontweight="bold"
    )
    gs = gridspec.GridSpec(2, 2, wspace=0.32, hspace=0.38)

    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, 0])
    ax4 = fig.add_subplot(gs[1, 1])

    aoa = df["AoA_deg"].values
    CL  = df["CL_wing"].values
    CD  = df["CD_wing"].values
    LD  = CL / CD
    CDi_ideal  = induced_drag_ideal(CL, AR)
    e_oswald   = oswald_efficiency(CL, df["CL_induced"].values, AR)

    cruise_idx = np.argmin(np.abs(aoa - CRUISE_AOA))

    # ── Panel 1: Lift curve ───────────────────────────────────────────────
    ax1.plot(aoa, CL, color="#378ADD", linewidth=2.2)
    ax1.scatter(aoa[cruise_idx], CL[cruise_idx],
                color="#FF4444", s=80, zorder=5,
                label=f"Cruise: Cl={CL[cruise_idx]:.3f}")
    ax1.axvline(CRUISE_AOA, color="grey", linewidth=0.8, linestyle=":")
    ax1.set_xlabel("Angle of Attack (°)", fontsize=10)
    ax1.set_ylabel("Wing CL", fontsize=10)
    ax1.set_title("Wing Lift Curve", fontsize=11, fontweight="bold")
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.25)

    # ── Panel 2: Drag polar ───────────────────────────────────────────────
    ax2.plot(CD, CL, color="#1D9E75", linewidth=2.2, label="Wing polar (LLT)")
    ax2.plot(CDi_ideal, CL, color="#D85A30", linewidth=1.5,
             linestyle="--", label="Ideal elliptic CDi")
    ax2.scatter(CD[cruise_idx], CL[cruise_idx],
                color="#FF4444", s=80, zorder=5)
    ax2.set_xlabel("Wing CD", fontsize=10)
    ax2.set_ylabel("Wing CL", fontsize=10)
    ax2.set_title("Wing Drag Polar", fontsize=11, fontweight="bold")
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.25)

    # ── Panel 3: L/D vs AoA ──────────────────────────────────────────────
    ax3.plot(aoa, LD, color="#7F77DD", linewidth=2.2)
    ax3.scatter(aoa[cruise_idx], LD[cruise_idx],
                color="#FF4444", s=80, zorder=5,
                label=f"Cruise: L/D={LD[cruise_idx]:.1f}")
    ax3.axvline(CRUISE_AOA, color="grey", linewidth=0.8, linestyle=":")
    ax3.set_xlabel("Angle of Attack (°)", fontsize=10)
    ax3.set_ylabel("L/D Ratio", fontsize=10)
    ax3.set_title("Aerodynamic Efficiency (L/D)", fontsize=11, fontweight="bold")
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.25)

    # ── Panel 4: Oswald efficiency vs AoA ────────────────────────────────
    valid = ~np.isnan(e_oswald) & (aoa > 1)
    ax4.plot(aoa[valid], e_oswald[valid], color="#D85A30", linewidth=2.2)
    ax4.axhline(1.0, color="grey", linewidth=0.8, linestyle="--",
                label="Ideal elliptic (e=1)")
    ax4.set_xlabel("Angle of Attack (°)", fontsize=10)
    ax4.set_ylabel("Oswald Efficiency Factor  e", fontsize=10)
    ax4.set_title("Span Efficiency vs AoA", fontsize=11, fontweight="bold")
    ax4.set_ylim(0, 1.2)
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.25)

    for ax in [ax1, ax2, ax3, ax4]:
        ax.set_facecolor("#FAFAFA")

    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    df = pd.read_csv(DATA_PATH)

    cruise = df[df["AoA_deg"] == CRUISE_AOA].iloc[0]
    CL_cruise = cruise["CL_wing"]
    CD_cruise = cruise["CD_wing"]
    e_cruise  = cruise["Span_efficiency"]
    CDi_ideal = induced_drag_ideal(CL_cruise, AR)

    print("Wing Polar Analysis Results:")
    print(f"  Aspect ratio              : {AR}")
    print(f"  Wing area                 : {WING_AREA} m²")
    print(f"\n  Cruise point (AoA = {CRUISE_AOA}°):")
    print(f"    CL                      : {CL_cruise:.4f}")
    print(f"    CD (total)              : {CD_cruise:.5f}")
    print(f"    L/D                     : {CL_cruise/CD_cruise:.2f}")
    print(f"    Induced drag (ideal)    : {CDi_ideal:.5f}")
    print(f"    Span efficiency (e)     : {e_cruise:.3f}")
    print(f"    CDi penalty vs elliptic : "
          f"{(CD_cruise - CDi_ideal)/CDi_ideal*100:.1f}%")

    best_ld_idx = (df["CL_wing"] / df["CD_wing"]).idxmax()
    best = df.iloc[best_ld_idx]
    print(f"\n  Best L/D point:")
    print(f"    AoA                     : {best['AoA_deg']:.1f}°")
    print(f"    L/D                     : {best['CL_wing']/best['CD_wing']:.2f}")
    print(f"    CL                      : {best['CL_wing']:.4f}")

    plot_wing_polar(df, os.path.join(RESULTS_DIR, "wing_polar_analysis.png"))

    print("\nWing polar analysis complete.")


if __name__ == "__main__":
    main()