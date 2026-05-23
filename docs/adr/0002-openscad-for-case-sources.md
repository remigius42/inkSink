<!-- spellchecker:ignore diffable -->

# ADR 0002 — OpenSCAD for 3D case sources

## Status

Accepted

## Context

The Device case is 3D-printed in two pieces (front bezel, back shell). The
source files need to live in the repository. Options considered:

- **OpenSCAD**: text-based parametric CAD, plain `.scad` files diff cleanly,
  no GUI required to read or modify
- **FreeCAD**: GUI-based parametric CAD, `.FCStd` files are binary and
  version-control unfriendly

The case geometry (rectangular enclosure with display cutout, button holes,
internal cavities) is well-suited to code-defined modeling. Future contributors
are more likely to have OpenSCAD than FreeCAD installed.

## Decision

Use OpenSCAD for all case source files in `hardware/case/`. Generated STLs may
be committed alongside sources for convenience but are not authoritative.

## Consequences

- Case files are plain text — readable, diffable, and editable without a GUI
- Shared parameters (wall thickness, tolerances) can live in a `params.scad`
  include
- Anyone iterating on dimensions needs OpenSCAD installed to preview changes
- FreeCAD is not used; contributors familiar only with FreeCAD would need to
  learn OpenSCAD
