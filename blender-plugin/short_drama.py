import bpy
import json
import os
import tempfile
from pathlib import Path


class AIBRIDGE_OT_GenerateScript(bpy.types.Operator):
    """生成短剧剧本"""
    
    bl_idname = "aibridge.generate_script"
    bl_label = "生成剧本 📝"
    bl_description = "使用 LLM 生成短剧剧本"
    bl_options = {'REGISTER', 'UNDO'}
    
    theme: bpy.props.StringProperty(
        name="主题",
        description="短剧主题",
        default="AI 觉醒之日"
    )
    
    duration: bpy.props.IntProperty(
        name="时长 (秒)",
        description="短剧时长",
        default=180,
        min=30,
        max=600
    )
    
    style: bpy.props.EnumProperty(
        name="风格",
        description="短剧风格",
        items=[
            ("sci-fi", "科幻", "Science Fiction"),
            ("drama", "剧情", "Drama"),
            ("comedy", "喜剧", "Comedy"),
            ("action", "动作", "Action"),
            ("romance", "爱情", "Romance")
        ],
        default="sci-fi"
    )
    
    def execute(self, context):
        """执行剧本生成"""
        settings = context.scene.aibridge_settings
        
        # 调用 LLM API 生成剧本
        try:
            script = self.call_llm_api(
                theme=self.theme,
                duration=self.duration,
                style=self.style,
                provider=settings.llm_provider
            )
            
            # 保存剧本
            script_file = self.save_script(script, self.theme)
            
            self.report({'INFO'}, f"✅ 剧本生成完成：{script_file}")
            
            # 在文本编辑器中打开
            bpy.ops.text.open(filepath=str(script_file))
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"❌ 生成失败：{str(e)}")
            return {'CANCELLED'}
    
    def call_llm_api(self, theme, duration, style, provider="aliyun"):
        """调用 LLM API"""
        import requests
        
        prompt = f"""
请创作一个{duration}秒的短剧剧本。

**主题**: {theme}
**风格**: {style}

**要求**:
1. 包含 3-5 个场景
2. 每个场景包含：
   - 场景描述 (地点、时间、氛围)
   - 角色列表
   - 详细镜头描述 (景别、角度、运动)
   - 角色对话 (如有)
3. 输出 JSON 格式，包含以下字段：
   - title: 剧本标题
   - logline: 一句话梗概
   - scenes: 场景列表
   - characters: 角色列表

**JSON 格式示例**:
```json
{{
  "title": "剧本标题",
  "logline": "一句话梗概",
  "characters": [
    {{"name": "角色名", "age": 年龄，"description": "角色描述"}}
  ],
  "scenes": [
    {{
      "scene_number": 1,
      "location": "地点",
      "time": "时间",
      "description": "场景描述",
      "shots": [
        {{
          "shot_number": 1,
          "type": "景别 (特写/中景/全景)",
          "angle": "角度",
          "movement": "镜头运动",
          "description": "镜头描述"
        }}
      ]
    }}
  ]
}}
```
"""
        
        # 根据提供商调用不同 API
        if provider == "aliyun":
            return self.call_aliyun(prompt)
        elif provider == "kimi":
            return self.call_kimi(prompt)
        elif provider == "glm":
            return self.call_glm(prompt)
        else:
            raise ValueError(f"不支持的提供商：{provider}")
    
    def call_aliyun(self, prompt):
        """调用阿里云通义千问"""
        import requests
        
        settings = bpy.context.scene.aibridge_settings
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        headers = {
            "Authorization": f"Bearer {settings.api_key_aliyun}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "qwen-plus",
            "input": {"messages": [{"role": "user", "content": prompt}]},
            "parameters": {"result_format": "message"}
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        # 解析响应
        content = result["output"]["choices"][0]["message"]["content"]
        return self.extract_json(content)
    
    def call_kimi(self, prompt):
        """调用 Kimi API"""
        import requests
        
        settings = bpy.context.scene.aibridge_settings
        url = "https://api.moonshot.cn/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.api_key_kimi}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "moonshot-v1-8k",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        content = result["choices"][0]["message"]["content"]
        return self.extract_json(content)
    
    def call_glm(self, prompt):
        """调用智谱 GLM API"""
        import requests
        
        settings = bpy.context.scene.aibridge_settings
        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.api_key_glm}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "glm-4",
            "messages": [{"role": "user", "content": prompt}]
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        content = result["choices"][0]["message"]["content"]
        return self.extract_json(content)
    
    def extract_json(self, content):
        """从响应中提取 JSON"""
        import re
        
        # 尝试查找 JSON 代码块
        match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            # 如果没有代码块，尝试直接解析
            json_str = content
        
        return json.loads(json_str)
    
    def save_script(self, script, theme):
        """保存剧本到文件"""
        blend_path = bpy.path.abspath("//")
        if not blend_path:
            blend_path = os.path.join(tempfile.gettempdir(), "ai_blender_bridge")
        output_dir = Path(blend_path) / "scripts"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        safe_theme = "".join(c for c in theme if c.isalnum() or c in " -_")
        script_file = output_dir / f"{safe_theme}.json"
        
        # 保存 JSON
        with open(script_file, 'w', encoding='utf-8') as f:
            json.dump(script, f, ensure_ascii=False, indent=2)
        
        print(f"📄 剧本已保存：{script_file}")
        return script_file
    
    def invoke(self, context, event):
        """弹出对话框"""
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def draw(self, context):
        """绘制对话框"""
        layout = self.layout
        col = layout.column(align=True)
        col.prop(self, "theme", text="主题")
        col.prop(self, "duration", text="时长 (秒)")
        col.prop(self, "style", text="风格")


class AIBRIDGE_OT_DesignStoryboard(bpy.types.Operator):
    """设计分镜头"""
    
    bl_idname = "aibridge.design_storyboard"
    bl_label = "设计分镜 🎞️"
    bl_description = "将剧本转换为分镜头脚本"
    bl_options = {'REGISTER', 'UNDO'}
    
    script_file: bpy.props.StringProperty(
        name="剧本文件",
        description="选择剧本 JSON 文件",
        subtype='FILE_PATH'
    )
    
    def execute(self, context):
        """执行分镜设计"""
        if not self.script_file:
            self.report({'ERROR'}, "请选择剧本文件")
            return {'CANCELLED'}
        
        try:
            # 加载剧本
            with open(self.script_file, 'r', encoding='utf-8') as f:
                script = json.load(f)
            
            # 转换为分镜头
            storyboard = self.convert_to_storyboard(script)
            
            # 保存分镜
            storyboard_file = self.save_storyboard(storyboard, script.get("title", "storyboard"))
            
            self.report({'INFO'}, f"✅ 分镜设计完成：{storyboard_file}")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"❌ 设计失败：{str(e)}")
            return {'CANCELLED'}
    
    def convert_to_storyboard(self, script):
        """将剧本转换为分镜头"""
        storyboard = {
            "title": f"{script.get('title', 'Untitled')} - 分镜头",
            "scenes": []
        }
        
        for scene in script.get("scenes", []):
            storyboard_scene = {
                "scene_number": scene.get("scene_number", 0),
                "location": scene.get("location", ""),
                "shots": []
            }
            
            for shot in scene.get("shots", []):
                # 为每个镜头生成 ComfyUI 提示词
                prompt = self.generate_comfyui_prompt(shot, scene)
                
                storyboard_shot = {
                    "shot_number": shot.get("shot_number", 0),
                    "type": shot.get("type", ""),
                    "description": shot.get("description", ""),
                    "comfyui_prompt": prompt
                }
                storyboard_scene["shots"].append(storyboard_shot)
            
            storyboard["scenes"].append(storyboard_scene)
        
        return storyboard
    
    def generate_comfyui_prompt(self, shot, scene):
        """为镜头生成 ComfyUI 提示词"""
        # 根据镜头类型生成提示词
        shot_type = shot.get("type", "medium shot")
        description = shot.get("description", "")
        location = scene.get("location", "")
        
        prompt = f"{shot_type}, {description}, {location}, cinematic lighting, highly detailed, 8k"
        
        return prompt
    
    def save_storyboard(self, storyboard, title):
        """保存分镜头"""
        blend_path = bpy.path.abspath("//")
        if not blend_path:
            blend_path = os.path.join(tempfile.gettempdir(), "ai_blender_bridge")
        output_dir = Path(blend_path) / "storyboards"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        safe_title = "".join(c for c in title if c.isalnum() or c in " -_")
        storyboard_file = output_dir / f"{safe_title}_storyboard.json"
        
        with open(storyboard_file, 'w', encoding='utf-8') as f:
            json.dump(storyboard, f, ensure_ascii=False, indent=2)
        
        print(f"📋 分镜头已保存：{storyboard_file}")
        return storyboard_file
    
    def invoke(self, context, event):
        """弹出文件选择器"""
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def draw(self, context):
        """绘制对话框"""
        layout = self.layout
        layout.prop(self, "script_file", text="剧本文件")


def register():
    """注册操作符"""
    bpy.utils.register_class(AIBRIDGE_OT_GenerateScript)
    bpy.utils.register_class(AIBRIDGE_OT_DesignStoryboard)


def unregister():
    """注销操作符"""
    bpy.utils.unregister_class(AIBRIDGE_OT_DesignStoryboard)
    bpy.utils.unregister_class(AIBRIDGE_OT_GenerateScript)
