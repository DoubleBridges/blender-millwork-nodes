"""
Parametric Panel geometry node group builder.

Creates a panel (sheet good) with configurable dimensions.
The panel is created as a box centered at origin, with:
- Length along X axis
- Width along Y axis
- Thickness along Z axis

This orientation matches typical millwork conventions where panels
are modeled "laying flat" and then rotated into position.

TODO: Implement corner-origin positioning per ADR-0001
"""

import bpy


def create_panel_node_group(name: str = "MN_Panel") -> bpy.types.GeometryNodeTree:
    """
    Create a parametric panel geometry node group.
    
    Parameters are exposed as group inputs:
    - Length (X dimension)
    - Width (Y dimension)
    - Thickness (Z dimension)
    
    Returns the created node group.
    """
    # Create new geometry node tree
    node_tree = bpy.data.node_groups.new(name=name, type='GeometryNodeTree')
    
    # Create interface sockets (Blender 4.0+ API)
    # Inputs
    node_tree.interface.new_socket(
        name="Length",
        in_out='INPUT',
        socket_type='NodeSocketFloat'
    )
    node_tree.interface.new_socket(
        name="Width",
        in_out='INPUT',
        socket_type='NodeSocketFloat'
    )
    node_tree.interface.new_socket(
        name="Thickness",
        in_out='INPUT',
        socket_type='NodeSocketFloat'
    )
    
    # Output
    node_tree.interface.new_socket(
        name="Geometry",
        in_out='OUTPUT', 
        socket_type='NodeSocketGeometry'
    )
    
    # Set default values on the interface items
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
    
    # Create nodes
    nodes = node_tree.nodes
    
    # Group Input node
    input_node = nodes.new('NodeGroupInput')
    input_node.location = (-400, 0)
    
    # Group Output node
    output_node = nodes.new('NodeGroupOutput')
    output_node.location = (400, 0)
    
    # Mesh Box node - creates the panel geometry
    box_node = nodes.new('GeometryNodeMeshCube')
    box_node.location = (0, 0)
    box_node.label = "Panel Box"
    
    # Combine XYZ node - assembles dimensions into a vector for box size
    combine_xyz = nodes.new('ShaderNodeCombineXYZ')
    combine_xyz.location = (-200, -100)
    combine_xyz.label = "Dimensions"
    
    # Create links
    links = node_tree.links
    
    # Connect inputs to Combine XYZ
    links.new(input_node.outputs['Length'], combine_xyz.inputs['X'])
    links.new(input_node.outputs['Width'], combine_xyz.inputs['Y'])
    links.new(input_node.outputs['Thickness'], combine_xyz.inputs['Z'])
    
    # Connect Combine XYZ to Box size
    links.new(combine_xyz.outputs['Vector'], box_node.inputs['Size'])
    
    # Connect Box to output
    links.new(box_node.outputs['Mesh'], output_node.inputs['Geometry'])
    
    return node_tree


def get_or_create_panel_node_group(name: str = "MN_Panel") -> bpy.types.GeometryNodeTree:
    """
    Get existing panel node group or create a new one.
    
    Useful for ensuring we don't create duplicates.
    """
    if name in bpy.data.node_groups:
        return bpy.data.node_groups[name]
    return create_panel_node_group(name)
