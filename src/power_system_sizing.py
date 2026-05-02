"""
power_system_sizing.py
----------------------
Power system sizing and endurance prediction for the hybrid VTOL platform.

Computes thrust-to-weight ratio, endurance, and power consumption across
the design dataset. Endurance model: E = Battery_Capacity / Power (hours).

Inputs : data/power_system_data.csv
Outputs: results/power_tw_ratio_endurance.png

Usage:
    python src/power_system_sizing.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Constants ─────────────────────────────────────────────────────────────────
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
DATA_PATH   = os.path.join(os.path.dirname(__file__), "..", "data",
                           "power_system_data.csv")

# ── Functions ─────────────────────────────────────────────────────────────────

def thrust_to_weight_ratio(thrust, weight):
    """Dimensionless TW ratio — must exceed 1.0 for VTOL hover."""
    return thrust / weight


def endurance_hours(battery_capacity_wh, power_w):
    """Flight endurance in hours: E = Capacity / Power."""
    return battery_capacity_wh / power_w


def plot_power_results(df, output_path):
    """Dual-axis plot: TW ratio (bar) and endurance (line) per dataset."""
    x      = np.arange(len(df))
    labels = [f"Dataset {i+1}" for i in x]

    fig, ax1 = plt.subplots(figsize=(10, 6))
    fig.suptitle("Power System Sizing — TW Ratio and Flight Endurance",
                 fontsize=13, fontweight="bold")

    # TW ratio bars
    bars = ax1.bar(x, df["TW_Ratio"], color="#378ADD", alpha=0.8,
                   width=0.5, label="TW Ratio", edgecolor="white")
    ax1.bar_label(bars, fmt="%.2f", padding=3, fontsize=10, fontweight="bold",
                  color="#0C447C")
    ax1.axhline(y=1.0, color="#E24B4A", linestyle="--", linewidth=1.5,
                label="TW = 1.0 (hover threshold)")
    ax1.set_xlabel("Design Dataset", fontsize=11)
    ax1.set_ylabel("Thrust-to-Weight Ratio", fontsize=11, color="#378ADD")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)
    ax1.tick_params(axis="y", labelcolor="#378ADD")

    # Endurance line on secondary axis
    ax2 = ax1.twinx()
    ax2.plot(x, df["Endurance_hr"], color="#1D9E75", linewidth=2.5,
             marker="o", markersize=8, label="Endurance (hr)")
    ax2.set_ylabel("Endurance (hours)", fontsize=11, color="#1D9E75")
    ax2.tick_params(axis="y", labelcolor="#1D9E75")

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
               loc="upper right", fontsize=10)

    ax1.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    data = pd.read_csv(DATA_PATH)

    data["TW_Ratio"]    = thrust_to_weight_ratio(data["Thrust"], data["Total_Weight"])
    data["Endurance_hr"] = endurance_hours(data["Battery_Capacity"], data["Power"])

    print("Power System Sizing Results:")
    for i, row in data.iterrows():
        hover_ok = "PASS" if row["TW_Ratio"] > 1.0 else "FAIL"
        print(f"\n  Dataset {i+1}:")
        print(f"    TW Ratio    : {row['TW_Ratio']:.3f}  [{hover_ok} — hover requires > 1.0]")
        print(f"    Endurance   : {row['Endurance_hr']:.2f} hours")
        print(f"    Power       : {row['Power']:.0f} W")

    print(f"\n  Mean endurance : {data['Endurance_hr'].mean():.2f} hours")
    print(f"  Mean TW ratio  : {data['TW_Ratio'].mean():.3f}")

    plot_power_results(
        data, os.path.join(RESULTS_DIR, "power_tw_ratio_endurance.png"))

    print("\nPower system sizing complete.")


if __name__ == "__main__":
    main()
