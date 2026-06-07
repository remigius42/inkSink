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
    // mini HDMI (Pi Zero): X centre=12.4, 12×5mm
    color("dimgray", 0.8)
        translate([12.4 - 6, -0.5, 7.5])
            cube([12, 2.5, 5]);
    // µUSB power (Pi Zero): X=41.4, ~8×3mm
    color("dimgray", 0.8)
        translate([41.4 - 4, -0.5, 7.5])
            cube([8, 2.5, 3]);
    // µUSB OTG (Pi Zero): X=54
    color("dimgray", 0.8)
        translate([54 - 4, -0.5, 7.5])
            cube([8, 2.5, 3]);
    // USB-C (PiSugar): X=53.5, 9×3.5mm, Z=1..4.5
    color("steelblue", 0.8)
        translate([53.5 - 4.5, -0.5, 1])
            cube([9, 2.5, 3.5]);
    // PiSugar edge buttons: X=11.5 (power) and X=43.5 (custom)
    color("steelblue", 0.6)
        for (xc = [11.5, 43.5])
            translate([xc - 3, -0.5, 0.5])
                cube([6, 2.5, 3]);

    // SD card (west/left face, X=0): protrudes 2.3mm beyond PCB; 12mm wide, 1.25mm tall
    color("silver", 0.8)
        translate([-2.3, elec_l - 5.5 - 12, 7.5])
            cube([4.3, 12, 1.25]);
}

// LED indicator window shapes — XY footprints of the power LED and indicator strip.
// Z runs from 0 to `depth`; caller sets translation and depth for cutout vs window use.
// Origin matches pi_stack_protrusion_ref coordinate system (X/Y from Pi stack corner).
module led_indicator_shapes(depth) {
    // Power LED: 1×2mm at X=1.5, Y=17.5
    translate([2 - 0.5, 18.5 - 1, 0]) cube([1, 2, depth]);
    // Indicator LEDs ×4: 7.5×2mm strip at X=15, Y=2
    translate([15, 3 - 1, 0]) cube([7.5, 2, depth]);
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
        _sd_y0 = elec_l - 5.5 - 12;  // 12.5mm from Y=0
        // Inner slot: snug fit for card (12mm wide, 1.25mm tall)
        translate([-cutout_reach, _sd_y0, 7.5])
            cube([cutout_reach + 2.3 + 2, 12, 1.25 + tol]);
        // Outer finger-access recess: 15mm wide, 5mm tall, wall_t - 0.5mm lip
        translate([-cutout_reach, _sd_y0 - 1.5, 7.5 - (5 - 1.25) / 2])
            cube([cutout_reach - 0.5, 15, 5]);
    }

    // --- BOTTOM FACE (Y=0): Pi Zero connectors on PCB top (Z=7.5) ---
    // Stepped cutout: inner = connector body, outer = plug housing clearance
    color("red", 0.4) {
        // mini HDMI: centre X=12.4, inner 12×5mm, housing 20×12mm, protrusion 8.5mm
        translate([12.4, 0, 7.5 + 2.5])
            connector_stepped_cutout(12, 5, 20, 12, 8.5, cutout_reach, wall_t);
        // µUSB power (X=41.4): housing_w 11→11.9; right edge 47.35 overlaps combined rect by 0.1mm (no coplanar face)
        translate([41.4, 0, 7.5 + 1.5])
            connector_stepped_cutout(8, 3, 11.9, 6.5, 3, cutout_reach, wall_t);
        // µUSB OTG (X=54): outer=false — shared with USB-C combined pocket below
        translate([54, 0, 7.5 + 1.5])
            connector_stepped_cutout(8, 3, 11, 6.5, 3, cutout_reach, wall_t, outer=false);
    }

    // --- BOTTOM FACE (Y=0): PiSugar connectors (approx Z=1..5) ---
    color("red", 0.4) {
        // Power button (X=11.5) and custom button (X=43.5): flex tab, hinge on left short edge.
        // Tab bottom aligned with HDMI outer bottom; height 4mm.
        // Three U-slot cuts free the tab; interior pocket thins hinge to 0.8mm in Y.
        _hdmi_z    = 7.5 + 2.5;               // HDMI centre Z
        _hdmi_oh   = 12;                       // HDMI outer housing height
        _btn_z0    = -btn_slot_kerf / 2;       // shift down so top slot's top edge = HDMI outer bottom
        _btn_tab_h = _hdmi_z - _hdmi_oh / 2;  // = 4; top of cut aligns with HDMI outer bottom
        _pillar_w  = 0.5;                      // anti-droop pillar width (1 nozzle)
        for (xc = [11.5, 43.5]) {
            // Right (free-side) slot: split to protect pillar Z range.
            // Right half (past pillar): full height.
            translate([xc + 3, -cutout_reach, _btn_z0 - btn_slot_kerf/2])
                cube([btn_slot_kerf/2, cutout_reach + 0.1, _btn_tab_h + btn_slot_kerf]);
            // Left half (over pillar X range): starts above pillar top, connects to top slot.
            translate([xc + 3 - btn_slot_kerf/2, -cutout_reach, _btn_z0 + btn_slot_kerf/2])
                cube([btn_slot_kerf/2, cutout_reach + 0.1, _btn_tab_h]);
            // Top slot
            translate([xc - 3 + btn_hinge_w, -cutout_reach, _btn_z0 + _btn_tab_h - btn_slot_kerf/2])
                cube([6 - btn_hinge_w, cutout_reach + 0.1, btn_slot_kerf]);
            // Bottom slot: continuous cut up to end pillar; end pillar Y-split to breakaway skins
            let (fx0 = xc - 3 + btn_hinge_w,
                 epx = xc + 3 - btn_slot_kerf/2 - _pillar_w + 0.25) {
                translate([fx0, -cutout_reach, _btn_z0 - btn_slot_kerf/2])
                    cube([epx - fx0, cutout_reach + 0.1, btn_slot_kerf]);
                // End pillar Y-split: outer 0.5mm + inner 0.5mm skins, 1mm gap
                translate([epx, -(wall_t - 0.5), _btn_z0 - btn_slot_kerf/2])
                    cube([_pillar_w, wall_t - 1.0, btn_slot_kerf]);
            }
            // Hinge thinning: pocket on interior face reduces hinge wall to 0.8mm
            translate([xc - 3, -(wall_t - 0.8), _btn_z0])
                cube([btn_hinge_w, wall_t - 0.8 + 0.1, _btn_tab_h]);
        }
        // USB-C (X=53.5): inner 9×3.5mm, housing 12.5×6.5mm, protrusion ~3mm
        // outer=false: combined outer pocket below covers µUSB ×2 + USB-C together
        translate([53.5, 0, 1 + 1.75])
            connector_stepped_cutout(9, 3.5, 12.5, 6.5, 3, cutout_reach, wall_t, outer=false);
        // Combined outer pocket for right µUSB + USB-C: X span = USB-C outer width (contains right µUSB)
        translate([53.5 - 12.5/2, -cutout_reach, 1 + 1.75 - 6.5/2])
            cube([12.7, cutout_reach - 0.5, 7.5 + 1.5 + 6.5/2 - (1 + 1.75 - 6.5/2)]);
    }

    // --- BACK FACE (Z=0): PiSugar PCB — access holes through back plate ---
    // Y measured from south/USB-C edge (Y=0 in assembled coords).
    color("blue", 0.4) {
        // Reset button at X=20.5, Y=5: 1.5mm diameter access hole (always a through-hole)
        translate([20.5, 5, -cutout_reach]) cylinder(d=1.5, h=cutout_reach + tol, $fn=16);
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
