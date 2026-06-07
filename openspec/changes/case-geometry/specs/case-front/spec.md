## ADDED Requirements

### Requirement: Front bezel has correct outer dimensions

`front.scad` SHALL produce a rectangular bezel with outer dimensions
`case_w × case_h × front_depth` (nominal: 135×210×2mm portrait). All
dimensions SHALL be driven by params.

#### Scenario: Front renders at correct outer size

- **WHEN** `front.scad` is rendered in OpenSCAD
- **THEN** the bounding box matches `case_w × case_h × front_depth`

---

### Requirement: Display window exposes the active screen area

`front.scad` SHALL subtract a rectangular cutout of `screen_area_w × screen_area_h`
(nominal: 100×165mm — active screen area of the Waveshare 7.5" panel)
positioned to leave the correct border on all sides (wide border 9.5mm on
one long edge, narrow border 2.5mm on the other, 2mm on short edges).

#### Scenario: Window cutout leaves correct borders

- **WHEN** `front.scad` is rendered
- **THEN** the border between outer edge and window opening matches the
  nominal panel border widths on all four sides

---

### Requirement: Rabbet tongue ring on all four inner edges

`front.scad` SHALL include a rectangular tongue ring protruding from the inner
face on all four sides: width `rabbet_w - tol = 0.8mm`, depth
`rabbet_d - tol = 1.3mm`. The tongue fits into the rabbet cut in `back.scad`
with `tol/2 = 0.1mm` clearance per face.

#### Scenario: Tongue ring fits in rabbet

- **WHEN** `assembly.scad` is rendered with front and back positioned
- **THEN** the tongue ring sits inside the back shell rabbet without interference

---

### Requirement: M2 side-entry screw towers on inner face

`front.scad` SHALL include four screw towers hanging from the inner face
beside the left and right walls (2 per side, at Y≈42mm and Y≈168mm). Each
tower: 3.6mm deep (X), 15mm wide (Y), 17mm tall (into back shell). Each
tower has a captured M2 hex nut trap (4mm AF, 1.6mm thick) with a 0.1mm
retention step and a 2mm ejection hole on the inner face.

#### Scenario: Screw towers align with back shell screw holes

- **WHEN** `assembly.scad` is rendered
- **THEN** each tower nut centre aligns with the corresponding horizontal
  screw hole in the back shell left/right walls

---

### Requirement: Eight button holes in lower front face (4×2 grid)

`front.scad` SHALL subtract eight cylindrical holes of diameter
`btn_hole_diameter = 10mm` (sized for printed cap outer diameter with `tol`
clearance) through the `btn_area_h = 35mm` zone (lower 35mm of the front
face), arranged in a 4×2 grid. The four columns SHALL be evenly distributed
across the available width. Two rows SHALL be vertically centred within
`btn_area_h`.

#### Scenario: Button holes span available width

- **WHEN** `front.scad` is rendered
- **THEN** outermost button column centres are at `btn_margin_x` from each
  edge, and all columns are evenly spaced at `btn_x_spacing`
