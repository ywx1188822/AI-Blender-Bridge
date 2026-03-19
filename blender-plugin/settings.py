import bpy


class AIBRIDGE_Settings(bpy.types.PropertyGroup):
    """AI Blender Bridge 设置"""
    
    comfyui_server: bpy.props.StringProperty(
        name="ComfyUI 服务器",
        description="ComfyUI 服务器地址 (如：192.168.3.86:8188)",
        default="192.168.3.86:8188"
    )
    
    llm_provider: bpy.props.EnumProperty(
        name="LLM 提供商",
        description="选择 LLM API 提供商",
        items=[
            ("aliyun", "阿里云通义千问", "Aliyun Qwen"),
            ("kimi", "Kimi", "Moonshot Kimi"),
            ("glm", "智谱 GLM", "Zhipu GLM"),
            ("ollama", "Ollama 本地", "Local Ollama")
        ],
        default="aliyun"
    )
    
    api_key_aliyun: bpy.props.StringProperty(
        name="阿里云 API Key",
        description="阿里云 DashScope API Key",
        default="",
        subtype='PASSWORD'
    )
    
    api_key_kimi: bpy.props.StringProperty(
        name="Kimi API Key",
        description="Moonshot Kimi API Key",
        default="",
        subtype='PASSWORD'
    )
    
    api_key_glm: bpy.props.StringProperty(
        name="智谱 API Key",
        description="Zhipu GLM API Key",
        default="",
        subtype='PASSWORD'
    )
    
    wan22_model: bpy.props.EnumProperty(
        name="Wan 2.2 模型",
        description="选择 Wan 2.2 视频生成模型",
        items=[
            ("wan2.1-i2v-720p-14B", "Wan 2.1 I2V 720P 14B", "高画质"),
            ("wan2.1-i2v-480p-14B", "Wan 2.1 I2V 480P 14B", "标准画质"),
            ("smoothMix", "Smooth Mix", "动作流畅")
        ],
        default="smoothMix"
    )
    
    output_dir: bpy.props.StringProperty(
        name="输出目录",
        description="生成文件输出目录",
        default="//output",
        subtype='DIR_PATH'
    )


def register():
    """注册设置"""
    bpy.utils.register_class(AIBRIDGE_Settings)
    bpy.types.Scene.aibridge_settings = bpy.props.PointerProperty(type=AIBRIDGE_Settings)


def unregister():
    """注销设置"""
    del bpy.types.Scene.aibridge_settings
    bpy.utils.unregister_class(AIBRIDGE_Settings)
