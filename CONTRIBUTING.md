# Contributing to Millwork Nodes

This project is part of the [MARS Platform](https://github.com/Mars-Platform). Development follows platform-wide standards defined in [Blueprint](https://github.com/Mars-Platform/blueprint).

## Standards Reference

All contributors should be familiar with:

| Standard | Description |
|----------|-------------|
| [Commit Conventions](https://github.com/Mars-Platform/blueprint/blob/master/docs/commit-conventions.md) | Conventional commit message format |
| [Branch Conventions](https://github.com/Mars-Platform/blueprint/blob/master/docs/branch-conventions.md) | Branch naming and workflow |
| [GitHub Conventions](https://github.com/Mars-Platform/blueprint/blob/master/docs/github-conventions.md) | Labels, issues, pull requests |
| [ADR Standards](https://github.com/Mars-Platform/blueprint/blob/master/docs/adr-standards.md) | Architecture Decision Record format |

## Quick Start

### Setup

```bash
# Clone the repository
git clone https://github.com/Mars-Platform/millwork-nodes.git
cd millwork-nodes

# Create a feature branch
git checkout -b feature/42-your-feature
```

### Development Workflow

1. **Check existing ADRs** in `docs/decisions/` before making architectural changes
2. **Write an ADR** if your change affects architecture (use [blueprint template](https://github.com/Mars-Platform/blueprint/blob/master/adr/template.md))
3. **Implement** following the project's patterns (see `CLAUDE.md`)
4. **Test** your changes in Blender
5. **Commit** using [conventional commits](https://github.com/Mars-Platform/blueprint/blob/master/docs/commit-conventions.md)
6. **Create PR** using the standard template

### Commit Examples

```bash
# Feature
git commit -m "feat(nodes): add MN_Divider geometry node group"

# Bug fix
git commit -m "fix(panels): correct corner-origin offset calculation"

# Documentation
git commit -m "docs(adr): add ADR-0008 for output format"
```

### Branch Naming

```
feature/42-add-divider-nodes
fix/57-panel-dimension-bug
docs/update-installation-guide
```

## Project-Specific Guidelines

### Blender Add-on Conventions

- **Node groups**: `MN_` prefix (e.g., `MN_Panel`, `MN_Divider`)
- **Operators**: `MN_OT_` prefix, `millwork_nodes.*` idname
- **Panels**: `MN_PT_` prefix
- **Properties**: Use Blender's property system for user-facing settings

### Architecture Principles

1. **The schema is the product** — Blender renders it, doesn't own it
2. **Document as source of truth** — Component Assembly Schema defines cabinets
3. **Two outputs** — Shop drawings AND parts/machining from same model

See `docs/PROJECT_NORTH_STAR.md` for full vision.

## Getting Help

- Check `CLAUDE.md` for AI assistant context
- Review ADRs in `docs/decisions/` for architectural decisions
- See `docs/ECOSYSTEM_ALIGNMENT.md` for relationship to other MARS projects
