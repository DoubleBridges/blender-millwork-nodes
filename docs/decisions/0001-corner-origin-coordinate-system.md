# ADR-0001: Corner-Origin Hierarchical Coordinate System

**Status**: Accepted  
**Date**: 2025-12-26  
**Authors**: Dave Kane  
**Relates to**: Component taxonomy, nested bounding boxes

## Context

Blender's default mesh creation places objects with their origin at the geometric center. For cabinet design, this creates positioning challenges:

- Placing a cabinet against a wall requires calculating half-dimensions
- Nesting components inside a cabinet requires constant offset math
- The mental model doesn't match how cabinetmakers think about positioning

Cabinet design naturally works in terms of reference corners:
- A cabinet sits at a position along a wall, measured from a corner
- A panel inside a cabinet is positioned from the cabinet's back-bottom-left
- A shelf inside a divided space is positioned from that space's origin

## Decision

All Cabinet Nodes components use a **corner-origin** coordinate system:

1. **Walls**: Origin at back-bottom-left corner of the wall's bounding volume
2. **Cabinets**: Origin at back-bottom-left corner of cabinet exterior
3. **Interior spaces**: Origin at back-bottom-left of available interior volume
4. **Panels/components**: Positioned relative to their parent space's origin

The coordinate convention:
- **X**: Left to right (width)
- **Y**: Back to front (depth)
- **Z**: Bottom to top (height)

### Implementation

Geometry node groups output geometry translated so that one corner lands at (0,0,0). For a panel with Length (X), Width (Y), Thickness (Z):

```
# Current (centered): origin at geometric center
box at (0, 0, 0)

# Corner-origin: back-bottom-left at origin
box translated by (Length/2, Width/2, Thickness/2)
```

### Hierarchical Nesting

Each level in the hierarchy defines a coordinate space for its children:

```
Room space
└── Wall (positioned in room, defines wall space)
    └── Cabinet (positioned in wall space, defines cabinet space)
        └── Interior cell (derived from cabinet minus panel thicknesses)
            └── Divider or terminal component (positioned in cell space)
                └── Child cells (if divider)
```

Components are **agnostic to their nesting depth**. A drawer box receives a bounding box and sizes itself accordingly—it doesn't know or care whether it's two or five levels deep.

## Rationale

### Why back-bottom-left?

- Matches common CAD conventions for cabinet work
- "Bottom-left" is the natural reference when facing a wall of cabinets
- "Back" aligns with the wall surface for wall-mounted components
- Consistent across all levels eliminates special-case logic

### Why hierarchical?

- Each component only needs to know its parent's bounding box
- Changes cascade naturally (widen a cabinet, interior space adjusts, components reflow)
- Matches the mental model of "this thing goes inside that thing"

### Alternatives Considered

**Center origin (Blender default)**
- Pros: Familiar to Blender users, symmetric operations are simpler
- Cons: Constant offset calculations, doesn't match cabinetry mental model
- Rejected: The cognitive overhead outweighs symmetry benefits

**Multiple origin options per component**
- Pros: Maximum flexibility
- Cons: Complexity explosion, inconsistent positioning logic
- Rejected: Consistency is more valuable than per-component flexibility

## Consequences

### Positive

- Intuitive positioning: "place cabinet at X=120 on wall" means exactly that
- Simplified nesting: child positions are direct offsets from parent origin
- Mental model alignment: matches how cabinetmakers think and communicate
- Consistent transforms: rotation/mirroring have predictable pivot points

### Negative

- Diverges from Blender conventions (may confuse users expecting centered geometry)
- Requires explicit translation in every geometry node group
- Some operations (centering, mirroring) require calculating dimensions first

### Mitigations

- Document the convention clearly in all component node groups
- Provide utility nodes for common operations (center-in-space, mirror-about-center)
- UI labels can show both absolute position and relative position in parent

## Implementation Notes

The translation can be done with a Transform Geometry node after the Mesh Cube:

```
[Group Input] → [Combine XYZ] → [Mesh Cube] → [Transform Geometry] → [Group Output]
                                              ↑
                              translation = (L/2, W/2, T/2)
```

Or by calculating offset vectors and adding to the size/2 values.

## References

- Cabinet Vision uses similar back-bottom-left conventions
- Microvellum uses insertion points that can be configured per product
- Furniture design typically references from a consistent corner

---

*Accepted: 2025-12-26*
