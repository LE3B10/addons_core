import bpy
from bpy.props import EnumProperty, StringProperty, IntProperty, BoolProperty, FloatProperty

LEVEL_TYPE_ITEMS = [
    ("StaticMesh",       "StaticMesh",       "描画するメッシュ（file_name必須）"),
    ("PlayerSpawnPoint", "PlayerSpawnPoint", "プレイヤースポーン"),
    ("EnemySpawnPoint",  "EnemySpawnPoint",  "敵スポーン"),
    ("BossSpawnPoint",   "BossSpawnPoint",   "ボススポーン"),
    ("IntroCameraPoint", "IntroCameraPoint", "開始演出カメラポイント"),
    ("IntroLookAtPoint", "IntroLookAtPoint", "開始演出注視ポイント"),
    ("Trigger",          "Trigger",          "トリガー"),
]

ENEMY_ARCHETYPE_ITEMS = [
    ("RifleGrunt",     "RifleGrunt",    "標準的なライフル兵"),
    ("SMGFlanker",     "SMGFlanker",    "近距離寄りの回り込み役"),
    ("Sniper",         "Sniper",        "遠距離単発高精度"),
    ("BurstTrooper",   "BurstTrooper",  "3～4点バーストよりの中距離兵"),
    ("HeavyRifleman",  "HeavyRifleman", "遅い・硬い・やや高火力"),
    ("ShotgunRusher",  "ShotgunRusher", "近距離まで詰めてくる突撃兵"),
    ("Scout",          "Scout",         "速い・柔らかい・発見しやすい軽量兵"),
    ("Marksman",       "Marksman",      "Sniperより軽い中距離兵"),
    ("Suppressor",     "Suppressor",    "弾幕で圧をかける支援兵"),
    ("EliteFlanker",   "EliteFlanker",  "SMGFlankerの上位互換"),
    ("HeavySniper",    "HeavySniper",   "発射は遅いが高火力重狙撃兵"),
]

SPAWN_POINT_TYPES = {"PlayerSpawnPoint", "EnemySpawnPoint", "BossSpawnPoint"}
WAVE_EDIT_TYPES = {"EnemySpawnPoint", "BossSpawnPoint"}
INTRO_CAMERA_TYPES = {"IntroCameraPoint", "IntroLookAtPoint"}


def _get_cp(obj, key, default):
    return obj.get(key, default)


def _set_cp(obj, key, value):
    obj[key] = value


def register_object_props():
    def get_level_type(self):
        return _get_cp(self, "type", "StaticMesh")

    def set_level_type(self, v):
        _set_cp(self, "type", v)

    def get_file_name(self):
        return _get_cp(self, "file_name", "")

    def set_file_name(self, v):
        _set_cp(self, "file_name", v)

    def get_disable(self):
        return bool(_get_cp(self, "disable", False))

    def set_disable(self, v):
        _set_cp(self, "disable", bool(v))

    def get_wave(self):
        return int(_get_cp(self, "wave", 0))

    def set_wave(self, v):
        _set_cp(self, "wave", int(v))

    def get_group(self):
        return int(_get_cp(self, "group", 0))

    def set_group(self, v):
        _set_cp(self, "group", int(v))

    def get_count(self):
        return int(_get_cp(self, "count", 0))

    def set_count(self, v):
        _set_cp(self, "count", int(v))

    def get_archetype(self):
        return str(_get_cp(self, "archetype", "RifleGrunt"))

    def set_archetype(self, v):
        _set_cp(self, "archetype", v)

    def get_order(self):
        return int(_get_cp(self, "order", 0))

    def set_order(self, v):
        _set_cp(self, "order", int(v))

    def get_duration(self):
        return float(_get_cp(self, "duration", 1.5))

    def set_duration(self, v):
        _set_cp(self, "duration", float(v))

    def get_fov(self):
        return float(_get_cp(self, "fov", 45.0))

    def set_fov(self, v):
        _set_cp(self, "fov", float(v))

    def get_target_name(self):
        return str(_get_cp(self, "target_name", ""))

    def set_target_name(self, v):
        _set_cp(self, "target_name", str(v))

    bpy.types.Object.level_type = EnumProperty(
        name="Type",
        items=LEVEL_TYPE_ITEMS,
        get=get_level_type,
        set=set_level_type
    )
    bpy.types.Object.level_file_name = StringProperty(
        name="File Name",
        description="例: stage/wall_01.gltf",
        get=get_file_name,
        set=set_file_name
    )
    bpy.types.Object.level_disable = BoolProperty(
        name="Disable",
        get=get_disable,
        set=set_disable
    )

    bpy.types.Object.level_wave = IntProperty(
        name="Wave",
        min=0,
        get=get_wave,
        set=set_wave
    )
    bpy.types.Object.level_group = IntProperty(
        name="Group",
        min=0,
        get=get_group,
        set=set_group
    )
    bpy.types.Object.level_count = IntProperty(
        name="Count",
        min=0,
        get=get_count,
        set=set_count
    )

    bpy.types.Object.level_archetype = EnumProperty(
        name="Archetype",
        items=ENEMY_ARCHETYPE_ITEMS,
        get=get_archetype,
        set=set_archetype
    )

    bpy.types.Object.level_order = IntProperty(
        name="Order",
        min=0,
        get=get_order,
        set=set_order
    )
    bpy.types.Object.level_duration = FloatProperty(
        name="Duration",
        min=0.0,
        get=get_duration,
        set=set_duration
    )
    bpy.types.Object.level_fov = FloatProperty(
        name="FOV",
        min=1.0,
        max=179.0,
        get=get_fov,
        set=set_fov
    )
    bpy.types.Object.level_target_name = StringProperty(
        name="Target Name",
        description="注視先オブジェクト名。例: IntroLook_001",
        get=get_target_name,
        set=set_target_name
    )


def unregister_object_props():
    for n in (
        "level_type",
        "level_file_name",
        "level_disable",
        "level_wave",
        "level_group",
        "level_count",
        "level_order",
        "level_duration",
        "level_fov",
        "level_target_name",
        "level_archetype",
    ):
        if hasattr(bpy.types.Object, n):
            delattr(bpy.types.Object, n)


class VIEW3D_PT_level_object(bpy.types.Panel):
    bl_label = "Level Object"
    bl_idname = "VIEW3D_PT_level_object"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Level"

    def draw(self, context):
        layout = self.layout
        obj = context.object

        if obj is None:
            layout.label(text="オブジェクトを選択してください")
            return

        layout.prop(obj, "level_type")
        layout.prop(obj, "level_disable")

        if obj.level_type == "StaticMesh":
            layout.prop(obj, "level_file_name")

        if obj.level_type in WAVE_EDIT_TYPES:
            col = layout.column(align=True)
            col.label(text="Spawn Props")
            col.prop(obj, "level_wave")
            col.prop(obj, "level_group")
            col.prop(obj, "level_count")

            if obj.level_type == "EnemySpawnPoint":
                col.prop(obj, "level_archetype")

        if obj.level_type == "IntroCameraPoint":
            col = layout.column(align=True)
            col.label(text="Intro Camera Props")
            col.prop(obj, "level_order")
            col.prop(obj, "level_duration")
            col.prop(obj, "level_fov")
            col.prop(obj, "level_target_name")

        layout.separator()

        if obj.level_type in SPAWN_POINT_TYPES:
            op = layout.operator("myaddon.create_spawn_point", text="SpawnPointを配置")
            op.spawn_type = obj.level_type

            if obj.level_type == "PlayerSpawnPoint":
                op.object_name = "PlayerSpawn"
            elif obj.level_type == "EnemySpawnPoint":
                op.object_name = "EnemySpawn"
            elif obj.level_type == "BossSpawnPoint":
                op.object_name = "BossSpawn"

        elif obj.level_type in INTRO_CAMERA_TYPES:
            op = layout.operator("myaddon.create_intro_camera_point", text="Intro Pointを配置")
            op.point_type = obj.level_type

            if obj.level_type == "IntroCameraPoint":
                op.object_name = "IntroCam"
                op.order = getattr(obj, "level_order", 0)
                op.duration = getattr(obj, "level_duration", 1.5)
                op.fov = getattr(obj, "level_fov", 45.0)
                op.target_name = getattr(obj, "level_target_name", "")
            elif obj.level_type == "IntroLookAtPoint":
                op.object_name = "IntroLook"


classes = (VIEW3D_PT_level_object,)


def register():
    register_object_props()
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    unregister_object_props()