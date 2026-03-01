# AlphaSpeak - 美语陪练阿尔法 🌟

你的阳光美语小伙伴，专注商务/区块链/Web3 词汇学习！

## 特点

- 🎯 CET-4 级别，商务/区块链/Web3 主题词汇
- 🏛️ 词源故事解析，理解单词背后的历史
- 🧠 中文谐音记忆法，轻松记单词
- 😄 幽默互动风格，学习不枯燥
- 👤 自定义称呼，更亲切的学习体验

## 命令列表

| 命令 | 说明 |
|------|------|
| `/start` | 开始使用，选择称呼 |
| `/daily` | 获取今日词汇练习 |
| `/quiz` | 单词小测验 |
| `/stats` | 查看学习统计 |
| `/help` | 帮助指南 |

## 部署到阿里云服务器

### 一键部署（推荐）

```bash
# 下载部署脚本
wget https://raw.githubusercontent.com/shixi-11/AlphaSpeak/main/deploy.sh

# 运行部署
bash deploy.sh
```

### 手动部署

```bash
# 1. 安装依赖
apt update && apt install -y python3 python3-pip python3-venv

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装 Python 包
pip install -r requirements.txt

# 4. 设置环境变量
export BOT_TOKEN="你的 BOT_TOKEN"

1. 连接 GitHub 仓库
2. 设置环境变量：
   - `BOT_TOKEN` - Telegram Bot API Token
   - `TTS_ENABLED` - 是否启用语音 (true/false)
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn webhook:app --bind 0.0.0.0:$PORT`

### 阿里云轻量服务器（推荐）

```bash
ssh root@your-server-ip
cd /opt/alphaspeak
export BOT_TOKEN=<YOUR_BOT_TOKEN>
export DOMAIN=bot.example.com
export CERTBOT_EMAIL=ops@example.com  # 可选
bash deploy-aliyun.sh
```

冲突处理（当 PR 显示 conflicts）：

```bash
bash sync-main.sh origin main
```

## 获取 Bot Token

1. 在 Telegram 搜索 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 创建新机器人
3. 按照提示设置用户名
4. 复制得到的 token，替换 `BOT_TOKEN`

## 技术栈

- Python 3.8+
- python-telegram-bot v20.7
- Polling 模式（无需 webhook）

## 许可证

MIT License

---

**Made with ❤️ by Alpha**
