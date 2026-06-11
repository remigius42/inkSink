// Button cap — press-fits over 3.5mm square tactile switch stem, sits in 10mm front-bezel hole
include <params.scad>

_btn_d    = btn_hole_diameter - btn_hole_tolerance;  // 9.8mm
_btn_h    = 2;    // cap height (mm)
_stem_d   = 3.35;  // tactile switch stem diameter for socket (mm) (3.5 too wide, 3.25 too tight)
_sock_d   = 1;    // socket depth (mm)
_kerf_l   = _btn_d / 2;  // kerf cut length (half button diameter)
_kerf_w   = 0.5;  // kerf cut width (mm)

difference() {
    cylinder(d=_btn_d, h=_btn_h, $fn=64);

    // stem socket — centred, from top
    translate([0, 0, _btn_h - _sock_d])
        cylinder(d=_stem_d, h=_sock_d + 0.1, $fn=32);

    // kerf cut — tolerance compensation, centred, from top
    translate([-_kerf_l / 2, -_kerf_w / 2, _btn_h - _sock_d])
        cube([_kerf_l, _kerf_w, _sock_d + 0.1]);
}
