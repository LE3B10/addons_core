# export_scene.py
import bpy
import json
import bpy_extras.io_utils
from .level_exporter import export_level_dict

class MYADDON_OT_export_scene(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    bl_idname = "myaddon.myaddon_ot_export_scene"
    bl_label = "シーン出力"
    filename_ext = ".json"

    def export_json(self):
        data = export_level_dict(bpy.context.scene)
        json_text = json.dumps(data, ensure_ascii=False, indent=4)

        with open(self.filepath, "wt", encoding="utf-8") as f:
            f.write(json_text)

    def execute(self, context):
        self.export_json()
        return {'FINISHED'}