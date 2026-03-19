# 🧪 AI Blender Bridge Blender 测试指南

**测试版本**: v0.2.0  
**测试日期**: 2026-03-17  
**ComfyUI 服务器**: 192.168.3.86:8188

---

## 📋 测试前准备

### 1. 确认环境

**Blender 版本**: 3.0+ (推荐 4.2.0 LTS)
- 路径：`/Applications/Blender.app`
- 检查：Blender → 关于 Blender

**ComfyUI 服务**: 确认运行中
```bash
# 检查 ComfyUI 是否运行
curl -s http://192.168.3.86:8188/queue | head -5
```

**Python 依赖**: geomdl (可选，用于本地 NURBS 计算)
```bash
pip3 install geomdl
```

---

## 🔌 安装插件

### 方法 1: 从 ZIP 安装 (推荐)

**步骤**:

1. **打开 Blender**
   - 双击 `/Applications/Blender.app`
   - 或终端运行：`/Applications/Blender.app/Contents/MacOS/Blender`

2. **打开偏好设置**
   - 菜单栏：`Edit` → `Preferences` (或按 `Ctrl + Alt + U`)
   - 选择左侧 `Add-ons` 标签

3. **安装插件**
   - 点击顶部 `Install...` 按钮
   - 导航到：`/tmp/ComfyUI-BlenderAI-node/ComfyUI-BlenderAI-node-main/`
   - 选择 `__init__.py` 文件
   - 点击 `Install Add-on`

4. **启用插件**
   - 在插件列表中找到 `3D View: ComfyUI BlenderAI-node`
   - 勾选复选框启用
   - 展开插件详情，确认版本信息

5. **保存设置**
   - 点击左下角 `Save Preferences`
   - 关闭偏好设置窗口

---

## 🧪 功能测试

### 测试 1: 插件加载验证 ✅

**步骤**:
1. 打开 3D Viewport
2. 按 `N` 键打开右侧边栏
3. 查找 `AI Bridge` 标签

**预期结果**:
- ✅ 看到 `AI Bridge` 标签
- ✅ 点击展开面板
- ✅ 显示短剧编导、角色生成、视频生成等模块

**失败处理**:
- ❌ 无 `AI Bridge` 标签 → 检查插件是否启用
- ❌ 面板显示错误 → 查看 Blender 控制台 (Window → Toggle System Console)

---

### 测试 2: 设置配置 ✅

**步骤**:
1. 在 `AI Bridge` 面板中，找到 `Settings` 子面板
2. 配置以下参数：
   - **ComfyUI Server**: `192.168.3.86:8188`
   - **LLM Provider**: 选择 `阿里云通义千问`
   - **API Key**: 输入你的 API Key

3. 点击 `Save Settings`

**预期结果**:
- ✅ 设置保存成功
- ✅ 重启 Blender 后设置保留

---

### 测试 3: 短剧编导功能 ✅

**步骤**:
1. 在 `AI Bridge` 面板，展开 `Short Drama` 子面板
2. 点击 `📝 生成剧本` 按钮
3. 在弹出窗口中：
   - **主题**: 输入 "AI 觉醒之日"
   - **时长**: 180 秒
   - **风格**: 科幻
4. 点击 `OK`

**预期结果**:
- ✅ 控制台显示 "正在生成剧本..."
- ✅ 1-2 分钟后显示 "剧本生成完成"
- ✅ 在 `//scripts/` 目录下生成 JSON 文件

**验证**:
```bash
# 检查剧本文件
ls -la /Users/junyu/.openclaw/workspace/scripts/*.json
cat /Users/junyu/.openclaw/workspace/scripts/AI 觉醒之日.json
```

---

### 测试 4: 角色生成功能 ✅

**步骤**:
1. 在 `AI Bridge` 面板，展开 `Character Generation` 子面板
2. 点击 `🎨 生成角色` 按钮
3. 在弹出窗口中：
   - **提示词**: `1girl, silver hair, blue eyes, school uniform, standing pose, white background`
   - **负向提示词**: `ugly, deformed, noisy, blurry, low quality`
   - **步数**: 20
   - **CFG Scale**: 7.0
4. 点击 `OK`

**预期结果**:
- ✅ 控制台显示 "正在提交到 ComfyUI..."
- ✅ 显示进度 "等待生成完成..."
- ✅ 3-5 分钟后显示 "角色生成完成"
- ✅ 在 `//output/characters/` 目录下生成图片
- ✅ 图片自动加载到 Blender 图像编辑器

**验证**:
```bash
# 检查生成的图片
ls -la /Users/junyu/.openclaw/workspace/output/characters/*.png
```

---

### 测试 5: Wan 2.2 视频生成 ✅ (核心功能)

**步骤**:
1. 在 `AI Bridge` 面板，展开 `Video Generation` 子面板
2. 点击 `🎬 Wan 2.2 图生视频` 按钮
3. 在文件选择器中：
   - 选择一张角色图片 (或使用上一步生成的)
   - 路径示例：`/Users/junyu/.openclaw/workspace/output/characters/xxx.png`
4. 在弹出窗口中：
   - **提示词**: `smooth animation, high quality, cinematic lighting`
   - **负向提示词**: `ugly, deformed, noisy, blurry`
   - **步数**: 30
   - **CFG Scale**: 7.0
   - **视频长度**: 48 帧
   - **帧率**: 24 fps
5. 点击 `OK`

**预期结果**:
- ✅ 控制台显示 "视频生成任务已提交"
- ✅ 显示 Prompt ID
- ✅ 轮询状态 "已等待 X 秒..."
- ✅ 5-10 分钟后显示 "视频生成完成"
- ✅ 在 `//output/videos/` 目录下生成 WEBP/PNG 动画
- ✅ 动画自动加载到 Blender

**验证**:
```bash
# 检查生成的视频
ls -la /Users/junyu/.openclaw/workspace/output/videos/*.webp
ls -la /Users/junyu/.openclaw/workspace/output/videos/*.png
```

---

## 🐛 常见问题排查

### 问题 1: 插件安装失败

**症状**: 安装时显示错误

**解决**:
```bash
# 检查 Blender Python 版本
/Applications/Blender.app/Contents/Resources/4.2/python/bin/python3 --version

# 重新下载 ZIP
cd /tmp
rm -rf ComfyUI-BlenderAI-node.zip ComfyUI-BlenderAI-node
curl -L https://github.com/AIGODLIKE/ComfyUI-BlenderAI-node/archive/refs/heads/main.zip -o ComfyUI-BlenderAI-node.zip
unzip ComfyUI-BlenderAI-node.zip
```

---

### 问题 2: ComfyUI 连接失败

**症状**: "Connection refused" 错误

**解决**:
```bash
# 检查 ComfyUI 是否运行
curl http://192.168.3.86:8188/queue

# 如果无响应，启动 ComfyUI
# (需要根据实际部署情况启动)
```

---

### 问题 3: LLM API 调用失败

**症状**: "401 Unauthorized" 错误

**解决**:
1. 检查 API Key 是否正确
2. 确认 API Key 有足够额度
3. 检查网络连接

---

### 问题 4: 视频生成超时

**症状**: "生成超时 (600 秒)" 错误

**解决**:
1. 检查 ComfyUI 队列状态
2. 减少视频长度 (改为 24 帧测试)
3. 降低采样步数 (改为 20 步)

---

## 📊 测试报告模板

### 测试执行记录

| 测试项 | 状态 | 用时 | 备注 |
|--------|------|------|------|
| 插件加载 | ⬜ 未开始 | - | - |
| 设置配置 | ⬜ 未开始 | - | - |
| 短剧编导 | ⬜ 未开始 | - | - |
| 角色生成 | ⬜ 未开始 | - | - |
| Wan 2.2 视频 | ⬜ 未开始 | - | - |

### 问题记录

| 问题描述 | 严重程度 | 状态 | 解决方案 |
|----------|----------|------|----------|
| - | - | - | - |

---

## 📞 联系支持

**项目文档**: `/Users/junyu/.openclaw/workspace/01-AI-Blender-Bridge/docs/`

**问题反馈**:
- GitHub Issues: (待创建)
- 项目负责人：余峻

---

_创建时间：2026-03-17 21:55_  
_版本：v0.2.0_
