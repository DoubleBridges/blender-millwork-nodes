"""
Operators for Millwork Nodes add-on.
"""

import bpy
from bpy.types import Operator
from bpy.props import FloatProperty, IntProperty, EnumProperty, BoolProperty

from .node_groups import (
    get_or_create_panel_node_group,
    get_or_create_carcass_node_group,
    GRAIN_LENGTH,
    GRAIN_WIDTH,
)


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


class MN_OT_AddCarcass(Operator):
    """Add a parametric carcass (cabinet box) with geometry nodes"""
    bl_idname = "millwork_nodes.add_carcass"
    bl_label = "Add Carcass"
    bl_options = {'REGISTER', 'UNDO'}
    
    width: FloatProperty(
        name="Width",
        description="Carcass width (X dimension)",
        default=0.6096,  # 24 inches
        min=0.001,
        unit='LENGTH',
    )
    height: FloatProperty(
        name="Height",
        description="Carcass height (Z dimension)",
        default=0.762,  # 30 inches
        min=0.001,
        unit='LENGTH',
    )
    depth: FloatProperty(
        name="Depth",
        description="Carcass depth (Y dimension)",
        default=0.6096,  # 24 inches
        min=0.001,
        unit='LENGTH',
    )
    material_thickness: FloatProperty(
        name="Material Thickness",
        description="Thickness of sides, top, bottom",
        default=0.01905,  # 3/4 inch
        min=0.001,
        unit='LENGTH',
    )
    back_thickness: FloatProperty(
        name="Back Thickness",
        description="Thickness of back panel",
        default=0.00635,  # 1/4 inch
        min=0.001,
        unit='LENGTH',
    )
    back_inset: FloatProperty(
        name="Back Inset",
        description="Dado depth for back panel",
        default=0.009525,  # 3/8 inch
        min=0.0,
        unit='LENGTH',
    )
    nailer_width: FloatProperty(
        name="Nailer Width",
        description="Width of nailer strips",
        default=0.1016,  # 4 inches
        min=0.001,
        unit='LENGTH',
    )
    include_top: BoolProperty(
        name="Include Top",
        description="Include top panel",
        default=True,
    )
    include_bottom: BoolProperty(
        name="Include Bottom",
        description="Include bottom panel",
        default=True,
    )
    include_back: BoolProperty(
        name="Include Back",
        description="Include back panel",
        default=True,
    )
    
    def execute(self, context):
        # Create a new mesh object
        mesh = bpy.data.meshes.new("Carcass")
        obj = bpy.data.objects.new("Carcass", mesh)
        
        # Link to scene
        context.collection.objects.link(obj)
        
        # Select and make active
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj
        
        # Add geometry nodes modifier
        modifier = obj.modifiers.new(name="Millwork Nodes", type='NODES')
        
        # Get or create the carcass node group
        node_group = get_or_create_carcass_node_group()
        modifier.node_group = node_group
        
        # Set the input values from operator properties
        for item in node_group.interface.items_tree:
            if item.item_type == 'SOCKET' and item.in_out == 'INPUT':
                identifier = item.identifier
                if item.name == "Width":
                    modifier[identifier] = self.width
                elif item.name == "Height":
                    modifier[identifier] = self.height
                elif item.name == "Depth":
                    modifier[identifier] = self.depth
                elif item.name == "Material Thickness":
                    modifier[identifier] = self.material_thickness
                elif item.name == "Back Thickness":
                    modifier[identifier] = self.back_thickness
                elif item.name == "Back Inset":
                    modifier[identifier] = self.back_inset
                elif item.name == "Nailer Width":
                    modifier[identifier] = self.nailer_width
                elif item.name == "Include Top":
                    modifier[identifier] = self.include_top
                elif item.name == "Include Bottom":
                    modifier[identifier] = self.include_bottom
                elif item.name == "Include Back":
                    modifier[identifier] = self.include_back
        
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


class MN_OT_CreateCarcassNodeGroup(Operator):
    """Create the Carcass node group in the blend file"""
    bl_idname = "millwork_nodes.create_carcass_nodegroup"
    bl_label = "Create Carcass Node Group"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        node_group = get_or_create_carcass_node_group()
        self.report({'INFO'}, f"Node group '{node_group.name}' ready")
        return {'FINISHED'}


# Registration
classes = (
    MN_OT_AddPanel,
    MN_OT_AddCarcass,
    MN_OT_CreatePanelNodeGroup,
    MN_OT_CreateCarcassNodeGroup,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
