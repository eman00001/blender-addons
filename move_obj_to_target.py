bl_info = {
    "name": "Move Object to Target",
    "author": "news0cks",
    "version": (1, 2),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > Item",
    "description": "Moves the active object to the location and rotation of a chosen target object",
    "category": "Object",
}

import bpy

class NEWS0CKS_Props(bpy.types.PropertyGroup):
    target_object: bpy.props.PointerProperty(
        name="Target Object",
        type=bpy.types.Object,
        description="Object to move the active object to"
    )

class NEWS0CKS_OT_MoveObject(bpy.types.Operator):
    bl_idname = "news0cks.move_object_to_target"
    bl_label = "Move Object to Target"
    bl_description = "Moves the active object to the location and rotation of the target object"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None

    def execute(self, context):
        props = context.scene.news0cks_props
        active_obj = context.active_object
        target = props.target_object

        if target is None:
            self.report({'ERROR'}, "No target object selected")
            return {'CANCELLED'}

        # Copy transforms
        active_obj.location = target.location
        active_obj.rotation_euler = target.rotation_euler

        self.report({'INFO'}, f"Moved {active_obj.name} to {target.name} (location + rotation)")
        return {'FINISHED'}

class NEWS0CKS_PT_MoveObjectPanel(bpy.types.Panel):
    bl_label = "Move Object to Target"
    bl_idname = "NEWS0CKS_PT_MoveObjectPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'

    def draw(self, context):
        layout = self.layout
        props = context.scene.news0cks_props

        layout.prop(props, "target_object")
        layout.operator("news0cks.move_object_to_target")

classes = [NEWS0CKS_Props, NEWS0CKS_OT_MoveObject, NEWS0CKS_PT_MoveObjectPanel]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.news0cks_props = bpy.props.PointerProperty(type=NEWS0CKS_Props)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.news0cks_props

if __name__ == "__main__":
    register()
