# 🧐 Agentic 3D Studio 需求差距分析

**分析日期**: 2026-03-19  
**当前版本**: v0.2.0  
**目标版本**: v1.0.0-Agentic

---

## 📊 核心需求 vs 当前状态

### 用户需求场景

```
┌─────────────────────────────────────────────────────────────┐
│  Agentic 3D Studio (代理式 3D 工作流控制台)                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Blender 本地服务端 (REST API)                            │
│     └── HTTP 服务 (端口 8123) 控制 Blender                   │
│                                                             │
│  2. 3D 场景与零件管理 (Scene Manager)                         │
│     ├── .glb 文件导入                                        │
│     ├── 实时读取物体坐标/旋转/缩放                            │
│     └── Live Render (Eevee 渲染回传)                          │
│                                                             │
│  3. AI 视觉总监闭环 (AI Director)                             │
│     ├── 自然语言目标输入                                     │
│     ├── AI 渲染画面 → 分析 → 输出 Transform 指令               │
│     ├── 发送给 Blender 执行 → 再次渲染验证                    │
│     └── 循环直到目标达成或达到最大迭代次数                     │
│                                                             │
│  4. 人工随时接管 (Human in the Loop)                         │
│     └── 手动修改后 AI 自动获取最新状态                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 功能差距分析

### 1. Blender 本地服务端 (REST API)

| 需求 | 当前状态 | 差距 |
|------|----------|------|
| HTTP 服务 (端口 8123) | ❌ 无 | 🔴 缺失 |
| REST API 控制 Blender | ❌ 无 | 🔴 缺失 |
| CORS 跨域支持 | ❌ 无 | 🔴 缺失 |
| 场景数据 JSON 导出 | ❌ 无 | 🔴 缺失 |
| Transform 指令接收 | ❌ 无 | 🔴 缺失 |

**当前实现**: 仅 Blender 插件 UI，无独立 HTTP 服务

---

### 2. 3D 场景与零件管理 (Scene Manager)

| 需求 | 当前状态 | 差距 |
|------|----------|------|
| .glb/.gltf 文件导入 | ⚠️ 基础支持 | 🟡 部分满足 |
| 实时读取物体坐标/旋转/缩放 | ❌ 无 | 🔴 缺失 |
| 物体列表显示 | ❌ 无 | 🔴 缺失 |
| Live Render (Eevee) | ❌ 无 | 🔴 缺失 |
| 渲染图像回传 Web | ❌ 无 | 🔴 缺失 |

**当前实现**: 仅有角色/视频生成，无场景管理功能

---

### 3. AI 视觉总监闭环 (AI Director)

| 需求 | 当前状态 | 差距 |
|------|----------|------|
| 自然语言目标输入 | ❌ 无 | 🔴 缺失 |
| Gemini/Qwen-VL 视觉模型 | ❌ 无 | 🔴 缺失 |
| AI 分析画面 + 坐标 | ❌ 无 | 🔴 缺失 |
| JSON Transform 指令输出 | ❌ 无 | 🔴 缺失 |
| 自动循环执行 | ❌ 无 | 🔴 缺失 |
| 目标达成判断 | ❌ 无 | 🔴 缺失 |

**当前实现**: 仅有剧本/分镜生成，无视觉空间推理能力

---

### 4. 人工随时接管 (Human in the Loop)

| 需求 | 当前状态 | 差距 |
|------|----------|------|
| 手动修改模型 | ✅ Blender 原生 | 🟢 满足 |
| AI 自动获取最新状态 | ❌ 无 | 🔴 缺失 |
| 人机协同工作流 | ❌ 无 | 🔴 缺失 |

**当前实现**: 无状态同步机制

---

### 5. Web 应用程序

| 需求 | 当前状态 | 差距 |
|------|----------|------|
| Web UI (Setup Connection) | ❌ 无 | 🔴 缺失 |
| Web UI (Scene Manager) | ❌ 无 | 🔴 缺失 |
| Web UI (AI Director) | ❌ 无 | 🔴 缺失 |
| Agent Loop 控制 | ❌ 无 | 🔴 缺失 |
| 实时状态显示 | ❌ 无 | 🔴 缺失 |

**当前实现**: 仅有 Blender 插件，无 Web 应用

---

## 📋 缺失功能清单

### 🔴 关键缺失 (P0)

1. **Blender HTTP 服务端** (新增模块)
   - `server/http_server.py` - Flask/FastAPI HTTP 服务
   - REST API: GET/PUT/POST/DELETE
   - CORS 跨域配置
   - 端口 8123 监听

2. **场景管理 API** (新增模块)
   - `server/scene_api.py` - 场景操作接口
   - 导入.glb/.gltf
   - 获取物体列表
   - 获取/设置 Transform (位置/旋转/缩放)
   - 删除/复制物体

3. **渲染回传 API** (新增模块)
   - `server/render_api.py` - 渲染接口
   - Eevee 实时渲染
   - 图像编码 (Base64/PNG)
   - 图像回传 HTTP 响应

4. **Web 应用程序** (新增项目)
   - `web-app/` - 独立 Web 项目
   - Setup Connection 页面
   - Scene Manager 页面
   - AI Director 页面
   - Agent Loop 控制

5. **AI 视觉总监** (新增模块)
   - `server/ai_director.py` - AI 导演逻辑
   - Gemini/Qwen-VL 集成
   - 视觉空间推理
   - Transform 指令生成
   - 循环控制逻辑

---

### 🟡 次要缺失 (P1)

6. **状态同步机制**
   - 物体状态变更监听
   - 手动修改检测
   - AI 状态同步

7. **迭代控制**
   - 最大迭代次数设置
   - 目标达成判断
   - 提前终止条件

8. **日志与调试**
   - AI 决策日志
   - Transform 历史记录
   - 可视化调试界面

---

## 🏗️ 新架构设计

```
┌──────────────────────────────────────────────────────────────┐
│                       Agentic 3D Studio                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐         HTTP/REST          ┌─────────────┐ │
│  │   Web App   │ ◄────────────────────────► │   Blender   │ │
│  │  (前端 UI)   │        端口 8123            │  本地服务端  │ │
│  └─────────────┘                            └─────────────┘ │
│         │                                      │             │
│         │                                      │             │
│         ▼                                      ▼             │
│  ┌─────────────┐                        ┌─────────────┐     │
│  │ AI Director │                        │  Scene API  │     │
│  │ (Gemini VL) │                        │ (Transform) │     │
│  └─────────────┘                        └─────────────┘     │
│         │                                      │             │
│         │                                      ▼             │
│         │                        ┌─────────────────────┐     │
│         │                        │   Render API (Eevee)│     │
│         │                        └─────────────────────┘     │
│         │                                      │             │
│         └──────────────────┬───────────────────┘             │
│                            │                                 │
│                            ▼                                 │
│                   ┌─────────────────┐                        │
│                   │  Agent Loop     │                        │
│                   │  (自动循环)      │                        │
│                   └─────────────────┘                        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 📁 新增目录结构

```
01-AI-Blender-Bridge/
├── blender-plugin/              # 现有插件 (保留)
│   ├── __init__.py
│   ├── ui/
│   └── ...
│
├── server/                      # 新增：Blender 服务端
│   ├── __init__.py
│   ├── http_server.py           # HTTP 服务 (Flask/FastAPI)
│   ├── scene_api.py             # 场景管理 API
│   ├── render_api.py            # 渲染回传 API
│   ├── ai_director.py           # AI 视觉总监
│   └── agent_loop.py            # 自动循环控制
│
├── web-app/                     # 新增：Web 应用程序
│   ├── index.html               # 主页面
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── app.js               # 主应用逻辑
│   │   ├── connection.js        # 连接管理
│   │   ├── scene-manager.js     # 场景管理
│   │   └── ai-director.js       # AI 导演
│   └── assets/
│
├── scripts/                     # 新增：安装脚本
│   ├── install-server.py        # 服务端安装脚本
│   ├── setup-blender.py         # Blender 配置脚本
│   └── run-web-app.sh           # Web 应用启动脚本
│
└── docs/
    ├── AGENTIC_ARCHITECTURE.md  # 架构文档
    ├── API_REFERENCE.md         # API 参考
    └── SETUP_GUIDE.md           # 安装指南
```

---

## 📅 实现计划

### Phase 1: Blender HTTP 服务端 (2 天)

**目标**: 实现 Blender 本地服务端，支持 REST API 控制

| 任务 | 预计时间 | 优先级 |
|------|----------|--------|
| 1.1 Flask/FastAPI 集成 | 2 小时 | P0 |
| 1.2 HTTP 服务启动脚本 | 2 小时 | P0 |
| 1.3 CORS 跨域配置 | 1 小时 | P0 |
| 1.4 场景管理 API | 4 小时 | P0 |
| 1.5 渲染回传 API | 4 小时 | P0 |
| 1.6 Transform API | 3 小时 | P0 |

**交付物**:
- `server/http_server.py` ✅
- `server/scene_api.py` ✅
- `server/render_api.py` ✅
- Blender 启动脚本 ✅

---

### Phase 2: Web 应用程序 (2 天)

**目标**: 实现 Web UI，支持连接管理和场景操作

| 任务 | 预计时间 | 优先级 |
|------|----------|--------|
| 2.1 项目脚手架 | 2 小时 | P0 |
| 2.2 Setup Connection 页面 | 3 小时 | P0 |
| 2.3 Scene Manager 页面 | 4 小时 | P0 |
| 2.4 物体列表显示 | 3 小时 | P0 |
| 2.5 Transform 编辑 UI | 3 小时 | P0 |
| 2.6 Live Render 显示 | 3 小时 | P0 |

**交付物**:
- `web-app/index.html` ✅
- `web-app/js/app.js` ✅
- Web UI 完整页面 ✅

---

### Phase 3: AI 视觉总监 (2 天)

**目标**: 实现 AI 自动排布功能

| 任务 | 预计时间 | 优先级 |
|------|----------|--------|
| 3.1 Gemini/Qwen-VL 集成 | 3 小时 | P0 |
| 3.2 视觉提示词工程 | 3 小时 | P0 |
| 3.3 Transform 指令生成 | 4 小时 | P0 |
| 3.4 Agent Loop 循环 | 4 小时 | P0 |
| 3.5 目标达成判断 | 2 小时 | P0 |
| 3.6 AI Director UI | 4 小时 | P0 |

**交付物**:
- `server/ai_director.py` ✅
- `server/agent_loop.py` ✅
- AI Director 页面 ✅

---

### Phase 4: 人机协同 (1 天)

**目标**: 实现人工接管和状态同步

| 任务 | 预计时间 | 优先级 |
|------|----------|--------|
| 4.1 状态变更监听 | 3 小时 | P0 |
| 4.2 手动修改检测 | 2 小时 | P0 |
| 4.3 AI 状态同步 | 2 小时 | P0 |
| 4.4 日志系统 | 2 小时 | P1 |
| 4.5 调试界面 | 3 小时 | P1 |

**交付物**:
- 状态同步机制 ✅
- 日志系统 ✅

---

## 🎯 总体时间线

```
2026-03-19 (今日)
└── 需求分析 ✅ 完成

2026-03-20 ~ 2026-03-21 (2 天)
└── Phase 1: Blender HTTP 服务端
    ├── HTTP 服务 + CORS
    ├── 场景管理 API
    └── 渲染回传 API

2026-03-22 ~ 2026-03-23 (2 天)
└── Phase 2: Web 应用程序
    ├── Setup Connection
    ├── Scene Manager
    └── Live Render

2026-03-24 ~ 2026-03-25 (2 天)
└── Phase 3: AI 视觉总监
    ├── Gemini 集成
    ├── Agent Loop
    └── AI Director UI

2026-03-26 (1 天)
└── Phase 4: 人机协同
    ├── 状态同步
    └── 日志系统

2026-03-27
└── 集成测试 + 文档

2026-03-28 🎯
└── v1.0.0-Agentic 发布
```

---

## 📊 工作量估算

| Phase | 任务数 | 预计工时 | 日历时间 |
|-------|--------|----------|----------|
| Phase 1 | 6 | 16 小时 | 2 天 |
| Phase 2 | 6 | 18 小时 | 2 天 |
| Phase 3 | 6 | 20 小时 | 2 天 |
| Phase 4 | 5 | 12 小时 | 1 天 |
| 测试 + 文档 | - | 8 小时 | 1 天 |
| **总计** | **23** | **74 小时** | **8 天** |

---

## ⚠️ 技术风险

### 风险 1: Blender Python 环境限制

**问题**: Blender 内置 Python 可能缺少 Flask/FastAPI 依赖

**应对**:
- 使用 Blender 内置 `http.server` 模块
- 或提供外部 Python 环境配置指南
- 或使用 WebSocket 替代 HTTP

### 风险 2: CORS 跨域问题

**问题**: Web 应用 (HTTPS) 请求本地 HTTP 服务被浏览器阻止

**应对**:
- 提供 ngrok HTTPS 映射方案
- 或在 Chrome 中允许不安全内容
- 或使用浏览器扩展临时禁用 CORS

### 风险 3: AI 视觉推理准确性

**问题**: AI 可能无法准确理解 3D 空间关系

**应对**:
- 使用 Gemini 2.5 Flash (强空间推理)
- 提供 Few-shot 示例
- 添加人工修正机制

---

## 🚀 立即可开始的任务

### Task 1: Blender HTTP 服务端原型 (今日)

```python
# server/http_server.py 原型

import bpy
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class BlenderAPIHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """处理 GET 请求"""
        if self.path == '/api/scene/objects':
            # 获取场景物体列表
            objects = [obj.name for obj in bpy.context.scene.objects]
            self.send_json({'objects': objects})
        
        elif self.path.startswith('/api/object/'):
            # 获取物体 Transform
            obj_name = self.path.split('/')[-1]
            obj = bpy.data.objects.get(obj_name)
            if obj:
                self.send_json({
                    'location': list(obj.location),
                    'rotation': list(obj.rotation_euler),
                    'scale': list(obj.scale)
                })
    
    def do_PUT(self):
        """处理 PUT 请求 (设置 Transform)"""
        content_length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(content_length))
        
        obj_name = data.get('object')
        obj = bpy.data.objects.get(obj_name)
        
        if obj:
            if 'location' in data:
                obj.location = data['location']
            if 'rotation' in data:
                obj.rotation_euler = data['rotation']
            if 'scale' in data:
                obj.scale = data['scale']
            
            self.send_json({'status': 'success'})
    
    def send_json(self, data):
        """发送 JSON 响应"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

# 启动服务
server = HTTPServer(('localhost', 8123), BlenderAPIHandler)
server.serve_forever()
```

---

## 📝 结论

**当前 AI Blender Bridge v0.2.0 与 Agentic 3D Studio 需求存在重大差距**:

- ✅ **现有功能**: 短剧编导、角色生成、视频生成 (Blender 插件)
- ❌ **缺失功能**: HTTP 服务端、Web 应用、AI 视觉总监、Agent Loop

**需要新增 4 个核心模块**:
1. Blender HTTP 服务端 (REST API)
2. Web 应用程序 (前端 UI)
3. AI 视觉总监 (Gemini VL)
4. Agent Loop (自动循环)

**预计开发周期**: 8 天 (74 小时)  
**预计完成日期**: 2026-03-28

---

**分析人**: ClawDaniel  
**创建时间**: 2026-03-19 13:20  
**状态**: 等待确认启动开发
