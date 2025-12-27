# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for Millwork Nodes.

## Standards

ADRs follow [MARS Platform ADR Standards](https://github.com/Mars-Platform/blueprint/blob/main/docs/adr-standards.md).

## Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [0001](0001-corner-origin-coordinate-system.md) | Corner-Origin Hierarchical Coordinate System | Accepted | 2025-12-26 |
| [0002](0002-component-taxonomy.md) | Three-Class Component Taxonomy | Accepted | 2025-12-26 |
| [0003](0003-document-source-of-truth.md) | Document as Source of Truth | Accepted | 2025-12-26 |
| [0004](0004-output-boundary.md) | Output Boundary - DXF Per Part Plus Cut List | Accepted | 2025-12-26 |
| [0005](0005-library-driven-workflow.md) | Library-Driven Workflow with Selection-Based UI | Accepted | 2025-12-26 |
| [0006](0006-shop-drawing-generation.md) | Native Shop Drawing Generation | Accepted | 2025-12-26 |
| [0007](0007-naming.md) | Naming - Millwork Nodes and Component Assembly Schema | Accepted | 2025-12-26 |

## Relationship to Blueprint

These ADRs govern Millwork Nodes-specific decisions. Ecosystem-wide decisions live in [Blueprint](https://github.com/Mars-Platform/blueprint/tree/main/adr):

| Blueprint ADR | Relevance to Millwork Nodes |
|---------------|----------------------------|
| [ADR-0001: Ecosystem Architecture](https://github.com/Mars-Platform/blueprint/blob/main/adr/0001-ecosystem-architecture.md) | Defines Millwork Nodes as the "production layer" |
| [ADR-0002: Persistence Strategy](https://github.com/Mars-Platform/blueprint/blob/main/adr/0002-updm-persistence-strategy.md) | PostgreSQL as primary persistence; applies when Millwork Nodes syncs with Knowledge Graph |
| [ADR-0003: Shared Platform Standards](https://github.com/Mars-Platform/blueprint/blob/main/adr/0003-shared-platform-standards.md) | ADR format, cross-referencing requirements |

## Creating New ADRs

Use sequential four-digit numbers: `0008-title.md`, `0009-title.md`, etc.

See [Blueprint ADR template](https://github.com/Mars-Platform/blueprint/blob/main/adr/template.md) for required sections.
