# AlphaSpeak 阿里云轻量服务器部署指南

> 推荐生产方式：`webhook.py + gunicorn + nginx + HTTPS`。

## 0. 前置条件

- 你已准备好域名（例如 `bot.example.com`），并将 A 记录解析到阿里云轻量服务器公网 IP。
- 服务器系统建议 Ubuntu 22.04。
- 已将代码仓库 clone 到服务器 `/opt/alphaspeak`。

## 1. SSH 登录服务器

```bash
ssh root@<你的服务器IP>
```

## 2. 设置环境变量并执行一键脚本

在服务器执行：

```bash
cd /opt/alphaspeak
export BOT_TOKEN='<YOUR_BOT_TOKEN>'
export DOMAIN='bot.example.com'
# 可选：仅在你要启用 GitHub 自动部署 webhook 时设置
export GITHUB_WEBHOOK_SECRET='<YOUR_GITHUB_WEBHOOK_SECRET>'
# 可选：Certbot 注册邮箱（不设会默认 admin@你的主域）
export CERTBOT_EMAIL='ops@example.com'

bash deploy-aliyun.sh
```

脚本会自动完成：
- 安装 Python/nginx/certbot
- 建立 venv 并安装依赖
- 生成 systemd 服务并启动 gunicorn
- 配置 nginx 反向代理
- 申请 HTTPS 证书
- 调用 Telegram `setWebhook`

## 3. 验证部署

```bash
systemctl status alphaspeak --no-pager
curl -s https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo
```

如果 `getWebhookInfo` 返回的 `url` 是 `https://<你的域名>/webhook`，表示接入成功。

## 4. 常用运维命令

```bash
# 查看实时日志
journalctl -u alphaspeak -f

# 重启服务
systemctl restart alphaspeak

# 更新代码并重启
cd /opt/alphaspeak && git pull --ff-only origin main && systemctl restart alphaspeak
```
