import bpy
import json
import math
from bpy_extras.io_utils import ImportHelper

# オペレータ シーンの入力
class MYADDON_OT_import_scene(bpy.types.Operator, ImportHelper):
    bl_idname = "myaddon.myaddon_ot_import_scene"
    bl_label = "シーン入力"
    bl_description = "シーン情報をImportします"
    filename_ext = ".json"

    def read_json(self):
        """JSON形式でファイルからデータを読み込む"""
        with open(self.filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data

    def import_json(self):
        """JSON形式のデータをBlenderシーンにインポート"""
        data = self.read_json()
        if data["name"] != "scene":
            raise ValueError("Invalid JSON format")

        def import_object(data, parent=None):
            """データからオブジェクトを作成し、Blenderに追加"""
            for obj_data in data:
                obj_type = obj_data["type"]
                obj_name = obj_data["name"]

                # 新しいオブジェクトを作成
                if obj_type == 'MESH':
                    bpy.ops.mesh.primitive_cube_add()  # 仮でキューブを追加
                    obj = bpy.context.object
                else:
                    continue  # 他の型については未対応

                obj.name = obj_name
                if parent:
                    obj.parent = parent

                # トランスフォームの設定
                transform = obj_data["transform"]
                obj.location = transform["translation"]
                obj.rotation_euler = [math.radians(angle) for angle in transform["rotation"]]
                obj.scale = transform["scaling"]

                # カスタムプロパティの設定
                if "file_name" in obj_data:
                    obj["file_name"] = obj_data["file_name"]
                if "collider" in obj_data:
                    obj["collider"] = obj_data["collider"]
                    obj["collider_center"] = obj_data["collider"]["center"]
                    obj["collider_size"] = obj_data["collider"]["size"]

                # 子オブジェクトのインポート
                if "children" in obj_data:
                    for child_data in obj_data["children"]:
                        import_object([child_data], parent=obj)

        import_object(data["objects"])

    def execute(self, context):
        """オペレーター実行時の処理"""
        print("シーン情報をImportします")
        self.import_json()
        self.report({'INFO'}, "シーン情報をImportしました")
        print("シーン情報をImportしました")
        return {'FINISHED'}
        