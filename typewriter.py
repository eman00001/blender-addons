bl_info = {
    "name": "Typewriter Animator",
    "author": "news0cks",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Text Animation",
    "description": "Animate letters appearing one by one like a typewriter",
    "category": "Animation",
}

import bpy

class TEXTANIM_OT_typewriter(bpy.types.Operator):
    bl_idname = "textanim.typewriter"
    bl_label = "Typewriter Effect"
    
    start_frame: bpy.props.IntProperty(name="Start Frame", default=1)
    letter_gap: bpy.props.IntProperty(name="Frames Between Letters", default=5)
    
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
        
        letters = [o for o in context.selected_objects if o.type == 'MESH']
        letters.sort(key=lambda o: o.location.x)
        letters = letters[::-1]  # Reverse order for typewriter effect
        
        frame = self.start_frame
        for letter in letters:
            letter.hide_viewport = True
            letter.keyframe_insert(data_path="hide_viewport", frame=frame)
            letter.hide_viewport = False
            letter.keyframe_insert(data_path="hide_viewport", frame=frame+self.letter_gap)
            frame += self.letter_gap
        
        return {'FINISHED'}

class TEXTANIM_PT_typewriter(bpy.types.Panel):
    bl_label = "Typewriter Effect"
    bl_idname = "TEXTANIM_PT_typewriter"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Text Animation"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("textanim.typewriter")

classes = [TEXTANIM_OT_typewriter, TEXTANIM_PT_typewriter]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
