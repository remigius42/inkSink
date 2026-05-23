// Back piece — electronics + battery cavities, button holes on side edge
// TODO: implement cavity and button-hole geometry
include <params.scad>

module back() {
    // Stub: solid back slab
    cube([case_w, case_h, case_d / 2]);
}

back();
