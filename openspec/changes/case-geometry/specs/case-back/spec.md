## ADDED Requirements

### Requirement: Back shell has correct outer dimensions

`back.scad` SHALL produce a shell with outer dimensions
`case_w × case_h × back_depth` (nominal: 135×210×20mm portrait). Wall
thickness SHALL be `wall_t` (nominal: 2mm) on all sides and the base.

#### Scenario: Back renders at correct outer size

- **WHEN** `back.scad` is rendered in OpenSCAD
- **THEN** the bounding box matches `case_w × case_h × back_depth`

---

### Requirement: Electronics cavity fits the Pi+PiSugar stack

`back.scad` SHALL provide a cavity zone for the Pi Zero 2W + PiSugar 3 stack
(65×30mm footprint, depth `elec_depth = 15.7mm`) with `tol` clearance on each
side. The HAT is **not** stacked — it occupies a separate adjacent zone.

#### Scenario: Pi+PiSugar stack fits in cavity zone

- **WHEN** the electronics zone dimensions are `(65 + 2*tol) × (30 + 2*tol) × elec_depth`
- **THEN** the nominal Pi+PiSugar stack (65×30×15.7mm) fits with clearance

---

### Requirement: HAT cavity fits the Waveshare HAT board

`back.scad` SHALL provide a cavity zone for the Waveshare HAT (30×66mm
footprint rotated 90°, height 9.5mm) adjacent to the Pi stack at
X=65–95mm.

#### Scenario: HAT fits in its zone

- **WHEN** the HAT zone is (30 + 2*tol) × (66 + 2*tol) at X=65mm
- **THEN** the nominal HAT board (30×66mm) fits with clearance

---

### Requirement: Battery cavity fits the PiSugar 3 battery

`back.scad` SHALL provide a cavity zone for the battery (28×59mm footprint,
depth 12.5mm) with compartment walls of height `bat_depth = 12.5mm` fully
containing the battery.

#### Scenario: Battery fits in cavity zone

- **WHEN** the battery zone dimensions are `(28 + 2*tol) × (59 + 2*tol)`
- **THEN** the nominal battery (28×59×12.5mm) fits with clearance

---

### Requirement: Compartment ribs locate components

`back.scad` SHALL include internal ribs on the back plate floor separating
the battery bay, Pi stack zone, and HAT zone. Rib heights: battery bay walls
`bat_depth = 12.5mm`; Pi stack / HAT bay walls 10mm.

#### Scenario: Ribs reach correct height

- **WHEN** `back.scad` is rendered
- **THEN** battery bay ribs reach Z=`wall_t + bat_depth = 14.5mm` and Pi
  stack / HAT bay ribs reach Z=`wall_t + 10mm = 12mm`

---

### Requirement: Display panel seated by L-bracket blocks and centre column pads

`back.scad` SHALL include four corner L-bracket blocks (15×15mm XY, height
`back_depth - wall_t`) with a step shelf at Z=`back_depth - disp_thickness
= 18.75mm`, providing lateral stops on all four panel edges and a seating
surface for the panel back face.

`back.scad` SHALL include three centre column pads (15×15mm XY, fully
recessed — top face at Z=18.75mm) at mid-display Y, at the left edge, centre,
and right edge of the display, providing mid-span support.

#### Scenario: Display panel seats at correct Z

- **WHEN** `back.scad` is rendered
- **THEN** the panel shelf on all L-bracket blocks is at Z=`back_depth − disp_thickness`
- **AND** the panel front face at Z=`back_depth` is flush with the mating face

---

### Requirement: Rabbet cut on all four inner walls at mating face

`back.scad` SHALL subtract a 1mm-wide × 1.5mm-deep rabbet from the inner face
of all four walls at the mating face (Z=`back_depth`), accepting the tongue
ring from `front.scad`.

#### Scenario: Tongue ring seats in rabbet

- **WHEN** `assembly.scad` is rendered with front and back positioned
- **THEN** the front tongue ring (0.8mm × 1.3mm) fits inside the back rabbet
  with `tol/2` clearance per face

---

### Requirement: M2 side screw holes in left and right walls

`back.scad` SHALL include four horizontal through-holes (2 per side) in the
left and right outer walls at Z=11mm from back exterior, sized for M2 screws
with a 3.8mm recessed head pocket flush with the outer wall face.

#### Scenario: Screw holes align with nut tower centres

- **WHEN** `assembly.scad` is rendered
- **THEN** screw hole axes align with the captured hex-nut centres in the
  front plate towers at Y≈42mm and Y≈168mm

---

### Requirement: South wall connector pockets and charging notch

`back.scad` SHALL provide access cutouts on the south face for all
south-facing connectors and buttons:

- **USB-C charging notch**: `usbc_notch_w × usbc_notch_h` (nominal: 12×4mm)
  for cable access, centred on PiSugar 3 USB-C at X=53.5mm
- **Combined µUSB+USB-C outer pocket**: housing clearance for Pi Zero µUSB OTG
  (X=54mm) and PiSugar USB-C (X=53.5mm), merged into one cutout
  (X=47.25–59.95mm)
- **Left µUSB outer pocket**: housing clearance for Pi Zero µUSB power
  (X=41.4mm), individual cutout (housing_w=11.9mm, right edge X=47.35mm)
- **Mini HDMI pocket**: housing clearance for Pi Zero mini HDMI (X=12.4mm,
  12mm wide, 5mm tall, protrudes 8.5mm beyond PCB edge)

#### Scenario: All south-facing connectors are accessible

- **WHEN** `back.scad` is rendered
- **THEN** a USB-C charging notch of at least 12×4mm is present at X≈53.5mm
- **AND** outer housing pockets clear the µUSB and HDMI connector bodies on
  the south face

---

### Requirement: Magnet recesses on back plate inner face

`back.scad` SHALL include two circular recesses (diameter 15mm, depth 1.5mm)
on the back plate inner face for glued retention magnets: one above the
PiSugar board and one above the battery.

#### Scenario: Magnet recesses are present at correct positions

- **WHEN** `back.scad` is rendered
- **THEN** two circular recesses of diameter 15mm and depth 1.5mm are present
  on the inner face, one centred over the PiSugar zone and one centred over
  the battery zone

---

### Requirement: Button carrier support structures

`back.scad` SHALL include U-channel support columns on internal walls that
provide a Z=14mm ledge for the button carrier to rest on, plus retain walls
(Z=14–18mm) outside the carrier Y span (6.5–28.5mm) that lock the carrier in
Y after insertion from the mating face.

#### Scenario: Carrier seats and locks

- **WHEN** the carrier is inserted vertically from Z=20mm to Z=14mm
- **THEN** retain walls do not obstruct insertion (they are outside carrier Y span)
- **AND** once seated, retain walls rise above carrier edges and block Y movement

---

### Requirement: Flex tabs for PiSugar power and custom buttons

`back.scad` SHALL include two flex tabs on the south inner wall aligned with
the PiSugar 3 power button (X=11.5mm) and custom button (X=43.5mm). Each tab
is freed by three 0.5mm slot cuts (U-shape), 6mm × 4mm × 2mm, with the hinge
on the right short edge (Z-direction bending). An anti-droop pillar at the
free end snaps on first press.

#### Scenario: Flex tabs are present at correct positions

- **WHEN** `back.scad` is rendered
- **THEN** two U-slot flex tabs are visible on the south inner wall, centred
  at X=11.5mm and X=43.5mm, each with three 0.5mm slot cuts and an
  anti-droop pillar at the free end
