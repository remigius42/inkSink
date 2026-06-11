// Button carrier — holds 8 × 6×6mm tactile switches in 4×2 grid
include <params.scad>

_sw_b     = 3;   // switch base height (mm)
_floor    = 1;   // material below switch base (mm)
_pin_d    = 1;   // pin hole diameter (mm)

_car_w = case_w - 2 * wall_t - 0.5 * tol;
_car_l = (btn_row_y2 - btn_row_y1) + _sw + 2 * _margin_y;  // 22mm
_car_t = _sw_b + _floor;                                     // 4mm

_rail_w = 6;   // rail width in X (mm)
_rail_h = 2;   // rail height above carrier top (mm) — closes gap to front plate inner face

module carrier() {
    union() {
    difference() {
        cube([_car_w, _car_l, _car_t]);

        for (col = [0 : btn_cols - 1])
            for (row = [0 : btn_rows - 1]) {
                _xc = (col + 0.5) * btn_zone_w - wall_t;
                _yc = row == 0 ? _loc_y1 : _loc_y2;

                // Switch pocket: 6×6mm, 3mm deep, leaving _floor at bottom
                translate([_xc - _sw/2, _yc - _sw/2, _floor])
                    cube([_sw, _sw, _sw_b + 0.1]);

                // Pin holes: 1mm Ø through full thickness, centres at 4 corners of switch body
                for (dx = [-_sw/2, _sw/2])
                    for (dy = [-_sw/2 + _pin_d/2, _sw/2 - _pin_d/2])
                        translate([_xc + dx, _yc + dy, -0.1])
                            cylinder(d=_pin_d, h=_car_t + 0.2, $fn=12);
            }

        // Bottom-face grooves for outward-bent spare legs — full X width, 2mm deep
        // turns the pin holes into slits for easier push through, holes are still needed because legs extend X width of switch.
        // Legs bend in X (outward from switch centre); groove keeps them flush with carrier bottom
        _wg_w = 1.25;
        _groove_d = 2;

        for (yc = [_loc_y1, _loc_y2])
            for (dy = [-_sw/2 + _pin_d/2, _sw/2 - _pin_d/2])
                translate([-0.1, yc + dy - _wg_w/2, -0.1])
                    cube([_car_w + 0.2, _wg_w, _groove_d + 0.1]);


        // Bottom-face wire channels — run full Y length, 5mm wide, 1mm deep
        // 1 fused channel per side: spans former ±8 and ±11 offsets (centre ±9.5, width 5mm)
        _ch_w      = 5;    // fused channel width (mm)
        _ch_offset = 9.5;  // channel centre offset from column X centre (mm)
        for (col = [0 : btn_cols - 1]) {
            _xc = (col + 0.5) * btn_zone_w - wall_t;
            for (side = [-1, 1])
                translate([_xc + side * _ch_offset - _ch_w/2, -0.1, -0.1])
                    cube([_ch_w, _car_l + 0.2, _groove_d + 0.1]);
        }
    }

    // Front-plate contact rails: left end, 3× between columns, right end
    for (rx = concat(
            [0],
            [for (n = [1 : btn_cols - 1]) n * btn_zone_w - wall_t - _rail_w / 2],
            [_car_w - _rail_w]
        ))
        translate([rx, 0, _car_t])
            cube([_rail_w, _car_l, _rail_h]);
    } // union
}

carrier();
