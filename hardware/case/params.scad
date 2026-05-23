// Case dimensions from build guide
// Overall envelope
case_w = 170;   // width  (mm) — display width + margins
case_h = 115;   // height (mm) — display height + margins
case_d = 26;    // depth  (mm) — uniform front-to-back

// Display cutout (front face)
display_w = 163; // display opening width  (mm)
display_h = 98;  // display opening height (mm)

// Cavity depths (back half)
battery_depth    = 6;   // battery cavity depth  (mm)
electronics_depth = 22; // electronics cavity depth (mm)

// Derived: wall thickness — raw expression gives -1mm with current dimensions
// (26 - 6 - 22) / 2 = -1; clamped to min_wall. Increase case_d for real geometry.
min_wall = 1;
wall = max(min_wall, (case_d - battery_depth - electronics_depth) / 2);
