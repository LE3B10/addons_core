# ブレンダーに登録するアドオン
bl_info = {
    "name": "レベルエディタ",
    "author": "Taro Kamata",
    "version": (1, 0),
    "blender": (3, 3, 1),
    "location": "",
    "description": "レベルエディタ",
    "warning": "",
    #"support": "TESTING",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}

import bpy

from .stretch_vertex import MYADDON_OT_stretch_vertex
from .create_ico_sphere import MYADDON_OT_create_ico_sphere
from .export_scene import MYADDON_OT_export_scene
from .import_scene import MYADDON_OT_import_scene
from .file_name import OBJECT_PT_file_name, MYADDON_OT_add_filename
from .disable_option import OBJECT_PT_disable_option, MYADDON_OT_disable_option
from .my_menu import TOPBAR_MT_my_menu, draw_menu_manual

# 各モジュールに register/unregister を任せる
from . import spawn
from . import intro_camera
from . import objective_points
from . import level_object_ui

# Collider (新方式)
from .collider_props import register_props, unregister_props
from .collider_ui import (
    OBJECT_PT_collider,
    MYADDON_OT_add_collider_props_dialog,
    MYADDON_OT_remove_collider_props,
    MYADDON_OT_reset_collider_values,
)
from . import collider_draw

# Blenderに登録するクラスリスト
classes = (
    # オペレータ
    MYADDON_OT_stretch_vertex,
    MYADDON_OT_create_ico_sphere,
    MYADDON_OT_export_scene,
    MYADDON_OT_import_scene,
    MYADDON_OT_add_filename,
    MYADDON_OT_disable_option,
    MYADDON_OT_add_collider_props_dialog,
    MYADDON_OT_remove_collider_props,
    MYADDON_OT_reset_collider_values,

    # パネル
    OBJECT_PT_file_name,
    OBJECT_PT_collider,
    OBJECT_PT_disable_option,

    # メニュー
    TOPBAR_MT_my_menu,
)

def draw_menu_manual(self, context):
    self.layout.menu(TOPBAR_MT_my_menu.bl_idname)

# アドオン有効化時コールバック
def register():
    register_props()

    # Blenderにクラスを登録
    for cls in classes:
        bpy.utils.register_class(cls)

    # メニューに項目を追加
    bpy.types.TOPBAR_MT_editor_menus.append(draw_menu_manual)

    # 3Dビューに描画関数を追加
    collider_draw.enable()

    # 各モジュール登録
    spawn.register()
    intro_camera.register()
    objective_points.register()
    level_object_ui.register()

    print("レベルエディタが有効化されました。")

# アドオン無効化時コールバック
def unregister():
    # 逆順で解除
    level_object_ui.unregister()
    objective_points.unregister()
    intro_camera.unregister()
    spawn.unregister()

    # メニューから項目を削除
    bpy.types.TOPBAR_MT_editor_menus.remove(draw_menu_manual)

    # 3Dビュー描画を無効化
    collider_draw.disable()

    # Blenderからクラスを削除
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    unregister_props()

    print("レベルエディタが無効化されました。")

# テスト実行用コード
if __name__ == "__main__":
    register()