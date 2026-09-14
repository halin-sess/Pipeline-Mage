## Pipeline Mage
Pipeline Mage is a Blender extension to simplify repetitive steps of the 3D game asset creation pipeline. It’s still a work-in-progress, but I plan to add more complex actions as the need arises. Sometimes it is just that I repeat a step so many times, it’s easier to have it a click away on the toolbar. Right now, I plan to prepare most exports for Godot, as that is my engine of choice nowadays. That being said, this list of actions will be updated as I add more things 🐌 & I would eventually like to give the UI a more unique look, but that’ll be a longer term goal! ✨ YAY!


## Prepare Mesh

Apply Transforms

Recalculate Normals

Remove Doubles

Triangulate

> ^ These all use operators already available in Blender.


Add Color Attribute
---
> Add a color attribute named Col to the active mesh <br>
> This was added to create and attach color attributes faster for vertex painting 🖌
    
```
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
    
```



Batch Rename
---

> Open Blender's batch rename popup <br>

Send Selected to Collection
---

> Move selected objects into collection

```
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


```

Add New Flat Materials
---
> Create flat material with empty image node and attach to selected mesh <br>
> I plan to change this at some point. I wouldn't say this is "FLAT" because it uses a P BSDF 🤔

```
class PIPELINEMAGE_add_flat_material_and_apply_to_selected_mesh(bpy.types.Operator):
    bl_idname = "pipeline_mage.new_flat_material"
    bl_label = "Create Flat Material With Empty Image Node and Attach to Selected"
    bl_description = "Create flat material with empty image node and attach to selected mesh"
    
    # User Selects Size (in px) of Texture. 16, 32, 64, 128, 256, 512, 1024, or 2048
    texture_size: bpy.props.EnumProperty(
        name= "Texture Size",
        description="Choose the size of the new texture",
        items = [
           ('16', "16 x 16", "Create a 16px texture"),
           ('32', "32 x 32", "Create a 32px texture"),
           ('64', "64 x 64", "Create a 64px texture"),
           ('128', "128 x 128", "Create a 128px texture"),
           ('256', "256 x 256", "Create a 256px texture"),
           ('512', "512 x 512", "Create a 512px texture"),
           ('1024', "1024 x 1024", "Create a 1024px texture"),
           ('2048', "2048 x 2048", "Create a 2048px texture"), 
        ],
        default='1024'
        
    )
    
    def invoke(self, context, event):
       return context.window_manager.invoke_props_dialog(self)
    
    
    def execute(self, context):
        obj = context.object
        
        if obj is None:
            self.report({'WARNING'}, "No active object selected")
            return {'CANCELLED'}
        
        if obj.type != 'MESH':
            self.report({'WARNING'}, "Active object is not a mesh")
            return {'CANCELLED'}
        
        mesh = obj.data
        size = int(self.texture_size)
        
        image = bpy.data.images.new(
           name=f"T_{mesh.name}_{size}",
           width=size,
           height=size,
           alpha=True
        
        )
        
        # If Material already exists on Object, don't create a dupe
        if "M_" + mesh.name in mesh.materials:
            self.report({'INFO'}, "Material already exists")
            return {'FINISHED'}
        
        # Add a New Material named M_ + Selected Active Object's Name
        bpy.data.materials.new(name="M_" + mesh.name)
        
        mat = bpy.data.materials.get("M_" + mesh.name)
        
        # Assign Material to Object, stick it in slot [0]
        
        if obj.data.materials:
           obj.data.materials[0] = mat
        else:
           # no slots
           obj.data.materials.append(mat)
            
            
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        
        image_node = nodes.new('ShaderNodeTexImage')
        image_node.location = (-300, 0)
        image_node.image = image
        
        
        # Why is an Image Texture Node called by its type name, but not a BSDF!? YARGH I love you Blender <3
        # There's probs a real reason. I'm sure
        
        bsdf_shader_node = nodes.get('Principled BSDF')
        
        if bsdf_shader_node is None:
            bsdf_shader_node = nodes.new(type='ShaderNodeBsdfPrincipled')
            bsdf_shader_node.location = (300, 0)
            
        
        links.new(image_node.outputs['Color'], bsdf_shader_node.inputs['Base Color'])
        
        self.report({'INFO'}, "Created a New Material For Object!")
        return {'FINISHED'}

```

Snap UVs to Selection
---
> Snap UVs to selected quadrant <br>
> This is mainly for the purpose of organizing UVs. Put this in that corner, this corner, etc... <br>
> Needs some work, but the idea is there...another one I need to revisit

```

class PIPELINEMAGE_snap_uvs_to_selected_quadrant(bpy.types.Operator):
    bl_idname = "pipeline_mage.snap_uvs_to_selected_quadrant"
    bl_label = "Snap UVs to Selected Quadrant"
    bl_description = "Snap UVs to selected quadrant"
     
     
    region: bpy.props.EnumProperty(
       name="UV Region",
       items=[
          ('0', "Upper Left", "Move UVS to upper-left region"),
          ('1', "Upper Right", "Move UVS to upper-right region"),
          ('2', "Lower Left", "Move UVS to lower-left region"),
          ('3', "Lower Right", "Move UVs to lower-right region"),
       ],
       default='1'
    )
    
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        obj = context.object
        
        if obj is None:
            self.report({'WARNING'}, "No active object selected")
            return {'CANCELLED'}
        
        if obj.type != 'MESH':
            self.report({'WARNING'}, "Active object is not a mesh")
            return {'CANCELLED'}
        
        mesh = obj.data
        uv_layer = mesh.uv_layers.active
    
        if uv_layer is None:
          self.report({'Warning'}, "Object has no UV Map")
          return {'CANCELLED'}  
    
        regions = {
            '0': (0.0, 0.5),
            '1': (0.5, 0.5),
            '2': (0.0, 0.0),
            '3': (0.5, 0.0),
    
        }
    
        offset_u, offset_v =regions[self.region]
     
        for loop in mesh.loops:
            uv = uv_layer.data[loop.index].uv
        
            uv.x = uv.x * 0.5 + offset_u
            uv.y = uv.y * 0.5 + offset_v
        
        mesh.update()
     
        self.report({'INFO'}, "Moved UVs to Selected Region")
        return {'FINISHED'}
```

