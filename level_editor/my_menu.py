import bpy


class TOPBAR_MT_my_menu(bpy.types.Menu):
    bl_idname = "TOPBAR_MT_my_menu"
    bl_label = "MyMenu"
    bl_description = "レベルエディタの拡張メニュー"

    def draw(self, context):
        layout = self.layout

        layout.operator("myaddon.myaddon_ot_stretch_vertex", text="頂点を伸ばす")
        layout.operator("myaddon.myaddon_ot_create_ico_sphere", text="ICO球生成")
        layout.operator("myaddon.myaddon_ot_export_scene", text="シーン出力")
        layout.operator("myaddon.myaddon_ot_import_scene", text="シーン入力")

        layout.separator()
        layout.label(text="Spawn Points")

        # プレイヤー
        op = layout.operator("myaddon.create_spawn_point", text="プレイヤーの出現ポイントを配置")
        op.spawn_type = "PlayerSpawnPoint"
        op.object_name = "PlayerSpawn"

        # エネミー
        op = layout.operator("myaddon.create_spawn_point", text="エネミーの出現ポイントを配置")
        op.spawn_type = "EnemySpawnPoint"
        op.object_name = "EnemySpawn"
        op.wave = 1
        op.group = 0
        op.count = 1

        # ボス
        op = layout.operator("myaddon.create_spawn_point", text="ボスの出現ポイントを配置")
        op.spawn_type = "BossSpawnPoint"
        op.object_name = "BossSpawn"
        op.wave = 0
        op.group = 0
        op.count = 1

        layout.separator()
        layout.label(text="Intro Camera")

        # 開始演出カメラポイント
        op = layout.operator("myaddon.create_intro_camera_point", text="開始演出カメラポイントを配置")
        op.point_type = "IntroCameraPoint"
        op.object_name = "IntroCam"
        op.order = 0
        op.duration = 1.5
        op.fov = 45.0
        op.target_name = ""

        # 開始演出注視ポイント
        op = layout.operator("myaddon.create_intro_camera_point", text="開始演出注視ポイントを配置")
        op.point_type = "IntroLookAtPoint"
        op.object_name = "IntroLook"

        layout.separator()
        layout.operator("wm.url_open_preset", text="Manual", icon='HELP')

    def submenu(self, context):
        self.layout.menu(TOPBAR_MT_my_menu.bl_idname)


def draw_menu_manual(self, context):
    self.layout.menu(TOPBAR_MT_my_menu.bl_idname)