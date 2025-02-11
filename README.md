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

**Material Prefix**

For each material on the active object change the prefix of the material name

**Sort Material by Area**

Sort materials on the active object by the whole area of the material on all selected objects

**Multiply Material Viewport Color**

Multiply Hue/Saturation/Value of the Material Viewport Color by a certain value for each material on the active object

**Mats Dbase to Active**

Append all materials from the scene to the currently active object material slots

Current version
-
1.5.0.

Blender version
-
2.79

Version history
-
1.5.0
- "Mats Dbase to Active" added

1.4.0
- "Material Prefix" added
- "Sort Material by Area" added
- "Multiply Material Viewport Color" added

1.3.2
- Modes for "Texture name to Material name": RANDOM, MAX_SIZE, MIN_SIZE, MAX_NAME, MIN_NAME

1.3.1
- Updated "Texture name to Material name" work
- Updated "Unpack textures to Material folders" work

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
