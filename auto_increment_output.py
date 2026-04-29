bl_info = {
    "name": "Auto-Increment Render Output",
    "author": "news0cks",
    "version": (1, 0),
    "blender": (4, 5, 0),
    "location": "Render Properties > Auto-Increment Output",
    "description": "Automatically increments render filenames to avoid overwriting",
    "category": "Render",
}

import bpy
import os
import re

def auto_increment_filename(scene):
    output_path = bpy.context.scene.render.filepath
    folder, base_name = os.path.split(output_path)
    
    if not folder:
        folder = os.path.dirname(bpy.data.filepath)  # fallback to blend file folder

    if not os.path.exists(folder):
        os.makedirs(folder)

    base_name_no_ext, ext = os.path.splitext(base_name)
    if not ext:
        ext = ".png"  # default if none set

    # Find existing files that match pattern
    existing_files = [f for f in os.listdir(folder) if f.startswith(base_name_no_ext)]
    numbers = []
    for f in existing_files:
        match = re.search(r"_(\d+)", f)
        if match:
            numbers.append(int(match.group(1)))
    
    next_number = max(numbers, default=0) + 1
    new_path = os.path.join(folder, f"{base_name_no_ext}_{next_number}{ext}")
    bpy.context.scene.render.filepath = new_path
    print(f"[Auto-Increment] Render will be saved as: {new_path}")

class NEWS0CKS_OT_toggle_auto_increment(bpy.types.Operator):
    bl_idname = "render.toggle_auto_increment"
    bl_label = "Toggle Auto-Increment Output"
    bl_description = "Enable or disable auto-incrementing filenames on render"

    def execute(self, context):
        prefs = context.scene.news0cks_auto_increment
        if prefs.enabled:
            # Remove handler
            if auto_increment_filename in bpy.app.handlers.render_pre:
                bpy.app.handlers.render_pre.remove(auto_increment_filename)
            prefs.enabled = False
            self.report({'INFO'}, "Auto-increment disabled")
        else:
            # Add handler
            if auto_increment_filename not in bpy.app.handlers.render_pre:
                bpy.app.handlers.render_pre.append(auto_increment_filename)
            prefs.enabled = True
            self.report({'INFO'}, "Auto-increment enabled")
        return {'FINISHED'}

class NEWS0CKS_Props(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(
        name="Enabled",
        default=False
    )

class NEWS0CKS_PT_auto_increment_panel(bpy.types.Panel):
    bl_label = "Auto-Increment Render Output"
    bl_idname = "NEWS0CKS_PT_auto_increment_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"

    def draw(self, context):
        layout = self.layout
        prefs = context.scene.news0cks_auto_increment
        row = layout.row()
        if prefs.enabled:
            row.operator("render.toggle_auto_increment", text="Disable Auto-Increment", icon="PAUSE")
        else:
            row.operator("render.toggle_auto_increment", text="Enable Auto-Increment", icon="PLAY")

classes = [
    NEWS0CKS_Props,
    NEWS0CKS_OT_toggle_auto_increment,
    NEWS0CKS_PT_auto_increment_panel
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.news0cks_auto_increment = bpy.props.PointerProperty(type=NEWS0CKS_Props)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.news0cks_auto_increment
    # Remove handler if it’s still registered
    if auto_increment_filename in bpy.app.handlers.render_pre:
        bpy.app.handlers.render_pre.remove(auto_increment_filename)

if __name__ == "__main__":
    register()
