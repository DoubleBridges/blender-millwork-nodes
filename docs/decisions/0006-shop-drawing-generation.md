# ADR-0006: Native Shop Drawing Generation

**Status**: Accepted  
**Date**: 2025-12-26  
**Authors**: Dave Kane  
**Relates to**: ADR-0004 (Output Boundary), Blender 2D capabilities

## Context

Shop drawings are essential manufacturing documentation:
- Cabinet elevations with dimensions
- Section views showing interior configuration
- Detail views for joinery and hardware
- Material schedules and cut lists

Traditional CAD/CAM systems (Microvellum, Cabinet Vision) generate shop drawings, but they're black boxes—when drawings are wrong or insufficient, you're limited in what you can fix.

Blender has underutilized 2D capabilities that could serve this need natively:
- Orthographic camera views
- Freestyle line rendering
- Grease Pencil annotation
- Geometry nodes for procedural content
- Export to PDF, SVG, DXF

## Decision

Millwork Nodes includes **native shop drawing generation** as a primary output, alongside parts/machining data.

### Drawing Types

**Cabinet Elevations**
- Front view with overall dimensions
- Height callouts for internal divisions
- Door/drawer front representation
- Hardware indication

**Section Views**
- Vertical sections showing shelf configuration
- Horizontal sections showing divider layout
- Material thickness visible

**Detail Views**
- Joinery details (dado depths, rabbets)
- Hardware mounting locations
- Edge banding indication

**Schedules**
- Cut list (parts with dimensions, material, edge banding)
- Hardware schedule
- Material summary

### Technical Approach

**View Generation**
```
3D Cabinet Geometry
    ↓
Orthographic cameras (front, side, top, section planes)
    ↓
Freestyle renders hidden/visible line styles
    ↓
Grease Pencil overlays dimensions, notes
    ↓
Compositor combines into sheet layout
    ↓
Export to PDF/SVG
```

**Dimension Automation**
Geometry nodes can calculate and output dimension values:
- Bounding box extents
- Component positions within parent
- Spacing between elements

These values drive Grease Pencil text objects or custom annotation geometry.

**View Linking**
Section cut planes as Blender objects that:
- Define where the section is taken
- Generate section view camera automatically
- Update when cabinet geometry changes

### Output Formats

| Format | Use Case |
|--------|----------|
| PDF | Print-ready shop drawings, multi-page documents |
| SVG | Scalable vectors for further editing, web display |
| DXF | Import into other CAD systems if needed |
| PNG | Quick previews, thumbnails |

## Rationale

### Why native in Blender?

**Control**: When a dimension is wrong or a view is unclear, you can fix it. No waiting for vendor patches.

**Integration**: Drawings derive from the same 3D model as manufacturing data. One source of truth.

**Customization**: Each shop has drawing standards. Native generation means you define those standards.

**Cost**: No additional software licenses for drawing generation.

### Why not external tools?

**Round-trip loss**: Exporting to AutoCAD/Draftsight for drawings means maintaining two representations.

**Sync burden**: Model changes require re-export and manual drawing updates.

**License cost**: Additional CAD software for 2D work.

### Blender's 2D Strengths

- **Freestyle**: Purpose-built for technical line rendering (visible, hidden, crease, contour lines)
- **Grease Pencil**: Full 2D drawing system with layers, materials, modifiers
- **Geometry Nodes**: Can generate annotation geometry procedurally
- **Compositor**: Combine multiple views into sheet layouts
- **Python API**: Full scripting access to automate drawing generation

### Blender's 2D Limitations

- **Dimension tools**: No native parametric dimensions (must build or use add-ons)
- **Sheet management**: No built-in title blocks, revision tracking
- **Learning curve**: Different workflow than traditional CAD drafting

## Consequences

### Positive

- **Single source of truth**: Drawings and manufacturing data from same model
- **Full control**: Drawing standards are yours to define
- **No additional cost**: Uses Blender's existing capabilities
- **Automation potential**: Geometry nodes can drive annotation content
- **Consistency**: Drawing style enforced by templates, not manual effort

### Negative

- **Development effort**: Must build dimension/annotation system
- **Learning curve**: Team must learn Blender's 2D workflow
- **Maturity gap**: Not as polished as dedicated drafting software
- **Performance**: Complex drawings with many annotations may be slow

### Mitigations

- Build reusable drawing templates with standard annotations
- Investigate existing Blender CAD add-ons (CAD Sketcher, others) for dimension tools
- Generate annotations procedurally where possible (reduce manual placement)
- Cache rendered views; only regenerate on model change

## Implementation Notes

### View Setup Automation

```python
def create_cabinet_views(cabinet_obj):
    """Create standard orthographic views for a cabinet."""
    views = []
    
    # Front elevation
    views.append(create_ortho_camera(
        name=f"{cabinet_obj.name}_front",
        location=(0, -10, cabinet_height/2),
        rotation=(90, 0, 0),  # Looking at front
    ))
    
    # Right side
    views.append(create_ortho_camera(
        name=f"{cabinet_obj.name}_right",
        location=(10, 0, cabinet_height/2),
        rotation=(90, 0, 90),
    ))
    
    # Top/plan
    views.append(create_ortho_camera(
        name=f"{cabinet_obj.name}_top",
        location=(0, 0, 10),
        rotation=(0, 0, 0),
    ))
    
    return views
```

### Freestyle Line Configuration

```python
# Line styles for technical drawing
LINESTYLES = {
    'visible': {'color': (0, 0, 0), 'thickness': 2},
    'hidden': {'color': (0.5, 0.5, 0.5), 'thickness': 1, 'dashed': True},
    'center': {'color': (0.8, 0, 0), 'thickness': 0.5, 'dash_dot': True},
    'dimension': {'color': (0, 0, 0.8), 'thickness': 0.5},
}
```

### Dimension Generation (Conceptual)

```python
def generate_dimension(start_point, end_point, offset, text=None):
    """Generate dimension annotation geometry."""
    length = (end_point - start_point).length
    text = text or f"{length:.2f}"
    
    # Create geometry: extension lines, dimension line, arrows, text
    # Could be Grease Pencil strokes or mesh geometry
    ...
```

## Future Considerations

- **Parametric dimensions**: Dimensions that update automatically when geometry changes
- **Drawing templates**: Standard sheet sizes, title blocks, revision tables
- **Batch generation**: Generate all drawings for a project in one operation
- **PDF bookmarks**: Multi-page PDF with navigation
- **Comparison views**: Show before/after for change orders

## References

- Blender Freestyle documentation
- Blender Grease Pencil documentation
- CAD Sketcher add-on (constraint-based sketching)
- Technical drawing standards (ASME Y14.5, etc.)

---

*Accepted: 2025-12-26*
