# level_exporter.py
import math
from .level_schema import SCHEMA_VERSION, DEFAULT_META
from .level_export_extras import extract_collections, extract_props

# シーンからレベルデータをエクスポートする関数
def export_level_dict(scene):

    # ルートデータ構造の初期化
    root = {
        "schema_version": SCHEMA_VERSION,
        "meta": dict(DEFAULT_META),  # メタデータは必要に応じてシーンから取得して上書きする
        "name": "scene",
        "objects": [],
    }

    # シーン内の全オブジェクトを処理
    for obj in scene.objects:
        if obj.parent:
            continue  # 子オブジェクトは親オブジェクトの一部として処理されるためスキップ
       
        obj_dict = _object_to_dict(obj)
        if obj_dict is not None:
            root["objects"].append(obj_dict)
        # else:
        #     print(f"[LevelExport] skipped (None): {obj.name}")

    return root

# オブジェクトを辞書形式に変換する関数
def _object_to_dict(obj):
    d = {}

    # type (カスタム優先)
    d["type"] = obj["type"] if "type" in obj else obj.type
    d["name"] = obj.name

    # collection / collections
    d.update(extract_collections(obj))

    # 位置、回転、スケール
    trans, rot, scale = obj.matrix_local.decompose()
    rot = rot.to_euler()
    d["transform"] = {
        "translation": [float(trans.x), float(trans.y), float(trans.z)],
        "rotation": [math.degrees(rot.x), math.degrees(rot.y), math.degrees(rot.z)],
        "scaling": [float(scale.x), float(scale.y), float(scale.z)],
    }

    # disable
    if "disable" in obj:
        d["disable"] = bool(obj["disable"])
    
    # file_name (カスタム優先)
    file_name = obj.get("file_name", "")  # Custom Properties
    if not file_name:
        # 旧方式の保険（使ってなければ空のままでOK）
        file_name = getattr(obj, "file_name", "")

    file_name = str(file_name).strip()
    if file_name:
        d["file_name"] = file_name

    # Collider
    col = getattr(obj, "collider", None)
    if col and col.enabled:
        c = {
            "type": str(col.type),
            "center": [float(col.center[0]), float(col.center[1]), float(col.center[2])],
        }
        if col.type == "BOX":
            c["size"] = [float(col.size[0]), float(col.size[1]), float(col.size[2])]
        else:
            c["radius"] = float(col.radius)
            if col.type in ["CAPSULE", "CYLINDER"]:
                c["height"] = float(col.height)
        d["collider"] = c

    # Custom Properties
    props = extract_props(obj)
    if props:
        d["props"] = props

    # 子オブジェクト
    if obj.children:
        children = []
        for ch in obj.children:
            ch_dict = _object_to_dict(ch)
            if ch_dict is not None:
                children.append(ch_dict)
            else:
                print(f"[LevelExport] skipped child (None): {ch.name} of parent {obj.name}")
        
        if children:
            d["children"] = children

    return d