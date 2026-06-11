// spellchecker:ignore centreline counterbore datasheet elec usbc waveshare
// --- Display ---
// Waveshare 7.5inch e-Paper V2 (800×480). Datasheet:
// https://www.waveshare.com/w/upload/6/60/7.5inch_e-Paper_V2_Specification.pdf
display_w        = 111.2;  // display panel width  (mm) — portrait
display_h        = 170.2;  // display panel height (mm) — portrait
disp_thickness   =   1.25; // display panel thickness (mm) — datasheet 1.18; 1.25 gives 0.07mm extra shelf clearance
screen_area_w    =  97.92; // active screen width  (mm)
screen_area_h    = 163.2;  // active screen height (mm)
display_border_wide  =  9.78; // wide border (long edge, right side; = display_w − display_border_narrow − screen_area_w)
display_border_narrow=  3.5;  // narrow border (long edge, left/top/bottom = 1.2+1.5+0.8mm from datasheet)
display_border_short =  3.5;  // short-edge border (top and bottom)
disp_shift           =  0.6;  // additional downward Y offset on display; creates 1mm stopper lip on upper L-blocks

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
btn_hinge_w     = 2;    // hinge strip width (mm) — right short edge, in-layer bending; flexing beam between fixed wall (_hinge_x1) and tab
btn_slot_kerf   = 1.0;  // slot kerf width (mm) — bottom horizontal slot (Z-direction gap), 0.7 will fuse to material below
btn_slot_kerf_top = 0.75; // slot kerf width (mm) — top horizontal slot (Z-direction gap)
btn_slot_kerf_x = 0.5;  // side slot kerf width (mm) — vertical free-side slot (X-direction gap); wider to prevent fusion

// --- Button area (front face, lower section below display) ---
btn_area_h     =  35;    // height of button zone at bottom of front face (mm)
btn_rows       =   2;
btn_cols       =   4;
btn_hole_tolerance = 0.2;
btn_hole_diameter = 10; // button hole diameter (mm) — physical cap sized to fit with tol clearance
btn_fillet_r   =   2;    // fillet radius on button hole outer edge (mm)
btn_zone_w     = case_w / btn_cols;   // each button is centred in its zone
btn_row_y1     = btn_area_h / 2 - 10;  // bottom row y centre
btn_row_y2     = btn_area_h / 2 + 4;  // top row y centre (closer to display)

// --- Carrier switch layout (shared with carrier.scad) ---
_sw            =  6;    // switch body footprint (mm)
_margin_y      =  1;    // Y margin beyond outermost switch edges (mm)
_loc_y1        = _sw / 2 + _margin_y;                   // 4mm  — bottom row centre in carrier coords
_loc_y2        = _loc_y1 + (btn_row_y2 - btn_row_y1);  // 18mm — top row centre in carrier coords

// --- Magnet recesses (back plate inner face) ---
magnet_d            = 15;   // diameter (mm) — derived from PiSugar image; tune after measuring
magnet_recess_depth = 1.5;  // depth into back plate; leaves 0.5mm wall

// --- Mating-face rabbet/tongue joint ---
rabbet_w       = 1;      // rabbet width into inner wall face (mm)
rabbet_d       = 1.5;    // rabbet depth from mating face (mm) — 2mm coincided with HDMI outer top

// --- M2 fasteners ---
screw_boss_id  = 2.1;    // screw shank clearance diameter (mm)
screw_head_d   = 4.0;    // screw head diameter (mm) — M2 button head, +clearance for circular-hole droop
screw_head_h   = wall_t; // screw head height (mm) — counterbore cuts through full wall thickness
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
_elec_x  = wall_t + 0.3;              // Pi Zero left edge (0.3mm right of inner wall; SD card tip flush with exterior)
_elec_y  = wall_t;                   // Pi Zero bottom edge (USB-C face)
_bat_x   = _elec_x + elec_w - bat_w; // battery right edge aligned with Pi Zero right edge
_bat_y   = wall_t + elec_l;          // battery bottom edge above Pi Zero
// Display: active area centred; wide border on right long edge
_screen_x = (case_w - screen_area_w) / 2;   // active screen X centre in case
_disp_x   = _screen_x - display_border_narrow; // panel left edge (narrow border on left)
_disp_y   = btn_area_h + (case_h - btn_area_h - display_h) / 2;  // panel vertically centred above buttons
// HAT holder pegs: centred between left and middle display column pads;
// HAT (66mm long edge along X, rotated 90°) holes 57.5mm apart, 4.25mm in from each end
_hat_peg_x = (_disp_x + 10 + 15/2 + _disp_x + (display_w - 15)/2 + 15/2) / 2;
_hat_peg_y = _disp_y - disp_shift + (display_h - 15) / 2 + 15 + 27;
// (boss_inset removed — corner bosses replaced by side-entry screw towers)
