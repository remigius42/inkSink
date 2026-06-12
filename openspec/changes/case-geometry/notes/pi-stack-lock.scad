// Insertable Pi-stack lateral lock — wedges into the gap between the Pi
// stack's right PCB edge and carrier support column 1, locking the stack
// against X movement (case width). Inserted vertically from the mating face,
// like pi-stack-divider. Sheet is oversized for trimming to fit print
// tolerances.
include <params.scad>

// spellchecker:ignore deboss elec halign insertable

// X: gap is 12mm (column 1 starts 12mm right of the Pi stack's right edge,
// shifted +2mm off its nominal 10mm position to clear the carrier's wire-channel
// groove — see back.scad). Thickness leaves 0.5*tol clearance to column 1.
_lock_x0 = _elec_x + elec_w;
_lock_w  = 12 - 0.5 * tol;

// Y: from the inner south wall (wall_t) to the carrier-seating cutaway's
// south edge (_cni, back.scad), so the shim sits in the south-retain zone of
// column 1 without colliding with the carrier or the south-wall rabbet.
// _cni = btn_row_y1 - 4 - 0.5*tol (mirrors back.scad's carrier support block).
_lock_y0 = wall_t;
_lock_y1 = btn_row_y1 - 4 - 0.5 * tol;

// Z: full pillar height, as high as the back shell.
_lock_h = back_depth - wall_t;

module pi_stack_lock() {
    difference() {
        translate([_lock_x0, _lock_y0, wall_t])
            cube([_lock_w, _lock_y1 - _lock_y0, _lock_h]);
        // Alignment mark: deboss "2" into the north face (opposite the south
        // face that seats against the wall), same X/Z as back.scad's mark, so
        // the two "2"s line up through the part's thickness when inserted
        // (text X = world X, text Y = world Z)
        translate([_lock_x0 + _lock_w / 2, _lock_y1 + 0.1, (wall_t + back_depth) / 2])
            rotate([90, 0, 0])
                mirror([1, 0, 0])
                    linear_extrude(0.4 + 0.1)
                        text("2", size = 9, halign = "center", valign = "center");
    }
}

pi_stack_lock();
