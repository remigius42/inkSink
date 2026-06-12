<!-- spellchecker:ignore insertable -->

## Why

The `repo-scaffold` change created stub `.scad` files. Hardware is now in
hand, making it possible to measure real tolerances and implement printable
geometry. This change produces a functional multi-part printable case (front shell,
back shell, button carrier, button caps) ready to slice and print.

## What Changes

- `hardware/case/params.scad` — all named dimensions, tolerances, and
  configurable parameters (case dimensions, wall thickness, display offsets,
  component positions, rabbet/tongue joint, M2 tower geometry, button layout,
  magnet recesses)
- `hardware/case/front.scad` — front bezel with display window cutout,
  rabbet tongue ring, M2 side-entry screw towers with captured hex nut traps,
  and eight button holes (4×2 grid) in the lower face
- `hardware/case/back.scad` — back shell with Pi+PiSugar electronics cavity,
  HAT cavity, battery cavity, compartment ribs, display seating L-bracket
  blocks and centre column pads, rabbet cut, M2 side screw holes, USB-C
  charging notch, magnet recesses, button carrier U-channel supports, and
  PiSugar flex tabs
- `hardware/case/carrier.scad` — insertable button carrier: 8 tactile switch
  seats, contact rails bridging to front plate, U-channel feet
- `hardware/case/button.scad` — printed cap that press-fits onto 6×6mm tactile
  switch stem and passes through the 10mm front-bezel hole
- `hardware/case/assembly.scad` — front, back, and carrier positioned in
  assembled orientation; verifies tongue/rabbet alignment, screw tower
  alignment, and carrier seating
- `hardware/case/leds.scad` — optional LED indicator windows for
  multi-material printing; assign transparent filament to this body in the
  slicer; single-filament users skip it (back shell has through-holes)
- `hardware/case/parts.scad` — reference geometry modules (bounding-box
  placeholders for display, battery, Pi stack, HAT) for fit verification in
  OpenSCAD preview; not printed
- `hardware/case/utils.scad` — shared geometry utilities (connector stepped
  cutouts, chamfered through-holes) used by front.scad and back.scad

## Capabilities

### New Capabilities

- `case-front`: printable front bezel geometry
- `case-back`: printable back shell geometry
- `case-carrier`: printable button carrier sub-assembly
- `case-button-cap`: printable button cap for 6×6mm tactile switches
- `case-leds`: optional transparent LED window body for multi-material printing

### Modified Capabilities

## Impact

- Replaces stub content in the four `.scad` files from `repo-scaffold`; adds
  `carrier.scad`, `button.scad`, `leds.scad`, `parts.scad`, and `utils.scad`
- No software or Ansible changes
- Requires OpenSCAD to preview; requires a 3D printer to produce physical parts
