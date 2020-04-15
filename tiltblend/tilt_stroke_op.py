import bpy 
import numpy
import bmesh
  
# This operator adds vertices to a stroke using the start of a line.
"""
    def get_ordered_verts(self, bm, selected_object):
        edges = [i for i in bm.edges if i.select]
        edge = edges[0]
        start_vert = edge.verts[0]
        edges.remove(edge)
        ordered_verts=[]
        ordered_verts.append(start_vert)
        while len(edges) > 0:
            print("edges:", len(edges))
            start_vert = self.get_next_vertice(start_vert, edges)
            if start_vert is not None:
                ordered_verts.append(start_vert)

        translated_verts = shared_convertLocalToWorld(self, selected_object, ordered_verts)
        return translated_verts

    def get_next_vertice(self, start_vert, edges):
        for e in edges:
            if e.verts[0] == start_vert or e.verts[1] == start_vert:
                if e.verts[0] == start_vert:
                    d = e.verts[1]
                else:
                    d = e.verts[0]
                edges.remove(e)
                return d

    def get_edges_for_vertex(self, vertice_list, v_index, mesh, marked_edges):
        all_edges = [e for e in mesh.edges if v_index in e.vertices]
        print(all_edges)
        vertice_list.append(all_edges)
        unmarked_edges = [e for e in all_edges if e.index not in marked_edges]
        return unmarked_edges

    def get_connected_vertices(self, v_index, mesh, vertice_list, connected_verts, marked_edges, maxdepth=10, level=0):  
        if level >= maxdepth:
            return

        edges = self.get_edges_for_vertex(vertice_list, v_index, mesh, marked_edges)

        for e in edges:
            othr_v_index = [idx for idx in mesh.edges[e.index].vertices if idx != v_index][0]
            connected_verts[othr_v_index] = True
            marked_edges.append(e.index)
            self.get_connected_vertices(othr_v_index, mesh, vertice_list, connected_verts, marked_edges, maxdepth=maxdepth, level=level+1)
"""
class TILT_OT_Control_Points_From_Mesh_Line_Start_Operator(bpy.types.Operator):
    bl_idname = "view3d.get_control_points_from_mesh_line"
    bl_label = "Add control points from mesh line"
    bl_description = "Add control points by traversing points in mesh line"

    def execute(self, context):
        return self.invoke(context, None)  

    def invoke(self, context, event):
        scene = context.scene
        obj = bpy.context.object

        if obj.type != 'MESH':
            msg = "Only Meshes are supported at the moment."
            bpy.ops.message.tiltmessagebox('INVOKE_DEFAULT', message = msg)
            return {'FINISHED'}

        #
        line_vertices = []

        # Check the distance between verts, alert on greater than > threshold
        mesh = obj.data
        print("# of vertices=%d" % len(mesh.vertices))
        for vert in mesh.vertices:
            print( 'v X: %f Y: %f  Z:%f\n' % (vert.co.x, vert.co.y, vert.co.z) )
            line_vertices.append(vert.co)

        # these verts dont need to be translated
        m = bpy.data.meshes.new(name='mesh container to hold control points')
        m.from_pydata(vertices=line_vertices, edges=[], faces=[])

        selected_stroke = scene.stroke_list[scene.selected_stroke_list_index]
        selected_stroke.control_pt_mesh_ptr = m
        
        print(line_vertices)
        return {'FINISHED'}
      
# This operator adds selected vertices to a stroke.
class TILT_OT_Control_Points_From_Selected_Vertices_Operator(bpy.types.Operator):
    bl_idname = "view3d.get_control_points_from_selected_vertices"
    bl_label = "Operator add vertices to stroke"
    bl_description = "This operator adds selected vertices to stroke, it is called from code not ui"

    def convert_local_to_world(self, selected_object, vertice_array=[]):
        converted_verts = []
        for v in vertice_array:
            local_point = v.co
            world_point = selected_object.matrix_world @ local_point # matrix multiplication convert to world space
            converted_verts.append(world_point)
        return converted_verts
    
    def get_verts_from_selection_history(self, context):
        obj = bpy.context.object
        selected_object = bpy.context.active_object 
        selected_bm_verts = []

        bm = bmesh.from_edit_mesh(obj.data)
        print("----")
        for h in bm.select_history:
            if type(h) is bmesh.types.BMVert:
                print("h position", h.co)
                selected_bm_verts.append(h)
                print("----")                    
        
        translated_verts = self.convert_local_to_world(selected_object, selected_bm_verts)
        return translated_verts

    def execute(self, context):
        return self.invoke(context, None)    

    def invoke(self, context, event):
        scene = context.scene
        obj = bpy.context.object

        if obj.mode != 'EDIT':
            msg = "Object is not in edit mode."
            bpy.ops.message.tiltmessagebox('INVOKE_DEFAULT', message = msg)
            return {'FINISHED'}

        if obj.type != 'MESH':
            msg = "Only Meshes are supported at the moment. Try convert to mesh!"
            bpy.ops.message.tiltmessagebox('INVOKE_DEFAULT', message = msg)
            return {'FINISHED'}

        stroke_verts = self.get_verts_from_selection_history(context)
  
        # We use a mesh as a container to store the vertice
        # list collected above.
        m = bpy.data.meshes.new(name='mesh container to hold control points')
        m.from_pydata(vertices=stroke_verts, edges=[], faces=[])

        print("TEST:", scene.selected_stroke_list_index)
        selected_stroke = scene.stroke_list[scene.selected_stroke_list_index]
        selected_stroke.control_pt_mesh_ptr = m

        print(selected_stroke.control_pt_mesh_ptr.vertices)
        
        return {'FINISHED'}