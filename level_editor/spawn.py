import bpy
import os
import bpy.ops
from bpy.props import StringProperty, EnumProperty, IntProperty

# ユニークな名前を作る関数
def make_unique_name(base_name: str) -> str:
    existing_names = {obj.name for obj in bpy.data.objects}
    index = 1
    while True:
        candidate = f"{base_name}_{index:03d}"
        if candidate not in existing_names:
            return candidate
        index += 1


LEVEL_TYPE_ITEMS = [
    ("PlayerSpawnPoint", "PlayerSpawnPoint", "プレイヤースポーン"),
    ("EnemySpawnPoint",  "EnemySpawnPoint",  "敵スポーン"),
    ("BossSpawnPoint",   "BossSpawnPoint",   "ボススポーン"),
    ("StaticMesh",       "StaticMesh",       "描画メッシュ（file_name必須）"),
    ("Trigger",          "Trigger",          "トリガー"),
]

SPAWN_PROP_TYPES = {"EnemySpawnPoint", "BossSpawnPoint"}


class MYADDON_OT_spawn_point(bpy.types.Operator):
    bl_idname = "myaddon.spawn_point"
    bl_label = "出現ポイントシンボルImport"
    bl_description = "出現ポイントシンボルをImportします"

    prototype_object_name = "__SpawnPointPrototype__"

    def execute(self, context):
        if bpy.data.objects.get(self.prototype_object_name) is not None:
            return {'FINISHED'}

        script_dir = os.path.dirname(__file__)
        model_path = os.path.abspath(
            os.path.join(script_dir, "Resources/Models/", "cube.gltf")
        )

        if not os.path.exists(model_path):
            self.report({'ERROR'}, f"ファイルが存在しません: {model_path}")
            return {'CANCELLED'}

        bpy.ops.import_scene.gltf(filepath=model_path)

        if not bpy.context.selected_objects:
            self.report({'ERROR'}, "gltfのインポートに失敗しました。")
            return {'CANCELLED'}

        import_object = bpy.context.selected_objects[0]
        bpy.context.view_layer.objects.active = import_object
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

        import_object.name = self.prototype_object_name
        import_object["type"] = "Prototype"

        # シーンから外してプロトタイプ化
        bpy.context.collection.objects.unlink(import_object)
        return {'FINISHED'}


class MYADDON_OT_create_spawn_point(bpy.types.Operator):
    bl_idname = "myaddon.create_spawn_point"
    bl_label = "レベルオブジェクトを配置"
    bl_description = "選択したTypeでレベル用オブジェクトを配置します"
    bl_options = {'REGISTER', 'UNDO'}

    spawn_type: EnumProperty(
        name="Type",
        items=LEVEL_TYPE_ITEMS,
        default="EnemySpawnPoint"
    )

    object_name: StringProperty(
        name="Name Prefix",
        description="名前のプレフィックス（例: EnemySpawn / PlayerSpawn / BossSpawn）",
        default="Obj"
    )

    wave: IntProperty(name="Wave", default=1, min=0)
    group: IntProperty(name="Group", default=0, min=0)
    count: IntProperty(name="Count", default=1, min=0)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "spawn_type")
        layout.prop(self, "object_name")

        if self.spawn_type in SPAWN_PROP_TYPES:
            col = layout.column(align=True)
            col.prop(self, "wave")
            col.prop(self, "group")
            col.prop(self, "count")

    def execute(self, context):
        spawn_point_object = bpy.data.objects.get(MYADDON_OT_spawn_point.prototype_object_name)

        if spawn_point_object is None:
            bpy.ops.myaddon.spawn_point("EXEC_DEFAULT")
            spawn_point_object = bpy.data.objects.get(MYADDON_OT_spawn_point.prototype_object_name)

        if spawn_point_object is None:
            self.report({'ERROR'}, "プロトタイプが取得できませんでした。")
            return {'CANCELLED'}

        bpy.ops.object.select_all(action='DESELECT')

        new_obj = spawn_point_object.copy()
        bpy.context.collection.objects.link(new_obj)

        # 3Dカーソル位置に配置
        new_obj.location = context.scene.cursor.location.copy()

        # type を反映
        new_obj["type"] = self.spawn_type

        # 既存props掃除
        for k in ("wave", "group", "count"):
            if k in new_obj:
                del new_obj[k]

        # Enemy / Boss のみ wave系を持たせる
        if self.spawn_type in SPAWN_PROP_TYPES:
            new_obj["wave"] = int(self.wave)
            new_obj["group"] = int(self.group)
            new_obj["count"] = int(self.count)

        # ユニーク名
        new_obj.name = make_unique_name(self.object_name)

        bpy.context.view_layer.objects.active = new_obj
        new_obj.select_set(True)

        return {'FINISHED'}


classes = (
    MYADDON_OT_spawn_point,
    MYADDON_OT_create_spawn_point,
)


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)