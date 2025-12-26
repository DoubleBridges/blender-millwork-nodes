"""
Parametric Carcass geometry node group builder.

Creates a cabinet carcass (box) composed of MN_Panel instances:
- Left side, Right side
- Top, Bottom (between sides)
- Back (dadoed into sides, in front of nailers)
- Top nailer, Bottom nailer (at back, behind back panel)

Uses corner-origin positioning per ADR-0001:
- Carcass origin at back-bottom-left corner (0, 0, 0)
- X axis: left to right (width)
- Y axis: back to front (depth)
- Z axis: bottom to top (height)

Interior bounding box is output as separate sockets for child components.
"""

import bpy
import math

from .panel import get_or_create_panel_node_group, GRAIN_LENGTH, GRAIN_WIDTH


def create_carcass_node_group(name: str = "MN_Carcass") -> bpy.types.GeometryNodeTree:
    """
    Create a parametric carcass geometry node group.
    
    Inputs:
    - Width (exterior X dimension)
    - Height (exterior Z dimension)
    - Depth (exterior Y dimension)
    - Material Thickness (sides, top, bottom)
    - Back Thickness
    - Back Inset (dado depth into sides)
    - Nailer Width (height of nailer strips)
    - Include Top (boolean)
    - Include Bottom (boolean)
    - Include Back (boolean)
    
    Outputs:
    - Geometry (all panels joined with part_id attributes)
    - Interior Origin (Vector: where child components start)
    - Interior Width (Float)
    - Interior Height (Float)
    - Interior Depth (Float)
    
    Construction:
    - Top/bottom between sides
    - Back dadoed into sides only, in front of nailers
    - Nailers at back, top and bottom
    """
    # Ensure MN_Panel exists
    panel_group = get_or_create_panel_node_group()
    
    # Create new geometry node tree
    node_tree = bpy.data.node_groups.new(name=name, type='GeometryNodeTree')
    
    # ===== INTERFACE =====
    # Inputs
    node_tree.interface.new_socket(name="Width", in_out='INPUT', socket_type='NodeSocketFloat')
    node_tree.interface.new_socket(name="Height", in_out='INPUT', socket_type='NodeSocketFloat')
    node_tree.interface.new_socket(name="Depth", in_out='INPUT', socket_type='NodeSocketFloat')
    node_tree.interface.new_socket(name="Material Thickness", in_out='INPUT', socket_type='NodeSocketFloat')
    node_tree.interface.new_socket(name="Back Thickness", in_out='INPUT', socket_type='NodeSocketFloat')
    node_tree.interface.new_socket(name="Back Inset", in_out='INPUT', socket_type='NodeSocketFloat')
    node_tree.interface.new_socket(name="Nailer Width", in_out='INPUT', socket_type='NodeSocketFloat')
    node_tree.interface.new_socket(name="Include Top", in_out='INPUT', socket_type='NodeSocketBool')
    node_tree.interface.new_socket(name="Include Bottom", in_out='INPUT', socket_type='NodeSocketBool')
    node_tree.interface.new_socket(name="Include Back", in_out='INPUT', socket_type='NodeSocketBool')
    
    # Outputs
    node_tree.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    node_tree.interface.new_socket(name="Interior Origin", in_out='OUTPUT', socket_type='NodeSocketVector')
    node_tree.interface.new_socket(name="Interior Width", in_out='OUTPUT', socket_type='NodeSocketFloat')
    node_tree.interface.new_socket(name="Interior Height", in_out='OUTPUT', socket_type='NodeSocketFloat')
    node_tree.interface.new_socket(name="Interior Depth", in_out='OUTPUT', socket_type='NodeSocketFloat')
    
    # Set default values
    for item in node_tree.interface.items_tree:
        if item.name == "Width":
            item.default_value = 0.6096  # 24"
            item.min_value = 0.001
            item.subtype = 'DISTANCE'
        elif item.name == "Height":
            item.default_value = 0.762  # 30"
            item.min_value = 0.001
            item.subtype = 'DISTANCE'
        elif item.name == "Depth":
            item.default_value = 0.6096  # 24"
            item.min_value = 0.001
            item.subtype = 'DISTANCE'
        elif item.name == "Material Thickness":
            item.default_value = 0.01905  # 3/4"
            item.min_value = 0.001
            item.subtype = 'DISTANCE'
        elif item.name == "Back Thickness":
            item.default_value = 0.00635  # 1/4"
            item.min_value = 0.001
            item.subtype = 'DISTANCE'
        elif item.name == "Back Inset":
            item.default_value = 0.009525  # 3/8" dado depth
            item.min_value = 0.0
            item.subtype = 'DISTANCE'
        elif item.name == "Nailer Width":
            item.default_value = 0.1016  # 4"
            item.min_value = 0.001
            item.subtype = 'DISTANCE'
        elif item.name == "Include Top":
            item.default_value = True
        elif item.name == "Include Bottom":
            item.default_value = True
        elif item.name == "Include Back":
            item.default_value = True
    
    nodes = node_tree.nodes
    links = node_tree.links
    
    # ===== INPUT NODE =====
    input_node = nodes.new('NodeGroupInput')
    input_node.location = (-1800, 0)
    
    # ===== OUTPUT NODE =====
    output_node = nodes.new('NodeGroupOutput')
    output_node.location = (2000, 0)
    
    # ===== DIMENSION CALCULATIONS =====
    # We need various derived dimensions for part sizing and positioning
    
    # Side panel dimensions: Length=Height, Width=Depth, Thickness=MaterialThickness
    # (sides run full height and full depth)
    
    # Top/Bottom dimensions: Length=Width-2*MaterialThickness, Width=Depth, Thickness=MaterialThickness
    # (between sides, full depth)
    
    # Nailer dimensions: Length=Width-2*MaterialThickness, Width=NailerWidth, Thickness=MaterialThickness
    # (spans between sides)
    
    # Back dimensions: Length=Width-2*MaterialThickness+2*BackInset, Height=Height-2*MaterialThickness, Thickness=BackThickness
    # (dadoed into sides, between top and bottom)
    
    # --- Interior Width: Width - 2*MaterialThickness ---
    interior_width_calc = nodes.new('ShaderNodeMath')
    interior_width_calc.location = (-1400, 200)
    interior_width_calc.operation = 'MULTIPLY'
    interior_width_calc.inputs[1].default_value = 2.0
    interior_width_calc.label = "2 * MatThk"
    links.new(input_node.outputs['Material Thickness'], interior_width_calc.inputs[0])
    
    interior_width = nodes.new('ShaderNodeMath')
    interior_width.location = (-1200, 200)
    interior_width.operation = 'SUBTRACT'
    interior_width.label = "Interior Width"
    links.new(input_node.outputs['Width'], interior_width.inputs[0])
    links.new(interior_width_calc.outputs['Value'], interior_width.inputs[1])
    
    # --- Interior Height: Height - 2*MaterialThickness (when top and bottom present) ---
    interior_height = nodes.new('ShaderNodeMath')
    interior_height.location = (-1200, 0)
    interior_height.operation = 'SUBTRACT'
    interior_height.label = "Interior Height"
    links.new(input_node.outputs['Height'], interior_height.inputs[0])
    links.new(interior_width_calc.outputs['Value'], interior_height.inputs[1])
    
    # --- Interior Depth: Depth - BackThickness - NailerThickness (space in front of back) ---
    # Actually: Depth - (BackInset + BackThickness) for the usable interior
    back_total = nodes.new('ShaderNodeMath')
    back_total.location = (-1400, -200)
    back_total.operation = 'ADD'
    back_total.label = "Back + Inset"
    # Back sits at Y = nailer thickness, and has its own thickness
    # Interior depth = Depth - MaterialThickness (nailer) - BackThickness? 
    # Let me reconsider: The back is in a dado. The interior starts after the back.
    # Interior Depth = Depth - BackThickness (the back panel itself)
    
    interior_depth = nodes.new('ShaderNodeMath')
    interior_depth.location = (-1200, -200)
    interior_depth.operation = 'SUBTRACT'
    interior_depth.label = "Interior Depth"
    links.new(input_node.outputs['Depth'], interior_depth.inputs[0])
    links.new(input_node.outputs['Back Thickness'], interior_depth.inputs[1])
    
    # ===== PART CREATION =====
    # We'll create each part using Group nodes referencing MN_Panel
    
    y_offset = 400  # Vertical spacing in node editor
    
    # ----- LEFT SIDE -----
    left_side = nodes.new('GeometryNodeGroup')
    left_side.node_tree = panel_group
    left_side.location = (-800, y_offset * 2)
    left_side.label = "Left Side"
    # Length=Height, Width=Depth, Thickness=MaterialThickness, Grain=Length (vertical)
    links.new(input_node.outputs['Height'], left_side.inputs['Length'])
    links.new(input_node.outputs['Depth'], left_side.inputs['Width'])
    links.new(input_node.outputs['Material Thickness'], left_side.inputs['Thickness'])
    left_side.inputs['Grain Direction'].default_value = GRAIN_LENGTH
    
    # Transform left side: rotate to stand upright, position at X=0
    left_side_transform = nodes.new('GeometryNodeTransform')
    left_side_transform.location = (-600, y_offset * 2)
    left_side_transform.label = "Position Left Side"
    links.new(left_side.outputs['Geometry'], left_side_transform.inputs['Geometry'])
    # Rotation: panel created flat (Length=X, Width=Y, Thickness=Z)
    # Need to rotate so Length runs up Z, Width runs along Y, Thickness along X
    # Rotate -90° around Y axis
    left_side_transform.inputs['Rotation'].default_value = (math.radians(90), 0, math.radians(-90))
    # Position: origin at back-bottom-left, which is already (0,0,0) after rotation
    left_side_transform.inputs['Translation'].default_value = (0, 0, 0)
    
    # Store part_id attribute on left side
    left_side_id = nodes.new('GeometryNodeStoreNamedAttribute')
    left_side_id.location = (-400, y_offset * 2)
    left_side_id.label = "ID: left_side"
    left_side_id.data_type = 'INT'
    left_side_id.domain = 'FACE'
    left_side_id.inputs['Name'].default_value = "part_id"
    left_side_id.inputs['Value'].default_value = 1  # 1 = left_side
    links.new(left_side_transform.outputs['Geometry'], left_side_id.inputs['Geometry'])
    
    # ----- RIGHT SIDE -----
    right_side = nodes.new('GeometryNodeGroup')
    right_side.node_tree = panel_group
    right_side.location = (-800, y_offset)
    right_side.label = "Right Side"
    links.new(input_node.outputs['Height'], right_side.inputs['Length'])
    links.new(input_node.outputs['Depth'], right_side.inputs['Width'])
    links.new(input_node.outputs['Material Thickness'], right_side.inputs['Thickness'])
    right_side.inputs['Grain Direction'].default_value = GRAIN_LENGTH
    
    # Position right side: same rotation, but translated to X = Width - MaterialThickness
    right_side_transform = nodes.new('GeometryNodeTransform')
    right_side_transform.location = (-600, y_offset)
    right_side_transform.label = "Position Right Side"
    links.new(right_side.outputs['Geometry'], right_side_transform.inputs['Geometry'])
    right_side_transform.inputs['Rotation'].default_value = (math.radians(90), 0, math.radians(-90))
    
    # Calculate right side X position: Width - MaterialThickness
    right_side_x = nodes.new('ShaderNodeMath')
    right_side_x.location = (-800, y_offset - 150)
    right_side_x.operation = 'SUBTRACT'
    right_side_x.label = "Right Side X"
    links.new(input_node.outputs['Width'], right_side_x.inputs[0])
    links.new(input_node.outputs['Material Thickness'], right_side_x.inputs[1])
    
    right_side_pos = nodes.new('ShaderNodeCombineXYZ')
    right_side_pos.location = (-600, y_offset - 150)
    right_side_pos.label = "Right Side Pos"
    links.new(right_side_x.outputs['Value'], right_side_pos.inputs['X'])
    links.new(right_side_transform.inputs['Translation'], right_side_pos.outputs['Vector'])
    
    right_side_id = nodes.new('GeometryNodeStoreNamedAttribute')
    right_side_id.location = (-400, y_offset)
    right_side_id.label = "ID: right_side"
    right_side_id.data_type = 'INT'
    right_side_id.domain = 'FACE'
    right_side_id.inputs['Name'].default_value = "part_id"
    right_side_id.inputs['Value'].default_value = 2  # 2 = right_side
    links.new(right_side_transform.outputs['Geometry'], right_side_id.inputs['Geometry'])
    
    # ----- BOTTOM -----
    bottom = nodes.new('GeometryNodeGroup')
    bottom.node_tree = panel_group
    bottom.location = (-800, 0)
    bottom.label = "Bottom"
    # Length = interior width, Width = Depth, Thickness = MaterialThickness
    links.new(interior_width.outputs['Value'], bottom.inputs['Length'])
    links.new(input_node.outputs['Depth'], bottom.inputs['Width'])
    links.new(input_node.outputs['Material Thickness'], bottom.inputs['Thickness'])
    bottom.inputs['Grain Direction'].default_value = GRAIN_WIDTH  # Grain runs front to back
    
    # Position bottom: X = MaterialThickness, Y = 0, Z = 0
    # Rotation: lies flat, but rotated so Length runs along X
    bottom_transform = nodes.new('GeometryNodeTransform')
    bottom_transform.location = (-600, 0)
    bottom_transform.label = "Position Bottom"
    links.new(bottom.outputs['Geometry'], bottom_transform.inputs['Geometry'])
    # Panel is already flat with Length on X - need to rotate so Length goes X, Width goes Y
    # Actually panel Length is on X, Width on Y - just need to swap for our orientation
    bottom_transform.inputs['Rotation'].default_value = (0, 0, 0)
    
    bottom_pos = nodes.new('ShaderNodeCombineXYZ')
    bottom_pos.location = (-600, -150)
    bottom_pos.label = "Bottom Pos"
    links.new(input_node.outputs['Material Thickness'], bottom_pos.inputs['X'])
    # Y = 0, Z = 0 (default)
    links.new(bottom_pos.outputs['Vector'], bottom_transform.inputs['Translation'])
    
    bottom_id = nodes.new('GeometryNodeStoreNamedAttribute')
    bottom_id.location = (-400, 0)
    bottom_id.label = "ID: bottom"
    bottom_id.data_type = 'INT'
    bottom_id.domain = 'FACE'
    bottom_id.inputs['Name'].default_value = "part_id"
    bottom_id.inputs['Value'].default_value = 3  # 3 = bottom
    links.new(bottom_transform.outputs['Geometry'], bottom_id.inputs['Geometry'])
    
    # ----- TOP -----
    top = nodes.new('GeometryNodeGroup')
    top.node_tree = panel_group
    top.location = (-800, -y_offset)
    top.label = "Top"
    links.new(interior_width.outputs['Value'], top.inputs['Length'])
    links.new(input_node.outputs['Depth'], top.inputs['Width'])
    links.new(input_node.outputs['Material Thickness'], top.inputs['Thickness'])
    top.inputs['Grain Direction'].default_value = GRAIN_WIDTH
    
    # Position top: X = MaterialThickness, Y = 0, Z = Height - MaterialThickness
    top_transform = nodes.new('GeometryNodeTransform')
    top_transform.location = (-600, -y_offset)
    top_transform.label = "Position Top"
    links.new(top.outputs['Geometry'], top_transform.inputs['Geometry'])
    top_transform.inputs['Rotation'].default_value = (0, 0, 0)
    
    top_z = nodes.new('ShaderNodeMath')
    top_z.location = (-800, -y_offset - 150)
    top_z.operation = 'SUBTRACT'
    top_z.label = "Top Z"
    links.new(input_node.outputs['Height'], top_z.inputs[0])
    links.new(input_node.outputs['Material Thickness'], top_z.inputs[1])
    
    top_pos = nodes.new('ShaderNodeCombineXYZ')
    top_pos.location = (-600, -y_offset - 150)
    top_pos.label = "Top Pos"
    links.new(input_node.outputs['Material Thickness'], top_pos.inputs['X'])
    links.new(top_z.outputs['Value'], top_pos.inputs['Z'])
    links.new(top_pos.outputs['Vector'], top_transform.inputs['Translation'])
    
    top_id = nodes.new('GeometryNodeStoreNamedAttribute')
    top_id.location = (-400, -y_offset)
    top_id.label = "ID: top"
    top_id.data_type = 'INT'
    top_id.domain = 'FACE'
    top_id.inputs['Name'].default_value = "part_id"
    top_id.inputs['Value'].default_value = 4  # 4 = top
    links.new(top_transform.outputs['Geometry'], top_id.inputs['Geometry'])
    
    # ----- BOTTOM NAILER -----
    bottom_nailer = nodes.new('GeometryNodeGroup')
    bottom_nailer.node_tree = panel_group
    bottom_nailer.location = (-800, -y_offset * 2)
    bottom_nailer.label = "Bottom Nailer"
    # Length = interior width, Width = NailerWidth, Thickness = MaterialThickness
    links.new(interior_width.outputs['Value'], bottom_nailer.inputs['Length'])
    links.new(input_node.outputs['Nailer Width'], bottom_nailer.inputs['Width'])
    links.new(input_node.outputs['Material Thickness'], bottom_nailer.inputs['Thickness'])
    bottom_nailer.inputs['Grain Direction'].default_value = GRAIN_LENGTH
    
    # Position: X = MaterialThickness, Y = 0, Z = MaterialThickness
    # Rotation: (90, 0, 90) to stand it up at the back
    # Let's think about this: nailer panel is created flat.
    # Length on X, Width on Y, Thickness on Z.
    # We want Length to run along X (width of cabinet) - OK
    # We want Width to run along Z (vertical) 
    # We want Thickness to run along Y (front-to-back)
    # So rotate 90° around X axis
    bottom_nailer_transform = nodes.new('GeometryNodeTransform')
    bottom_nailer_transform.location = (-600, -y_offset * 2)
    bottom_nailer_transform.label = "Position Bottom Nailer"
    links.new(bottom_nailer.outputs['Geometry'], bottom_nailer_transform.inputs['Geometry'])
    bottom_nailer_transform.inputs['Rotation'].default_value = (math.radians(90), 0, 0)
    
    bottom_nailer_pos = nodes.new('ShaderNodeCombineXYZ')
    bottom_nailer_pos.location = (-600, -y_offset * 2 - 150)
    bottom_nailer_pos.label = "Bottom Nailer Pos"
    links.new(input_node.outputs['Material Thickness'], bottom_nailer_pos.inputs['X'])
    # Y = 0
    links.new(input_node.outputs['Material Thickness'], bottom_nailer_pos.inputs['Z'])
    links.new(bottom_nailer_pos.outputs['Vector'], bottom_nailer_transform.inputs['Translation'])
    
    bottom_nailer_id = nodes.new('GeometryNodeStoreNamedAttribute')
    bottom_nailer_id.location = (-400, -y_offset * 2)
    bottom_nailer_id.label = "ID: bottom_nailer"
    bottom_nailer_id.data_type = 'INT'
    bottom_nailer_id.domain = 'FACE'
    bottom_nailer_id.inputs['Name'].default_value = "part_id"
    bottom_nailer_id.inputs['Value'].default_value = 5  # 5 = bottom_nailer
    links.new(bottom_nailer_transform.outputs['Geometry'], bottom_nailer_id.inputs['Geometry'])
    
    # ----- TOP NAILER -----
    top_nailer = nodes.new('GeometryNodeGroup')
    top_nailer.node_tree = panel_group
    top_nailer.location = (-800, -y_offset * 3)
    top_nailer.label = "Top Nailer"
    links.new(interior_width.outputs['Value'], top_nailer.inputs['Length'])
    links.new(input_node.outputs['Nailer Width'], top_nailer.inputs['Width'])
    links.new(input_node.outputs['Material Thickness'], top_nailer.inputs['Thickness'])
    top_nailer.inputs['Grain Direction'].default_value = GRAIN_LENGTH
    
    # Position: X = MaterialThickness, Y = 0, Z = Height - MaterialThickness - NailerWidth
    # (top of nailer touches bottom of top panel)
    top_nailer_transform = nodes.new('GeometryNodeTransform')
    top_nailer_transform.location = (-600, -y_offset * 3)
    top_nailer_transform.label = "Position Top Nailer"
    links.new(top_nailer.outputs['Geometry'], top_nailer_transform.inputs['Geometry'])
    top_nailer_transform.inputs['Rotation'].default_value = (math.radians(90), 0, 0)
    
    # Z = Height - MaterialThickness - NailerWidth
    top_nailer_z_step1 = nodes.new('ShaderNodeMath')
    top_nailer_z_step1.location = (-1000, -y_offset * 3 - 150)
    top_nailer_z_step1.operation = 'SUBTRACT'
    top_nailer_z_step1.label = "H - MatThk"
    links.new(input_node.outputs['Height'], top_nailer_z_step1.inputs[0])
    links.new(input_node.outputs['Material Thickness'], top_nailer_z_step1.inputs[1])
    
    top_nailer_z = nodes.new('ShaderNodeMath')
    top_nailer_z.location = (-800, -y_offset * 3 - 150)
    top_nailer_z.operation = 'SUBTRACT'
    top_nailer_z.label = "Top Nailer Z"
    links.new(top_nailer_z_step1.outputs['Value'], top_nailer_z.inputs[0])
    links.new(input_node.outputs['Nailer Width'], top_nailer_z.inputs[1])
    
    top_nailer_pos = nodes.new('ShaderNodeCombineXYZ')
    top_nailer_pos.location = (-600, -y_offset * 3 - 150)
    top_nailer_pos.label = "Top Nailer Pos"
    links.new(input_node.outputs['Material Thickness'], top_nailer_pos.inputs['X'])
    links.new(top_nailer_z.outputs['Value'], top_nailer_pos.inputs['Z'])
    links.new(top_nailer_pos.outputs['Vector'], top_nailer_transform.inputs['Translation'])
    
    top_nailer_id = nodes.new('GeometryNodeStoreNamedAttribute')
    top_nailer_id.location = (-400, -y_offset * 3)
    top_nailer_id.label = "ID: top_nailer"
    top_nailer_id.data_type = 'INT'
    top_nailer_id.domain = 'FACE'
    top_nailer_id.inputs['Name'].default_value = "part_id"
    top_nailer_id.inputs['Value'].default_value = 6  # 6 = top_nailer
    links.new(top_nailer_transform.outputs['Geometry'], top_nailer_id.inputs['Geometry'])
    
    # ----- BACK -----
    back = nodes.new('GeometryNodeGroup')
    back.node_tree = panel_group
    back.location = (-800, -y_offset * 4)
    back.label = "Back"
    # Back is dadoed into sides, so it extends into the dado on each side
    # Length = interior_width + 2 * back_inset
    # Height = interior_height (between top and bottom)
    # Thickness = back_thickness
    
    back_inset_double = nodes.new('ShaderNodeMath')
    back_inset_double.location = (-1200, -y_offset * 4)
    back_inset_double.operation = 'MULTIPLY'
    back_inset_double.inputs[1].default_value = 2.0
    back_inset_double.label = "2 * BackInset"
    links.new(input_node.outputs['Back Inset'], back_inset_double.inputs[0])
    
    back_length = nodes.new('ShaderNodeMath')
    back_length.location = (-1000, -y_offset * 4)
    back_length.operation = 'ADD'
    back_length.label = "Back Length"
    links.new(interior_width.outputs['Value'], back_length.inputs[0])
    links.new(back_inset_double.outputs['Value'], back_length.inputs[1])
    
    links.new(back_length.outputs['Value'], back.inputs['Length'])
    links.new(interior_height.outputs['Value'], back.inputs['Width'])
    links.new(input_node.outputs['Back Thickness'], back.inputs['Thickness'])
    back.inputs['Grain Direction'].default_value = GRAIN_WIDTH  # Grain vertical
    
    # Position back: 
    # X = MaterialThickness - BackInset (dadoed into left side)
    # Y = MaterialThickness (in front of nailers - nailers are MaterialThickness deep)
    # Z = MaterialThickness (above bottom)
    # Rotation: stand up so Width (now height) runs along Z
    back_transform = nodes.new('GeometryNodeTransform')
    back_transform.location = (-600, -y_offset * 4)
    back_transform.label = "Position Back"
    links.new(back.outputs['Geometry'], back_transform.inputs['Geometry'])
    # Rotate 90° around X to stand it up
    back_transform.inputs['Rotation'].default_value = (math.radians(90), 0, 0)
    
    back_x = nodes.new('ShaderNodeMath')
    back_x.location = (-800, -y_offset * 4 - 150)
    back_x.operation = 'SUBTRACT'
    back_x.label = "Back X"
    links.new(input_node.outputs['Material Thickness'], back_x.inputs[0])
    links.new(input_node.outputs['Back Inset'], back_x.inputs[1])
    
    back_pos = nodes.new('ShaderNodeCombineXYZ')
    back_pos.location = (-600, -y_offset * 4 - 150)
    back_pos.label = "Back Pos"
    links.new(back_x.outputs['Value'], back_pos.inputs['X'])
    links.new(input_node.outputs['Material Thickness'], back_pos.inputs['Y'])  # In front of nailers
    links.new(input_node.outputs['Material Thickness'], back_pos.inputs['Z'])
    links.new(back_pos.outputs['Vector'], back_transform.inputs['Translation'])
    
    back_id = nodes.new('GeometryNodeStoreNamedAttribute')
    back_id.location = (-400, -y_offset * 4)
    back_id.label = "ID: back"
    back_id.data_type = 'INT'
    back_id.domain = 'FACE'
    back_id.inputs['Name'].default_value = "part_id"
    back_id.inputs['Value'].default_value = 7  # 7 = back
    links.new(back_transform.outputs['Geometry'], back_id.inputs['Geometry'])
    
    # ===== JOIN GEOMETRY =====
    # Join all parts together
    # We'll use a series of Join Geometry nodes
    
    join1 = nodes.new('GeometryNodeJoinGeometry')
    join1.location = (0, y_offset)
    join1.label = "Join Sides"
    links.new(left_side_id.outputs['Geometry'], join1.inputs['Geometry'])
    links.new(right_side_id.outputs['Geometry'], join1.inputs['Geometry'])
    
    join2 = nodes.new('GeometryNodeJoinGeometry')
    join2.location = (200, y_offset)
    join2.label = "Join Top/Bottom"
    links.new(join1.outputs['Geometry'], join2.inputs['Geometry'])
    links.new(bottom_id.outputs['Geometry'], join2.inputs['Geometry'])
    links.new(top_id.outputs['Geometry'], join2.inputs['Geometry'])
    
    join3 = nodes.new('GeometryNodeJoinGeometry')
    join3.location = (400, y_offset)
    join3.label = "Join Nailers"
    links.new(join2.outputs['Geometry'], join3.inputs['Geometry'])
    links.new(bottom_nailer_id.outputs['Geometry'], join3.inputs['Geometry'])
    links.new(top_nailer_id.outputs['Geometry'], join3.inputs['Geometry'])
    
    join4 = nodes.new('GeometryNodeJoinGeometry')
    join4.location = (600, y_offset)
    join4.label = "Join Back"
    links.new(join3.outputs['Geometry'], join4.inputs['Geometry'])
    links.new(back_id.outputs['Geometry'], join4.inputs['Geometry'])
    
    # Connect geometry to output
    links.new(join4.outputs['Geometry'], output_node.inputs['Geometry'])
    
    # ===== INTERIOR BBOX OUTPUTS =====
    # Interior origin: X = MaterialThickness, Y = BackThickness + MaterialThickness, Z = MaterialThickness
    interior_origin_y = nodes.new('ShaderNodeMath')
    interior_origin_y.location = (800, -200)
    interior_origin_y.operation = 'ADD'
    interior_origin_y.label = "Interior Y"
    links.new(input_node.outputs['Back Thickness'], interior_origin_y.inputs[0])
    links.new(input_node.outputs['Material Thickness'], interior_origin_y.inputs[1])
    
    interior_origin = nodes.new('ShaderNodeCombineXYZ')
    interior_origin.location = (1000, -200)
    interior_origin.label = "Interior Origin"
    links.new(input_node.outputs['Material Thickness'], interior_origin.inputs['X'])
    links.new(interior_origin_y.outputs['Value'], interior_origin.inputs['Y'])
    links.new(input_node.outputs['Material Thickness'], interior_origin.inputs['Z'])
    
    links.new(interior_origin.outputs['Vector'], output_node.inputs['Interior Origin'])
    links.new(interior_width.outputs['Value'], output_node.inputs['Interior Width'])
    links.new(interior_height.outputs['Value'], output_node.inputs['Interior Height'])
    
    # Interior depth = Depth - BackThickness - MaterialThickness (nailer depth)
    interior_depth_calc = nodes.new('ShaderNodeMath')
    interior_depth_calc.location = (800, -400)
    interior_depth_calc.operation = 'SUBTRACT'
    interior_depth_calc.label = "Depth - Back"
    links.new(input_node.outputs['Depth'], interior_depth_calc.inputs[0])
    links.new(interior_origin_y.outputs['Value'], interior_depth_calc.inputs[1])
    
    links.new(interior_depth_calc.outputs['Value'], output_node.inputs['Interior Depth'])
    
    return node_tree


def get_or_create_carcass_node_group(name: str = "MN_Carcass") -> bpy.types.GeometryNodeTree:
    """
    Get existing carcass node group or create a new one.
    """
    if name in bpy.data.node_groups:
        return bpy.data.node_groups[name]
    return create_carcass_node_group(name)
