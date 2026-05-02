# Methodology — Hybrid VTOL Wing Analysis

## Overview

This project uses a two-phase approach: aerodynamic polar characterisation
in XFLR5 followed by multi-module performance modelling in Python. This
document explains both phases and the decisions behind them.

---

## Phase 1 — XFLR5 Aerodynamic Analysis

### Why XFLR5

XFLR5 implements Lifting Line Theory (LLT) and Vortex Lattice Method (VLM),
both of which are industry-standard panel methods for subsonic, low-Reynolds
number aerodynamic analysis. At Re = 500,000 (representative of the VTOL
transition regime at sea level), panel methods produce Cl and Cd values
within 2–5% of wind tunnel data for clean aerofoil sections, making them
appropriate for preliminary design.

XFLR5 was chosen over full CFD (OpenFOAM/ANSYS Fluent) for the initial
analysis because:
- Panel methods are 100–1000× faster than RANS CFD for polar sweeps
- Sufficient accuracy for preliminary design trade studies
- XFLR5 outputs export directly to CSV for downstream Python processing
- Appropriate fidelity for the Re regime of this platform

### Wing geometry

| Parameter        | Value   | Derivation                        |
|------------------|---------|-----------------------------------|
| Full span        | 2.4 m   | Design requirement                |
| Semi-span        | 1.2 m   | Span / 2                          |
| Wing area        | 0.48 m² | Design requirement                |
| Aspect ratio     | 6.0     | b² / S = 2.4² / 0.48             |
| Mean chord       | 0.283 m | √(S / AR) = √(0.48 / 6)          |
| Taper ratio      | 1.0     | Constant chord — baseline design  |
| Sweep            | 0°      | Unswept — hover stability         |
| Dihedral         | 0°      | Baseline configuration            |

### Airfoil spanwise layout

| Station   | y position | Airfoil    | Engineering rationale                          |
|-----------|------------|------------|------------------------------------------------|
| Root      | 0.0 m      | NACA 0012  | Symmetric — zero pitching moment, predictable  |
|           |            |            | hover behaviour, no adverse yaw coupling       |
| Mid-span  | 0.6 m      | NACA 2415  | 2% camber — improved cruise L/D with moderate  |
|           |            |            | low-speed lift penalty                         |
| Tip       | 1.2 m      | NACA 4412  | 4% camber — maximum low-speed lift for         |
|           |            |            | transition, accepted higher drag at cruise      |

This spanwise progression transitions from hover-optimised (root) to
cruise-optimised (tip), creating a blended aerodynamic characteristic
that partially satisfies both flight regimes without active morphing.

### Analysis settings

| Parameter         | Value        | Justification                              |
|-------------------|--------------|--------------------------------------------|
| Reynolds number   | 500,000      | Transition airspeed ~25 m/s, chord 0.283 m |
| AoA range         | −4° to 14°   | Covers hover incidence to pre-stall        |
| AoA step          | 1°           | Sufficient resolution for polar curves     |
| Analysis method   | LLT          | Appropriate for straight, unswept wings    |
| Ncrit             | 9            | XFLR5 default — clean tunnel conditions   |

### Polar export

After analysis, Cl, Cd, and Cm polars for each airfoil section were
exported from XFLR5 as CSV files. These are stored in `data/`:

```
data/xflr5_polar_naca0012.csv
data/xflr5_polar_naca2415.csv
data/xflr5_polar_naca4412.csv
```

The Python analysis modules read these CSVs directly, ensuring the
aerodynamic inputs are traceable to the XFLR5 analysis session.

---

## Phase 2 — Python Performance Modelling

### Module architecture

Each analysis domain is isolated in its own Python module. This was a
deliberate design decision — monolithic scripts make it impossible to
test individual physics models independently or swap input data without
affecting unrelated calculations.

```
src/
├── airfoil_comparison.py      # Polar overlay — all three profiles
├── aerodynamic_analysis.py    # Lift and drag vs airspeed
├── structural_analysis.py     # Spanwise stress, moment, shear
├── weight_estimation.py       # Mass breakdown — Al 7075 vs CFRP
├── power_system_sizing.py     # T/W ratio, battery endurance
├── flight_performance.py      # Take-off, climb, cruise speed
└── control_system_dynamics.py # Hinge moment, servo torque, roll rate
```

### Shared constants

All modules use consistent geometric and atmospheric constants:

| Constant     | Value      | Units  |
|--------------|------------|--------|
| Wing area S  | 0.48       | m²     |
| Full span b  | 2.4        | m      |
| Air density ρ| 1.225      | kg/m³  |
| Gravity g    | 9.81       | m/s²   |
| Load factor  | 2.5        | —      |

### Physics models — summary

**Aerodynamic analysis** uses thin-aerofoil theory:
```
L = 0.5 × ρ × Cl × V² × S
D = 0.5 × ρ × Cd × V² × S
```

**Structural analysis** integrates distributed lift load spanwise using
Euler-Bernoulli beam theory. Shear V(x) and bending moment M(x) are
computed by tip-to-root integration. Bending stress uses the flexure
formula σ = M·y / I. Load case: 2.5g CS-23 manoeuvre.

**Weight estimation** uses a thin-walled box spar approximation:
```
m_spar = ρ_material × b_semi × c_mean × t_skin × perimeter_factor
```
Two materials compared: Al 7075-T6 (ρ = 2810 kg/m³) and CFRP (ρ = 1600 kg/m³).

**Control surface dynamics** models aileron hinge moment:
```
H = Ch × q × S_aileron × c_aileron
```
Response time derived from servo bandwidth: τ = 1 / (2π × f_bw).

---

## Limitations

- LLT underestimates induced drag at high AoA and neglects viscous
  separation — RANS CFD (OpenFOAM) is identified as future validation work
- Structural model assumes a rectangular box spar with uniform taper —
  full composite layup FEA in ANSYS Mechanical is planned
- Aerodynamic-structural coupling is not modelled — aeroelastic effects
  at cruise speed are not captured
- Ground effect during take-off is neglected in the flight performance module

---

## References

- Abbott, I.H. and Von Doenhoff, A.E. (1959) *Theory of Wing Sections*. Dover.
- NACA Technical Report 824 — Summary of Airfoil Data.
- EASA CS-23 Amendment 5 — Normal-Category Aeroplanes.
- XFLR5 Documentation v6.x — Analysis methods and validation.
