import bpy
from bpy.types import PropertyGroup, UIList, Operator, Panel 
from bpy.props import StringProperty, PointerProperty 

BRUSH_ITEMS = [
    ('0','Bubbles',''),
    ('1','CelVinyl',''),
    ('2','ChromaticWave',''),
    ('3','CoarseBristles',''),
    ('4','CoarseBristlesSingleSided',''),
    ('5','Comet',''),
    ('6','DiamondHull',''),
    ('7','Disco',''),
    ('8','DotMarker',''),
    ('9','Dots',''),
    ('10','DoubleTaperedFlat',''),
    ('11','DoubleTaperedMarker',''),
    ('12','DuctTape',''),
    ('13','DuctTapeSingleSided',''),
    ('14','Electricity',''),
    ('15','Embers',''),
    ('16','Fire',''),
    ('17','Flat',''),
    ('18','FlatDeprecated',''),
    ('19','FlatSingleSided',''),
    ('20','Highlighter',''),
    ('21','HyperGrid',''),
    ('22','Hypercolor',''),
    ('23','HypercolorSingleSided',''),
    ('24','Icing',''),
    ('25','Ink',''),
    ('26','InkSingleSided',''),
    ('27','Leaves',''),
    ('28','LeavesSingleSided',''),
    ('29','Light',''),
    ('30','LightWire',''),
    ('31','Lofted',''),
    ('32','Marker',''),
    ('33','MatteHull',''),
    ('34','NeonPulse',''),
    ('35','OilPaint',''),
    ('36','OilPaintSingleSided',''),
    ('37','Paper',''),
    ('38','PaperSingleSided',''),
    ('39','Petal',''),
    ('40','Plasma',''),
    ('41','Rainbow',''),
    ('42','ShinyHull',''),
    ('43','Smoke',''),
    ('44','Snow',''),
    ('45','SoftHighlighter',''),
    ('46','Spikes',''),
    ('47','Splatter',''),
    ('48','SplatterSingleSided',''),
    ('49','Stars',''),
    ('50','Streamers',''),
    ('51','Taffy',''),
    ('52','TaperedFlat',''),
    ('53','TaperedFlatSingleSided',''),
    ('54','TaperedMarker',''),
    ('55','TaperedMarker_Flat',''),
    ('56','ThickPaint',''),
    ('57','ThickPaintSingleSided',''),
    ('58','Toon',''),
    ('59','UnlitHull',''),
    ('60','VelvetInk',''),
    ('61','Waveform',''),
    ('62','WetPaint',''),
    ('63','WetPaintSingleSided',''),
    ('64','WigglyGraphite',''),
    ('65','WigglyGraphiteSingleSided',''),
    ('66','Wire','')
]

class TILT_PT_Panel(Panel): 
    bl_idname = "TILT_PT_Panel"
    bl_label = "Tilt Tools Panel"
    bl_category = "Tiltbrush Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    def draw(self, context): # this draws the control
        layout = self.layout
        scene = context.scene
        row = layout.row()

        #
        layout.label(text="Strokes:")
        row = layout.row()
        row.template_list("TILT_STROKE_UL_List", "Stroke_List", scene, "stroke_list", scene, "selected_stroke_list_index")
        row = layout.row()
        #row.operator('stroke_list.new_item', icon='ADD') # just add strokes with a button
        row.operator('stroke_list.delete_item', icon='REMOVE')
        row.operator('stroke_list.move_item', icon='TRIA_UP').direction = 'UP'
        row.operator('stroke_list.move_item', icon='TRIA_DOWN').direction = 'DOWN'

        row = layout.row()
        row.operator('stroke_list.new_item', text="Create Stroke From Selection")

        layout.label(text="Selected Stroke Properies:")
        if scene.selected_stroke_list_index >= 0 and scene.stroke_list: 
            item = scene.stroke_list[scene.selected_stroke_list_index]
            row = layout.row()
            row.prop(item, "stroke_name")  # make this a one time setting
            row = layout.row()
            row.prop(item, "brush_tuple")
            row = layout.row()
            row.prop(item, "brush_size")
            row = layout.row()
            row.prop(item, "brush_color")
            row = layout.row()

        row = layout.row()
        row.operator('view3d.generate_sketch_file', text="Generate Sketch File")

class TILT_PT_StrokeDefaultPropertiesSubPanel(bpy.types.Panel):
    bl_label = "Stroke Default Properties"
    bl_idname = "TILT_PT_SubPanel"
    bl_parent_id = 'TILT_PT_Panel'
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        # XXX: make this section collapsable
        layout.label(text="Default Stroke Properties:")
        row = layout.row()
        stroke_property_defaults = scene.stroke_property_defaults
        row.prop(stroke_property_defaults, "default_brush")
        row = layout.row()
        row.prop(stroke_property_defaults, "default_brush_size")
        row = layout.row()
        row.prop(stroke_property_defaults, "default_brush_color")

class StrokePropertyDefaults(PropertyGroup):
    """The properties used to control strokes in scene""" 
    default_brush = bpy.props.EnumProperty(items=BRUSH_ITEMS, name = "Default Brush")
    default_brush_color = bpy.props.FloatVectorProperty(name='Default Colour', subtype='COLOR', default=(0.5,0.5,0.9))
    default_brush_size = bpy.props.FloatProperty(name="Default Brush Size", default=0.2)

class StrokeListItem(PropertyGroup): 
    """Group of properties representing an item in the list.""" 

    stroke_name = StringProperty(name="Name", description="A name for this stroke", default="Stroke") 
    brush_tuple = bpy.props.EnumProperty(items=BRUSH_ITEMS, name = "Brush")
    brush_color = bpy.props.FloatVectorProperty(name='Colour', subtype='COLOR', default=(0.5,0.5,0.9))
    brush_size = bpy.props.FloatProperty(name="Brush Size", default=0.2)

    # We use a mesh to store the vertices which represent control points. This is because 
    # this is the most optimal storage container for this use-case.

    control_pt_mesh_ptr = PointerProperty(name = "", type = bpy.types.Mesh)

class TILT_STROKE_UL_List(UIList):
    """A UI list that contains our stroke items."""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index): 
        # We could write some code to decide which icon to use here... 
        custom_icon = 'CURVE_DATA' 
        # Make sure your code supports all 3 layout types 
        if self.layout_type in {'DEFAULT', 'COMPACT'}: 
            layout.label(text=item.stroke_name, icon = custom_icon) 
        elif self.layout_type in {'GRID'}: 
            layout.alignment = 'CENTER' 
            layout.label(text="", icon = custom_icon) 

class TILT_STROKE_LIST_OT_NewItem(Operator): 
    """Add a new item to the list.""" 
    bl_idname = "stroke_list.new_item" 
    bl_label = "" # Add a new stroke to the list 
    
    #
    # Add the selected vertices here
    #
    def execute(self, context): 

        obj = bpy.context.object
        if obj.mode != 'EDIT':
            msg = "Object is not in edit mode."
            bpy.ops.message.tiltmessagebox('INVOKE_DEFAULT', message = msg)
            return {'FINISHED'}

        scene = context.scene
        scene.stroke_list.add() 
        new_stroke = scene.stroke_list[-1]
        scene.selected_stroke_list_index = len(scene.stroke_list) - 1
        stroke_property_defaults = scene.stroke_property_defaults
        new_stroke.stroke_name = "Stroke " + str(scene.stroke_counter)
        new_stroke.brush_tuple = stroke_property_defaults.default_brush
        new_stroke.brush_color = stroke_property_defaults.default_brush_color
        new_stroke.brush_size = stroke_property_defaults.default_brush_size
        scene.stroke_counter += 1
        bpy.ops.view3d.add_stroke_control_points('EXEC_DEFAULT') # add the selected vertices
        return{'FINISHED'}

class TILT_STROKE_LIST_OT_DeleteItem(Operator): 
    """Delete the selected stroke item from the list."""
    bl_idname = "stroke_list.delete_item"
    bl_label = "" # Deletes a stroke item 

    @classmethod 
    def poll(cls, context): 
        return context.scene.stroke_list
    
    def execute(self, context): 
        stroke_list = context.scene.stroke_list
        index = context.scene.selected_stroke_list_index
        stroke_list.remove(index)
        context.scene.selected_stroke_list_index = min(max(0, index - 1), len(stroke_list) - 1) 
        return{'FINISHED'}

class TILT_STROKE_LIST_OT_MoveItem(Operator):
    """Move an item in the list."""
    bl_idname = "stroke_list.move_item"
    bl_label = "" # Move an item in the list
    direction = bpy.props.EnumProperty(items=(('UP', 'Up', ""), ('DOWN', 'Down', ""),))
    
    @classmethod
    def poll(cls, context):
        return context.scene.stroke_list
    
    def move_index(self):
        """ Move index of an item render queue while clamping it. """
        index = bpy.context.scene.selected_stroke_list_index
        list_length = len(bpy.context.scene.stroke_list) - 1 # (index starts at 0)
        new_index = index + (-1 if self.direction == 'UP' else 1) 
        bpy.context.scene.selected_stroke_list_index = max(0, min(new_index, list_length))
    
    def execute(self, context):
        stroke_list = context.scene.stroke_list
        index = context.scene.selected_stroke_list_index
        neighbor = index + (-1 if self.direction == 'UP' else 1)
        stroke_list.move(neighbor, index)
        self.move_index() 
        return{'FINISHED'}