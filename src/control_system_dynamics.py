"""
control_system_dynamics.py
--------------------------
Control surface dynamics analysis for the hybrid VTOL wing ailerons.

Models aileron hinge moment, required servo torque, achievable roll rate,
and bandwidth-limited step response time across the VTOL airspeed envelope
(15 to 60 m/s).

Physics:
    Hinge moment  H  = Ch * q * S_a * c_a
    Servo torque  T  = H / eta_servo
    Roll rate     p  = (2 * V * Cl_delta * S_a * b_a) / (Ix * b)   [simplified]
    Response time tau = 1 / (2 * pi * f_bandwidth)

where:
    Ch        = empirical hinge moment coefficient (~0.008 for plain flap)
    q         = dynamic pressure = 0.5 * rho * V^2
    S_a, c_a  = aileron area and mean chord
    eta_servo = servo mechanical efficiency
    f_bw      = servo bandwidth (Hz)

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
RHO             = 1.225     # kg/m^3 — ISA sea level
CH              = 0.008     # Hinge moment coefficient — plain flap, typical
DEFLECTION_RAD  = np.radians(15.0)   # Design aileron deflection — 15°
ETA_SERVO       = 0.88      # Servo mechanical efficiency
CL_DELTA        = 0.032     # Roll control effectiveness per radian deflection
WING_SPAN       = 2.4       # Full wing span, m
IX_APPROX       = 0.18      # Roll moment of inertia, kg·m^2 (estimated)

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
DATA_PATH   = os.path.join(os.path.dirname(__file__), "..", "data",
                           "control_system_dynamics_data.csv")


# ── Functions ─────────────────────────────────────────────────────────────────

def hinge_moment(q_Pa, aileron_area_m2, aileron_span_m, Ch=CH):
    """
    Aerodynamic hinge moment (N·m).
    H = Ch * q * S_a * c_a
    where c_a = S_a / b_a (mean aileron chord)
    """
    mean_chord = aileron_area_m2 / aileron_span_m
    return Ch * q_Pa * aileron_area_m2 * mean_chord


def servo_torque_required(hinge_moment_Nm, eta=ETA_SERVO):
    """Servo output torque required to overcome hinge moment (N·m)."""
    return hinge_moment_Nm / eta


def roll_rate(airspeed_ms, aileron_area_m2, aileron_span_m,
              Cl_delta=CL_DELTA, b=WING_SPAN, Ix=IX_APPROX, rho=RHO):
    """
    Steady-state roll rate (deg/s) — simplified strip theory.
    p = (rho * V^2 * Cl_delta * S_a * b_a) / (Ix * b)
    """
    p_rads = (rho * airspeed_ms**2 * Cl_delta *
              aileron_area_m2 * aileron_span_m) / (Ix * b)
    return np.degrees(p_rads)


def response_time(bandwidth_hz):
    """
    First-order step response time constant (s).
    tau = 1 / (2 * pi * f_bw)
    """
    return 1.0 / (2.0 * np.pi * bandwidth_hz)


def time_to_deflect(bandwidth_hz, deflection_deg=15.0, slew_rate_degs=180.0):
    """
    Actual time to reach full deflection — limited by slew rate.
    t = max(deflection / slew_rate, 2.2 * tau)
    2.2*tau gives ~89% of step response for first-order system.
    """
    tau  = response_time(bandwidth_hz)
    t_sr = deflection_deg / slew_rate_degs
    return np.maximum(2.2 * tau, t_sr)


def plot_control_dynamics(df, output_path):
    """Four-panel control dynamics summary."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle(
        "Control Surface Dynamics — Hybrid VTOL Wing Ailerons\n"
        "Deflection = 15°  ·  ISA Sea Level  ·  Plain Flap  Ch = 0.008",
        fontsize=12, fontweight="bold"
    )

    x      = np.arange(len(df))
    bar_kw = dict(width=0.55, edgecolor="white")

    # Panel 1 — Hinge moment vs airspeed
    axes[0, 0].bar(x, df["Hinge_Moment_Nm"], color="#378ADD", **bar_kw)
    axes[0, 0].bar_label(axes[0, 0].containers[0], fmt="%.3f", padding=3,
                         fontsize=8, fontweight="bold")
    axes[0, 0].set_title("Aileron Hinge Moment", fontsize=11, fontweight="bold")
    axes[0, 0].set_ylabel("Hinge Moment (N·m)", fontsize=10)

    # Panel 2 — Servo torque required
    axes[0, 1].bar(x, df["Servo_Torque_Nm"], color="#1D9E75", **bar_kw)
    axes[0, 1].bar_label(axes[0, 1].containers[0], fmt="%.3f", padding=3,
                         fontsize=8, fontweight="bold")
    axes[0, 1].set_title("Servo Torque Required", fontsize=11, fontweight="bold")
    axes[0, 1].set_ylabel("Torque (N·m)", fontsize=10)

    # Panel 3 — Achievable roll rate
    axes[1, 0].bar(x, df["Roll_Rate_degs"], color="#D85A30", **bar_kw)
    axes[1, 0].bar_label(axes[1, 0].containers[0], fmt="%.1f", padding=3,
                         fontsize=8, fontweight="bold")
    axes[1, 0].axhline(df["Desired_Roll_Rate_degs"].mean(), color="grey",
                       linestyle="--", linewidth=1.2, label="Target roll rate")
    axes[1, 0].set_title("Achievable Roll Rate", fontsize=11, fontweight="bold")
    axes[1, 0].set_ylabel("Roll Rate (deg/s)", fontsize=10)
    axes[1, 0].legend(fontsize=9)

    # Panel 4 — Response time
    axes[1, 1].bar(x, df["Response_Time_s"] * 1000, color="#7F77DD", **bar_kw)
    axes[1, 1].bar_label(axes[1, 1].containers[0], fmt="%.1f", padding=3,
                         fontsize=8, fontweight="bold")
    axes[1, 1].set_title("Step Response Time (to 89%)", fontsize=11,
                         fontweight="bold")
    axes[1, 1].set_ylabel("Response Time (ms)", fontsize=10)

    for ax in axes.flat:
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

    data["Hinge_Moment_Nm"]  = hinge_moment(
        data["Dynamic_Pressure_Pa"],
        data["Aileron_Area_m2"],
        data["Aileron_Span_m"])

    data["Servo_Torque_Nm"]  = servo_torque_required(data["Hinge_Moment_Nm"])

    data["Roll_Rate_degs"]   = roll_rate(
        data["Airspeed_ms"],
        data["Aileron_Area_m2"],
        data["Aileron_Span_m"])

    data["Response_Time_s"]  = time_to_deflect(data["Servo_Bandwidth_Hz"])

    print("Control Surface Dynamics Results:")
    print(f"\n  {'DS':<5} {'V (m/s)':>8} {'H (N·m)':>9} "
          f"{'T_servo (N·m)':>14} {'Roll (°/s)':>11} {'t_resp (ms)':>12}")
    print("  " + "─" * 63)
    for i, row in data.iterrows():
        print(f"  {i+1:<5} {row['Airspeed_ms']:>8.0f} "
              f"{row['Hinge_Moment_Nm']:>9.4f} "
              f"{row['Servo_Torque_Nm']:>14.4f} "
              f"{row['Roll_Rate_degs']:>11.1f} "
              f"{row['Response_Time_s']*1000:>11.1f}")

    # Key design check — does roll rate meet requirement?
    passing = (data["Roll_Rate_degs"] >= data["Desired_Roll_Rate_degs"]).sum()
    print(f"\n  Roll rate requirement met: {passing}/{len(data)} datasets")
    print(f"  Max servo torque required: {data['Servo_Torque_Nm'].max():.4f} N·m")
    print(f"  Max response time        : {data['Response_Time_s'].max()*1000:.1f} ms")

    plot_control_dynamics(
        data, os.path.join(RESULTS_DIR, "control_system_dynamics.png"))

    print("\nControl system dynamics analysis complete.")


if __name__ == "__main__":
    main()