"""
Operators for Millwork Nodes add-on.
"""

import bpy
from bpy.types import Operator
from bpy.props import FloatProperty, IntProperty, EnumProperty

from .node_groups import get_or_create_panel_node_group
from .node_groups.panel import GRAIN_LENGTH, GRAIN_WIDTH


class MN_OT_AddPanel(Operator):
    """Add a parametric panel object with geometry nodes"""
    bl_idname = "millwork_nodes.add_panel"
    bl_label = "Add Panel"
    bl_options = {'REGISTER', 'UNDO'}
    
    length: FloatProperty(
        name="Length",
        description="Panel length (X dimension)",
        default=0.6096,  # 24 inches
        min=0.001,
        unit='LENGTH',
    )
    width: FloatProperty(
        name="Width",
        description="Panel width (Y dimension)",
        default=0.3048,  # 12 inches
        min=0.001,
        unit='LENGTH',
    )
    thickness: FloatProperty(
        name="Thickness",
        description="Panel thickness (Z dimension)",
        default=0.01905,  # 3/4 inch
        min=0.001,
        unit='LENGTH',
    )
    grain_direction: EnumProperty(
        name="Grain Direction",
        description="Direction of material grain",
        items=[
            ('LENGTH', "Along Length", "Grain runs along the length (X axis)"),
            ('WIDTH', "Along Width", "Grain runs along the width (Y axis)"),
        ],
        default='LENGTH',
    )
    
    def execute(self, context):
        # Create a new mesh object
        mesh = bpy.data.meshes.new("Panel")
        obj = bpy.data.objects.new("Panel", mesh)
        
        # Link to scene
        context.collection.objects.link(obj)
        
        # Select and make active
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj
        
        # Add geometry nodes modifier
        modifier = obj.modifiers.new(name="Millwork Nodes", type='NODES')
        
        # Get or create the panel node group
        node_group = get_or_create_panel_node_group()
        modifier.node_group = node_group
        
        # Convert grain direction enum to integer
        grain_int = GRAIN_LENGTH if self.grain_direction == 'LENGTH' else GRAIN_WIDTH
        
        # Set the input values from operator properties
        # In Blender 4.0+, modifier inputs use identifier-based access
        for item in node_group.interface.items_tree:
            if item.item_type == 'SOCKET' and item.in_out == 'INPUT':
                identifier = item.identifier
                if item.name == "Length":
                    modifier[identifier] = self.length
                elif item.name == "Width":
                    modifier[identifier] = self.width
                elif item.name == "Thickness":
                    modifier[identifier] = self.thickness
                elif item.name == "Grain Direction":
                    modifier[identifier] = grain_int
        
        # Position at 3D cursor
        obj.location = context.scene.cursor.location.copy()
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class MN_OT_CreatePanelNodeGroup(Operator):
    """Create the Panel node group in the blend file"""
    bl_idname = "millwork_nodes.create_panel_nodegroup"
    bl_label = "Create Panel Node Group"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        node_group = get_or_create_panel_node_group()
        self.report({'INFO'}, f"Node group '{node_group.name}' ready")
        return {'FINISHED'}


# Registration
classes = (
    MN_OT_AddPanel,
    MN_OT_CreatePanelNodeGroup,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
