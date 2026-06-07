// Front bezel — display window, tongue joint, nut trap towers

// spellchecker:ignore openscad polyround toleranced

include <params.scad>
include <../../../../vendor/openscad-round-anything/polyround.scad>
use <utils.scad>

// Outer profile (CCW, radiiPoints = [x, y, r])
_outer = [
    [0,      0,      fillet_r],
    [case_w, 0,      fillet_r],
    [case_w, case_h, fillet_r],
    [0,      case_h, fillet_r]
];

// Display window: uses same _disp_x as back shell (active screen centred, narrow border left)
_disp_y = btn_area_h + (case_h - btn_area_h - display_h) / 2;

module _btn_cutout() {
    hole_chamfer_fillet_cutout(
        r0    = btn_hole_diameter / 2,
        fr    = btn_fillet_r,
        h     = front_depth + 0.2,
        zt    = front_depth + 0.1,
        alpha = edge_overhang_angle,
        fn    = 20
    );
}

module front() {
    difference() {
        // Outer solid: chamfer+fillet at z=front_depth (outer face), sharp at z=0 (mating face)
        chamfer_fillet_extrude(front_depth, fillet_r, edge_overhang_angle, fn=20)
            polygon(polyRound(_outer, 32));

        // Display window — active screen area only; origin at _screen_x / panel bottom + short border
        translate([_screen_x, _disp_y + display_border_short, -0.1])
            chamfer_fillet_extrude(front_depth + 0.2, fillet_r, edge_overhang_angle, fn=20, invert=true)
                square([screen_area_w, screen_area_h]);

        // Button holes: 4×2 grid in btn_area_h zone, through z (front face)
        for (col = [0 : btn_cols - 1])
            for (row = [0 : btn_rows - 1])
                translate([
                    (col + 0.5) * btn_zone_w,
                    (row == 0 ? btn_row_y1 : btn_row_y2),
                    -0.1
                ])
                    _btn_cutout();

    }

    // Mating tongue: protrudes below z=0, fits into back rabbet
    // tol/2 clearance on each face; inner hollow clears back's un-rabbeted inner wall
    _tx0 = wall_t - rabbet_w + tol / 2;
    _tw  = rabbet_w - tol;
    _td  = rabbet_d - tol;
    difference() {
        translate([_tx0, _tx0, -_td])
            cube([case_w - 2*_tx0, case_h - 2*_tx0, _td]);
        translate([_tx0 + _tw, _tx0 + _tw, -_td - 0.1])
            cube([case_w - 2*(_tx0 + _tw), case_h - 2*(_tx0 + _tw), _td + 0.2]);
    }

    // Hex-nut trap towers: hang from inner face (z=0) beside left and right walls.
    // Nut slides in from the outer Y face of the tower (side-loading).
    // Pocket is closed in Z (top and bottom), so gravity can never push the nut out
    // regardless of how the plate is flipped. A 0.1mm Z-step at the entry retains it.
    // Closed inner Y wall prevents the nut being driven out by the screw.
    _nt_d  = nut_t  + 2;        // X depth: 1mm wall + nut + 1mm wall = 4mm
    _nt_w  = tower_w;
    _nt_zc = -(back_depth - front_depth) / 2;  // nut Z centre: mid assembled-depth (front.scad local)
    _nt_px = (_nt_d - nut_t - tol) / 2;  // nut pocket X offset (centres nut in X)

    for (bx = [wall_t, case_w - wall_t - _nt_d])
        for (sy = side_screw_y)
            difference() {
                // Tower body
                translate([bx, sy - _nt_w / 2, -tower_h])
                    cube([_nt_d, _nt_w, tower_h]);

                // Screw clearance hole through tower — shank only, head stays in case wall
                translate([bx - 0.1, sy, _nt_zc])
                    rotate([0, 90, 0])
                        cylinder(d=screw_boss_id, h=_nt_d + 0.2, $fn=16);

                // Nut pocket entry: outer Y face, tight in Z (nut_af, no tol) → snap-in
                translate([bx + _nt_px, sy + _nt_w / 2 - 0.5, _nt_zc - nut_af / 2 - 0.1])
                    cube([nut_t + tol, 0.5 + 0.1, nut_af + 0.2]);

                // Nut pocket interior: toleranced in Z, closed at inner Y wall
                translate([bx + _nt_px, sy + _nt_w / 2 - 0.5 - (nut_af + tol), _nt_zc - (nut_af + tol) / 2 - 0.1])
                    cube([nut_t + tol, nut_af + tol + 0.1, nut_af + tol + 0.2]);

                // Ejection hole (2mm) through inner Y wall — push a pin to release nut
                translate([bx + _nt_d / 2, sy - _nt_w / 2 - 0.1, _nt_zc])
                    rotate([-90, 0, 0])
                        cylinder(d=2, h=_nt_w - 0.5 - (nut_af + tol) + 0.2, $fn=16);
            }
}

front();
