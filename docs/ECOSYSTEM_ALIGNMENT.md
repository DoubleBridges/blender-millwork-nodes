# Ecosystem Alignment: Millwork Nodes ↔ Conduit

**Date**: 2025-12-26  
**Purpose**: Define the relationship between Millwork Nodes and Conduit, identify integration points, and clarify responsibilities.

---

## The Ecosystem

```
┌─────────────────────────────────────────────────────────────────────┐
│                         KNOWLEDGE GRAPH                             │
│           (Ontology: what things are, how they relate)              │
│    Materials, Hardware, Construction Methods, Machine Operations    │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                    Referenced by both systems
                                   │
        ┌──────────────────────────┴──────────────────────────┐
        ▼                                                      ▼
┌───────────────────┐                              ┌───────────────────┐
│      CONDUIT      │                              │  MILLWORK NODES   │
│                   │                              │                   │
│  Business Layer   │─────── Native Path ────────▶│  Production Layer │
│                   │                              │                   │
│  • ERP Import     │                              │  • 3D Rendering   │
│  • Customer Data  │                              │  • Part Resolution│
│  • Scope/Reqs     │    ┌─────────────────┐       │  • Shop Drawings  │
│  • Materials      │    │ UniversalProject│       │  • DXF + Cut List │
│  • Hardware       │───▶│ Model + CAS     │──────▶│                   │
│                   │    └─────────────────┘       │                   │
│  Legacy Adapters: │                              │                   │
│  • Microvellum    │                              │                   │
│  • Cabinet Vision │                              │                   │
└───────────────────┘                              └───────────────────┘
```

**CAS** = Component Assembly Schema (the rich product model)

---

## Division of Responsibilities

### Conduit Owns

| Domain | Examples |
|--------|----------|
| **Business data** | Customer info, contacts, addresses |
| **Project scope** | Rooms/locations, product selections, quantities |
| **Requirements** | Specifications, finish schedules, constraints |
| **Material assignments** | Which material for which product type |
| **Hardware assignments** | Which hinges, slides, pulls for which configuration |
| **Cost/pricing** | Material costs, labor, margins |
| **Timeline** | Due dates, milestones |
| **Adapter translations** | ERP → Universal Model → Legacy CAD/CAM |

Conduit is the **coordination layer**. It knows about the business: who, what, when, how much.

### Millwork Nodes Owns

| Domain | Examples |
|--------|----------|
| **Component structure** | Carcass, dividers, fills, externals |
| **Part resolution** | Exploding products into individual panels |
| **Geometry generation** | 3D models via geometry nodes |
| **Joinery logic** | Dado depths, rabbet widths, edge banding |
| **Machining data** | Drill patterns, pocket locations, routing paths |
| **Shop drawings** | Elevations, sections, details, schedules |
| **Manufacturing output** | DXF per part, cut lists |

Millwork Nodes is the **production layer**. It knows about making things: how to build, what parts, what operations.

### Shared / Handoff

| Data | Origin | Consumer |
|------|--------|----------|
| UniversalProjectModel | Conduit | Millwork Nodes |
| Component Assembly Schema | Millwork Nodes defines | Both reference |
| Material library | Knowledge Graph | Both reference |
| Hardware library | Knowledge Graph | Both reference |
| Construction methods | Defined in ecosystem | Both apply |

---

## Data Flow

### Forward Flow (Design to Production)

```
1. ERP System (Innergy, etc.)
   └─▶ Conduit ingests via adapter
   
2. Conduit enriches:
   • Categorizes products
   • Assigns materials from library
   • Assigns hardware from library
   • Calculates relationships (neighbors, stacking)
   • Derives manufacturing prompts
   
3. Conduit outputs UniversalProjectModel
   • Products with dimensions, materials, hardware refs
   • Locations with walls, positions
   • Project metadata (customer, dates)
   
4. Millwork Nodes consumes project:
   • Resolves each product into Component Assembly
   • Generates 3D geometry in Blender
   • User reviews/edits via custom UI
   
5. Millwork Nodes outputs:
   • Shop drawings (PDF/SVG)
   • Parts + machining (DXF per part)
   • Cut list (CSV/JSON/Excel)
   
6. Downstream:
   • Shop drawings → production floor
   • Parts → nesting software → CAM → CNC
```

### Feedback Flow (Production to Business)

Future consideration: information flowing back from production to Conduit:
- Actual material usage vs. estimated
- Production time tracking
- Quality issues linked to source data

---

## Schema Relationships

### Conduit's UniversalProduct (Simplified)

```yaml
# What Conduit knows about a product
id: "prod-001"
name: "36\" Base Cabinet"
category: "Base Cabinet"
width: 36.0      # inches
height: 34.5
depth: 24.0
material_id: "mat-maple-ply-3/4"
hardware_set_id: "hw-euro-soft-close"
location_id: "loc-kitchen"
wall_id: "wall-north"
x_origin: 120.0  # position on wall
prompts:
  - "LEFT END"
  - "TOE NOTCH"
```

This is sufficient for coordination and legacy adapter export. It's a **product-level** view.

### Millwork Nodes' Component Assembly (Rich)

```yaml
# What Millwork Nodes knows about the same product
id: "prod-001"
type: "base_cabinet"
exterior:
  width: 914.4   # mm
  height: 876.3
  depth: 609.6
  
carcass:
  material: → ref:mat-maple-ply-3/4
  construction: "dado_rabbet"
  parts:
    - id: "left_side"
      dimensions: [depth, height, thickness]
      edges: {front: "maple_2mm", ...}
    - id: "right_side"
      ...
    - id: "top"
      ...
    - id: "bottom"
      ...
    - id: "back"
      ...

interior:
  bbox: [width - 2*thickness, depth - thickness, height - 2*thickness]
  children:
    - type: "vertical_divider"
      position: 0.5
      children:
        - cell: "left"
          component:
            type: "drawer_stack"
            drawer_count: 4
        - cell: "right"
          component:
            type: "adjustable_shelves"
            
externals:
  - type: "drawer_front"
    count: 4
    cell: "left"
    style: → ref:door-style-shaker
  - type: "door"
    cell: "right"
    style: → ref:door-style-shaker
```

This is a **component-level** view. It knows every panel, every edge, every machining operation.

### The Bridge

Millwork Nodes can generate the rich model FROM Conduit's simplified model + rules:

```
UniversalProduct (what) + Construction Method (how) = Component Assembly (detailed)
```

The construction method fills in the details that Conduit doesn't specify:
- Default joinery type
- Edge banding rules
- Shelf pin hole patterns
- Hardware mounting standards

---

## Integration Points

### Phase 1: File-Based Handoff

```
Conduit                          Millwork Nodes
   │                                   │
   ├── Export JSON ─────────────────▶  │
   │   (UniversalProjectModel)         │
   │                                   ├── Import JSON
   │                                   │
   │                                   ├── Resolve components
   │                                   │
   │                                   ├── Generate geometry
   │                                   │
   │   ◀──────────────────────────────┤
   │        (status/results)           │
```

Simple, decoupled. Good for initial development.

### Phase 2: API Integration

```
Conduit                          Millwork Nodes
   │                                   │
   ├── GraphQL query ───────────────▶  │
   │   (get project)                   │
   │                                   │
   │   ◀─────────────────────────────  │
   │   (project data)                  │
   │                                   │
   │                                   ├── Generate outputs
   │                                   │
   ├── GraphQL mutation ◀────────────  │
   │   (report results)                │
```

Tighter integration. Conduit orchestrates, Millwork Nodes executes.

### Phase 3: Shared Services

Both systems reference shared services:
- Material library API
- Hardware library API  
- Construction method library
- Knowledge graph queries

---

## Terminology Mapping

| Concept | Conduit | Millwork Nodes | Canonical |
|---------|---------|----------------|-----------|
| A cabinet | UniversalProduct | Cabinet (document) | Product |
| A room | UniversalLocation | Location | Location |
| A wall | UniversalWall | Wall | Wall |
| Material spec | material_id (ref) | material (ref + resolved) | Material |
| Style preset | (in customer config) | Construction Method | Construction Method |
| Internal structure | (not modeled) | Component Assembly | Component Assembly |
| Individual panel | (not modeled) | Part | Part |

---

## Future: Component Assembly Schema as Universal Product Model

Currently, Conduit's UniversalProduct is simplified—it knows products, not parts.

Long-term vision: **Component Assembly Schema becomes the rich product model across the ecosystem.**

- Conduit adopts CAS for products that warrant detail
- Legacy adapters flatten CAS → their expected format
- Millwork Nodes works natively with CAS
- Other tools (web viewer, mobile app) can render CAS

The simplified model remains for:
- Quick estimates before full resolution
- Legacy systems that can't consume detail
- Summary views and reports

---

## Open Questions

1. **Units**: Conduit uses inches, Millwork Nodes uses mm internally. Where does conversion happen?
   - Recommendation: Convert at boundaries, store in canonical units (mm)

2. **Material library location**: Does it live in Conduit, Millwork Nodes, or a shared service?
   - Recommendation: Shared service (knowledge graph), both reference

3. **Construction method authoring**: Where are methods created and edited?
   - Recommendation: Separate tool/UI, both systems consume

4. **Feedback loop**: How does production data flow back to inform future estimates?
   - Future consideration, not blocking

---

*Last updated: 2025-12-26*
