// Standalone anti-droop pillar supports for the PiSugar flex-tab hinges
// (south wall, bottom slot). Optional: place these as additional objects on
// the print bed inside the bottom-slot gap to support the tab overhang,
// instead of using slicer-generated supports.
// spellchecker:ignore droop

include <params.scad>

_pillar_w  = 0.5; // anti-droop pillar width (1 nozzle)
_btn_z0    = -btn_slot_kerf / 2;

// Outer/inner skin towers for one hinge (xc = button centre X)
module hinge_print_support_pair(xc) {
    _epx = xc + 3 - btn_slot_kerf_x/2 - _pillar_w + 0.25;
    for (yo = [-(wall_t - 0.5), -0.5])
        translate([_elec_x + _epx, _elec_y + yo, wall_t + _btn_z0 - btn_slot_kerf/2])
            cube([_pillar_w, 0.5, btn_slot_kerf]);
}

module hinge_print_supports() {
    for (xc = [10.5, 42.5])
        hinge_print_support_pair(xc);
}

hinge_print_supports();
