# 🔌 Blender 集成遗留工作项

**创建日期**: 2026-03-16  
**优先级**: P0  
**状态**: ⏳ 待完成 (转交同事)  
**预计工时**: 2-3 小时

---

## 📋 工作目标

将 AI Blender Bridge 插件集成到 ComfyUI-BlenderAI-node 项目中，并在 Blender 中测试功能。

---

## ✅ 已完成工作 (v0.1.0)

### 插件开发

| 文件 | 状态 | 说明 |
|------|------|------|
| `blender-plugin/__init__.py` | ✅ | 插件入口 (35 行) |
| `blender-plugin/settings.py` | ✅ | 设置管理 (65 行) |
| `blender-plugin/short_drama.py` | ✅ | 短剧编导 (320 行) |
| `blender-plugin/character_gen.py` | ✅ | 角色生成 (450 行) |
| `blender-plugin/storyboard.py` | ✅ | 分镜模块 (15 行) |
| `blender-plugin/ui/panel.py` | ✅ | UI 面板 (115 行) |
| `blender-plugin/comfyui_workflows/character_gen.json` | ✅ | 角色工作流 |
| `blender-plugin/README.md` | ✅ | 使用文档 |

### 文档

| 文档 | 状态 | 路径 |
|------|------|------|
| 分析报告 | ✅ | `docs/ComfyUI-BlenderAI-node 分析报告.md` |
| 插件开发计划 | ✅ | `docs/插件开发计划.md` |
| 插件开发报告 | ✅ | `docs/插件开发报告-v0.1.0.md` |
| 集成指南 | ✅ | `docs/集成指南.md` |

---

## ⏳ 待完成工作

### 1. 下载 ComfyUI-BlenderAI-node 项目

**方法 A: Git 克隆 (推荐)**
```bash
cd /tmp
git clone --depth 1 https://github.com/AIGODLIKE/ComfyUI-BlenderAI-node.git
cd ComfyUI-BlenderAI-node
```

**方法 B: ZIP 下载 (备选)**
```bash
cd /tmp
curl -L https://github.com/AIGODLIKE/ComfyUI-BlenderAI-node/archive/refs/heads/main.zip -o ComfyUI-BlenderAI-node.zip
unzip ComfyUI-BlenderAI-node.zip
cd ComfyUI-BlenderAI-node-main
```

**已知问题**: 
- Git 克隆可能因网络问题失败
- 解决方法：使用 ZIP 下载或等待网络恢复

---

### 2. 复制插件文件

```bash
# 将 AI Blender Bridge 插件复制到 SDNode/plugins 目录
cp -r /path/to/ai-blender-bridge/blender-plugin \
      /path/to/ComfyUI-BlenderAI-node/SDNode/plugins/ai_blender_bridge
```

**目标路径**:
```
ComfyUI-BlenderAI-node/
└── SDNode/
    └── plugins/
        └── ai_blender_bridge/
            ├── __init__.py
            ├── settings.py
            ├── short_drama.py
            ├── character_gen.py
            ├── storyboard.py
            ├── ui/
            │   ├── __init__.py
            │   └── panel.py
            └── comfyui_workflows/
                └── character_gen.json
```

---

### 3. 注册插件

**文件**: `SDNode/plugins/__init__.py`

**操作**: 在文件末尾添加插件注册代码

```python
# 在文件末尾添加以下代码

# ============== AI Blender Bridge 插件注册 ==============
try:
    from .ai_blender_bridge import register as aibridge_register
    from .ai_blender_bridge import unregister as aibridge_unregister
    
    def register_all_plugins():
        # ... 现有代码 ...
        
        # 注册 AI Blender Bridge
        print("🦞 注册 AI Blender Bridge 插件...")
        aibridge_register()
    
    def unregister_all_plugins():
        # ... 现有代码 ...
        
        # 注销 AI Blender Bridge
        print("🦞 注销 AI Blender Bridge 插件...")
        aibridge_unregister()
        
except ImportError as e:
    print(f"⚠️ AI Blender Bridge 插件导入失败：{e}")
    
    def register_all_plugins():
        pass
    
    def unregister_all_plugins():
        pass
# =======================================================
```

---

### 4. 测试插件

**步骤**:

1. **打开 Blender** (3.0+)

2. **安装插件**
   - 编辑 → 偏好设置 → 插件
   - 点击 "安装"
   - 导航到 `ComfyUI-BlenderAI-node/SDNode/plugins/ai_blender_bridge`
   - 选择 `__init__.py` 并安装
   - 勾选启用插件

3. **验证安装**
   - 打开 3D Viewport
   - 按 `N` 打开侧边栏
   - 查看是否有 "AI Bridge" 标签
   - 点击展开面板

4. **配置设置**
   - 设置 ComfyUI 服务器：`192.168.3.86:8188`
   - 选择 LLM 提供商 (阿里云/Kimi/智谱)
   - 输入 API Key

5. **测试功能**
   - [ ] 点击 "📝 生成剧本"，输入主题测试
   - [ ] 点击 "🎨 生成角色"，输入提示词测试
   - [ ] 点击 "📋 三视图角色卡"，输入角色名测试

---

## 🧪 测试清单

### 基础功能测试

- [ ] 插件能否正常加载 (查看 Blender 控制台输出)
- [ ] UI 面板是否显示 (AI Bridge 标签)
- [ ] 设置能否保存 (重启 Blender 后检查)
- [ ] ComfyUI 连接是否正常 (点击按钮测试)

### 短剧编导测试

- [ ] 剧本生成功能 (输入主题，检查输出)
- [ ] 分镜设计功能 (选择剧本文件，检查输出)
- [ ] LLM API 调用 (检查 API 响应)
- [ ] JSON 格式输出 (检查文件格式)

### 角色生成测试

- [ ] 角色图像生成 (输入提示词，检查图像)
- [ ] 三视图角色卡 (输入角色名，检查图像)
- [ ] ComfyUI 工作流提交 (检查 ComfyUI 队列)
- [ ] 图片加载到 Blender (检查图像编辑器)

---

## 🐛 常见问题

### 问题 1: 模块导入错误

**症状**: `ModuleNotFoundError: No module named 'xxx'`

**解决**:
```python
# 在 __init__.py 中添加
import sys
from pathlib import Path
plugin_dir = Path(__file__).parent
if str(plugin_dir) not in sys.path:
    sys.path.append(str(plugin_dir))
```

### 问题 2: 面板不显示

**症状**: 侧边栏没有 "AI Bridge" 标签

**解决**:
1. 确认插件已启用 (偏好设置 → 插件)
2. 重启 Blender
3. 检查 `bl_category = "AI Bridge"` 设置

### 问题 3: ComfyUI 连接失败

**症状**: "Connection refused" 错误

**解决**:
1. 检查 ComfyUI 是否运行
2. 确认服务器地址正确 (`192.168.3.86:8188`)
3. 检查防火墙设置

### 问题 4: LLM API 调用失败

**症状**: "401 Unauthorized" 错误

**解决**:
1. 检查 API Key 是否正确
2. 确认 API Key 有足够额度
3. 检查网络连接

---

## 📊 验收标准

### 必须通过

- [ ] 插件能在 Blender 中正常加载
- [ ] UI 面板正常显示
- [ ] ComfyUI 连接成功
- [ ] 至少一个功能测试通过 (剧本生成 或 角色生成)

### 建议通过

- [ ] 所有功能测试通过
- [ ] 错误处理正常
- [ ] 设置持久化正常

---

## 📁 相关文件

### 插件源码

```
/home/ClawHawk/.openclaw/workspace/infinite-canvas/01-AI-Blender-Bridge/blender-plugin/
```

### 参考文档

- `docs/ComfyUI-BlenderAI-node 分析报告.md` - 项目结构分析
- `docs/插件开发计划.md` - 开发计划
- `docs/插件开发报告-v0.1.0.md` - 开发报告
- `docs/集成指南.md` - 详细集成步骤

---

## 👤 负责人

- **开发**: AI Assistant (已完成 v0.1.0)
- **集成**: (待分配同事)
- **测试**: (待分配同事)

---

## 📞 联系方式

如有疑问，请联系：
- **余峻**: 项目负责人
- **AI Assistant**: 插件开发者

---

## 📝 更新记录

### 2026-03-16 16:00

- ✅ 创建遗留工作文档
- ✅ 插件 v0.1.0 开发完成
- ⏳ 等待同事接手集成

---

_创建时间：2026-03-16 16:00_  
_下次更新：集成完成后_
