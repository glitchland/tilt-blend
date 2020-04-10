# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "TiltBlend",
    "author" : "glitch",
    "description" : "Blender Tiltbrush Tools",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "View3D",
    "warning" : "",
    "category" : "Generic"
}

from . tilt_message_box_op import TILT_OT_MessageBox
from . tilt_stroke_op import TILT_OT_Stroke_Operator
from . tilt_sketch_op import TILT_OT_Sketch_Operator
from . tilt_panel import TILT_PT_Panel, TILT_PT_StrokeDefaultPropertiesSubPanel, StrokeListItem, StrokePropertyDefaults, TILT_STROKE_LIST_OT_NewItem, TILT_STROKE_LIST_OT_DeleteItem, TILT_STROKE_LIST_OT_MoveItem, TILT_STROKE_UL_List

import bpy 
from bpy.props import CollectionProperty, IntProperty, PointerProperty, StringProperty 

def register():
    bpy.utils.register_class(StrokeListItem) 
    bpy.utils.register_class(StrokePropertyDefaults)     
    bpy.utils.register_class(TILT_PT_Panel)
    bpy.utils.register_class(TILT_PT_StrokeDefaultPropertiesSubPanel)
    bpy.utils.register_class(TILT_OT_Sketch_Operator) # creates sketch file
    bpy.utils.register_class(TILT_OT_Stroke_Operator) # adds selected vertices to a stroke
    bpy.utils.register_class(TILT_STROKE_UL_List)     # a UI list that contains our StrokeListItems
    bpy.utils.register_class(TILT_STROKE_LIST_OT_NewItem)
    bpy.utils.register_class(TILT_STROKE_LIST_OT_DeleteItem)
    bpy.utils.register_class(TILT_STROKE_LIST_OT_MoveItem)
    bpy.utils.register_class(TILT_OT_MessageBox)

    # attach these items to the scene, this means they can be referenced easily
    # from different operator classes without having to pass them around.
    bpy.types.Scene.stroke_list = CollectionProperty(type = StrokeListItem)
    bpy.types.Scene.selected_stroke_list_index = IntProperty(name = "Index for selected stroke_list", default = 0)   
    bpy.types.Scene.stroke_counter = IntProperty(name = "Counts the number of strokes in scene", default = 0)   
    bpy.types.Scene.stroke_property_defaults = PointerProperty(name = "Stroke Property Defaults", type = StrokePropertyDefaults)

def unregister():
    del bpy.types.Scene.stroke_list
    del bpy.types.Scene.selected_stroke_list_index
    del bpy.types.Scene.stroke_counter    
    del bpy.types.Scene.stroke_property_defaults
    bpy.utils.unregister_class(StrokeListItem)
    bpy.utils.unregister_class(StrokePropertyDefaults)     
    bpy.utils.unregister_class(TILT_PT_Panel)
    bpy.utils.unregister_class(TILT_PT_StrokeDefaultPropertiesSubPanel)    
    bpy.utils.unregister_class(TILT_OT_Sketch_Operator)
    bpy.utils.unregister_class(TILT_OT_Stroke_Operator)   
    bpy.utils.unregister_class(TILT_STROKE_UL_List)
    bpy.utils.unregister_class(TILT_STROKE_LIST_OT_NewItem)
    bpy.utils.unregister_class(TILT_STROKE_LIST_OT_DeleteItem)
    bpy.utils.unregister_class(TILT_STROKE_LIST_OT_MoveItem)
    bpy.utils.unregister_class(TILT_OT_MessageBox)