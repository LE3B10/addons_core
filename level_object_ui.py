import bpy
from bpy.props import EnumProperty, StringProperty, IntProperty, BoolProperty, FloatProperty

LEVEL_TYPE_ITEMS = [
    ("StaticMesh",       "StaticMesh",       "描画するメッシュ"),
    ("PlayerSpawnPoint", "PlayerSpawnPoint", "プレイヤースポーン"),
    ("EnemySpawnPoint",  "EnemySpawnPoint",  "敵スポーン"),
    ("BossSpawnPoint",   "BossSpawnPoint",   "ボススポーン"),

    ("DeviceObjective",  "DeviceObjective",  "探索用の装置目標"),
    ("InteractPoint",    "InteractPoint",    "インタラクト地点"),
    ("DefenseTarget",    "DefenseTarget",    "防衛対象"),
    ("DefenseArea",      "DefenseArea",      "防衛エリア"),
    ("EscapePoint",      "EscapePoint",      "脱出地点"),
    ("Checkpoint",       "Checkpoint",       "通過チェック地点"),

    ("BossPhaseTrigger", "BossPhaseTrigger", "ボスフェーズ切替"),
    ("BossEventPoint",   "BossEventPoint",   "ボス戦イベント地点"),

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

INTERP_MODE_ITEMS = [
    ("Linear", "Linear", "線形補間"),
    ("CatmullRom", "CatmullRom", "Catmull-Rom 曲線補間"),
]

AIM_MODE_ITEMS = [
    ("Target", "Target", "target_name の注視点を見る"),
    ("Euler", "Euler", "Empty の回転をそのままカメラ向きに使う"),
]

BOSS_TRIGGER_TYPE_ITEMS = [
    ("BossHPBelow", "BossHPBelow", "ボスHPが閾値未満になったら発火"),
    ("OnEnterArea", "OnEnterArea", "エリア侵入で発火"),
    ("OnInteract",  "OnInteract",  "インタラクトで発火"),
    ("Manual",      "Manual",      "ゲーム側から手動発火"),
]

SPAWN_POINT_TYPES = {"PlayerSpawnPoint", "EnemySpawnPoint", "BossSpawnPoint"}
WAVE_EDIT_TYPES = {"EnemySpawnPoint", "BossSpawnPoint"}
INTRO_CAMERA_TYPES = {"IntroCameraPoint", "IntroLookAtPoint"}
OBJECTIVE_POINT_TYPES = {"DeviceObjective", "DefenseTarget", "EscapePoint", "BossPhaseTrigger"}


def _get_cp(obj, key, default):
    return obj.get(key, default)


def _set_cp(obj, key, value):
    obj[key] = value


def register_object_props():
    # --------------------------------------------------
    # 基本
    # --------------------------------------------------
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

    # --------------------------------------------------
    # Spawn
    # --------------------------------------------------
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

    # --------------------------------------------------
    # Intro Camera
    # --------------------------------------------------
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

    def get_interp_mode(self):
        return str(_get_cp(self, "interp_mode", "Linear"))

    def set_interp_mode(self, v):
        _set_cp(self, "interp_mode", str(v))

    def get_aim_mode(self):
        return str(_get_cp(self, "aim_mode", "Target"))

    def set_aim_mode(self, v):
        _set_cp(self, "aim_mode", str(v))

    # --------------------------------------------------
    # Objective 共通
    # --------------------------------------------------
    def get_objective_id(self):
        return str(_get_cp(self, "objective_id", ""))

    def set_objective_id(self, v):
        _set_cp(self, "objective_id", str(v))

    def get_ui_name(self):
        return str(_get_cp(self, "ui_name", ""))

    def set_ui_name(self, v):
        _set_cp(self, "ui_name", str(v))

    def get_activate_time(self):
        return float(_get_cp(self, "activate_time", 0.0))

    def set_activate_time(self, v):
        _set_cp(self, "activate_time", float(v))

    # --------------------------------------------------
    # Defense
    # --------------------------------------------------
    def get_max_hp(self):
        return int(_get_cp(self, "max_hp", 100))

    def set_max_hp(self, v):
        _set_cp(self, "max_hp", int(v))

    def get_start_hp(self):
        return int(_get_cp(self, "start_hp", 100))

    def set_start_hp(self, v):
        _set_cp(self, "start_hp", int(v))

    def get_defense_time(self):
        return float(_get_cp(self, "defense_time", 60.0))

    def set_defense_time(self, v):
        _set_cp(self, "defense_time", float(v))

    # --------------------------------------------------
    # Boss Phase Trigger
    # --------------------------------------------------
    def get_phase(self):
        return int(_get_cp(self, "phase", 1))

    def set_phase(self, v):
        _set_cp(self, "phase", int(v))

    def get_trigger_type(self):
        return str(_get_cp(self, "trigger_type", "BossHPBelow"))

    def set_trigger_type(self, v):
        _set_cp(self, "trigger_type", str(v))

    def get_threshold(self):
        return float(_get_cp(self, "threshold", 1.0))

    def set_threshold(self, v):
        _set_cp(self, "threshold", float(v))

    def get_event_id(self):
        return str(_get_cp(self, "event_id", ""))

    def set_event_id(self, v):
        _set_cp(self, "event_id", str(v))

    # --------------------------------------------------
    # Property 登録
    # --------------------------------------------------
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
    bpy.types.Object.level_interp_mode = EnumProperty(
        name="Interpolation",
        items=INTERP_MODE_ITEMS,
        get=get_interp_mode,
        set=set_interp_mode
    )
    bpy.types.Object.level_aim_mode = EnumProperty(
        name="Aim Mode",
        items=AIM_MODE_ITEMS,
        get=get_aim_mode,
        set=set_aim_mode
    )

    bpy.types.Object.level_objective_id = StringProperty(
        name="Objective ID",
        description="ゲーム側で目的を識別するID",
        get=get_objective_id,
        set=set_objective_id
    )
    bpy.types.Object.level_ui_name = StringProperty(
        name="UI Name",
        description="UI表示名",
        get=get_ui_name,
        set=set_ui_name
    )
    bpy.types.Object.level_activate_time = FloatProperty(
        name="Activate Time",
        description="起動・操作に必要な時間(秒)",
        min=0.0,
        get=get_activate_time,
        set=set_activate_time
    )

    bpy.types.Object.level_max_hp = IntProperty(
        name="Max HP",
        min=0,
        get=get_max_hp,
        set=set_max_hp
    )
    bpy.types.Object.level_start_hp = IntProperty(
        name="Start HP",
        min=0,
        get=get_start_hp,
        set=set_start_hp
    )
    bpy.types.Object.level_defense_time = FloatProperty(
        name="Defense Time",
        min=0.0,
        get=get_defense_time,
        set=set_defense_time
    )

    bpy.types.Object.level_phase = IntProperty(
        name="Phase",
        min=1,
        get=get_phase,
        set=set_phase
    )
    bpy.types.Object.level_trigger_type = EnumProperty(
        name="Trigger Type",
        items=BOSS_TRIGGER_TYPE_ITEMS,
        get=get_trigger_type,
        set=set_trigger_type
    )
    bpy.types.Object.level_threshold = FloatProperty(
        name="Threshold",
        description="HP割合などの閾値",
        min=0.0,
        max=1.0,
        get=get_threshold,
        set=set_threshold
    )
    bpy.types.Object.level_event_id = StringProperty(
        name="Event ID",
        description="発火させるイベントID",
        get=get_event_id,
        set=set_event_id
    )


def unregister_object_props():
    for n in (
        "level_type",
        "level_file_name",
        "level_disable",
        "level_wave",
        "level_group",
        "level_count",
        "level_archetype",
        "level_order",
        "level_duration",
        "level_fov",
        "level_target_name",
        "level_interp_mode",
        "level_aim_mode",
        "level_objective_id",
        "level_ui_name",
        "level_activate_time",
        "level_max_hp",
        "level_start_hp",
        "level_defense_time",
        "level_phase",
        "level_trigger_type",
        "level_threshold",
        "level_event_id",
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
            col.prop(obj, "level_interp_mode")
            col.prop(obj, "level_aim_mode")

            if obj.level_aim_mode == "Target":
                col.prop(obj, "level_target_name")

        if obj.level_type == "DeviceObjective":
            col = layout.column(align=True)
            col.label(text="Device Objective")
            col.prop(obj, "level_objective_id")
            col.prop(obj, "level_ui_name")
            col.prop(obj, "level_activate_time")

        if obj.level_type == "DefenseTarget":
            col = layout.column(align=True)
            col.label(text="Defense Target")
            col.prop(obj, "level_objective_id")
            col.prop(obj, "level_ui_name")
            col.prop(obj, "level_max_hp")
            col.prop(obj, "level_start_hp")
            col.prop(obj, "level_defense_time")

        if obj.level_type == "EscapePoint":
            col = layout.column(align=True)
            col.label(text="Escape")
            col.prop(obj, "level_objective_id")
            col.prop(obj, "level_ui_name")
            col.prop(obj, "level_activate_time")

        if obj.level_type == "BossPhaseTrigger":
            col = layout.column(align=True)
            col.label(text="Boss Phase Trigger")
            col.prop(obj, "level_phase")
            col.prop(obj, "level_trigger_type")
            col.prop(obj, "level_threshold")
            col.prop(obj, "level_event_id")

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
                op.interp_mode = getattr(obj, "level_interp_mode", "Linear")
                op.aim_mode = getattr(obj, "level_aim_mode", "Target")
            elif obj.level_type == "IntroLookAtPoint":
                op.object_name = "IntroLook"

        elif obj.level_type in OBJECTIVE_POINT_TYPES:
            op = layout.operator("myaddon.create_objective_point", text="Objectiveを配置")
            op.point_type = obj.level_type

            if obj.level_type == "DeviceObjective":
                op.object_name = "Device"
                op.objective_id = getattr(obj, "level_objective_id", "")
                op.ui_name = getattr(obj, "level_ui_name", "")
                op.activate_time = getattr(obj, "level_activate_time", 3.0)

            elif obj.level_type == "DefenseTarget":
                op.object_name = "Defense"
                op.objective_id = getattr(obj, "level_objective_id", "")
                op.ui_name = getattr(obj, "level_ui_name", "")
                op.max_hp = getattr(obj, "level_max_hp", 1000)
                op.start_hp = getattr(obj, "level_start_hp", 1000)
                op.defense_time = getattr(obj, "level_defense_time", 120.0)

            elif obj.level_type == "EscapePoint":
                op.object_name = "Escape"
                op.objective_id = getattr(obj, "level_objective_id", "")
                op.ui_name = getattr(obj, "level_ui_name", "")
                op.activate_time = getattr(obj, "level_activate_time", 5.0)

            elif obj.level_type == "BossPhaseTrigger":
                op.object_name = "BossPhase"
                op.phase = getattr(obj, "level_phase", 2)
                op.trigger_type = getattr(obj, "level_trigger_type", "BossHPBelow")
                op.threshold = getattr(obj, "level_threshold", 0.65)
                op.event_id = getattr(obj, "level_event_id", "")


classes = (VIEW3D_PT_level_object,)


def register():
    register_object_props()
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    unregister_object_props()