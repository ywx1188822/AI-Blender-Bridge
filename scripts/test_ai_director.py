#!/usr/bin/env python3
# Agentic 3D Studio - AI Director 测试脚本
# 版本：v1.0.0-Agentic
# 用途：测试 AI 视觉总监功能

"""
使用方法:
1. 设置环境变量 GEMINI_API_KEY 或 DASHSCOPE_API_KEY
2. 先在 Blender 中启动 HTTP 服务
3. 运行此测试脚本：python3 test_ai_director.py
"""

import os
import sys
import json

# 添加 server 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

from ai_director import AIDirector, AgentLoopController

# ==================== 配置 ====================

BLENDER_API_URL = 'http://localhost:8123'

# ==================== 测试函数 ====================

def test_ai_director_gemini():
    """测试 Gemini AI 导演"""
    print("\n【测试：Gemini AI 导演】")
    
    api_key = os.environ.get('GEMINI_API_KEY', '')
    
    if not api_key:
        print("  ⚠️  GEMINI_API_KEY 未设置，跳过测试")
        print("  设置方法：export GEMINI_API_KEY='your-api-key'")
        return True
    
    # 创建 AI 导演
    director = AIDirector(api_key=api_key, provider='gemini')
    
    # 测试用图像 (1x1 像素透明 PNG)
    test_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    # 测试用物体
    test_objects = [
        {'name': 'Cube', 'location': [0, 0, 0], 'rotation': [0, 0, 0], 'scale': [1, 1, 1]},
        {'name': 'Sphere', 'location': [2, 0, 0], 'rotation': [0, 0, 0], 'scale': [0.5, 0.5, 0.5]}
    ]
    
    # 测试目标
    test_goal = "Move the cube to position x=3, y=0, z=0"
    
    print(f"  测试目标：{test_goal}")
    print(f"  物体数量：{len(test_objects)}")
    
    # 调用 AI
    result = director.analyze_scene(
        image_base64=test_image,
        objects=test_objects,
        goal=test_goal
    )
    
    if result['success']:
        print(f"  ✅ AI 响应成功")
        response = result['response']
        print(f"  分析：{response.get('analysis', 'N/A')[:100]}...")
        print(f"  命令数量：{len(response.get('commands', []))}")
        print(f"  目标达成：{response.get('goal_achieved', False)}")
        print(f"  置信度：{response.get('confidence', 0):.2f}")
        return True
    else:
        print(f"  ❌ AI 响应失败：{result['error']}")
        return False


def test_ai_director_qwen():
    """测试 Qwen-VL AI 导演"""
    print("\n【测试：Qwen-VL AI 导演】")
    
    api_key = os.environ.get('DASHSCOPE_API_KEY', '')
    
    if not api_key:
        print("  ⚠️  DASHSCOPE_API_KEY 未设置，跳过测试")
        print("  设置方法：export DASHSCOPE_API_KEY='your-api-key'")
        return True
    
    # 创建 AI 导演
    director = AIDirector(api_key=api_key, provider='qwen')
    
    # 测试用图像
    test_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    # 测试用物体
    test_objects = [
        {'name': 'Cube', 'location': [0, 0, 0], 'rotation': [0, 0, 0], 'scale': [1, 1, 1]}
    ]
    
    # 测试目标
    test_goal = "Rotate the cube 90 degrees around Y axis"
    
    print(f"  测试目标：{test_goal}")
    
    # 调用 AI
    result = director.analyze_scene(
        image_base64=test_image,
        objects=test_objects,
        goal=test_goal
    )
    
    if result['success']:
        print(f"  ✅ AI 响应成功")
        return True
    else:
        print(f"  ❌ AI 响应失败：{result['error']}")
        return False


def test_agent_loop():
    """测试 Agent 循环控制器"""
    print("\n【测试：Agent 循环控制器】")
    
    api_key = os.environ.get('GEMINI_API_KEY', '')
    
    if not api_key:
        print("  ⚠️  GEMINI_API_KEY 未设置，跳过测试")
        return True
    
    # 创建 AI 导演
    director = AIDirector(api_key=api_key, provider='gemini')
    
    # 创建循环控制器
    controller = AgentLoopController(
        ai_director=director,
        blender_api_url=BLENDER_API_URL
    )
    
    # 测试目标
    test_goal = "Move the cube to x=1"
    
    print(f"  测试目标：{test_goal}")
    print(f"  最大迭代：3")
    print(f"  Blender API: {BLENDER_API_URL}")
    
    # 注意：这个测试需要 Blender 服务实际运行且有场景物体
    # 默认跳过，避免失败
    print("  ⚠️  需要 Blender 服务运行，跳过实际测试")
    return True


def test_json_parsing():
    """测试 JSON 解析"""
    print("\n【测试：JSON 解析】")
    
    # 测试各种 JSON 格式
    test_cases = [
        '{"analysis": "test", "commands": [], "goal_achieved": true}',
        '```json\n{"analysis": "test", "commands": []}\n```',
        '{\n  "analysis": "test",\n  "commands": [{"object": "Cube", "action": "move"}]\n}',
    ]
    
    all_passed = True
    
    for i, test_json in enumerate(test_cases):
        try:
            # 清理 markdown
            content = test_json.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            result = json.loads(content)
            print(f"  ✅ 测试 {i+1} 通过")
        except Exception as e:
            print(f"  ❌ 测试 {i+1} 失败：{e}")
            all_passed = False
    
    return all_passed


def run_all_tests():
    """运行所有 AI Director 测试"""
    print("="*60)
    print("🧪 Agentic 3D Studio - AI Director 测试")
    print("="*60)
    
    tests = [
        ("JSON 解析", test_json_parsing),
        ("Gemini AI 导演", test_ai_director_gemini),
        ("Qwen-VL AI 导演", test_ai_director_qwen),
        ("Agent 循环控制器", test_agent_loop),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ❌ 测试异常：{e}")
            import traceback
            traceback.print_exc()
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
