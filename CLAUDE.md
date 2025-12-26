# CLAUDE.md - Millwork Nodes AI Context

> Quick reference for AI assistants working on this project.

## What Is This?

**Millwork Nodes** is a Blender add-on that serves as the native design-to-production system for custom millwork. It consumes project data from Conduit, renders parametric 3D cabinets, and produces:
1. **Shop drawings** (PDF/SVG) - elevations, sections, details
2. **Parts + machining** (DXF per part + cut list) - for nesting/CAM

The schema is the product. Blender is a renderer.

## Key Files

```
blender-millwork-nodes/  (currently named blender-cabinet-nodes)
├── __init__.py              # Add-on registration
├── operators.py             # Blender operators
├── panels.py                # UI panels
├── node_groups/
│   └── panel.py             # CN_Panel (to become MN_Panel)
├── schemas/                 # Component Assembly Schema (planned)
└── docs/
    ├── PROJECT_NORTH_STAR.md    # Vision and full scope
    ├── ECOSYSTEM_ALIGNMENT.md   # Conduit relationship
    └── decisions/               # ADRs (6 so far)
```

## Core Concepts

### Two Primary Outputs
1. **Shop drawings** - Native Blender 2D (Freestyle, Grease Pencil, orthographic views)
2. **Parts + machining** - DXF per panel with layers for operations, plus cut list

### Three Component Classes
1. **Dividers** - Split interior space, output child bounding boxes
2. **Terminal Fills** - Occupy interior space, output geometry only
3. **Externals** - Relate to exterior faces (doors, fronts, finished ends)

### Corner-Origin Coordinates
Back-bottom-left corner as origin at every level. Children position within parent's bounding box.

### Document as Source of Truth
Component Assembly Schema (YAML/JSON) defines cabinets. Blender renders them. Documents flow to other consumers without Blender.

## Ecosystem Position

```
Conduit (business data) → Millwork Nodes → Shop Drawings + Parts → CAM/Nesting
                              ↑
                    Component Assembly Schema
```

- **Conduit** = coordination layer (ERP data, materials, hardware assignments)
- **Millwork Nodes** = production layer (part resolution, geometry, machining, drawings)
- **Legacy adapters** = alternative paths for shops using Microvellum/Cabinet Vision

## Related Projects

| Project | Location | Role |
|---------|----------|------|
| Conduit | `../Conduit-win/` | Business data coordination |
| mmwx-wiki | `../mmwx-wiki/` | Knowledge documentation |

## Current State

- ✅ Basic add-on structure
- ✅ CN_Panel node group (proof of concept)
- ✅ 6 ADRs documenting architecture
- 🎯 Next: Rename to Millwork Nodes (MN_ prefix)
- 🎯 Next: Implement corner-origin positioning
- 🎯 Next: Create Component Assembly Schema
- 🔮 Future: Shop drawing generation system

## Guiding Principles

1. **The schema is the product** - Blender renders it, doesn't own it
2. **Transparent beats black box** - Logic is visible and editable
3. **Native path for control** - Legacy adapters for compatibility
4. **Two outputs, one source** - Drawings and parts from same model

## Naming

| Scope | Current | Target |
|-------|---------|--------|
| Repository | blender-cabinet-nodes | blender-millwork-nodes |
| Node prefix | CN_ | MN_ |
| Data model | (unnamed) | Component Assembly Schema |
| Add-on name | Cabinet Nodes | Millwork Nodes |

## Key ADRs

| ADR | Topic |
|-----|-------|
| 0001 | Corner-origin coordinate system |
| 0002 | Three-class component taxonomy |
| 0003 | Document as source of truth |
| 0004 | Output boundary (DXF + cut list) |
| 0005 | Library-driven workflow with selection UI |
| 0006 | Native shop drawing generation |

## When Starting a Conversation

1. Read `docs/PROJECT_NORTH_STAR.md` for full vision
2. Check `docs/ECOSYSTEM_ALIGNMENT.md` for Conduit relationship
3. Review relevant ADRs in `docs/decisions/`
4. Remember: TWO outputs (drawings AND parts)
5. Current code is POC; focus on architecture
