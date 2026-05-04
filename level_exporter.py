# level_exporter.py
import math
from .level_schema import SCHEMA_VERSION, DEFAULT_META
from .level_export_extras import extract_collections, extract_props


VALID_STAGE_MODES = {"Unknown", "Wave", "Explore", "Defend", "Escape", "Boss"}

TYPE_NORMALIZE_MAP = {
    "PlayerSpawnPoint": "PlayerSpawn",
    "EnemySpawnPoint": "EnemySpawn",
    "EscapePoint": "EscapeGoal",
    "DefenseTarget": "DefendTarget",
    "BossEventPoint": "BossSpawn",
}


def _normalize_type(raw_type: str) -> str:
    return TYPE_NORMALIZE_MAP.get(raw_type, raw_type)


def _resolve_stage_mode(scene):
    mode = getattr(scene, "level_stage_mode", None)
    if not mode:
        mode = scene.get("stage_mode", "Unknown") if hasattr(scene, "get") else "Unknown"

    mode = str(mode) if mode is not None else "Unknown"
    if mode not in VALID_STAGE_MODES:
        return "Unknown"
    return mode


def _categorize_entity(obj_dict):
    t = obj_dict.get("type")
    if t == "PlayerSpawn":
        return "player_spawns"
    if t == "EnemySpawn":
        return "enemy_spawns"
    if t == "DefendTarget":
        return "defend_targets"
    if t == "EscapeGoal":
        return "escape_goals"
    if t == "BossSpawn":
        return "boss_spawns"
    if t == "DefenseArea":
        return "boss_areas"
    if t == "Trigger":
        return "triggers"
    if "collider" in obj_dict:
        return "collisions"
    return "items"


# シーンからレベルデータをエクスポートする関数
def export_level_dict(scene):

    # ルートデータ構造の初期化
    root = {
        "schema_version": SCHEMA_VERSION,
        "meta": dict(DEFAULT_META),  # メタデータは必要に応じてシーンから取得して上書きする
        "stage": {
            "id": scene.name,
            "mode": _resolve_stage_mode(scene),
        },
        "name": "scene",
        "objects": [],
        "entities": {
            "player_spawns": [],
            "enemy_spawns": [],
            "items": [],
            "defend_targets": [],
            "escape_goals": [],
            "boss_spawns": [],
            "boss_areas": [],
            "triggers": [],
            "collisions": [],
        },
    }

    # シーン内の全オブジェクトを処理
    for obj in scene.objects:
        if obj.parent:
            continue  # 子オブジェクトは親オブジェクトの一部として処理されるためスキップ

        obj_dict = _object_to_dict(obj)
        if obj_dict is not None:
            root["objects"].append(obj_dict)
            key = _categorize_entity(obj_dict)
            root["entities"][key].append(obj_dict)
        # else:
        #     print(f"[LevelExport] skipped (None): {obj.name}")

    return root


# オブジェクトを辞書形式に変換する関数
def _object_to_dict(obj):
    d = {}

    # type (カスタム優先) + 正規化
    raw_type = obj["type"] if "type" in obj else obj.type
    d["type"] = _normalize_type(str(raw_type))
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
        d["model"] = file_name

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
