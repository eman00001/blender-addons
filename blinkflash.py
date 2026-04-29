bl_info = {
    "name": "Blink Animator (Position)",
    "author": "news0cks",
    "version": (1, 3),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > Text Animation",
    "description": "Animate letters blinking by moving them out of view",
    "category": "Animation",
}

import bpy
from mathutils import Vector

class TEXTANIM_Props(bpy.types.PropertyGroup):
    start_frame: bpy.props.IntProperty(name="Start Frame", default=1, min=1)
    blink_interval: bpy.props.IntProperty(name="Frames Between Blinks", default=5, min=1)
    total_duration: bpy.props.IntProperty(name="Total Duration (Frames)", default=60, min=1)
    far_away_offset: bpy.props.FloatProperty(name="Distance Away", default=1000.0)

class TEXTANIM_OT_blink(bpy.types.Operator):
    bl_idname = "textanim.blink_pos"
    bl_label = "Blink / Flash (Position)"
    
    def execute(self, context):
        props = context.scene.textanim_props
        obj = context.active_object
        if not obj or obj.type != 'FONT':
            self.report({'ERROR'}, "Select a text object")
            return {'CANCELLED'}
        
        # Duplicate to preserve original
        bpy.ops.object.duplicate()
        obj = context.active_object
        
        # Convert to mesh and separate letters
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.separate(type='LOOSE')
        bpy.ops.object.editmode_toggle()
        
        letters = [o for o in context.selected_objects if o.type == 'MESH']
        
        for letter in letters:
            orig_loc = letter.location.copy()
            frame = props.start_frame
            
            while frame < props.start_frame + props.total_duration:
                # Show letter (move to original location)
                letter.location = orig_loc
                letter.keyframe_insert(data_path="location", frame=frame)
                frame += props.blink_interval
                # Hide letter (move far away)
                letter.location = orig_loc + Vector((0, 0, props.far_away_offset))
                letter.keyframe_insert(data_path="location", frame=frame)
                frame += props.blink_interval
        
        return {'FINISHED'}

class TEXTANIM_PT_blink(bpy.types.Panel):
    bl_label = "Blink / Flash"
    bl_idname = "TEXTANIM_PT_blink"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Text Animation"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.textanim_props
        layout.prop(props, "start_frame")
        layout.prop(props, "blink_interval")
        layout.prop(props, "total_duration")
        layout.prop(props, "far_away_offset")
        layout.operator("textanim.blink_pos")

classes = [TEXTANIM_Props, TEXTANIM_OT_blink, TEXTANIM_PT_blink]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.textanim_props = bpy.props.PointerProperty(type=TEXTANIM_Props)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.textanim_props

if __name__ == "__main__":
    register()
