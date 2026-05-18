import bpy, math, mathutils, gpu
import gpu_extras.batch as batch
from .collider_types import COL_BOX, COL_SPHERE, COL_CYLINDER, COL_CAPSULE

def _draw_lines(verts, edges, color=(0.5,1.0,1.0,1.0)):
    sh = gpu.shader.from_builtin("UNIFORM_COLOR")
    b  = batch.batch_for_shader(sh, "LINES", {"pos": verts}, indices=edges)
    sh.bind(); sh.uniform_float("color", color)
    b.draw(sh)

# （…各形状のワイヤ生成関数は既存の方針でOK…）

# Boxのワイヤを追加
def _add_box(mat_world, center, size, out_vertices, out_indices):
    """
    center: mathutils.Vector(3)
    size  : mathutils.Vector(3)
    out_vertices: list[mathutils.Vector]
    out_indices : list[tuple[int,int]]
    """
    offsets = [
        (-0.5, -0.5, -0.5), ( 0.5, -0.5, -0.5),
        (-0.5,  0.5, -0.5), ( 0.5,  0.5, -0.5),
        (-0.5, -0.5,  0.5), ( 0.5, -0.5,  0.5),
        (-0.5,  0.5,  0.5), ( 0.5,  0.5,  0.5),
    ]
    base = len(out_vertices)

    # 8頂点を追加
    for ox, oy, oz in offsets:
        p = mathutils.Vector((
            center.x + ox * size.x,
            center.y + oy * size.y,
            center.z + oz * size.z,
        ))
        out_vertices.append(mat_world @ p)

    # 12本の辺を1回だけ追加（←重要：頂点ループの外でやる）
    edges = [
        (0,1),(2,3),(0,2),(1,3),      # 前面
        (4,5),(6,7),(4,6),(5,7),      # 背面
        (0,4),(1,5),(2,6),(3,7),      # 前後を結ぶ
    ]
    for a,b in edges:
        out_indices.append((base + a, base + b))

# Sphereのワイヤを追加
def _add_circle(center, radius, axis, segments, mat_world, out_vertices, out_indices):
    """
    axis: 'X' | 'Y' | 'Z' ・・・円の法線方向
    """
    base = len(out_vertices)
    for i in range(segments):
        t = 2.0 * math.pi * (i / segments)
        if axis == 'X':
            p = mathutils.Vector((center.x,
                                  center.y + radius * math.cos(t),
                                  center.z + radius * math.sin(t)))
        elif axis == 'Y':
            p = mathutils.Vector((center.x + radius * math.cos(t),
                                  center.y,
                                  center.z + radius * math.sin(t)))
        else:  # 'Z'
            p = mathutils.Vector((center.x + radius * math.cos(t),
                                  center.y + radius * math.sin(t),
                                  center.z))
        out_vertices.append(mat_world @ p)
    for i in range(segments):
        out_indices.append((base + i, base + ((i + 1) % segments)))

def _add_sphere(mat_world, center, radius, out_vertices, out_indices):
    seg = 32  # 見やすさと軽さのバランス
    c = mathutils.Vector(center)
    _add_circle(c, radius, 'X', seg, mat_world, out_vertices, out_indices)
    _add_circle(c, radius, 'Y', seg, mat_world, out_vertices, out_indices)
    _add_circle(c, radius, 'Z', seg, mat_world, out_vertices, out_indices)



# 既存の draw_handler() をこの分岐で拡張
def draw_handler():
    verts = []
    edges = []

    for obj in bpy.context.scene.objects:
        col = getattr(obj, "collider", None)
        if not col or not col.enabled:
            continue
        if col.type == COL_BOX:
            # 保存済みのワールド中心・サイズ・回転からBox Colliderの描画行列を組み立てる。
            c = mathutils.Vector(col.center)
            s = mathutils.Vector(col.size)
            rot = mathutils.Euler(col.rotation, 'XYZ').to_matrix().to_4x4()
            mat_world = mathutils.Matrix.Translation(c) @ rot
            _add_box(mat_world, mathutils.Vector((0.0, 0.0, 0.0)), s, verts, edges)

        elif col.type == COL_SPHERE:
            # Sphere Colliderも保存済みのワールド中心と半径で描画する。
            mat_world = mathutils.Matrix.Identity(4)
            _add_sphere(mat_world, col.center, float(col.radius), verts, edges)

    if verts:
        _draw_lines(verts, edges)

_handle = None
def enable():
    global _handle
    if not _handle:
        _handle = bpy.types.SpaceView3D.draw_handler_add(draw_handler, (), "WINDOW", "POST_VIEW")

def disable():
    global _handle
    if _handle:
        bpy.types.SpaceView3D.draw_handler_remove(_handle, "WINDOW")
        _handle = None
