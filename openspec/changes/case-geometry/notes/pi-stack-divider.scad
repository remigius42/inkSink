// Insertable Pi-stack upper divider — two sections:
//   Section 1 (wall to pillar end): pillar height, front plate locks it in Z.
//   Section 2 (pillar end to battery wall): 10mm tall, leaves space for cables.

// spellchecker:ignore deboss halign insertable

include <params.scad>

// _pad/2 = 7.5 (matches back.scad local _pad = 15)
_s1_w = _disp_x + 7.5 - wall_t;                     // section 1 X width
_s2_w = _bat_x - (_disp_x + 7.5) - tol;              // section 2 X width (includes battery wall thickness)
_div_y = 2.1 - tol;                                  // tol/2 clearance per Y face (slot = 2.1mm)

module pi_stack_divider() {
    difference() {
        translate([wall_t, tol/2, 0]) {
            cube([_s1_w, _div_y, back_depth - wall_t]);   // section 1: full pillar height
            translate([_s1_w, 0, 0])
                cube([_s2_w, _div_y, 10]);                // section 2: cable clearance
        }
        // Alignment mark: deboss "1" into the opposite large face (same X/Z as
        // back.scad's mark, so the two "1"s line up through the part's
        // thickness when inserted) (text X = world X, text Y = world Z)
        translate([wall_t + _s1_w / 2, tol/2 + 0.4, (back_depth - wall_t) / 2])
            rotate([90, 0, 0])
                linear_extrude(0.4 + 0.1)
                    text("1", size = 9, halign = "center", valign = "center");
    }
}

pi_stack_divider();
