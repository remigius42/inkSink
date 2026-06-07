## 0. Vendor / Library

- [x] 0.1 Vendor Round-Anything at
        `vendor/openscad-round-anything/polyround.scad` (commit `061fef7`,
        2026-05-28); add VENDOR.md

## 1. Measure Hardware

All dimensions measured and recorded in `notes/physical-design.md`. Back
depth (20mm) is the one value still marked "unconfirmed, verify fits" —
confirm with assembled hardware before the final print.

## 2. `params.scad` — acceptance criteria

All values derived from `notes/physical-design.md`.

- [ ] 2.1 Outer case dimensions: `case_w=135`, `case_h=210`,
        `front_depth=2`, `back_depth=20`; `wall_t=2`, `tol=0.2`
- [ ] 2.2 Display params: `display_w=100`, `display_h=165`
        (active area); `disp_thickness=1.25`; border offsets per
        physical-design.md (wide 9.5mm, narrow 2.5mm, short edges 2mm)
- [ ] 2.3 Electronics: `elec_w=65`, `elec_l=30`, `elec_depth=15.7`;
        HAT: `hat_w=30`, `hat_l=66`, `hat_h=9.5`
- [ ] 2.4 Battery: `bat_w=28`, `bat_l=59`, `bat_depth=12.5`
- [ ] 2.5 Buttons: `btn_count=8`, `btn_rows=2`, `btn_cols=4`,
        `btn_hole_diameter=10`, `btn_area_h=35`
- [ ] 2.6 Rabbet/tongue joint: `rabbet_w=1`, `rabbet_d=1.5`
        (derived tongue: `rabbet_w-tol`, `rabbet_d-tol`)
- [ ] 2.7 M2 side-entry screws: `side_screw_z=11`,
        `side_screw_y=[42, 168]`; tower: `tower_d=3.6`, `tower_w=15`,
        `tower_h=17`
- [ ] 2.8 USB-C notch: `usbc_notch_w=12`, `usbc_notch_h=4`
- [ ] 2.9 Magnet recesses: `magnet_d=15`, `magnet_recess=1.5`

## 3. `front.scad` — acceptance criteria

- [ ] 3.1 Base plate: `cube([case_w, case_h, front_depth])`
- [ ] 3.2 Display window cutout with correct border offsets
- [ ] 3.3 Rabbet tongue ring on all four inner edges
- [ ] 3.4 8 button holes (4×2 grid, `btn_hole_diameter=10mm`) in
        `btn_area_h` zone
- [ ] 3.5 Four M2 side-entry screw towers (2 per side) with captured
        hex nut traps and ejection holes
- [ ] 3.6 Preview in OpenSCAD; verify window borders, tongue ring, towers

## 4. `back.scad` — acceptance criteria

- [ ] 4.1 Base shell: outer cube minus inner pocket (`wall_t` on sides and base)
- [ ] 4.2 Compartment ribs for battery bay (12.5mm), Pi stack, and HAT
        zone (10mm)
- [ ] 4.3 Display seating: four corner L-bracket blocks (15×15mm, shelf
        at Z=18.75mm) and three centre column pads (fully recessed, top at
        Z=18.75mm)
- [ ] 4.4 Rabbet on all four inner walls at mating face
        (`rabbet_w=1mm`, `rabbet_d=1.5mm`)
- [ ] 4.5 M2 horizontal screw holes in left/right walls (Z=11mm,
        with 3.8mm head pocket flush with outer face)
- [ ] 4.6 South wall: USB-C notch (12×4mm at X=53.5mm); combined
        µUSB+USB-C outer pocket (X=47.25–59.95); left µUSB outer pocket;
        Pi Zero mini HDMI pocket (X=12.4mm, 12mm wide, 5mm tall)
- [ ] 4.7 Magnet recesses on back plate inner face (×2, 15mm dia, 1.5mm deep)
- [ ] 4.8 Button carrier support columns: U-channel ledges at Z=14mm
        with retain walls Z=14–18mm outside carrier Y span
- [ ] 4.9 Flex tabs on south inner wall for PiSugar power (X=11.5mm)
        and custom (X=43.5mm) buttons; anti-droop pillar on each
- [ ] 4.10 Preview in OpenSCAD; verify all cavities, display seating,
        rabbet, south wall pockets, flex tabs visible

## 5. `assembly.scad` — acceptance criteria

- [ ] 5.1 Front and back positioned: back at z=0, front at z=`back_depth`
- [ ] 5.2 Tongue ring seats in rabbet in cross-section view
- [ ] 5.3 Screw tower axes align with screw holes in back walls

## 6. Apply draft implementations

Draft `.scad` files exist in `notes/`. Review each against the acceptance
criteria in sections 2–5 above, then copy to `hardware/case/`.

- [ ] 6.1 Review `notes/params.scad` → `hardware/case/params.scad`
- [ ] 6.2 Review `notes/front.scad` → `hardware/case/front.scad`
- [ ] 6.3 Review `notes/back.scad` → `hardware/case/back.scad`
- [ ] 6.4 Review `notes/assembly.scad` → `hardware/case/assembly.scad`;
        update include paths from `../../../../vendor/` to `../../vendor/`
- [ ] 6.5 Review `notes/carrier.scad` → `hardware/case/carrier.scad`
- [ ] 6.6 Review `notes/button.scad` → `hardware/case/button.scad`
- [ ] 6.7 Review `notes/leds.scad` → `hardware/case/leds.scad`
- [ ] 6.8 Review `notes/parts.scad` → `hardware/case/parts.scad`
- [ ] 6.9 Review `notes/utils.scad` → `hardware/case/utils.scad`

## 7. Test Print

- [ ] 7.1 Export `front.scad`, `back.scad`, `carrier.scad`, and `button.scad`
        to STL
- [ ] 7.2 Slice at draft quality (0.3mm layer, 20% infill) and print
- [ ] 7.3 Test fit: Pi+PiSugar stack, battery, HAT, carrier all seat correctly;
        tongue/rabbet joint aligns; M2 screws engage; south wall pockets clear
        all connectors
- [ ] 7.4 Adjust tolerance params as needed; re-print if required
- [ ] 7.5 Commit final STLs alongside `.scad` sources

## 8. Housekeeping

- [ ] 8.1 Run pre-commit hooks (`pre-commit run --all-files`) and fix any issues
- [ ] 8.2 Update `docs/build_guide.md` Physical Design section with finalized
  dimensions (depth, wall thickness, display recess) once caliper measurements
  and params are confirmed
- [ ] 8.3 Update `hardware/bom.md` Pi Zero 2W header note: pre-soldered headers
  are recommended (larger soldering target, avoids pad lift risk on GPIO pads)
  but not strictly required — the design places the Waveshare HAT side-by-side
  rather than stacked, so headers vs. no headers does not affect case depth
