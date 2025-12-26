"""
UI Panels for Millwork Nodes add-on.
"""

import bpy
from bpy.types import Panel


class MN_PT_MainPanel(Panel):
    """Main panel for Millwork Nodes in the 3D View sidebar"""
    bl_label = "Millwork Nodes"
    bl_idname = "MN_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Millwork Nodes"
    
    def draw(self, context):
        layout = self.layout
        
        # Components section
        layout.label(text="Add Components:")
        col = layout.column(align=True)
        col.operator("millwork_nodes.add_panel", icon='MESH_PLANE')
        col.operator("millwork_nodes.add_carcass", icon='MESH_CUBE')
        
        layout.separator()
        
        # Node Groups section
        layout.label(text="Node Groups:")
        col = layout.column(align=True)
        col.operator("millwork_nodes.create_panel_nodegroup", icon='NODETREE')
        col.operator("millwork_nodes.create_carcass_nodegroup", icon='NODETREE')


class MN_PT_ActiveObjectPanel(Panel):
    """Panel showing parameters for active millwork object"""
    bl_label = "Active Component"
    bl_idname = "MN_PT_active_object"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Millwork Nodes"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        """Only show when active object has a Millwork Nodes modifier"""
        obj = context.active_object
        if obj is None:
            return False
        for mod in obj.modifiers:
            if mod.type == 'NODES' and mod.node_group:
                if mod.node_group.name.startswith("MN_"):
                    return True
        return False
    
    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        
        # Find the millwork nodes modifier
        for mod in obj.modifiers:
            if mod.type == 'NODES' and mod.node_group:
                if mod.node_group.name.startswith("MN_"):
                    # Show node group name
                    layout.label(text=f"Type: {mod.node_group.name}")
                    layout.separator()
                    
                    # Draw modifier inputs
                    for item in mod.node_group.interface.items_tree:
                        if item.item_type == 'SOCKET' and item.in_out == 'INPUT':
                            layout.prop(mod, f'["{item.identifier}"]', text=item.name)
                    break


# Registration
classes = (
    MN_PT_MainPanel,
    MN_PT_ActiveObjectPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
