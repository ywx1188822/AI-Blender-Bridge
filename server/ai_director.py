# AI 视觉总监 - Gemini/Qwen-VL 集成
# 版本：v1.0.0-Agentic
# 功能：视觉空间推理 + Transform 指令生成

"""
AI Director 工作流:
1. 请求 Blender 渲染当前场景
2. 发送图像 + 自然语言目标给 AI 视觉模型
3. AI 分析图像并输出 JSON 格式的 Transform 指令
4. 发送指令给 Blender 执行
5. 重复 1-4 直到目标达成或达到最大迭代次数
"""

import json
import base64
import urllib.request
import urllib.error
from typing import Dict, List, Optional, Any


# ==================== AI 模型配置 ====================

class AIModelConfig:
    """AI 模型配置"""
    
    # Gemini 2.5 Flash (推荐 - 强空间推理)
    GEMINI = {
        'provider': 'gemini',
        'model': 'gemini-2.5-flash-preview-04-17',
        'api_url': 'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
        'api_key_env': 'GEMINI_API_KEY',
    }
    
    # Qwen-VL (阿里云)
    QWEN_VL = {
        'provider': 'qwen',
        'model': 'qwen-vl-max',
        'api_url': 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation',
        'api_key_env': 'DASHSCOPE_API_KEY',
    }


# ==================== AI 导演 ====================

class AIDirector:
    """AI 视觉总监"""
    
    def __init__(self, api_key: str, provider: str = 'gemini'):
        self.api_key = api_key
        self.provider = provider
        self.config = AIModelConfig.GEMINI if provider == 'gemini' else AIModelConfig.QWEN_VL
        
        # 系统提示词 - 空间推理专家
        self.system_prompt = """You are an expert 3D spatial reasoning AI assistant. Your task is to analyze rendered images of a 3D scene and provide precise transform commands to achieve a user-specified goal.

You will receive:
1. A rendered image of the current 3D scene
2. A list of objects with their current positions, rotations, and scales
3. A natural language goal from the user

You must output a JSON response with the following structure:
{
  "analysis": "Brief analysis of the current scene and what needs to change",
  "goal_understood": "Restate the goal in your own words",
  "commands": [
    {
      "object": "object_name",
      "action": "move|rotate|scale",
      "location": [x, y, z],  // optional, for move
      "rotation": [rx, ry, rz],  // optional, for rotate (Euler angles in radians)
      "scale": [sx, sy, sz],  // optional, for scale
      "reason": "Why this transformation is needed"
    }
  ],
  "goal_achieved": true|false,  // Whether the goal has been achieved
  "confidence": 0.0-1.0,  // Confidence in the solution
  "next_step": "What should be done next if goal not achieved"
}

Important guidelines:
- Blender uses right-handed coordinate system: +X right, +Y forward, +Z up
- Rotations are in Euler angles (radians), order XYZ
- Scale is relative (1.0 = original size)
- Be precise with numerical values
- If multiple objects need adjustment, include all in commands array
- If goal is already achieved, set goal_achieved=true and commands=[]
"""
    
    def analyze_scene(self, image_base64: str, objects: List[Dict], goal: str) -> Dict:
        """
        分析场景并生成 Transform 指令
        
        参数:
            image_base64: 渲染图像的 Base64 编码
            objects: 物体列表 (包含名称和当前 Transform)
            goal: 用户目标 (自然语言)
        
        返回:
            AI 响应字典 (包含 commands、goal_achieved 等)
        """
        
        if self.provider == 'gemini':
            return self._call_gemini(image_base64, objects, goal)
        else:
            return self._call_qwen_vl(image_base64, objects, goal)
    
    def _extract_json(self, content):
        """从 AI 响应中提取 JSON（处理 markdown 包裹和各种格式）"""
        # 如果 content 是列表（Qwen-VL 可能返回 list 格式），提取文本部分
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, str):
                    text_parts.append(item)
                elif isinstance(item, dict) and 'text' in item:
                    text_parts.append(item['text'])
            content = '\n'.join(text_parts)

        content = content.strip()

        # 去除 markdown 代码块包裹
        if '```json' in content:
            start = content.index('```json') + 7
            end = content.index('```', start) if '```' in content[start:] else len(content)
            content = content[start:end]
        elif '```' in content:
            start = content.index('```') + 3
            end = content.index('```', start) if '```' in content[start:] else len(content)
            content = content[start:end]

        content = content.strip()
        return json.loads(content)

    def _call_gemini(self, image_base64: str, objects: List[Dict], goal: str) -> Dict:
        """调用 Gemini API"""
        
        # 构建物体信息文本
        objects_text = "Current scene objects:\n"
        for obj in objects:
            objects_text += f"- {obj['name']}: location={obj['location']}, rotation={obj['rotation']}, scale={obj['scale']}\n"
        
        # 构建用户提示词
        user_prompt = f"""{objects_text}

User Goal: {goal}

Please analyze the image and provide transform commands to achieve the goal.
Output ONLY valid JSON, no markdown or additional text."""
        
        # 构建 API 请求
        api_url = self.config['api_url'].format(model=self.config['model'])
        
        request_data = {
            "contents": [{
                "parts": [
                    {"text": self.system_prompt},
                    {"text": user_prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": image_base64
                        }
                    }
                ]
            }],
            "generationConfig": {
                "temperature": 0.2,
                "topP": 0.8,
                "topK": 40,
                "maxOutputTokens": 2048,
            }
        }
        
        # 发送请求（注意：API key 通过 URL 参数传递，这是 Google API 的标准方式）
        url = f"{api_url}?key={self.api_key}"

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(request_data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )

            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))

            # 解析响应
            if 'candidates' in result and len(result['candidates']) > 0:
                content = result['candidates'][0]['content']['parts'][0]['text']

                # 提取 JSON (去除可能的 markdown 格式)
                ai_response = self._extract_json(content)

                return {
                    'success': True,
                    'response': ai_response
                }
            else:
                return {
                    'success': False,
                    'error': 'No response from AI'
                }
        
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            return {
                'success': False,
                'error': f'HTTP Error {e.code}: {error_body}'
            }
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'JSON parse error: {e}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _call_qwen_vl(self, image_base64: str, objects: List[Dict], goal: str) -> Dict:
        """调用 Qwen-VL API (阿里云)"""
        
        # 构建物体信息文本
        objects_text = "当前场景物体:\n"
        for obj in objects:
            objects_text += f"- {obj['name']}: 位置={obj['location']}, 旋转={obj['rotation']}, 缩放={obj['scale']}\n"
        
        # 构建用户提示词
        user_prompt = f"""{objects_text}

用户目标：{goal}

请分析图像并提供变换指令来实现目标。
仅输出有效的 JSON 格式，不要 markdown 或其他文字。"""
        
        # 构建 API 请求
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        request_data = {
            "model": self.config['model'],
            "input": {
                "messages": [
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {"image": f"data:image/png;base64,{image_base64}"},
                            {"text": user_prompt}
                        ]
                    }
                ]
            },
            "parameters": {
                "temperature": 0.2,
                "top_p": 0.8,
                "max_tokens": 2048
            }
        }
        
        try:
            req = urllib.request.Request(
                self.config['api_url'],
                data=json.dumps(request_data).encode('utf-8'),
                headers=headers
            )
            
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            # 解析响应
            if 'output' in result and 'choices' in result['output']:
                content = result['output']['choices'][0]['message']['content']

                # 使用统一的 JSON 提取方法（兼容 string 和 list 格式）
                ai_response = self._extract_json(content)

                return {
                    'success': True,
                    'response': ai_response
                }
            else:
                return {
                    'success': False,
                    'error': 'No response from AI'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# ==================== Agent 循环控制器 ====================

class AgentLoopController:
    """Agent 自动循环控制器"""
    
    def __init__(self, ai_director: AIDirector, blender_api_url: str):
        self.ai_director = ai_director
        self.blender_api_url = blender_api_url
        self.max_iterations = 10
        self.current_iteration = 0
        self.is_running = False
        self.history = []
    
    def start(self, goal: str, max_iterations: int = 10):
        """
        启动 Agent 循环
        
        参数:
            goal: 用户目标 (自然语言)
            max_iterations: 最大迭代次数
        """
        self.max_iterations = max_iterations
        self.current_iteration = 0
        self.is_running = True
        self.history = []
        
        print(f"🤖 Agent Loop started")
        print(f"   Goal: {goal}")
        print(f"   Max iterations: {max_iterations}")
        
        while self.is_running and self.current_iteration < self.max_iterations:
            self.current_iteration += 1
            print(f"\n{'='*60}")
            print(f"📍 Iteration {self.current_iteration}/{self.max_iterations}")
            print(f"{'='*60}")
            
            # Step 1: 渲染当前场景
            print("📸 Rendering scene...")
            render_result = self._render_scene()
            
            if not render_result['success']:
                print(f"❌ Render failed: {render_result['error']}")
                break
            
            # Step 2: 获取物体列表
            print("📦 Getting objects...")
            objects_result = self._get_objects()
            
            if not objects_result['success']:
                print(f"❌ Get objects failed: {objects_result['error']}")
                break
            
            # Step 3: AI 分析
            print("🧠 AI analyzing...")
            ai_result = self.ai_director.analyze_scene(
                image_base64=render_result['image_base64'],
                objects=objects_result['objects'],
                goal=goal
            )
            
            if not ai_result['success']:
                print(f"❌ AI analysis failed: {ai_result['error']}")
                break
            
            ai_response = ai_result['response']
            
            # 保存历史记录
            self.history.append({
                'iteration': self.current_iteration,
                'ai_response': ai_response
            })
            
            # 打印 AI 分析
            print(f"\n📝 AI Analysis:")
            print(f"   {ai_response.get('analysis', 'N/A')}")
            print(f"   Goal achieved: {ai_response.get('goal_achieved', False)}")
            print(f"   Confidence: {ai_response.get('confidence', 0):.2f}")
            
            # 检查目标是否达成
            if ai_response.get('goal_achieved', False):
                print(f"\n✅ Goal achieved!")
                self.is_running = False
                break
            
            # Step 4: 执行 Transform 命令
            commands = ai_response.get('commands', [])
            
            if commands:
                print(f"\n🔧 Executing {len(commands)} commands...")
                
                for cmd in commands:
                    success = self._execute_command(cmd)
                    if success:
                        print(f"   ✅ {cmd.get('object', 'unknown')}: {cmd.get('action', 'unknown')}")
                    else:
                        print(f"   ❌ Failed: {cmd}")
            else:
                print(f"\n⚠️  No commands to execute")
            
            # 检查是否继续
            if self.current_iteration >= self.max_iterations:
                print(f"\n⚠️  Max iterations reached")
                self.is_running = False
        
        print(f"\n{'='*60}")
        print(f"🏁 Agent Loop finished")
        print(f"{'='*60}")
        
        return self.history
    
    def _render_scene(self) -> Dict:
        """渲染场景"""
        try:
            url = f"{self.blender_api_url}/api/render"
            
            req = urllib.request.Request(
                url,
                data=json.dumps({'width': 1920, 'height': 1080}).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            return {
                'success': True,
                'image_base64': result['render']['image_base64']
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_objects(self) -> Dict:
        """获取物体列表"""
        try:
            url = f"{self.blender_api_url}/api/scene/objects"
            
            with urllib.request.urlopen(url, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            return {
                'success': True,
                'objects': result['objects']
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _execute_command(self, cmd: Dict) -> bool:
        """执行单个 Transform 命令"""
        try:
            obj_name = cmd.get('object')
            action = cmd.get('action')
            
            if not obj_name:
                return False
            
            # 构建请求数据
            data = {}
            
            if action == 'move' and 'location' in cmd:
                data['location'] = cmd['location']
            elif action == 'rotate' and 'rotation' in cmd:
                data['rotation'] = cmd['rotation']
            elif action == 'scale' and 'scale' in cmd:
                data['scale'] = cmd['scale']
            
            if not data:
                return False
            
            # 发送 PUT 请求
            url = f"{self.blender_api_url}/api/object/{obj_name}"
            
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='PUT'
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            return result.get('success', False)
        
        except Exception as e:
            print(f"   Error executing command: {e}")
            return False
    
    def stop(self):
        """停止循环"""
        self.is_running = False
        print("⏹️  Agent Loop stopped")


# ==================== 测试函数 ====================

def test_ai_director():
    """测试 AI 导演"""
    import os
    
    # 从环境变量获取 API Key
    api_key = os.environ.get('GEMINI_API_KEY', '')
    
    if not api_key:
        print("❌ Please set GEMINI_API_KEY environment variable")
        return
    
    # 创建 AI 导演
    director = AIDirector(api_key=api_key, provider='gemini')
    
    # 测试用图像 (占位符)
    test_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    # 测试用物体
    test_objects = [
        {'name': 'Cube', 'location': [0, 0, 0], 'rotation': [0, 0, 0], 'scale': [1, 1, 1]},
        {'name': 'Sphere', 'location': [2, 0, 0], 'rotation': [0, 0, 0], 'scale': [0.5, 0.5, 0.5]}
    ]
    
    # 测试目标
    goal = "Move the cube to x=3 and rotate it 90 degrees around Y axis"
    
    print("🧪 Testing AI Director...")
    result = director.analyze_scene(
        image_base64=test_image,
        objects=test_objects,
        goal=goal
    )
    
    if result['success']:
        print("✅ AI Director test passed")
        print(json.dumps(result['response'], indent=2))
    else:
        print(f"❌ AI Director test failed: {result['error']}")


if __name__ == "__main__":
    test_ai_director()
