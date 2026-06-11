// Assembly preview — back at z=0, front at z=back_depth
// spellchecker:ignore insertable

include <params.scad>
use <back.scad>
use <front.scad>
use <parts.scad>
use <carrier.scad>
use <pi-stack-divider.scad>
use <pi-stack-lock.scad>
use <hinge-print-supports.scad>

back();
color("yellow", 0.8)
    hinge_print_supports();
translate([0, 0, back_depth])
    color([0.8, 0.8, 0.8, 0.65])
    front();

// Reference parts — seated inside back shell
translate([_elec_x, _elec_y, wall_t]) {
    pi_stack_ref();
    pi_stack_protrusion_ref();  // red/blue overlays show required wall cutouts
}

// Pi-stack divider: insertable, seats at wall_t, south face at _bat_y
translate([0, _bat_y, wall_t])
    color("lime", 0.7)
        pi_stack_divider();

// Pi-stack lateral lock: insertable, wedges between Pi stack right edge and
// carrier support column 1
color("orange", 0.7)
    pi_stack_lock();

// Battery: portrait (28×59), right edge aligned with Pi Zero right edge
translate([_bat_x, _bat_y, wall_t])
    battery_ref();

// Waveshare HAT: rotated 90° (66×30, long edge along X), centred on the two
// HAT holder pegs (back.scad "HAT holder pegs", _hat_peg_x ± 28.75, _hat_peg_y)
translate([_hat_peg_x + 33, _hat_peg_y - 15, wall_t])
    rotate([0, 0, 90])
        waveshare_hat_ref();

// Display: panel left edge offset so active area is centred in case width
translate([_disp_x, _disp_y, back_depth - disp_thickness])
    display_ref();

// Carrier + switches: placed at inner-wall X origin (wall_t), correct Z height
// Z=14: stem tip at Z=21 (1mm into front bezel) - stem(3) - base(3) - floor(1)
// Y=4.5: btn_row_y1(10.5) - sw/2(3) - margin(1)
_car_ox = wall_t ;
_car_oy = btn_row_y1 - 3 - 1;                 // 6.5: carrier south Y (row_y1 - sw/2 - margin)
_car_oz = 14;                                  // back_depth+1 - stem(3) - base(3) - floor(1)
translate([_car_ox, _car_oy, _car_oz]) {
    color("peru", 0.85)
        carrier();
    // Switches seated in pockets (Z=1 = floor thickness)
    for (col = [0 : btn_cols - 1])
        for (row = [0 : btn_rows - 1]) {
            _sxc = (col + 0.5) * btn_zone_w - wall_t;
            _syc = row == 0 ? _loc_y1 : _loc_y2;
            translate([_sxc - 3, _syc - 3, 1])
                tactile_switch_ref();
        }
}
