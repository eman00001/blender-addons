bl_info = {
    "name": "Fade-In/Out Animation",
    "blender": (3, 0, 0),
    "category": "Animation",
    "author": "news0cks",
    "description": "Adds fade-in up or fade-out down animations to the selected object with easing",
}

import bpy

# --- Operator: Apply Animation ---
class OBJECT_OT_fadeio(bpy.types.Operator):
    bl_idname = "object.fadeio"
    bl_label = "Apply Fade Animation"
    bl_description = "Animate the selected object with fade-in up or fade-out down effect"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj:
            self.report({'ERROR'}, "No object selected!")
            return {'CANCELLED'}

        props = context.scene.fadeio_props
        start_frame = props.start_frame
        duration = props.duration
        offset = props.offset
        end_frame = start_frame + duration
        mode = props.mode
        easing = props.easing

        # --- Ensure material ---
        if not obj.data.materials:
            mat = bpy.data.materials.new(name="FadeMat")
            mat.use_nodes = True
            obj.data.materials.append(mat)
        else:
            mat = obj.data.materials[0]
            if mat is None:
                mat = bpy.data.materials.new(name="FadeMat")
                mat.use_nodes = True
                obj.data.materials[0] = mat
            else:
                mat.use_nodes = True

        # Get Principled BSDF
        nodes = mat.node_tree.nodes
        principled = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if principled is None:
            principled = nodes.new(type="ShaderNodeBsdfPrincipled")

        # --- Apply animations ---
        if mode == 'IN_UP':
            # Location
            obj.location.z -= offset
            obj.keyframe_insert(data_path="location", frame=start_frame)
            obj.location.z += offset
            obj.keyframe_insert(data_path="location", frame=end_frame)
            # Opacity
            principled.inputs["Alpha"].default_value = 0.0
            principled.inputs["Alpha"].keyframe_insert("default_value", frame=start_frame)
            principled.inputs["Alpha"].default_value = 1.0
            principled.inputs["Alpha"].keyframe_insert("default_value", frame=end_frame)

        elif mode == 'OUT_DOWN':
            # Location
            obj.keyframe_insert(data_path="location", frame=start_frame)
            obj.location.z -= offset
            obj.keyframe_insert(data_path="location", frame=end_frame)
            # Opacity
            principled.inputs["Alpha"].default_value = 1.0
            principled.inputs["Alpha"].keyframe_insert("default_value", frame=start_frame)
            principled.inputs["Alpha"].default_value = 0.0
            principled.inputs["Alpha"].keyframe_insert("default_value", frame=end_frame)

        # Transparency setup
        mat.blend_method = 'BLEND'
        if hasattr(mat, "shadow_method"):
            mat.shadow_method = 'HASHED'
        elif hasattr(mat, "use_shadow"):
            mat.use_shadow = True

        # --- Adjust easing ---
        action = obj.animation_data.action if obj.animation_data else None
        if action:
            for fcurve in action.fcurves:
                for kp in fcurve.keyframe_points:
                    if easing == 'LINEAR':
                        kp.interpolation = 'LINEAR'
                    elif easing == 'EASE_IN':
                        kp.interpolation = 'BEZIER'
                        kp.handle_left_type = 'AUTO'
                        kp.handle_right_type = 'FREE'
                        kp.handle_right.y = kp.co.y * 1.3
                    elif easing == 'EASE_OUT':
                        kp.interpolation = 'BEZIER'
                        kp.handle_left_type = 'AUTO'
                        kp.handle_right_type = 'FREE'
                        kp.handle_left.y = kp.co.y * 0.7
                    elif easing == 'EASE_IN_OUT':
                        kp.interpolation = 'BEZIER'
                        kp.handle_left_type = 'AUTO'
                        kp.handle_right_type = 'AUTO'

        self.report({'INFO'}, f"{mode} ({easing}) applied: frames {start_frame} to {end_frame}")
        return {'FINISHED'}


# --- Property Group (UI settings) ---
class FadeIOProperties(bpy.types.PropertyGroup):
    duration: bpy.props.IntProperty(
        name="Duration",
        description="Length of animation in frames",
        default=40,
        min=1
    )
    offset: bpy.props.FloatProperty(
        name="Offset",
        description="How far the object moves vertically",
        default=1.0,
        min=0.0
    )
    start_frame: bpy.props.IntProperty(
        name="Start Frame",
        description="Frame to start the animation",
        default=1,
        min=0
    )
    mode: bpy.props.EnumProperty(
        name="Mode",
        description="Choose animation type",
        items=[
            ('IN_UP', "Fade-In Up", "Fade in while moving upward"),
            ('OUT_DOWN', "Fade-Out Down", "Fade out while moving downward")
        ],
        default='IN_UP'
    )
    easing: bpy.props.EnumProperty(
        name="Easing",
        description="Interpolation style",
        items=[
            ('LINEAR', "Linear", "Constant speed"),
            ('EASE_IN', "Ease In", "Slow start, fast end"),
            ('EASE_OUT', "Ease Out", "Fast start, slow end"),
            ('EASE_IN_OUT', "Ease In-Out", "Smooth both ends"),
        ],
        default='EASE_OUT'
    )


# --- UI Panel ---
class VIEW3D_PT_fadeio(bpy.types.Panel):
    bl_label = "Fade In/Out Animation"
    bl_idname = "VIEW3D_PT_fadeio"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Animation"

    def draw(self, context):
        layout = self.layout
        props = context.scene.fadeio_props

        layout.prop(props, "mode")
        layout.prop(props, "duration")
        layout.prop(props, "offset")
        layout.prop(props, "start_frame")
        layout.prop(props, "easing")
        layout.operator("object.fadeio", icon="ANIM")


# --- Registration ---
classes = (
    OBJECT_OT_fadeio,
    FadeIOProperties,
    VIEW3D_PT_fadeio,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.fadeio_props = bpy.props.PointerProperty(type=FadeIOProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.fadeio_props

if __name__ == "__main__":
    register()
