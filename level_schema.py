# level_schema.py
SCHEMA_VERSION = 2

# メタデータのデフォルト値
DEFAULT_META = {
    "units": "m",           # モデルの単位（m, cm, mmなど）
    "rotation_unit": "deg", # 回転の単位（deg, radなど）
    "source_forward": "+Y", # モデルの前方（+X, -X, +Y, -Y, +Z, -Z）
    "source_up": "+Z",      # モデルの上方向（+X, -X, +Y, -Y, +Z, -Z）
    "game_forward": "+Z",   # ゲームエンジンでの前方（+X, -X, +Y, -Y, +Z, -Z）
    "game_up": "+Y",        # ゲームエンジンでの上方向（+X, -X, +Y, -Y, +Z, -Z）
}