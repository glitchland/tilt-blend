import bpy 
import numpy
import bmesh

import os 
import sys 

# Make the tiltbrush submodule accessible for code imports
# copy into zip for release
lib_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(lib_path)

#lib_path = os.path.abspath(os.path.join(__file__, '..', 'tilt-brush-toolkit', 'Python'))
#sys.path.append(lib_path)

#lib_path = os.path.abspath(os.path.join(__file__))
#sys.path.append(lib_path)

from tilted import Sketch
from tilted import Stroke
from tilted import ControlPoint
from tilted import MetaDataFile
from tilted import TiltThumbnailPNG
from tilted import TiltHeader
from tilted import TiltArchive

# TODO: Preserve order of selected vertices

STROKE_EXT_FLAGS = 'flags'
STROKE_EXT_SCALE = 'scale'
STROKE_EXT_GROUP = 'group'
STROKE_EXT_SEED  = 'seed'

# XXX expose these settings
STROKE_MASK = 11       # flags, scale, seed
STROKE_FLAGS = 0
STROKE_SCALE = 0.5
STROKE_SEED = 859071859
CONTROL_POINT_MASK = 3 # pressure, timestamp 
CONTROL_POINT_PRESSURE = 1.0

class TILT_OT_Sketch_Operator(bpy.types.Operator):
    bl_idname = "view3d.generate_sketch_file"
    bl_label = "Generate Sketch File"
    bl_description = "Generate a sketch file from vertex data"

    def execute(self, context):
        scene = context.scene

        # pass the objects into the tiltarchive object, with checks on the handler methods

        #
        # Make the directory to hold our tild data
        #
        tilt_archive = TiltArchive()

        #
        # Make the header.bin
        #
        header = TiltHeader()
        hdr_data = header.getData()
        tilt_archive.write_header(hdr_data)

        #
        # Make the sketch.data
        #
        my_sketch = Sketch()

        # iterate over all of the strokes in the scene
        for i in range(len(scene.stroke_list)):
            brush_index  = int(scene.stroke_list[i].brush_tuple[0])  # the index into guid arr
            r = scene.stroke_list[i].brush_color[0] 
            g = scene.stroke_list[i].brush_color[1] 
            b = scene.stroke_list[i].brush_color[2] 
            a = 1.0 # XXX allow user to configure alpha
            stroke_color = [r, g, b, a] # RGBA color, as 4 floats in the range [0, 1]
            stroke_size  = scene.stroke_list[i].brush_size # Brush size, in decimeters, as a float. (multiplied by scale)
            stroke_extensions = [STROKE_FLAGS, STROKE_SCALE, STROKE_SEED]
            stroke = Stroke(brush_index, stroke_color, stroke_size, STROKE_MASK, CONTROL_POINT_MASK, stroke_extensions)
            my_sketch.add_stroke(stroke)

            time_counter = 0
            for mesh_vertices in scene.stroke_list[i].control_pt_mesh_ptr.vertices: # MeshVertices container (check if this has multiple)
                pos = mesh_vertices.co     #XXX probably need to massage this data
                rot = [0.0, 0.0, 0.0, 1.0] #XXX allow user to control rotation, but default to quaternion identity for now
                ext_pressure = CONTROL_POINT_PRESSURE
                ext_time = time_counter
                extensions = [CONTROL_POINT_PRESSURE, ext_time]
                my_sketch.add_control_point_to_stroke(i, pos, rot, extensions)
                time_counter += 1

        sketch_bin_data = my_sketch.pack()
        sketch_file_array = bytearray(sketch_bin_data)
        tilt_archive.write_sketch(sketch_bin_data)

        #
        # Make the metadata JSON
        #
        metadata = MetaDataFile()
        metadata_json = metadata.get_metadata_json()
        print("metadata_json:", metadata_json)
        tilt_archive.write_metadata(metadata_json)

        #
        # Make the thimbnail PNG
        #
        png = TiltThumbnailPNG(50,50)
        r = [0,255,0]
        g = [255,255,255]
        b = [0,255,0]
        png_data = png.makeRGBPNG(r, g, b)

        tilt_archive.write_thumbnail(png_data)

        tilt_archive.finalize()

        msg = "Wrote the tilt file to: \n" + tilt_archive.get_filename()
        bpy.ops.message.tiltmessagebox('INVOKE_DEFAULT', message = msg)

        return {'FINISHED'}