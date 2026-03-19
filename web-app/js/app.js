// Agentic 3D Studio - Web Application
// 版本：v1.0.0-Agentic

// ==================== 全局状态 ====================

let blenderConnected = false;
let blenderURL = 'http://localhost:8123';
let selectedObject = null;
let agentRunning = false;
let agentLoopController = null;

// ==================== 工具函数 ====================

function log(message, type = 'info') {
    const logContainer = document.getElementById('agent-log');
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    logContainer.appendChild(entry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

function clearLog() {
    const logContainer = document.getElementById('agent-log');
    logContainer.innerHTML = '';
}

function updateStatus(connected) {
    blenderConnected = connected;
    const statusDot = document.getElementById('connection-status');
    const statusText = document.getElementById('connection-text');
    
    if (connected) {
        statusDot.className = 'status-dot connected';
        statusText.textContent = 'Connected to Blender';
    } else {
        statusDot.className = 'status-dot disconnected';
        statusText.textContent = 'Disconnected';
    }
}

async function apiRequest(endpoint, method = 'GET', data = null) {
    const url = `${blenderURL}${endpoint}`;
    
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || `HTTP ${response.status}`);
        }
        
        return result;
    } catch (error) {
        console.error(`API Error (${endpoint}):`, error);
        throw error;
    }
}

// ==================== Tab 切换 ====================

function switchTab(tabName, btn) {
    // 隐藏所有 Tab
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // 取消所有按钮激活状态
    document.querySelectorAll('.tab-btn').forEach(b => {
        b.classList.remove('active');
    });

    // 激活选中的 Tab
    document.getElementById(`tab-${tabName}`).classList.add('active');
    btn.classList.add('active');
}

// ==================== Tab 1: Connection ====================

async function testConnection() {
    const urlInput = document.getElementById('blender-url');
    blenderURL = urlInput.value.trim();
    
    log(`Testing connection to ${blenderURL}...`);
    
    try {
        const result = await apiRequest('/api/status');
        
        if (result.success) {
            updateStatus(true);
            log(`✅ Connected to Blender ${result.blender_version}`, 'success');
            log(`   Scene: ${result.scene}, Objects: ${result.object_count}`);
        } else {
            updateStatus(false);
            log('❌ Connection failed', 'error');
        }
    } catch (error) {
        updateStatus(false);
        log(`❌ Connection error: ${error.message}`, 'error');
    }
}

function getInstallScript() {
    return `# Blender HTTP Server Installer
# 复制此脚本并在 Blender Scripting 标签页中运行

import bpy
import sys
import os

# 添加 server 目录到 Python 路径
# ⚠️ 请将下面的路径修改为你本地 server 目录的实际路径
server_path = r"E:\\Project\\Code\\01-AI-Blender-Bridge\\server"
if server_path not in sys.path:
    sys.path.insert(0, server_path)

# 导入并启动 HTTP 服务
exec(open(os.path.join(server_path, "http_server.py")).read())

print("✅ HTTP Server started on :8123")
`;
}

function copyInstallScript() {
    const script = getInstallScript();
    navigator.clipboard.writeText(script).then(() => {
        alert('✅ Installation script copied to clipboard!');
    }).catch(err => {
        console.error('Copy failed:', err);
        alert('❌ Failed to copy. Please copy manually.');
    });
}

// 页面加载时获取安装脚本
document.addEventListener('DOMContentLoaded', () => {
    const scriptElement = document.getElementById('install-script');
    if (scriptElement) {
        scriptElement.textContent = getInstallScript();
    }
});

// ==================== Tab 2: Scene Manager ====================

async function refreshObjects() {
    if (!blenderConnected) {
        alert('❌ Please connect to Blender first');
        return;
    }
    
    try {
        const result = await apiRequest('/api/scene/objects');
        displayObjects(result.objects);
        log(`📦 Loaded ${result.objects.length} objects`, 'success');
    } catch (error) {
        log(`❌ Failed to load objects: ${error.message}`, 'error');
    }
}

function displayObjects(objects) {
    const listContainer = document.getElementById('object-list');
    listContainer.innerHTML = '';
    
    if (objects.length === 0) {
        listContainer.innerHTML = '<p style="color: rgba(255,255,255,0.5);">No objects in scene</p>';
        return;
    }
    
    objects.forEach(obj => {
        const item = document.createElement('div');
        item.className = 'object-item';
        item.innerHTML = `
            <div class="object-name">${obj.name} <span class="badge">${obj.type}</span></div>
            <div class="object-transform">
                Pos: [${obj.location.map(v => v.toFixed(2)).join(', ')}] |
                Rot: [${obj.rotation.map(v => v.toFixed(2)).join(', ')}] |
                Scale: [${obj.scale.map(v => v.toFixed(2)).join(', ')}]
            </div>
        `;
        
        item.onclick = () => selectObject(obj, item);
        listContainer.appendChild(item);
    });
}

function selectObject(obj, element) {
    // 移除之前的选中状态
    document.querySelectorAll('.object-item').forEach(item => {
        item.classList.remove('selected');
    });
    
    // 添加新的选中状态
    element.classList.add('selected');
    selectedObject = obj;
    
    // 显示 Transform 面板
    const panel = document.getElementById('transform-panel');
    panel.style.display = 'block';
    
    // 填充当前值
    document.getElementById('selected-object').value = obj.name;
    document.getElementById('loc-x').value = obj.location[0].toFixed(3);
    document.getElementById('loc-y').value = obj.location[1].toFixed(3);
    document.getElementById('loc-z').value = obj.location[2].toFixed(3);
    document.getElementById('rot-x').value = obj.rotation[0].toFixed(3);
    document.getElementById('rot-y').value = obj.rotation[1].toFixed(3);
    document.getElementById('rot-z').value = obj.rotation[2].toFixed(3);
    document.getElementById('scale-x').value = obj.scale[0].toFixed(3);
    document.getElementById('scale-y').value = obj.scale[1].toFixed(3);
    document.getElementById('scale-z').value = obj.scale[2].toFixed(3);
}

async function applyTransform() {
    if (!selectedObject) {
        alert('❌ Please select an object first');
        return;
    }
    
    const data = {
        location: [
            parseFloat(document.getElementById('loc-x').value),
            parseFloat(document.getElementById('loc-y').value),
            parseFloat(document.getElementById('loc-z').value)
        ],
        rotation: [
            parseFloat(document.getElementById('rot-x').value),
            parseFloat(document.getElementById('rot-y').value),
            parseFloat(document.getElementById('rot-z').value)
        ],
        scale: [
            parseFloat(document.getElementById('scale-x').value),
            parseFloat(document.getElementById('scale-y').value),
            parseFloat(document.getElementById('scale-z').value)
        ]
    };
    
    try {
        const result = await apiRequest(`/api/object/${selectedObject.name}`, 'PUT', data);
        
        if (result.success) {
            log(`✅ Applied transform to ${selectedObject.name}`, 'success');
            refreshObjects();
        } else {
            log(`❌ Failed: ${result.message}`, 'error');
        }
    } catch (error) {
        log(`❌ Error: ${error.message}`, 'error');
    }
}

async function importGLB() {
    const pathInput = document.getElementById('import-path');
    const filepath = pathInput.value.trim();
    
    if (!filepath) {
        alert('❌ Please enter a file path');
        return;
    }
    
    try {
        const result = await apiRequest('/api/scene/import', 'POST', { filepath });
        
        if (result.success) {
            log(`✅ Imported ${result.message} objects`, 'success');
            result.objects.forEach(name => {
                log(`   📦 ${name}`);
            });
            refreshObjects();
        } else {
            log(`❌ Import failed: ${result.error}`, 'error');
        }
    } catch (error) {
        log(`❌ Error: ${error.message}`, 'error');
    }
}

async function clearScene() {
    if (!confirm('⚠️ Are you sure you want to clear the scene? This will delete all objects except cameras and lights.')) {
        return;
    }
    
    try {
        const result = await apiRequest('/api/scene/clear', 'POST');
        
        if (result.success) {
            log('🗑️ Scene cleared', 'success');
            refreshObjects();
        } else {
            log(`❌ Failed: ${result.error}`, 'error');
        }
    } catch (error) {
        log(`❌ Error: ${error.message}`, 'error');
    }
}

async function liveRender() {
    try {
        log('📸 Rendering...');
        
        const result = await apiRequest('/api/render', 'POST', {
            width: 1920,
            height: 1080
        });
        
        if (result.success) {
            const preview = document.getElementById('render-preview');
            preview.innerHTML = `<img src="data:image/png;base64,${result.render.image_base64}" alt="Render">`;
            log('✅ Render complete', 'success');
        } else {
            log(`❌ Render failed: ${result.error}`, 'error');
        }
    } catch (error) {
        log(`❌ Error: ${error.message}`, 'error');
    }
}

// ==================== Tab 3: AI Director ====================

async function startAgentLoop() {
    const apiKey = document.getElementById('api-key').value.trim();
    const provider = document.getElementById('ai-provider').value;
    const goal = document.getElementById('ai-goal').value.trim();
    const maxIterations = parseInt(document.getElementById('max-iterations').value);
    
    if (!apiKey) {
        alert('❌ Please enter your API key');
        return;
    }
    
    if (!goal) {
        alert('❌ Please enter a goal');
        return;
    }
    
    if (!blenderConnected) {
        alert('❌ Please connect to Blender first');
        return;
    }
    
    // 更新 UI
    agentRunning = true;
    document.getElementById('start-agent-btn').style.display = 'none';
    document.getElementById('stop-agent-btn').style.display = 'inline-flex';
    clearLog();
    
    log(`🚀 Starting Agent Loop...`);
    log(`   Goal: ${goal}`);
    log(`   Max iterations: ${maxIterations}`);
    log(`   Provider: ${provider}`);
    
    // 启动 Agent 循环
    runAgentLoop(apiKey, provider, goal, maxIterations);
}

function stopAgentLoop() {
    agentRunning = false;
    document.getElementById('start-agent-btn').style.display = 'inline-flex';
    document.getElementById('stop-agent-btn').style.display = 'none';
    log('⏹️ Agent Loop stopped by user');
}

async function runAgentLoop(apiKey, provider, goal, maxIterations) {
    for (let iteration = 1; iteration <= maxIterations && agentRunning; iteration++) {
        // 更新进度
        const progress = (iteration / maxIterations) * 100;
        document.getElementById('agent-progress').style.width = `${progress}%`;
        document.getElementById('agent-status-text').textContent = `Iteration ${iteration}/${maxIterations}`;
        
        log(`\n${'='.repeat(60)}`);
        log(`📍 Iteration ${iteration}/${maxIterations}`);
        log(`${'='.repeat(60)}`);
        
        try {
            // Step 1: 渲染场景
            log('📸 Rendering scene...');
            const renderResult = await apiRequest('/api/render', 'POST', { width: 1920, height: 1080 });
            
            if (!renderResult.success) {
                throw new Error(`Render failed: ${renderResult.error}`);
            }
            
            // Step 2: 获取物体列表
            log('📦 Getting objects...');
            const objectsResult = await apiRequest('/api/scene/objects');
            
            if (!objectsResult.success) {
                throw new Error(`Get objects failed: ${objectsResult.error}`);
            }
            
            // Step 3: AI 分析
            log('🧠 AI analyzing...');
            const aiResult = await callAI(apiKey, provider, renderResult.render.image_base64, objectsResult.objects, goal);
            
            if (!aiResult.success) {
                throw new Error(`AI analysis failed: ${aiResult.error}`);
            }
            
            const aiResponse = aiResult.response;
            
            // 显示 AI 分析
            log(`📝 AI Analysis: ${aiResponse.analysis || 'N/A'}`);
            log(`   Goal achieved: ${aiResponse.goal_achieved || false}`);
            log(`   Confidence: ${(aiResponse.confidence || 0).toFixed(2)}`);
            
            // 检查目标是否达成
            if (aiResponse.goal_achieved) {
                log(`\n✅ Goal achieved!`, 'success');
                break;
            }
            
            // Step 4: 执行命令
            const commands = aiResponse.commands || [];
            
            if (commands.length > 0) {
                log(`\n🔧 Executing ${commands.length} commands...`);
                
                for (const cmd of commands) {
                    const success = await executeCommand(cmd);
                    if (success) {
                        log(`   ✅ ${cmd.object}: ${cmd.action}`, 'success');
                    } else {
                        log(`   ❌ Failed: ${JSON.stringify(cmd)}`, 'error');
                    }
                }
            } else {
                log(`\n⚠️ No commands to execute`);
            }
            
        } catch (error) {
            log(`❌ Iteration ${iteration} failed: ${error.message}`, 'error');
            
            // 遇到严重错误时停止
            if (error.message.includes('Connection') || error.message.includes('Network')) {
                log('⚠️ Stopping due to connection error', 'error');
                break;
            }
        }
        
        // 短暂延迟
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    // 完成
    log(`\n${'='.repeat(60)}`);
    log(`🏁 Agent Loop finished`);
    log(`${'='.repeat(60)}`);
    
    // 重置 UI
    agentRunning = false;
    document.getElementById('start-agent-btn').style.display = 'inline-flex';
    document.getElementById('stop-agent-btn').style.display = 'none';
    document.getElementById('agent-progress').style.width = '0%';
    document.getElementById('agent-status-text').textContent = 'Idle';
}

async function callAI(apiKey, provider, imageBase64, objects, goal) {
    // 构建物体信息文本
    const objectsText = objects.map(obj => 
        `- ${obj.name}: location=${JSON.stringify(obj.location)}, rotation=${JSON.stringify(obj.rotation)}, scale=${JSON.stringify(obj.scale)}`
    ).join('\n');
    
    // 系统提示词
    const systemPrompt = `You are an expert 3D spatial reasoning AI assistant. Your task is to analyze rendered images of a 3D scene and provide precise transform commands to achieve a user-specified goal.

Blender coordinate system: +X right, +Y forward, +Z up
Rotations are in Euler angles (radians), order XYZ
Scale is relative (1.0 = original size)

Output ONLY valid JSON with this structure:
{
  "analysis": "Brief analysis",
  "goal_understood": "Restated goal",
  "commands": [{"object": "name", "action": "move|rotate|scale", "location/rotation/scale": [...], "reason": "..."}],
  "goal_achieved": true|false,
  "confidence": 0.0-1.0,
  "next_step": "What to do next"
}`;
    
    // 用户提示词
    const userPrompt = `${objectsText}

User Goal: ${goal}

Please analyze the image and provide transform commands to achieve the goal.
Output ONLY valid JSON, no markdown or additional text.`;
    
    // 调用 API
    if (provider === 'gemini') {
        return await callGemini(apiKey, imageBase64, systemPrompt, userPrompt);
    } else {
        return await callQwenVL(apiKey, imageBase64, systemPrompt, userPrompt);
    }
}

/**
 * 从 AI 响应文本中提取 JSON（处理 markdown 包裹和各种格式）
 */
function extractJSON(content) {
    // 如果 content 是数组（Qwen-VL 可能返回 list），提取文本
    if (Array.isArray(content)) {
        content = content.map(item => {
            if (typeof item === 'string') return item;
            if (item && item.text) return item.text;
            return '';
        }).join('\n');
    }

    content = content.trim();

    // 去除 markdown 代码块
    if (content.includes('```json')) {
        const start = content.indexOf('```json') + 7;
        const end = content.indexOf('```', start);
        content = content.substring(start, end !== -1 ? end : undefined);
    } else if (content.includes('```')) {
        const start = content.indexOf('```') + 3;
        const end = content.indexOf('```', start);
        content = content.substring(start, end !== -1 ? end : undefined);
    }

    return JSON.parse(content.trim());
}

async function callGemini(apiKey, imageBase64, systemPrompt, userPrompt) {
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-04-17:generateContent?key=${apiKey}`;

    const requestBody = {
        contents: [{
            parts: [
                { text: systemPrompt },
                { text: userPrompt },
                {
                    inline_data: {
                        mime_type: 'image/png',
                        data: imageBase64
                    }
                }
            ]
        }],
        generationConfig: {
            temperature: 0.2,
            topP: 0.8,
            topK: 40,
            maxOutputTokens: 2048
        }
    };

    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
        const errText = await response.text();
        return { success: false, error: `Gemini API error ${response.status}: ${errText}` };
    }

    const result = await response.json();

    if (result.candidates && result.candidates.length > 0) {
        try {
            const content = result.candidates[0].content.parts[0].text;
            const aiResponse = extractJSON(content);
            return { success: true, response: aiResponse };
        } catch (e) {
            return { success: false, error: `JSON parse error: ${e.message}` };
        }
    } else {
        return { success: false, error: 'No response from AI' };
    }
}

async function callQwenVL(apiKey, imageBase64, systemPrompt, userPrompt) {
    const url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation';

    const requestBody = {
        model: 'qwen-vl-max',
        input: {
            messages: [
                { role: 'system', content: systemPrompt },
                {
                    role: 'user',
                    content: [
                        { image: `data:image/png;base64,${imageBase64}` },
                        { text: userPrompt }
                    ]
                }
            ]
        },
        parameters: {
            temperature: 0.2,
            top_p: 0.8,
            max_tokens: 2048
        }
    };

    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
        const errText = await response.text();
        return { success: false, error: `Qwen-VL API error ${response.status}: ${errText}` };
    }

    const result = await response.json();

    if (result.output && result.output.choices && result.output.choices.length > 0) {
        try {
            const content = result.output.choices[0].message.content;
            const aiResponse = extractJSON(content);
            return { success: true, response: aiResponse };
        } catch (e) {
            return { success: false, error: `JSON parse error: ${e.message}` };
        }
    } else {
        return { success: false, error: 'No response from AI' };
    }
}

async function executeCommand(cmd) {
    try {
        const objName = cmd.object;
        const action = cmd.action;

        const data = {};

        if (action === 'move' && cmd.location) {
            data.location = cmd.location;
        } else if (action === 'rotate' && cmd.rotation) {
            data.rotation = cmd.rotation;
        } else if (action === 'scale' && cmd.scale) {
            data.scale = cmd.scale;
        }

        if (Object.keys(data).length === 0) {
            return false;
        }

        const result = await apiRequest(`/api/object/${encodeURIComponent(objName)}`, 'PUT', data);
        return result.success;
    } catch (error) {
        console.error('executeCommand error:', error);
        return false;
    }
}

// ==================== 页面加载 ====================

document.addEventListener('DOMContentLoaded', () => {
    log('🎬 Agentic 3D Studio loaded');
    log('📝 Please connect to Blender first');
});
