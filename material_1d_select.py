# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/1d_material_select

import re
from bpy.props import BoolProperty
from bpy.types import Operator, Panel, Scene
from bpy.utils import register_class, unregister_class

bl_info = {
    "name": "Material 1D Select",
    "description": "Selects all objects with the same material on active object",
    "author": "Nikita Akimov, Paul Kotelevets",
    "version": (1, 1, 0),
    "blender": (2, 79, 0),
    "location": "View3D > Tool panel > 1D > Vertical Vertices",
    "doc_url": "https://github.com/Korchy/1d_material_select",
    "tracker_url": "https://github.com/Korchy/1d_material_select",
    "category": "All"
}


# MAIN CLASS

class MaterialSelect:

    @classmethod
    def find_any(cls, context, src_obj, exact_number):
        # select objects which has one or more materials from obj
        if src_obj:
            cls._deselect_all(context=context)
            checking_objects = (obj for obj in context.blend_data.objects if obj.type == 'MESH')
            for obj in checking_objects:
                # check at least one material by names from scr_obj in obj
                if exact_number:
                    # full names matching
                    src_names = [material.name for material in src_obj.data.materials]
                    obj_names = [material.name for material in obj.data.materials]
                else:
                    # ignore postfixes (.001, .002, and etc) in names
                    src_names = [cls._clear_name(name=material.name) for material in src_obj.data.materials]
                    obj_names = [cls._clear_name(name=material.name) for material in obj.data.materials]
                disjoint = not set(src_names).isdisjoint(obj_names)
                if disjoint:
                    obj.select = True
        else:
            print('ERR: no active object')

    @classmethod
    def find_matching(cls, context, src_obj, exact_number):
        # select objects which has all materials from obj
        if src_obj:
            cls._deselect_all(context=context)
            checking_objects = (obj for obj in context.blend_data.objects if obj.type == 'MESH')
            for obj in checking_objects:
                # check all materials by names from src_obj in obj
                if exact_number:
                    # full names matching
                    src_names = [material.name for material in src_obj.data.materials]
                    obj_names = [material.name for material in obj.data.materials]
                else:
                    # ignore postfixes (.001, .002, and etc) in names
                    src_names = [cls._clear_name(name=material.name) for material in src_obj.data.materials]
                    obj_names = [cls._clear_name(name=material.name) for material in obj.data.materials]
                subset = set(src_names).issubset(obj_names)
                if subset:
                    obj.select = True
        else:
            print('ERR: no active object')

    @classmethod
    def find_exact(cls, context, src_obj, exact_number):
        # select objects which has the same list of materials as the source object
        if src_obj:
            cls._deselect_all(context=context)
            checking_objects = (obj for obj in context.blend_data.objects if obj.type == 'MESH')
            for obj in checking_objects:
                # check all materials by names from src_obj in obj
                if exact_number:
                    # full names matching
                    src_names = [material.name for material in src_obj.data.materials]
                    obj_names = [material.name for material in obj.data.materials]
                else:
                    # ignore postfixes (.001, .002, and etc) in names
                    src_names = [cls._clear_name(name=material.name) for material in src_obj.data.materials]
                    obj_names = [cls._clear_name(name=material.name) for material in obj.data.materials]
                if set(src_names) == set(obj_names):
                    obj.select = True
        else:
            print('ERR: no active object')

    @staticmethod
    def _deselect_all(context):
        # deselect all objects
        for obj in context.scene.objects:
            obj.select = False

    @staticmethod
    def _clear_name(name: str):
        # remove .001 postfix from name
        regexp = re.compile(r'(\.\d{3}$)')
        return regexp.split(name)[0]


# OPERATORS

class MaterialSelect_OT_find_any(Operator):
    bl_idname = 'materialselect.find_any'
    bl_label = 'Find Any Mats'
    bl_description = 'Selects objects containing any active object material'
    bl_options = {'REGISTER', 'UNDO'}

    exact_number = BoolProperty(
        name='Exact Number',
        description='Process material clone suffixes exactly, ignore suffixes when turned off',
        default=False
    )

    def execute(self, context):
        MaterialSelect.find_any(
            context=context,
            src_obj=context.active_object,
            exact_number=self.exact_number
        )
        return {'FINISHED'}


class MaterialSelect_OT_find_matching(Operator):
    bl_idname = 'materialselect.find_matching'
    bl_label = 'Find Matching Mats'
    bl_description = 'Select objects that contain the same set of materials as the active object'
    bl_options = {'REGISTER', 'UNDO'}

    exact_number = BoolProperty(
        name='Exact Number',
        description='Process material clone suffixes exactly, ignore suffixes when turned off',
        default=False
    )

    def execute(self, context):
        MaterialSelect.find_matching(
            context=context,
            src_obj=context.active_object,
            exact_number=self.exact_number
        )
        return {'FINISHED'}


class MaterialSelect_OT_find_exact(Operator):
    bl_idname = 'materialselect.find_exact'
    bl_label = 'Find Exact Mats'
    bl_description = 'Select objects that contain the same list of materials as the active one'
    bl_options = {'REGISTER', 'UNDO'}

    exact_number = BoolProperty(
        name='Exact Number',
        description='Process material clone suffixes exactly, ignore suffixes when turned off',
        default=False
    )

    def execute(self, context):
        MaterialSelect.find_exact(
            context=context,
            src_obj=context.active_object,
            exact_number=self.exact_number
        )
        return {'FINISHED'}


# PANELS

class MaterialSelect_PT_panel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = 'Material 1D Select'
    bl_category = '1D'

    def draw(self, context):
        layout = self.layout
        op = layout.operator(
            operator='materialselect.find_any',
            icon='IMAGE_RGB_ALPHA'
        )
        op.exact_number = context.scene.material_select_exact_number
        op = layout.operator(
            operator='materialselect.find_matching',
            icon='SEQ_PREVIEW'
        )
        op.exact_number = context.scene.material_select_exact_number
        op = layout.operator(
            operator='materialselect.find_exact',
            icon='POTATO'
        )
        op.exact_number = context.scene.material_select_exact_number
        layout.prop(
            data=context.scene,
            property='material_select_exact_number'
        )


# REGISTER

def register():
    Scene.material_select_exact_number = BoolProperty(
        name='Exact Number',
        description='Process material clone suffixes exactly, ignore suffixes when turned off',
        default=False
    )
    register_class(MaterialSelect_OT_find_any)
    register_class(MaterialSelect_OT_find_matching)
    register_class(MaterialSelect_OT_find_exact)
    register_class(MaterialSelect_PT_panel)


def unregister():
    unregister_class(MaterialSelect_PT_panel)
    unregister_class(MaterialSelect_OT_find_exact)
    unregister_class(MaterialSelect_OT_find_matching)
    unregister_class(MaterialSelect_OT_find_any)
    del Scene.material_select_exact_number


if __name__ == "__main__":
    register()
