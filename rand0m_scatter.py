bl_info = {
    "name": "Random Scatter Animator",
    "author": "news0cks",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Text Animation",
    "description": "Animate letters from random positions into place",
    "category": "Animation",
}

import bpy, random

class TEXTANIM_OT_random_scatter(bpy.types.Operator):
    bl_idname = "textanim.random_scatter"
    bl_label = "Random Scatter"
    
    start_frame: bpy.props.IntProperty(name="Start Frame", default=1)
    duration: bpy.props.IntProperty(name="Duration", default=20)
    letter_gap: bpy.props.IntProperty(name="Frames Between Letters", default=5)
    offset_range: bpy.props.FloatProperty(name="Max Random Offset", default=2.0)
    
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
        
        frame = self.start_frame
        for letter in letters:
            orig_pos = letter.location.copy()
            letter.location.x += random.uniform(-self.offset_range, self.offset_range)
            letter.location.y += random.uniform(-self.offset_range, self.offset_range)
            letter.location.z += random.uniform(-self.offset_range, self.offset_range)
            
            letter.keyframe_insert(data_path="location", frame=frame)
            letter.location = orig_pos
            letter.keyframe_insert(data_path="location", frame=frame+self.duration)
            
            frame += self.letter_gap
        
        return {'FINISHED'}

class TEXTANIM_PT_random_scatter(bpy.types.Panel):
    bl_label = "Random Scatter"
    bl_idname = "TEXTANIM_PT_random_scatter"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Text Animation"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("textanim.random_scatter")

classes = [TEXTANIM_OT_random_scatter, TEXTANIM_PT_random_scatter]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
