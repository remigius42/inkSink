// Back shell — open tray with internal compartment walls and snap tabs
// Draft; replace hardware/case/back.scad once reviewed.
include <params.scad>
include <../../../../vendor/openscad-round-anything/polyround.scad>
use <utils.scad>
use <parts.scad>

_outer = [
    [0,      0,      fillet_r],
    [case_w, 0,      fillet_r],
    [case_w, case_h, fillet_r],
    [0,      case_h, fillet_r]
];

// Internal walls only need enough height to stop parts wiggling
_wall_h     = 10;
_bat_wall_h = 12.5;  // matches bat_depth so battery sits fully enclosed

module back() {
    difference() {
        union() {
            // Open tray: outer rounded solid minus hollow interior, keeps base + perimeter walls
            difference() {
                // chamfer+fillet at z=0 (base/exterior face); mirror puts the feature at the bottom
                translate([0, 0, back_depth])
                    mirror([0, 0, 1])
                        chamfer_fillet_extrude(back_depth, fillet_r, edge_overhang_angle, fn=20)
                            polygon(polyRound(_outer, 32));
                translate([wall_t, wall_t, wall_t])
                    cube([case_w - 2*wall_t, case_h - 2*wall_t, back_depth - wall_t + 0.1]);
            }

            // Internal wall: vertical divider between Pi Zero+battery area and HAT area
            // Spans Y = wall_t to top of battery (elec_l + bat_l)
            translate([_hat_x, wall_t, wall_t])
                cube([wall_t, elec_l + bat_l, _bat_wall_h]);

            // Internal wall: top edge of Pi Zero area (closes Pi stack in +Y)
            // Runs from left inner wall to battery left edge
            translate([wall_t, _bat_y, wall_t])
                cube([_bat_x - wall_t, wall_t, _wall_h]);

            // Internal wall: left side of battery (stops battery sliding toward centre)
            translate([_bat_x - wall_t, _bat_y, wall_t])
                cube([wall_t, bat_l, _bat_wall_h]);

            // Internal wall: right side of HAT bay
            translate([_hat_x + hat_w, wall_t, wall_t])
                cube([wall_t, hat_l, _wall_h]);

            // Internal wall: top of HAT bay
            translate([_hat_x, _hat_y + hat_l, wall_t])
                cube([hat_w + wall_t, wall_t, _wall_h]);

            // Internal wall: top of battery bay — overlaps left-side and vertical-divider walls
            translate([_bat_x - wall_t, _bat_y + bat_l, wall_t])
                cube([bat_w + 2 * wall_t, wall_t, _bat_wall_h]);

            // Battery retaining lip: spans full outer width (incl. side walls) at the top end
            // Connects flush to left wall, vertical divider, and top wall
            translate([_bat_x - wall_t, _bat_y + bat_l - 10, wall_t + bat_depth])
                cube([bat_w + 2*wall_t, 10 + wall_t, back_depth - wall_t - bat_depth - disp_thickness]);

            // Display holding blocks: 15×15mm pillars that straddle the display panel edge
            // Left blocks: centred on display left edge (_disp_x); outer half is the
            //   lateral stop, inner half has the disp_thickness step so the panel seats
            // Right blocks: inner face at display right edge; case wall is lateral stop,
            //   inner (centre-facing) half carries the seating step
            _pad   = 15;
            _pad_h = back_depth - wall_t;

            // Left-edge blocks: centred on _disp_x; outer half = lateral stop pillar
            // Step at back_depth-disp_thickness; non-cutaway rim reaches back_depth (mating face)
            // Top
            difference() {
                translate([_disp_x - _pad/2, _disp_y + display_h - _pad, wall_t])
                    cube([_pad, _pad, _pad_h]);
                translate([_disp_x, _disp_y + display_h - _pad - 0.1, back_depth - disp_thickness])
                    cube([_pad/2 + 0.2, _pad + 0.2, disp_thickness + 0.1]);
            }
            // Bottom: extends 5mm below display edge; step face at _disp_y locks panel in Y
            difference() {
                translate([_disp_x - _pad/2, _disp_y - 5, wall_t])
                    cube([_pad, _pad, _pad_h]);
                translate([_disp_x - 0.1, _disp_y, back_depth - disp_thickness])
                    cube([_pad/2 + 0.2, _pad - 5 + 0.1, disp_thickness + 0.1]);
            }

            // Right-edge blocks: right face flush with case inner wall (case_w - wall_t).
            // Cutaway covers display underside only (block left face → display right edge),
            // leaving the 5.5mm strip right of the display edge as lateral stop.
            // Top
            difference() {
                translate([case_w - wall_t - _pad, _disp_y + display_h - _pad, wall_t])
                    cube([_pad, _pad, _pad_h]);
                translate([case_w - wall_t - _pad - 0.1, _disp_y + display_h - _pad - 0.1, back_depth - disp_thickness])
                    cube([_disp_x + display_w - (case_w - wall_t - _pad) + 0.2, _pad + 0.2, disp_thickness + 0.1]);
            }
            // Bottom
            difference() {
                translate([case_w - wall_t - _pad, _disp_y - 5, wall_t])
                    cube([_pad, _pad, _pad_h]);
                translate([case_w - wall_t - _pad - 0.1, _disp_y, back_depth - disp_thickness])
                    cube([_disp_x + display_w - (case_w - wall_t - _pad) + 0.2, _pad - 5 + 0.1, disp_thickness + 0.1]);
            }

            // Centre column pads: fully recessed (top flush with display back face, no rim)
            // Left-edge, centre, and right-edge — all at mid-height of display
            _col_y = _disp_y + (display_h - _pad) / 2;
            for (px = [_disp_x + 10,
                       _disp_x + (display_w - _pad) / 2,
                       _disp_x + display_w - 10 - _pad])
                translate([px, _col_y, wall_t])
                    cube([_pad, _pad, back_depth - wall_t - disp_thickness]);

            // Power button marker: 2.5mm dome, 0.4mm proud of south wall exterior
            // Centred on the power-button flex tab (xc=11.5); only on power button, not custom button
            translate([_elec_x + 11.5, 0, wall_t - btn_slot_kerf/2 + 2])
                rotate([90, 0, 0])
                    cylinder(d=2.5, h=0.4, $fn=32);

            // Carrier support columns — U-channel profile at three X positions
            // Carrier Y zone: _cni..._csi (6.5–28.5mm). South/north retain walls above Z=14
            // lock carrier in Y; carrier footprint clears retain walls during Z insertion.
            {
                _cni = btn_row_y1 - 4;                    //  6.5mm carrier south edge
                _csi = btn_row_y2 + 4;                    // 28.5mm carrier north edge
                _csy = wall_t;                             //  2mm  outer south (into south wall)
                _cny = side_screw_y[0] - tower_w/2 - 1;  // 33.5mm outer north (fuses with nut tower)
                _clz = back_depth - 6;                    // 14mm  carrier floor
                // Three columns: Pi stack right wall, HAT-bay right wall, right-wall ledge
                for (col = [[_hat_x,             wall_t],
                             [_hat_x + hat_w,    wall_t],
                             [case_w - wall_t - 3, 3   ]]) {
                    // South/north retain: extend to mating face; rabbet trims to Z=18.5
                    translate([col[0], _csy, wall_t])
                        cube([col[1], _cni - _csy, back_depth - wall_t]);
                    // Ledge in carrier zone: only to carrier floor (carrier rests here)
                    translate([col[0], _cni, wall_t])
                        cube([col[1], _csi - _cni, _clz - wall_t]);
                    // North retain
                    translate([col[0], _csi, wall_t])
                        cube([col[1], _cny - _csi, back_depth - wall_t]);
                }
            }

            // Left-wall diagonal ledge — carrier support south of SD card
            // PCB stack occupies Z < 10.75mm at left wall; ledge starts exactly there
            // and rises at 40° outward to carrier bottom (Z=14mm, = back_depth-6)
            {
                _ll_z0 = 11;                               // just above SD card top (10.75mm)
                _ll_z1 = back_depth - 6;                   // carrier bottom = 14mm
                _ll_dx = (_ll_z1 - _ll_z0) / tan(40);     // ramp reach ≈ 3.87mm
                _ll_y0 = wall_t;                           // south inner wall face
                _ll_y1 = side_screw_y[0] - tower_w/2 - 1; // 33.5mm — fuses with nut tower receiver
                _ll_cni = btn_row_y1 - 4;                  // 6.5mm carrier south edge
                _ll_csi = btn_row_y2 + 4;                  // 28.5mm carrier north edge
                // Ramp spans full Y range
                translate([0, _ll_y1, 0])
                    rotate([90, 0, 0])
                    linear_extrude(_ll_y1 - _ll_y0)
                        polygon([
                            [wall_t,              _ll_z0],
                            [wall_t,              _ll_z1],
                            [wall_t + _ll_dx,     _ll_z1]
                        ]);
                // Vertical retain walls above wedge tip: extend to mating face (rabbet trims to Z=18.5)
                translate([wall_t, _ll_y0, _ll_z1])
                    cube([_ll_dx, _ll_cni - _ll_y0, back_depth - _ll_z1]);
                translate([wall_t, _ll_csi, _ll_z1])
                    cube([_ll_dx, _ll_y1 - _ll_csi, back_depth - _ll_z1]);
            }

            // Nut tower receivers — full-height block with 1mm pad; pockets cut in outer difference()
            _nt_d   = nut_t + 2;
            _nt_w   = tower_w;
            _nr_pad = 1;
            for (sy = side_screw_y) {
                translate([wall_t, sy - _nt_w/2 - _nr_pad, wall_t])
                    cube([_nt_d + _nr_pad, _nt_w + 2*_nr_pad, back_depth - wall_t]);
                translate([case_w - wall_t - _nt_d - _nr_pad, sy - _nt_w/2 - _nr_pad, wall_t])
                    cube([_nt_d + _nr_pad, _nt_w + 2*_nr_pad, back_depth - wall_t]);
            }
        }

        // Mating-face rabbet: ring cut into inner wall faces only (matches tongue ring in front.scad)
        translate([wall_t - rabbet_w, wall_t - rabbet_w, back_depth - rabbet_d])
            difference() {
                cube([case_w - 2*(wall_t - rabbet_w), case_h - 2*(wall_t - rabbet_w), rabbet_d + 0.1]);
                translate([rabbet_w, rabbet_w, -0.1])
                    cube([case_w - 2*wall_t, case_h - 2*wall_t, rabbet_d + 0.3]);
            }

        // Tower pockets — in outer difference
        _nt_d   = nut_t + 2;
        _nt_w   = tower_w;
        for (sy = side_screw_y) {
            translate([wall_t - 0.1, sy - _nt_w/2 - tol/2, back_depth - tower_h])
                cube([_nt_d + tol + 0.1, _nt_w + tol, tower_h + 0.1]);
            translate([case_w - wall_t - _nt_d - tol/2, sy - _nt_w/2 - tol/2, back_depth - tower_h])
                cube([_nt_d + tol + 0.1, _nt_w + tol, tower_h + 0.1]);
        }

        // Side-wall screw holes: countersunk head flush with exterior + screw_depth clearance
        _scr_z = (back_depth + front_depth) / 2;
        for (sy = side_screw_y) {
            translate([-0.1, sy, _scr_z]) rotate([0, 90, 0])
                union() {
                    cylinder(d=screw_head_d, h=screw_head_h + 0.1, $fn=20);
                    cylinder(d=screw_boss_id, h=screw_depth + 0.1, $fn=16);
                }
            translate([case_w + 0.1, sy, _scr_z]) rotate([0, -90, 0])
                union() {
                    cylinder(d=screw_head_d, h=screw_head_h + 0.1, $fn=20);
                    cylinder(d=screw_boss_id, h=screw_depth + 0.1, $fn=16);
                }
        }

        // Magnet recesses — open on inner face, glue magnets in to hold components
        // PiSugar: X=20, Y=15 from board origin (per image measurement)
        translate([_elec_x + 20, _elec_y + 15, wall_t - magnet_recess_depth])
            cylinder(d=magnet_d, h=magnet_recess_depth + 0.1, $fn=64);
        // Battery: centred on short axis (bat_w/2), centre 18mm from top edge (10mm edge-to-edge)
        translate([_bat_x + bat_w / 2, _bat_y + bat_l - 18, wall_t - magnet_recess_depth])
            cylinder(d=magnet_d, h=magnet_recess_depth + 0.1, $fn=64);

        // All connector/button/LED cutouts (SD slot, HDMI, µUSB, PiSugar buttons/USB-C,
        // reset button, power LED) driven by the pi stack protrusion geometry
        translate([_elec_x, _elec_y, wall_t])
            pi_stack_protrusion_ref();
    }
}

back();
