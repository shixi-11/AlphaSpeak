#!/bin/bash
# 阿里云轻量服务器一键部署脚本（Nginx + HTTPS + systemd）
# 用法：
#   export BOT_TOKEN="<YOUR_BOT_TOKEN>"
#   export DOMAIN="bot.example.com"
#   export GITHUB_WEBHOOK_SECRET="<OPTIONAL_SECRET>"   # 可选
#   bash deploy-aliyun.sh

set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "❌ 请使用 root 运行此脚本"
  exit 1
fi

if [ -z "${BOT_TOKEN:-}" ] || [ -z "${DOMAIN:-}" ]; then
  echo "❌ 必须先设置 BOT_TOKEN 与 DOMAIN 环境变量"
  exit 1
fi

APP_DIR="/opt/alphaspeak"
PY_BIN="/usr/bin/python3"

echo "[1/9] 安装系统依赖..."
apt-get update -y
apt-get install -y git python3 python3-venv python3-pip nginx certbot python3-certbot-nginx

echo "[2/9] 准备代码目录..."
mkdir -p "$APP_DIR"
if [ ! -d "$APP_DIR/.git" ]; then
  echo "❌ $APP_DIR 不是 git 仓库，请先 git clone 你的仓库到该目录"
  exit 1
fi
cd "$APP_DIR"
git pull --ff-only origin main

echo "[3/9] 创建虚拟环境并安装依赖..."
$PY_BIN -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "[4/9] 写入环境变量文件..."
cat > /etc/alphaspeak.env <<ENV
BOT_TOKEN=${BOT_TOKEN}
TTS_ENABLED=false
GITHUB_WEBHOOK_SECRET=${GITHUB_WEBHOOK_SECRET:-}
ENV
chmod 600 /etc/alphaspeak.env

echo "[5/9] 配置 systemd 服务..."
cat > /etc/systemd/system/alphaspeak.service <<'UNIT'
[Unit]
Description=AlphaSpeak Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/alphaspeak
EnvironmentFile=/etc/alphaspeak.env
ExecStart=/opt/alphaspeak/venv/bin/gunicorn -w 2 -b 127.0.0.1:8080 webhook:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable alphaspeak
systemctl restart alphaspeak

echo "[6/9] 配置 Nginx..."
cat > /etc/nginx/sites-available/alphaspeak <<NGINX
server {
    listen 80;
    server_name ${DOMAIN};

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
NGINX
ln -sf /etc/nginx/sites-available/alphaspeak /etc/nginx/sites-enabled/alphaspeak
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

echo "[7/9] 申请 HTTPS 证书..."
certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "admin@${DOMAIN}" --redirect

echo "[8/9] 设置 Telegram Webhook..."
WEBHOOK_URL="https://${DOMAIN}/webhook"
curl -s "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook?url=${WEBHOOK_URL}" | tee /tmp/alphaspeak-setwebhook.json

echo "[9/9] 完成，输出状态..."
systemctl --no-pager --full status alphaspeak || true
curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo" | tee /tmp/alphaspeak-webhook-info.json

echo "✅ 部署完成：${WEBHOOK_URL}"
