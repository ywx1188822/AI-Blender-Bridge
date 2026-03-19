# 🎬 Agentic 3D Studio - 使用指南

**版本**: v1.0.0-Agentic  
**创建日期**: 2026-03-19  
**项目**: AI Blender Bridge

---

## 📋 目录

1. [快速开始](#快速开始)
2. [安装与配置](#安装与配置)
3. [功能说明](#功能说明)
4. [API 参考](#api-参考)
5. [故障排查](#故障排查)
6. [示例场景](#示例场景)

---

## 🚀 快速开始

### 5 分钟快速测试

#### Step 1: 启动 Blender HTTP 服务

1. 打开 **Blender 4.x**
2. 切换到 **Scripting** 标签页
3. 新建文本文件，粘贴以下代码：

```python
import bpy
import sys
import os

# 修改为你的项目路径
project_path = "/Users/junyu/.openclaw/workspace/01-AI-Blender-Bridge"
sys.path.insert(0, os.path.join(project_path, 'server'))

# 运行 HTTP 服务
exec(open(os.path.join(project_path, 'server', 'http_server.py')).read())
```

4. 点击 **▶ 运行脚本**
5. 看到输出 `🚀 Blender HTTP Server started` 表示成功

#### Step 2: 打开 Web 应用

1. 用浏览器打开：
   ```
   file:///Users/junyu/.openclaw/workspace/01-AI-Blender-Bridge/web-app/index.html
   ```

2. 在 **Setup Connection** 页面：
   - Blender URL: `http://localhost:8123`
   - 点击 **🔌 Test Connection**
   - 看到 `✅ Connected to Blender` 表示成功

#### Step 3: 测试场景管理

1. 切换到 **Scene Manager** 页面
2. 点击 **🔄 Refresh Objects** 加载物体列表
3. 点击任一物体，在 Transform Editor 中修改位置
4. 点击 **✅ Apply Transform** 应用修改
5. 点击 **📸 Live Render** 查看渲染结果

#### Step 4: 测试 AI Director

1. 切换到 **AI Director** 页面
2. 输入你的 API Key (Gemini 或 Qwen-VL)
3. 输入目标，例如：
   ```
   Move the cube to x=3 and rotate it 90 degrees around Y axis
   ```
4. 点击 **🚀 Start Agent Loop**
5. 观察 AI 自动执行变换操作

---

## 📦 安装与配置

### 系统要求

| 组件 | 要求 |
|------|------|
| Blender | 3.0+ (推荐 4.x) |
| Python | 3.8+ (Blender 内置) |
| 浏览器 | Chrome/Edge/Safari (支持现代 JS) |
| 网络 | 本地回环 (localhost) |

### 项目结构

```
01-AI-Blender-Bridge/
├── server/                      # Blender 服务端
│   ├── http_server.py           # HTTP 服务 (端口 8123)
│   └── ai_director.py           # AI 视觉总监
│
├── web-app/                     # Web 应用程序
│   ├── index.html               # 主页面
│   └── js/
│       └── app.js               # 前端逻辑
│
├── scripts/                     # 测试脚本
│   ├── test_http_server.py      # HTTP 服务测试
│   └── test_ai_director.py      # AI Director 测试
│
├── blender-plugin/              # Blender 插件 (可选)
│   └── ...
│
└── docs/                        # 文档
    └── AGENTIC_使用指南.md      # 本文件
```

### API Key 获取

#### Gemini API (推荐)

1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 创建 API Key
3. 设置环境变量：
   ```bash
   export GEMINI_API_KEY='your-api-key-here'
   ```

#### Qwen-VL API (阿里云)

1. 访问 [阿里云 DashScope](https://dashscope.console.aliyun.com/)
2. 创建 API Key
3. 设置环境变量：
   ```bash
   export DASHSCOPE_API_KEY='your-api-key-here'
   ```

---

## 🎯 功能说明

### 1️⃣ Setup Connection

**功能**: 连接 Blender HTTP 服务

- **Blender URL**: 输入 HTTP 服务地址 (默认 `http://localhost:8123`)
- **Test Connection**: 测试连接状态
- **安装脚本**: 一键复制 Blender 启动脚本

**状态指示**:
- 🟢 Connected: 已连接
- 🔴 Disconnected: 未连接

---

### 2️⃣ Scene Manager

**功能**: 3D 场景管理

#### 导入模型
- 输入 `.glb` 或 `.gltf` 文件的绝对路径
- 点击 **📦 Import Model** 导入

#### 物体列表
- 显示场景中所有物体
- 显示类型、位置、旋转、缩放
- 点击物体可编辑 Transform

#### Transform 编辑器
- **Location**: 位置 (X, Y, Z)
- **Rotation**: 旋转 (欧拉角，弧度)
- **Scale**: 缩放 (相对值)
- 点击 **✅ Apply Transform** 应用

#### Live Render
- 使用 Eevee 引擎实时渲染
- 分辨率：1920x1080
- 格式：PNG (Base64 回传)

---

### 3️⃣ AI Director

**功能**: AI 自动排布

#### 配置
- **AI Provider**: 选择 AI 模型
  - Gemini 2.5 Flash (推荐，强空间推理)
  - Qwen-VL (阿里云)
- **API Key**: 输入对应的 API Key

#### 目标输入
用自然语言描述你的目标，例如：

```
将立方体移动到 x=3 的位置，并绕 Y 轴旋转 90 度
```

```
把球体放到立方体旁边，让它们对齐
```

```
创建一个螺旋排列的物体阵列
```

#### Agent Loop
- **Max Iterations**: 最大迭代次数 (默认 10)
- **Start**: 启动自动循环
- **Stop**: 手动停止

**循环流程**:
1. 📸 渲染当前场景
2. 📦 获取物体列表
3. 🧠 AI 分析图像 + 坐标
4. 🔧 执行 Transform 命令
5. 重复 1-4 直到目标达成

---

## 🔌 API 参考

### 基础信息

- **基础 URL**: `http://localhost:8123`
- **数据格式**: JSON
- **CORS**: 允许所有来源 (`*`)

### 端点列表

#### GET /api/status

获取服务状态

**响应**:
```json
{
  "success": true,
  "status": "running",
  "blender_version": "4.0.0",
  "scene": "Scene",
  "object_count": 5
}
```

---

#### GET /api/scene/objects

获取场景所有物体

**响应**:
```json
{
  "success": true,
  "objects": [
    {
      "name": "Cube",
      "type": "MESH",
      "location": [0, 0, 0],
      "rotation": [0, 0, 0],
      "scale": [1, 1, 1],
      "visible": true,
      "selectable": true
    }
  ]
}
```

---

#### GET /api/object/{name}

获取单个物体信息

**路径参数**:
- `name`: 物体名称

**响应**:
```json
{
  "success": true,
  "object": {
    "name": "Cube",
    "type": "MESH",
    "location": [0, 0, 0],
    "rotation": [0, 0, 0],
    "scale": [1, 1, 1],
    "bounds": {
      "min": [-0.5, -0.5, -0.5],
      "max": [0.5, 0.5, 0.5]
    }
  }
}
```

---

#### PUT /api/object/{name}

设置物体 Transform

**请求体**:
```json
{
  "location": [1.0, 2.0, 0.5],
  "rotation": [0, 1.57, 0],
  "scale": [1.5, 1.5, 1.5]
}
```

**响应**:
```json
{
  "success": true,
  "message": "Success",
  "object": { ... }
}
```

---

#### POST /api/scene/import

导入 .glb/.gltf 文件

**请求体**:
```json
{
  "filepath": "/path/to/model.glb"
}
```

**响应**:
```json
{
  "success": true,
  "message": 3,
  "objects": ["Object_1", "Object_2", "Object_3"]
}
```

---

#### POST /api/render

渲染当前场景

**请求体**:
```json
{
  "width": 1920,
  "height": 1080
}
```

**响应**:
```json
{
  "success": true,
  "render": {
    "format": "PNG",
    "width": 1920,
    "height": 1080,
    "image_base64": "iVBORw0KGgoAAAANSUhEUgAA..."
  }
}
```

---

#### GET /api/render/settings

获取渲染设置

**响应**:
```json
{
  "success": true,
  "settings": {
    "engine": "BLENDER_EEVEE",
    "resolution_x": 1920,
    "resolution_y": 1080,
    "resolution_percentage": 100,
    "frame_current": 1,
    "frame_end": 250
  }
}
```

---

#### POST /api/scene/clear

清空场景 (保留相机和灯光)

**响应**:
```json
{
  "success": true,
  "message": "Scene cleared"
}
```

---

## 🐛 故障排查

### 问题 1: 无法连接 Blender

**症状**: `Connection refused` 或 `Disconnected`

**解决方案**:

1. 检查 Blender HTTP 服务是否运行
   ```python
   # 在 Blender 中重新运行
   exec(open('/path/to/server/http_server.py').read())
   ```

2. 检查端口 8123 是否被占用
   ```bash
   lsof -i :8123
   ```

3. 检查防火墙设置
   ```bash
   # macOS
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off
   ```

---

### 问题 2: CORS 跨域错误

**症状**: 浏览器控制台显示 CORS 错误

**解决方案**:

**Chrome/Edge**:
1. 点击地址栏锁图标
2. 选择 **网站设置**
3. 找到 **不安全内容** 设置为 **允许**
4. 刷新页面

**或使用 ngrok**:
```bash
ngrok http 8123
```
将生成的 HTTPS 地址填入 Blender URL

---

### 问题 3: AI 响应失败

**症状**: `AI analysis failed` 或 `No response from AI`

**解决方案**:

1. 检查 API Key 是否正确
   ```bash
   echo $GEMINI_API_KEY
   ```

2. 检查网络连接
   ```bash
   curl https://generativelanguage.googleapis.com
   ```

3. 检查 API 额度是否充足

4. 尝试降低图像分辨率
   ```javascript
   // 在 app.js 中修改
   width: 1280,  // 从 1920 降低到 1280
   height: 720   // 从 1080 降低到 720
   ```

---

### 问题 4: 导入.glb 失败

**症状**: `Import failed` 或 `File not found`

**解决方案**:

1. 使用绝对路径
   ```
   ✅ /Users/username/models/test.glb
   ❌ ./models/test.glb
   ```

2. 检查文件权限
   ```bash
   ls -la /path/to/model.glb
   ```

3. 验证文件格式
   ```bash
   file /path/to/model.glb
   ```

---

### 问题 5: 渲染失败

**症状**: `Render failed` 或空白图像

**解决方案**:

1. 检查场景中是否有相机
   - 没有相机会导致渲染失败
   - 添加默认相机：`Shift+A → Camera`

2. 检查渲染引擎设置
   - 确保使用 Eevee 引擎
   - 在 Blender 中：Render Properties → Render Engine → Eevee

3. 检查场景是否有物体
   - 空场景会渲染为黑色

---

## 📚 示例场景

### 示例 1: 简单物体移动

**目标**: 将立方体从原点移动到 (3, 0, 0)

**AI 指令**:
```
Move the cube to position x=3, y=0, z=0
```

**预期 AI 输出**:
```json
{
  "analysis": "The cube is at origin, needs to move to x=3",
  "commands": [
    {
      "object": "Cube",
      "action": "move",
      "location": [3, 0, 0],
      "reason": "Move to target position"
    }
  ],
  "goal_achieved": true,
  "confidence": 0.95
}
```

---

### 示例 2: 物体旋转

**目标**: 将立方体绕 Y 轴旋转 90 度

**AI 指令**:
```
Rotate the cube 90 degrees around the Y axis
```

**预期 AI 输出**:
```json
{
  "analysis": "The cube needs 90° rotation around Y",
  "commands": [
    {
      "object": "Cube",
      "action": "rotate",
      "rotation": [0, 1.57, 0],
      "reason": "90 degrees = π/2 radians ≈ 1.57"
    }
  ],
  "goal_achieved": true,
  "confidence": 0.9
}
```

---

### 示例 3: 多物体对齐

**目标**: 将球体放到立方体旁边并对齐

**AI 指令**:
```
Place the sphere next to the cube and align them
```

**预期 AI 输出**:
```json
{
  "analysis": "Need to position sphere adjacent to cube",
  "commands": [
    {
      "object": "Sphere",
      "action": "move",
      "location": [2.5, 0, 0],
      "reason": "Place sphere next to cube with gap"
    }
  ],
  "goal_achieved": false,
  "confidence": 0.8,
  "next_step": "Verify alignment and adjust if needed"
}
```

---

### 示例 4: 创建阵列

**目标**: 创建一排 5 个立方体

**AI 指令**:
```
Create a row of 5 cubes with equal spacing
```

**注意**: 这个任务需要 AI 理解需要复制物体，可能需要多次迭代或手动干预。

---

## 📞 支持与反馈

### 项目地址
- **GitHub**: (待添加)

### 问题反馈
- 提交 Issue 时请包含：
  - Blender 版本
  - 错误信息
  - 复现步骤
  - 截图 (如有)

### 更新日志

#### v1.0.0-Agentic (2026-03-19)
- ✅ Blender HTTP 服务端
- ✅ REST API (8 个端点)
- ✅ AI 视觉总监 (Gemini/Qwen-VL)
- ✅ Web 应用程序
- ✅ Agent Loop 自动循环
- ✅ CORS 跨域支持
- ✅ 完整测试脚本

---

**创建时间**: 2026-03-19  
**维护者**: ClawDaniel  
**版本**: v1.0.0-Agentic
