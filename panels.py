"""
UI Panels for Cabinet Nodes add-on.
"""

import bpy
from bpy.types import Panel


class CN_PT_MainPanel(Panel):
    """Main panel for Cabinet Nodes in the 3D View sidebar"""
    bl_label = "Cabinet Nodes"
    bl_idname = "CN_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cabinet Nodes"
    
    def draw(self, context):
        layout = self.layout
        
        # Components section
        layout.label(text="Add Components:")
        col = layout.column(align=True)
        col.operator("cabinet_nodes.add_panel", icon='MESH_PLANE')
        
        layout.separator()
        
        # Node Groups section
        layout.label(text="Node Groups:")
        col = layout.column(align=True)
        col.operator("cabinet_nodes.create_panel_nodegroup", icon='NODETREE')


class CN_PT_ActiveObjectPanel(Panel):
    """Panel showing parameters for active cabinet object"""
    bl_label = "Active Panel"
    bl_idname = "CN_PT_active_object"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cabinet Nodes"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        """Only show when active object has a Cabinet Nodes modifier"""
        obj = context.active_object
        if obj is None:
            return False
        for mod in obj.modifiers:
            if mod.type == 'NODES' and mod.node_group:
                if mod.node_group.name.startswith("CN_"):
                    return True
        return False
    
    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        
        # Find the cabinet nodes modifier
        for mod in obj.modifiers:
            if mod.type == 'NODES' and mod.node_group:
                if mod.node_group.name.startswith("CN_"):
                    # Draw modifier inputs
                    layout.label(text=f"Modifier: {mod.name}")
                    
                    # Use the modifier's draw method for inputs
                    # This automatically handles the node group inputs
                    for item in mod.node_group.interface.items_tree:
                        if item.item_type == 'SOCKET' and item.in_out == 'INPUT':
                            layout.prop(mod, f'["{item.identifier}"]', text=item.name)
                    break


# Registration
classes = (
    CN_PT_MainPanel,
    CN_PT_ActiveObjectPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
