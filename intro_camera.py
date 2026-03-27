import bpy
from bpy.props import (
    StringProperty,
    EnumProperty,
    IntProperty,
    FloatProperty
)

def make_unique_name(base_name: str) -> str:
    existing_names = {obj.name for obj in bpy.data.objects}
    index = 1
    while True:
        candidate = f"{base_name}_{index:03d}"
        if candidate not in existing_names:
            return candidate
        index += 1


INTRO_CAMERA_TYPE_ITEMS = [
    ("IntroCameraPoint", "IntroCameraPoint", "開始演出のカメラ位置ポイント"),
    ("IntroLookAtPoint", "IntroLookAtPoint", "開始演出の注視点"),
]

INTERP_MODE_ITEMS = [
    ("Linear", "Linear", "線形補間"),
    ("CatmullRom", "CatmullRom", "Catmull-Rom 曲線補間"),
]

AIM_MODE_ITEMS = [
    ("Target", "Target", "target_name の注視点を見る"),
    ("Euler", "Euler", "Empty の回転をそのままカメラ向きに使う"),
]


class MYADDON_OT_create_intro_camera_point(bpy.types.Operator):
    bl_idname = "myaddon.create_intro_camera_point"
    bl_label = "開始演出ポイントを配置"
    bl_description = "開始演出用のカメラポイント / 注視ポイントを配置します"
    bl_options = {'REGISTER', 'UNDO'}

    point_type: EnumProperty(
        name="Type",
        items=INTRO_CAMERA_TYPE_ITEMS,
        default="IntroCameraPoint"
    )

    object_name: StringProperty(
        name="Name Prefix",
        description="名前のプレフィックス",
        default="IntroCam"
    )

    order: IntProperty(
        name="Order",
        description="再生順",
        default=0,
        min=0
    )

    duration: FloatProperty(
        name="Duration",
        description="このポイントから次のポイントまでの移動時間(秒)",
        default=1.5,
        min=0.0
    )

    fov: FloatProperty(
        name="FOV",
        description="この地点で使う視野角",
        default=45.0,
        min=1.0,
        max=179.0
    )

    target_name: StringProperty(
        name="Target Name",
        description="注視先のオブジェクト名。例: IntroLook_001",
        default=""
    )

    interp_mode: EnumProperty(
        name="Interpolation",
        items=INTERP_MODE_ITEMS,
        default="Linear"
    )

    aim_mode: EnumProperty(
        name="Aim Mode",
        items=AIM_MODE_ITEMS,
        default="Target"
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "point_type")
        layout.prop(self, "object_name")

        if self.point_type == "IntroCameraPoint":
            col = layout.column(align=True)
            col.prop(self, "order")
            col.prop(self, "duration")
            col.prop(self, "fov")
            col.prop(self, "interp_mode")
            col.prop(self, "aim_mode")

            if self.aim_mode == "Target":
                col.prop(self, "target_name")
            else:
                box = layout.box()
                box.label(text="Euler の場合は配置後に Empty を回転してください。")
                box.label(text="その回転を C++ 側で注視方向として使います。")

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

        if self.point_type == "IntroCameraPoint":
            obj.empty_display_size = 1.5
        else:
            obj.empty_display_size = 1.0

        for k in (
            "order", "duration", "fov", "target_name",
            "interp_mode", "aim_mode"
        ):
            if k in obj:
                del obj[k]

        if self.point_type == "IntroCameraPoint":
            obj["order"] = int(self.order)
            obj["duration"] = float(self.duration)
            obj["fov"] = float(self.fov)
            obj["interp_mode"] = str(self.interp_mode)
            obj["aim_mode"] = str(self.aim_mode)

            if self.aim_mode == "Target":
                target_name = str(self.target_name).strip()
                if target_name:
                    obj["target_name"] = target_name

        return {'FINISHED'}


classes = (
    MYADDON_OT_create_intro_camera_point,
)


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)