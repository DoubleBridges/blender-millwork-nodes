bl_info = {
    "name": "Millwork Nodes",
    "author": "Dave Kane",
    "version": (0, 1, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > Millwork Nodes",
    "description": "Native design-to-production system for custom millwork using geometry nodes",
    "category": "Object",
}

import bpy

from . import operators
from . import panels


def register():
    operators.register()
    panels.register()


def unregister():
    panels.unregister()
    operators.unregister()


if __name__ == "__main__":
    register()
