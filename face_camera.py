bl_info = {
    "name": "Copy Camera Rotation",
    "author": "news0cks",
    "version": (1, 0),
    "blender": (4, 5, 0),
    "location": "3D View > Sidebar > Item",
    "description": "Make selected objects face the camera by copying its rotation",
    "category": "Object",
}

import bpy

class NEWS0CKS_OT_CopyCameraRotation(bpy.types.Operator):
    bl_idname = "news0cks.copy_camera_rotation"
    bl_label = "Copy Camera Rotation"
    bl_description = "Copy the active camera rotation to selected objects"

    def execute(self, context):
        cam = context.scene.camera
        if not cam:
            self.report({'ERROR'}, "No active camera in the scene")
            return {'CANCELLED'}

        for obj in context.selected_objects:
            if obj.type != 'CAMERA':  # avoid copying onto camera itself
                obj.rotation_euler = cam.rotation_euler
                obj.keyframe_insert(data_path="rotation_euler")  # optional if you want to animate
        self.report({'INFO'}, f"Copied camera rotation to {len(context.selected_objects)} objects")
        return {'FINISHED'}

class NEWS0CKS_PT_CameraToolsPanel(bpy.types.Panel):
    bl_label = "Face Camera"
    bl_idname = "NEWS0CKS_PT_CameraToolsPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'

    def draw(self, context):
        layout = self.layout
        layout.operator("news0cks.copy_camera_rotation")

classes = [NEWS0CKS_OT_CopyCameraRotation, NEWS0CKS_PT_CameraToolsPanel]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
