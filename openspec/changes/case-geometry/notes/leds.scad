// LED indicator windows — print in transparent filament on a multi-material printer.
// Import alongside back.scad in your slicer and assign transparent filament to this body.
// Single-filament users: skip this file; the back shell has through-holes instead.
include <params.scad>
use <parts.scad>

// Windows: thin (0.4mm = 2 layers @ 0.2mm) transparent plugs flush with the
// back plate's exterior face (Z=0), leaving the rest of the through-hole
// (Z=0.4..wall_t) open. Thin keeps the LEDs distinct/countable and maximizes
// brightness for the dim power LED, rather than diffusing them.
translate([_elec_x, _elec_y, 0])
    led_indicator_shapes(0.4);
