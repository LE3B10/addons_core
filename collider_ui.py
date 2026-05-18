# collider_ui.py
import bpy
from bpy.types import Panel, Operator
from mathutils import Vector
from .collider_types import (
    COL_BOX,
    COL_CYLINDER,
    COL_CAPSULE,
    COLLISION_TYPE_DEFAULT,
    collision_type_enum_items,
    enum_items,
)

# 追加：初期化ソース選択
INIT_ITEMS = [
    ('BOUNDS', "From Object Bounds", "Use object's bounding box (default)"),
    ('ZERO',   "From Zero",          "Center=(0,0,0), size=1 or radius=1"),
    ('LAST',   "Reuse Last Values",  "Reuse values if any"),
]

def _object_bounds_collider_values(obj: bpy.types.Object):
    # obj.bound_box を obj.matrix_world で変換して、見た目に一致するワールド空間のCollider値を作る。
    bb_local = [Vector(corner) for corner in obj.bound_box]
    bb_world = [obj.matrix_world @ corner for corner in bb_local]
    center = sum(bb_world, Vector()) / len(bb_world)

    min_local = Vector((
        min(corner.x for corner in bb_local),
        min(corner.y for corner in bb_local),
        min(corner.z for corner in bb_local),
    ))
    max_local = Vector((
        max(corner.x for corner in bb_local),
        max(corner.y for corner in bb_local),
        max(corner.z for corner in bb_local),
    ))
    local_size = max_local - min_local

    world_axes = obj.matrix_world.to_3x3()
    size = Vector((
        local_size.x * world_axes.col[0].length,
        local_size.y * world_axes.col[1].length,
        local_size.z * world_axes.col[2].length,
    ))
    rotation = obj.matrix_world.to_quaternion().to_euler('XYZ')
    return center, size, rotation

def _set_collider_from_bounds(obj: bpy.types.Object, col):
    # Add/Reset時は選択オブジェクトごとに現在のワールド姿勢からCollider値を再計算する。
    center, size, rotation = _object_bounds_collider_values(obj)
    col.center = center
    col.rotation = rotation

    if col.type == COL_BOX:
        col.size = size
    else:
        col.radius = max(size.x, size.y, size.z) * 0.5
        if col.type in (COL_CYLINDER, COL_CAPSULE):
            col.height = size.z

def _selected_collider_objects():
    # Collider操作はアクティブではなく選択中の全オブジェクトを対象にする。
    return [obj for obj in bpy.context.selected_objects if hasattr(obj, "collider")]

def _redraw_3d_views():
    for win in bpy.context.window_manager.windows:
        for area in win.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


class OBJECT_PT_collider(Panel):
    bl_label = "Collider"
    bl_idname = "OBJECT_PT_collider"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, ctx):
        layout = self.layout
        obj = ctx.object
        col = getattr(obj, "collider", None)

        if not col or not col.enabled:
            layout.operator("myaddon.add_collider_props_dialog", icon="MESH_CUBE")
            return

        row = layout.row(align=True)
        row.prop(col, "type")
        row.operator("myaddon.remove_collider_props", text="", icon="X")

        # Collision TypeはCollider形状とは別項目として表示する
        layout.prop(col, "collision_type")
        layout.prop(col, "center")

        if col.type == COL_BOX:
            # Box Colliderは中心・サイズに加えて回転も編集できるように表示する。
            layout.prop(col, "size")
            layout.prop(col, "rotation")
        else:
            layout.prop(col, "radius")
            if col.type in (COL_CYLINDER, COL_CAPSULE):
                layout.prop(col, "height")

        # 任意：完全リセットボタン（原点＆既定値へ）
        row2 = layout.row(align=True)
        row2.operator("myaddon.reset_collider_values", icon="LOOP_BACK")

class MYADDON_OT_add_collider_props_dialog(Operator):
    bl_idname = "myaddon.add_collider_props_dialog"
    bl_label = "Add Collider"

    create_type: bpy.props.EnumProperty(name="Type", items=enum_items(), default=COL_BOX)
    # Add Collider時にCollision Typeも初期設定できるようにする
    create_collision_type: bpy.props.EnumProperty(
        name="Collision Type",
        items=collision_type_enum_items(),
        default=COLLISION_TYPE_DEFAULT,
    )
    initialize_from: bpy.props.EnumProperty(name="Initialize", items=INIT_ITEMS, default='BOUNDS')

    def invoke(self, ctx, event):
        return ctx.window_manager.invoke_props_dialog(self)

    def draw(self, ctx):
        col = self.layout.column()
        col.prop(self, "create_type")
        col.prop(self, "create_collision_type")
        col.prop(self, "initialize_from")

    def execute(self, ctx):
        selected_objects = _selected_collider_objects()
        if not selected_objects:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}

        for obj in selected_objects:
            col = getattr(obj, "collider", None)
            if not col:
                continue

            col.enabled = True
            col.type = self.create_type
            col.collision_type = self.create_collision_type

            # 選択中の各オブジェクトに同じCollider設定を適用しつつ寸法は個別に初期化する。
            init = self.initialize_from

            col.center = (0,0,0)

            if col.type == COL_BOX:
                if init == 'BOUNDS':
                    # Box Collider追加時は回転・スケール込みの境界から初期化する。
                    _set_collider_from_bounds(obj, col)
                elif init == 'ZERO':
                    col.rotation = (0.0, 0.0, 0.0)
                    col.size = (1,1,1)
                elif init == 'LAST':
                    pass
            else:
                if init == 'BOUNDS':
                    # Box以外も同じ境界計算を使って中心と寸法を合わせる。
                    _set_collider_from_bounds(obj, col)
                elif init == 'ZERO':
                    col.rotation = (0.0, 0.0, 0.0)
                    col.radius = 1.0
                    if col.type in (COL_CYLINDER, COL_CAPSULE):
                        col.height = 2.0
                elif init == 'LAST':
                    pass

        _redraw_3d_views()
        return {'FINISHED'}

class MYADDON_OT_remove_collider_props(Operator):
    bl_idname = "myaddon.remove_collider_props"
    bl_label = "Remove Collider"

    def execute(self, ctx):
        selected_objects = _selected_collider_objects()
        if not selected_objects:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}

        for obj in selected_objects:
            col = getattr(obj, "collider", None)
            if not col:
                continue
            # Remove Colliderも選択中の全オブジェクトへ一括適用する。
            col.enabled = False
        _redraw_3d_views()
        return {'FINISHED'}

# 完全リセット（原点＆既定値へ戻す）
class MYADDON_OT_reset_collider_values(Operator):
    bl_idname = "myaddon.reset_collider_values"
    bl_label = "Reset Collider Values"

    def execute(self, ctx):
        selected_objects = _selected_collider_objects()
        if not selected_objects:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}

        for obj in selected_objects:
            col = getattr(obj, "collider", None)
            if not col:
                continue
            # Reset Colliderも選択中の全オブジェクトへ一括適用する。
            _set_collider_from_bounds(obj, col)
        _redraw_3d_views()
        return {'FINISHED'}
