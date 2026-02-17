import bpy
import os
import bpy.ops
from bpy.props import StringProperty

# ユニークな名前を作る関数
def make_unique_name(base_name: str) -> str:
    """base_name_001, base_name_002, ... のようにユニークな名前を生成する"""
    existing_names = {obj.name for obj in bpy.data.objects}
    index = 1
    while True:
        candidate = f"{base_name}_{index:03d}"
        if candidate not in existing_names:
            return candidate
        index += 1

# オペレーター 出現ポイントのシンボルを読み込む
class MYADDON_OT_spawn_point(bpy.types.Operator):
    bl_idname = "myaddon.spawn_point"
    bl_label = "出現ポイントシンボルImport"
    bl_description = "出現ポイントシンボルImportします"

    # プロトタイプ用オブジェクト名（非表示の元モデル）
    prototype_object_name = "PlayerSpawnPoint"

    def execute(self, context):
        print("出現ポイントシンボルをインポートします")

        # 重複ロード防止
        if bpy.data.objects.get(MYADDON_OT_spawn_point.prototype_object_name) is not None:
            return {'CANCELLED'}

        # スクリプトファイルの場所を取得（level_editor）
        script_dir = os.path.dirname(__file__)

        # 同じフォルダ内のファイルを指定
        model_path = os.path.abspath(os.path.join(script_dir, "Resources/Models/","cube.gltf"))

        # デバッグ出力
        print(f"モデルパス: {model_path}")

        # ファイル存在確認（エラー回避用）
        if not os.path.exists(model_path):
            self.report({'ERROR'}, f"ファイルが存在しません: {model_path}")
            return {'CANCELLED'}

        # モデルをインポート
        bpy.ops.import_scene.gltf(filepath=model_path)

        # 読み込んだオブジェクトを取得（最後に追加された1つを想定）
        import_object = bpy.context.selected_objects[0]

        # ローカル回転をゼロに固定する or 変換適用
        bpy.context.view_layer.objects.active = import_object
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

        # オブジェクトの名前を設定
        import_object.name = self.prototype_object_name

        # カスタムプロパティの追加（レベルエディタで使いたい場合）
        import_object["type"] = self.prototype_object_name

        # メモリ上に置いておくがシーンからは削除
        bpy.context.collection.objects.unlink(import_object)

        return {'FINISHED'}

# オペレータ 出現ポイントのシンボルを作成・配置する
class MYADDON_OT_create_spawn_point(bpy.types.Operator):
    bl_idname = "myaddon.create_spawn_point"
    bl_label = "出現ポイントシンボルを配置"
    bl_description = "出現ポイントシンボルを配置します"
    bl_options = {'REGISTER', 'UNDO'}

    object_name: StringProperty(
        name="Spawn name",
        description="SpwanPointの名前を指定します",
    )

    def execute(self, context):
        # プロトタイプ取得
        spawn_point_object = bpy.data.objects.get(MYADDON_OT_spawn_point.prototype_object_name)

        # まだ読み込んでいない場合はインポート
        if spawn_point_object is None:
            bpy.ops.myaddon.spawn_point("EXEC_DEFAULT")
            spawn_point_object = bpy.data.objects.get(MYADDON_OT_spawn_point.prototype_object_name)

        # それでも取れなければエラー
        if spawn_point_object is None:
            self.report({'ERROR'}, "SpawnPointのプロトタイプが取得できませんでした。")
            return {'CANCELLED'}

        # ここからは「毎回必ず」実行される複製処理
        bpy.ops.object.select_all(action='DESELECT')

        new_obj = spawn_point_object.copy()
        bpy.context.collection.objects.link(new_obj)

        # ユニークな名前を付与
        base_type = self.object_name

        new_obj.name = make_unique_name(base_type)

        return {'FINISHED'}
