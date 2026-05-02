"""
flight_performance.py
---------------------
Flight performance prediction for the hybrid VTOL platform.

Computes take-off distance, climb rate, maximum speed, and endurance
from fundamental aerodynamic and propulsion parameters.

Inputs : data/flight_performance_data.csv
Outputs: results/flight_performance.png

Usage:
    python src/flight_performance.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Constants ─────────────────────────────────────────────────────────────────
GRAVITY        = 9.81        # m/s^2
BATTERY_CAP_WH = 10000       # Battery capacity, Wh
POWER_W        = 1000        # Cruise power consumption, W
RESULTS_DIR    = os.path.join(os.path.dirname(__file__), "..", "results")
DATA_PATH      = os.path.join(os.path.dirname(__file__), "..", "data",
                              "flight_performance_data.csv")

# ── Functions ─────────────────────────────────────────────────────────────────

def takeoff_distance(thrust, weight, wing_area, Cd):
    """
    Simplified ground roll estimate (m).
    s = 0.1 * (T/W) * (W/S) * (1/Cd)
    """
    return 0.1 * (thrust / weight) * (weight / wing_area) * (1.0 / Cd)


def climb_rate(thrust, weight, Cd):
    """Rate of climb (m/s) — excess thrust model."""
    return (thrust - weight * GRAVITY) / (0.5 * weight * GRAVITY / Cd)


def max_speed(thrust, weight, Cd):
    """Maximum level flight speed (m/s)."""
    return (thrust / weight) / (0.5 * GRAVITY / Cd)


def endurance(battery_wh, power_w):
    """Flight endurance (hours)."""
    return battery_wh / power_w


def plot_performance(df, output_path):
    """Four-panel performance summary dashboard."""
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    fig.suptitle(
        "Flight Performance Prediction — Hybrid VTOL Platform",
        fontsize=14, fontweight="bold"
    )

    x      = np.arange(len(df))
    labels = [f"Dataset {i+1}" for i in x]
    bar_kw = dict(width=0.5, edgecolor="white")

    metrics = [
        (axes[0, 0], df["Takeoff_m"],    "#378ADD", "Take-off Distance (m)",   "Take-off Distance"),
        (axes[0, 1], df["ClimbRate_ms"], "#1D9E75", "Climb Rate (m/s)",         "Climb Rate"),
        (axes[1, 0], df["MaxSpeed_ms"],  "#D85A30", "Maximum Speed (m/s)",       "Maximum Speed"),
        (axes[1, 1], df["Endurance_hr"], "#7F77DD", "Endurance (hours)",         "Flight Endurance"),
    ]

    for ax, values, color, ylabel, title in metrics:
        bars = ax.bar(x, values, color=color, **bar_kw)
        ax.bar_label(bars, fmt="%.2f", padding=3, fontsize=10, fontweight="bold")
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=9)
        ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    data = pd.read_csv(DATA_PATH)

    data["Takeoff_m"]    = takeoff_distance(
        data["Thrust"], data["Total_Weight"], data["Wing_Area"], data["Drag_Coefficient"])
    data["ClimbRate_ms"] = climb_rate(
        data["Thrust"], data["Total_Weight"], data["Drag_Coefficient"])
    data["MaxSpeed_ms"]  = max_speed(
        data["Thrust"], data["Total_Weight"], data["Drag_Coefficient"])
    data["Endurance_hr"] = endurance(BATTERY_CAP_WH, POWER_W)

    print("Flight Performance Results:")
    for i, row in data.iterrows():
        print(f"\n  Dataset {i+1}:")
        print(f"    Take-off distance : {row['Takeoff_m']:.2f} m")
        print(f"    Climb rate        : {row['ClimbRate_ms']:.2f} m/s")
        print(f"    Maximum speed     : {row['MaxSpeed_ms']:.2f} m/s")
        print(f"    Endurance         : {row['Endurance_hr']:.2f} hours")

    plot_performance(
        data, os.path.join(RESULTS_DIR, "flight_performance.png"))

    print("\nFlight performance prediction complete.")


if __name__ == "__main__":
    main()
