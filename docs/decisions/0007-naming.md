# ADR-0007: Naming - Millwork Nodes and Component Assembly Schema

**Status**: Accepted  
**Date**: 2025-12-26  
**Authors**: Dave Kane  
**Relates to**: All previous ADRs, ecosystem positioning

## Context

The project started as "Cabinet Nodes"—a reasonable name for a Blender add-on that creates cabinet geometry via geometry nodes. As the scope clarified, limitations of this name became apparent:

1. **Too Blender-specific**: The data model (Component Assembly Schema) could be implemented in other tools
2. **Too narrow**: Millwork includes more than cabinets (fixtures, displays, architectural elements)
3. **Conflates concerns**: The add-on and the schema are different things with different lifecycles

We need names that accurately reflect scope and separate concerns.

## Decision

### The Data Model: Component Assembly Schema

The structured definition of how millwork products decompose into components, parts, and relationships.

**Characteristics**:
- Tool-agnostic (could be rendered by Blender, Rhino, web viewer, etc.)
- Defines the component taxonomy (dividers, terminal fills, externals)
- Defines the hierarchical bounding box system
- Portable, versionable, integration-ready

**Not called**:
- "Cabinet Schema" (too narrow)
- "Millwork Nodes Schema" (ties to implementation)
- "Universal Component Model" (confuses with Conduit's Universal* naming)

### The Blender Add-on: Millwork Nodes

The implementation that renders Component Assembly Schema documents using Blender's geometry nodes.

**Characteristics**:
- Blender-specific
- Uses geometry nodes as execution engine
- Provides custom UI for editing
- Generates shop drawings and manufacturing output

**Not called**:
- "Cabinet Nodes" (too narrow)
- "Component Assembly Blender" (awkward)
- "Blender Millwork" (doesn't convey the node-based approach)

### Naming Conventions

| Scope | Name |
|-------|------|
| Data model / schema | Component Assembly Schema (CAS) |
| Blender add-on | Millwork Nodes |
| Node group prefix | `MN_` |
| Python package | `millwork_nodes` |
| Repository | `blender-millwork-nodes` |

## Rationale

### Why "Millwork"?

- Industry-standard term covering cabinets, fixtures, displays, architectural woodwork
- Broader than "cabinet" without being vague
- Aligns with how the industry talks about this work

### Why "Nodes"?

- Accurately describes the Blender implementation (geometry nodes)
- Familiar to Blender users
- Suggests composability and visual programming

### Why separate naming?

The schema and the add-on have different:

**Lifecycles**: Schema may stabilize while add-on continues evolving

**Consumers**: Schema could be read by web apps, mobile apps, other CAD tools; add-on is Blender-only

**Ownership**: Schema is ecosystem-wide; add-on is one implementation

Conflating them would create confusion when discussing integrations or alternative implementations.

## Consequences

### Positive

- **Clear communication**: Can discuss schema vs. implementation distinctly
- **Future-proof**: Schema naming doesn't lock us to Blender
- **Accurate scope**: "Millwork" covers the full range of products
- **Professional**: Industry-aligned terminology

### Negative

- **Rename effort**: Need to update code, documentation, repository
- **Potential confusion**: Two names to explain to new contributors
- **Transition period**: Old name may persist in discussions

### Migration Plan

1. Update documentation (this conversation) ✓
2. Rename repository (`blender-cabinet-nodes` → `blender-millwork-nodes`)
3. Update `bl_info` in `__init__.py`
4. Rename node group prefix (`CN_` → `MN_`)
5. Update Python package structure
6. Redirect any old references

## References

- "Millwork" industry usage: AWI (Architectural Woodwork Institute) standards
- Similar naming patterns: Geometry Nodes, Animation Nodes, Sverchok

---

*Accepted: 2025-12-26*
