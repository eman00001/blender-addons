bl_info = {
    "name": "Lyrics Animated Creator (Alpha Fade Only, No NLA)",
    "author": "news0cks",
    "version": (1, 0),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > Lyrics Creator (No NLA)",
    "description": "Create text objects for lyrics with alpha fade animation (no NLA/actions)",
    "category": "Animation",
}

import bpy
import re
import os

FONT_PATH = r"C:\Users\emiyu\OneDrive\Documents\fonts\testamentos-jeda\Testamento-Jed@.ttf"

def sanitize_name(s):
    s = re.sub(r"[^0-9A-Za-z_]", "_", s.strip())
    return s[:20] if s else "Line"

class NEWS0CKS_SIMPLE_Props(bpy.types.PropertyGroup):
    lyrics_text: bpy.props.StringProperty(
        name="Lyrics",
        description="Enter lyrics separated by commas",
        default="Line 1, Line 2, Line 3"
    )
    visibility_duration: bpy.props.IntProperty(
        name="Visible Frames",
        default=24,
        min=1
    )
    fade_frames: bpy.props.IntProperty(
        name="Fade Duration",
        default=6,
        min=1,
        description="Number of frames for fade in/out"
    )
    line_spacing: bpy.props.IntProperty(
        name="Line Spacing",
        default=30,
        min=1
    )
    clear_existing: bpy.props.BoolProperty(
        name="Clear Existing Collection",
        default=True
    )

class NEWS0CKS_SIMPLE_OT_CreateLyrics(bpy.types.Operator):
    bl_idname = "news0cks_simple.create_lyrics"
    bl_label = "Create Lyrics (No NLA)"
    bl_description = "Create animated text objects for lyrics with alpha fade (no NLA)"

    def execute(self, context):
        props = context.scene.news0cks_simple_props
        lyrics = [l.strip() for l in props.lyrics_text.split(",") if l.strip()]

        coll_name = "Lyrics_Animated"
        coll = bpy.data.collections.get(coll_name)
        if not coll:
            coll = bpy.data.collections.new(coll_name)
            context.scene.collection.children.link(coll)
        elif props.clear_existing:
            for o in list(coll.objects):
                try:
                    bpy.data.objects.remove(o, do_unlink=True)
                except Exception:
                    coll.objects.unlink(o)

        # Find the highest existing number in the collection
        existing_numbers = []
        for o in coll.objects:
            match = re.match(r"(\d{3})_", o.name)
            if match:
                existing_numbers.append(int(match.group(1)))
        start_number = max(existing_numbers, default=0) + 1

        # Load the custom font
        font = None
        if os.path.exists(FONT_PATH):
            font = bpy.data.fonts.load(FONT_PATH)
        else:
            self.report({'WARNING'}, f"Font not found at {FONT_PATH}, using default font")

        for offset, line in enumerate(lyrics):
            num = start_number + offset
            obj_name = f"{num:03d}_{sanitize_name(line)}"

            # Create text object
            curve = bpy.data.curves.new(name=f"Text_{num:03d}", type='FONT')
            obj = bpy.data.objects.new(obj_name, curve)
            obj.data.body = line
            if font:
                obj.data.font = font
            coll.objects.link(obj)

            frame_start = (num - 1) * props.line_spacing
            frame_visible_start = frame_start + 1
            frame_visible_end = frame_visible_start + props.visibility_duration
            fade = props.fade_frames

            # Create material with alpha driven by custom property
            mat = bpy.data.materials.new(name=f"Mat_{obj.name}")
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            bsdf.inputs["Alpha"].default_value = 0
            obj.data.materials.append(mat)
            mat.blend_method = 'BLEND'

            # Add custom property for alpha control
            if "lyric_alpha" not in obj:
                obj["lyric_alpha"] = 0.0

            # Create driver from object property -> material alpha
            drv = bsdf.inputs["Alpha"].driver_add("default_value").driver
            drv.type = 'SCRIPTED'
            var = drv.variables.new()
            var.name = "a"
            var.targets[0].id = obj
            var.targets[0].data_path = '["lyric_alpha"]'
            drv.expression = "a"

            # Animate object property directly (no NLA, no action reassignment)
            obj["lyric_alpha"] = 0.0
            obj.keyframe_insert('["lyric_alpha"]', frame=frame_visible_start - fade)

            obj["lyric_alpha"] = 1.0
            obj.keyframe_insert('["lyric_alpha"]', frame=frame_visible_start)

            obj["lyric_alpha"] = 1.0
            obj.keyframe_insert('["lyric_alpha"]', frame=frame_visible_end)

            obj["lyric_alpha"] = 0.0
            obj.keyframe_insert('["lyric_alpha"]', frame=frame_visible_end + fade)

        self.report({'INFO'}, f"Created {len(lyrics)} text objects in '{coll_name}' with alpha fade (no NLA)")
        return {'FINISHED'}

class NEWS0CKS_SIMPLE_PT_LyricPanel(bpy.types.Panel):
    bl_label = "Lyrics Animated Creator (No NLA)"
    bl_idname = "NEWS0CKS_SIMPLE_PT_LyricPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Lyrics'

    def draw(self, context):
        layout = self.layout
        props = context.scene.news0cks_simple_props

        layout.prop(props, "lyrics_text")
        layout.prop(props, "visibility_duration")
        layout.prop(props, "fade_frames")
        layout.prop(props, "line_spacing")
        layout.prop(props, "clear_existing")
        layout.operator("news0cks_simple.create_lyrics")

classes = [NEWS0CKS_SIMPLE_Props, NEWS0CKS_SIMPLE_OT_CreateLyrics, NEWS0CKS_SIMPLE_PT_LyricPanel]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.news0cks_simple_props = bpy.props.PointerProperty(type=NEWS0CKS_SIMPLE_Props)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.news0cks_simple_props

if __name__ == "__main__":
    register()
