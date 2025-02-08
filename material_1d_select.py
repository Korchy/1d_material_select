# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/1d_material_select

from functools import reduce
from operator import mul
import os
import re
import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, StringProperty
from bpy.types import Operator, Panel, Scene, WindowManager
from bpy.utils import register_class, unregister_class

bl_info = {
    "name": "Material 1D Select",
    "description": "Selects all objects with the same material on active object",
    "author": "Nikita Akimov, Paul Kotelevets",
    "version": (1, 4, 0),
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
    def principled_color_to_viewport(context):
        # copy Principled BSDF node Base Color input color to the Material Viewport color
        # for each material
        for material in context.blend_data.materials:
            if material.node_tree:
                # check if it has PrincipledBSDF node
                principled_node = material.node_tree.nodes.get('Principled BSDF')
                if principled_node:
                    # copy Base Color from node to the material Viewport color
                    material.diffuse_color = principled_node.inputs['Base Color'].default_value[:3]

    @staticmethod
    def viewport_color_to_principled(context):
        # copy the Material Viewport color to the Principled BSDF node Base Color input color
        # for each material
        for material in context.blend_data.materials:
            if material.node_tree:
                # check if it has PrincipledBSDF node
                principled_node = material.node_tree.nodes.get('Principled BSDF')
                if principled_node:
                    # copy the material Viewport color to the Base Color input of the PrincipledGSDF node
                    principled_node.inputs['Base Color'].default_value = material.diffuse_color[:] + (1.0, )

    @staticmethod
    def texture_name_to_material(context, mode):
        # if material has an Image Texture node with a texture loaded - copy the texture name to the material name
        # for each material on each selected object
        for obj in (_obj for _obj in context.selected_objects if _obj.data and hasattr(_obj.data, 'materials')):
            for material in (_mat for _mat in obj.data.materials if _mat.node_tree):
                # list of nodes with image texture and texture loaded to it
                # [(node, image_size, image_name), ...]
                image_texture_nodes = [(node, reduce(mul, node.image.size), len(bpy.path.basename(node.image.filepath)))
                                       for node in material.node_tree.nodes
                                       if node.type == 'TEX_IMAGE' and node.image]
                # print(list(image_texture_nodes))
                if mode == 'LONGEST_NAME':
                    node_data = max(image_texture_nodes, key=lambda _t: _t[2]) if image_texture_nodes else None
                elif mode == 'SHORTEST_NAME':
                    node_data = min(image_texture_nodes, key=lambda _t: _t[2]) if image_texture_nodes else None
                elif mode == 'LONGEST_SIZE':
                    node_data = max(image_texture_nodes, key=lambda _t: _t[1]) if image_texture_nodes else None
                elif mode == 'SHORTEST_SIZE':
                    node_data = min(image_texture_nodes, key=lambda _t: _t[1]) if image_texture_nodes else None
                else:
                    node_data = image_texture_nodes[0] if image_texture_nodes else None
                # for founded node
                if node_data:
                    node = node_data[0] # (node, image_size, image_name)
                    texture_path = node.image.filepath  # '//textures\\T_EdvardaGriga_4A_001_d_1.png'
                    texture_name = bpy.path.basename(texture_path)
                    if texture_name:
                        material.name = texture_name

    @staticmethod
    def unpack_textures_to_mat(context):
        # if material has an Image Texture node with a texture loaded - unpack this texture to the folder with the material name
        # for each material on each selected object
        current_dir = os.path.dirname(bpy.path.abspath(bpy.data.filepath))
        for obj in (_obj for _obj in context.selected_objects if _obj.data and hasattr(_obj.data, 'materials')):
            for material in (_mat for _mat in obj.data.materials if _mat.node_tree):
                material_dir = os.path.join(current_dir, '_textures', material.name)
                # for each Image Texture node in the material
                image_texture_nodes = (node for node in material.node_tree.nodes
                                       if node.type == 'TEX_IMAGE' and node.image)
                for node in image_texture_nodes:
                    # create directory with the material name only if this material has a texture
                    if not os.path.isdir(material_dir):
                        os.makedirs(material_dir)
                    # save image texture to the material directory
                    image_texture_name = bpy.path.basename(node.image.filepath)
                    # change filepath for saving
                    node.image.filepath = os.path.join(material_dir, image_texture_name)
                    try:
                        node.image.save() # saves by the current .filepath
                    except Exception as err:
                        print('ERR: Cant save texture', image_texture_name, 'from material', material.name, 'to', node.image.filepath)

    @staticmethod
    def mat_prefix(context, prefix_from, prefix_to):
        # for each material on the active object change the prefix of the material name
        for material in (_mat for _mat in context.active_object.data.materials if _mat.node_tree):
            # remove prefix
            if material.name.startswith(prefix_from):
                material.name = material.name[len(prefix_from):]
            # add new prefix
            material.name = prefix_to + material.name

    @classmethod
    def sort_by_area(cls, context, op):
        # sort materials on the active object by the whole area of the material on all selected objects
        # switch to the OBJECT mode
        mode = context.object.mode
        if mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')
        # count an area of all polygons by used material
        # ['cyan', 'blue', 'None'] - None for empty slots
        active_obj_materials = [cls._material_name(_material) \
                                for _material in context.active_object.data.materials]
        # print('aom', active_obj_materials)
        # active_obj_materials_weights = {'blue': 0.0, 'cyan': 0.0, 'None': 0.0}
        active_obj_materials_weights = {_k: 0.0 for _k in active_obj_materials}
        # print('aom_weights', active_obj_materials_weights)
        # for each selected object
        # active_obj_materials_weights = {'cyan': 20.0, 'blue': 52.0, 'None': 4.0}
        for obj in (_obj for _obj in context.selected_objects if _obj.type == 'MESH' and _obj.data.materials):
            # for each polygon with applied material
            for polygon in obj.data.polygons:
                polygon_material_name = cls._material_name(obj.data.materials[polygon.material_index])
                # only for active object materials
                if polygon_material_name in active_obj_materials_weights:
                    active_obj_materials_weights[polygon_material_name] += polygon.area
        # print('active_obj_materials_weights', active_obj_materials_weights)
        active_obj_materials_sorted = sorted(active_obj_materials_weights, key=active_obj_materials_weights.get)
        # report
        op.report(
            type={'INFO'},
            message='Active object material weights: '
                    + str([name + ': ' + str(round(active_obj_materials_weights[name], 1))
                           for name in active_obj_materials_sorted])
        )
        # extend to all material slots
        #   [(index, name, weight), ...]
        #   [(0, 'cyan', 20.0), (1, 'blue', 52.0, (2, 'None', 4.0)]
        active_obj_materials_i = [
            (_i, cls._material_name(_material), active_obj_materials_weights[cls._material_name(_material)])
            for _i, _material in enumerate(context.active_object.data.materials)
        ]
        # print('aom_w_i', active_obj_materials_i)
        # [(2, 'None', 4.0), (0, 'cyan', 20.0), (1, 'blue', 52.0]
        active_obj_materials_sorted = sorted(active_obj_materials_i, key=lambda _item: _item[2])
        # print('aom_sorted', active_obj_materials_sorted)
        # sort materials in object's material_slots by weight
        for _slot_i, (_i, mat_name, weight) in enumerate(active_obj_materials_sorted):
            # get material index from which switch material by its name
            slot_from = next((_idx + _slot_i for _idx, _material in enumerate(context.object.data.materials[_slot_i:])
                              if cls._material_name(_material) == mat_name), None)
            if slot_from:
                cls._switch_materials(context.object, slot_from, _slot_i)
        # return mode back
        bpy.ops.object.mode_set(mode=mode)

    @staticmethod
    def multiply_viewport_color(context, hue_adder=0.0, saturation_multiplier=1.0, value_multiplier=1.0):
        # multiply Hue of the Material Viewport Color by a certain value for each material on the active object
        if hasattr(context.object.data, 'materials'):
            for material in (_mat for _mat in context.object.data.materials if _mat.node_tree):
                material.diffuse_color.h += hue_adder  # Palu: summ, not multiplying
                material.diffuse_color.s *= saturation_multiplier
                material.diffuse_color.v *= value_multiplier

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

    @staticmethod
    def _material_name(_material):
        # get material name
        return _material.name if _material else 'None'

    @staticmethod
    def _switch_materials(obj, mat_1_idx, mat_2_idx):
        # witch material with mat_1_idx index with material with mat_2_idx index in obj materials list
        #   switching only in materials list / materials slots, no real changes on objects
        # switch materials
        obj.data.materials[mat_1_idx], obj.data.materials[mat_2_idx] = \
            obj.data.materials[mat_2_idx], obj.data.materials[mat_1_idx]
        # switch material indices on polygons
        polygons_mat_1_idx = [_p for _p in obj.data.polygons if _p.material_index == mat_1_idx]
        polygons_mat_2_idx = [_p for _p in obj.data.polygons if _p.material_index == mat_2_idx]
        for polygon in polygons_mat_1_idx:
            polygon.material_index = mat_2_idx
        for polygon in polygons_mat_2_idx:
            polygon.material_index = mat_1_idx

    @staticmethod
    def ui(layout, context):
        # ui panel
        # find operators
        box = layout.box()
        op = box.operator(
            operator='materialselect.find_any',
            icon='IMAGE_RGB_ALPHA'
        )
        op.exact_number = context.scene.material_select_exact_number
        op = box.operator(
            operator='materialselect.find_matching',
            icon='SEQ_PREVIEW'
        )
        op.exact_number = context.scene.material_select_exact_number
        op = box.operator(
            operator='materialselect.find_exact',
            icon='POTATO'
        )
        op.exact_number = context.scene.material_select_exact_number
        box.prop(
            data=context.scene,
            property='material_select_exact_number'
        )
        # material operators
        layout.separator()
        box = layout.box()
        box.operator(
            operator='materialselect.principled_color_to_viewport',
            icon='RESTRICT_COLOR_ON',
            text='Principled color to Viewport'
        )
        box.operator(
            operator='materialselect.viewport_color_to_principled',
            icon='GROUP_VCOL',
            text='Viewport color to Principled'
        )
        # sort, unpack
        layout.separator()
        box = layout.box()
        # sort by area
        box.operator(
            operator='materialselect.sort_by_area',
            icon='SORTSIZE'
        )
        # unpack textures operator
        box.operator(
            operator='materialselect.unpack_textures_to_mat',
            icon='PACKAGE',
            text='Unpack textures by Material'
        )
        # texture operators
        layout.separator()
        box = layout.box()
        op = box.operator(
            operator='materialselect.texture_name_to_material',
            icon='FORCE_TEXTURE',
            text='Texture name to Material'
        )
        op.t2m_mode = context.scene.material_select_prop_t2m_mode
        row = box.row()
        row.prop(
            data=context.scene,
            property='material_select_prop_t2m_mode',
            expand=False,
            text=''
        )
        # material prefix
        layout.separator()
        box = layout.box()
        col = box.column(align=True)
        col.prop(
            data=context.window_manager,
            property='material_select_prop_prefix_from'
        )
        col.prop(
            data=context.window_manager,
            property='material_select_prop_prefix_to'
        )
        op = col.operator(
            operator='materialselect.mat_prefix',
            icon='FONTPREVIEW'
        )
        op.prefix_from = context.window_manager.material_select_prop_prefix_from
        op.prefix_to = context.window_manager.material_select_prop_prefix_to
        # multiply viewport color (hue)
        layout.separator()
        box = layout.box()
        col = box.column(align=True)
        op = col.operator(
            operator='materialselect.multiply_viewport_color',
            icon='COLORSET_08_VEC'
        )
        op.hue_adder = context.window_manager.material_select_prop_viewport_color_hue_adder
        op.saturation_multiplier = context.window_manager.material_select_prop_viewport_color_saturation_multiplier
        op.value_multiplier = context.window_manager.material_select_prop_viewport_color_value_multiplier
        col.prop(
            data=context.window_manager,
            property='material_select_prop_viewport_color_hue_adder'
        )
        col.prop(
            data=context.window_manager,
            property='material_select_prop_viewport_color_saturation_multiplier'
        )
        col.prop(
            data=context.window_manager,
            property='material_select_prop_viewport_color_value_multiplier'
        )


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


class MaterialSelect_OT_principled_color_to_viewport(Operator):
    bl_idname = 'materialselect.principled_color_to_viewport'
    bl_label = 'PrincipledBSDF to Viewport Color'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        MaterialSelect.principled_color_to_viewport(
            context=context
        )
        return {'FINISHED'}


class MaterialSelect_OT_viewport_color_to_principled(Operator):
    bl_idname = 'materialselect.viewport_color_to_principled'
    bl_label = 'Viewport Color to PrincipledBSDF'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        MaterialSelect.viewport_color_to_principled(
            context=context
        )
        return {'FINISHED'}


class MaterialSelect_OT_texture_name_to_material(Operator):
    bl_idname = 'materialselect.texture_name_to_material'
    bl_label = 'Texture name to Material name'
    bl_options = {'REGISTER', 'UNDO'}

    t2m_mode = EnumProperty(
        name='Texture to Material mode',
        items=[
            ('RANDOM', 'RANDOM', 'RANDOM', '', 0),
            ('LONGEST_NAME', 'LONGEST NAME', 'LONGEST NAME', '', 1),
            ('SHORTEST_NAME', 'SHORTEST NAME', 'SHORTEST NAME', '', 2),
            ('LONGEST_SIZE', 'MAX SIZE', 'LONGEST SIZE', '', 3),
            ('SHORTEST_SIZE', 'MIN SIZE', 'SHORTEST SIZE', '', 4)
        ],
        default='LONGEST_SIZE'
    )

    def execute(self, context):
        MaterialSelect.texture_name_to_material(
            context=context,
            mode=self.t2m_mode
        )
        return {'FINISHED'}


class MaterialSelect_OT_unpack_textures_to_mat(Operator):
    bl_idname = 'materialselect.unpack_textures_to_mat'
    bl_label = 'Unpack textures by Materials folders'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        MaterialSelect.unpack_textures_to_mat(
            context=context
        )
        return {'FINISHED'}


class MaterialSelect_OT_mat_prefix(Operator):
    bl_idname = 'materialselect.mat_prefix'
    bl_label = 'Set Material Prefix'
    bl_options = {'REGISTER', 'UNDO'}

    prefix_from = StringProperty(
        name='From',
        default=''
    )
    prefix_to = StringProperty(
        name='To',
        default=''
    )

    def execute(self, context):
        MaterialSelect.mat_prefix(
            context=context,
            prefix_from=self.prefix_from,
            prefix_to=self.prefix_to
        )
        return {'FINISHED'}


class MaterialSelect_OT_sort_by_area(Operator):
    bl_idname = 'materialselect.sort_by_area'
    bl_label = 'Sort Materials by Area'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        MaterialSelect.sort_by_area(
            context=context,
            op=self
        )
        return {'FINISHED'}


class MaterialSelect_OT_multiply_viewport_color(Operator):
    bl_idname = 'materialselect.multiply_viewport_color'
    bl_label = 'Viewport Color Multiply'
    bl_options = {'REGISTER', 'UNDO'}

    hue_adder = FloatProperty(
        name='Hue Adder',
        default=0.0
    )
    saturation_multiplier = FloatProperty(
        name='Saturation Multiplier',
        default=1.0
    )
    value_multiplier = FloatProperty(
        name='Value Multiplier',
        default=1.0
    )

    def execute(self, context):
        MaterialSelect.multiply_viewport_color(
            context=context,
            hue_adder=self.hue_adder,
            saturation_multiplier=self.saturation_multiplier,
            value_multiplier=self.value_multiplier
        )
        return {'FINISHED'}


# PANELS

class MaterialSelect_PT_panel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = 'Material 1D Select'
    bl_category = 'NA 1D TOOLS'

    def draw(self, context):
        MaterialSelect.ui(
            layout=self.layout,
            context=context
        )


# REGISTER

def register(ui=True):
    WindowManager.material_select_prop_viewport_color_hue_adder = FloatProperty(
        name='Hue Adder',
        default=0.0
    )
    WindowManager.material_select_prop_viewport_color_saturation_multiplier = FloatProperty(
        name='Saturation Multiplier',
        default=1.0
    )
    WindowManager.material_select_prop_viewport_color_value_multiplier = FloatProperty(
        name='Value Multiplier',
        default=1.0
    )
    WindowManager.material_select_prop_prefix_from = StringProperty(
        name='From',
        default=''
    )
    WindowManager.material_select_prop_prefix_to = StringProperty(
        name='To',
        default=''
    )
    Scene.material_select_prop_t2m_mode = EnumProperty(
        name='Texture to Material mode',
        items=[
            ('RANDOM', 'RANDOM', 'RANDOM', '', 0),
            ('LONGEST_NAME', 'LONGEST NAME', 'LONGEST NAME', '', 1),
            ('SHORTEST_NAME', 'SHORTEST NAME', 'SHORTEST NAME', '', 2),
            ('LONGEST_SIZE', 'MAX SIZE', 'LONGEST SIZE', '', 3),
            ('SHORTEST_SIZE', 'MIN SIZE', 'SHORTEST SIZE', '', 4)
        ],
        default='LONGEST_SIZE'
    )
    Scene.material_select_exact_number = BoolProperty(
        name='Exact Number',
        description='Process material clone suffixes exactly, ignore suffixes when turned off',
        default=False
    )
    register_class(MaterialSelect_OT_find_any)
    register_class(MaterialSelect_OT_find_matching)
    register_class(MaterialSelect_OT_find_exact)
    register_class(MaterialSelect_OT_principled_color_to_viewport)
    register_class(MaterialSelect_OT_viewport_color_to_principled)
    register_class(MaterialSelect_OT_texture_name_to_material)
    register_class(MaterialSelect_OT_unpack_textures_to_mat)
    register_class(MaterialSelect_OT_mat_prefix)
    register_class(MaterialSelect_OT_sort_by_area)
    register_class(MaterialSelect_OT_multiply_viewport_color)
    if ui:
        register_class(MaterialSelect_PT_panel)


def unregister(ui=True):
    if ui:
        unregister_class(MaterialSelect_PT_panel)
    unregister_class(MaterialSelect_OT_multiply_viewport_color)
    unregister_class(MaterialSelect_OT_sort_by_area)
    unregister_class(MaterialSelect_OT_mat_prefix)
    unregister_class(MaterialSelect_OT_unpack_textures_to_mat)
    unregister_class(MaterialSelect_OT_texture_name_to_material)
    unregister_class(MaterialSelect_OT_viewport_color_to_principled)
    unregister_class(MaterialSelect_OT_principled_color_to_viewport)
    unregister_class(MaterialSelect_OT_find_exact)
    unregister_class(MaterialSelect_OT_find_matching)
    unregister_class(MaterialSelect_OT_find_any)
    del Scene.material_select_exact_number
    del Scene.material_select_prop_t2m_mode
    del WindowManager.material_select_prop_prefix_to
    del WindowManager.material_select_prop_prefix_from
    del WindowManager.material_select_prop_viewport_color_hue_adder
    del WindowManager.material_select_prop_viewport_color_saturation_multiplier
    del WindowManager.material_select_prop_viewport_color_value_multiplier


if __name__ == "__main__":
    register()
