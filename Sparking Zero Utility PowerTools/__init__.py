bl_info = {
    "name": "Sparking Zero Utility PowerTools",
    "author": "RaYVen",
    "version": (0, 2),
    "blender": (4, 3, 0),
    "location": "View3D > Sidebar > SZUP",
    "description": "Bone collection organization and utility tools for Sparking Zero",
    "warning": "",
    "category": "Rigging",
    "support": "COMMUNITY",
    "wiki_url": "",
    "tracker_url": "",
}

import bpy
from . import bone_collection_organizer

def register():
    bone_collection_organizer.register()

def unregister():
    bone_collection_organizer.unregister()

if __name__ == "__main__":
    register()
