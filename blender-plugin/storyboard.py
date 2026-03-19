import bpy


class AIBRIDGE_OT_GenerateStoryboard(bpy.types.Operator):
    """生成分镜"""
    
    bl_idname = "aibridge.generate_storyboard"
    bl_label = "生成分镜 🎞️"
    bl_description = "使用 ComfyUI 生成分镜图像"
    bl_options = {'REGISTER', 'UNDO'}
    
    # TODO: 实现分镜生成功能
    
    def execute(self, context):
        self.report({'INFO'}, "分镜生成功能开发中...")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(AIBRIDGE_OT_GenerateStoryboard)


def unregister():
    bpy.utils.unregister_class(AIBRIDGE_OT_GenerateStoryboard)
