import bpy
import os
import bpy.ops

# オペレーター 出現ポイントのシンボルを読み込む
class MYADDON_OT_spawn_point(bpy.types.Operator):
    bl_idname = "myaddon.spawn_point"
    bl_label = "出現ポイントシンボルImport"
    bl_description = "出現ポイントシンボルImportします"

    prototype_object_name = "PlayerSpawnPoint"

    def execute(self, context):
        print("出現ポイントシンボルをインポートします")

        # 重複ロード防止
        if bpy.data.objects.get(MYADDON_OT_spawn_point.prototype_object_name) is not None:
            return {'CANCELLED'}

        # スクリプトファイルの場所を取得（level_editor）
        script_dir = os.path.dirname(__file__)

        # 同じフォルダ内のファイルを指定
        model_path = os.path.abspath(os.path.join(script_dir, "PlayerStateModel","PlayerIdleState.gltf"))

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

    object_name = "SpawnPoint"

    def execute(self, context):
        # 読み込み済みの出現ポイントシンボルを取得
        spawn_point_object = bpy.data.objects.get(MYADDON_OT_spawn_point.prototype_object_name)

        # まだ読み込んでいない場合
        if spawn_point_object is None:
            # 読み込みオペレータを実行
            bpy.ops.myaddon.spawn_point("EXEC_DEFAULT")
            # 再探索、今度は確実に取得できるはず
            spawn_point_object = bpy.data.objects.get(MYADDON_OT_spawn_point.prototype_object_name)

            print("出現ポイントシンボルを読み込みました")

            # Blenderでの選択を解除する
            bpy.ops.object.select_all(action='DESELECT')

            # 複製元の非表示オブジェクトを複製する
            object = spawn_point_object.copy()

            # 複製したオブジェクトを現在のシーンにリンク（出現させる）
            bpy.context.collection.objects.link(object)

            # オブジェクト名を設定
            object.name = MYADDON_OT_create_spawn_point.object_name

            return {'FINISHED'}