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
                obj_type = obj_data.get("type", "EMPTY")
                obj_name = obj_data.get("name", "ImportedObject")

                obj = None

                # --------------------------------------------------
                # オブジェクト生成
                # --------------------------------------------------
                if obj_type in {"MESH", "StaticMesh"}:
                    bpy.ops.mesh.primitive_cube_add()
                    obj = bpy.context.object

                elif obj_type in {
                    "PlayerSpawnPoint",
                    "EnemySpawnPoint",
                    "BossSpawnPoint",
                    "IntroCameraPoint",
                    "IntroLookAtPoint",
                    "Trigger",
                }:
                    bpy.ops.object.empty_add(type='ARROWS')
                    obj = bpy.context.object

                else:
                    # 未知の type も Empty で受ける
                    bpy.ops.object.empty_add(type='PLAIN_AXES')
                    obj = bpy.context.object

                if obj is None:
                    continue

                obj.name = obj_name
                obj["type"] = obj_type

                if parent:
                    obj.parent = parent

                # --------------------------------------------------
                # Transform
                # --------------------------------------------------
                transform = obj_data.get("transform", {})

                loc = transform.get("translation", [0.0, 0.0, 0.0])
                rot_deg = transform.get("rotation", [0.0, 0.0, 0.0])
                scale = transform.get("scaling", [1.0, 1.0, 1.0])

                collider = obj_data.get("collider")
                if collider is not None:
                    center = collider.get("center")
                    if center is not None:
                        loc = center

                    col_type = collider.get("type", "BOX")
                    if col_type == "BOX" and "size" in collider:
                        size = collider["size"]
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
                        scale = [r, r, h * 0.5]

                obj.location = loc
                obj.rotation_euler = [math.radians(angle) for angle in rot_deg]
                obj.scale = scale

                # --------------------------------------------------
                # Custom Properties
                # --------------------------------------------------
                if "file_name" in obj_data:
                    obj["file_name"] = obj_data["file_name"]

                if "props" in obj_data and isinstance(obj_data["props"], dict):
                    for k, v in obj_data["props"].items():
                        obj[k] = v

                if "collider" in obj_data:
                    obj["collider"] = obj_data["collider"]
                    if "center" in obj_data["collider"]:
                        obj["collider_center"] = obj_data["collider"]["center"]
                    if "size" in obj_data["collider"]:
                        obj["collider_size"] = obj_data["collider"]["size"]

                # --------------------------------------------------
                # 子オブジェクト
                # --------------------------------------------------
                if "children" in obj_data:
                    import_object(obj_data["children"], parent=obj)

        import_object(data["objects"])

    def execute(self, context):
        """オペレーター実行時の処理"""
        print("シーン情報をImportします")
        self.import_json()
        self.report({'INFO'}, "シーン情報をImportしました")
        print("シーン情報をImportしました")
        return {'FINISHED'}
        