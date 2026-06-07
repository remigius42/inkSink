// Stepped rectangular connector cutout — outer pocket sized for plug housing,
// inner hole sized for connector body. Opens toward -Y; centre call on the
// connector's X/Z position at the wall inner face (Y=0).
//
// inner_w, inner_h   : connector body (X, Z)
// housing_w, housing_h : plug housing clearance (X, Z)
// protrusion         : how far connector extends beyond wall inner face
// cutout_reach       : overshoot beyond wall outer face for clean boolean
// wall_t             : wall thickness
// lip                : material between pocket floor and inner hole (default 0.5mm)
module connector_stepped_cutout(inner_w, inner_h, housing_w, housing_h,
                                  protrusion, cutout_reach, wall_t, lip=0.5, outer=true) {
    // Inner hole: tight fit, full depth (wall + protrusion)
    translate([-inner_w/2,   -cutout_reach, -inner_h/2])
        cube([inner_w,   cutout_reach + protrusion, inner_h]);
    // Outer pocket: housing clearance, depth = wall_t - lip
    if (outer)
        translate([-housing_w/2, -cutout_reach, -housing_h/2])
            cube([housing_w, cutout_reach - lip, housing_h]);
}

// Subtraction module: through-hole with chamfer+fillet groove at the outer face.
// Same chamfer→fillet math as chamfer_fillet_extrude, applied in the r-z plane.
//
// r0    : hole radius (mm)
// fr    : fillet radius (mm)
// h     : total hole depth incl. overshoot (mm)
// zt    : z of outer face in local coords (typically h - 0.1)
// alpha : min printable overhang angle from horizontal (deg)
// fn    : arc segments
module hole_chamfer_fillet_cutout(r0, fr, h, zt, alpha=55, fn=20) {
    if ($preview) {
        cylinder(r=r0, h=h, $fn=16);
    } else {
        _r_top = r0 + fr * (sin(alpha) + cos(alpha) - 1) / sin(alpha);
        _r_c   = r0 + fr * (1 - sin(alpha));
        _z_c   = zt - fr * (1 - cos(alpha));

        cylinder(r=r0, h=h, $fn=48);
        rotate_extrude($fn=48)
            polygon(concat(
                [[r0 - 0.01, zt - fr],
                 [r0 - 0.01, zt + 0.01],
                 [_r_top,    zt + 0.01],
                 [_r_c,      _z_c]],
                [for (i = [1:fn])
                    [r0 + fr - fr * sin(alpha + (90 - alpha) * i / fn),
                     zt - fr  + fr * cos(alpha + (90 - alpha) * i / fn)]]
            ));
    }
}

// Extrude a 2D child with a chamfer-to-fillet edge at the top face.
//
// The outer face (z=length) starts inset, growing outward to full size at z=length-r.
// The steep inset zone (worst overhang when printed top-face-down) is replaced by a
// straight chamfer tangent to the fillet arc at the transition angle.
//
// length : extrusion height (mm)
// r      : fillet radius (mm)
// alpha  : min printable overhang angle from horizontal (deg) — 55 is safe on X1C
// fn     : slices per section
// invert : false = outline shrinks at top (solid outer edge)
//          true  = outline expands at top (use as subtraction for cutout inner edges)
module chamfer_fillet_extrude(length, r, alpha=55, fn=20, invert=false) {
    if ($preview) {
        linear_extrude(length) children();
    } else {
        _b  = 90 - alpha;
        _zc = r * (1 - sin(_b));
        _oc = r * (cos(_b) - 1);
        _s  = invert ? -1 : 1;

        linear_extrude(length - r + 0.01) children();

        for (i = [0:fn]) {
            _zl  = r - (r - _zc) * i / fn;
            _ofs = _s * (sqrt(r*r - (r-_zl)*(r-_zl)) - r);
            translate([0, 0, length - _zl])
                linear_extrude((r - _zc) / fn + 0.01)
                    offset(_ofs) children();
        }

        for (i = [0:fn]) {
            _zl  = _zc * (fn - i) / fn;
            _ofs = _s * (_oc + tan(_b) * (_zl - _zc));
            translate([0, 0, length - _zc + _zc * i / fn])
                linear_extrude(_zc / fn + 0.01)
                    offset(_ofs) children();
        }
    }
}
