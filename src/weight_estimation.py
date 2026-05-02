"""
weight_estimation.py
--------------------
Wing mass breakdown estimation for the hybrid VTOL platform.

Estimates mass contributions from structural materials, propulsion,
control surfaces, and avionics across multiple design datasets.
Total estimated wing mass is printed and a breakdown chart saved.

Inputs : data/Weight_Analysis_data.csv
Outputs: results/weight_distribution.png
         results/weight_breakdown_bar.png

Usage:
    python src/weight_estimation.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Constants ─────────────────────────────────────────────────────────────────
GRAVITY     = 9.81
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
DATA_PATH   = os.path.join(os.path.dirname(__file__), "..", "data",
                           "Weight_Analysis_data.csv")

# ── Functions ─────────────────────────────────────────────────────────────────

def estimate_structural_mass(wing_area, wing_loading, material_density):
    """Structural mass from wing area, loading, and material density (kg)."""
    return wing_area * wing_loading / GRAVITY * material_density


def estimate_propulsion_mass(propulsion_power):
    """Propulsion system mass — empirical ratio: 0.1 kg/W (kg)."""
    return 0.1 * propulsion_power


def estimate_control_surface_mass(area, density):
    """Control surface mass from area and surface density (kg)."""
    return area * density


def build_mass_breakdown(data):
    """Return DataFrame with per-row mass components and totals."""
    df = data.copy()
    df["mass_structural"]  = estimate_structural_mass(
        df["Wing_Area"], df["Wing_Loading"], df["Material_Density"])
    df["mass_propulsion"]  = estimate_propulsion_mass(df["Propulsion_Power"])
    df["mass_controls"]    = estimate_control_surface_mass(
        df["Control_Surface_Area"], df["Control_Surface_Density"])
    df["mass_electronics"] = df["Electronics_Weight"]
    df["mass_total"]       = (df["mass_structural"] + df["mass_propulsion"]
                               + df["mass_controls"] + df["mass_electronics"])
    return df


def plot_weight_distribution(df, output_path):
    """Stacked bar chart showing mass breakdown per design dataset row."""
    components = ["mass_structural", "mass_propulsion",
                  "mass_controls",   "mass_electronics"]
    labels     = ["Structural", "Propulsion", "Controls", "Electronics"]
    colors     = ["#378ADD", "#1D9E75", "#D85A30", "#7F77DD"]

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(df))
    bottom = np.zeros(len(df))

    for comp, label, color in zip(components, labels, colors):
        vals = df[comp].values
        ax.bar(x, vals, bottom=bottom, label=label, color=color,
               width=0.6, edgecolor="white")
        bottom += vals

    ax.set_xlabel("Design Dataset (row index)", fontsize=11)
    ax.set_ylabel("Mass (kg)", fontsize=11)
    ax.set_title("Wing Mass Breakdown by Component\nHybrid VTOL Platform",
                 fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([f"Dataset {i+1}" for i in x])
    ax.legend(loc="upper right", fontsize=10)
    ax.grid(axis="y", alpha=0.3)

    for i, total in enumerate(df["mass_total"]):
        ax.text(i, total + total * 0.01, f"{total:.0f} kg",
                ha="center", va="bottom", fontsize=9, fontweight="bold")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


def plot_average_breakdown(df, output_path):
    """Pie chart of average mass breakdown across all datasets."""
    components = ["mass_structural", "mass_propulsion",
                  "mass_controls",   "mass_electronics"]
    labels     = ["Structural", "Propulsion", "Controls", "Electronics"]
    colors     = ["#378ADD", "#1D9E75", "#D85A30", "#7F77DD"]
    means      = [df[c].mean() for c in components]

    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(
        means, labels=labels, colors=colors,
        autopct="%1.1f%%", startangle=90,
        wedgeprops=dict(edgecolor="white", linewidth=1.5)
    )
    for at in autotexts:
        at.set_fontsize(10)
        at.set_fontweight("bold")

    ax.set_title(
        f"Average Wing Mass Distribution\nTotal: {sum(means):.1f} kg",
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

    print("Weight Estimation Results:")
    for i, row in df.iterrows():
        print(f"\n  Dataset {i+1}:")
        print(f"    Structural  : {row['mass_structural']:.1f} kg")
        print(f"    Propulsion  : {row['mass_propulsion']:.1f} kg")
        print(f"    Controls    : {row['mass_controls']:.1f} kg")
        print(f"    Electronics : {row['mass_electronics']:.1f} kg")
        print(f"    TOTAL       : {row['mass_total']:.1f} kg")

    print(f"\n  Mean total mass across all datasets: {df['mass_total'].mean():.1f} kg")

    plot_weight_distribution(
        df, os.path.join(RESULTS_DIR, "weight_distribution.png"))
    plot_average_breakdown(
        df, os.path.join(RESULTS_DIR, "weight_breakdown_pie.png"))

    print("\nWeight estimation complete.")


if __name__ == "__main__":
    main()
