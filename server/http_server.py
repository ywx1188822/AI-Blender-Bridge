# Blender 本地服务端 - REST API
# 版本：v1.0.0-Agentic
# 功能：HTTP 服务 (端口 8123) 控制 Blender

"""
使用方法:
1. 在 Blender Scripting 标签页中运行此脚本
2. 服务将在 http://localhost:8123 启动
3. 使用 REST API 控制 Blender

API 端点:
- GET  /api/scene/objects          - 获取场景物体列表
- GET  /api/object/{name}          - 获取物体 Transform
- PUT  /api/object/{name}          - 设置物体 Transform
- POST /api/scene/import           - 导入.glb 文件
- POST /api/render                 - 渲染当前画面
- GET  /api/status                 - 服务状态
"""

import bpy
import json
import base64
import tempfile
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote
import threading
import queue
import time

# ==================== 全局状态 ====================

server_instance = None
server_thread = None
is_running = False

# 线程安全：主线程任务队列
# bpy 操作必须在 Blender 主线程执行，HTTP 服务运行在后台线程
_main_thread_queue = queue.Queue()


def _process_main_thread_queue():
    """Blender 定时器回调：在主线程中执行队列中的任务"""
    while not _main_thread_queue.empty():
        try:
            func, result_holder, event = _main_thread_queue.get_nowait()
            try:
                result_holder['result'] = func()
                result_holder['success'] = True
            except Exception as e:
                result_holder['error'] = str(e)
                result_holder['success'] = False
            finally:
                event.set()
        except queue.Empty:
            break
    return 0.05  # 每 50ms 检查一次


def run_on_main_thread(func, timeout=120):
    """
    将函数调度到 Blender 主线程执行并等待结果。
    用于从 HTTP 服务线程安全地调用 bpy 操作。
    """
    result_holder = {'result': None, 'success': False, 'error': None}
    event = threading.Event()
    _main_thread_queue.put((func, result_holder, event))

    if not event.wait(timeout=timeout):
        raise TimeoutError(f"Main thread operation timed out after {timeout}s")

    if not result_holder['success']:
        raise RuntimeError(result_holder['error'])

    return result_holder['result']

# ==================== Blender API 封装 ====================

class BlenderSceneAPI:
    """场景管理 API（所有方法通过 run_on_main_thread 调度到主线程执行）"""

    @staticmethod
    def get_objects():
        """获取场景所有物体（线程安全）"""
        def _get():
            objects = []
            for obj in bpy.context.scene.objects:
                objects.append({
                    'name': obj.name,
                    'type': obj.type,
                    'location': list(obj.location),
                    'rotation': list(obj.rotation_euler),
                    'scale': list(obj.scale),
                    'visible': obj.hide_viewport == False,
                    'selectable': obj.hide_select == False
                })
            return objects
        return run_on_main_thread(_get)

    @staticmethod
    def get_object(name):
        """获取单个物体信息（线程安全）"""
        def _get():
            obj = bpy.data.objects.get(name)
            if not obj:
                return None
            return {
                'name': obj.name,
                'type': obj.type,
                'location': list(obj.location),
                'rotation': list(obj.rotation_euler),
                'scale': list(obj.scale),
                'visible': obj.hide_viewport == False,
                'selectable': obj.hide_select == False,
                'bounds': {
                    'min': list(obj.bound_box[0]),
                    'max': list(obj.bound_box[6])
                } if obj.type == 'MESH' else None
            }
        return run_on_main_thread(_get)

    @staticmethod
    def set_transform(name, location=None, rotation=None, scale=None):
        """设置物体 Transform（线程安全）"""
        def _set():
            obj = bpy.data.objects.get(name)
            if not obj:
                return False, f"Object '{name}' not found"
            if location is not None:
                obj.location = location
            if rotation is not None:
                obj.rotation_euler = rotation
            if scale is not None:
                obj.scale = scale
            bpy.context.view_layer.update()
            return True, "Success"
        return run_on_main_thread(_set)

    @staticmethod
    def import_glb(filepath):
        """导入.glb/.gltf 文件（线程安全）"""
        if not os.path.exists(filepath):
            return False, f"File not found: {filepath}"
        def _import():
            bpy.ops.import_scene.gltf(filepath=filepath)
            imported = bpy.context.selected_objects
            return True, {
                'imported_count': len(imported),
                'objects': [obj.name for obj in imported]
            }
        try:
            return run_on_main_thread(_import)
        except Exception as e:
            return False, str(e)

    @staticmethod
    def delete_object(name):
        """删除物体（线程安全）"""
        def _delete():
            obj = bpy.data.objects.get(name)
            if not obj:
                return False, f"Object '{name}' not found"
            bpy.data.objects.remove(obj, do_unlink=True)
            return True, "Deleted"
        return run_on_main_thread(_delete)

    @staticmethod
    def clear_scene():
        """清空场景 - 保留相机和灯光（线程安全，迭代安全）"""
        def _clear():
            objects_to_remove = [
                obj for obj in bpy.context.scene.objects
                if obj.type not in ['CAMERA', 'LIGHT']
            ]
            for obj in objects_to_remove:
                bpy.data.objects.remove(obj, do_unlink=True)
            return True, "Scene cleared"
        return run_on_main_thread(_clear)


class BlenderRenderAPI:
    """渲染 API（所有方法通过 run_on_main_thread 调度到主线程执行）"""

    @staticmethod
    def render_live(format='PNG', width=1920, height=1080):
        """实时渲染 - Eevee（线程安全，兼容 Blender 3.x/4.x）"""
        def _render():
            # 兼容 Blender 4.0+ (EEVEE_NEXT) 和 3.x (EEVEE)
            if bpy.app.version >= (4, 0, 0):
                bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
            else:
                bpy.context.scene.render.engine = 'BLENDER_EEVEE'

            bpy.context.scene.render.resolution_x = width
            bpy.context.scene.render.resolution_y = height
            bpy.context.scene.render.resolution_percentage = 100

            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, f"blender_render_{int(time.time())}.png")

            bpy.context.scene.render.filepath = temp_file
            bpy.ops.render.render(write_still=True)

            with open(temp_file, 'rb') as f:
                image_data = f.read()

            try:
                os.remove(temp_file)
            except OSError:
                pass

            return {
                'format': 'PNG',
                'width': width,
                'height': height,
                'image_base64': base64.b64encode(image_data).decode('utf-8')
            }
        return run_on_main_thread(_render, timeout=120)

    @staticmethod
    def get_render_settings():
        """获取渲染设置（线程安全）"""
        def _get():
            scene = bpy.context.scene
            return {
                'engine': scene.render.engine,
                'resolution_x': scene.render.resolution_x,
                'resolution_y': scene.render.resolution_y,
                'resolution_percentage': scene.render.resolution_percentage,
                'frame_current': scene.frame_current,
                'frame_end': scene.frame_end
            }
        return run_on_main_thread(_get)


# ==================== HTTP 请求处理器 ====================

class BlenderAPIHandler(BaseHTTPRequestHandler):
    """HTTP API 请求处理器"""
    
    # 禁用日志
    def log_message(self, format, *args):
        print(f"[API] {args[0]}")
    
    # CORS 头
    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    # 发送 JSON 响应
    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    # 发送错误响应
    def send_error_response(self, message, status=400):
        self.send_json_response({
            'success': False,
            'error': message
        }, status)
    
    # 处理 OPTIONS 请求 (CORS preflight)
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    # 处理 GET 请求
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        try:
            # 获取场景物体列表
            if path == '/api/scene/objects':
                objects = BlenderSceneAPI.get_objects()
                self.send_json_response({
                    'success': True,
                    'objects': objects
                })

            # 获取单个物体
            elif path.startswith('/api/object/'):
                obj_name = unquote(path.split('/')[-1])
                obj_data = BlenderSceneAPI.get_object(obj_name)

                if obj_data:
                    self.send_json_response({
                        'success': True,
                        'object': obj_data
                    })
                else:
                    self.send_error_response(f"Object '{obj_name}' not found", 404)

            # 获取渲染设置
            elif path == '/api/render/settings':
                settings = BlenderRenderAPI.get_render_settings()
                self.send_json_response({
                    'success': True,
                    'settings': settings
                })

            # 服务状态（线程安全读取 bpy 数据）
            elif path == '/api/status':
                def _status():
                    return {
                        'success': True,
                        'status': 'running',
                        'blender_version': bpy.app.version_string,
                        'scene': bpy.context.scene.name,
                        'object_count': len(bpy.context.scene.objects)
                    }
                self.send_json_response(run_on_main_thread(_status))

            # 404
            else:
                self.send_error_response("Not Found", 404)

        except Exception as e:
            self.send_error_response(str(e), 500)
    
    # 处理 PUT 请求 (设置 Transform)
    def do_PUT(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}
            
            # 设置物体 Transform
            if path.startswith('/api/object/'):
                obj_name = unquote(path.split('/')[-1])
                
                location = data.get('location')
                rotation = data.get('rotation')
                scale = data.get('scale')
                
                success, result = BlenderSceneAPI.set_transform(
                    obj_name,
                    location=location,
                    rotation=rotation,
                    scale=scale
                )
                
                if success:
                    self.send_json_response({
                        'success': True,
                        'message': result,
                        'object': BlenderSceneAPI.get_object(obj_name)
                    })
                else:
                    self.send_error_response(result, 404)
            else:
                self.send_error_response("Not Found", 404)
        
        except json.JSONDecodeError:
            self.send_error_response("Invalid JSON", 400)
        except Exception as e:
            self.send_error_response(str(e), 500)
    
    # 处理 POST 请求
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}
            
            # 导入.glb 文件
            if path == '/api/scene/import':
                filepath = data.get('filepath')
                
                if not filepath:
                    self.send_error_response("Missing 'filepath' parameter", 400)
                    return
                
                success, result = BlenderSceneAPI.import_glb(filepath)
                
                if success:
                    self.send_json_response({
                        'success': True,
                        'message': result['imported_count'],
                        'objects': result['objects']
                    })
                else:
                    self.send_error_response(result, 500)
            
            # 渲染
            elif path == '/api/render':
                width = data.get('width', 1920)
                height = data.get('height', 1080)
                
                result = BlenderRenderAPI.render_live(
                    width=width,
                    height=height
                )
                
                self.send_json_response({
                    'success': True,
                    'render': result
                })
            
            # 删除物体
            elif path.startswith('/api/object/') and data.get('_method') == 'DELETE':
                obj_name = unquote(path.split('/')[-1])
                success, result = BlenderSceneAPI.delete_object(obj_name)
                
                if success:
                    self.send_json_response({
                        'success': True,
                        'message': result
                    })
                else:
                    self.send_error_response(result, 404)
            
            # 清空场景
            elif path == '/api/scene/clear':
                success, result = BlenderSceneAPI.clear_scene()
                
                if success:
                    self.send_json_response({
                        'success': True,
                        'message': result
                    })
                else:
                    self.send_error_response(result, 500)
            
            # 404
            else:
                self.send_error_response("Not Found", 404)
        
        except json.JSONDecodeError:
            self.send_error_response("Invalid JSON", 400)
        except Exception as e:
            self.send_error_response(str(e), 500)


# ==================== 服务器管理 ====================

class BlenderHTTPServer:
    """Blender HTTP 服务器"""
    
    def __init__(self, host='localhost', port=8123):
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
        self.is_running = False
    
    def start(self):
        """启动服务器"""
        if self.is_running:
            print(f"[Server] Already running on {self.host}:{self.port}")
            return False

        try:
            self.server = HTTPServer((self.host, self.port), BlenderAPIHandler)
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            self.is_running = True

            # 注册主线程定时器，用于处理来自 HTTP 线程的 bpy 调用
            if not bpy.app.timers.is_registered(_process_main_thread_queue):
                bpy.app.timers.register(_process_main_thread_queue, persistent=True)

            print("="*60)
            print(f"🚀 Blender HTTP Server started")
            print(f"   URL: http://{self.host}:{self.port}")
            print(f"   API Docs: http://{self.host}:{self.port}/api/status")
            print(f"   Thread-safe dispatch: enabled")
            print(f"   Press Ctrl+C to stop")
            print("="*60)

            return True

        except OSError as e:
            print(f"[Server] Failed to start: {e}")
            return False

    def stop(self):
        """停止服务器"""
        if not self.is_running:
            return

        if self.server:
            self.server.shutdown()
            self.server = None

        # 注销主线程定时器
        if bpy.app.timers.is_registered(_process_main_thread_queue):
            bpy.app.timers.unregister(_process_main_thread_queue)

        self.is_running = False
        print("[Server] Stopped")


# ==================== 全局实例 ====================

server = BlenderHTTPServer()


# ==================== Blender 操作符 ====================

class AIBRIDGE_OT_StartServer(bpy.types.Operator):
    """启动 HTTP 服务"""
    
    bl_label = "Start HTTP Server"
    bl_idname = "aibridge.start_server"
    bl_description = "启动 Blender HTTP 服务 (端口 8123)"
    
    def execute(self, context):
        if server.start():
            self.report({'INFO'}, "HTTP Server started on :8123")
        else:
            self.report({'WARNING'}, "Failed to start server")
        return {'FINISHED'}


class AIBRIDGE_OT_StopServer(bpy.types.Operator):
    """停止 HTTP 服务"""
    
    bl_label = "Stop HTTP Server"
    bl_idname = "aibridge.stop_server"
    bl_description = "停止 Blender HTTP 服务"
    
    def execute(self, context):
        server.stop()
        self.report({'INFO'}, "HTTP Server stopped")
        return {'FINISHED'}


# ==================== 注册 ====================

def register():
    """注册操作符"""
    bpy.utils.register_class(AIBRIDGE_OT_StartServer)
    bpy.utils.register_class(AIBRIDGE_OT_StopServer)
    print("✅ Blender HTTP Server API registered")


def unregister():
    """注销操作符"""
    server.stop()
    bpy.utils.unregister_class(AIBRIDGE_OT_StopServer)
    bpy.utils.unregister_class(AIBRIDGE_OT_StartServer)
    print("❌ Blender HTTP Server API unregistered")


# ==================== 自动启动 ====================

if __name__ == "__main__":
    # 注册并启动服务
    register()
    server.start()
