// --- Display ---
display_w        = 112.5;  // display panel width  (mm) — portrait
display_h        = 170;    // display panel height (mm) — portrait
disp_thickness   =   1.25; // display panel thickness (mm)
screen_area_w    = 100;    // active screen width  (mm)
screen_area_h    = 165;    // active screen height (mm)
display_border_wide  =  9.5;  // wide border (long edge, assumed right; TBD after driver rotation)
display_border_narrow=  2.5;  // narrow border (long edge)
display_border_short =  2;    // short-edge border (top and bottom)

// --- Cavities (back shell interior) ---
elec_w         =  65;    // Pi Zero width  (mm)
elec_l         =  30;    // Pi Zero length (mm)
elec_depth     =  16;    // Pi Zero + PiSugar stack depth (mm) — 15.7mm actual
hat_w          =  30;    // Waveshare HAT width  (mm) — rotated 90° in case
hat_l          =  66;    // Waveshare HAT length (mm)
hat_depth      =   9.5;  // Waveshare HAT depth  (mm)
bat_w          =  28;    // battery width  (mm) — portrait: 28×59 footprint
bat_l          =  59;    // battery length (mm)
bat_depth      =  12.5;  // battery depth  (mm) — 10.7 body + 1.8 magnet

// --- Primitives first (no dependencies) ---
case_w         = 135;    // width  (mm) — 135mm clears 4mm nut towers with 1.5mm margin right of display
case_h         = 210;    // height (mm) — 2+170+35+2=209 → 210
front_depth    =   2;    // front bezel thickness (mm)
back_depth     =  20;    // back shell depth (mm) — elec_depth 15.7 + 2 wall + 2.3 clearance; unconfirmed
fillet_r       =   2;    // outer-edge fillet radius (mm)
edge_overhang_angle = 55; // chamfer→fillet transition (deg from horizontal); 45=safe, 55=X1C tuned
tol            = 0.2;    // FDM clearance on each mating face (mm)
wall_t         = 2;      // nominal wall thickness (mm)

// --- PiSugar flex-tab buttons (south wall) ---
btn_hinge_w   = 0.8;  // hinge strip width (mm) — right short edge, in-layer bending
btn_slot_kerf = 0.5;  // slot kerf width (mm) — 1 nozzle diameter

// --- Button area (front face, lower section below display) ---
btn_area_h     =  35;    // height of button zone at bottom of front face (mm)
btn_rows       =   2;
btn_cols       =   4;
btn_hole_tolerance = 0.2;
btn_hole_diameter = 10; // button hole diameter (mm) — physical cap sized to fit with tol clearance
btn_fillet_r   =   2;    // fillet radius on button hole outer edge (mm)
btn_zone_w     = case_w / btn_cols;   // each button is centred in its zone
btn_row_y1     = btn_area_h / 2 - 7;  // bottom row y centre
btn_row_y2     = btn_area_h / 2 + 7;  // top row y centre (closer to display)

// --- Magnet recesses (back plate inner face) ---
magnet_d            = 15;   // diameter (mm) — derived from PiSugar image; tune after measuring
magnet_recess_depth = 1.5;  // depth into back plate; leaves 0.5mm wall

// --- Mating-face rabbet/tongue joint ---
rabbet_w       = 1;      // rabbet width into inner wall face (mm)
rabbet_d       = 1.5;    // rabbet depth from mating face (mm) — 2mm coincided with HDMI outer top

// --- M2 fasteners ---
screw_boss_id  = 2.4;    // screw shank clearance diameter (mm)
screw_head_d   = 3.8;    // screw head diameter (mm) — M2 button head
screw_head_h   = 1.4;    // screw head height (mm) — sinks fully in 2mm wall
screw_depth    = 25;     // total clearance hole depth from exterior (mm)
nut_af         = 4;      // hex nut across-flats (mm)
nut_t          = 1.6;    // hex nut thickness (mm)
tower_h        = 17;     // nut tower height from front plate inner face (mm) — 17mm leaves 1mm above back floor
tower_w        = 15;     // nut tower width in Y (mm)
// Y centres of the two screws per side; symmetric around case_h/2, clear of Pi stack (Y<32)
side_screw_y   = [case_h / 2 - case_h * 0.3, case_h / 2 + case_h * 0.3];

// --- USB-C notch ---
usbc_notch_w   =  12;    // notch width  (mm)
usbc_notch_h   =   4;    // notch height (mm)

// --- Derived positions (all dependencies above) ---
// Y=0 at bottom (USB-C / south face); X=0 at left inner wall
_elec_x  = wall_t;                   // Pi Zero left edge
_elec_y  = wall_t;                   // Pi Zero bottom edge (USB-C face)
_bat_x   = wall_t + elec_w - bat_w;  // battery right edge aligned with Pi Zero right edge
_bat_y   = wall_t + elec_l;          // battery bottom edge above Pi Zero
_hat_x   = wall_t + elec_w;          // HAT left edge = Pi Zero right edge
_hat_y   = wall_t;                   // HAT bottom edge flush with Pi Zero
// Display: active area centred; wide border on right long edge
_screen_x = (case_w - screen_area_w) / 2;   // active screen X centre in case
_disp_x   = _screen_x - display_border_narrow; // panel left edge (narrow border on left)
_disp_y   = btn_area_h + (case_h - btn_area_h - display_h) / 2;  // panel vertically centred above buttons
// (boss_inset removed — corner bosses replaced by side-entry screw towers)
