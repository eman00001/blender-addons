bl_info = {
    "name": "Cumulative Centered Words",
    "author": "news0cks",
    "version": (1, 0),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > Cumulative Words",
    "description": "Animate words cumulatively, keeping the group centered",
    "category": "Animation",
}

import bpy

class NEWS0CKS_CumWordsProps(bpy.types.PropertyGroup):
    line_text: bpy.props.StringProperty(
        name="Line Text",
        default="This is a sample line"
    )
    start_frame: bpy.props.IntProperty(
        name="Start Frame",
        default=1,
        min=1
    )
    word_spacing: bpy.props.FloatProperty(
        name="Word Spacing",
        default=2.0
    )
    fade_frames: bpy.props.IntProperty(
        name="Fade-in Frames",
        default=6,
        min=1
    )
    clear_existing: bpy.props.BoolProperty(
        name="Clear Previous Words",
        default=True
    )

class NEWS0CKS_OT_CumulativeWords(bpy.types.Operator):
    bl_idname = "news0cks.cumulative_words"
    bl_label = "Create Cumulative Words"
    bl_description = "Create text objects for each word with cumulative centering animation"

    def execute(self, context):
        props = context.scene.news0cks_cum_props
        words = [w.strip() for w in props.line_text.split() if w.strip()]
        coll_name = "CumulativeWords"
        coll = bpy.data.collections.get(coll_name)
        if not coll:
            coll = bpy.data.collections.new(coll_name)
            context.scene.collection.children.link(coll)
        elif props.clear_existing:
            for o in list(coll.objects):
                try:
                    bpy.data.objects.remove(o, do_unlink=True)
                except:
                    coll.objects.unlink(o)

        objects = []
        word_spacing = props.word_spacing
        frame = props.start_frame

        for i, word in enumerate(words):
            # Create text object
            curve = bpy.data.curves.new(name=f"Word_{i:03d}", type='FONT')
            obj = bpy.data.objects.new(f"{i:03d}_{word}", curve)
            obj.data.body = word
            coll.objects.link(obj)

            # Create alpha material
            mat = bpy.data.materials.new(name=f"Mat_{obj.name}")
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            bsdf.inputs["Alpha"].default_value = 0
            obj.data.materials.append(mat)
            mat.blend_method = 'BLEND'

            # Animate alpha fade-in
            bsdf.inputs["Alpha"].keyframe_insert(data_path="default_value", frame=frame)
            bsdf.inputs["Alpha"].default_value = 1
            bsdf.inputs["Alpha"].keyframe_insert(data_path="default_value", frame=frame + props.fade_frames)

            objects.append(obj)

            # Re-center all words
            total_width = sum(o.dimensions.x for o in objects) + word_spacing * (len(objects)-1)
            start_x = -total_width / 2
            for j, o in enumerate(objects):
                x_pos = start_x + sum(objects[k].dimensions.x + word_spacing for k in range(j))
                o.location.x = x_pos
                o.keyframe_insert(data_path="location", index=0, frame=frame)

            frame += props.fade_frames  # Next word appears after fade-in

        self.report({'INFO'}, f"Created {len(words)} cumulative words in '{coll_name}'")
        return {'FINISHED'}

class NEWS0CKS_PT_CumWordsPanel(bpy.types.Panel):
    bl_label = "Cumulative Words Animator"
    bl_idname = "NEWS0CKS_PT_CumWordsPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Cumulative Words'

    def draw(self, context):
        layout = self.layout
        props = context.scene.news0cks_cum_props
        layout.prop(props, "line_text")
        layout.prop(props, "start_frame")
        layout.prop(props, "word_spacing")
        layout.prop(props, "fade_frames")
        layout.prop(props, "clear_existing")
        layout.operator("news0cks.cumulative_words")

classes = [NEWS0CKS_CumWordsProps, NEWS0CKS_OT_CumulativeWords, NEWS0CKS_PT_CumWordsPanel]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.news0cks_cum_props = bpy.props.PointerProperty(type=NEWS0CKS_CumWordsProps)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.news0cks_cum_props

if __name__ == "__main__":
    register()
