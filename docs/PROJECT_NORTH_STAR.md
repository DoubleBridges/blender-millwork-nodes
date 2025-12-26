# Millwork Nodes - Project North Star

> **One-page guide to what Millwork Nodes is, who it's for, and where we're headed.**
> For AI assistants and collaborators.

---

## What Is Millwork Nodes?

**Millwork Nodes is a native design-to-production system for custom millwork, built on Blender.** It consumes project data from Conduit, renders parametric 3D cabinets using geometry nodes, and outputs shop drawings and manufacturing data.

Think of it as: **Conduit (business data) → Millwork Nodes → Shop Drawings + Parts/Machining → CAM/Nesting**

The core problem: Existing CAD/CAM systems (Microvellum, Cabinet Vision) are black boxes. You can't see or control how they resolve parts, generate drawings, or produce machining data. When something goes wrong, you're at the mercy of the vendor. Millwork Nodes puts the logic in the open—transparent, editable, yours.

---

## Where It Fits in the Ecosystem

```
┌─────────────────────────────────────────────────────────────────────┐
│                            CONDUIT                                  │
│  ┌──────────┐    ┌─────────────────────┐    ┌──────────────────┐   │
│  │ Innergy  │───▶│                     │───▶│ Microvellum      │   │
│  │ 2020     │    │ UniversalProject    │    │ Cabinet Vision   │   │
│  │ CSV      │    │ Model               │    │ (legacy paths)   │   │
│  │ Manual   │    │                     │    └──────────────────┘   │
│  └──────────┘    └─────────┬───────────┘                           │
└────────────────────────────┼───────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        MILLWORK NODES                               │
│  ┌─────────────────────┐    ┌─────────────────────────────────┐    │
│  │ Component Assembly  │    │         Blender Engine          │    │
│  │ Schema              │───▶│  • Geometry Nodes (3D)          │    │
│  │ (part resolution)   │    │  • Custom UI                    │    │
│  └─────────────────────┘    │  • Shop Drawing Generation      │    │
│                             └──────────────┬──────────────────┘    │
│                                            │                        │
│                         ┌──────────────────┴──────────────────┐    │
│                         ▼                                      ▼    │
│              ┌──────────────────┐              ┌──────────────────┐ │
│              │  Shop Drawings   │              │ Parts + Machining│ │
│              │  (PDF/SVG)       │              │ (DXF + Cut List) │ │
│              └──────────────────┘              └────────┬─────────┘ │
└─────────────────────────────────────────────────────────┼──────────┘
                                                          │
                                                          ▼
                                               ┌──────────────────┐
                                               │   CAM/Nesting    │
                                               │   (shop's own)   │
                                               └──────────────────┘
```

**Conduit** handles business data: customer info, costs, scope, requirements, materials, hardware. It ingests from various ERPs and exports to various targets.

**Millwork Nodes** is the native production path: takes Conduit's project model, resolves it into 3D geometry with full part detail, and produces the outputs a shop floor needs.

**Legacy adapters** (Microvellum, Cabinet Vision) remain available for shops committed to those ecosystems. Millwork Nodes is for shops that want control.

---

## Who Is It For?

**Primary users:** Production coordinators and engineers at custom millwork shops who want transparency and control over their design-to-manufacturing pipeline.

**Typical workflow:**
1. Conduit imports job from ERP (customer, rooms, product selections)
2. Millwork Nodes receives project with material/hardware assignments
3. User reviews 3D model, makes adjustments via custom UI
4. System generates shop drawings (elevations, sections, details)
5. System generates parts with machining (DXF per part + cut list)
6. Parts go to shop's existing nesting/CAM software
7. Shop drawings go to production floor

**Key insight:** The parametric logic is visible. When a cabinet doesn't resolve correctly, you can see why and fix it—in geometry nodes, in the schema, or in Conduit's source data.

---

## Two Primary Outputs

### 1. Shop Drawings (2D Documentation)

Blender has native 2D capabilities that most users overlook:
- Orthographic camera views (front, side, top, sections)
- Freestyle line rendering for technical illustration
- Grease Pencil for annotations
- Geometry-node-driven dimensions and callouts
- Export to PDF, SVG, or DXF

Shop drawings include:
- Cabinet elevations with dimensions
- Section views showing interior configuration
- Detail views for joinery, hardware mounting
- Cut lists and material schedules

### 2. Parts + Machining (Manufacturing Data)

Every panel becomes a discrete output:
- DXF file with outline, dado locations, drill patterns, pockets
- Layers separate operation types for CAM processing
- Arc geometry preserved (not tessellated) for smooth toolpaths

Cut list includes:
- Part dimensions, material, grain direction
- Edge banding per edge
- Quantity, parent cabinet reference
- Link to corresponding DXF file

---

## Architecture Philosophy

**The schema is the product. Blender is a renderer.**

| Layer | Responsibility |
|-------|----------------|
| **Component Assembly Schema** | Defines cabinet structure, component taxonomy, part relationships |
| **UniversalProjectModel** (from Conduit) | Business context: customer, location, materials, hardware |
| **Blender Geometry Nodes** | Renders schema into 3D geometry |
| **Python Add-on** | Manages data, custom UI, export pipelines |
| **Shop Drawing System** | 2D views, dimensions, annotations |
| **Part Export System** | DXF generation, cut list generation |

The Component Assembly Schema could be implemented in other tools (Rhino/Grasshopper, web viewer, etc.). Millwork Nodes is the Blender implementation.

---

## Current State (December 2025)

### ✅ Complete
- Basic add-on structure (operators, panels, registration)
- CN_Panel node group with Length/Width/Thickness inputs
- Architectural decisions documented (5 ADRs)
- Ecosystem alignment with Conduit documented

### 🎯 Current Focus
- Renaming from "Cabinet Nodes" to "Millwork Nodes"
- Implementing corner-origin coordinate system
- Defining Component Assembly Schema
- Building first complete cabinet template

### 🔮 Roadmap
- Shop drawing generation system
- Construction methods (style presets)
- CAD Sketcher integration for custom panel shapes
- DXF export with arc preservation
- Full Conduit integration (consume UniversalProjectModel)

---

## Key Technical Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Execution engine | Blender Geometry Nodes | Visual, composable, transparent logic |
| Data model | Component Assembly Schema (YAML/JSON) | Portable, versionable, tool-agnostic |
| Coordinate system | Corner-origin hierarchical | Intuitive positioning within parent spaces |
| Component taxonomy | 3 classes (dividers, terminal fills, externals) | Minimal, generic, extensible |
| Manufacturing output | DXF per part + cut list | Agnostic to downstream CAM tools |
| Drawing output | Native Blender 2D (Freestyle, Grease Pencil) | No external dependencies |
| UI approach | Selection-driven property panel | No manual node graph navigation |

See `docs/decisions/` for full ADRs.

---

## Repository Map

```
blender-millwork-nodes/
├── node_groups/           # Geometry node group builders
│   └── panel.py           # CN_Panel (to be renamed MN_Panel)
├── operators.py           # Blender operators
├── panels.py              # UI panels
├── __init__.py            # Add-on registration
├── schemas/               # Component Assembly Schema (planned)
└── docs/
    ├── PROJECT_NORTH_STAR.md
    ├── ECOSYSTEM_ALIGNMENT.md
    └── decisions/         # ADRs
```

---

## Naming Conventions

| Scope | Name | Notes |
|-------|------|-------|
| The schema/data model | Component Assembly Schema | Tool-agnostic, could be implemented anywhere |
| The Blender add-on | Millwork Nodes | Blender-specific implementation |
| Node group prefix | `MN_` | Millwork Nodes (was `CN_` for Cabinet Nodes) |
| The ecosystem | (unnamed) | Conduit + Millwork Nodes + Knowledge Graph |

---

## Quick Context for AI Assistants

When starting a conversation about Millwork Nodes:

1. **Read this document** – Understand the full scope including shop drawings
2. **Check `docs/decisions/`** – ADRs have detailed rationale
3. **See `ECOSYSTEM_ALIGNMENT.md`** – Relationship with Conduit
4. **Remember the outputs** – Shop drawings AND parts/machining, not just one

**Guiding principles:**
- "The schema is the product. Blender is a renderer."
- "Transparent and editable beats black box."
- "Native path for control, legacy adapters for compatibility."

---

*Last updated: 2025-12-26*
