import bpy


class AIBRIDGE_PT_Panel(bpy.types.Panel):
    """AI Blender Bridge 主面板"""
    
    bl_label = "AI Blender Bridge 🦞"
    bl_idname = "AIBRIDGE_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "AI Bridge"
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.aibridge_settings
        
        # 服务器状态
        box = layout.box()
        row = box.row()
        row.label(text="🖥️ ComfyUI 服务器", icon='SERVER')
        row.label(text=settings.comfyui_server)
        
        # 短剧编导模块
        box = layout.box()
        box.label(text="🎬 短剧编导", icon='SCRIPT')
        col = box.column(align=True)
        col.operator("aibridge.generate_script", text="📝 生成剧本", icon='SCRIPT')
        col.operator("aibridge.design_storyboard", text="🎞️ 设计分镜", icon='RENDERLAYERS')
        
        # 角色生成模块
        box = layout.box()
        box.label(text="👤 角色生成", icon='USER')
        col = box.column(align=True)
        col.operator("aibridge.generate_character", text="🎨 生成角色", icon='IMAGE')
        col.operator("aibridge.generate_character_card", text="📋 三视图角色卡", icon='IMAGE')
        
        # 视频生成模块
        box = layout.box()
        box.label(text="🎥 视频生成", icon='RENDERLAYERS')
        col = box.column(align=True)
        col.operator("aibridge.generate_wan_video", text="🎬 Wan 2.2 图生视频", icon='RENDERLAYERS')
        
        # 快捷设置
        box = layout.box()
        box.label(text="⚙️ 快捷设置", icon='SETTINGS')
        col = box.column(align=True)
        col.prop(settings, "comfyui_server", text="服务器")
        col.prop(settings, "llm_provider", text="LLM")


class AIBRIDGE_PT_ShortDrama(bpy.types.Panel):
    """短剧编导子面板"""
    
    bl_label = "🎬 短剧编导"
    bl_idname = "AIBRIDGE_PT_ShortDrama"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "AI Bridge"
    bl_parent_id = "AIBRIDGE_PT_Panel"
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.aibridge_settings
        
        box = layout.box()
        box.label(text="剧本生成参数", icon='SCRIPT')
        box.prop(settings, "llm_provider", text="LLM 提供商")
        
        if settings.llm_provider == "aliyun":
            box.prop(settings, "api_key_aliyun", text="API Key")
        elif settings.llm_provider == "kimi":
            box.prop(settings, "api_key_kimi", text="API Key")
        elif settings.llm_provider == "glm":
            box.prop(settings, "api_key_glm", text="API Key")


class AIBRIDGE_PT_VideoGen(bpy.types.Panel):
    """视频生成子面板"""
    
    bl_label = "🎥 视频生成"
    bl_idname = "AIBRIDGE_PT_VideoGen"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "AI Bridge"
    bl_parent_id = "AIBRIDGE_PT_Panel"
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.aibridge_settings
        
        box = layout.box()
        box.label(text="Wan 2.2 参数", icon='RENDERLAYERS')
        box.prop(settings, "wan22_model", text="模型")
        box.prop(settings, "comfyui_server", text="ComfyUI 服务器")


def register():
    """注册 UI 面板"""
    bpy.utils.register_class(AIBRIDGE_PT_Panel)
    bpy.utils.register_class(AIBRIDGE_PT_ShortDrama)
    bpy.utils.register_class(AIBRIDGE_PT_VideoGen)


def unregister():
    """注销 UI 面板"""
    bpy.utils.unregister_class(AIBRIDGE_PT_VideoGen)
    bpy.utils.unregister_class(AIBRIDGE_PT_ShortDrama)
    bpy.utils.unregister_class(AIBRIDGE_PT_Panel)
