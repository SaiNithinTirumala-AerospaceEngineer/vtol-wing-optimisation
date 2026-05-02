"""
cog_analysis.py
---------------
Centre of Gravity (CoG) analysis for the hybrid VTOL platform.

Computes the overall CoG location from component masses and positions,
evaluates static margin relative to the aerodynamic centre, and
generates a mass map showing component contributions.

Physics:
    x_cog = sum(m_i * x_i) / sum(m_i)
    y_cog = sum(m_i * y_i) / sum(m_i)   [should be ~0 for symmetric design]
    z_cog = sum(m_i * z_i) / sum(m_i)

    Static margin = (x_ac - x_cog) / MAC
    Positive static margin → longitudinally stable

Inputs : data/COG_Analysis_data.csv
Outputs: results/cog_analysis.png

Usage:
    python src/cog_analysis.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Constants ─────────────────────────────────────────────────────────────────
MAC          = 0.283    # Mean aerodynamic chord, m
X_AC         = 0.453    # Aerodynamic centre — 25% MAC from leading edge
                        # x_ac = x_le + 0.25 * MAC = 0.170 + 0.283*0.25 = ~0.241
                        # Using fuselage nose reference: ~0.453 m from nose
WING_SPAN    = 2.4      # m
RESULTS_DIR  = os.path.join(os.path.dirname(__file__), "..", "results")
DATA_PATH    = os.path.join(os.path.dirname(__file__), "..", "data",
                            "COG_Analysis_data.csv")


# ── Functions ─────────────────────────────────────────────────────────────────

def compute_cog(masses, x_pos, y_pos, z_pos):
    """
    Compute CoG location from component masses and positions.
    Returns (x_cog, y_cog, z_cog) in metres from nose reference.
    """
    total_mass = masses.sum()
    x_cog = (masses * x_pos).sum() / total_mass
    y_cog = (masses * y_pos).sum() / total_mass
    z_cog = (masses * z_pos).sum() / total_mass
    return x_cog, y_cog, z_cog, total_mass


def static_margin(x_cog, x_ac, mac):
    """
    Static margin as fraction of MAC.
    Positive value → stable. Typical target: 5–15% MAC.
    """
    return (x_ac - x_cog) / mac


def plot_cog_analysis(df, x_cog, y_cog, z_cog, sm, output_path):
    """Two-panel plot: top view mass map + component breakdown bar."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(
        "Centre of Gravity Analysis — Hybrid VTOL Platform\n"
        f"CoG: x={x_cog:.3f} m, y={y_cog:.4f} m, z={z_cog:.3f} m  "
        f"·  Static Margin: {sm*100:.1f}% MAC",
        fontsize=12, fontweight="bold"
    )

    # ── Panel 1: Top-view mass map ────────────────────────────────────────
    ax = axes[0]
    colors = plt.cm.Set2(np.linspace(0, 1, len(df)))

    for i, (_, row) in enumerate(df.iterrows()):
        size = row["Mass_kg"] * 120
        ax.scatter(row["Y_from_centreline_m"], row["X_from_nose_m"],
                   s=size, color=colors[i], alpha=0.8,
                   edgecolors="white", linewidth=0.8, zorder=3)
        ax.annotate(row["Component"].replace("_", " "),
                    (row["Y_from_centreline_m"], row["X_from_nose_m"]),
                    fontsize=6.5, ha="center", va="bottom",
                    xytext=(0, 6), textcoords="offset points", color="white")

    # CoG marker
    ax.scatter(y_cog, x_cog, s=250, color="#FF4444", marker="*",
               zorder=5, label=f"CoG ({x_cog:.3f}, {y_cog:.4f}) m")
    # AC marker
    ax.axhline(X_AC, color="#FFD700", linewidth=1.2, linestyle="--",
               label=f"Aero Centre x={X_AC:.3f} m")

    ax.set_xlabel("Y — Spanwise Position (m)", fontsize=10)
    ax.set_ylabel("X — From Nose (m)", fontsize=10)
    ax.set_title("Top View — Component Mass Map", fontsize=11, fontweight="bold")
    ax.set_facecolor("#1a1a2e")
    ax.legend(fontsize=8, loc="upper right")
    ax.grid(True, alpha=0.2)
    ax.invert_yaxis()   # nose at top

    # ── Panel 2: Component mass breakdown bar ─────────────────────────────
    ax2 = axes[1]
    sorted_df = df.sort_values("Mass_kg", ascending=True)
    bars = ax2.barh(sorted_df["Component"].str.replace("_", " "),
                    sorted_df["Mass_kg"],
                    color=plt.cm.Set2(np.linspace(0, 1, len(sorted_df))),
                    edgecolor="white", height=0.6)
    ax2.bar_label(bars, fmt="%.3f kg", padding=4, fontsize=8)
    ax2.set_xlabel("Mass (kg)", fontsize=10)
    ax2.set_title(
        f"Component Mass Breakdown\nTotal: {df['Mass_kg'].sum():.3f} kg",
        fontsize=11, fontweight="bold"
    )
    ax2.grid(axis="x", alpha=0.3)
    ax2.set_facecolor("#FAFAFA")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    df = pd.read_csv(DATA_PATH)

    x_cog, y_cog, z_cog, total_mass = compute_cog(
        df["Mass_kg"],
        df["X_from_nose_m"],
        df["Y_from_centreline_m"],
        df["Z_from_datum_m"]
    )

    sm = static_margin(x_cog, X_AC, MAC)

    print("CoG Analysis Results:")
    print(f"  Total mass          : {total_mass:.3f} kg")
    print(f"  CoG x (from nose)   : {x_cog:.4f} m")
    print(f"  CoG y (lateral)     : {y_cog:.4f} m  "
          f"{'[symmetric ✓]' if abs(y_cog) < 0.001 else '[asymmetric — check]'}")
    print(f"  CoG z (vertical)    : {z_cog:.4f} m")
    print(f"  Aerodynamic centre  : {X_AC:.4f} m from nose")
    print(f"  Static margin       : {sm*100:.2f}% MAC")

    if 0.05 <= sm <= 0.20:
        print(f"  → Longitudinally STABLE — SM within 5–20% MAC target ✓")
    elif sm > 0.20:
        print(f"  → Overly stable — may require high elevator authority")
    else:
        print(f"  → Unstable or marginal — CoG ahead of AC, review layout")

    print(f"\n  Component breakdown:")
    print(f"  {'Component':<30} {'Mass (kg)':>10} {'X (m)':>8} {'Y (m)':>8}")
    print("  " + "─" * 60)
    for _, row in df.sort_values("Mass_kg", ascending=False).iterrows():
        print(f"  {row['Component'].replace('_',' '):<30} "
              f"{row['Mass_kg']:>10.3f} "
              f"{row['X_from_nose_m']:>8.3f} "
              f"{row['Y_from_centreline_m']:>8.3f}")

    plot_cog_analysis(
        df, x_cog, y_cog, z_cog, sm,
        os.path.join(RESULTS_DIR, "cog_analysis.png")
    )

    print("\nCoG analysis complete.")


if __name__ == "__main__":
    main()