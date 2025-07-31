import bpy

# オペレーター 無効オプションを追加する
class MYADDON_OT_disable_option(bpy.types.Operator):
    bl_idname = "myaddon.myaddon_ot_disable_option"
    bl_label = "無効オプション"
    bl_description = "オペレータの無効オプションを追加します"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.object
        obj["disable"] = True

        # 無効オプションを追加する処理
        return {"FINISHED"}

# パネル 無効オプション
class OBJECT_PT_disable_option(bpy.types.Panel):
    bl_idname = "OBJECT_PT_disable_option"
    bl_label = "無効オプション"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    # サブメニューの描画
    def draw(self, context):
        # パネルに項目を追加
        if "disable" in context.object:
            # 既にプロパティがあれば、プロパティを表示
            self.layout.prop(context.object, '["disable"]', text = "無効オプション")
        else:
            # プロパティがなければ、プロパティ追加ボタンを表示
            self.layout.operator(MYADDON_OT_disable_option.bl_idname, text = "無効オプションを追加")
