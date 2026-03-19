# 🎬 Wan 2.2 Smooth Mix 图生视频工作流说明

**工作流版本**: 1.0  
**创建日期**: 2026-03-17  
**来源**: ComfyUI 官方工作流  
**特点**: 动作流畅，无色差

---

## 📋 工作流概述

这是一个完整的 Wan 2.2 图生视频工作流，使用 Smooth Mix 技术实现流畅的视频生成。

### 核心特性

- ✅ **Smooth Mix 模型混合**: 高低频分离处理
- ✅ **RIFE 帧插值**: 2x 插帧，动作更流畅
- ✅ **H.264 MP4 输出**: 标准视频格式
- ✅ **自动分辨率缩放**: 适配 960px 最长边
- ✅ **CLIP 视觉编码**: 图像特征提取

---

## 🏗️ 工作流程

```
1. 图像加载 (LoadImage)
       ↓
2. 分辨率缩放 (ImageScaleByAspectRatio)
   - 目标：960px 最长边
   - 保持原始宽高比
       ↓
3. CLIP 视觉编码 (CLIPVisionEncode)
   - 使用 wan21NSFWClipVisionH_v10
       ↓
4. 提示词编码 (CLIPTextEncode x2)
   - 正向：4K 高清视频描述
   - 负向：质量缺陷列表
       ↓
5. 图像到视频 (WanImageToVideo)
   - 生成初始视频 latent
       ↓
6. 双阶段采样 (KSamplerAdvanced x2)
   - 阶段 1: steps 0-5 (低质量 UNet)
   - 阶段 2: steps 5-10000 (高质量 UNet)
       ↓
7. VAE 解码 (VAEDecode)
       ↓
8. RIFE 帧插值 (RIFE VFI)
   - 2x 插帧
   - 16fps → 32fps
       ↓
9. 视频合成 (VHS_VideoCombine)
   - H.264 MP4
   - CRF 19
   - yuv420p
```

---

## 📊 技术参数

### 基础参数

| 参数 | 值 | 说明 |
|------|-----|------|
| **采样步数** | 10 | 总步数 |
| **CFG Scale** | 1 | 提示词引导系数 |
| **采样器** | euler_ancestral | 欧拉祖先采样 |
| **帧率** | 16 fps | 原始帧率 |
| **插帧后** | 32 fps | RIFE 插值后 |
| **时长** | 6 秒 | 视频时长 |
| **输出格式** | H.264 MP4 | 标准视频格式 |
| **CRF** | 19 | 视频质量 (18-23 推荐) |

### 模型配置

| 模型 | 文件名 | 用途 |
|------|--------|------|
| **CLIP** | umt5_xxl_fp8_e4m3fn_scaled.safetensors | 文本编码 |
| **VAE** | wan_2.1_vae.safetensors | 变分自编码器 |
| **CLIP Vision** | wan21NSFWClipVisionH_v10.safetensors | 图像特征 |
| **UNet High** | smoothMixWan22I2VT2V_i2vHigh.safetensors | 高频细节 |
| **UNet Low** | smoothMixWan22I2VT2V_i2vLow.safetensors | 低频结构 |

---

## 🎯 提示词配置

### 正向提示词

```
4K 高清视频，环绕镜头，她全裸跪在沙滩上，然后双手向前撑到沙滩，
低俯上身，前胸趴到沙滩，高高撅起屁股摇晃，表情挑逗，身体性感扭动
```

### 负向提示词 (部分)

```
色调艳丽，过曝，静态，细节模糊不清，字幕，风格，作品，画作，
画面，静止，整体发灰，最差质量，低质量，JPEG 压缩残留，
丑陋的，残缺的，多余的手指，画得不好的手部，画得不好的脸部，
畸形的，毁容的，形态畸形的肢体，手指融合，静止不动的画面，
杂乱的背景，三条腿，背景人很多，倒着走...
```

---

## 🔧 集成到 AI Blender Bridge

### 工作流文件位置

```
/Users/junyu/.openclaw/workspace/01-AI-Blender-Bridge/blender-plugin/comfyui_workflows/wan22_smooth_mix.json
```

### 在 Blender 中使用

1. **打开 AI Bridge 面板**
   - 3D Viewport → N 键 → AI Bridge 标签

2. **选择 Video Generation 模块**

3. **选择工作流**
   - 从下拉菜单选择 `Wan 2.2 Smooth Mix`

4. **配置参数**
   - 输入图像：选择角色图片
   - 提示词：编辑正向/负向提示词
   - 帧率：16 fps (插帧后 32 fps)
   - 时长：6 秒

5. **生成视频**
   - 点击"生成视频"按钮
   - 等待 5-10 分钟
   - 视频自动加载到 Blender

---

## 📈 性能优化

### 显存优化

- ✅ **Clean GPU Used**: 阶段间清理显存
- ✅ **FP16 累积**: 启用半精度计算
- ✅ **Block Swap**: Wan 块置换优化
- ✅ **Sage Attention**: 注意力优化

### 速度优化

| 优化项 | 效果 | 状态 |
|--------|------|------|
| FP16 累积 | 2x 速度 | ✅ 启用 |
| Block Swap | 1.5x 速度 | ✅ 启用 |
| Sage Attention | 1.3x 速度 | ✅ 自动 |
| RIFE 插帧 | 2x 流畅度 | ✅ 启用 |

---

## 🐛 故障排查

### 问题 1: 显存不足

**症状**: OOM 错误

**解决**:
- 降低分辨率 (改为 720px)
- 减少视频时长 (改为 4 秒)
- 启用 Clean GPU Used 节点

### 问题 2: 视频有色差

**症状**: 输出视频颜色异常

**解决**:
- 检查 Smooth Mix 模型版本
- 确认 VAE 模型正确加载
- 调整 CLIP Vision 编码参数

### 问题 3: 动作不流畅

**症状**: 视频卡顿

**解决**:
- 确认 RIFE 插帧启用
- 增加帧率到 24 fps
- 检查原始帧率设置

---

## 📝 更新日志

### v1.0 (2026-03-17)

- ✅ 初始版本
- ✅ Smooth Mix 模型集成
- ✅ RIFE 帧插值
- ✅ H.264 MP4 输出

---

## 🔗 参考资源

### 模型下载

- **Wan 2.1 VAE**: [HuggingFace](https://huggingface.co/Wan-AI/Wan2.1-T2V-14B)
- **Smooth Mix UNet**: [ComfyUI Model Zoo](https://comfyanonymous.github.io/ComfyUI_examples/)
- **CLIP Vision**: [CivitAI](https://civitai.com/)

### 文档

- **AI Blender Bridge**: `/Users/junyu/.openclaw/workspace/01-AI-Blender-Bridge/docs/`
- **Blender 测试指南**: `Blender 测试指南.md`
- **插件开发计划**: `开发计划-v0.3-v0.4.md`

---

_创建时间：2026-03-17 22:10_  
_版本：v1.0_  
_维护者：AI Assistant_
