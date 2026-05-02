"""
control_system_dynamics.py
--------------------------
Control surface dynamics analysis for the hybrid VTOL wing.

Models control surface deflection, servo torque requirements, and
system response time across the design envelope.

Inputs : data/control_system_dynamics_data.csv
Outputs: results/control_system_dynamics.png

Usage:
    python src/control_system_dynamics.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ── Constants ─────────────────────────────────────────────────────────────────
RESPONSE_TIME = 0.1          # Fixed response time, seconds (servo hardware)
RESULTS_DIR   = os.path.join(os.path.dirname(__file__), "..", "results")
DATA_PATH     = os.path.join(os.path.dirname(__file__), "..", "data",
                             "control_system_dynamics_data.csv")

# ── Functions ─────────────────────────────────────────────────────────────────

def control_surface_deflection(desired_maneuverability):
    """
    Deflection angle (radians) from desired maneuverability factor.
    Linear model: delta = 0.1 * maneuverability_factor
    """
    return desired_maneuverability * 0.1


def servo_torque(surface_area, deflection, efficiency):
    """
    Servo torque requirement (N·m).
    T = A * delta / eta
    """
    return surface_area * deflection / efficiency


def plot_control_dynamics(df, output_path):
    """Three-panel: deflection, servo torque, and response bandwidth."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Control System Dynamics Analysis — Hybrid VTOL Wing",
                 fontsize=13, fontweight="bold")

    x      = np.arange(len(df))
    labels = [f"DS {i+1}" for i in x]

    # Panel 1 — Control surface deflection
    axes[0].bar(x, np.degrees(df["Deflection_rad"]),
                color="#378ADD", width=0.5, edgecolor="white")
    axes[0].set_title("Control Surface Deflection", fontsize=11, fontweight="bold")
    axes[0].set_ylabel("Deflection (degrees)", fontsize=10)
    axes[0].set_xticks(x); axes[0].set_xticklabels(labels)
    axes[0].grid(axis="y", alpha=0.3)

    # Panel 2 — Servo torque
    axes[1].bar(x, df["Servo_Torque_Nm"],
                color="#1D9E75", width=0.5, edgecolor="white")
    axes[1].set_title("Servo Torque Requirement", fontsize=11, fontweight="bold")
    axes[1].set_ylabel("Torque (N·m)", fontsize=10)
    axes[1].set_xticks(x); axes[1].set_xticklabels(labels)
    axes[1].grid(axis="y", alpha=0.3)

    # Panel 3 — Maneuverability vs efficiency scatter
    scatter = axes[2].scatter(
        df["Servo_Efficiency"], df["Desired_Maneuverability"],
        c=df["Servo_Torque_Nm"], cmap="viridis", s=100, edgecolors="white"
    )
    plt.colorbar(scatter, ax=axes[2], label="Servo Torque (N·m)")
    axes[2].set_xlabel("Servo Efficiency", fontsize=10)
    axes[2].set_ylabel("Desired Maneuverability Factor", fontsize=10)
    axes[2].set_title("Maneuverability vs Servo Efficiency", fontsize=11,
                      fontweight="bold")
    axes[2].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    data = pd.read_csv(DATA_PATH)

    data["Deflection_rad"]  = control_surface_deflection(data["Desired_Maneuverability"])
    data["Servo_Torque_Nm"] = servo_torque(
        data["Control_Surface_Area"],
        data["Deflection_rad"],
        data["Servo_Efficiency"]
    )
    data["Response_Time_s"] = RESPONSE_TIME

    print("Control System Dynamics Results:")
    for i, row in data.iterrows():
        print(f"\n  Dataset {i+1}:")
        print(f"    Deflection   : {np.degrees(row['Deflection_rad']):.2f}°")
        print(f"    Servo torque : {row['Servo_Torque_Nm']:.4f} N·m")
        print(f"    Response time: {row['Response_Time_s']:.2f} s")

    plot_control_dynamics(
        data, os.path.join(RESULTS_DIR, "control_system_dynamics.png"))

    print("\nControl system dynamics analysis complete.")


if __name__ == "__main__":
    main()
