# ADR-0005: Library-Driven Workflow with Selection-Based UI

**Status**: Accepted  
**Date**: 2025-12-26  
**Authors**: Dave Kane  
**Relates to**: ADR-0003 (Document as Source of Truth), User experience

## Context

Geometry nodes in Blender are powerful but have UX challenges for production use:

- **Parameter surfacing**: Only top-level inputs show in the modifier panel
- **Deep nesting**: Accessing parameters of nested components requires navigating the node graph
- **Node graph complexity**: Even simple cabinets produce complex graphs
- **Learning curve**: Users must understand geometry nodes to modify cabinets

For a production tool, users need to:
- Work from templates most of the time
- Access key parameters without diving into node graphs
- Occasionally customize deeply (unusual cabinet configurations)

## Decision

### Library-Driven Workflow

Users work from a **library of cabinet templates**, not from scratch:

1. **Select template** from library (e.g., "24-inch Base Cabinet, Single Door")
2. **Adjust exposed parameters** in the sidebar panel (width, material, door style)
3. **Export** when done

Building cabinets from primitives is possible but not the typical workflow. Templates encode common configurations with sensible defaults.

### Selection-Based Property Panel

The UI shows properties for the **currently selected component**, not the whole cabinet:

- Click on cabinet exterior → show cabinet-level parameters (width, height, construction method)
- Click on a door → show door parameters (style, overlay, handle position)
- Click on drawer front → show drawer parameters (height, gap, handle)
- Click on interior space → show what's assigned to that space (shelves, dividers, etc.)

### Parallel Data Structure

The add-on maintains a **component tree** that mirrors the document structure:

```python
class CabinetTree:
    """Parallel data structure for UI navigation."""
    root: CarcassNode
    children: list[ComponentNode]  # Dividers, fills
    externals: list[ExternalNode]  # Doors, drawer fronts

class ComponentNode:
    id: str
    type: str  # 'divider', 'terminal_fill', 'external'
    parameters: dict
    children: list[ComponentNode]  # For dividers
    geometry_id: str  # Links to Blender geometry (for selection mapping)
```

This tree is the UI's navigation model. It's derived from the document but optimized for:
- Tree view display (collapsible outline in sidebar)
- Selection mapping (geometry → component)
- Parameter editing (component → modifier inputs)

### Component Identification via Attributes

Each geometry node group stamps an identifier attribute onto its output geometry:

```python
# In geometry node group
store_named_attribute(
    geometry=output,
    name="cabinet_component_id",
    value=component_id
)
```

When user selects geometry:
1. Read `cabinet_component_id` attribute from selected faces/vertices
2. Look up component in the tree
3. Display that component's parameters in the panel

## Rationale

### Why library-driven?

- **80/20 rule**: Most cabinets are variations of common types
- **Productivity**: Start with 90% done, customize the 10%
- **Consistency**: Templates enforce shop standards
- **Expertise capture**: Complex configurations become reusable

Users who need unusual cabinets can still build from primitives or modify templates deeply. But the common path is template → adjust → export.

### Why selection-based UI?

- **Focus**: See only relevant parameters for what you're working on
- **Discoverability**: Click to explore, no node graph navigation needed
- **Direct manipulation**: Select in viewport, edit in panel
- **Familiar pattern**: Matches how most 3D software works (select object, edit properties)

### Why a parallel data structure?

The geometry node graph is optimized for execution, not navigation. A parallel tree provides:

- **Fast lookups**: Component by ID without traversing node graph
- **UI-friendly structure**: Collapsible tree, breadcrumbs, history
- **Decoupled concerns**: Node graph can change without breaking UI
- **Document alignment**: Tree structure matches document structure

The cost is keeping them in sync, but the document-as-source-of-truth pattern (ADR-0003) already requires this.

### Alternatives Considered

**Rely only on node graph navigation**
- Pros: No parallel structure to maintain
- Cons: Requires geometry node expertise, poor production UX
- Rejected: Too high a barrier for typical users

**Surface all parameters to top level**
- Pros: Everything in modifier panel
- Cons: Overwhelming parameter lists, no organization
- Rejected: Doesn't scale beyond simple cabinets

**Custom viewport overlays for selection**
- Pros: Rich selection feedback
- Cons: Complex to implement, Blender-version fragile
- Rejected: Start simple, add later if needed

## Consequences

### Positive

- **Low barrier to entry**: Work from templates without deep knowledge
- **Focused editing**: See only what's relevant to current selection
- **Scalable complexity**: Simple use is simple, complex use is possible
- **Document-aligned**: UI tree and document tree stay consistent

### Negative

- **Sync overhead**: Tree must stay in sync with document and Blender
- **Attribute dependency**: Selection mapping requires attribute presence
- **Library curation**: Templates need to be built and maintained
- **Two mental models**: Users may confuse tree view vs node graph

### Mitigations

- Robust sync logic with clear ownership (document is source of truth)
- Validate attribute presence on export/load
- Start with essential templates, expand based on usage
- Clear documentation distinguishing template use from custom building

## Implementation Notes

### Tree View Panel

```python
class CN_PT_ComponentTree(Panel):
    bl_label = "Cabinet Structure"

    def draw(self, context):
        layout = self.layout
        tree = get_cabinet_tree(context.active_object)
        draw_tree_recursive(layout, tree.root, level=0)

def draw_tree_recursive(layout, node, level):
    row = layout.row()
    row.label(text="  " * level + node.name)
    if node.selected:
        row.active = True
    for child in node.children:
        draw_tree_recursive(layout, child, level + 1)
```

### Selection Mapping

```python
def on_selection_change(context):
    """Update panel when user selects different geometry."""
    obj = context.active_object
    if not is_cabinet_object(obj):
        return

    # Get component ID from selected geometry
    component_id = get_selected_component_id(obj)
    if component_id:
        # Update tree selection
        tree = get_cabinet_tree(obj)
        tree.select(component_id)
        # Refresh panel
        context.area.tag_redraw()
```

### Parameter Panel

```python
class CN_PT_ComponentParameters(Panel):
    bl_label = "Component Parameters"

    def draw(self, context):
        layout = self.layout
        tree = get_cabinet_tree(context.active_object)
        selected = tree.get_selected()

        if selected:
            layout.label(text=f"Type: {selected.type}")
            for param_name, param_value in selected.parameters.items():
                layout.prop(selected, param_name)
```

## Future Considerations

- **Breadcrumb navigation**: Show path to selected component (Cabinet > Left Cell > Drawer Stack)
- **Quick actions**: Right-click menu on tree nodes (duplicate, delete, swap type)
- **Search/filter**: Find components by name or type in large projects
- **Undo integration**: Tree changes participate in Blender undo stack

## References

- Blender's outliner: Example of tree-based object navigation
- CAD software: Property panels tied to selection
- Conduit: Similar pattern with product tree and property panels

---

*Accepted: 2025-12-26*
