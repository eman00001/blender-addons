bl_info = {
    "name": "Letter Jitter Animator",
    "author": "news0cks",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Text Animation",
    "description": "Animate letters shaking in place",
    "category": "Animation",
}

import bpy, random

class TEXTANIM_OT_jitter(bpy.types.Operator):
    bl_idname = "textanim.jitter"
    bl_label = "Letter Jitter / Shake"
    
    start_frame: bpy.props.IntProperty(name="Start Frame", default=1)
    duration: bpy.props.IntProperty(name="Duration", default=20)
    amplitude: bpy.props.FloatProperty(name="Shake Amplitude", default=0.1)
    frequency: bpy.props.IntProperty(name="Shakes Per Letter", default=5)
    
    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'FONT':
            self.report({'ERROR'}, "Select a text object")
            return {'CANCELLED'}
        
        bpy.ops.object.duplicate()
        obj = context.active_object
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.separate(type='LOOSE')
        bpy.ops.object.editmode_toggle()
        
classes = [TEXTANIM_OT_jitter]  # all your classes

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()

