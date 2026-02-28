# AlphaSpeak 快速部署指南

## 🚨 当前状态

| 组件 | 状态 |
|------|------|
| GitHub 仓库 | ✅ 正常 |
| Bot Token | ✅ 正常 |
| Webhook | ❌ 需要 HTTPS |

## 🔧 修复步骤（3 步）

### 步骤 1：SSH 登录阿里云

```bash
ssh root@47.236.42.143
```

### 步骤 2：更新代码

```bash
cd /opt/alphaspeak
git pull origin main
```

### 步骤 3：设置 HTTPS（2 选 1）

#### 方案 A：使用 ngrok（最快）

```bash
# 安装 ngrok
cd /tmp
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xzf ngrok-v3-stable-linux-amd64.tgz
mv ngrok /usr/local/bin/

# 启动 ngrok
nohup ngrok http 8080 > /var/log/ngrok.log 2>&1 &
sleep 3

# 获取 HTTPS URL
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')

# 设置 Webhook
curl -s "https://api.telegram.org/bot8603041416:AAHMAVuUXQ0agNns9ZJW5VjngeOzwS0IC0M/setWebhook?url=$NGROK_URL/webhook"
```

#### 方案 B：使用阿里云 SSL（正式）

需要配置 Nginx + SSL 证书。

## ✅ 验证

在浏览器访问：
```
https://api.telegram.org/bot8603041416:AAHMAVuUXQ0agNns9ZJW5VjngeOzwS0IC0M/getWebhookInfo
```

看到 `"url": "https://..."` 即成功！

## 📱 测试

在 Telegram 发送 `/start`，应该看到称呼选择按钮！