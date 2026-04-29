bl_info = {
    "name": "news0cks Text Letter Animator",
    "author": "news0cks",
    "version": (1, 2),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Text Animation",
    "description": "Animate text objects letter by letter with fade-in/fade-out, upward motion, and easing",
    "category": "Animation",
}

import bpy

class TEXTANIM_OT_letter_animate(bpy.types.Operator):
    bl_idname = "textanim.letter_animate"
    bl_label = "Animate Letters"
    bl_description = "Animate each letter of the selected text sequentially with easing"
    bl_options = {"REGISTER", "UNDO"}
    
    start_frame: bpy.props.IntProperty(name="Start Frame", default=1, min=1)
    letter_gap: bpy.props.IntProperty(name="Frames Between Letters", default=5, min=1)
    duration: bpy.props.IntProperty(name="Fade/Move Duration", default=15, min=1)
    distance: bpy.props.FloatProperty(name="Move Distance", default=0.5)
    mode: bpy.props.EnumProperty(
        name="Animation Mode",
        description="Fade In or Fade Out",
        items=[('IN', "Fade In", ""), ('OUT', "Fade Out", "")],
        default='IN'
    )
    easing: bpy.props.EnumProperty(
        name="Easing",
        description="Keyframe interpolation type",
        items=[
            ('LINEAR', "Linear", "Constant speed"),
            ('EASE_IN', "Ease In", "Slow start, fast end"),
            ('EASE_OUT', "Ease Out", "Fast start, slow end"),
            ('EASE_IN_OUT', "Ease In-Out", "Smooth start and end"),
        ],
        default='EASE_OUT'
    )
    
    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'FONT':
            self.report({'ERROR'}, "Please select a text object")
            return {'CANCELLED'}
        
        # Duplicate original object to preserve it
        bpy.ops.object.duplicate()
        obj = context.active_object
        
        # Convert to separate letters
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.separate(type='LOOSE')
        bpy.ops.object.editmode_toggle()
        
        letters = [o for o in context.selected_objects if o.type == 'MESH']
        letters.sort(key=lambda o: o.location.x)
        
        frame = self.start_frame
        
        for letter in letters:
            letter.select_set(True)
            context.view_layer.objects.active = letter
            
            # Material with transparency
            if not letter.data.materials:
                mat = bpy.data.materials.new(name="LetterMaterial")
                mat.use_nodes = True
            else:
                mat = letter.data.materials[0]
                mat.use_nodes = True
            
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            nodes.clear()
            
            out = nodes.new("ShaderNodeOutputMaterial")
            trans = nodes.new("ShaderNodeBsdfTransparent")
            diffuse = nodes.new("ShaderNodeBsdfPrincipled")
            mix = nodes.new("ShaderNodeMixShader")
            
            links.new(trans.outputs[0], mix.inputs[1])
            links.new(diffuse.outputs[0], mix.inputs[2])
            links.new(mix.outputs[0], out.inputs[0])
            
            mat.blend_method = 'BLEND'
            
            # Set keyframes
            if self.mode == 'IN':
                mix.inputs[0].default_value = 0.0
                mix.inputs[0].keyframe_insert("default_value", frame=frame)
                mix.inputs[0].default_value = 1.0
                mix.inputs[0].keyframe_insert("default_value", frame=frame+self.duration)
                
                letter.keyframe_insert(data_path="location", frame=frame)
                letter.location.z += self.distance
                letter.keyframe_insert(data_path="location", frame=frame+self.duration)
                letter.location.z -= self.distance
            else:
                mix.inputs[0].default_value = 1.0
                mix.inputs[0].keyframe_insert("default_value", frame=frame)
                mix.inputs[0].default_value = 0.0
                mix.inputs[0].keyframe_insert("default_value", frame=frame+self.duration)
                
                letter.keyframe_insert(data_path="location", frame=frame)
                letter.location.z += self.distance
                letter.keyframe_insert(data_path="location", frame=frame+self.duration)
                letter.location.z -= self.distance
            
            # Apply easing
            if letter.animation_data and letter.animation_data.action:
                for fcurve in letter.animation_data.action.fcurves:
                    for kp in fcurve.keyframe_points:
                        if self.easing == 'LINEAR':
                            kp.interpolation = 'LINEAR'
                        else:
                            kp.interpolation = 'BEZIER'
                            if self.easing == 'EASE_IN':
                                kp.handle_left_type = 'AUTO'
                                kp.handle_right_type = 'FREE'
                            elif self.easing == 'EASE_OUT':
                                kp.handle_left_type = 'FREE'
                                kp.handle_right_type = 'AUTO'
                            elif self.easing == 'EASE_IN_OUT':
                                kp.handle_left_type = 'AUTO'
                                kp.handle_right_type = 'AUTO'
            
            frame += self.letter_gap
        
        return {'FINISHED'}

class TEXTANIM_PT_panel(bpy.types.Panel):
    bl_label = "Text Letter Animator"
    bl_idname = "TEXTANIM_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Text Animation"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("textanim.letter_animate")

classes = [TEXTANIM_OT_letter_animate, TEXTANIM_PT_panel]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
