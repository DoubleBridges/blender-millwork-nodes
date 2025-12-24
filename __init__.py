bl_info = {
    "name": "Cabinet Nodes",
    "author": "Dave Kane",
    "version": (0, 1, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > Cabinet Nodes",
    "description": "Parametric geometry nodes for cabinet and sheet goods construction",
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
