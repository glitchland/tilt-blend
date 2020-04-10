import bpy
 
class TILT_OT_MessageBox(bpy.types.Operator):
    bl_idname = "message.tiltmessagebox"
    bl_label = ""
 
    message = bpy.props.StringProperty(
        name = "message",
        description = "message",
        default = ''
    )
 
    def execute(self, context):
        self.report({'INFO'}, self.message)
        print(self.message)
        return {'FINISHED'}
 
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 600)
 
    def draw(self, context):
        self.layout.label(text=self.message)
        self.layout.label(text='')