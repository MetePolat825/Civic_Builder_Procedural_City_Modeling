import bpy
import os
import math
import webbrowser

# Ensure everything is unregistered before registering again
if "bpy" in locals():
    import importlib
    if "register" in locals():
        unregister()
        print("Unregistered successfully!")
    importlib.reload(bpy)

# Custom operator to handle extrusion of buildings
class OBJECT_OT_ExtrudeBuilding(bpy.types.Operator):
    bl_idname = "object.extrude_building"
    bl_label = "Extrude Building"
    
    def execute(self, context):
        building_height = bpy.context.scene.building_height
        obj = context.active_object
        
        # Check if an object is selected and ensure it's a mesh
        if obj and obj.type == 'MESH':
            # Switch to edit mode and select all polygons (faces)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')  # Select all faces

            # Apply extrusion tool
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

            # Get texture paths from the scene properties or fallback to default
            roof_texture_path = context.scene.roof_texture_path or os.path.join(media_directory, "roof.jpg")
            wall_texture_path = context.scene.wall_texture_path or os.path.join(media_directory, "wall.jpg")
            imagery_texture_path = context.scene.imagery_texture_path or os.path.join(media_directory, "imagery.jpg")
            
            # Check if the files exist at the given path
            if not os.path.exists(roof_texture_path):
                self.report({'ERROR'}, f"Roof texture not found: {roof_texture_path}")
                return {'CANCELLED'}
            if not os.path.exists(wall_texture_path):
                self.report({'ERROR'}, f"Wall texture not found: {wall_texture_path}")
                return {'CANCELLED'}
            if not os.path.exists(imagery_texture_path):
                self.report({'ERROR'}, f"Imagery texture not found: {imagery_texture_path}")
                return {'CANCELLED'}
            
            # Load textures
            roof_texture = bpy.data.images.load(roof_texture_path)
            wall_texture = bpy.data.images.load(wall_texture_path)
            imagery_texture = bpy.data.images.load(imagery_texture_path)

            # Create materials for roof, wall, and imagery
            roof_material = bpy.data.materials.new(name="RoofMaterial")
            wall_material = bpy.data.materials.new(name="WallMaterial")
            imagery_material = bpy.data.materials.new(name="ImageryMaterial")
            
            roof_material_index = obj.data.materials.find(roof_material.name)
            wall_material_index = obj.data.materials.find(roof_material.name)
            imagery_material_index = obj.data.materials.find(roof_material.name)                        

            # Set up the Principled BSDF for all materials
            roof_material.use_nodes = True
            wall_material.use_nodes = True
            imagery_material.use_nodes = True

            roof_bsdf = roof_material.node_tree.nodes["Principled BSDF"]
            wall_bsdf = wall_material.node_tree.nodes["Principled BSDF"]
            imagery_bsdf = imagery_material.node_tree.nodes["Principled BSDF"]

            roof_texture_node = roof_material.node_tree.nodes.new(type='ShaderNodeTexImage')
            wall_texture_node = wall_material.node_tree.nodes.new(type='ShaderNodeTexImage')
            imagery_texture_node = imagery_material.node_tree.nodes.new(type='ShaderNodeTexImage')

            roof_texture_node.image = roof_texture
            wall_texture_node.image = wall_texture
            imagery_texture_node.image = imagery_texture

            # Set roughness to 1.0 for all materials
            roof_bsdf.inputs["Roughness"].default_value = 1.0
            wall_bsdf.inputs["Roughness"].default_value = 1.0
            imagery_bsdf.inputs["Roughness"].default_value = 1.0

            # Connect the texture to the BSDF's Base Color for each material
            roof_material.node_tree.links.new(roof_texture_node.outputs["Color"], roof_bsdf.inputs["Base Color"])
            wall_material.node_tree.links.new(wall_texture_node.outputs["Color"], wall_bsdf.inputs["Base Color"])
            imagery_material.node_tree.links.new(imagery_texture_node.outputs["Color"], imagery_bsdf.inputs["Base Color"])

            # Add the materials to the object
            obj.data.materials.append(roof_material)
            obj.data.materials.append(wall_material)
            obj.data.materials.append(imagery_material)

           # Loop through all the faces and assign textures based on the face's normal and object name
            for face in obj.data.polygons:
                # Get the normal vector of the face
                normal = face.normal
                
                # Check if the object name contains "imagery" or "footprint"
                if "imagery" in obj.name.lower():
                    # Assign the imagery material to all faces of imagery objects
                    face.material_index = 2  # Imagery material is index 2
                elif "footprint" in obj.name.lower():
                    # Assign the footprint material based on the face normal for footprint objects
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
        
# Custom operator for regenerating UVs with Cube Projection (Roof)
class OBJECT_OT_RegenerateRoofUVs(bpy.types.Operator):
    bl_idname = "object.regenerate_roof_uvs"
    bl_label = "Regenerate Roof UVs (Cube Projection)"

    def execute(self, context):
        obj = context.active_object
        roof_scale = context.scene.roof_uv_scale
        
        # Check if an object is selected and it's a mesh
        if obj and obj.type == 'MESH':
            # Switch to edit mode and select all faces
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')

            # Apply Cube Projection for the roof faces
            bpy.ops.uv.cube_project(cube_size=roof_scale)

            # Return to object mode
            bpy.ops.object.mode_set(mode='OBJECT')
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "No mesh object selected.")
            return {'CANCELLED'}

# Custom operator for regenerating UVs with Cube Projection (Wall)
class OBJECT_OT_RegenerateWallUVs(bpy.types.Operator):
    bl_idname = "object.regenerate_wall_uvs"
    bl_label = "Regenerate Wall UVs (Cube Projection)"

    def execute(self, context):
        obj = context.active_object
        wall_scale = context.scene.wall_uv_scale
        
        # Check if an object is selected and it's a mesh
        if obj and obj.type == 'MESH':
            # Switch to edit mode and select all faces
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')

            # Apply Cube Projection for the wall faces
            bpy.ops.uv.cube_project(cube_size=wall_scale)

            # Return to object mode
            bpy.ops.object.mode_set(mode='OBJECT')
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "No mesh object selected.")
            return {'CANCELLED'}
        
# Custom operator for regenerating UVs with Cube Projection (Wall)
class OBJECT_OT_RegenerateImageryUVs(bpy.types.Operator):
    bl_idname = "object.regenerate_imagery_uvs"
    bl_label = "Regenerate Imagery UVs (Cube Projection)"

    def execute(self, context):
        obj = context.active_object
        wall_scale = context.scene.wall_uv_scale
        
        # Check if an object is selected and it's a mesh
        if obj and obj.type == 'MESH':
            # Switch to edit mode and select all faces
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')

            # Apply Cube Projection for the imagery faces
            bpy.ops.uv.cube_project(cube_size=640)
            
            bpy.ops.uv.muv_flip_rotate_uv(seams=True, flip = True)

            # Return to object mode
            bpy.ops.object.mode_set(mode='OBJECT')
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "No mesh object selected.")
            return {'CANCELLED'}


# Custom operator for importing footprints .obj file
class OBJECT_OT_ImportFootprintObj(bpy.types.Operator):
    bl_idname = "object.import_footprint_obj"
    bl_label = "Import Footprint .obj File"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        try:
            bpy.ops.wm.obj_import(filepath=self.filepath)
            self.report({'INFO'}, f"Imported footprint .obj file: {self.filepath}")
            
            # Get the active object (the one that was imported)
            obj = context.active_object
            
            # Ensure the object exists and is a mesh
            if obj and obj.type == 'MESH':
                # Apply rotation of 90 degrees on the X-axis
                obj.rotation_euler[0] += math.radians(90)  # Rotate by 90 degrees on the X-axis
                self.report({'INFO'}, "Footprint import .obj rotated by 90 degrees on X-axis.")   
                
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error importing footprint .obj file: {str(e)}")
            return {'CANCELLED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# Custom operator for importing imagery .obj file
class OBJECT_OT_ImportImageryObj(bpy.types.Operator):
    bl_idname = "object.import_imagery_obj"
    bl_label = "Import Imagery .obj File"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        try:
            bpy.ops.wm.obj_import(filepath=self.filepath)
            self.report({'INFO'}, f"Imported imagery .obj file: {self.filepath}")
            
            # Get the active object (the one that was imported)
            obj = context.active_object
            
            # Ensure the object exists and is a mesh
            if obj and obj.type == 'MESH':
                # Apply rotation of 90 degrees on the X-axis
                obj.rotation_euler[0] += math.radians(90)  # Rotate by 90 degrees on the X-axis
                self.report({'INFO'}, "Imagery polygon import .obj rotated by 90 degrees on X-axis.") 
                
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error importing imagery .obj file: {str(e)}")
            return {'CANCELLED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
# Operator to open the local documentation
class OBJECT_OT_OpenDocumentation(bpy.types.Operator):
    bl_idname = "object.open_documentation"
    bl_label = "Open Documentation"
    
    def execute(self, context):
        # Define the path to your local documentation file
        doc_path = r"C:\Users\Prometheus\Desktop\ARU\Yr3 - Major Project\CivicBuilder Development\Civic_Builder_Procedural_City_Modeling\documentation\index.html"
        
        # Check if the file exists
        if os.path.exists(doc_path):
            webbrowser.open(f"file://{doc_path}")
            self.report({'INFO'}, "Opening documentation.")
        else:
            self.report({'ERROR'}, f"Documentation not found at {doc_path}.")
        
        return {'FINISHED'}
    
# Custom panel to organize UI elements
class OBJECT_PT_BuildingTools(bpy.types.Panel):
    bl_idname = "OBJECT_PT_building_tools"
    bl_label = "Civic Builder Blender"
    bl_category = "Civic Builder"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    def draw(self, context):
        layout = self.layout
        
        # Import Footprint Panel
        box = layout.box()
        box.label(text="Import Footprint Geometry:")
        box.operator("object.import_footprint_obj", icon="IMPORT")

        # Import Imagery Panel
        box = layout.box()
        box.label(text="Import Imagery Geometry:")
        box.operator("object.import_imagery_obj", icon="IMPORT")
        
        # Set Paths Panel
        box = layout.box()
        box.label(text="Set Texture Paths:")
        box.prop(context.scene, "roof_texture_path", icon = "FILE_IMAGE")
        box.prop(context.scene, "wall_texture_path", icon = "FILE_IMAGE")
        box.prop(context.scene, "imagery_texture_path", icon = "FILE_IMAGE")
        
        # User Parameters Panel
        box = layout.box()
        box.label(text="User Parameters:")
        box.prop(context.scene, "building_height")
        box.prop(context.scene, "roof_uv_scale", text="Roof UV Scale")
        box.prop(context.scene, "wall_uv_scale", text="Wall UV Scale")
        
        # Generation Panel
        box = layout.box()
        box.label(text="Geometry Generation:")
        row = box.row()
        row.operator("object.extrude_building", icon = "MESH_CUBE")
        row.operator("object.apply_textures", icon = "MESH_CUBE")
        
        # UV Regeneration Panel
        box = layout.box()
        box.label(text="Regenerate UV Mapping:")
        row = box.row()
        box.operator("object.regenerate_roof_uvs", text="Regenerate Roof UVs", icon = "UV")
        box.operator("object.regenerate_wall_uvs", text="Regenerate Wall UVs", icon = "UV")
        box.operator("object.regenerate_imagery_uvs", text="Regenerate Imagery UVs", icon = "UV")

        # Help Button
        box = layout.box()
        box.label(text="Help and Documentation:")
        box.operator("object.open_documentation", icon="HELP")


# Register all the operators and panels
def register():
        
        
    bpy.utils.register_class(OBJECT_PT_BuildingTools)
    bpy.utils.register_class(OBJECT_OT_ImportFootprintObj)
    bpy.utils.register_class(OBJECT_OT_ImportImageryObj)
    bpy.utils.register_class(OBJECT_OT_ExtrudeBuilding)
    bpy.utils.register_class(OBJECT_OT_ApplyTextures)
    bpy.utils.register_class(OBJECT_OT_RegenerateRoofUVs)
    bpy.utils.register_class(OBJECT_OT_RegenerateWallUVs)
    bpy.utils.register_class(OBJECT_OT_RegenerateImageryUVs)    
    bpy.utils.register_class(OBJECT_OT_OpenDocumentation)

            
    # Add properties
    bpy.types.Scene.building_height = bpy.props.FloatProperty(name="Building Height", default=25.0)
    bpy.types.Scene.roof_texture_path = bpy.props.StringProperty(name="Roof Texture", subtype="FILE_PATH")
    bpy.types.Scene.wall_texture_path = bpy.props.StringProperty(name="Wall Texture", subtype="FILE_PATH")
    bpy.types.Scene.imagery_texture_path = bpy.props.StringProperty(name="Imagery Texture", subtype="FILE_PATH")
    bpy.types.Scene.roof_uv_scale = bpy.props.FloatProperty(name="Roof UV Scale", default=40.0)
    bpy.types.Scene.wall_uv_scale = bpy.props.FloatProperty(name="Wall UV Scale", default=40.0)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_ExtrudeBuilding)
    bpy.utils.unregister_class(OBJECT_OT_ApplyTextures)
    bpy.utils.unregister_class(OBJECT_OT_RegenerateRoofUVs)
    bpy.utils.unregister_class(OBJECT_OT_RegenerateWallUVs)
    bpy.utils.unregister_class(OBJECT_OT_RegenerateImageryUVs)
    bpy.utils.unregister_class(OBJECT_OT_ImportFootprintObj)
    bpy.utils.unregister_class(OBJECT_OT_ImportImageryObj)
    bpy.utils.unregister_class(OBJECT_PT_BuildingTools)
    bpy.utils.unregister_class(OBJECT_OT_OpenDocumentation)

    del bpy.types.Scene.building_height
    del bpy.types.Scene.roof_texture_path
    del bpy.types.Scene.wall_texture_path
    del bpy.types.Scene.imagery_texture_path
    del bpy.types.Scene.roof_uv_scale
    del bpy.types.Scene.wall_uv_scale

if __name__ == "__main__":
    register()
