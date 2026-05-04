# Collider Properties
import bpy
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, EnumProperty, FloatProperty, FloatVectorProperty, PointerProperty
from .collider_types import enum_items, COL_BOX, COL_SPHERE, COL_CYLINDER, COL_CAPSULE

# 3Dビューを再描画する
def _redraw_3d_views():
    for win in bpy.context.window_manager.windows:
        for area in win.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

# プロパティ変更時コールバック
def _on_change(self, context):
    _redraw_3d_views()

# Collider PropertyGroup
class ColliderProps(PropertyGroup):
    # 有効/無効フラグ
    enabled: BoolProperty(name="Enabled", default=False)

    type: EnumProperty(
        name="Type",
        items=enum_items(),
        default=COL_BOX,
        update=_on_change,  # 変更時に3Dビュー再描画
    )
    center: FloatVectorProperty(name="Center", size=3, default=(0,0,0), update=_on_change) # 全タイプ共通
    size:   FloatVectorProperty(name="Size",   size=3, default=(2,2,2), min=0.0, update=_on_change)   # BOX
    radius: FloatProperty(name="Radius", default=1.0, min=0.0, update=_on_change)                     # SP/CL/CY
    height: FloatProperty(name="Height", default=2.0, min=0.0, update=_on_change)                     # CL/CY

def register_props():
    bpy.utils.register_class(ColliderProps)
    bpy.types.Object.collider = PointerProperty(type=ColliderProps)

def unregister_props():
    del bpy.types.Object.collider
    bpy.utils.unregister_class(ColliderProps)
