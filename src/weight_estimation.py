"""
weight_estimation.py
--------------------
Wing mass breakdown estimation for the hybrid VTOL platform.

Estimates mass contributions from structural spar, skin, propulsion,
control surfaces, and avionics. Two spar materials compared:
  - Al 7075-T6  (density 2810 kg/m^3)
  - CFRP        (density 1600 kg/m^3)

Structural mass model (thin-walled box spar approximation):
    m_spar = rho_mat * b * c * t_skin * perimeter_factor
where b = semi-span, c = mean chord, t_skin = skin thickness.

Inputs : data/Weight_Analysis_data.csv
Outputs: results/weight_distribution.png
         results/weight_breakdown_pie.png

Usage:
    python src/weight_estimation.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Constants ─────────────────────────────────────────────────────────────────
GRAVITY       = 9.81
ASPECT_RATIO  = 6.0        # Wing AR — used to derive semi-span from area
SPAR_PERIMETER_FACTOR = 2.4  # Approximate box-spar cross-section perimeter / chord
PROPULSION_SPECIFIC_MASS = 0.005  # kg/W — modern brushless motor empirical ratio
RESULTS_DIR   = os.path.join(os.path.dirname(__file__), "..", "results")
DATA_PATH     = os.path.join(os.path.dirname(__file__), "..", "data",
                             "Weight_Analysis_data.csv")


# ── Functions ─────────────────────────────────────────────────────────────────

def spar_mass(wing_area_m2, skin_thickness_mm, density_kgm3,
              AR=ASPECT_RATIO, pf=SPAR_PERIMETER_FACTOR):
    """
    Thin-walled box spar + skin mass (kg).
    Semi-span  b  = sqrt(AR * S) / 2
    Mean chord c  = sqrt(S / AR)
    Volume ≈ b * c * t_skin * perimeter_factor
    """
    t_m       = skin_thickness_mm / 1000.0
    semi_span = np.sqrt(AR * wing_area_m2) / 2.0
    chord     = np.sqrt(wing_area_m2 / AR)
    volume    = semi_span * chord * t_m * pf
    return density_kgm3 * volume


def propulsion_mass(power_w, specific_mass=PROPULSION_SPECIFIC_MASS):
    """Propulsion system mass (kg) — motor + ESC empirical ratio."""
    return specific_mass * power_w


def control_surface_mass(area_m2, surface_density_kgm2=1.8):
    """
    Control surface mass (kg).
    Typical CFRP control surface: ~1.8 kg/m^2 areal density.
    """
    return area_m2 * surface_density_kgm2


def build_mass_breakdown(data):
    """Return DataFrame with per-row mass components and totals."""
    df = data.copy()
    df["mass_spar_kg"]        = spar_mass(
        df["Wing_Area_m2"], df["Skin_Thickness_mm"], df["Spar_Density_kgm3"])
    df["mass_propulsion_kg"]  = propulsion_mass(df["Propulsion_Power_W"])
    df["mass_controls_kg"]    = control_surface_mass(df["Control_Surface_Area_m2"])
    df["mass_electronics_kg"] = df["Electronics_Weight_kg"]
    df["mass_total_kg"]       = (df["mass_spar_kg"] + df["mass_propulsion_kg"]
                                  + df["mass_controls_kg"] + df["mass_electronics_kg"])
    return df


def plot_weight_distribution(df, output_path):
    """Stacked bar chart — mass breakdown per design variant."""
    components = ["mass_spar_kg", "mass_propulsion_kg",
                  "mass_controls_kg", "mass_electronics_kg"]
    labels     = ["Spar + Skin", "Propulsion", "Control Surfaces", "Electronics"]
    colors     = ["#378ADD", "#1D9E75", "#D85A30", "#7F77DD"]

    fig, ax = plt.subplots(figsize=(12, 6))
    x      = np.arange(len(df))
    bottom = np.zeros(len(df))

    for comp, label, color in zip(components, labels, colors):
        vals = df[comp].values
        ax.bar(x, vals, bottom=bottom, label=label, color=color,
               width=0.6, edgecolor="white")
        bottom += vals

    # Annotate totals
    for i, (total, mat) in enumerate(zip(df["mass_total_kg"], df["Spar_Material"])):
        ax.text(i, total + 0.02, f"{total:.2f} kg\n({mat})",
                ha="center", va="bottom", fontsize=8, fontweight="bold")

    ax.set_xlabel("Design Variant", fontsize=11)
    ax.set_ylabel("Mass (kg)", fontsize=11)
    ax.set_title(
        "Wing Mass Breakdown by Component — Hybrid VTOL Platform\n"
        "Al 7075-T6 vs CFRP Spar Comparison",
        fontsize=12, fontweight="bold"
    )
    ax.set_xticks(x)
    ax.set_xticklabels([f"DS{i+1}" for i in x], fontsize=9)
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    ax.set_facecolor("#FAFAFA")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


def plot_average_breakdown(df, output_path):
    """Pie chart of mean mass breakdown across all variants."""
    components = ["mass_spar_kg", "mass_propulsion_kg",
                  "mass_controls_kg", "mass_electronics_kg"]
    labels     = ["Spar + Skin", "Propulsion", "Control Surfaces", "Electronics"]
    colors     = ["#378ADD", "#1D9E75", "#D85A30", "#7F77DD"]
    means      = [df[c].mean() for c in components]

    fig, ax = plt.subplots(figsize=(7, 6))
    wedges, texts, autotexts = ax.pie(
        means, labels=labels, colors=colors,
        autopct="%1.1f%%", startangle=90,
        wedgeprops=dict(edgecolor="white", linewidth=1.5)
    )
    for at in autotexts:
        at.set_fontsize(10)
        at.set_fontweight("bold")

    ax.set_title(
        f"Mean Wing Mass Distribution\nTotal: {sum(means):.2f} kg",
        fontsize=13, fontweight="bold"
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    data = pd.read_csv(DATA_PATH)
    df   = build_mass_breakdown(data)

    print("Weight Estimation Results  (wing structure only):")
    print(f"\n  {'DS':<5} {'Material':<8} {'Spar+Skin':>10} "
          f"{'Propulsion':>11} {'Controls':>9} {'Avionics':>9} {'TOTAL':>8}")
    print("  " + "─" * 62)
    for i, row in df.iterrows():
        print(f"  {i+1:<5} {row['Spar_Material']:<8} "
              f"{row['mass_spar_kg']:>9.3f}  "
              f"{row['mass_propulsion_kg']:>10.3f}  "
              f"{row['mass_controls_kg']:>8.3f}  "
              f"{row['mass_electronics_kg']:>8.3f}  "
              f"{row['mass_total_kg']:>7.3f} kg")

    al_mean   = df[df["Spar_Material"] == "Al7075"]["mass_total_kg"].mean()
    cfrp_mean = df[df["Spar_Material"] == "CFRP"]["mass_total_kg"].mean()
    saving    = (al_mean - cfrp_mean) / al_mean * 100

    print(f"\n  Al 7075 mean total  : {al_mean:.3f} kg")
    print(f"  CFRP mean total     : {cfrp_mean:.3f} kg")
    print(f"  CFRP mass saving    : {saving:.1f}%")

    plot_weight_distribution(df, os.path.join(RESULTS_DIR, "weight_distribution.png"))
    plot_average_breakdown(df, os.path.join(RESULTS_DIR, "weight_breakdown_pie.png"))

    print("\nWeight estimation complete.")


if __name__ == "__main__":
    main()