# AI Blender Bridge Plugin for ComfyUI-BlenderAI-node

bl_info = {
    "name": "AI Blender Bridge",
    "author": "AI Assistant",
    "version": (0, 2, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > AI Bridge",
    "description": "Short drama creation and character generation tools",
    "category": "AI",
}

import bpy

# 导入模块
from . import short_drama
from . import character_gen
from . import video_gen
from . import storyboard
from .ui import panel
from . import settings


def register():
    """注册插件"""
    print("🦞 AI Blender Bridge 插件正在加载...")
    
    # 注册设置
    settings.register()
    
    # 注册 UI 面板
    panel.register()
    
    # 注册业务模块
    short_drama.register()
    character_gen.register()
    video_gen.register()
    storyboard.register()
    
    print("✅ AI Blender Bridge 插件加载完成")


def unregister():
    """注销插件"""
    print("🦞 AI Blender Bridge 插件正在卸载...")
    
    # 注销业务模块
    storyboard.unregister()
    video_gen.unregister()
    character_gen.unregister()
    short_drama.unregister()
    
    # 注销 UI 面板
    panel.unregister()
    
    # 注销设置
    settings.unregister()
    
    print("✅ AI Blender Bridge 插件卸载完成")


if __name__ == "__main__":
    register()
