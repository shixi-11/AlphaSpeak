#!/bin/bash
# AlphaSpeak - 美语陪练阿尔法 - 一键部署脚本
# 使用方法：bash deploy.sh

set -e

echo "========================================"
echo "🌟 AlphaSpeak 英语机器人部署"
echo "========================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置
BOT_TOKEN="${BOT_TOKEN:-8603041416:AAHMAVuUXQ0agNns9ZJW5VjngeOzwS0IC0M}"
VOICE_ENABLED="${VOICE_ENABLED:-true}"
INSTALL_DIR="/opt/alphaspeak"

echo -e "${BLUE}📋 配置信息:${NC}"
echo "  安装目录：$INSTALL_DIR"
echo "  语音功能：$VOICE_ENABLED"
echo ""

# 1. 更新系统
echo -e "${YELLOW}📦 步骤 1/7: 更新系统...${NC}"
apt update && apt upgrade -y

# 2. 安装依赖
echo -e "${YELLOW}🐍 步骤 2/7: 安装 Python 和依赖...${NC}"
apt install -y python3 python3-pip python3-venv git curl

# 3. 创建应用目录
echo -e "${YELLOW}📁 步骤 3/7: 创建应用目录...${NC}"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# 4. 克隆代码
echo -e "${YELLOW}📥 步骤 4/7: 克隆代码仓库...${NC}"
rm -rf * 2>/dev/null || true
git clone https://github.com/shixi-11/AlphaSpeak.git .

# 5. 创建虚拟环境
echo -e "${YELLOW}🔧 步骤 5/7: 创建虚拟环境...${NC}"
python3 -m venv venv
source venv/bin/activate

# 6. 安装 Python 依赖
echo -e "${YELLOW}📦 步骤 6/7: 安装 Python 依赖...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# 7. 创建 systemd 服务
echo -e "${YELLOW}⚙️ 步骤 7/7: 创建系统服务...${NC}"
cat > /etc/systemd/system/alphaspeak.service << EOF
[Unit]
Description=AlphaSpeak English Learning Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
Environment="BOT_TOKEN=$BOT_TOKEN"
Environment="VOICE_ENABLED=$VOICE_ENABLED"
ExecStart=$INSTALL_DIR/venv/bin/python bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# 启用并启动服务
echo ""
echo -e "${GREEN}🚀 启动机器人服务...${NC}"
systemctl daemon-reload
systemctl enable alphaspeak
systemctl start alphaspeak

# 等待服务启动
sleep 3

# 检查状态
echo ""
echo -e "${YELLOW}📊 服务状态：${NC}"
systemctl status alphaspeak --no-pager -l

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ 部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}📱 测试机器人：${NC}"
echo "   在 Telegram 中搜索你的机器人，发送 /start"
echo ""
echo -e "${BLUE}🔧 常用命令：${NC}"
echo "   查看日志：journalctl -u alphaspeak -f"
echo "   重启服务：systemctl restart alphaspeak"
echo "   停止服务：systemctl stop alphaspeak"
echo "   查看状态：systemctl status alphaspeak"
echo ""
echo -e "${BLUE}⚙️ 环境变量：${NC}"
echo "   BOT_TOKEN=$BOT_TOKEN"
echo "   VOICE_ENABLED=$VOICE_ENABLED"
echo ""
echo -e "${YELLOW}💡 提示：${NC}"
echo "   - 修改配置请编辑：/etc/systemd/system/alphaspeak.service"
echo "   - 代码更新：cd $INSTALL_DIR && git pull && systemctl restart alphaspeak"
echo ""
