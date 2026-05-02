"""
flight_performance.py
---------------------
Flight performance prediction for the hybrid VTOL platform.

Computes take-off distance, climb rate, maximum cruise speed, and
endurance from fundamental aerodynamic and propulsion parameters.

Physics:
    Take-off distance : s = V_lof^2 / (2 * a)   where a = (T-D-muR) / m
    Climb rate        : RC = (T - D) * V / (m * g)   excess power method
    Max cruise speed  : solved where T = D = 0.5*rho*Cd*V^2*S
    Endurance         : E = Battery_Wh / Power_cruise_W  (hours)

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
GRAVITY   = 9.81      # m/s^2
RHO       = 1.225     # kg/m^3 — ISA sea level
MU_ROLL   = 0.04      # Rolling resistance coefficient (tarmac)
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
DATA_PATH   = os.path.join(os.path.dirname(__file__), "..", "data",
                           "flight_performance_data.csv")


# ── Functions ─────────────────────────────────────────────────────────────────

def takeoff_distance(thrust_N, mass_kg, wing_area_m2, Cl_to, Cd_to,
                     rho=RHO, g=GRAVITY, mu=MU_ROLL):
    """
    Ground roll to lift-off using energy method.
    V_lof = sqrt(2*W / (rho*S*Cl_to))
    s = V_lof^2 / (2 * a_avg)  where a_avg = (T - D_avg - mu*W) / m
    """
    weight_N = mass_kg * g
    V_lof    = np.sqrt(2 * weight_N / (rho * wing_area_m2 * Cl_to))
    # Average drag during ground roll at 0.7*V_lof
    V_avg    = 0.7 * V_lof
    D_avg    = 0.5 * rho * Cd_to * V_avg**2 * wing_area_m2
    R_avg    = mu * weight_N
    a_avg    = (thrust_N - D_avg - R_avg) / mass_kg
    a_avg    = np.maximum(a_avg, 0.1)   # guard against divide-by-zero if thrust < weight
    return V_lof**2 / (2 * a_avg)


def climb_rate(thrust_N, mass_kg, wing_area_m2, Cl, Cd,
               rho=RHO, g=GRAVITY):
    """
    Rate of climb — excess power method (m/s).
    RC = (T - D) * V_cruise / W
    where V_cruise = sqrt(2W / (rho*S*Cl))
    """
    weight_N  = mass_kg * g
    V_cruise  = np.sqrt(2 * weight_N / (rho * wing_area_m2 * Cl))
    D_cruise  = 0.5 * rho * Cd * V_cruise**2 * wing_area_m2
    excess_P  = (thrust_N - D_cruise) * V_cruise
    return excess_P / weight_N


def max_cruise_speed(thrust_N, mass_kg, wing_area_m2, Cd, rho=RHO, g=GRAVITY):
    """
    Maximum level-flight speed (m/s) — where thrust equals drag.
    T = 0.5 * rho * Cd * V^2 * S  =>  V = sqrt(T / (0.5*rho*Cd*S))
    """
    return np.sqrt(thrust_N / (0.5 * rho * Cd * wing_area_m2))


def endurance_hr(battery_wh, power_w):
    """Flight endurance (hours)."""
    return battery_wh / power_w


def plot_performance(df, output_path):
    """Four-panel performance summary dashboard."""
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    fig.suptitle(
        "Flight Performance Prediction — Hybrid VTOL Platform\n"
        "ISA Sea Level  ·  NACA 4412 Wing Section at Cruise AoA",
        fontsize=13, fontweight="bold"
    )

    x      = np.arange(len(df))
    bar_kw = dict(width=0.55, edgecolor="white")

    metrics = [
        (axes[0, 0], df["Takeoff_m"],     "#378ADD",
         "Take-off Distance (m)",   "Ground Roll to Lift-off"),
        (axes[0, 1], df["ClimbRate_ms"],  "#1D9E75",
         "Rate of Climb (m/s)",      "Climb Rate  [excess power]"),
        (axes[1, 0], df["MaxSpeed_ms"],   "#D85A30",
         "Max Cruise Speed (m/s)",   "Maximum Level-flight Speed"),
        (axes[1, 1], df["Endurance_hr"],  "#7F77DD",
         "Endurance (hours)",         "Flight Endurance"),
    ]

    for ax, values, color, ylabel, title in metrics:
        bars = ax.bar(x, values, color=color, **bar_kw)
        ax.bar_label(bars, fmt="%.1f", padding=3, fontsize=9, fontweight="bold")
        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels([f"DS{i+1}" for i in x], fontsize=8)
        ax.grid(axis="y", alpha=0.3)
        ax.set_facecolor("#FAFAFA")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    data = pd.read_csv(DATA_PATH)

    data["Takeoff_m"]    = takeoff_distance(
        data["Thrust_N"], data["MTOW_kg"], data["Wing_Area_m2"],
        data["Cl_cruise"], data["Cd_cruise"])

    data["ClimbRate_ms"] = climb_rate(
        data["Thrust_N"], data["MTOW_kg"], data["Wing_Area_m2"],
        data["Cl_cruise"], data["Cd_cruise"])

    data["MaxSpeed_ms"]  = max_cruise_speed(
        data["Thrust_N"], data["MTOW_kg"], data["Wing_Area_m2"],
        data["Cd_cruise"])

    data["Endurance_hr"] = endurance_hr(
        data["Battery_Wh"], data["Power_cruise_W"])

    print("Flight Performance Results:")
    print(f"\n  {'DS':<5} {'TO dist (m)':>12} {'RC (m/s)':>10} "
          f"{'Vmax (m/s)':>11} {'Endurance (hr)':>15}")
    print("  " + "─" * 57)
    for i, row in data.iterrows():
        print(f"  {i+1:<5} {row['Takeoff_m']:>12.1f} {row['ClimbRate_ms']:>10.2f} "
              f"{row['MaxSpeed_ms']:>11.1f} {row['Endurance_hr']:>15.2f}")

    plot_performance(data, os.path.join(RESULTS_DIR, "flight_performance.png"))
    print("\nFlight performance prediction complete.")


if __name__ == "__main__":
    main()