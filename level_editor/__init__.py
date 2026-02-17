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
from .spawn import MYADDON_OT_spawn_point, MYADDON_OT_create_spawn_point

# Collider (新方式)
from .collider_props import register_props, unregister_props   # ← 必須
from .collider_ui import OBJECT_PT_collider, MYADDON_OT_add_collider_props_dialog, MYADDON_OT_remove_collider_props, MYADDON_OT_reset_collider_values  # ← 新パネル、ダイアログ、オペレータ
from . import collider_draw   # ← enable()/disable() を使う

# Blenderに登録するクラスリスト
classes = (
   # オペレータ
    MYADDON_OT_stretch_vertex,
    MYADDON_OT_create_ico_sphere,
    MYADDON_OT_export_scene,
    MYADDON_OT_import_scene,
    MYADDON_OT_add_filename,
    MYADDON_OT_disable_option,
    MYADDON_OT_spawn_point,
    MYADDON_OT_create_spawn_point,
    MYADDON_OT_add_collider_props_dialog, # ← 新ダイアログ
    MYADDON_OT_remove_collider_props,  # ← 新“Remove Collider”オペ
    MYADDON_OT_reset_collider_values,  # ← 新“Reset Collider”オペ

    # パネル
    OBJECT_PT_file_name,
    OBJECT_PT_collider,             # ← 新Colliderパネル
    OBJECT_PT_disable_option,

    # メニュー
    TOPBAR_MT_my_menu,
)

# メニュー項目描画
def draw_menu_manual(self, context):
    #self : 呼び出し元のクラスインスタンス。
    # context : カーソルを合わせた時のポップアップのカスタマイズなどに使用

    # トップバーの「エディターメニュー」に項目（オペレータ）を追加
    self.layout.menu(TOPBAR_MT_my_menu.bl_idname)

# アドオン有効化時コールバック
def register():
    register_props()  # ← 必須
    # Blenderにクラスを登録
    for cls in classes:
        bpy.utils.register_class(cls)

    # メニューに項目を追加
    bpy.types.TOPBAR_MT_editor_menus.append(draw_menu_manual)
    # 3Dビューに描画関数を追加
    collider_draw.enable() # ← 新Collider描画有効化
    print("レベルエディタが有効化されました。")

#アドオン無効化時コールバック
def unregister():
    # メニューから項目を削除
    bpy.types.TOPBAR_MT_editor_menus.remove(draw_menu_manual)
    # 3Dビューに描画関数を追加
    collider_draw.disable() # ← 新Collider描画無効化

    # Blenderからクラスを削除
    for cls in classes:
        bpy.utils.unregister_class(cls)

    unregister_props()  # ← 必須

    print("レベルエディタが無効化されました。")

# テスト実行用コード
if __name__ == "__main__":
    register()