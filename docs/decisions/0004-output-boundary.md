# ADR-0004: Output Boundary - DXF Per Part Plus Cut List

**Status**: Accepted  
**Date**: 2025-12-26  
**Authors**: Dave Kane  
**Relates to**: ADR-0003 (Document as Source of Truth), Manufacturing pipeline

## Context

The path from parametric design to CNC-cut parts involves multiple specialized tools:

1. **Design system** → parts with geometry and metadata
2. **Nesting software** → arranges parts on sheets, optimizes yield
3. **CAM/Post-processor** → generates machine-specific code

Each shop has existing tooling for steps 2 and 3. Cabinet Nodes shouldn't try to replace these—it should produce clean intermediate data that existing tools can consume.

The challenge: what format maximizes compatibility while preserving manufacturing-critical information?

## Decision

Cabinet Nodes outputs:

### Per Part: DXF File

- Panel outline with arcs preserved (not tessellated)
- Layers for different operations:
  - `OUTLINE` - through-cut profile
  - `DADO` - dado/groove operations
  - `DRILL` - hole locations
  - `POCKET` - pocket/mortise operations
  - `ENGRAVE` - text/marking
- Metadata in DXF extended data (XDATA) or separate sidecar file

### Per Project: Cut List

Structured data containing:

```yaml
parts:
  - id: "part-001"
    name: "Left Side"
    cabinet: "cab-kitchen-001"
    material: "maple_plywood_19mm"
    dimensions:
      length: 869.95  # mm
      width: 584.2
      thickness: 19.05
    grain_direction: "length"
    edge_banding:
      front: "maple_2mm"
      back: null
      left: null
      right: null
    quantity: 1
    dxf_file: "parts/cab-kitchen-001_left-side.dxf"
```

Format options:
- CSV (simple, universal import)
- JSON (structured, machine-readable)
- YAML (human-editable, comments)
- Excel (familiar to production staff)

## Rationale

### Why DXF?

- **Universal**: Virtually every nesting and CAM system reads DXF
- **Arc preservation**: Native arc/circle entities (not polyline approximations)
- **Layer support**: Operations can be separated and processed differently
- **Mature tooling**: Libraries available in every language (ezdxf for Python)
- **Industry standard**: Shops already have workflows around DXF

### Why per-part files?

- Each part can be handled independently
- Nesting software expects individual part files
- Failed parts don't corrupt the whole export
- Easier to reprocess single parts

### Why a separate cut list?

- Metadata doesn't belong in DXF (limited, proprietary extensions)
- Material, edge banding, grain direction are properties, not geometry
- Cut list format can vary per shop (CSV vs Excel vs custom)
- Enables cut list without DXF (for quoting, material ordering)

### Why not G-code directly?

- Machine-specific (different controllers, different dialects)
- Requires post-processor knowledge Cabinet Nodes shouldn't have
- Bypasses nesting (critical for sheet good optimization)
- Shops already have post-processors they trust

### Alignment with ecosystem

- Conduit exports Microvellum XML + Excel (different target, same philosophy)
- Cabinet Nodes exports DXF + cut list (design system output)
- Both produce structured data for downstream tools
- Neither tries to be the whole pipeline

## Consequences

### Positive

- **Agnostic**: Works with any nesting/CAM toolchain
- **Clean boundary**: Cabinet Nodes does design, other tools do manufacturing
- **Expertise respect**: Leverages specialized tools where they're strong
- **Shop flexibility**: No lock-in to specific nesting or CAM software

### Negative

- **No optimization control**: Can't influence nesting or toolpath decisions
- **Information loss**: Some parametric relationships don't survive export
- **Multiple files**: Shops must manage DXF folder + cut list together
- **Arc fidelity**: Depends on CAD Sketcher for non-rectangular panels

### Mitigations

- Package exports in ZIP with consistent structure
- Include manifest file linking parts to cut list entries
- Document expected workflow for common nesting tools
- Support multiple cut list formats (CSV, Excel, JSON)

## Implementation Notes

### DXF Generation

Use `ezdxf` library for Python:

```python
import ezdxf

doc = ezdxf.new('R2010')
msp = doc.modelspace()

# Panel outline
points = [(0, 0), (width, 0), (width, height), (0, height), (0, 0)]
msp.add_lwpolyline(points, dxfattribs={'layer': 'OUTLINE'})

# Shelf pin holes (example)
for hole in shelf_pin_holes:
    msp.add_circle(
        center=(hole.x, hole.y),
        radius=hole.diameter / 2,
        dxfattribs={'layer': 'DRILL'}
    )

doc.saveas(f"{part_id}.dxf")
```

### Arc Preservation

For curved edges from CAD Sketcher:
- Extract arc definitions from sketch (center, radius, start/end angles)
- Write as DXF ARC entities, not polylines
- CAM software receives true arcs for smooth toolpaths

### Cut List Formats

Support multiple outputs from same data:

```python
def export_cutlist(parts, format='csv'):
    if format == 'csv':
        return export_cutlist_csv(parts)
    elif format == 'xlsx':
        return export_cutlist_excel(parts)
    elif format == 'json':
        return export_cutlist_json(parts)
```

### Export Directory Structure

```
export_20251226/
├── manifest.json           # Links everything together
├── cutlist.csv             # Material, dimensions, edge banding
├── cutlist.xlsx            # Same data, Excel format
├── parts/
│   ├── cab-001_left-side.dxf
│   ├── cab-001_right-side.dxf
│   ├── cab-001_top.dxf
│   └── ...
└── README.txt              # Human-readable summary
```

## Future Considerations

- **Nesting hints**: Could include preferred orientation, must-avoid zones
- **Material optimization**: Could suggest sheet sizes based on parts
- **Batch export**: Export all cabinets in project, or selected only
- **Direct integration**: Plugins for specific nesting software (long term)

## References

- ezdxf library: https://ezdxf.readthedocs.io/
- DXF specification: Autodesk reference
- CAD Sketcher: Blender add-on for constraint-based sketching

---

*Accepted: 2025-12-26*
