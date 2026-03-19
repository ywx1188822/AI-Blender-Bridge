# Wan 2.2 Video Generation Module
# 图生视频功能模块

import bpy
import requests
import json
import time
import os
import tempfile
from pathlib import Path


class AIBRIDGE_OT_GenerateWanVideo(bpy.types.Operator):
    """使用 Wan 2.2 生成视频"""
    
    bl_idname = "aibridge.generate_wan_video"
    bl_label = "Wan 2.2 图生视频 🎬"
    bl_description = "使用 Wan 2.2 模型从图像生成视频"
    bl_options = {'REGISTER', 'UNDO'}
    
    image_path: bpy.props.StringProperty(
        name="输入图像",
        description="用于生成视频的输入图像路径",
        default="",
        subtype='FILE_PATH'
    )
    
    prompt: bpy.props.StringProperty(
        name="提示词",
        description="视频生成提示词",
        default="smooth animation, high quality, cinematic lighting",
        subtype='LINE'
    )
    
    negative_prompt: bpy.props.StringProperty(
        name="负向提示词",
        description="不想要的内容",
        default="ugly, deformed, noisy, blurry, low quality",
        subtype='LINE'
    )
    
    steps: bpy.props.IntProperty(
        name="步数",
        description="采样步数",
        default=30,
        min=20,
        max=100
    )
    
    cfg_scale: bpy.props.FloatProperty(
        name="CFG Scale",
        description="提示词引导系数",
        default=7.0,
        min=1.0,
        max=20.0
    )
    
    seed: bpy.props.IntProperty(
        name="种子",
        description="随机种子 (-1 为随机)",
        default=-1
    )
    
    video_length: bpy.props.IntProperty(
        name="视频长度 (帧)",
        description="生成视频的帧数",
        default=48,
        min=24,
        max=120
    )
    
    fps: bpy.props.IntProperty(
        name="帧率",
        description="每秒帧数",
        default=24,
        min=12,
        max=60
    )
    
    def execute(self, context):
        """执行视频生成"""
        settings = context.scene.aibridge_settings
        
        try:
            # 检查输入图像
            if not self.image_path:
                self.report({'ERROR'}, "请选择输入图像")
                return {'CANCELLED'}
            
            # 加载 Wan 2.2 工作流
            workflow = self.load_wan_workflow()
            
            # 更新工作流参数
            self.update_workflow(workflow, {
                "prompt": self.prompt,
                "negative_prompt": self.negative_prompt,
                "steps": self.steps,
                "cfg_scale": self.cfg_scale,
                "seed": self.seed if self.seed != -1 else self.random_seed(),
                "video_length": self.video_length,
                "fps": self.fps,
                "model": settings.wan22_model,
                "image_path": self.image_path
            })
            
            # 提交到 ComfyUI
            prompt_id = self.submit_to_comfyui(workflow, settings.comfyui_server)
            
            self.report({'INFO'}, f"🎬 视频生成任务已提交 (ID: {prompt_id})")
            
            # 等待完成
            video_files = self.wait_for_completion(prompt_id, settings.comfyui_server)
            
            # 加载到 Blender
            self.load_video_to_blender(video_files, settings.comfyui_server)
            
            self.report({'INFO'}, f"✅ 视频生成完成，共 {len(video_files)} 个文件")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"视频生成失败：{str(e)}")
            return {'CANCELLED'}
    
    def load_wan_workflow(self):
        """加载 Wan 2.2 工作流"""
        workflow_file = Path(__file__).parent / "comfyui_workflows" / "wan22_video.json"
        
        if not workflow_file.exists():
            # 如果工作流文件不存在，创建默认工作流
            return self.create_default_wan_workflow()
        
        with open(workflow_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def create_default_wan_workflow(self):
        """创建默认 Wan 2.2 工作流"""
        workflow = {
            "1": {
                "class_type": "LoadImage",
                "inputs": {
                    "image": "",
                    "upload": "image"
                }
            },
            "2": {
                "class_type": "WanVideoModelLoader",
                "inputs": {
                    "model_name": "wan2.1-i2v-720p-14B",
                    "precision": "fp16",
                    "load_vae": True
                }
            },
            "3": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": self.prompt,
                    "clip": ["2", "clip"]
                }
            },
            "4": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": self.negative_prompt,
                    "clip": ["2", "clip"]
                }
            },
            "5": {
                "class_type": "WanVideoSampler",
                "inputs": {
                    "model": ["2", "model"],
                    "positive": ["3", "conditioning"],
                    "negative": ["4", "conditioning"],
                    "vae": ["2", "vae"],
                    "image": ["1", "image"],
                    "steps": self.steps,
                    "cfg": self.cfg_scale,
                    "seed": self.seed,
                    "video_length": self.video_length,
                    "fps": self.fps
                }
            },
            "6": {
                "class_type": "SaveAnimatedWEBP",
                "inputs": {
                    "images": ["5", "images"],
                    "filename_prefix": "wan_video",
                    "fps": self.fps,
                    "quality": 90
                }
            }
        }
        
        return workflow
    
    def update_workflow(self, workflow, params):
        """更新工作流参数"""
        # 更新提示词
        if "prompt" in params:
            if "3" in workflow and "inputs" in workflow["3"]:
                workflow["3"]["inputs"]["text"] = params["prompt"]
        
        if "negative_prompt" in params:
            if "4" in workflow and "inputs" in workflow["4"]:
                workflow["4"]["inputs"]["text"] = params["negative_prompt"]
        
        # 更新采样参数
        if "steps" in params and "5" in workflow:
            workflow["5"]["inputs"]["steps"] = params["steps"]
        
        if "cfg_scale" in params and "5" in workflow:
            workflow["5"]["inputs"]["cfg"] = params["cfg_scale"]
        
        if "seed" in params and "5" in workflow:
            workflow["5"]["inputs"]["seed"] = params["seed"]
        
        if "video_length" in params and "5" in workflow:
            workflow["5"]["inputs"]["video_length"] = params["video_length"]
        
        if "fps" in params:
            if "5" in workflow:
                workflow["5"]["inputs"]["fps"] = params["fps"]
            if "6" in workflow:
                workflow["6"]["inputs"]["fps"] = params["fps"]
        
        # 更新模型
        if "model" in params and "2" in workflow:
            workflow["2"]["inputs"]["model_name"] = params["model"]
        
        # 更新输入图像
        if "image_path" in params:
            if "1" in workflow:
                workflow["1"]["inputs"]["image"] = params["image_path"]
    
    def submit_to_comfyui(self, workflow, server):
        """提交到 ComfyUI"""
        import uuid
        
        url = f"http://{server}/prompt"
        client_id = str(uuid.uuid4())
        
        response = requests.post(url, json={
            "prompt": workflow,
            "client_id": client_id
        })
        response.raise_for_status()
        result = response.json()
        
        return result["prompt_id"]
    
    def wait_for_completion(self, prompt_id, server, timeout=600):
        """等待生成完成"""
        url = f"http://{server}/history/{prompt_id}"
        
        start_time = time.time()
        print(f"⏳ 等待视频生成完成... (超时：{timeout}秒)")
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url)
                response.raise_for_status()
                history = response.json()
                
                if prompt_id in history:
                    outputs = history[prompt_id].get("outputs", {})
                    video_files = []
                    
                    for node_id, node_out in outputs.items():
                        if "gifs" in node_out:
                            for gif in node_out["gifs"]:
                                if "filename" in gif and "subfolder" in gif:
                                    video_files.append({
                                        "filename": gif["filename"],
                                        "subfolder": gif["subfolder"],
                                        "type": gif.get("type", "output")
                                    })
                        if "images" in node_out:
                            for img in node_out["images"]:
                                if "filename" in img and "subfolder" in img:
                                    video_files.append({
                                        "filename": img["filename"],
                                        "subfolder": img["subfolder"],
                                        "type": img.get("type", "output")
                                    })
                    
                    if video_files:
                        print(f"✅ 视频生成完成，共 {len(video_files)} 个文件")
                        return video_files
                
                # 显示进度
                elapsed = int(time.time() - start_time)
                print(f"⏰ 已等待 {elapsed}秒...")
                
            except Exception as e:
                print(f"⚠️ 轮询失败：{e}")
            
            time.sleep(3)
        
        raise TimeoutError(f"视频生成超时 ({timeout}秒)")
    
    def load_video_to_blender(self, video_files, server):
        """加载视频到 Blender"""
        blend_path = bpy.path.abspath("//")
        if not blend_path:
            blend_path = os.path.join(tempfile.gettempdir(), "ai_blender_bridge")
        output_dir = Path(blend_path) / "output" / "videos"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for video in video_files:
            # 下载视频
            url = f"http://{server}/view"
            params = {
                "filename": video["filename"],
                "subfolder": video["subfolder"],
                "type": video["type"]
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # 保存到本地
            video_file = output_dir / video["filename"]
            with open(video_file, 'wb') as f:
                f.write(response.content)
            
            print(f"📹 视频已保存：{video_file}")
            
            # 如果是 GIF/WEBP，加载为图像序列
            if video["filename"].endswith(('.gif', '.webp')):
                try:
                    bpy.ops.image.open(filepath=str(video_file))
                    print(f"🖼️ 已加载 {video['filename']} 到 Blender")
                except Exception as e:
                    print(f"⚠️ 加载图像失败：{e}")
        
        print(f"✅ 已加载 {len(video_files)} 个视频文件")
    
    def random_seed(self):
        """生成随机种子"""
        import random
        return random.randint(0, 2**32 - 1)
    
    def invoke(self, context, event):
        """调用时打开文件选择器"""
        if not self.image_path:
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}
        return self.execute(context)


def register():
    """注册模块"""
    bpy.utils.register_class(AIBRIDGE_OT_GenerateWanVideo)
    print("✅ Wan 2.2 视频生成模块已注册")


def unregister():
    """注销模块"""
    bpy.utils.unregister_class(AIBRIDGE_OT_GenerateWanVideo)
    print("✅ Wan 2.2 视频生成模块已注销")


if __name__ == "__main__":
    register()
