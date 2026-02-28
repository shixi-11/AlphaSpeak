#!/bin/bash
# AlphaSpeak 自动部署脚本
# 使用方法：bash auto-deploy.sh

set -e

echo "========================================"
echo "  🚀 AlphaSpeak 自动部署脚本"
echo "========================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 进入应用目录
echo -e "${YELLOW}[1/6]${NC} 进入应用目录..."
cd /opt/alphaspeak || { echo -e "${RED}错误：/opt/alphaspeak 目录不存在${NC}"; exit 1; }

# 2. 拉取最新代码
echo -e "${YELLOW}[2/6]${NC} 拉取最新代码..."
git pull origin main
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 代码拉取成功${NC}"
else
    echo -e "${RED}✗ 代码拉取失败${NC}"
    exit 1
fi

# 3. 激活虚拟环境
echo -e "${YELLOW}[3/6]${NC} 激活虚拟环境..."
source venv/bin/activate

# 4. 安装依赖
echo -e "${YELLOW}[4/6]${NC} 安装依赖包..."
pip install -r requirements.txt --quiet
echo -e "${GREEN}✓ 依赖安装完成${NC}"

# 5. 更新 systemd 服务（添加 GitHub Webhook 环境变量）
echo -e "${YELLOW}[5/6]${NC} 配置 systemd 服务..."
cat > /etc/systemd/system/alphaspeak.service << EOF
[Unit]
Description=AlphaSpeak English Learning Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/alphaspeak
Environment="BOT_TOKEN=8603041416:AAHMAVuUXQ0agNns9ZJW5VjngeOzwS0IC0M"
Environment="GITHUB_WEBHOOK_SECRET=alphaspeak2026"
Environment="TTS_ENABLED=false"
ExecStart=/opt/alphaspeak/venv/bin/python webhook.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
echo -e "${GREEN}✓ systemd 配置完成${NC}"

# 6. 重启服务
echo -e "${YELLOW}[6/6]${NC} 重启服务..."
systemctl restart alphaspeak
sleep 3

# 检查服务状态
echo ""
echo -e "${YELLOW}服务状态：${NC}"
systemctl status alphaspeak --no-pager

echo ""
echo "========================================"
echo -e "${GREEN}  ✅ 部署完成！${NC}"
echo "========================================"
echo ""
echo "📱 测试机器人：在 Telegram 中发送 /start"
echo "📋 查看日志：journalctl -u alphaspeak -f"
echo "🔄 手动更新：bash /opt/alphaspeak/auto-deploy.sh"
echo ""
echo "🎉 现在 GitHub 推送代码会自动部署啦！"
echo ""
