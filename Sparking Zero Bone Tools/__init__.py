bl_info = {
    "name": "Sparking Zero Bone Tools",
    "author": "RaYVen",
    "version": (0, 1),
    "blender": (4, 3, 0),
    "location": "View3D > Tools > Bone Collections",
    "description": "Bone collection organization tools for Sparking Zero",
    "warning": "",
    "category": "Rigging",
}

import bpy
from . import bone_collection_organizer

def register():
    bone_collection_organizer.register()

def unregister():
    bone_collection_organizer.unregister()

if __name__ == "__main__":
    register()
