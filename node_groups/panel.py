"""
Parametric Panel geometry node group builder.

Creates a panel (sheet good) with configurable dimensions.
The panel uses corner-origin positioning per ADR-0001:
- Origin at back-bottom-left corner (0, 0, 0)
- X axis: left to right (length)
- Y axis: back to front (width)
- Z axis: bottom to top (thickness)

Grain direction is stored as an attribute for manufacturing export.
"""

import bpy


# Grain direction constants
GRAIN_LENGTH = 0  # Grain runs along X (length)
GRAIN_WIDTH = 1   # Grain runs along Y (width)


def create_panel_node_group(name: str = "MN_Panel") -> bpy.types.GeometryNodeTree:
    """
    Create a parametric panel geometry node group.
    
    Parameters are exposed as group inputs:
    - Length (X dimension)
    - Width (Y dimension)
    - Thickness (Z dimension)
    - Grain Direction (0=length, 1=width)
    
    The panel origin is at back-bottom-left corner.
    Grain direction is stored as a 'grain_direction' attribute on the geometry.
    
    Returns the created node group.
    """
    # Create new geometry node tree
    node_tree = bpy.data.node_groups.new(name=name, type='GeometryNodeTree')
    
    # Create interface sockets (Blender 4.0+ API)
    # Inputs
    length_socket = node_tree.interface.new_socket(
        name="Length",
        in_out='INPUT',
        socket_type='NodeSocketFloat'
    )
    width_socket = node_tree.interface.new_socket(
        name="Width",
        in_out='INPUT',
        socket_type='NodeSocketFloat'
    )
    thickness_socket = node_tree.interface.new_socket(
        name="Thickness",
        in_out='INPUT',
        socket_type='NodeSocketFloat'
    )
    grain_socket = node_tree.interface.new_socket(
        name="Grain Direction",
        in_out='INPUT',
        socket_type='NodeSocketInt'
    )
    
    # Output
    node_tree.interface.new_socket(
        name="Geometry",
        in_out='OUTPUT', 
        socket_type='NodeSocketGeometry'
    )
    
    # Set default values and constraints on the interface items
    for item in node_tree.interface.items_tree:
        if item.name == "Length":
            item.default_value = 0.6096  # 24 inches in meters
            item.min_value = 0.001
            item.subtype = 'DISTANCE'
        elif item.name == "Width":
            item.default_value = 0.3048  # 12 inches in meters
            item.min_value = 0.001
            item.subtype = 'DISTANCE'
        elif item.name == "Thickness":
            item.default_value = 0.01905  # 3/4 inch in meters
            item.min_value = 0.001
            item.subtype = 'DISTANCE'
        elif item.name == "Grain Direction":
            item.default_value = GRAIN_LENGTH  # Default grain along length
            item.min_value = 0
            item.max_value = 1
    
    # Create nodes
    nodes = node_tree.nodes
    links = node_tree.links
    
    # ===== INPUT =====
    input_node = nodes.new('NodeGroupInput')
    input_node.location = (-600, 0)
    
    # ===== OUTPUT =====
    output_node = nodes.new('NodeGroupOutput')
    output_node.location = (600, 0)
    
    # ===== GEOMETRY CREATION =====
    
    # Mesh Cube - creates the panel geometry (centered at origin initially)
    box_node = nodes.new('GeometryNodeMeshCube')
    box_node.location = (-200, 100)
    box_node.label = "Panel Box"
    
    # Combine XYZ - assembles dimensions into a vector for box size
    combine_size = nodes.new('ShaderNodeCombineXYZ')
    combine_size.location = (-400, 0)
    combine_size.label = "Size Vector"
    
    # Connect dimensions to size vector
    links.new(input_node.outputs['Length'], combine_size.inputs['X'])
    links.new(input_node.outputs['Width'], combine_size.inputs['Y'])
    links.new(input_node.outputs['Thickness'], combine_size.inputs['Z'])
    
    # Connect size to box
    links.new(combine_size.outputs['Vector'], box_node.inputs['Size'])
    
    # ===== CORNER ORIGIN TRANSLATION =====
    # Move geometry so back-bottom-left corner is at (0,0,0)
    # Box is centered, so we translate by +half dimensions
    
    # Math nodes to calculate half dimensions
    half_length = nodes.new('ShaderNodeMath')
    half_length.location = (-400, -150)
    half_length.operation = 'MULTIPLY'
    half_length.inputs[1].default_value = 0.5
    half_length.label = "Length/2"
    links.new(input_node.outputs['Length'], half_length.inputs[0])
    
    half_width = nodes.new('ShaderNodeMath')
    half_width.location = (-400, -300)
    half_width.operation = 'MULTIPLY'
    half_width.inputs[1].default_value = 0.5
    half_width.label = "Width/2"
    links.new(input_node.outputs['Width'], half_width.inputs[0])
    
    half_thickness = nodes.new('ShaderNodeMath')
    half_thickness.location = (-400, -450)
    half_thickness.operation = 'MULTIPLY'
    half_thickness.inputs[1].default_value = 0.5
    half_thickness.label = "Thickness/2"
    links.new(input_node.outputs['Thickness'], half_thickness.inputs[0])
    
    # Combine into translation vector
    combine_offset = nodes.new('ShaderNodeCombineXYZ')
    combine_offset.location = (-200, -300)
    combine_offset.label = "Origin Offset"
    links.new(half_length.outputs['Value'], combine_offset.inputs['X'])
    links.new(half_width.outputs['Value'], combine_offset.inputs['Y'])
    links.new(half_thickness.outputs['Value'], combine_offset.inputs['Z'])
    
    # Transform Geometry - apply the translation
    transform_node = nodes.new('GeometryNodeTransform')
    transform_node.location = (0, 100)
    transform_node.label = "Corner Origin"
    links.new(box_node.outputs['Mesh'], transform_node.inputs['Geometry'])
    links.new(combine_offset.outputs['Vector'], transform_node.inputs['Translation'])
    
    # ===== GRAIN DIRECTION ATTRIBUTE =====
    # Store grain direction as an integer attribute on the geometry
    # This travels with the geometry for export/manufacturing
    
    store_grain = nodes.new('GeometryNodeStoreNamedAttribute')
    store_grain.location = (200, 100)
    store_grain.label = "Store Grain Direction"
    store_grain.data_type = 'INT'
    store_grain.domain = 'FACE'  # Store on faces
    store_grain.inputs['Name'].default_value = "grain_direction"
    
    links.new(transform_node.outputs['Geometry'], store_grain.inputs['Geometry'])
    links.new(input_node.outputs['Grain Direction'], store_grain.inputs['Value'])
    
    # ===== STORE DIMENSIONS AS ATTRIBUTES =====
    # Useful for downstream nodes that need to know panel size
    
    store_length = nodes.new('GeometryNodeStoreNamedAttribute')
    store_length.location = (400, 100)
    store_length.label = "Store Length"
    store_length.data_type = 'FLOAT'
    store_length.domain = 'FACE'
    store_length.inputs['Name'].default_value = "panel_length"
    
    links.new(store_grain.outputs['Geometry'], store_length.inputs['Geometry'])
    links.new(input_node.outputs['Length'], store_length.inputs['Value'])
    
    # Connect final geometry to output
    links.new(store_length.outputs['Geometry'], output_node.inputs['Geometry'])
    
    return node_tree


def get_or_create_panel_node_group(name: str = "MN_Panel") -> bpy.types.GeometryNodeTree:
    """
    Get existing panel node group or create a new one.
    
    Useful for ensuring we don't create duplicates.
    """
    if name in bpy.data.node_groups:
        return bpy.data.node_groups[name]
    return create_panel_node_group(name)
