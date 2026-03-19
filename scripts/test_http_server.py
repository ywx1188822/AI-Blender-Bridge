#!/usr/bin/env python3
# Agentic 3D Studio - 测试脚本
# 版本：v1.0.0-Agentic
# 用途：测试 Blender HTTP 服务端 API

"""
使用方法:
1. 先在 Blender 中运行 server/http_server.py 启动服务
2. 运行此测试脚本：python3 test_http_server.py
"""

import urllib.request
import urllib.error
import json
import sys
import time

# ==================== 配置 ====================

BASE_URL = 'http://localhost:8123'
TIMEOUT = 30

# ==================== 工具函数 ====================

def api_request(endpoint, method='GET', data=None):
    """发送 API 请求"""
    url = f"{BASE_URL}{endpoint}"
    print(f"  → {method} {url}")
    
    try:
        req = urllib.request.Request(url, method=method)
        req.add_header('Content-Type', 'application/json')
        
        if data:
            req.data = json.dumps(data).encode('utf-8')
        
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            result = json.loads(response.read().decode('utf-8'))
            return True, result
    
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        return False, f"HTTP {e.code}: {error_body}"
    except urllib.error.URLError as e:
        return False, f"Connection error: {e.reason}"
    except Exception as e:
        return False, str(e)


def print_result(success, result, test_name=""):
    """打印测试结果"""
    if success:
        print(f"  ✅ {test_name} OK")
    else:
        print(f"  ❌ {test_name} FAILED: {result}")
    return success


# ==================== 测试用例 ====================

def test_01_server_status():
    """测试 1: 服务器状态"""
    print("\n【测试 1: 服务器状态】")
    
    success, result = api_request('/api/status')
    
    if success:
        print(f"  状态：{result.get('status', 'unknown')}")
        print(f"  Blender 版本：{result.get('blender_version', 'unknown')}")
        print(f"  场景：{result.get('scene', 'unknown')}")
        print(f"  物体数：{result.get('object_count', 0)}")
    
    return print_result(success, result, "服务器状态")


def test_02_scene_objects():
    """测试 2: 获取场景物体列表"""
    print("\n【测试 2: 获取场景物体列表】")
    
    success, result = api_request('/api/scene/objects')
    
    if success:
        objects = result.get('objects', [])
        print(f"  找到 {len(objects)} 个物体:")
        for obj in objects[:5]:  # 只显示前 5 个
            print(f"    - {obj['name']} ({obj['type']})")
        if len(objects) > 5:
            print(f"    ... 还有 {len(objects) - 5} 个")
    
    return print_result(success, result, "获取物体列表")


def test_03_get_object():
    """测试 3: 获取单个物体信息"""
    print("\n【测试 3: 获取单个物体信息】")
    
    # 先获取物体列表
    success, result = api_request('/api/scene/objects')
    if not success or not result.get('objects'):
        print("  ⚠️ 场景中没有物体，跳过此测试")
        return True
    
    obj_name = result['objects'][0]['name']
    print(f"  测试物体：{obj_name}")
    
    success, result = api_request(f'/api/object/{obj_name}')
    
    if success:
        obj = result.get('object', {})
        print(f"  位置：{obj.get('location', 'N/A')}")
        print(f"  旋转：{obj.get('rotation', 'N/A')}")
        print(f"  缩放：{obj.get('scale', 'N/A')}")
    
    return print_result(success, result, "获取物体信息")


def test_04_set_transform():
    """测试 4: 设置物体 Transform"""
    print("\n【测试 4: 设置物体 Transform】")
    
    # 先获取物体列表
    success, result = api_request('/api/scene/objects')
    if not success or not result.get('objects'):
        print("  ⚠️ 场景中没有物体，跳过此测试")
        return True
    
    # 找一个 Mesh 类型的物体
    obj_name = None
    for obj in result['objects']:
        if obj['type'] == 'MESH':
            obj_name = obj['name']
            break
    
    if not obj_name:
        print("  ⚠️ 没有 Mesh 物体，跳过此测试")
        return True
    
    print(f"  测试物体：{obj_name}")
    
    # 设置新位置
    test_data = {
        'location': [1.0, 2.0, 0.5],
        'rotation': [0.0, 0.0, 0.0],
        'scale': [1.5, 1.5, 1.5]
    }
    
    print(f"  设置位置：{test_data['location']}")
    print(f"  设置缩放：{test_data['scale']}")
    
    success, result = api_request(f'/api/object/{obj_name}', 'PUT', test_data)
    
    if success:
        # 验证设置是否生效
        success2, result2 = api_request(f'/api/object/{obj_name}')
        if success2:
            obj = result2.get('object', {})
            print(f"  验证位置：{obj.get('location', 'N/A')}")
            print(f"  验证缩放：{obj.get('scale', 'N/A')}")
    
    return print_result(success, result, "设置 Transform")


def test_05_render():
    """测试 5: 渲染测试"""
    print("\n【测试 5: 渲染测试】")
    
    print("  请求渲染 (1920x1080)...")
    
    success, result = api_request('/api/render', 'POST', {
        'width': 1920,
        'height': 1080
    })
    
    if success:
        render = result.get('render', {})
        image_size = len(render.get('image_base64', ''))
        print(f"  渲染格式：{render.get('format', 'unknown')}")
        print(f"  图像大小：{render.get('width')}x{render.get('height')}")
        print(f"  Base64 长度：{image_size} 字符")
    
    return print_result(success, result, "渲染")


def test_06_render_settings():
    """测试 6: 获取渲染设置"""
    print("\n【测试 6: 获取渲染设置】")
    
    success, result = api_request('/api/render/settings')
    
    if success:
        settings = result.get('settings', {})
        print(f"  渲染引擎：{settings.get('engine', 'unknown')}")
        print(f"  分辨率：{settings.get('resolution_x')}x{settings.get('resolution_y')}")
        print(f"  当前帧：{settings.get('frame_current')}")
    
    return print_result(success, result, "获取渲染设置")


def test_07_import_glb():
    """测试 7: 导入 GLB (可选)"""
    print("\n【测试 7: 导入 GLB (可选)】")
    
    # 这个测试需要实际的.glb 文件，默认跳过
    print("  ⚠️ 跳过 (需要实际的.glb 文件)")
    return True


def test_08_cors():
    """测试 8: CORS 跨域头"""
    print("\n【测试 8: CORS 跨域头】")
    
    url = f"{BASE_URL}/api/status"
    
    try:
        req = urllib.request.Request(url)
        req.add_header('Origin', 'http://localhost:3000')
        
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            headers = response.headers
            cors_header = headers.get('Access-Control-Allow-Origin', '')
            
            if cors_header == '*':
                print(f"  CORS 头：{cors_header} ✅")
                return print_result(True, {}, "CORS 跨域")
            else:
                print(f"  CORS 头：{cors_header or 'Missing'} ❌")
                return print_result(False, "Missing CORS header", "CORS 跨域")
    
    except Exception as e:
        return print_result(False, str(e), "CORS 跨域")


def test_09_invalid_object():
    """测试 9: 错误处理 - 不存在的物体"""
    print("\n【测试 9: 错误处理 - 不存在的物体】")
    
    success, result = api_request('/api/object/NonExistentObject_12345')
    
    if not success:
        print(f"  正确返回错误：{result}")
        return print_result(True, {}, "错误处理")
    else:
        print(f"  ❌ 应该返回错误但成功了")
        return print_result(False, "Should return error", "错误处理")


def test_10_invalid_endpoint():
    """测试 10: 错误处理 - 不存在的端点"""
    print("\n【测试 10: 错误处理 - 不存在的端点】")
    
    success, result = api_request('/api/nonexistent/endpoint')
    
    if not success:
        print(f"  正确返回错误：{result}")
        return print_result(True, {}, "错误处理")
    else:
        print(f"  ❌ 应该返回错误但成功了")
        return print_result(False, "Should return error", "错误处理")


# ==================== 测试运行器 ====================

def run_all_tests():
    """运行所有测试"""
    print("="*60)
    print("🧪 Agentic 3D Studio - HTTP Server 测试")
    print("="*60)
    print(f"目标服务器：{BASE_URL}")
    print(f"超时时间：{TIMEOUT}秒")
    print("="*60)
    
    # 先检查服务器是否运行
    print("\n【预检查：服务器连接】")
    success, result = api_request('/api/status')
    if not success:
        print(f"  ❌ 无法连接到服务器：{result}")
        print("\n  请先在 Blender 中运行：")
        print(f"    python3 {sys.argv[0].replace('test_http_server.py', 'server/http_server.py')}")
        print("\n  或者在 Blender Scripting 标签页中运行 server/http_server.py")
        return False
    
    print(f"  ✅ 服务器运行正常")
    
    # 运行所有测试
    tests = [
        ("服务器状态", test_01_server_status),
        ("获取物体列表", test_02_scene_objects),
        ("获取物体信息", test_03_get_object),
        ("设置 Transform", test_04_set_transform),
        ("渲染测试", test_05_render),
        ("获取渲染设置", test_06_render_settings),
        ("CORS 跨域", test_08_cors),
        ("错误处理 - 不存在物体", test_09_invalid_object),
        ("错误处理 - 不存在端点", test_10_invalid_endpoint),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ❌ 测试异常：{e}")
            results.append((name, False))
    
    # 打印总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    failed = sum(1 for _, r in results if not r)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {name}")
    
    print("\n" + "-"*60)
    print(f"总计：{total} 个测试")
    print(f"通过：{passed} ✅")
    print(f"失败：{failed} ❌")
    print(f"通过率：{passed/total*100:.1f}%")
    print("="*60)
    
    if failed == 0:
        print("\n🎉 所有测试通过!")
        return True
    else:
        print(f"\n⚠️  {failed} 个测试失败")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
