import bpy
import os
import math

# Custom operator to handle extrusion of buildings
class OBJECT_OT_ExtrudeBuilding(bpy.types.Operator):
    bl_idname = "object.extrude_building"
    bl_label = "Extrude Building"
    
    def execute(self, context):
        building_height = context.scene.building_height
        obj = context.active_object
        
        # Check if an object is selected and ensure it's a mesh
        if obj and obj.type == 'MESH':
            # Switch to edit mode and select all polygons (faces)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')  # Select all faces

            # Apply extrusion tool (no rotation here)
            bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, 0, building_height)})  # Extrude along the Z axis
            
            # Return to object mode
            bpy.ops.object.mode_set(mode='OBJECT')
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "No mesh object selected.")
            return {'CANCELLED'}

# Custom operator to apply textures based on face orientation
class OBJECT_OT_ApplyTextures(bpy.types.Operator):
    bl_idname = "object.apply_textures"
    bl_label = "Apply Textures"

    def execute(self, context):
        obj = context.active_object
        
        # Check if an object is selected and it's a mesh
        if obj and obj.type == 'MESH':
            # Ensure the object is in object mode
            bpy.ops.object.mode_set(mode='OBJECT')

            # Get the path for textures (assuming the "media" folder is in the same directory as the Blender file)
            blend_directory = bpy.path.abspath("//")  # Path to current .blend file
            media_directory = os.path.join(blend_directory, "media")

            # Print to check the actual paths being used
            print("Blend Directory:", blend_directory)
            print("Media Directory:", media_directory)

            # Check if the files exist at the given path
            roof_texture_path = os.path.join(media_directory, "roof.jpg")
            wall_texture_path = os.path.join(media_directory, "wall.jpg")
            
            if not os.path.exists(roof_texture_path):
                self.report({'ERROR'}, f"Roof texture not found: {roof_texture_path}")
                return {'CANCELLED'}
            if not os.path.exists(wall_texture_path):
                self.report({'ERROR'}, f"Wall texture not found: {wall_texture_path}")
                return {'CANCELLED'}

            # Load textures
            roof_texture = bpy.data.images.load(roof_texture_path)
            wall_texture = bpy.data.images.load(wall_texture_path)

            # Create materials for roof and wall textures
            roof_material = bpy.data.materials.new(name="RoofMaterial")
            wall_material = bpy.data.materials.new(name="WallMaterial")

            roof_material.use_nodes = True
            wall_material.use_nodes = True

            # Set up the Principled BSDF for both materials
            roof_bsdf = roof_material.node_tree.nodes["Principled BSDF"]
            wall_bsdf = wall_material.node_tree.nodes["Principled BSDF"]

            roof_texture_node = roof_material.node_tree.nodes.new(type='ShaderNodeTexImage')
            wall_texture_node = wall_material.node_tree.nodes.new(type='ShaderNodeTexImage')

            roof_texture_node.image = roof_texture
            wall_texture_node.image = wall_texture

            # Connect the texture to the BSDF's Base Color
            roof_material.node_tree.links.new(roof_texture_node.outputs["Color"], roof_bsdf.inputs["Base Color"])
            wall_material.node_tree.links.new(wall_texture_node.outputs["Color"], wall_bsdf.inputs["Base Color"])

            # Add the materials to the object
            obj.data.materials.append(roof_material)
            obj.data.materials.append(wall_material)

            # Loop through all the faces and assign textures based on the face's normal
            for face in obj.data.polygons:
                # Get the normal vector of the face
                normal = face.normal

                # If the normal is close to pointing upwards (Z-axis), assign the roof texture
                if abs(normal.z) > 0.9:
                    # Assign the roof material to this face
                    face.material_index = 0  # The first material (index 0) is the roof material
                else:
                    # Assign the wall material to this face
                    face.material_index = 1  # The second material (index 1) is the wall material

            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "No mesh object selected.")
            return {'CANCELLED'}

# Custom operator to rotate the imported footprint by 90 degrees on the X-axis
class OBJECT_OT_RotateFootprint(bpy.types.Operator):
    bl_idname = "object.rotate_footprint"
    bl_label = "Rotate Footprint 90° X-axis"

    def execute(self, context):
        obj = context.active_object
        
        # Ensure an object is selected and it's a mesh
        if obj and obj.type == 'MESH':
            # Rotate the object by 90 degrees on the X-axis
            obj.rotation_euler[0] += math.radians(90)  # Corrected to use math.radians()
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "No mesh object selected.")
            return {'CANCELLED'}

# Custom operator for regenerating UVs with Cube Projection
class OBJECT_OT_RegenerateUVs(bpy.types.Operator):
    bl_idname = "object.regenerate_uvs"
    bl_label = "Regenerate UVs (Cube Projection)"

    def execute(self, context):
        obj = context.active_object
        
        # Check if an object is selected and it's a mesh
        if obj and obj.type == 'MESH':
            # Switch to edit mode and select all faces
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')

            # Apply Cube Projection for roof and wall UVs separately with user-controlled scale
            roof_scale = context.scene.roof_uv_scale
            wall_scale = context.scene.wall_uv_scale
            
            # Apply Cube Projection for the roof faces
            bpy.ops.uv.cube_project(scale_to_bounds=True)
            bpy.ops.object.mode_set(mode='OBJECT')  # Switch to object mode to allow access to the UV editor

            # Switch to UV Editing mode and scale the UVs based on the user input
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.transform.resize(value=(roof_scale, roof_scale, 1))  # Scale UVs for roof faces
            bpy.ops.object.mode_set(mode='OBJECT')  # Return to object mode

            # Apply Cube Projection for the wall faces
            bpy.ops.uv.cube_project(scale_to_bounds=True)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.transform.resize(value=(wall_scale, wall_scale, 1))  # Scale UVs for wall faces
            bpy.ops.object.mode_set(mode='OBJECT')  # Return to object mode

            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "No mesh object selected.")
            return {'CANCELLED'}

# Panel for the Civic Builder UI
class CivicBuilderPanel(bpy.types.Panel):
    bl_label = "Civic Builder"
    bl_idname = "OBJECT_PT_civic_builder"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Civic Builder'

    def draw(self, context):
        layout = self.layout

        # Button to import .obj file
        layout.operator("object.import_obj", text="Import .obj File")

        # Add a button to rotate the imported object by 90 degrees on the X-axis
        layout.operator("object.rotate_footprint", text="Rotate Footprint 90° X-axis")

        # Height control for extrusion
        layout.prop(context.scene, "building_height", text="Building Height")

        # Button to extrude the building
        layout.operator("object.extrude_building", text="Extrude Building")

        # Button to apply textures
        layout.operator("object.apply_textures", text="Apply Textures")

        # UV Scale control for Roof
        layout.label(text="Roof UV Scale")
        layout.prop(context.scene, "roof_uv_scale", text="Roof Scale")

        # UV Scale control for Wall
        layout.label(text="Wall UV Scale")
        layout.prop(context.scene, "wall_uv_scale", text="Wall Scale")

        # Button to regenerate UVs
        layout.operator("object.regenerate_uvs", text="Regenerate UVs (Cube Projection)")

# Register and unregister functions to handle custom properties and operators
def register():
    bpy.utils.register_class(OBJECT_OT_ExtrudeBuilding)
    bpy.utils.register_class(OBJECT_OT_ApplyTextures)
    bpy.utils.register_class(OBJECT_OT_RotateFootprint)
    bpy.utils.register_class(OBJECT_OT_RegenerateUVs)
    bpy.utils.register_class(CivicBuilderPanel)
    bpy.utils.register_class(OBJECT_OT_ImportObj)

    bpy.types.Scene.building_height = bpy.props.FloatProperty(name="Building Height", default=10.0, min=0.0, step=0.1)
    bpy.types.Scene.roof_uv_scale = bpy.props.FloatProperty(name="Roof UV Scale", default=10.0, min=0.1, max=50.0, step=0.1)
    bpy.types.Scene.wall_uv_scale = bpy.props.FloatProperty(name="Wall UV Scale", default=10.0, min=0.1, max=50.0, step=0.1)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_ExtrudeBuilding)
    bpy.utils.unregister_class(OBJECT_OT_ApplyTextures)
    bpy.utils.unregister_class(OBJECT_OT_RotateFootprint)
    bpy.utils.unregister_class(OBJECT_OT_RegenerateUVs)
    bpy.utils.unregister_class(CivicBuilderPanel)
    bpy.utils.unregister_class(OBJECT_OT_ImportObj)

    del bpy.types.Scene.building_height
    del bpy.types.Scene.roof_uv_scale
    del bpy.types.Scene.wall_uv_scale


if __name__ == "__main__":
    register()
