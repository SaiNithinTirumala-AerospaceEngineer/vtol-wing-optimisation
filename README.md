# Aerodynamic-Structural Optimisation of a Hybrid VTOL Transition Wing

![Python](https://img.shields.io/badge/Python-3.x-blue)
![XFLR5](https://img.shields.io/badge/Analysis-XFLR5-green)
![ANSYS](https://img.shields.io/badge/FEA-ANSYS%202024%20R1-teal)
![License](https://img.shields.io/badge/License-MIT-lightgrey)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

## Problem statement

Hybrid VTOL aircraft must transition between hover and cruise flight modes,
requiring a wing that simultaneously generates sufficient lift at low speeds
during transition and maintains aerodynamic efficiency in cruise. A single
airfoil profile cannot optimise for both conditions. This project analyses a
spanwise combination of NACA 0012, NACA 2415, and NACA 4412 profiles to
characterise the aerodynamic trade-offs and quantify the structural, weight,
and flight performance implications of each configuration.

## Design overview

The hybrid VTOL wing design combines three NACA airfoils across the span,
each selected for a specific aerodynamic role:

| Airfoil | Location | Role |
|---------|----------|------|
| NACA 0012 | Root | Symmetric profile — predictable VTOL behaviour |
| NACA 2415 | Mid-span | Cambered — improved cruise lift-to-drag ratio |
| NACA 4412 | Tip | Higher camber — enhanced low-speed lift |

*Wing design and airfoil polar analysis performed in XFLR5.*

## Methodology

### Phase 1 — XFLR5 aerodynamic analysis
Panel method (Lifting Line Theory) applied to each airfoil across an angle
of attack sweep from −4° to 18°. Lift coefficient (Cl), drag coefficient (Cd),
and moment coefficient (Cm) extracted and exported as CSV for each profile.

### Phase 2 — Python performance modelling
CSV polar data fed into six purpose-built Python modules covering:
- Aerodynamic lift and drag vs airspeed
- Structural stress, bending moment, and shear force distribution
- Wing weight estimation (two independent datasets)
- Power system sizing and thrust-to-weight ratio
- Flight endurance prediction
- Control system dynamics analysis

## Results

*Plots and quantified results will be added as each module is completed.*

## Validation

*Validation table comparing XFLR5 outputs against published NACA data
will be added upon completion of aerodynamic analysis module.*

## Limitations and future scope

- Structural model uses simplified beam theory — full 3D FEA with composite
  layup in ANSYS Mechanical is a planned extension
- XFLR5 panel method underestimates drag at high angles of attack — a
  validated RANS CFD analysis (OpenFOAM) is identified as future work
- AI optimisation using NSGA-II across all three airfoil configurations
  simultaneously is the primary planned extension

## How to run

```bash
git clone https://github.com/SaiNithinTirumala-AerospaceEngineer/vtol-wing-optimisation.git
cd vtol-wing-optimisation
pip install -r requirements.txt
python src/aerodynamic_analysis.py
```

## References

- Abbott, I.H. and Von Doenhoff, A.E. (1959) *Theory of Wing Sections*.
  Dover Publications.
- NACA Technical Report 586 — Aerodynamic characteristics of aerofoils.
- XFLR5 Documentation v6.x