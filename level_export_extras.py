# level_export_extras.py
from __future__ import annotations

from typing import Any, Dict, Optional

# Jsonに直接入れてOKな型
_JSON_PRIMITIVES = (int, float, str, bool)

# exporter側で予約しているキー
RESERVED_CUSTOM_KEYS = {
    "type", "name", "disable", "file_name", "collider",
    "transform", "children"
}

def extract_collections(obj) -> Dict[str, Any]:
    """ オブジェクトのコレクションを抽出して辞書形式で返す。
    obj が属しているコレクション名をJSONに入れたいときに使用します。
    - collection : 代表１つ
    - collections : 全て（リスト）
    """
    cols = [c.name for c in getattr(obj, "users_collection", [])]
    out: Dict[str, Any] = {}
    if cols:
        out["collection"] = cols[0]
        out["collections"] = cols
    return out

def _to_jsonable(v: Any) -> Optional[Any]:
    """
    BlenderのCustom Propertyの値をJsonに入れられる形にする。
    対応:
    - int / float / str / bool
    - 配列 / リスト / タプル (中身が数値ならlist化)
    """
    if isinstance(v, _JSON_PRIMITIVES):
        return v
    
    # IDプロパティの配列（例: Vector, Colorなど）
    if hasattr(v, "__iter__") and not isinstance(v, (str, bytes)):
        try:
            arr = list(v)
            # 数値配列だけ許可
            if all(isinstance(x, (int, float)) for x in arr):
                return [float(x) for x in arr]
        except Exception:
            return None

    return None

def extract_props(obj) -> Dict[str, Any]:
    """
    Custom Propertiesをpropsにまとめて抽出する。
    予約キーは除外
    """
    props: Dict[str, Any] = {}
    # obj.items() はCustom Propertiesのみを返す
    for k, v in obj.items():
        if k in RESERVED_CUSTOM_KEYS:
            continue
        jsonable = _to_jsonable(v)
        if jsonable is not None:
            props[k] = jsonable
    
    return props