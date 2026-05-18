# collider_ui.py
import bpy
from bpy.types import Panel, Operator
import math
from mathutils import Matrix, Vector
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

def _convex_hull_2d(points):
    unique_points = sorted(set(points))
    if len(unique_points) <= 1:
        return unique_points

    def cross(origin, a, b):
        return ((a[0] - origin[0]) * (b[1] - origin[1])
                - (a[1] - origin[1]) * (b[0] - origin[0]))

    lower = []
    for point in unique_points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0.0:
            lower.pop()
        lower.append(point)

    upper = []
    for point in reversed(unique_points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0.0:
            upper.pop()
        upper.append(point)

    return lower[:-1] + upper[:-1]


def _minimum_area_rect_2d(points):
    hull = _convex_hull_2d(points)
    if not hull:
        return 0.0, 0.0, 0.0, 0.0, 0.0
    if len(hull) == 1:
        x, y = hull[0]
        return x, y, 0.0, 0.0, 0.0

    best = None
    for i, point in enumerate(hull):
        next_point = hull[(i + 1) % len(hull)]
        edge_x = next_point[0] - point[0]
        edge_y = next_point[1] - point[1]
        edge_len = math.hypot(edge_x, edge_y)
        if edge_len <= 1.0e-8:
            continue

        axis_x = (edge_x / edge_len, edge_y / edge_len)
        axis_y = (-axis_x[1], axis_x[0])
        projected_x = [p[0] * axis_x[0] + p[1] * axis_x[1] for p in hull]
        projected_y = [p[0] * axis_y[0] + p[1] * axis_y[1] for p in hull]
        min_x, max_x = min(projected_x), max(projected_x)
        min_y, max_y = min(projected_y), max(projected_y)
        size_x = max_x - min_x
        size_y = max_y - min_y
        area = size_x * size_y

        if best is None or area < best[0]:
            center_x = (min_x + max_x) * 0.5
            center_y = (min_y + max_y) * 0.5
            best = (area, center_x, center_y, size_x, size_y, math.atan2(axis_x[1], axis_x[0]))

    if best is None:
        x, y = hull[0]
        return x, y, 0.0, 0.0, 0.0
    return best[1], best[2], best[3], best[4], best[5]


def _mesh_vertices_local(obj: bpy.types.Object):
    if obj.type != 'MESH' or not obj.data or not obj.data.vertices:
        return []

    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = None
    try:
        mesh = eval_obj.to_mesh()
        return [vertex.co.copy() for vertex in mesh.vertices]
    finally:
        if mesh is not None:
            eval_obj.to_mesh_clear()


def _object_bounds_collider_values(obj: bpy.types.Object):
    # Box Colliderはobj.bound_boxではなくメッシュ頂点からローカル空間OBBを作り、matrix_worldでワールド値へ変換する。
    vertices = _mesh_vertices_local(obj)
    if not vertices:
        return _fallback_object_bounds_collider_values(obj)

    min_z = min(vertex.z for vertex in vertices)
    max_z = max(vertex.z for vertex in vertices)
    center_x, center_y, size_x, size_y, angle = _minimum_area_rect_2d([(vertex.x, vertex.y) for vertex in vertices])
    center_z = (min_z + max_z) * 0.5
    size_z = max_z - min_z

    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    local_axis_x = Vector((cos_a, sin_a, 0.0))
    local_axis_y = Vector((-sin_a, cos_a, 0.0))
    local_axis_z = Vector((0.0, 0.0, 1.0))
    local_center = (local_axis_x * center_x) + (local_axis_y * center_y) + (local_axis_z * center_z)

    world_matrix = obj.matrix_world
    world_center = world_matrix @ local_center
    world_linear = world_matrix.to_3x3()
    world_axes = [world_linear @ local_axis_x, world_linear @ local_axis_y, world_linear @ local_axis_z]
    local_sizes = [size_x, size_y, size_z]
    world_sizes = []
    normalized_axes = []

    for axis, local_size in zip(world_axes, local_sizes):
        axis_length = axis.length
        world_sizes.append(abs(local_size * axis_length))
        normalized_axes.append(axis.normalized() if axis_length > 1.0e-8 else Vector((0.0, 0.0, 0.0)))

    if normalized_axes[0].length == 0.0 or normalized_axes[1].length == 0.0:
        rotation = world_matrix.to_euler('XYZ')
    else:
        normalized_axes[2] = normalized_axes[0].cross(normalized_axes[1]).normalized()
        if normalized_axes[2].length == 0.0:
            normalized_axes[2] = (world_linear @ local_axis_z).normalized()
        normalized_axes[1] = normalized_axes[2].cross(normalized_axes[0]).normalized()
        rotation_matrix = Matrix((
            (normalized_axes[0].x, normalized_axes[1].x, normalized_axes[2].x),
            (normalized_axes[0].y, normalized_axes[1].y, normalized_axes[2].y),
            (normalized_axes[0].z, normalized_axes[1].z, normalized_axes[2].z),
        ))
        rotation = rotation_matrix.to_euler('XYZ')

    return world_center, Vector(world_sizes), rotation


def _fallback_object_bounds_collider_values(obj: bpy.types.Object):
    # メッシュ頂点が取得できない場合だけ従来のobj.bound_box計算へフォールバックする。
    bb_local = [Vector(corner) for corner in obj.bound_box]
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

    local_center = (min_local + max_local) * 0.5
    local_size = max_local - min_local
    world_scale = obj.matrix_world.to_scale()

    center = obj.matrix_world @ local_center
    size = Vector((
        local_size.x * abs(world_scale.x),
        local_size.y * abs(world_scale.y),
        local_size.z * abs(world_scale.z),
    ))
    rotation = obj.matrix_world.to_euler('XYZ')
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
