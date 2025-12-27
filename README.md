# Millwork Nodes

A Blender add-on for parametric millwork design using geometry nodes. Part of the [MARS Platform](https://github.com/Mars-Platform) ecosystem.

## What It Does

Millwork Nodes takes project data from Conduit, renders parametric 3D cabinets and fixtures using Blender's geometry nodes, and outputs shop drawings and manufacturing data.

```
Conduit (business data) → Millwork Nodes → Shop Drawings + Parts/Machining → CAM/Nesting
```

### Key Outputs

- **Shop Drawings**: Cabinet elevations, sections, details (PDF/SVG)
- **Parts + Machining**: DXF per part with operation layers, cut lists

### Core Philosophy

> "The schema is the product. Blender is a renderer."

Cabinets are defined in structured documents (Component Assembly Schema). Blender executes that schema as 3D geometry. This separation means the data is portable, versionable, and integration-ready.

## Ecosystem Context

Millwork Nodes is the **native production path** in the MARS Platform:

| Component | Role |
|-----------|------|
| [Blueprint](https://github.com/Mars-Platform/blueprint) | Canonical schema, architecture decisions, platform standards |
| [Conduit](https://github.com/Mars-Platform/conduit) | Business/coordination layer—imports from ERPs, assigns materials/hardware |
| **Millwork Nodes** | Production layer—3D geometry, shop drawings, manufacturing output |
| [MV Library Tools](https://github.com/Mars-Platform/mv-library-tools) | Legacy library tooling—parse and query Microvellum libraries |

Conduit handles *who, what, when, how much*. Millwork Nodes handles *how to build*.

See [Blueprint ADR-0001](https://github.com/Mars-Platform/blueprint/blob/main/adr/0001-ecosystem-architecture.md) for the full ecosystem architecture.

## Current State

**Stage**: Proof of concept

### Complete
- Basic add-on structure (operators, panels, registration)
- Panel node group with parametric dimensions
- Architectural decisions documented (7 ADRs)
- Ecosystem alignment documented

### In Progress
- Carcass node group (assembles panels into cabinet shell)
- Component Assembly Schema formalization
- Corner-origin coordinate system implementation

## Documentation

- [Project North Star](docs/PROJECT_NORTH_STAR.md) — Full scope, roadmap, technical context
- [Ecosystem Alignment](docs/ECOSYSTEM_ALIGNMENT.md) — Relationship with Conduit
- [Architecture Decisions](docs/decisions/) — ADRs for key technical decisions

## Repository Structure

```
millwork-nodes/
├── node_groups/           # Geometry node group builders
│   ├── panel.py           # MN_Panel node group
│   └── carcass.py         # MN_Carcass node group
├── operators.py           # Blender operators
├── panels.py              # UI panels
├── __init__.py            # Add-on registration
└── docs/
    ├── PROJECT_NORTH_STAR.md
    ├── ECOSYSTEM_ALIGNMENT.md
    └── decisions/         # ADRs
```

## Platform Standards

This project follows [MARS Platform standards](https://github.com/Mars-Platform/blueprint/blob/main/adr/0003-shared-platform-standards.md):

- ADR format per [blueprint/docs/adr-standards.md](https://github.com/Mars-Platform/blueprint/blob/main/docs/adr-standards.md)
- Python tooling where applicable (Blender's embedded Python for add-on)

## License

Proprietary. All rights reserved.
