# ADR-0003: Document as Source of Truth

**Status**: Accepted  
**Date**: 2025-12-26  
**Authors**: Dave Kane  
**Relates to**: Ecosystem integration, Conduit alignment

## Context

Blender stores everything in .blend files—a binary format optimized for Blender's internal data structures. For cabinet design, this creates problems:

- Data is locked in a format only Blender can read
- Version control is difficult (binary diffs are meaningless)
- Integration with other systems requires export/import cycles
- The parametric relationships become opaque outside Blender

The broader vision: Cabinet Nodes is part of an ecosystem that includes knowledge graphs, integration platforms (Conduit), and various downstream tools. Data needs to flow between systems without loss.

## Decision

**The cabinet document is the source of truth. Blender is a renderer.**

### Document Model

Cabinets are defined in structured documents (JSON or YAML):

```yaml
type: base_cabinet
id: cab-kitchen-001
name: "24\" Base Cabinet"
width: 609.6  # mm
height: 869.95  # mm (34.25")
depth: 609.6  # mm
construction_method: frameless_euro
material: maple_plywood_19mm

children:
  - type: vertical_divider
    position: 0.5  # 50% across
    children:
      - cell: left
        component:
          type: drawer_stack
          drawer_count: 4
      - cell: right
        component:
          type: adjustable_shelves
          shelf_count: 2

externals:
  - type: drawer_front
    count: 4
    cell: left
  - type: door
    style: shaker
    cell: right
```

### Execution Flow

```
Document (YAML/JSON)
    ↓
Add-on Python code (interprets document)
    ↓
Instantiates geometry node groups with parameters
    ↓
Blender renders 3D geometry
    ↓
User sees/manipulates in Blender UI
    ↓
Changes sync back to document
```

### What Lives Where

| Concern | Location | Why |
|---------|----------|-----|
| Cabinet structure & parameters | Document | Portable, versionable, integration-ready |
| Geometry generation logic | Geometry nodes | Visual, editable, Blender-native |
| Data transformation & UI | Python add-on | Bridges document and Blender |
| 3D visualization | Blender viewport | Best-in-class rendering |
| Manufacturing data | Document + export | Separate from visual representation |

## Rationale

### Why not just use .blend files?

.blend files are excellent for Blender-centric workflows. But:

- **Portability**: Other tools can't read them
- **Version control**: Can't meaningfully diff or merge
- **Data extraction**: Need Blender running to query cabinet data
- **Integration**: Every downstream system needs a Blender adapter

With documents as source of truth:
- Cut list generators read the document directly
- ERP systems sync from the document
- Nesting software receives structured data
- The .blend file becomes a cache/view, not the master

### Why JSON/YAML?

- Human-readable and editable
- Version control friendly
- Widely supported across languages
- Schema-validatable
- Matches Conduit's approach (YAML schemas as contracts)

### Alignment with Conduit

Conduit uses `schemas/*.schema.yaml` as contracts for its universal data model. Cabinet Nodes documents should align:

- Same structural conventions
- Compatible type definitions where applicable
- Products in Cabinet Nodes can export to Conduit's UniversalProduct schema
- Enables seamless handoff from design to production coordination

## Consequences

### Positive

- **Integration-ready**: Documents flow to any system
- **Version control**: Full git history with meaningful diffs
- **Separation of concerns**: Blender does rendering, documents hold data
- **Testability**: Validate documents without Blender
- **Portability**: Move to different rendering engine without data loss

### Negative

- **Synchronization**: Document and Blender state must stay in sync
- **Complexity**: Two representations of the same cabinet
- **Performance**: Parsing/serializing adds overhead
- **Learning curve**: Users must understand the document model

### Mitigations

- Robust sync logic in the add-on (document changes → Blender updates, and vice versa)
- Document structure mirrors Blender object hierarchy for intuitive mapping
- Lazy serialization (only write document on save/export, not every change)
- UI hides document complexity for template-based workflows

## Implementation Notes

### Sync Strategy

**Document → Blender**:
- On project load: traverse document, create/update Blender objects
- On document edit (via UI): update corresponding Blender object

**Blender → Document**:
- On parameter change in modifier panel: update document node
- On save: serialize full document to file
- On structural change (add/remove component): update document tree

### Storage Format

- Primary: YAML (human-editable, comments allowed)
- Alternative: JSON (better tooling support, no comments)
- Internal: Python dicts (runtime representation)

### File Association

Each .blend file can have an associated `.cabinet.yaml` (or embedded in .blend as text block):

```
project/
├── kitchen.blend
├── kitchen.cabinet.yaml  # Source of truth
└── exports/
    ├── parts/
    │   └── *.dxf
    └── cutlist.csv
```

## References

- Conduit's schema approach: `Conduit-win/schemas/*.schema.yaml`
- Conduit's PROJECT_NORTH_STAR: "The backend is the product. Frontends are windows."
- Similar pattern: Infrastructure as Code (Terraform, Pulumi)

---

*Accepted: 2025-12-26*
