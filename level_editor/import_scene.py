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

                # 基本は transform の値を使う
                loc = transform["translation"]
                rot_deg = transform["rotation"]
                scale = transform["scaling"]

                # collider 情報がある場合は、そちらを優先して
                # 位置 / 大きさを決める
                collider = obj_data.get("collider")
                if collider is not None:
                    # 位置：collider.center を使う
                    center = collider.get("center")
                    if center is not None:
                        loc = center

                    # 大きさ：collider.size / radius から scale を決める
                    col_type = collider.get("type", "BOX")
                    if col_type == "BOX" and "size" in collider:
                        size = collider["size"]
                        # Blender のデフォルトキューブは 2x2x2 なので、
                        # 半分がスケールになる
                        scale = [
                            size[0] * 0.5,
                            size[1] * 0.5,
                            size[2] * 0.5,
                        ]
                    elif col_type == "SPHERE" and "radius" in collider:
                        r = collider["radius"]
                        scale = [r, r, r]
                    elif col_type in {"CYLINDER", "CAPSULE"} and \
                            "radius" in collider and "height" in collider:
                        r = collider["radius"]
                        h = collider["height"]
                        # デフォルトの Cylinder は半径1, 高さ2なので、高さは半分
                        scale = [r, r, h * 0.5]

                # 計算した loc / rot / scale をオブジェクトに適用
                obj.location = loc
                obj.rotation_euler = [math.radians(angle) for angle in rot_deg]
                obj.scale = scale

                # カスタムプロパティの設定
                if "file_name" in obj_data:
                    obj["file_name"] = obj_data["file_name"]
                if "collider" in obj_data:
                    obj["collider"] = obj_data["collider"]
                    obj["collider_center"] = obj_data["collider"]["center"]
                    if "size" in obj_data["collider"]:
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
        