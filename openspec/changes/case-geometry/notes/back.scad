// Back shell — open tray with internal compartment walls and snap tabs
// Draft; replace hardware/case/back.scad once reviewed.
// spellchecker:ignore deboss debossed elec halign insertable

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

// Carrier south edge (+ tol/4 clearance), shared by the lock guide wedge and
// the carrier support columns
_cni = btn_row_y1 - 4 - 0.5 * tol;

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

            // Pi stack support pad: raises the stack's near corner (left+bottom inner walls) by 1mm to prevent tilting
            translate([wall_t, wall_t, wall_t])
                cube([5, 5, 1]);

            // Pi stack X-stop: ridge along inner west wall, width = _elec_x - wall_t
            // (0.3mm), pushes the Pi stack's left edge to _elec_x so the SD card tip
            // sits flush with the case exterior. Height stops below the SD card slot
            // (local Z=7.5) to avoid the slot cutout.
            translate([wall_t, _elec_y, wall_t])
                cube([_elec_x - wall_t, elec_l, 7.5]);

            // Internal wall: battery right-side retaining wall (battery right edge = _bat_x + bat_w)
            // Only above carrier zone (_cny=33.5mm) — lower section removed for battery wire clearance
            translate([_bat_x + bat_w, _bat_y + bat_l / 2, wall_t])
                cube([wall_t, bat_l / 2, _bat_wall_h]);

            // South guide wedge: X matches north wedge (gap zone only, no overlap with slot cut)
            hull() {
                translate([_disp_x + _pad/2, _bat_y - 1.5, wall_t])
                    cube([_bat_x - wall_t - (_disp_x + _pad/2), 1.5, 0.01]);
                translate([_disp_x + _pad/2, _bat_y - 0.01, wall_t + 2])
                    cube([_bat_x - wall_t - (_disp_x + _pad/2), 0.01, 0.01]);
            }

            // North guide wedge (mirrored): flat face at Y=_bat_y+2.0 (pointing south), between pillar and battery wall
            hull() {
                translate([_disp_x + _pad/2, _bat_y + 2.0, wall_t])
                    cube([_bat_x - wall_t - (_disp_x + _pad/2), 1.5, 0.01]);
                translate([_disp_x + _pad/2, _bat_y + 2.0 - 0.01, wall_t + 2])
                    cube([_bat_x - wall_t - (_disp_x + _pad/2), 0.01, 0.01]);
            }

            // Pi-stack lock guide wedge: flat face at Y=_cni (pointing south),
            // retains the insertable pi-stack-lock shim (Y=wall_t.._cni)
            {
                _lock_x0 = _elec_x + elec_w;
                _lock_w  = 12 - 0.5 * tol;
                hull() {
                    translate([_lock_x0, _cni, wall_t])
                        cube([_lock_w, 2.5, 0.01]);
                    translate([_lock_x0, _cni - 0.01, wall_t + 3])
                        cube([_lock_w, 0.01, 0.01]);
                }
            }

            // Internal wall: left side of battery (stops battery sliding toward centre)
            translate([_bat_x - wall_t, _bat_y + 2.0, wall_t])
                cube([wall_t, bat_l - 2.0, _bat_wall_h]);


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
            // Top: flush with top inner wall; 1mm lip above display top stops upward sliding
            difference() {
                translate([_disp_x - _pad/2, case_h - wall_t - _pad, wall_t])
                    cube([_pad, _pad, _pad_h]);
                translate([_disp_x, case_h - wall_t - _pad - 0.1, back_depth - disp_thickness])
                    cube([_pad/2 + 0.2, _pad - 0.8, disp_thickness + 0.1]);
            }
            // Bottom: extended left to inner wall (left face at wall_t; was _disp_x-_pad/2 = 7.54mm, shift = 5.54mm)
            difference() {
                translate([wall_t, _bat_y, wall_t])
                    cube([_disp_x + _pad/2 - wall_t, _pad, _pad_h]);
                translate([_disp_x - 0.1, _disp_y - disp_shift, back_depth - disp_thickness])
                    cube([_pad/2 + 0.2, _pad - 5 + 0.7, disp_thickness + 0.1]);
            }

            // Right-edge blocks: right face flush with case inner wall (case_w - wall_t).
            // Cutaway covers display underside only (block left face → display right edge),
            // leaving the 5.5mm strip right of the display edge as lateral stop.
            // Top: flush with top inner wall; 1mm lip above display top stops upward sliding
            difference() {
                translate([case_w - wall_t - _pad, case_h - wall_t - _pad, wall_t])
                    cube([_pad, _pad, _pad_h]);
                translate([case_w - wall_t - _pad - 0.1, case_h - wall_t - _pad - 0.1, back_depth - disp_thickness])
                    cube([_disp_x + display_w - (case_w - wall_t - _pad) + 0.2, _pad - 0.8, disp_thickness + 0.1]);
            }
            // Bottom
            difference() {
                translate([case_w - wall_t - _pad, _disp_y - 5, wall_t])
                    cube([_pad, _pad, _pad_h]);
                translate([case_w - wall_t - _pad - 0.1, _disp_y - disp_shift, back_depth - disp_thickness])
                    cube([_disp_x + display_w - (case_w - wall_t - _pad) + 0.2, _pad - 5 + 0.7, disp_thickness + 0.1]);
            }

            // Centre column pads: fully recessed (top flush with display back face, no rim)
            _col_y = _disp_y - disp_shift + (display_h - _pad) / 2;
            // Left and centre: single pad at mid-display Y
            for (px = [_disp_x + 10,
                       _disp_x + (display_w - _pad) / 2])
                translate([px, _col_y, wall_t])
                    cube([_pad, _pad, back_depth - wall_t - disp_thickness]);
            // Connector adapter pegs: 4 × ⌀2.3mm cylinders locking the FPC adapter under the display right edge
            {
                _cx  = _disp_x + display_w - 10;
                _cy  = _disp_y - disp_shift + display_h / 2;
                _ch  = back_depth - wall_t - disp_thickness;
                _cr  = 1.15;  // cylinder radius
                // Base block ties all four pegs together at the bottom
                translate([_cx - 10 - _cr, _cy - 12 - _cr, wall_t])
                    cube([10 + 2*_cr, 24 + 2*_cr, 5]);
                for (xo = [0, -10])
                    for (yo = [12, -12])
                        translate([_cx + xo, _cy + yo, wall_t])
                            cylinder(d=2.3, h=_ch, $fn=16);
            }

            // Right column: display connector obstructs mid-Y; two pads at 1/4 and 3/4 of inter-block span
            {
                _rx    = _disp_x + display_w - 10 - _pad;
                _y_bot = _disp_y + 10;               // top face of bottom L-blocks
                _y_top = case_h - wall_t - _pad;     // bottom face of top L-blocks
                for (qy = [_y_bot + (_y_top - _y_bot) / 4     - _pad / 2,
                            _y_bot + (_y_top - _y_bot) * 3 / 4 - _pad / 2])
                    translate([_rx, qy, wall_t])
                        cube([_pad, _pad, back_depth - wall_t - disp_thickness]);
            }

            // HAT holder pegs: 2× ⌀2.8mm + ⌀5mm base, centred between left and middle display column pads
            {
                _hh = back_depth - wall_t - disp_thickness;
                for (xo = [-28.75, 28.75])
                    translate([_hat_peg_x + xo, _hat_peg_y, wall_t]) {
                        cylinder(d=5, h=3, $fn=20);
                        cylinder(d=2.8, h=_hh, $fn=16);
                    }
            }

            // Power button marker: 2.5mm dome, 0.4mm proud of south wall exterior
            // Centred on the power-button flex tab (xc=10.5); only on power button, not custom button
            translate([_elec_x + 10.5, 0, wall_t - btn_slot_kerf/2 + 2])
                rotate([90, 0, 0])
                    cylinder(d=2.5, h=0.4, $fn=32);

            // Carrier support columns — U-channel profile at three X positions
            // Carrier Y zone: _cni..._csi (6.5–28.5mm). South/north retain walls above Z=14
            // lock carrier in Y; carrier footprint clears retain walls during Z insertion.
            {
                _csi = btn_row_y2 + 4 + 0.5 * tol;          // 28.55mm carrier north edge (+ tol/4 clearance)
                _csy = wall_t;                             //  2mm  outer south (into south wall)
                _cny = side_screw_y[0] - tower_w/2 - 1;  // 33.5mm outer north (fuses with nut tower)
                _clz = back_depth - 6;                    // 14mm  carrier floor
                // Two freestanding columns: 10mm right of Pi stack, then midpoint to right inner wall
                // (column at Pi-stack right edge removed: carrier wire clearance; battery wall covers above _cny)
                // Shifted +2mm/-2mm from those nominal positions to clear the carrier's
                // bottom-face wire-channel grooves (else the column loses support contact
                // under the channel, and a button press could pinch the wire there).
                _col1 = _elec_x + elec_w + 10 + 2;
                _col2 = (_elec_x + elec_w + 10 + case_w - wall_t) / 2 - 2;
                // Right-wall ledge: width trimmed from 3mm to 2.875mm (right edge flush
                // with inner wall) to clear the 0.125mm overlap with the rightmost
                // carrier wire-channel groove
                for (col = [[_col1, wall_t],
                             [_col2, wall_t],
                             [case_w - wall_t - 2.875, 2.875]]) {
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
                _ll_cni = btn_row_y1 - 4 - 0.25 * tol;        // 6.45mm carrier south edge (matches column _cni)
                _ll_csi = btn_row_y2 + 4 + 0.25 * tol;        // 28.55mm carrier north edge (matches column _csi)
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

        // Identification labels: 0.4mm debossed text into the floor (2 layers
        // at 0.2mm), read from inside the open shell (+Z looking down)
        translate([_elec_x + 50, _elec_y + 15, wall_t - 0.4])
            linear_extrude(0.4 + 0.1)
                text("Pi Stack", size = 7, halign = "center", valign = "center");
        translate([_bat_x + bat_w / 2, _bat_y + bat_l / 2, wall_t - 0.4])
            linear_extrude(0.4 + 0.1)
                text("Batt", size = 7, halign = "center", valign = "center");
        // HAT: centred in X on the HAT holder pegs; in Y, between the pegs
        // and the upper edge of the display support column pads
        _hat_label_pad_top = _disp_y - disp_shift + (display_h - 15) / 2 + 15;
        translate([_hat_peg_x, (_hat_peg_y + _hat_label_pad_top) / 2, wall_t - 0.4])
            linear_extrude(0.4 + 0.1)
                text("HAT", size = 7, halign = "center", valign = "center");

        // Pi-stack divider alignment mark: deboss "1" into the channel wall the
        // divider's large face seats against (text X = world X, text Y = world Z)
        translate([(_disp_x + 7.5 + wall_t) / 2, _bat_y + 2.4, (wall_t + back_depth) / 2 - 2])
            rotate([90, 0, 0])
                linear_extrude(0.4 + 0.1)
                    text("1", size = 9, halign = "center", valign = "center");

        // Pi-stack lock alignment mark: deboss "2" into the south inner wall
        // where the lock's south face seats (text X = world X, text Y = world Z)
        translate([_elec_x + elec_w + 6 - 0.25 * tol, wall_t + 0.1, (wall_t + back_depth) / 2])
            rotate([90, 0, 0])
                mirror([1, 0, 0])
                    linear_extrude(0.4 + 0.1)
                        text("2", size = 9, halign = "center", valign = "center");

        // Insertable divider slot: cuts through pillar + any overlapping geometry.
        // Open from mating face (Z=back_depth) to floor (Z=wall_t); starts right at inner wall face.
        translate([wall_t, _bat_y - 0.1, wall_t])
            cube([_disp_x + 7.5 - wall_t + 0.1, 2.1, back_depth - wall_t + 0.1]);

        // Divider pull notch: 1mm Y relief, 5mm from mating face
        translate([wall_t+5, _bat_y + 2.0 - 0.1, back_depth - 5])
            cube([_disp_x + 7.5 - wall_t - 1, 1 + 0.1, 5 + 0.1]);
    }
}

back();
