#!/bin/bash
# AlphaSpeak 快速修复脚本 - 使用 ngrok 提供 HTTPS

echo "🚀 开始修复 Telegram Webhook..."

if [ -z "${BOT_TOKEN}" ]; then
  echo "❌ 请先导出 BOT_TOKEN 环境变量"
  exit 1
fi


# 1. 安装 ngrok
echo "📦 安装 ngrok..."
cd /tmp
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xzf ngrok-v3-stable-linux-amd64.tgz
mv ngrok /usr/local/bin/

# 2. 启动 ngrok（后台运行）
echo "🔌 启动 ngrok..."
nohup ngrok http 8080 --log=stdout > /var/log/ngrok.log 2>&1 &
sleep 5

# 3. 获取 ngrok URL
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')
echo "🌐 ngrok URL: $NGROK_URL"

# 4. 设置 Telegram Webhook
WEBHOOK_URL="$NGROK_URL/webhook"
echo "🔗 设置 Webhook: $WEBHOOK_URL"
curl -s "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook?url=$WEBHOOK_URL"

echo ""
echo "✅ 修复完成！"
echo "📱 在 Telegram 测试 /start 命令"
