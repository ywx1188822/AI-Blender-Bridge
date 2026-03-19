import bpy
import requests
import json
import os
import tempfile
from pathlib import Path


class AIBRIDGE_OT_GenerateCharacter(bpy.types.Operator):
    """生成角色"""
    
    bl_idname = "aibridge.generate_character"
    bl_label = "生成角色 🎨"
    bl_description = "使用 ComfyUI 生成角色图像"
    bl_options = {'REGISTER', 'UNDO'}
    
    prompt: bpy.props.StringProperty(
        name="提示词",
        description="角色描述提示词",
        default="1girl, silver hair, blue eyes, school uniform, standing pose, white background",
        subtype='LINE'
    )
    
    negative_prompt: bpy.props.StringProperty(
        name="负向提示词",
        description="不想要的内容",
        default="ugly, deformed, noisy, blurry, low quality, extra limbs, bad anatomy",
        subtype='LINE'
    )
    
    steps: bpy.props.IntProperty(
        name="步数",
        description="采样步数",
        default=20,
        min=10,
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
    
    def execute(self, context):
        """执行角色生成"""
        settings = context.scene.aibridge_settings
        
        try:
            # 加载角色生成工作流
            workflow = self.load_character_workflow()
            
            # 修改提示词参数
            self.update_workflow(workflow, {
                "prompt": self.prompt,
                "negative_prompt": self.negative_prompt,
                "steps": self.steps,
                "cfg_scale": self.cfg_scale,
                "seed": self.seed if self.seed != -1 else self.random_seed()
            })
            
            # 提交到 ComfyUI
            prompt_id = self.submit_to_comfyui(workflow, settings.comfyui_server)
            
            # 等待完成
            images = self.wait_for_completion(prompt_id, settings.comfyui_server)
            
            # 加载到 Blender
            self.load_images_to_blender(images, settings.comfyui_server)
            
            self.report({'INFO'}, f"✅ 角色生成完成，共 {len(images)} 张图片")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"❌ 生成失败：{str(e)}")
            return {'CANCELLED'}
    
    def load_character_workflow(self):
        """加载角色生成工作流"""
        workflow_file = Path(__file__).parent / "comfyui_workflows" / "character_gen.json"
        
        if not workflow_file.exists():
            # 如果工作流文件不存在，创建默认工作流
            return self.create_default_workflow()
        
        with open(workflow_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def create_default_workflow(self):
        """创建默认工作流"""
        return {
            "3": {
                "inputs": {"ckpt_name": "v1-5-pruned-emaonly.ckpt"},
                "class_type": "CheckpointLoaderSimple"
            },
            "5": {
                "inputs": {
                    "width": 512,
                    "height": 768,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "6": {
                "inputs": {"text": "", "clip": ["3", 1]},
                "class_type": "CLIPTextEncode"
            },
            "7": {
                "inputs": {"text": "", "clip": ["3", 1]},
                "class_type": "CLIPTextEncode"
            },
            "8": {
                "inputs": {
                    "seed": 0,
                    "steps": 20,
                    "cfg": 7.0,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["3", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "KSampler"
            },
            "9": {
                "inputs": {"samples": ["8", 0], "vae": ["3", 2]},
                "class_type": "VAEDecode"
            },
            "10": {
                "inputs": {"filename_prefix": "characters/", "images": ["9", 0]},
                "class_type": "SaveImage"
            }
        }
    
    def update_workflow(self, workflow, params):
        """更新工作流参数"""
        # 更新提示词
        if "prompt" in params:
            workflow["6"]["inputs"]["text"] = params["prompt"]
        if "negative_prompt" in params:
            workflow["7"]["inputs"]["text"] = params["negative_prompt"]
        
        # 更新采样参数
        if "steps" in params:
            workflow["8"]["inputs"]["steps"] = params["steps"]
        if "cfg_scale" in params:
            workflow["8"]["inputs"]["cfg"] = params["cfg_scale"]
        if "seed" in params:
            workflow["8"]["inputs"]["seed"] = params["seed"]
    
    def submit_to_comfyui(self, workflow, server):
        """提交到 ComfyUI"""
        url = f"http://{server}/prompt"
        
        import uuid
        client_id = str(uuid.uuid4())
        
        response = requests.post(url, json={
            "prompt": workflow,
            "client_id": client_id
        }, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        return result["prompt_id"]
    
    def wait_for_completion(self, prompt_id, server, timeout=300):
        """等待生成完成"""
        import time
        
        url = f"http://{server}/history/{prompt_id}"
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            history = response.json()
            
            if prompt_id in history:
                outputs = history[prompt_id].get("outputs", {})
                images = []
                
                for node_id, node_out in outputs.items():
                    if "images" in node_out:
                        for img in node_out["images"]:
                            if "filename" in img and "subfolder" in img:
                                images.append({
                                    "filename": img["filename"],
                                    "subfolder": img["subfolder"],
                                    "type": img.get("type", "output")
                                })
                
                if images:
                    return images
            
            time.sleep(2)
        
        raise TimeoutError("生成超时")
    
    def load_images_to_blender(self, images, server):
        """加载图片到 Blender"""
        blend_path = bpy.path.abspath("//")
        if not blend_path:
            blend_path = os.path.join(tempfile.gettempdir(), "ai_blender_bridge")
        output_dir = Path(blend_path) / "output" / "characters"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for img in images:
            # 下载图片
            url = f"http://{server}/view"
            params = {
                "filename": img["filename"],
                "subfolder": img["subfolder"],
                "type": img["type"]
            }
            
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            
            # 保存图片到本地
            img_file = output_dir / img["filename"]
            with open(img_file, 'wb') as f:
                f.write(response.content)
            
            # 加载为 Blender 图像
            bpy.ops.image.open(filepath=str(img_file))
        
        print(f"🖼️ 已加载 {len(images)} 张图片到 Blender")
    
    def random_seed(self):
        """生成随机种子"""
        import random
        return random.randint(0, 2**32 - 1)
    
    def invoke(self, context, event):
        """弹出对话框"""
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def draw(self, context):
        """绘制对话框"""
        layout = self.layout
        col = layout.column(align=True)
        col.prop(self, "prompt", text="提示词")
        col.prop(self, "negative_prompt", text="负向提示词")
        row = col.row(align=True)
        row.prop(self, "steps", text="步数")
        row.prop(self, "cfg_scale", text="CFG")
        col.prop(self, "seed", text="种子")


class AIBRIDGE_OT_GenerateCharacterCard(bpy.types.Operator):
    """生成三视图角色卡"""
    
    bl_idname = "aibridge.generate_character_card"
    bl_label = "生成三视图角色卡 📋"
    bl_description = "生成角色三视图 (正面/侧面/背面)"
    bl_options = {'REGISTER', 'UNDO'}
    
    character_name: bpy.props.StringProperty(
        name="角色名称",
        description="角色名称",
        default="Character_001"
    )
    
    def execute(self, context):
        """执行三视图生成"""
        settings = context.scene.aibridge_settings
        
        try:
            # 加载三视图工作流
            workflow = self.load_character_card_workflow()
            
            # 提交到 ComfyUI
            prompt_id = self.submit_to_comfyui(workflow, settings.comfyui_server)
            
            # 等待完成
            images = self.wait_for_completion(prompt_id, settings.comfyui_server)
            
            # 加载到 Blender
            self.load_images_to_blender(images, settings.comfyui_server, self.character_name)
            
            self.report({'INFO'}, f"✅ 三视图生成完成")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"❌ 生成失败：{str(e)}")
            return {'CANCELLED'}
    
    def load_character_card_workflow(self):
        """加载三视图工作流"""
        workflow_file = Path(__file__).parent / "comfyui_workflows" / "character_card.json"
        
        if not workflow_file.exists():
            # 返回默认工作流
            return self.create_default_workflow()
        
        with open(workflow_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def create_default_workflow(self):
        """创建默认三视图工作流"""
        return {
            "3": {
                "inputs": {"ckpt_name": "v1-5-pruned-emaonly.ckpt"},
                "class_type": "CheckpointLoaderSimple"
            },
            "5": {
                "inputs": {
                    "width": 768,
                    "height": 512,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "6": {
                "inputs": {
                    "text": "character sheet, three views, front view, side view, back view, white background",
                    "clip": ["3", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "7": {
                "inputs": {
                    "text": "ugly, deformed, noisy, blurry",
                    "clip": ["3", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "8": {
                "inputs": {
                    "seed": 0,
                    "steps": 20,
                    "cfg": 7.0,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["3", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "KSampler"
            },
            "9": {
                "inputs": {"samples": ["8", 0], "vae": ["3", 2]},
                "class_type": "VAEDecode"
            },
            "10": {
                "inputs": {"filename_prefix": "character_cards/", "images": ["9", 0]},
                "class_type": "SaveImage"
            }
        }
    
    def submit_to_comfyui(self, workflow, server):
        """提交到 ComfyUI"""
        url = f"http://{server}/prompt"
        
        import uuid
        client_id = str(uuid.uuid4())
        
        response = requests.post(url, json={
            "prompt": workflow,
            "client_id": client_id
        }, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        return result["prompt_id"]
    
    def wait_for_completion(self, prompt_id, server, timeout=300):
        """等待生成完成"""
        import time
        
        url = f"http://{server}/history/{prompt_id}"
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            history = response.json()
            
            if prompt_id in history:
                outputs = history[prompt_id].get("outputs", {})
                images = []
                
                for node_id, node_out in outputs.items():
                    if "images" in node_out:
                        for img in node_out["images"]:
                            if "filename" in img and "subfolder" in img:
                                images.append({
                                    "filename": img["filename"],
                                    "subfolder": img["subfolder"],
                                    "type": img.get("type", "output")
                                })
                
                if images:
                    return images
            
            time.sleep(2)
        
        raise TimeoutError("生成超时")
    
    def load_images_to_blender(self, images, server, character_name):
        """加载图片到 Blender"""
        blend_path = bpy.path.abspath("//")
        if not blend_path:
            blend_path = os.path.join(tempfile.gettempdir(), "ai_blender_bridge")
        output_dir = Path(blend_path) / "output" / "character_cards" / character_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for img in images:
            # 下载图片
            url = f"http://{server}/view"
            params = {
                "filename": img["filename"],
                "subfolder": img["subfolder"],
                "type": img["type"]
            }
            
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            
            # 保存图片到本地
            img_file = output_dir / img["filename"]
            with open(img_file, 'wb') as f:
                f.write(response.content)
            
            # 加载为 Blender 图像
            bpy.ops.image.open(filepath=str(img_file))
        
        print(f"🖼️ 三视图已加载到 Blender")
    
    def invoke(self, context, event):
        """弹出对话框"""
        return context.window_manager.invoke_props_dialog(self, width=300)
    
    def draw(self, context):
        """绘制对话框"""
        layout = self.layout
        layout.prop(self, "character_name", text="角色名称")


def register():
    """注册操作符"""
    bpy.utils.register_class(AIBRIDGE_OT_GenerateCharacter)
    bpy.utils.register_class(AIBRIDGE_OT_GenerateCharacterCard)


def unregister():
    """注销操作符"""
    bpy.utils.unregister_class(AIBRIDGE_OT_GenerateCharacterCard)
    bpy.utils.unregister_class(AIBRIDGE_OT_GenerateCharacter)
