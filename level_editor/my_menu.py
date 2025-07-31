import bpy

# トップバーの拡張メニュー（サブメニュークラス）
class TOPBAR_MT_my_menu(bpy.types.Menu):
    # Blenderがクラスを識別するための固有の文字列
    bl_idname = "TOPBAR_MT_my_menu"
    # メニューのラベルとして表示される文字列
    bl_label = "MyMenu"
    # 著者表示用の文字列
    bl_description = "レベルエディタの拡張メニュー"

    # サブメニューの描画
    def draw(self, context):
        layout = self.layout
        layout.operator("myaddon.myaddon_ot_stretch_vertex", text="頂点を伸ばす")
        layout.operator("myaddon.myaddon_ot_create_ico_sphere", text="ICO球生成")
        layout.operator("myaddon.myaddon_ot_export_scene", text="シーン出力")
        layout.operator("myaddon.myaddon_ot_import_scene", text="シーン入力")
        #layout.operator("myaddon.myaddon_ot_add_filename", text="FileName追加")
        #layout.operator("myaddon.myaddon_ot_add_collider", text="コライダー追加")
        #layout.operator("myaddon.myaddon_ot_disable_option", text="無効オプション追加")
        
        # 区切り線
        layout.separator()
        layout.operator("wm.url_open_preset", text="Manual", icon='HELP')

    # 既存のメニューにサブメニューを追加
    def submenu(self, context):
        # ID指定でサブメニューを追加
        self.layout.menu(TOPBAR_MT_my_menu.bl_idname)

# メニュー項目描画
def draw_menu_manual(self, context):
    #self : 呼び出し元のクラスインスタンス。
    # context : カーソルを合わせた時のポップアップのカスタマイズなどに使用

    # トップバーの「エディターメニュー」に項目（オペレータ）を追加
    self.layout.menu(TOPBAR_MT_my_menu.bl_idname)
