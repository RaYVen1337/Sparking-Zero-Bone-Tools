import bpy

def create_collection(armature, name):
    """Create a new bone collection if it doesn't exist, and return it."""
    if name not in armature.data.collections:
        collection = armature.data.collections.new(name)
        # Hide all collections except "Uncategorized Bones" by default
        if name != "Uncategorized Bones":
            collection.is_visible = False
        return collection
    return armature.data.collections.get(name)


def assign_to_collection(bone, collection):
    """Assign a bone to a collection."""
    collection.assign(bone)


def extract_base_name(name):
    """Extract base name for jiggle bones."""
    # Remove common suffixes and JIGGLE part
    name = name.replace('_JIGGLE', '').replace('_ROOT', '')
    for suffix in ['_L', '_R', '_LW', '_RW', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
        name = name.replace(suffix, '')

    # Group similar items
    if 'SHIRT' in name:
        return 'SHIRT'
    if 'PANT' in name:
        return 'PANTS'
    if 'SKIRT' in name:
        return 'SKIRT'
    if 'HAIR' in name:
        return 'HAIR'
    if 'CAPE' in name:
        return 'CAPE'

    return name.strip('_')


def organize_bone_collections():
    """Clear, recreate, and reassign bone collections based on bone names."""
    armature = bpy.context.active_object
    if not (armature and armature.type == 'ARMATURE'):
        return

    # 1) Clear bone collection assignments so we can safely remove collections
    for bone in armature.data.bones:
        bone.collections.clear()

    # 2) Remove all existing collections
    existing_collections = list(armature.data.collections)
    for coll in existing_collections:
        armature.data.collections.remove(coll)

    # 3) Create primary collections
    uncategorized_collection = create_collection(armature, "Uncategorized Bones")
    aim_collection = create_collection(armature, "AIM Bones")
    socket_collection = create_collection(armature, "SOCKET Bones")
    effect_collection = create_collection(armature, "EFFECT Bones")
    ik_collection = create_collection(armature, "IK Bones")
    utility_collection = create_collection(armature, "UTILITY Bones")
    hair_collection = create_collection(armature, "HAIR Bones")
    acce_collection = create_collection(armature, "ACCE Bones")
    obi_collection = create_collection(armature, "OBI Bones")

    # Dictionaries to store jiggle bone groups and driver bone groups
    jiggle_groups = {}
    driver_groups = {}

    # 4) Process all bones
    for bone in armature.data.bones:
        name = bone.name.upper()

        # Handle JIGGLE bones
        if "JIGGLE" in name:
            base_name = extract_base_name(name)
            collection_name = f"{base_name} Jigglebones"
            if base_name not in jiggle_groups:
                jiggle_groups[base_name] = create_collection(armature, collection_name)
            assign_to_collection(bone, jiggle_groups[base_name])
            continue

        # Handle DRIVER bones
        if "DRIVER" in name:
            base_name = extract_base_name(name.replace('DRIVER', 'JIGGLE'))
            collection_name = f"{base_name} Drivers"
            if base_name not in driver_groups:
                driver_groups[base_name] = create_collection(armature, collection_name)
            assign_to_collection(bone, driver_groups[base_name])
            continue

        # Handle special named bones
        if "AIM" in name:
            assign_to_collection(bone, aim_collection)
        elif "SOCKET" in name:
            assign_to_collection(bone, socket_collection)
        elif "EFFECT" in name:
            assign_to_collection(bone, effect_collection)
        elif "IK" in name:  # 'IK' is already uppercase
            assign_to_collection(bone, ik_collection)
        elif "UTILITY" in name:
            assign_to_collection(bone, utility_collection)
        elif "HAIR" in name and "JIGGLE" not in name:
            assign_to_collection(bone, hair_collection)
        elif "ACCE" in name:
            assign_to_collection(bone, acce_collection)
        elif "OBI" in name:
            assign_to_collection(bone, obi_collection)
        else:
            # Assign to "Uncategorized Bones" if no special category
            assign_to_collection(bone, uncategorized_collection)


class AUTO_OT_organize_bone_collections(bpy.types.Operator):
    """Operator: Organize Bone Collections"""
    bl_idname = "armature.organize_bone_collections"
    bl_label = "Organize Bone Collections"
    bl_description = "Automatically organize bones into collections based on their names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        organize_bone_collections()
        return {'FINISHED'}


class VIEW3D_PT_bone_collections(bpy.types.Panel):
    """Panel: Bone Collections"""
    bl_label = "Bone Collections"
    bl_idname = "VIEW3D_PT_bone_collections"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        layout.operator(AUTO_OT_organize_bone_collections.bl_idname)


classes = (
    AUTO_OT_organize_bone_collections,
    VIEW3D_PT_bone_collections,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


# For running this file directly (not needed if using as an addon, but handy for testing):
if __name__ == "__main__":
    register()
