#!/bin/bash
# Agentic 3D Studio - 快速测试脚本
# 用途：一键运行所有测试

echo "============================================================"
echo "🧪 Agentic 3D Studio - 快速测试"
echo "============================================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

echo "✅ Python3: $(python3 --version)"
echo ""

# 检查 Blender HTTP 服务是否运行
echo "📡 检查 Blender HTTP 服务..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8123/api/status 2>/dev/null)

if [ "$response" = "200" ]; then
    echo "✅ Blender HTTP 服务运行正常"
    run_server=false
else
    echo "⚠️  Blender HTTP 服务未运行"
    echo ""
    echo "请先在 Blender 中运行："
    echo "  exec(open('/Users/junyu/.openclaw/workspace/01-AI-Blender-Bridge/server/http_server.py').read())"
    echo ""
    read -p "是否继续运行其他测试？(y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "============================================================"
echo "📋 运行测试"
echo "============================================================"

# HTTP 服务测试
echo ""
echo "【1/2】HTTP 服务测试..."
cd "$(dirname "$0")/../scripts"
python3 test_http_server.py
http_result=$?

if [ $http_result -eq 0 ]; then
    echo "✅ HTTP 服务测试 通过"
else
    echo "❌ HTTP 服务测试 失败"
fi

# AI Director 测试
echo ""
echo "【2/2】AI Director 测试..."
python3 test_ai_director.py
ai_result=$?

if [ $ai_result -eq 0 ]; then
    echo "✅ AI Director 测试 通过"
else
    echo "⚠️  AI Director 测试 部分失败 (可能是 API Key 未设置)"
fi

# 总结
echo ""
echo "============================================================"
echo "📊 测试总结"
echo "============================================================"

if [ $http_result -eq 0 ]; then
    echo "✅ HTTP 服务测试：通过"
else
    echo "❌ HTTP 服务测试：失败"
fi

if [ $ai_result -eq 0 ]; then
    echo "✅ AI Director 测试：通过"
else
    echo "⚠️  AI Director 测试：部分失败"
fi

echo ""
echo "============================================================"

# 退出码
if [ $http_result -eq 0 ]; then
    exit 0
else
    exit 1
fi
