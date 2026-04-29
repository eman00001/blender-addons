bl_info = {
    "name": "Camera Ease Toolkit",
    "author": "news0cks",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Camera Ease",
    "description": "Adds advanced ease in/out and curve presets for camera animation",
    "category": "Animation",
}

import bpy
from math import pi

# -----------------------------
# Helper Functions
# -----------------------------

def get_fcurves(obj):
    if not obj.animation_data or not obj.animation_data.action:
        return []
    return obj.animation_data.action.fcurves


def apply_curve_preset(fcurve, preset):
    for kp in fcurve.keyframe_points:
        kp.interpolation = 'BEZIER'

        if preset == 'SMOOTH':
            kp.easing = 'AUTO'
            kp.handle_left_type = 'AUTO'
            kp.handle_right_type = 'AUTO'

        elif preset == 'EASE_IN':
            kp.handle_left_type = 'VECTOR'
            kp.handle_right_type = 'ALIGNED'

        elif preset == 'EASE_OUT':
            kp.handle_left_type = 'ALIGNED'
            kp.handle_right_type = 'VECTOR'

        elif preset == 'SHARP':
            kp.handle_left_type = 'VECTOR'
            kp.handle_right_type = 'VECTOR'

        elif preset == 'BOUNCE':
            kp.interpolation = 'BACK'

        elif preset == 'ELASTIC':
            kp.interpolation = 'ELASTIC'

    fcurve.update()


# -----------------------------
# Operator
# -----------------------------

class CAMERA_OT_apply_ease(bpy.types.Operator):
    bl_idname = "camera.apply_ease_curve"
    bl_label = "Apply Ease Curve"

    preset: bpy.props.EnumProperty(
        name="Preset",
        items=[
            ('SMOOTH', "Smooth (Default)", "Smooth cinematic easing"),
            ('EASE_IN', "Ease In", "Slow start"),
            ('EASE_OUT', "Ease Out", "Slow end"),
            ('SHARP', "Sharp", "Linear sharp motion"),
            ('BOUNCE', "Bounce", "Bouncy effect"),
            ('ELASTIC', "Elastic", "Elastic spring motion"),
        ]
    )

    def execute(self, context):
        obj = context.object

        if not obj or obj.type != 'CAMERA':
            self.report({'ERROR'}, "Select a camera")
            return {'CANCELLED'}

        fcurves = get_fcurves(obj)

        if not fcurves:
            self.report({'WARNING'}, "No animation found")
            return {'CANCELLED'}

        for fc in fcurves:
            apply_curve_preset(fc, self.preset)

        self.report({'INFO'}, f"Applied {self.preset} curve")
        return {'FINISHED'}


# -----------------------------
# UI Panel
# -----------------------------

class CAMERA_PT_ease_panel(bpy.types.Panel):
    bl_label = "Camera Ease Toolkit"
    bl_idname = "CAMERA_PT_ease_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Camera Ease'

    def draw(self, context):
        layout = self.layout

        layout.label(text="Apply Curve Presets:")

        col = layout.column(align=True)
        col.operator("camera.apply_ease_curve", text="Smooth").preset = 'SMOOTH'
        col.operator("camera.apply_ease_curve", text="Ease In").preset = 'EASE_IN'
        col.operator("camera.apply_ease_curve", text="Ease Out").preset = 'EASE_OUT'
        col.operator("camera.apply_ease_curve", text="Sharp").preset = 'SHARP'
        col.operator("camera.apply_ease_curve", text="Bounce").preset = 'BOUNCE'
        col.operator("camera.apply_ease_curve", text="Elastic").preset = 'ELASTIC'


# -----------------------------
# Registration
# -----------------------------

classes = (
    CAMERA_OT_apply_ease,
    CAMERA_PT_ease_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
