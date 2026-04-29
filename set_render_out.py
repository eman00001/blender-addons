bl_info = {
    "name": "Set Render Output",
    "author": "news0cks",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "Render Properties > Output",
    "description": "Sets render output folder to project name before last underscore",
    "category": "Render",
}

import bpy
import os

class RENDER_OT_set_output_path(bpy.types.Operator):
    bl_idname = "render.set_output_path_project"
    bl_label = "Set Output Path"
    bl_description = "Set render output path based on project name before last underscore"

    def execute(self, context):
        # Get current file path
        filepath = bpy.data.filepath
        if not filepath:
            self.report({'ERROR'}, "Please save the project first.")
            return {'CANCELLED'}

        # Extract project name without extension
        filename = os.path.splitext(os.path.basename(filepath))[0]

        # Split by underscores and remove the last part
        parts = filename.split("_")
        if len(parts) > 1:
            project_name = "_".join(parts[:-1])
        else:
            project_name = filename

        # Build output directory
        output_dir = os.path.join("C:\\Users\\emiyu\\Videos\\Blender Outs", project_name)

        # Ensure path ends with slash
        output_path = output_dir + os.sep

        # Set render output path
        bpy.context.scene.render.filepath = output_path

        self.report({'INFO'}, f"Render output set to: {output_path}")
        return {'FINISHED'}

class RENDER_PT_output_path_panel(bpy.types.Panel):
    bl_label = "Custom Output Path"
    bl_idname = "RENDER_PT_output_path_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"

    def draw(self, context):
        layout = self.layout
        layout.operator("render.set_output_path_project", icon="FILE_FOLDER")

def register():
    bpy.utils.register_class(RENDER_OT_set_output_path)
    bpy.utils.register_class(RENDER_PT_output_path_panel)

def unregister():
    bpy.utils.unregister_class(RENDER_OT_set_output_path)
    bpy.utils.unregister_class(RENDER_PT_output_path_panel)

if __name__ == "__main__":
    register()
