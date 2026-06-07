// LED indicator windows — print in transparent filament on a multi-material printer.
// Import alongside back.scad in your slicer and assign transparent filament to this body.
// Single-filament users: skip this file; the back shell has through-holes instead.
include <params.scad>
use <parts.scad>

// Windows sit in the back plate (Z=0..wall_t), positioned at the pi stack origin.
translate([_elec_x, _elec_y, 0])
    led_indicator_shapes(wall_t);
