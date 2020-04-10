import bpy 
import numpy
import bmesh

# TODO: Preserve order of selected vertices
# This operator adds selected vertices to a stroke.
class TILT_OT_Stroke_Operator(bpy.types.Operator):
    bl_idname = "view3d.add_stroke_control_points"
    bl_label = "Operator add vertices to stroke"
    bl_description = "This operator adds selected vertices to stroke, it is called from code not ui"

    def convertLocalToWorld(self, selected_object, vertice_array=[]):
        converted_verts = []
        for v in vertice_array:
            local_point = v.co
            world_point = selected_object.matrix_world @ v.co # matrix multiplication convert to world space
            converted_verts.append(world_point)
        return converted_verts

    def orderSelectedVerts(self, _bm, selected_object):
        _edges=[i for i in _bm.edges if i.select]
        edge=_edges[0]
        startvert=edge.verts[0]
        _edges.remove(edge)
        _orderedVerts=[]
        _orderedVerts.append(startvert)
        while len(_edges)>0:
            print("edges:", len(_edges))
            startvert=self.getNextVert(startvert, _edges)
            if startvert is not None:
                _orderedVerts.append(startvert)

        worldPositions = self.convertLocalToWorld(selected_object, _orderedVerts)
        return worldPositions

    def getNextVert(self, sv, _edges):
        for e in _edges:
            if e.verts[0]==sv or e.verts[1]==sv:
                if e.verts[0]==sv:
                    d=e.verts[1]
                else:
                    d=e.verts[0]
                _edges.remove(e)
                return d

  def execute(self, context):
        return self.invoke(context, None)    

    def invoke(self, context, event):
        scene = context.scene

        # preserve order
        selected_bm_verts = []
        if scene.stroke_list_index >= 0 and scene.stroke_list: 

            obj = bpy.context.object
            selected_object = bpy.context.active_object  
            # if we are in edit mode, get the selected vertices
            # and add them to the vertices array
            if obj.mode == 'EDIT':
                bm = bmesh.from_edit_mesh(obj.data)
                print("----")
                for h in bm.select_history:
                    if type(h) is bmesh.types.BMVert:
                        print("h position", h.co)
                        selected_bm_verts.append(h)
                print("----")                    
                translated_verts = self.convertLocalToWorld(selected_object, selected_bm_verts)
            else:
                msg = "Object is not in edit mode."
                bpy.ops.message.tiltmessagebox('INVOKE_DEFAULT', message = msg)
                return {'FINISHED'}
  
            # We use a mesh as a container to store the vertice
            # list collected above.
            m = bpy.data.meshes.new(name='mesh container to hold control points')
            m.from_pydata(vertices=translated_verts, edges=[], faces=[])

            selected_stroke = scene.stroke_list[scene.stroke_list_index]
            selected_stroke.control_pt_mesh_ptr = m

            print(selected_stroke.control_pt_mesh_ptr.vertices)

        return {'FINISHED'}