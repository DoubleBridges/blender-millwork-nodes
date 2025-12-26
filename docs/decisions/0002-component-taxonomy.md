# ADR-0002: Three-Class Component Taxonomy

**Status**: Accepted  
**Date**: 2025-12-26  
**Authors**: Dave Kane  
**Relates to**: ADR-0001 (Coordinate System), Nested bounding boxes

## Context

A cabinet is composed of many types of components: panels, shelves, dividers, doors, drawer boxes, hardware, etc. To build a composable system, we need a classification scheme that:

- Is generic enough to cover most use cases
- Is specific enough to define clear behavior contracts
- Supports arbitrary nesting depth
- Minimizes special-case logic

The key insight: components relate to *space* in fundamentally different ways.

## Decision

Cabinet Nodes uses **three component classes** based on how they relate to interior/exterior space:

### 1. Dividers

**Relationship to space**: Splits interior volume, outputs multiple child bounding boxes

**Characteristics**:
- Takes a parent bounding box as input
- Outputs geometry (the physical divider panel)
- Outputs N child bounding boxes (spaces created by the division)
- Can be nested (a child bbox can receive another divider)

**Examples**:
- Vertical partition (fixed shelf standing upright)
- Horizontal divider (fixed shelf lying flat)
- Grid divider (both vertical and horizontal)

**Interface**:
```
Inputs:
  - Parent bbox (origin, dimensions)
  - Division parameters (position, count, spacing)
  - Material/thickness

Outputs:
  - Geometry (divider panel(s))
  - Child bboxes (array of origin + dimensions)
```

### 2. Terminal Fills

**Relationship to space**: Occupies/consumes interior volume, outputs only geometry

**Characteristics**:
- Takes a parent bounding box as input
- Outputs geometry that serves or fills that space
- Does NOT output child bounding boxes (terminates the subdivision tree)
- May include multiple physical parts as a unit

**Examples**:
- Adjustable shelf system (shelf panels + shelf pin holes on sides)
- Drawer box (the interior box, not the face)
- Pullout hardware (waste bin, spice rack, etc.)
- Roll-out tray

**Interface**:
```
Inputs:
  - Parent bbox (origin, dimensions)
  - Component-specific parameters (shelf count, drawer height, etc.)
  - Material/thickness

Outputs:
  - Geometry (all physical parts of the component)
  - Machining data (shelf pin holes, drawer runner locations, etc.)
```

### 3. Externals

**Relationship to space**: Relates to exterior faces of a bounding box, not interior volume

**Characteristics**:
- References a face or opening, not a volume
- Positioned by overlay/offset from reference face
- Typically covers, closes, or finishes an exterior surface

**Examples**:
- Doors (overlay or inset to opening)
- Drawer fronts (attached to drawer box)
- Finished ends (applied to exposed cabinet sides)
- Toe kicks (cover the recessed base)
- Back panels (close the rear of cabinet)

**Interface**:
```
Inputs:
  - Reference face (which face: front, left, right, etc.)
  - Opening/face dimensions
  - Overlay or inset parameters
  - Material/thickness

Outputs:
  - Geometry (door panel, end panel, etc.)
  - Hardware mounting data (hinge locations, etc.)
```

## Rationale

### Why three classes?

Two classes (interior/exterior) isn't enough—dividers and terminal fills both operate on interior space but have fundamentally different outputs (child bboxes vs. none).

Four+ classes risks over-specification. Every additional class creates combinatorial complexity in how components interact. The three-class model covers observed use cases without forcing artificial distinctions.

### Why these three specifically?

They're distinguished by their **output contract**:

| Class | Consumes | Produces |
|-------|----------|----------|
| Divider | Interior bbox | Geometry + child bboxes |
| Terminal Fill | Interior bbox | Geometry only |
| External | Face reference | Geometry only |

This contract-based distinction makes the system predictable. When you add a component, you know exactly what it needs and what it provides.

### What about the carcass?

The carcass (outer shell: top, bottom, sides, back) is special—it *creates* the first interior bbox from nothing (or from wall space). It's the root of the subdivision tree.

Conceptually, the carcass could be considered a special divider (takes wall space, outputs interior bbox). In practice, it may warrant its own handling because it also produces external faces for doors/finished ends.

For now, we treat carcass as a distinct root component, not as a fourth class.

## Consequences

### Positive

- **Clear contracts**: Each class has defined inputs/outputs
- **Composability**: Dividers and fills can be mixed at any depth
- **Simplicity**: Three classes cover most cabinet constructions
- **Extensibility**: New component types slot into existing classes

### Negative

- **Edge cases**: Some components blur boundaries (e.g., a rollout shelf that also divides space)
- **Carcass ambiguity**: The outer shell doesn't fit cleanly into the three classes
- **Multi-function components**: A single component might need to act as both divider and fill

### Mitigations

- Handle edge cases by composition (a rollout that divides is a divider containing a fill)
- Document carcass as a special root type, not a fourth class
- Allow components to output optional child bboxes (fills that can divide if needed)

## Examples

### Simple Base Cabinet
```
Carcass (creates interior bbox)
└── Terminal Fill: Adjustable Shelves (fills the single interior)
External: Door (covers front opening)
External: Finished End (covers exposed right side)
```

### Divided Base Cabinet
```
Carcass (creates interior bbox)
└── Divider: Vertical Partition at 50% (creates left and right cells)
    ├── Left cell → Terminal Fill: Drawer Stack (4 drawers)
    └── Right cell → Terminal Fill: Adjustable Shelves
External: Drawer Fronts (4, cover left opening)
External: Door (covers right opening)
```

### Tall Pantry with Mixed Storage
```
Carcass (creates interior bbox)
└── Divider: Horizontal at 60" (creates upper and lower cells)
    ├── Upper cell → Divider: Horizontal at 50% (creates two shelf zones)
    │   ├── Zone 1 → Terminal Fill: Adjustable Shelves
    │   └── Zone 2 → Terminal Fill: Adjustable Shelves
    └── Lower cell → Divider: Vertical at 50%
        ├── Left → Terminal Fill: Pullout Waste Bin
        └── Right → Terminal Fill: Adjustable Shelves
External: Doors (2, cover full height)
```

## Future Considerations

- **Frames**: Face frames in traditional cabinetry act like dividers for door/drawer openings. The three-class model accommodates this—stiles and rails are dividers creating openings for externals.
- **Hardware**: Hinges, slides, etc. may need their own handling or could be attributes on externals/fills.
- **Machining**: Shelf pin holes, dado grooves, etc. are outputs alongside geometry—the class determines what machining is relevant.

---

*Accepted: 2025-12-26*
