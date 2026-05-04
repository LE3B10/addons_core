import bpy
from bpy.props import (
    StringProperty,
    EnumProperty,
    IntProperty,
    FloatProperty,
)

def make_unique_name(base_name: str) -> str:
    existing_names = {obj.name for obj in bpy.data.objects}
    index = 1
    while True:
        candidate = f"{base_name}_{index:03d}"
        if candidate not in existing_names:
            return candidate
        index += 1


OBJECTIVE_TYPE_ITEMS = [
    ("DeviceObjective",  "DeviceObjective",  "探索用の装置目標"),
    ("DefenseTarget",    "DefenseTarget",    "防衛対象"),
    ("EscapePoint",      "EscapePoint",      "脱出地点"),
    ("BossPhaseTrigger", "BossPhaseTrigger", "ボスフェーズ切替"),
]

BOSS_TRIGGER_TYPE_ITEMS = [
    ("BossHPBelow", "BossHPBelow", "ボスHPが閾値未満になったら発火"),
    ("OnEnterArea", "OnEnterArea", "エリア侵入で発火"),
    ("OnInteract",  "OnInteract",  "インタラクトで発火"),
    ("Manual",      "Manual",      "ゲーム側から手動発火"),
]


class MYADDON_OT_create_objective_point(bpy.types.Operator):
    bl_idname = "myaddon.create_objective_point"
    bl_label = "目的オブジェクトを配置"
    bl_description = "Device / Defense / Escape / BossTrigger を配置します"
    bl_options = {'REGISTER', 'UNDO'}

    point_type: EnumProperty(
        name="Type",
        items=OBJECTIVE_TYPE_ITEMS,
        default="DeviceObjective"
    )

    object_name: StringProperty(
        name="Name Prefix",
        description="名前のプレフィックス",
        default="Objective"
    )

    objective_id: StringProperty(
        name="Objective ID",
        default=""
    )

    ui_name: StringProperty(
        name="UI Name",
        default=""
    )

    activate_time: FloatProperty(
        name="Activate Time",
        default=3.0,
        min=0.0
    )

    max_hp: IntProperty(
        name="Max HP",
        default=1000,
        min=0
    )

    start_hp: IntProperty(
        name="Start HP",
        default=1000,
        min=0
    )

    defense_time: FloatProperty(
        name="Defense Time",
        default=120.0,
        min=0.0
    )

    phase: IntProperty(
        name="Phase",
        default=2,
        min=1
    )

    trigger_type: EnumProperty(
        name="Trigger Type",
        items=BOSS_TRIGGER_TYPE_ITEMS,
        default="BossHPBelow"
    )

    threshold: FloatProperty(
        name="Threshold",
        default=0.65,
        min=0.0,
        max=1.0
    )

    event_id: StringProperty(
        name="Event ID",
        default=""
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout

        layout.prop(self, "point_type")
        layout.prop(self, "object_name")

        if self.point_type == "DeviceObjective":
            col = layout.column(align=True)
            col.prop(self, "objective_id")
            col.prop(self, "ui_name")
            col.prop(self, "activate_time")

        elif self.point_type == "DefenseTarget":
            col = layout.column(align=True)
            col.prop(self, "objective_id")
            col.prop(self, "ui_name")
            col.prop(self, "max_hp")
            col.prop(self, "start_hp")
            col.prop(self, "defense_time")

        elif self.point_type == "EscapePoint":
            col = layout.column(align=True)
            col.prop(self, "objective_id")
            col.prop(self, "ui_name")
            col.prop(self, "activate_time")

        elif self.point_type == "BossPhaseTrigger":
            col = layout.column(align=True)
            col.prop(self, "phase")
            col.prop(self, "trigger_type")
            col.prop(self, "threshold")
            col.prop(self, "event_id")

    def execute(self, context):
        bpy.ops.object.empty_add(
            type='ARROWS',
            location=context.scene.cursor.location
        )
        obj = context.active_object

        if obj is None:
            self.report({'ERROR'}, "オブジェクトの作成に失敗しました。")
            return {'CANCELLED'}

        obj.name = make_unique_name(self.object_name)
        obj.rotation_mode = 'XYZ'
        obj.show_name = True
        obj["type"] = self.point_type

        if self.point_type == "DeviceObjective":
            obj.empty_display_size = 1.2
            obj["objective_id"] = str(self.objective_id)
            obj["ui_name"] = str(self.ui_name)
            obj["activate_time"] = float(self.activate_time)

        elif self.point_type == "DefenseTarget":
            obj.empty_display_size = 1.5
            obj["objective_id"] = str(self.objective_id)
            obj["ui_name"] = str(self.ui_name)
            obj["max_hp"] = int(self.max_hp)
            obj["start_hp"] = int(self.start_hp)
            obj["defense_time"] = float(self.defense_time)

        elif self.point_type == "EscapePoint":
            obj.empty_display_size = 1.5
            obj["objective_id"] = str(self.objective_id)
            obj["ui_name"] = str(self.ui_name)
            obj["activate_time"] = float(self.activate_time)

        elif self.point_type == "BossPhaseTrigger":
            obj.empty_display_size = 1.3
            obj["phase"] = int(self.phase)
            obj["trigger_type"] = str(self.trigger_type)
            obj["threshold"] = float(self.threshold)
            obj["event_id"] = str(self.event_id)

        return {'FINISHED'}


classes = (
    MYADDON_OT_create_objective_point,
)


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)