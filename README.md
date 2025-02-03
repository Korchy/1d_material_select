# 1D Material Select

Blender add-on.

Add-on functionality
-
Selects all objects that have match materials.

**Find Any Mats**

Select objects that have at least one same material as an active object.

**Find Matching Mats**

Select objects that have all material as an active object.

**Exact Number**

If "Exact Number" option is on, searching is made for all materials without numeric postfixes (.001).
Ex: "Material.001", "Material.002" and "Material" will be find in search.

**Principled to Viewport**

For all materials in the scene if the material has the "PrincipledBSDF" node copy its "Base Color" input color to the Material Viewport color

**Viewport to Principled**

For all materials in the scene if the material has the "PrincipledBSDF" node copy the Material Viewport color to the "PrincipledBSDF" node "Base Color" input color

**Texture name to Material name**

For all selected objects for all materials in the object - if the material has the Image Texture node with loaded texture, the name of this texture applies to the material name.

**Unpack textures to Material folders**

For all selected objects for all materials in the object - if the material has the Image Texture node with loaded texture, the name of this texture unpack this texture to the folder with the current material name.

Current version
-
1.3.0.

Blender version
-
2.79

Version history
-
1.3.0
- Added "Texture name to Material name" function
- Added "Unpack textures to Material folders" function

1.2.0
- Added two functions:
  - copy Principled BSDF node Base Color input color to the Material Viewport color
  - copy the Material Viewport color to the Principled BSDF node Base Color input color

1.1.1
- Integrated to the NA 1D Tools

1.1.0
- Added new option "Find Exact Mats" for finding objects with fully equal materials lists

1.0.1
- "Exact Number" functional added

1.0.0
- Release
