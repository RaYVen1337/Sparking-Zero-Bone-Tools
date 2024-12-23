import bpy

# --- Bone Collection Organizer Functions ---

def create_collection(armature, name):
    """Create a new bone collection if it doesn't exist, and return it."""
    if name not in armature.data.collections:
        collection = armature.data.collections.new(name)
        # Hide all collections except "Main Bones" by default
        if name != "Main Bones":
            collection.hide_viewport = True
        return collection
    return armature.data.collections.get(name)


def assign_to_collection(bone, collection):
    """Assign a bone to a collection."""
    collection.objects.link(bone.id_data)  # Ensure the armature is linked
    bone.collections.link(collection)


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
        bpy.ops.object.message_box('INVOKE_DEFAULT', message="Please select an armature.")
        return

    # 1) Clear bone collection assignments so we can safely remove collections
    for bone in armature.data.bones:
        bone.collections.clear()

    # 2) Remove all existing collections
    existing_collections = list(armature.data.collections)
    for coll in existing_collections:
        armature.data.collections.remove(coll)

    # 3) Create primary collections
    main_collection = create_collection(armature, "Main Bones")
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
            # Assign to "Main Bones" if no special category
            assign_to_collection(bone, main_collection)


# --- Armature Toggle Operator ---

class TOGGLE_ARMATURE_POS(bpy.types.Operator):
    """Toggle Armature Between Pose and Rest Position"""
    bl_idname = "armature.toggle_armature_pos"
    bl_label = "Toggle Pose/Rest"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        armature = None

        # Determine the relevant armature
        active_obj = context.active_object

        if active_obj:
            if active_obj.type == 'ARMATURE':
                armature = active_obj
            else:
                parent = active_obj.parent
                if parent and parent.type == 'ARMATURE':
                    armature = parent

        # If armature is still not found, check selected objects
        if armature is None:
            for obj in context.selected_objects:
                if obj.type == 'ARMATURE':
                    armature = obj
                    break

        if armature is None:
            self.report({'WARNING'}, "No Armature found for toggling.")
            return {'CANCELLED'}

        # Toggle the pose_position enum
        current_pos = armature.data.pose_position
        if current_pos == 'POSE':
            armature.data.pose_position = 'REST'
            mode = "Rest Position"
        else:
            armature.data.pose_position = 'POSE'
            mode = "Pose Position"

        self.report({'INFO'}, f"Armature '{armature.name}' set to {mode}.")

        return {'FINISHED'}


# --- Bone Collection Organizer Operator ---

class AUTO_OT_organize_bone_collections(bpy.types.Operator):
    """Operator: Organize Bone Collections"""
    bl_idname = "armature.organize_bone_collections"
    bl_label = "Organize Bone Collections"
    bl_description = "Automatically organize bones into collections based on their names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        organize_bone_collections()
        return {'FINISHED'}


# --- Compact N Panel ---

class VIEW3D_PT_sz_utilities(bpy.types.Panel):
    """Panel: Sparking Zero Utility PowerTools"""
    bl_label = "SZ Utility PowerTools"
    bl_idname = "VIEW3D_PT_sz_utilities"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'SZ Utilities'

    def draw(self, context):
        layout = self.layout

        # Header
        layout.label(text="Bone Tools", icon='BONE_DATA')

        # Organize Bone Collections Button
        layout.operator(AUTO_OT_organize_bone_collections.bl_idname, icon='GROUP_BONE')

        # Separator
        layout.separator()

        # Header for Utilities
        layout.label(text="Utilities", icon='MODIFIER')

        # Toggle Pose/Rest Button
        layout.operator("armature.toggle_armature_pos", icon='ARMATURE_DATA', text="Toggle Pose/Rest")


# --- Message Box for Error Handling (Optional) ---

def draw_message_box(self, context, message="", title="Message Box", icon='INFO'):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


# Register Classes
classes = (
    AUTO_OT_organize_bone_collections,
    TOGGLE_ARMATURE_POS,
    VIEW3D_PT_sz_utilities,
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
