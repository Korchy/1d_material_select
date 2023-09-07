# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/1d_material_select

from bpy.types import Operator, Panel
from bpy.utils import register_class, unregister_class

bl_info = {
    "name": "Material Select",
    "description": "Selects all objects with the same material on active object",
    "author": "Nikita Akimov, Paul Kotelevets",
    "version": (1, 0, 0),
    "blender": (2, 79, 0),
    "location": "View3D > Tool panel > 1D > Vertical Vertices",
    "doc_url": "https://github.com/Korchy/1d_material_select",
    "tracker_url": "https://github.com/Korchy/1d_material_select",
    "category": "All"
}


# MAIN CLASS

class MaterialSelect:

    @classmethod
    def find_any(cls, context, obj):
        # select objects which has one ore more materials from obj
        pass

    @classmethod
    def find_matching(cls, context, obj):
        # select objects which has all materials from obj
        pass


# OPERATORS

class MaterialSelect_OT_find_any(Operator):
    bl_idname = 'materialselect.find_any'
    bl_label = 'Find Any Mats'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        MaterialSelect.find_any(
            context=context,
            obj=context.active_object
        )
        return {'FINISHED'}

class MaterialSelect_OT_find_matching(Operator):
    bl_idname = 'materialselect.find_matching'
    bl_label = 'Find Matching Mats'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        MaterialSelect.find_matching(
            context=context,
            obj=context.active_object
        )
        return {'FINISHED'}


# PANELS

class MaterialSelect_PT_panel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Material Select"
    bl_category = '1D'

    def draw(self, context):
        layout = self.layout
        layout.operator(
            operator='materialselect.find_any',
            icon='IMAGE_RGB_ALPHA'
        )
        layout.operator(
            operator='materialselect.find_matching',
            icon='SEQ_PREVIEW'
        )


# REGISTER

def register():
    register_class(MaterialSelect_OT_find_any)
    register_class(MaterialSelect_OT_find_matching)
    register_class(MaterialSelect_PT_panel)


def unregister():
    unregister_class(MaterialSelect_PT_panel)
    unregister_class(MaterialSelect_OT_find_matching)
    unregister_class(MaterialSelect_OT_find_any)


if __name__ == "__main__":
    register()
