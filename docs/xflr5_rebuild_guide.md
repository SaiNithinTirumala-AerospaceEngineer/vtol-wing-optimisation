# XFLR5 Model Rebuild Guide

**Wing:** Hybrid VTOL Transition Wing  
**Software:** XFLR5 v6.x (free download — xflr5.tech)  
**Time required:** ~45 minutes

---

## Step 1 — Install and open XFLR5

Download from https://xflr5.tech and install.  
Open the application. You will land on the **Direct Foil Design** view.

---

## Step 2 — Load the three airfoils

1. Go to **Foil → NACA Foils**
2. In the dialog, type `0012` → click **OK**
3. Repeat — type `2415` → **OK**
4. Repeat — type `4412` → **OK**

All three now appear in the foil list on the left panel.

To view them overlaid:
- Go to **Foil → Current Foil** and cycle through each
- For a side-by-side screenshot: all three will show in the main canvas
  when none is selected — take your `assets/airfoil_profiles.png` screenshot here

---

## Step 3 — Run polars for each airfoil (XFoil analysis)

Do this for **each of the three airfoils** in turn.

1. Click on the airfoil name in the left panel to select it
2. Go to **Analysis → Batch Analysis**
3. Set the following:

| Field | Value |
|---|---|
| Type | Type 1 (fixed speed) |
| Reynolds number | 500000 |
| AoA min | −4 |
| AoA max | 14 |
| AoA step | 1 |
| Mach | 0 |
| Ncrit | 9 |

4. Click **Analyse** — wait for completion (green progress bar)
5. The polar curve appears in the lower panel

Repeat for all three airfoils.

### Export polar CSVs

For each airfoil after analysis:

1. In the polar graph panel, right-click → **Export polar**  
   *Or:* **Foil → Export → Export Polar**
2. Save to your `data/` folder with these exact names:
   - `xflr5_polar_naca0012.csv`
   - `xflr5_polar_naca2415.csv`
   - `xflr5_polar_naca4412.csv`

---

## Step 4 — Switch to Wing & Plane Design

Go to **Application → Wing & Plane Design**  
*(top menu — the view changes completely)*

---

## Step 5 — Define the wing

1. Click **Wing → New Wing**
2. The wing editor dialog opens
3. Set the wing name: `Hybrid_VTOL_Wing`

### Enter the wing sections

The table in the wing editor has one row per spanwise section.  
Click **Insert** or **Add** to add rows. Enter these values:

| Section | Y (m) | Chord (m) | Offset (m) | Dihedral (°) | Twist (°) | Foil |
|---|---|---|---|---|---|---|
| 1 (root) | 0.000 | 0.283 | 0.000 | 0.0 | 0.0 | NACA 0012 |
| 2 (mid)  | 0.600 | 0.283 | 0.000 | 0.0 | 0.0 | NACA 2415 |
| 3 (tip)  | 1.200 | 0.283 | 0.000 | 0.0 | 0.0 | NACA 4412 |

> Note: Y is the **semi-span** position. XFLR5 mirrors the wing automatically.  
> Total span = 2 × 1.2 m = **2.4 m** ✓

4. In the **Foil** column, click each cell and select the correct airfoil
   from the dropdown
5. Click **OK** to save the wing

### Verify geometry

After creating the wing, check the properties panel shows:
- Span: **2.4 m**
- Area: **≈ 0.48 m²**
- AR: **≈ 6.0**
- MAC: **≈ 0.283 m**

If these match, the model is consistent with the Python analysis.

---

## Step 6 — Take the assets screenshots

Before running analysis, take the wing geometry screenshots.

**Screenshot 1 — Isometric view** → save as `assets/vtol_wing_isometric.png`
- Press **numpad 5** or go to **View → Iso View**
- The wing shows in 3D with airfoil sections visible
- Take screenshot with **Ctrl+S** or use Windows Snipping Tool

**Screenshot 2 — Wing analysis panel** → save as `assets/xflr5_wing_analysis.png`
- This is taken after Step 7 (analysis) — come back here
- The panel shows the Cl spanwise distribution across the wing

---

## Step 7 — Run the wing analysis (LLT)

1. Go to **Analysis → Define Analysis**
2. Select **Wing Analysis**
3. Method: **Lifting Line Theory (LLT)**
4. Set:

| Field | Value |
|---|---|
| Density | 1.225 kg/m³ |
| Viscosity | 1.789e-5 |
| AoA range | −4° to 14° |
| AoA step | 1° |

5. Click **Analyse**

After analysis completes:
- The spanwise Cl distribution appears — take screenshot → `assets/xflr5_wing_analysis.png`
- The polar curves appear in the bottom panel

---

## Step 8 — Export the wing polar

1. In the polar results panel, right-click → **Export**
2. Save as `data/Hybrid_VTOL_Wing_Analysis.csv`

This replaces the placeholder CSV already in the repo with real XFLR5 output.

---

## Step 9 — Commit the assets and data

Once you have:
```
assets/vtol_wing_isometric.png      ← XFLR5 isometric view
assets/xflr5_wing_analysis.png      ← Cl spanwise distribution
assets/airfoil_profiles.png         ← three foils overlaid
data/xflr5_polar_naca0012.csv       ← XFoil polar export
data/xflr5_polar_naca2415.csv
data/xflr5_polar_naca4412.csv
data/Hybrid_VTOL_Wing_Analysis.csv  ← wing LLT polar export
```

Commit with:
```
feat: add XFLR5 model assets and polar exports

- Add wing isometric, analysis panel, and airfoil profile screenshots
- Add XFoil polar CSVs for NACA 0012, 2415, 4412 at Re=500,000
- Add LLT wing polar export — Hybrid_VTOL_Wing_Analysis.csv
- Wing geometry: span=2.4m, chord=0.283m, AR=6, no sweep/dihedral
```

---

## Troubleshooting

**"Foil not found" in wing editor dropdown**  
→ You must load foils in Step 2 before switching to Wing & Plane Design.
Go back to Direct Foil Design, load all three, then switch.

**Analysis stops early / polar has gaps**  
→ Normal for LLT at high AoA (stall). The polar will simply stop
at the angle where convergence fails. This is expected behaviour.

**Wing area shows wrong value**  
→ Check that Y positions are in metres, not millimetres.
XFLR5 defaults vary by installation.

**Can't find Export Polar option**  
→ Right-click directly on the polar curve graph (not the foil canvas).
The export option appears in the context menu.
