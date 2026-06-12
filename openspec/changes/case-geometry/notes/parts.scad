// Reference geometry — bounding-box placeholders for fit checks only

// spellchecker:ignore darkgray dimgray elec steelblue

include <params.scad>
use <utils.scad>

module display_ref() {
    // Panel with active screen area cut through as a visual marker
    difference() {
        color("lightblue", 0.5)
            cube([display_w, display_h, disp_thickness]);
        // Active screen offset: narrow border left, short border bottom
        translate([display_border_narrow,
                   display_border_short,
                   disp_thickness - 0.5])
            cube([screen_area_w, screen_area_h, 0.51]);
    }
}

module battery_ref() {
    // Portrait orientation: bat_w (28mm) along X, bat_l (59mm) along Y
    color("yellow", 0.5)
        cube([bat_w, bat_l, bat_depth]);
}

module pi_stack_ref() {
    // Pi Zero 2W + PiSugar 3 stack — landscape, Y=0 at USB-C/south edge
    // Z=0: pogo-pin underside (back-plate face); Z=7.5: Pi Zero PCB top
    _pcb_t   = 1.4;
    _gpio_w  = 20 * 2.54;  // 50.8mm
    _gpio_x0 = (elec_w - _gpio_w) / 2;

    // PiSugar 3 PCB
    color("green", 0.35)
        cube([elec_w, elec_l, _pcb_t]);

    // Pi Zero 2W PCB (top at Z=7.5)
    color("green", 0.5)
        translate([0, 0, 7.5 - _pcb_t])
            cube([elec_w, elec_l, _pcb_t]);

    // GPIO header: 2×20, 2.54mm pitch, top long edge; height = remaining elec_depth
    color("gold", 0.9)
        translate([_gpio_x0, elec_l - 2, 7.5])
            cube([_gpio_w, 2, elec_depth - 7.5]);

    // South-face (Y=0) connectors — shown as shallow bumps at inner PCB face only;
    // protrusion_ref handles the outward extent for wall cutouts
    // mini HDMI (Pi Zero): X centre=12.65, 12.5×5mm (right edge +0.5mm)
    color("dimgray", 0.8)
        translate([12.4 - 6, -0.5, 7.5])
            cube([12.5, 2.5, 5]);
    // µUSB power (Pi Zero): X=41.4, 9×3.5mm (sides ±0.5mm, bottom +0.5mm)
    color("dimgray", 0.8)
        translate([41.4 - 4.5, -0.5, 7.25])
            cube([9, 2.5, 3.5]);
    // µUSB OTG (Pi Zero): X=54
    color("dimgray", 0.8)
        translate([54 - 4.5, -0.5, 7.25])
            cube([9, 2.5, 3.5]);
    // USB-C (PiSugar): X=53.25, 9.5×4.0mm, Z=0.5..4.5 (left +0.5mm, bottom +0.5mm)
    color("steelblue", 0.8)
        translate([53.5 - 5.0, -0.5, 0.5])
            cube([9.5, 2.5, 4.0]);
    // PiSugar edge buttons: X=10.5 (power) and X=42.5 (custom)
    color("steelblue", 0.6)
        for (xc = [10.5, 42.5])
            translate([xc - 3, -0.5, 0.5])
                cube([6, 2.5, 3]);

    // SD card (west/left face, X=0): protrudes 2.3mm beyond PCB; 12mm wide, 1.25mm tall
    color("silver", 0.8)
        translate([-2.3, elec_l - 7.0 - 12, 7.5])
            cube([4.3, 12, 1.25]);
}

// LED indicator window shapes — XY footprints of the power LED and indicator strip.
// Z runs from 0 to `depth`; caller sets translation and depth for cutout vs window use.
// Origin matches pi_stack_protrusion_ref coordinate system (X/Y from Pi stack corner).
module led_indicator_shapes(depth) {
    // Power LED: 1×2mm at X=1.5, Y=18.0
    translate([2 - 0.75, 19.0 - 1, 0]) cube([1.5, 2, depth]);
    // Indicator LEDs ×4: 8×2mm strip at X=14.5, Y=1.0
    translate([14.5, 3 - 2, 0]) cube([8, 2, depth]);
}

// Protrusion blocks for every connector/button that needs a wall cutout.
// Place at the same translation as pi_stack_ref; subtract from back shell to
// get all cutouts in one operation.
//
// cutout_reach: how far each block extends BEYOND the bounding-box face so
// that a difference() cuts cleanly through the wall (default: wall_t + 1).
module pi_stack_protrusion_ref(cutout_reach = wall_t + 1) {

    // --- LEFT FACE (X=0): SD card slot (friction-fit, stepped for finger access) ---
    color("red", 0.4) {
        _sd_y0 = elec_l - 7.0 - 12;  // 11.0mm from Y=0
        // Inner slot: snug fit for card (12mm wide, 1.25mm tall)
        translate([-cutout_reach, _sd_y0, 7.5])
            cube([cutout_reach + 2.3 + 2, 12, 1.25 + tol]);
        // Outer finger-access recess: 15mm wide, 5mm tall, wall_t - 1mm lip
        // (1mm lip in the 1.5mm side-wall zones keeps them printable; thinner
        // lips there were getting dropped during slicing)
        translate([-cutout_reach, _sd_y0 - 1.5, 7.5 - (5 - 1.25) / 2])
            cube([cutout_reach - 1.3, 15, 5]);
        // Top wall (above inner slot, slit width only): cut to the original
        // deeper depth (0.5mm lip) so it stays open as a fingernail gap above
        // the card's top edge, without weakening the side walls
        translate([-cutout_reach, _sd_y0, 7.5 + 1.25 + tol])
            cube([cutout_reach - 0.5, 12, 1.875 - tol]);
    }

    // --- BOTTOM FACE (Y=0): Pi Zero connectors on PCB top (Z=7.5) ---
    // Stepped cutout: inner = connector body, outer = plug housing clearance
    color("red", 0.4) {
        // mini HDMI: centre X=12.65, inner 12.5×5mm (+0.5mm right), housing 20×12mm, protrusion 8.5mm
        translate([12.65, 0, 7.5 + 2.5])
            connector_stepped_cutout(12.5, 5, 20, 12, 8.5, cutout_reach, wall_t);
        // µUSB power (X=41.4): inner 9×3.5mm (sides ±0.5mm, bottom +0.5mm); housing_w 11.9
        translate([41.4, 0, 7.5 + 1.25])
            connector_stepped_cutout(9, 3.5, 11.9, 6.5, 3, cutout_reach, wall_t);
        // µUSB OTG (X=54): inner 9×3.5mm; outer=false — shared with USB-C combined pocket below
        translate([54, 0, 7.5 + 1.25])
            connector_stepped_cutout(9, 3.5, 11, 6.5, 3, cutout_reach, wall_t, outer=false);
    }

    // --- BOTTOM FACE (Y=0): PiSugar connectors (approx Z=1..5) ---
    color("red", 0.4) {
        // Power button (X=10.5) and custom button (X=42.5): flex tab, hinge on left short edge.
        // Tab bottom aligned with HDMI outer bottom; height 4mm.
        // Three U-slot cuts free the tab; interior pocket thins hinge to 0.6mm in Y.
        _hdmi_z    = 7.5 + 2.5;               // HDMI centre Z
        _hdmi_oh   = 12;                       // HDMI outer housing height
        _btn_z0    = -btn_slot_kerf / 2;       // shift down so top slot's top edge = HDMI outer bottom
        _btn_tab_h = _hdmi_z - _hdmi_oh / 2;  // = 4; top of cut aligns with HDMI outer bottom
        // Hinge boundary fixed at the original 0.8mm hinge's centre + half-width
        // (xc-3+0.4+0.4); widening btn_hinge_w extends the flexing beam rightward
        // from this boundary, into the tab area already freed by the top/bottom slots.
        _hinge_c = -3 + 0.4;
        for (xc = [10.5, 42.5]) {
            _hinge_x1 = xc + _hinge_c + 0.4;
            // Right (free-side) slot: split to protect pillar Z range.
            // Right half (past pillar): full height.
            translate([xc + 3, -cutout_reach, _btn_z0 - btn_slot_kerf/2])
                cube([btn_slot_kerf_x/2, cutout_reach + 0.1, _btn_tab_h + btn_slot_kerf]);
            // Left half (over pillar X range): starts above pillar top, connects to top slot.
            translate([xc + 3 - btn_slot_kerf_x/2, -cutout_reach, _btn_z0 + btn_slot_kerf/2])
                cube([btn_slot_kerf_x/2, cutout_reach + 0.1, _btn_tab_h]);
            // Top slot: top edge fixed at _btn_tab_h (HDMI outer bottom), independent
            // of the bottom kerf (_btn_z0) — so changing either kerf doesn't shift it
            translate([_hinge_x1, -cutout_reach, _btn_tab_h - btn_slot_kerf_top])
                cube([xc + 3 - _hinge_x1, cutout_reach + 0.1, btn_slot_kerf_top]);
            // Bottom slot: complete cut, full width to the free-side slot boundary.
            // No built-in anti-droop pillar — see hinge-print-supports.scad for
            // standalone tower objects that sit in this gap as printable
            // supports, as an alternative to slicer-generated supports.
            translate([_hinge_x1, -cutout_reach, _btn_z0 - btn_slot_kerf/2])
                cube([xc + 3 - _hinge_x1, cutout_reach + 0.1, btn_slot_kerf]);
            // Hinge thinning: pocket on interior face reduces hinge wall to 0.6mm.
            // Starts at the fixed wall/tab boundary (_hinge_x1) and extends rightward
            // into the tab area (already freed top/bottom by the slots above), so the
            // thinned strip can flex along its full length as a beam.
            translate([_hinge_x1, -(wall_t - 0.6), _btn_z0])
                cube([btn_hinge_w, wall_t - 0.6 + 0.1, _btn_tab_h]);
            // Back relief: removes 0.25mm from the interior face of the tab (rest of width,
            // excluding hinge) so the tab doesn't press the PiSugar button at rest
            translate([_hinge_x1, -0.25, _btn_z0])
                cube([xc + 3 - _hinge_x1, 0.25 + 0.1, _btn_tab_h]);
        }
        // USB-C (X=53.25): inner 9.5×4.5mm (left +0.5mm, bottom +1.0mm), housing 12.5×6.5mm, protrusion ~3mm
        // outer=false: combined outer pocket below covers µUSB ×2 + USB-C together
        translate([53.25, 0, 2.25])
            connector_stepped_cutout(9.5, 4.5, 12.5, 6.5, 3, cutout_reach, wall_t, outer=false);
        // Combined outer pocket for right µUSB + USB-C: X span = USB-C outer width (contains right µUSB)
        translate([53.25 - 12.5/2, -cutout_reach, 2.5 - 6.5/2])
            cube([12.95, cutout_reach - 0.5, 7.5 + 1.25 + 6.5/2 - (2.5 - 6.5/2)]);
    }

    // --- BACK FACE (Z=0): PiSugar PCB — access holes through back plate ---
    // Y measured from south/USB-C edge (Y=0 in assembled coords).
    color("blue", 0.4) {
        // Reset button at X=20.5, Y=5: 1.5mm diameter access hole (always a through-hole)
        translate([20.5, 5, -cutout_reach]) cylinder(d=2.25, h=cutout_reach + tol, $fn=16);
        // LED windows — shared module; here used as through-hole cutouts
        translate([0, 0, -cutout_reach]) led_indicator_shapes(cutout_reach + tol);
    }
}

module waveshare_hat_ref() {
    // HAT rotated 90° — hat_w (30mm) along X, hat_l (66mm) along Y
    color("orange", 0.5)
        cube([hat_w, hat_l, hat_depth]);
}

module tactile_switch_ref() {
    // 6×6mm tactile switch — origin at base bottom-left corner
    // Base: 6×6×3mm; stem: 3.4mm Ø cylinder, 3mm tall
    color("darkgray", 0.9) {
        cube([6, 6, 3]);
        translate([3, 3, 3])
            cylinder(d=3.4, h=3, $fn=20);
    }
}
