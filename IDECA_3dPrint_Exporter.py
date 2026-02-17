bl_info = {
    "name": "IDECA_3dPrint_exporter",
    "author": "Roque & Gemini",
    "version": (1, 1),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > IDECA 3D",
    "description": "Herramientas de escala y exportación optimizada para impresión 3D",
    "category": "Import-Export",
}

import bpy
import os

# --- OPERADORES ---

class IDECA_OT_setup_units(bpy.types.Operator):
    bl_idname = "ideca.setup_units"
    bl_label = "1. Configurar Unidades (mm)"
    bl_description = "Ajusta la escena a milímetros y escala global a 0.001"
    
    def execute(self, context):
        scene = context.scene
        scene.unit_settings.system = 'METRIC'
        scene.unit_settings.scale_length = 0.001
        scene.unit_settings.length_unit = 'MILLIMETERS'
        self.report({'INFO'}, "IDECA: Unidades configuradas a mm")
        return {'FINISHED'}

class IDECA_OT_apply_dim(bpy.types.Operator):
    bl_idname = "ideca.apply_dimensions"
    bl_label = "2. Aplicar Dimensiones"
    bl_description = "Aplica dimensiones reales y resetea la escala a 1.0"
    
    def execute(self, context):
        obj = context.active_object
        scene = context.scene
        
        if obj and obj.type == 'MESH':
            if bpy.context.object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')

            # Reseteamos escala inicial
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            
            target_dims = [scene.ideca_dim_x, scene.ideca_dim_y, scene.ideca_dim_z]
            
            for i in range(3):
                current_dim = obj.dimensions[i]
                if current_dim > 1e-6:
                    obj.scale[i] = target_dims[i] / current_dim
                else:
                    obj.dimensions[i] = target_dims[i]

            # Aplicamos escala final para exportación limpia
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            self.report({'INFO'}, "IDECA: Dimensiones aplicadas")
        else:
            self.report({'WARNING'}, "Selecciona un objeto tipo malla")
        return {'FINISHED'}

class IDECA_OT_export_stl(bpy.types.Operator):
    bl_idname = "ideca.export_stl"
    bl_label = "3. Exportar STL"
    bl_description = "Exporta el objeto con el nombre elegido a la carpeta del proyecto"
    
    def execute(self, context):
        if not bpy.data.is_saved:
            self.report({'ERROR'}, "¡Guarda tu archivo .blend primero!")
            return {'CANCELLED'}
            
        obj = context.active_object
        scene = context.scene
        if obj:
            basedir = os.path.dirname(bpy.data.filepath)
            custom_name = scene.ideca_file_name.strip()
            
            if not custom_name:
                custom_name = bpy.path.clean_name(obj.name)
            
            if not custom_name.lower().endswith(".stl"):
                custom_name += ".stl"
                
            filepath = os.path.join(basedir, custom_name)
            
            # Exportación STL nativa de Blender 4.x
            bpy.ops.wm.stl_export(filepath=filepath, export_selected_objects=True)
            self.report({'INFO'}, f"Exportado: {custom_name}")
        else:
            self.report({'WARNING'}, "No hay objeto seleccionado")
        return {'FINISHED'}

# --- INTERFAZ ---

class IDECA_PT_main_panel(bpy.types.Panel):
    bl_label = "IDECA 3D Print Exporter"
    bl_idname = "IDECA_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'IDECA 3D'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        layout.label(text="Paso 1: Configurar", icon='TOOL_SETTINGS')
        layout.operator("ideca.setup_units", icon='SCENE_DATA')
        
        layout.separator()
        
        layout.label(text="Paso 2: Medidas (mm)", icon='FIXED_SIZE')
        col = layout.column(align=True)
        col.prop(scene, "ideca_dim_x", text="X")
        col.prop(scene, "ideca_dim_y", text="Y")
        col.prop(scene, "ideca_dim_z", text="Z")
        layout.operator("ideca.apply_dimensions", icon='CHECKMARK')
        
        layout.separator()
        
        layout.label(text="Paso 3: Archivo", icon='EXPORT')
        layout.prop(scene, "ideca_file_name", text="", icon='EDITMODE_HLT', placeholder="Nombre del STL...")
        layout.operator("ideca.export_stl", icon='FILE_3D')

# --- REGISTRO ---

classes = (
    IDECA_OT_setup_units,
    IDECA_OT_apply_dim,
    IDECA_OT_export_stl,
    IDECA_PT_main_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.ideca_dim_x = bpy.props.FloatProperty(name="X", default=20.0, min=0.001)
    bpy.types.Scene.ideca_dim_y = bpy.props.FloatProperty(name="Y", default=20.0, min=0.001)
    bpy.types.Scene.ideca_dim_z = bpy.props.FloatProperty(name="Z", default=20.0, min=0.001)
    bpy.types.Scene.ideca_file_name = bpy.props.StringProperty(
        name="Nombre Archivo",
        default=""
    )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.ideca_dim_x
    del bpy.types.Scene.ideca_dim_y
    del bpy.types.Scene.ideca_dim_z
    del bpy.types.Scene.ideca_file_name

if __name__ == "__main__":
    register()