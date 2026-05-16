bl_info = {
        "name": "Pipeline Mage",
        "author": "Halin",
        "version":  (0, 0, 1),
        "blender": (2, 80, 0),
        "location": "View3D  > Sidebar > Pipeline Mage",
        "description": "My tech art buttons",
        "category": "Development",
}


import os

# Give Python Access to Blender's Functionality

import bpy

# For Custom Icons

import bpy.utils.previews

custom_icons = None

class PipelineMageProperties(bpy.types.PropertyGroup):
    
    
    show_prepare: bpy.props.BoolProperty(
        name = "Prepare Mesh",
        default=True
    )
    
    show_validate: bpy.props.BoolProperty(
        name = "Validate Mesh",
        default=False
    )
    
    show_export: bpy.props.BoolProperty(
        name = "Export",
        default=False
    )
    

# Section Header, Avoid Mess
def draw_section(layout, props, prop_name, label):
    box = layout.box()
    row = box.row()
    is_open = getattr(props, prop_name)
    
    # Is the section open? If so, display visually
    row.prop(
        props,
        prop_name,
        icon="TRIA_DOWN" if is_open else "TRIA_RIGHT",
        icon_only=True,
        emboss=False
    )
    
    row.label(text=label)
    
    return box, is_open

# Add a color attribute named Col to the Active Mesh

class PIPELINEMAGE_add_col_attribute(bpy.types.Operator):
    bl_idname = "pipeline_mage.add_col_attribute"
    bl_label = "Add Col for Vertex Painting"
    bl_description = "Add a color attribute named Col to the active mesh"
    
    def execute(self, context):
        obj = context.object
        
        if obj is None:
            self.report({'WARNING'}, "No active object selected")
            return {'CANCELLED'}
        
        if obj.type != 'MESH':
            self.report({'WARNING'}, "Active object is not a mesh")
            return {'CANCELLED'}
        
        mesh = obj.data
        
        # If Col (Color Attribute) already exists, don't create a dupe
        if "Col" in mesh.color_attributes:
            self.report({'INFO'}, "Color attribute 'Col' already exists")
            return {'FINISHED'}
        
        mesh.color_attributes.new(
            name="Col",
            type='BYTE_COLOR',
            domain='CORNER'
        )
        
        self.report({'INFO'}, "Added color attribute 'Col' YAY!")
        return {'FINISHED'}
    
class PIPELINEMAGE_batch_rename(bpy.types.Operator):
    bl_idname = "pipeline_mage.batch_rename"
    bl_label = "Batch Rename"
    bl_description = "Open Blender's batch rename popup"
    
    def execute(self, context):
        bpy.ops.wm.batch_rename('INVOKE_DEFAULT')
        return {'FINISHED'}

class PIPELINEMAGE_send_selected_to_collection(bpy.types.Operator):
    bl_idname = "pipeline_mage.new_collection"
    bl_label = "Move to New Collection"
    bl_description = "Move selected objects into a collection"
    
    def execute(self, context):
        selection = context.selected_objects
        
          
        if not selection:
            self.report({'WARNING'}, "No active objects selected")
            return {'CANCELLED'}
        
        collection_name = "Group"
        
        # Create Collection if it Does Not Exist
        if collection_name not in bpy.data.collections:
            target_collection = bpy.data.collections.new(collection_name)
            context.scene.collection.children.link(target_collection)    
        else:
            target_collection = bpy.data.collections[collection_name]
            
        for obj in selection: 
            if obj.name not in target_collection.objects.keys():
                target_collection.objects.link(obj)
                
            # Unlink From Other Collections
            for old_collection in list (obj.users_collection):
                if old_collection != target_collection:
                    old_collection.objects.unlink(obj)
        
       
        self.report({'INFO'}, "Moved to new collection! :D")
        return {'FINISHED'}
            

# Prepare Mesh

def draw_prepare_section(layout, context, props):
    box, is_open = draw_section(layout, props, "show_prepare", "Prepare Mesh")

    if not is_open:
        return

    
    col = box.column(align=True)
    # Apply All Transforms
    col.operator("object.transform_apply", text = "Apply Transforms", icon="OBJECT_ORIGIN")
    # Recalculate Normals
    col.operator("mesh.normals_make_consistent", text= "Recalculate Normals", icon="MESH_DATA")
    # Remove Doubles aka Merge by Distance
    col.operator("mesh.remove_doubles", text= "Remove Doubles", icon = "AUTOMERGE_ON")
    # Triangulate
    col.operator("mesh.quads_convert_to_tris", text= "Triangulate", icon = "MOD_TRIANGULATE")
    col.separator()
    # Add Color Attribute
    col.operator("pipeline_mage.add_col_attribute", text= "Add Color Attribute", icon = "VPAINT_HLT")
    # Batch Rename and Group
    col.operator("pipeline_mage.batch_rename", text= "Batch Rename", icon = "GREASEPENCIL")
    # Send Selected to New Collection
    col.operator("pipeline_mage.new_collection", text= "Send Selected to Collection", icon = "COLLECTION_NEW")
    # Add Material
    col.operator("material.new", text= "Add Material (WIP)", icon = "MATERIAL")

        
        
        
# Validate Mesh

def draw_validate_section(layout, context, props):
    box, is_open = draw_section(layout, props, "show_validate", "Validate Mesh")

    if not is_open:
        return
    
    
    col = box.column(align=True)
    # Check Scale
    col.operator("", text= "Check Scale", icon="EXPORT")



# Export Mesh



def draw_export_section(layout, context, props):
    box, is_open = draw_section(layout, props, "show_export", "Export Mesh")
    
    if not is_open:
        return
    
    col = box.column(align=True)
    col.operator("", text= "Batch")


class VIEW3D_PT_pipeline_mage(bpy.types.Panel): # class naming convention 'CATEGORY_PT_name'
  
    # Where to Add the Panel in the UI

    bl_space_type = "VIEW_3D" # 3D Viewport area
    bl_region_type = "UI" # sidebar region

    # add labels
    bl_category = "Pipeline Mage" # found in the Sidebar
    bl_label = "Pipeline Mage" # found at the top of the Panel
    bl_idname = "VIEW3D_PT_pipeline_mage"
    
    
    def draw(self, context):
        
        layout = self.layout
        
        if custom_icons and "MAGIC_STAFF" in custom_icons:
            icon_id = custom_icons["MAGIC_STAFF"].icon_id
            layout.label(text="Magic", icon_value=icon_id)
        else:
            layout.label(text="Magic", icon="OUTLINER_OB_LIGHT")
        
        
        props = context.scene.pipeline_mage
        
        draw_prepare_section(layout, context, props)
        draw_validate_section(layout, context, props)
        draw_export_section(layout, context, props)
        
    
classes = (
    PipelineMageProperties,
    PIPELINEMAGE_add_col_attribute,
    PIPELINEMAGE_batch_rename,
    PIPELINEMAGE_send_selected_to_collection,
    VIEW3D_PT_pipeline_mage,
)


# Register the Panel with Blender

def register():
    global custom_icons
    custom_icons = bpy.utils.previews.new()
    
    
    
    addon_path = os.path.dirname(__file__)
    icons_path = os.path.join(addon_path, "icons")
    icon_file = os.path.join(icons_path, "MAGIC_STAFF.png")
    

    if os.path.exists(icon_file):
        custom_icons.load("MAGIC_STAFF", icon_file, 'IMAGE')
    
    
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.pipeline_mage =  bpy.props.PointerProperty(
        type=PipelineMageProperties
    )
        
def unregister():
    global custom_icons
    
    
    
    if custom_icons:
        bpy.utils.previews.remove(custom_icons)
        custom_icons = None
        
        
    del bpy.types.Scene.pipeline_mage
    
    for cls in reversed(classes):
            bpy.utils.unregister_class(cls)
    
    
if __name__ == "__main__":
    register()