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

def _local_bounds_size(obj: bpy.types.Object) -> Vector:
    # obj.dimensions はワールド系スケール込みなので、ローカルに戻す
    sx, sy, sz = (abs(obj.scale.x), abs(obj.scale.y), abs(obj.scale.z))
    sx = sx if sx > 1e-6 else 1.0
    sy = sy if sy > 1e-6 else 1.0
    sz = sz if sz > 1e-6 else 1.0
    dims_world = obj.dimensions
    return Vector((dims_world.x / sx, dims_world.y / sy, dims_world.z / sz))

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
            layout.prop(col, "size")
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
        obj = ctx.object
        col = getattr(obj, "collider", None)
        if not col:
            self.report({'ERROR'}, "Collider PropertyGroup is missing")
            return {'CANCELLED'}

        col.enabled = True
        col.type = self.create_type
        col.collision_type = self.create_collision_type

        # 初期化方針
        init = self.initialize_from

        col.center = (0,0,0)

        if col.type == COL_BOX:
            if init == 'BOUNDS':
                # ローカルバウンディングボックスからサイズ＆中心を取る
                from mathutils import Vector
                bb = [Vector(v) for v in obj.bound_box]
                bb_center = sum(bb, Vector()) / 8.0
                col.center = bb_center
                col.size = _local_bounds_size(obj)
            elif init == 'ZERO':
                col.size = (1,1,1)
            elif init == 'LAST':
                pass
        else:
            if init == 'BOUNDS':
                s = _local_bounds_size(obj)
                col.radius = max(s.x, s.y, s.z) * 0.5
                if col.type in (COL_CYLINDER, COL_CAPSULE):
                    col.height = s.z
            elif init == 'ZERO':
                col.radius = 1.0
                if col.type in (COL_CYLINDER, COL_CAPSULE):
                    col.height = 2.0
            elif init == 'LAST':
                pass

        # 再描画
        for win in bpy.context.window_manager.windows:
            for area in win.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
        return {'FINISHED'}

class MYADDON_OT_remove_collider_props(Operator):
    bl_idname = "myaddon.remove_collider_props"
    bl_label = "Remove Collider"

    def execute(self, ctx):
        obj = ctx.object
        col = getattr(obj, "collider", None)
        if not col:
            return {'CANCELLED'}
        col.enabled = False
        # 値は保持（再追加で LAST を選べば復活）
        for win in bpy.context.window_manager.windows:
            for area in win.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
        return {'FINISHED'}

# 完全リセット（原点＆既定値へ戻す）
class MYADDON_OT_reset_collider_values(Operator):
    bl_idname = "myaddon.reset_collider_values"
    bl_label = "Reset Collider Values"

    def execute(self, ctx):
        obj = ctx.object
        col = getattr(obj, "collider", None)
        if not col:
            return {'CANCELLED'}
        col.center = (0,0,0)
        if col.type == COL_BOX:
            col.size = (2,2,2)
        else:
            col.radius = 1.0
            if col.type in (COL_CYLINDER, COL_CAPSULE):
                col.height = 2.0
        for win in bpy.context.window_manager.windows:
            for area in win.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
        return {'FINISHED'}
