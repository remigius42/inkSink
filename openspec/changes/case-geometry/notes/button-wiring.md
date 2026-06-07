# Button Wiring

## Soldering Procedure

Solder 28AWG silicone wires to the GPIO header pins before placing the
HAT side-by-side. Do this before the HAT is wired up so the header is
fully accessible.

1. Cut 28AWG silicone wires ~10–15cm
2. Strip 2mm of insulation from one end
3. Slide 5mm of 2mm heat shrink tubing onto each wire
4. Solder wire to the **side** of the GPIO header pin (between plastic
   base and tip — not the tip)
5. Slide heat shrink over joint and apply heat
6. Repeat for all button GPIO pins (4, 12, 13, 16, 19, 22, 26, 27) + GND

```text
GPIO Pin ─── [28AWG wire with heat shrink] ─── Tactile Button ─── GND
```

## Case Design Implications

- Wire routing: wires run from the GPIO header area down to the bottom
  face; the back shell cavity must leave a clear channel along the bottom
  interior
- Cavity must have enough room for soldered wire tails (~5mm) behind the
  tactile buttons
- All 8 button wires share a single common GND — one GND pin needed in
  addition to the 8 signal wires; no power-button wire (PiSugar 3 handles
  power)
