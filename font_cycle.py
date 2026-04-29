bl_info = {
    "name": "Font Cycle Animator (Selected Text Only)",
    "author": "news0cks",
    "version": (1, 2),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > Text Animation",
    "description": "Cycle fonts by duplicating the selected text object and toggling render visibility sequentially",
    "category": "Animation",
}

import bpy
import os

# ---------------- Properties ----------------

class FontCycleProps(bpy.types.PropertyGroup):
    font_folder: bpy.props.StringProperty(
        name="Font Folder",
        description="Folder containing font files (searched recursively)",
        subtype='DIR_PATH',
        default=""
    )
    frame_start: bpy.props.IntProperty(
        name="Start Frame",
        default=1,
        min=1
    )
    frame_spacing: bpy.props.IntProperty(
        name="Frames Per Font",
        default=10,
        min=2  # need at least 2 frames so off-frame can be before the next on-frame
    )
    font_limit: bpy.props.IntProperty(
        name="Max Fonts (0 = all)",
        default=0,
        min=0
    )

# ---------------- Utilities ----------------

def find_fonts(folder, limit=0):
    fonts = []
    if not folder:
        return fonts
    folder_abs = bpy.path.abspath(folder)
    if not os.path.isdir(folder_abs):
        return fonts
    for root, _, files in os.walk(folder_abs):
        for f in files:
            if f.lower().endswith((".ttf", ".otf")):
                fonts.append(os.path.join(root, f))
                if limit and len(fonts) >= limit:
                    return sorted(fonts)
    return sorted(fonts)

def load_font_safe(path):
    abs_path = os.path.abspath(path)
    for font in bpy.data.fonts:
        fp = getattr(font, "filepath", None)
        if fp:
            try:
                if os.path.abspath(bpy.path.abspath(fp)) == abs_path:
                    return font
            except Exception:
                if os.path.abspath(fp) == abs_path:
                    return font
    try:
        return bpy.data.fonts.load(abs_path)
    except Exception:
        return None

def set_constant_interpolation(action, data_path):
    if action is None:
        return
    for fcu in action.fcurves:
        if fcu.data_path == data_path:
            for kp in fcu.keyframe_points:
                kp.interpolation = 'CONSTANT'

# ---------------- Operator ----------------

class FONT_OT_cycle_reliable(bpy.types.Operator):
    bl_idname = "font.cycle_reliable"
    bl_label = "Generate Reliable Font Cycle"
    bl_description = "Duplicate selected text with different fonts and animate render visibility sequentially"

    def execute(self, context):
        props = context.scene.font_cycle_props
        folder = props.font_folder
        start = props.frame_start
        spacing = props.frame_spacing
        limit = props.font_limit or 0

        # Use selected text object
        base = context.active_object
        if not base or base.type != 'FONT':
            self.report({'ERROR'}, "Select a single text object (FONT) before running")
            return {'CANCELLED'}

        fonts = find_fonts(folder, limit)
        if not fonts:
            self.report({'ERROR'}, "No fonts found in folder (check folder path)")
            return {'CANCELLED'}

        n = len(fonts)
        last_frame = start + n * spacing - 1

        coll_name = "FontCycle"
        coll = bpy.data.collections.get(coll_name)
        if coll is None:
            coll = bpy.data.collections.new(coll_name)
            context.scene.collection.children.link(coll)
        else:
            for o in list(coll.objects):
                try:
                    bpy.data.objects.remove(o, do_unlink=True)
                except Exception:
                    try:
                        coll.objects.unlink(o)
                    except Exception:
                        pass

        try:
            original_base_state = base.hide_render
            if base.animation_data is None:
                base.animation_data_create()
            if base.animation_data.action is None:
                base_action = bpy.data.actions.new(name=f"Action_base_{base.name}")
                base.animation_data.action = base_action
            else:
                base_action = base.animation_data.action

            base.hide_render = original_base_state
            base.keyframe_insert(data_path="hide_render", frame=max(1, start - 1))
            base.hide_render = True
            base.keyframe_insert(data_path="hide_render", frame=start)
            base.hide_render = original_base_state
            base.keyframe_insert(data_path="hide_render", frame=last_frame + 1)
            set_constant_interpolation(base_action, "hide_render")
        except Exception:
            base.hide_render = True

        duplicates = []
        for i, font_path in enumerate(fonts):
            font = load_font_safe(font_path)
            if not font:
                continue

            dup = base.copy()
            dup.data = base.data.copy()
            dup.name = f"{base.name}_font_{i:03d}"
            try:
                dup.matrix_world = base.matrix_world.copy()
            except Exception:
                pass
            try:
                dup.data.font = font
            except Exception:
                continue
            dup.hide_viewport = base.hide_viewport
            dup.hide_render = True
            coll.objects.link(dup)

            if dup.animation_data is None:
                dup.animation_data_create()
            action = bpy.data.actions.new(name=f"Action_{dup.name}")
            dup.animation_data.action = action
            duplicates.append((dup, action))

        if not duplicates:
            self.report({'ERROR'}, "No duplicates created (fonts may have failed to load)")
            return {'CANCELLED'}

        for idx, (dup, action) in enumerate(duplicates):
            frame_on = start + idx * spacing
            frame_off = frame_on + spacing - 2  # end 1 frame before the next starts

            # invisible before
            dup.hide_render = True
            dup.keyframe_insert(data_path="hide_render", frame=frame_on - 1)

            # visible
            dup.hide_render = False
            dup.keyframe_insert(data_path="hide_render", frame=frame_on)

            # back to invisible BEFORE next one starts
            dup.hide_render = True
            dup.keyframe_insert(data_path="hide_render", frame=frame_off + 1)

            set_constant_interpolation(action, "hide_render")

        self.report({'INFO'}, f"Created {len(duplicates)} font duplicates in '{coll_name}'. Frames {start}..{last_frame}")
        return {'FINISHED'}

# ---------------- UI Panel ----------------

class FONT_PT_cycle_panel(bpy.types.Panel):
    bl_label = "Font Cycle Animator"
    bl_idname = "FONT_PT_cycle_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Text Animation'

    def draw(self, context):
        layout = self.layout
        props = context.scene.font_cycle_props
        layout.prop(props, "font_folder")
        layout.prop(props, "font_limit")
        layout.prop(props, "frame_start")
        layout.prop(props, "frame_spacing")
        layout.operator("font.cycle_reliable", text="Generate Font Cycle")

# ---------------- Register ----------------

classes = [FontCycleProps, FONT_OT_cycle_reliable, FONT_PT_cycle_panel]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.font_cycle_props = bpy.props.PointerProperty(type=FontCycleProps)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.font_cycle_props

if __name__ == "__main__":
    register()
