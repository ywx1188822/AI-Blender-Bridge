# 🦞 AI Blender Bridge - Blender 插件

**版本**: v0.1.0  
**创建日期**: 2026-03-16  
**目标**: 短剧编导与角色生成工具

---

## 📋 功能特性

### 🎬 短剧编导
- **剧本生成** - 使用 LLM (阿里云/Kimi/智谱) 自动生成短剧剧本
- **分镜设计** - 将剧本转换为分镜头脚本
- **ComfyUI 集成** - 自动生成 ComfyUI 提示词

### 👤 角色生成
- **角色图像生成** - 使用 ComfyUI 生成角色图像
- **三视图角色卡** - 生成正面/侧面/背面三视图
- **批量生成** - 支持多种子批量探索

### 🎥 视频生成
- **Wan 2.2 图生视频** - 集成 Wan 2.2 Smooth Mix 工作流
- **动感解压视频** - 自动生成 6 秒动感视频
- **批量处理** - 支持 4 个视频批量生成

---

## 📁 目录结构

```
blender-plugin/
├── __init__.py              # 插件入口
├── settings.py              # 设置管理
├── short_drama.py           # 短剧编导模块
├── character_gen.py         # 角色生成模块
├── storyboard.py            # 分镜模块
├── ui/
│   ├── __init__.py
│   └── panel.py             # UI 面板
└── comfyui_workflows/
    ├── character_gen.json   # 角色生成工作流
    └── character_card.json  # 三视图工作流
```

---

## 🔧 安装方法

### 方法 1: 直接安装

1. 下载插件文件夹
2. Blender → 编辑 → 偏好设置 → 插件 → 安装
3. 选择 `blender-plugin` 文件夹
4. 勾选启用插件

### 方法 2: 集成到 ComfyUI-BlenderAI-node

1. Fork ComfyUI-BlenderAI-node 项目
2. 将 `blender-plugin` 目录复制到 `SDNode/plugins/ai_blender_bridge/`
3. 在 ComfyUI-BlenderAI-node 的 `plugins/__init__.py` 中注册

---

## 🚀 使用方法

### 1. 配置服务器

在 3D Viewport 侧边栏 → AI Bridge 面板：
- 设置 ComfyUI 服务器地址 (默认：`192.168.3.86:8188`)
- 选择 LLM 提供商 (阿里云/Kimi/智谱)
- 输入对应的 API Key

### 2. 生成剧本

1. 点击 "📝 生成剧本"
2. 输入主题、时长、风格
3. 点击确定，等待生成
4. 剧本自动在文本编辑器中打开

### 3. 生成角色

1. 点击 "🎨 生成角色"
2. 输入角色描述提示词
3. 调整采样参数 (步数、CFG、种子)
4. 点击确定，等待生成
5. 图像自动加载到 Blender

### 4. 生成三视图

1. 点击 "📋 三视图角色卡"
2. 输入角色名称
3. 点击确定，等待生成
4. 三视图自动加载到 Blender

---

## ⚙️ 配置说明

### ComfyUI 服务器

- **地址**: `192.168.3.86:8188` (局域网)
- **要求**: ComfyUI 0.10.0+
- **网络**: 确保 Blender 可以访问 ComfyUI 服务器

### LLM API 配置

#### 阿里云通义千问
- **API Key**: 在 DashScope 控制台获取
- **模型**: qwen-plus
- **文档**: https://help.aliyun.com/zh/dashscope/

#### Kimi
- **API Key**: 在 Moonshot 控制台获取
- **模型**: moonshot-v1-8k
- **文档**: https://platform.moonshot.cn/

#### 智谱 GLM
- **API Key**: 在 BigModel 控制台获取
- **模型**: glm-4
- **文档**: https://open.bigmodel.cn/

---

## 📊 输出目录

```
//output/
├── characters/          # 角色图像
├── character_cards/     # 三视图角色卡
│   └── Character_001/
└── scripts/             # 剧本文件
    └── AI 觉醒之日.json
```

---

## 🔌 开发插件

### 添加新功能

1. 在 `blender-plugin/` 目录创建新模块
2. 定义操作符类 (继承 `bpy.types.Operator`)
3. 在 `__init__.py` 中注册

### 示例：添加视频生成

```python
# video_gen.py
import bpy

class AIBRIDGE_OT_GenerateVideo(bpy.types.Operator):
    bl_idname = "aibridge.generate_video"
    bl_label = "生成视频 🎥"
    
    def execute(self, context):
        # 实现视频生成逻辑
        return {'FINISHED'}

def register():
    bpy.utils.register_class(AIBRIDGE_OT_GenerateVideo)

def unregister():
    bpy.utils.unregister_class(AIBRIDGE_OT_GenerateVideo)
```

在 `__init__.py` 中导入并注册：

```python
from . import video_gen

def register():
    video_gen.register()

def unregister():
    video_gen.unregister()
```

---

## 🐛 故障排查

### 问题 1: 插件无法加载

**症状**: Blender 报错 "ModuleNotFoundError"

**解决**:
1. 确保所有 `.py` 文件都在正确位置
2. 检查 `__init__.py` 中的导入路径
3. 重启 Blender

### 问题 2: 无法连接 ComfyUI

**症状**: "Connection refused" 错误

**解决**:
1. 检查 ComfyUI 服务器是否运行
2. 确认服务器地址正确
3. 检查防火墙设置

### 问题 3: LLM API 调用失败

**症状**: "401 Unauthorized" 错误

**解决**:
1. 检查 API Key 是否正确
2. 确认 API Key 有足够额度
3. 检查网络连接

---

## 📝 更新日志

### v0.1.0 (2026-03-16)
- ✅ 初始版本
- ✅ 短剧编导模块 (剧本生成、分镜设计)
- ✅ 角色生成模块 (角色图像、三视图)
- ✅ UI 面板 (主面板、设置面板)
- ✅ ComfyUI 工作流集成

---

## 📞 联系方式

- **GitHub**: https://github.com/your-repo/ai-blender-bridge
- **问题反馈**: 提交 Issue

---

## 📄 许可证

MIT License

---

_创建时间：2026-03-16 15:10_
