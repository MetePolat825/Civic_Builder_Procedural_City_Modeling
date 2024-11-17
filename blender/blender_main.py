bl_info = {
    "name": "Civic Builder",
    "blender": (4, 0, 1),  # Set to your target Blender version
    "category": "Object",
}

import bpy
import os

# Operator for importing .obj files
class ImportOBJOperator(bpy.types.Operator):
    bl_idname = "object.import_obj"
    bl_label = "Import Building Footprint"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        # Import .obj file logic
        bpy.ops.import_scene.obj(filepath=self.filepath)
        return {'FINISHED'}

# Operator for extrusion and height control
class ExtrudeHeightOperator(bpy.types.Operator):
    bl_idname = "object.extrude_building"
    bl_label = "Extrude Building Height"

    height: bpy.props.FloatProperty(name="Height", default=10.0, min=0.1)

    def execute(self, context):
        # Extrude logic
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                # Extrude the selected object based on the height property
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, 0, self.height)})
                bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}

# Operator for applying texture
class ApplyTextureOperator(bpy.types.Operator):
    bl_idname = "object.apply_textures"
    bl_label = "Apply Textures"

    def execute(self, context):
        # Apply texture to walls and roof of the building
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                # Apply texture to walls (extruded faces)
                material = bpy.data.materials.new(name="BuildingMaterial")
                material.use_nodes = True
                bsdf = material.node_tree.nodes["Principled BSDF"]
                # Set a texture node (you can load an image here)
                texture = material.node_tree.nodes.new('ShaderNodeTexImage')
                texture.image = bpy.data.images.load("path/to/your/texture.jpg")
                material.node_tree.links.new(bsdf.inputs['Base Color'], texture.outputs['Color'])

                # Assign material to the object
                if obj.data.materials:
                    obj.data.materials[0] = material
                else:
                    obj.data.materials.append(material)

                # You can add more logic for different faces (roof, walls, etc.)

        return {'FINISHED'}

# Panel to control the plugin's functionality
class CivicBuilderPanel(bpy.types.Panel):
    bl_label = "Civic Builder"
    bl_idname = "OBJECT_PT_civic_builder"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Civic Builder'

    def draw(self, context):
        layout = self.layout

        # File import button
        layout.operator("object.import_obj", text="Import .obj File")

        # Height control
        layout.prop(context.scene, "building_height")
        layout.operator("object.extrude_building", text="Extrude Buildings")

        # Apply textures button
        layout.operator("object.apply_textures", text="Apply Textures")


# Register and unregister classes
def register():
    bpy.utils.register_class(ImportOBJOperator)
    bpy.utils.register_class(ExtrudeHeightOperator)
    bpy.utils.register_class(ApplyTextureOperator)
    bpy.utils.register_class(CivicBuilderPanel)
    bpy.types.Scene.building_height = bpy.props.FloatProperty(name="Building Height", default=10.0, min=0.1)

def unregister():
    bpy.utils.unregister_class(ImportOBJOperator)
    bpy.utils.unregister_class(ExtrudeHeightOperator)
    bpy.utils.unregister_class(ApplyTextureOperator)
    bpy.utils.unregister_class(CivicBuilderPanel)
    del bpy.types.Scene.building_height


if __name__ == "__main__":
    register()
