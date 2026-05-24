## Purpose

Define the OpenSCAD source file structure for the two-piece device case,
including shared dimension parameters derived from the build guide.

## Requirements

### Requirement: Case sources are OpenSCAD files

The `hardware/case/` directory SHALL contain OpenSCAD (`.scad`) source files
for the two-piece device case: `front.scad`, `back.scad`, and
`assembly.scad`. Shared parameters SHALL be defined in a `params.scad` file
included by the others.

#### Scenario: Files are parseable by OpenSCAD

- **WHEN** each `.scad` file is opened in OpenSCAD
- **THEN** it loads without parse errors (preview may be empty for stubs)

### Requirement: Stubs reference build guide dimensions

Stub files SHALL include the target device dimensions from the build guide
as commented parameters: 170×115×26mm overall, 163×98mm display cutout,
22mm electronics cavity depth, 6mm battery cavity depth.

#### Scenario: Dimensions are present in params.scad

- **WHEN** `params.scad` is read
- **THEN** all six dimensions from the build guide are present as named
  variables with inline comments

### Requirement: `assembly.scad` shows both pieces together

`assembly.scad` SHALL import `front.scad` and `back.scad` and position them
for visual inspection of the assembled device.

#### Scenario: Assembly is a union of both pieces

- **WHEN** `assembly.scad` is rendered in OpenSCAD
- **THEN** both front and back pieces are visible in their assembled positions
