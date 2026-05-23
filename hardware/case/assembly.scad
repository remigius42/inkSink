// Assembly — front + back positioned for visual inspection
include <params.scad>
use <front.scad>
use <back.scad>

front();

translate([0, 0, case_d / 2])
    back();
