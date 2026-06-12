<!-- spellchecker:ignore insertable minkowski openscad polyround -->

## Notes

- [notes/physical-design.md](notes/physical-design.md) — all verified
  dimensions: case, display, electronics stack, component measurements,
  assembly hardware, button layout, and deliberate omissions
- [notes/button-wiring.md](notes/button-wiring.md) — GPIO pin soldering
  technique and wire routing notes (written when HAT was stacked; 11mm
  clearance constraint no longer applies with side-by-side HAT layout)

### Build guide references

- 3D printed case design notes → [`docs/build_guide.md#3d-printed-case`](../../../docs/build_guide.md#3d-printed-case)
- Hardware assembly steps → [`docs/build_guide.md#assembly-order`](../../../docs/build_guide.md#assembly-order)

## Context

All geometry derives from `notes/physical-design.md`, which contains
dimensions verified by direct measurement. Back depth (20mm) is the one
value still marked unconfirmed — verify with assembled hardware before the
final print (task 1.1).

The device is used in **portrait orientation**: the long panel edge (170mm)
is vertical. The case is therefore taller than wide, with 8 tactile buttons
(4×2 grid) on the short bottom edge. Outer dimensions: 135mm wide × 210mm
tall (135mm clears M2 nut towers with margin; 210 = 2+170+35+2+1).

```text
FRONT VIEW (portrait, assembled):
┌──────────────────┐  ← top
│   bezel (≥2mm)   │
│  ┌────────────┐  │
│  │  display   │  │  ← 100mm wide × 165mm tall active opening
│  │  window    │  │
│  │            │  │
│  └────────────┘  │
│   bezel          │
├──────────────────┤  ← rabbet/tongue joint + M2 side screws
│ [1] [2] [3] [4]  │  ← top button row (btn_1–btn_4)
│ [5] [6] [7] [8]  │  ← bottom button row (btn_5–btn_8)
└──────────────────┘  ← bottom
     ← 135mm →

SIDE CROSS-SECTION:
┌──────────┐  ← front face (2mm)
│  bezel   │
├──────────┤  ← rabbet/tongue joint + M2 side screws
│ ┌──┐┌─┐  │
│ │el││b│  │  electronics 15.7mm / battery 12.5mm deep cavities
│ └──┘└─┘  │
└──────────┘  ← back face (20mm back depth)
```

## Goals / Non-Goals

**Goals:**

- Produce printable geometry that fits the actual hardware stack
- Parameterize all dimensions so tolerances are adjustable without
  touching shape logic
- Rabbet/tongue joint for self-alignment + M2 side-entry screws for retention
- Eight button holes (4×2 grid) on the short bottom edge; buttons are
  unlabeled hardware (labels rendered on screen — see ADR 0007)

**Non-Goals:**

- Rounded/organic exterior styling — rectangular with chamfered edges only
- Full multi-material print instructions (`leds.scad` provides an optional
  transparent LED window body for multi-material printers; single-filament
  users skip it)

## Decisions

### Rabbet/tongue joint + M2 side-entry screws

Rabbet cut (1mm wide × 1.5mm deep) in all four inner walls of the back shell
at the mating face; matching tongue ring (0.8mm wide × 1.3mm deep) on the
front plate projects into the rabbet. Provides self-alignment and eliminates
visible seam gaps at the joint line.

Retention: four M2 side-entry screws pass horizontally through the back shell
left/right walls and thread into captured hex nuts in towers on the front
plate inner face (2 towers per side, at Y≈42mm and Y≈168mm).

Snap-fit considered and dropped: clips fatigue over repeat open/close cycles,
conflict geometrically with the rabbet cut at the mating face, and would be a
third redundant retention mechanism alongside the joint and screws.

### HAT placed side-by-side with Pi stack, not stacked

The Waveshare HAT board (30×66mm) is placed adjacent to the Pi+PiSugar stack
at X=65–95mm, rotated 90°, and connected via hand-wired jumpers to the GPIO
header pins. This reduces the electronics stack depth from ~22mm (stacked) to
15.7mm (GPIO header height only), allowing `back_depth = 20mm`.

### Button holes sized for 6×6mm tactile switches with printed caps

Switches: 6×6mm footprint, 6mm total height (3mm base + 3mm stem), 3.5×3.5mm
square stem. Switches are pre-assembled onto an insertable carrier. Printed
caps (10mm OD, 2mm tall, 1mm socket depth) press-fit onto stems and set the
visible hole size. Hole diameter: 10mm (cap OD with `tol` clearance).

### Button carrier: insertable sub-assembly

Eight tactile switches are mounted on a printed carrier that inserts vertically
from the mating face and seats at Z=14mm on U-channel ledges. Retain walls
(Z=14–18mm) outside the carrier Y span lock it in place after insertion.
Contact rails on the carrier top face bridge the 2mm gap to the front plate
inner face. Allows pre-assembly, testing, and replacement without full case
disassembly.

### Display panel seated in back shell (L-brackets + column pads)

Four corner L-bracket blocks (15×15mm XY, full interior height) provide
lateral stops and a step shelf at Z=`back_depth − disp_thickness = 18.75mm`.
Three fully-recessed centre column pads (top at shelf height) provide
mid-span support. Panel front face sits flush with the back shell mating face
(Z=20mm). Replaces earlier "open cutout with clamping" approach — positive
location prevents lateral rattle.

### Exterior edges filleted with Round-Anything (3mm radius)

3D outer-edge fillets via [Round-Anything](https://github.com/Irev-Dev/Round-Anything)
(`polyRoundExtrude`) at `fillet_r=3mm`. This avoids `minkowski()` (slow, breaks
hole geometry) and keeps all corner radii in a single param.
Vendored at `vendor/openscad-round-anything/polyround.scad`.

### Parametric tolerance offsets

All inter-part fits (tongue/rabbet gap, button hole, cavity clearance) are
expressed as `tol = 0.2` (default FDM tolerance) added/subtracted from
nominal dimensions. Changing one variable re-generates all dependent
geometry.

## Risks / Trade-offs

- **Back depth unconfirmed**: `back_depth = 20mm` gives 2.3mm clearance above
  the 15.7mm electronics stack (+ 2mm wall). Marked unconfirmed in
  physical-design.md — verify with assembled hardware before final print.
  → Mitigation: task 1.1 caliper measurement; increase `back_depth` if needed.

- **Nominal dimensions ≠ real hardware**: Dimensions in physical-design.md are
  verified by measurement where noted, but HAT placement and wire routing may
  require minor clearance adjustments.
  → Mitigation: draft-quality test print (task 6) before final print.

- **Button hole alignment**: Carrier positions switches; carrier ledge geometry
  must match the actual back shell. First test print will confirm.
  → Mitigation: carrier is a separate printed part — reprint carrier only if
  fit adjustment is needed.
