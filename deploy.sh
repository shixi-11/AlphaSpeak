#!/bin/bash
# AlphaSpeak 英语机器人 - 阿里云一键部署脚本 (Polling 模式)
# 使用方法：在服务器上运行 bash deploy.sh

set -e

echo "🚀 开始部署 AlphaSpeak 英语机器人 (Polling 模式)..."
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 更新系统
echo -e "${YELLOW}📦 步骤 1/8: 更新系统...${NC}"
apt update && apt upgrade -y

# 2. 安装 Python 和依赖
echo -e "${YELLOW}🐍 步骤 2/8: 安装 Python...${NC}"
apt install -y python3 python3-pip python3-venv git curl

# 3. 创建应用目录
echo -e "${YELLOW}📁 步骤 3/8: 创建应用目录...${NC}"
mkdir -p /opt/alphaspeak
cd /opt/alphaspeak

# 4. 下载代码（从 workspace 复制或使用 GitHub）
echo -e "${YELLOW}📥 步骤 4/8: 获取代码...${NC}"
# 清理旧文件
rm -rf *

# 方法 A: 从 GitHub 克隆（推荐）
# git clone https://github.com/shixi-11/AlphaSpeak.git .
# cp bot_simple.py bot.py

# 方法 B: 直接创建文件（如果 GitHub 没有最新代码）
cat > bot.py << 'BOTCODE'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AlphaSpeak - Polling 模式"""

import os, random, logging
from datetime import datetime
from typing import Dict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8603041416:AAHMAVuUXQ0agNns9ZJW5VjngeOzwS0IC0M")

NICKNAME_OPTIONS = {
    "1": {"label": "富公", "emoji": "💰"}, "2": {"label": "富婆", "emoji": "💎"},
    "3": {"label": "小主人", "emoji": "👑"}, "4": {"label": "少主", "emoji": "🌟"},
    "5": {"label": "主公", "emoji": "⚔️"}, "6": {"label": "可爱多", "emoji": "🍦"},
    "7": {"label": "灭霸", "emoji": "🧤"},
}

VOCABULARY_DB = {
    "business": {
        "leverage": {"definition": "利用（资源、优势等）", "example": "We can leverage our existing customer base.", "etymology": "来自拉丁语 'levare' (举起)", "chinese_mnemonic": "联想：'leave' + 'rage' → 留下愤怒的力量来撬动成功！", "pronunciation": "ˈliː.vər.ɪdʒ", "story": "阿基米德：'给我一个支点，我能撬动地球'。"},
        "synergy": {"definition": "协同效应，合力", "example": "The merger created synergy between the two companies.", "etymology": "希腊语 'syn' (一起) + 'ergon' (工作)", "chinese_mnemonic": "谐音：'新能量' → 新的合作产生新能量！", "pronunciation": "ˈsɪn.ə.dʒi", "story": "synergy 就像 1+1>2 的魔法！"},
    },
    "blockchain": {
        "consensus": {"definition": "共识机制", "example": "Proof of Stake is a consensus mechanism.", "etymology": "拉丁语 'con' (一起) + 'sentire' (感觉)", "chinese_mnemonic": "谐音：'肯死死' → 肯定要死死地达成共识！", "pronunciation": "kənˈsen.səs"},
        "immutable": {"definition": "不可变的", "example": "Blockchain records are immutable.", "etymology": "拉丁语 'in' (不) + 'mutare' (改变)", "chinese_mnemonic": "联想：'一木土' → 一块木头埋在土里，永远不变！", "pronunciation": "ɪmjuː.tə.bəl"},
    },
    "web3": {
        "tokenomics": {"definition": "代币经济学", "example": "Good tokenomics is crucial for a crypto project.", "etymology": "token + economics", "chinese_mnemonic": "谐音：'偷啃我米克斯' → 偷啃我的米还要学经济！", "pronunciation": "ˌtəʊ.kəˈnɒm.ɪks"},
        "metaverse": {"definition": "元宇宙", "example": "Many companies are investing in the metaverse.", "etymology": "前缀 'meta' (超越) + 'universe' (宇宙)", "chinese_mnemonic": "联想：'妹她佛斯' → 妹妹在虚拟世界里当佛祖！", "pronunciation": "ˈmet.ə.vɜːs"},
    }
}

USER_DATA = {}

def get_user_data(user_id: int) -> Dict:
    if user_id not in USER_DATA:
        USER_DATA[user_id] = {"nickname": None, "daily_streak": 0, "total_words_learned": 0, "mastered_words": [], "achievements": []}
    return USER_DATA[user_id]

def get_nickname(user_id: int) -> str:
    user = get_user_data(user_id)
    code = user.get("nickname")
    return NICKNAME_OPTIONS[code]["label"] if code and code in NICKNAME_OPTIONS else None

def set_nickname(user_id: int, code: str):
    user = get_user_data(user_id)
    user["nickname"] = code

def generate_daily_vocabulary():
    theme = random.choice(list(VOCABULARY_DB.keys()))
    word = random.choice(list(VOCABULARY_DB[theme].keys()))
    return {"word": word, "theme": theme, "data": VOCABULARY_DB[theme][word]}

EMOJIS = ["🌟", "✨", "🎉", "😎", "💪", "🔥"]
KAOMOJI = ["(ง •̀_•́)ง", "(✧ω✧)", "(｡•̀ᴗ-)✧", "ヾ (•ω•`)o"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user_data(user_id)
    
    if user.get("nickname"):
        nickname = get_nickname(user_id)
        await update.message.reply_text(f"{random.choice(EMOJIS)} 欢迎回来，{nickname}！我是 Alpha，你的美语小伙伴~\n\n📚 输入 /daily 开始今天的学习吧！{random.choice(KAOMOJI)}")
    else:
        keyboard = [[InlineKeyboardButton(f"{info['emoji']} {info['label']}", callback_data=f"nickname_{code}")] for code, info in NICKNAME_OPTIONS.items()]
        await update.message.reply_text(f"🌟 欢迎来到 Alpha 的美语训练营！\n\n我是 Alpha，你的阳光美语小伙伴~ (✧ω✧)\n\n让我知道怎么称呼你吧！👇", reply_markup=InlineKeyboardMarkup(keyboard))

async def set_nickname_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    code = query.data.split("_")[1]
    user_id = update.effective_user.id
    set_nickname(user_id, code)
    nickname = NICKNAME_OPTIONS[code]["label"]
    emoji = NICKNAME_OPTIONS[code]["emoji"]
    await query.edit_message_text(f"{emoji} 太好啦！以后我就叫你 **{nickname}** 啦！{emoji}\n\n输入 /daily 开始学习吧！📚")

async def daily_vocabulary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user_data(user_id)
    
    if not user.get("nickname"):
        await update.message.reply_text("🤔 先选择称呼吧！输入 /start~")
        return
    
    nickname = get_nickname(user_id)
    vocab = generate_daily_vocabulary()
    word, data, theme = vocab["word"], vocab["data"], vocab["theme"]
    user["total_words_learned"] += 1
    
    await update.message.reply_text(f"""{random.choice(EMOJIS)} **{nickname}，今日词汇：{word.upper()}** {random.choice(EMOJIS)}
📍 主题：{theme.title()}

🎙️ 发音：/{data['pronunciation']}/
📝 定义：{data['definition']}
💬 例句：{data['example']}

🏛️ 词源：{data.get('story', data['etymology'])}
🧠 记忆法：{data['chinese_mnemonic']}

{random.choice(KAOMOJI)} 用这个单词造个句子吧！""")

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not get_user_data(user_id).get("nickname"):
        await update.message.reply_text("🤔 先选择称呼吧！输入 /start~")
        return
    
    vocab = generate_daily_vocabulary()
    word, data = vocab["word"], vocab["data"]
    all_words = [w for words in VOCABULARY_DB.values() for w in words.keys()]
    options = [word] + random.sample([w for w in all_words if w != word], 3)
    random.shuffle(options)
    
    keyboard = [[InlineKeyboardButton(f"{chr(65+i)}. {opt}", callback_data=f"quiz_{word}_{opt}")] for i, opt in enumerate(options)]
    nickname = get_nickname(user_id)
    await update.message.reply_text(f"🤔 {nickname}，'{data['definition']}' 对应哪个单词？", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    nickname = get_nickname(update.effective_user.id) or "小伙伴"
    
    if data.startswith("quiz_"):
        correct, selected = data.split("_")[1], data.split("_")[2]
        if selected == correct:
            await query.edit_message_text(f"✅ {nickname} 太棒了！答对了！{random.choice(KAOMOJI)}")
        else:
            await query.edit_message_text(f"❌ {nickname}，正确答案是：{correct}\n\n加油！💪")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user_data(update.effective_user.id)
    nickname = get_nickname(update.effective_user.id) or "小伙伴"
    await update.message.reply_text(f"📊 **{nickname} 的学习统计**\n📚 已学：{user['total_words_learned']} 词\n🔥 连续：{user['daily_streak']} 天\n🏆 成就：{len(user['achievements'])} 个")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nickname = get_nickname(update.effective_user.id) or "小伙伴"
    await update.message.reply_text(f"""🆘 **{nickname} 的帮助指南**

📚 学习功能：
/daily - 每日词汇
/quiz - 小测验
/stats - 学习统计
/start - 重新选择称呼

💡 学习建议：
1. 每天学习 30 分钟
2. 多用新单词造句
3. 不怕犯错，大胆说

有问题随时找 Alpha！{random.choice(KAOMOJI)}""")

def main():
    logger.info("🌟 Alpha bot is starting... (Polling Mode)")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("daily", daily_vocabulary))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CallbackQueryHandler(set_nickname_handler))
    logger.info("✅ Alpha bot initialized!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
BOTCODE

# 5. 创建虚拟环境
echo -e "${YELLOW}🔧 步骤 5/8: 创建虚拟环境...${NC}"
python3 -m venv venv
source venv/bin/activate

# 6. 安装依赖
echo -e "${YELLOW}📦 步骤 6/8: 安装依赖包...${NC}"
pip install --upgrade pip
pip install python-telegram-bot==20.7

# 7. 创建环境变量文件
echo -e "${YELLOW}⚙️ 步骤 7/8: 配置环境变量...${NC}"
cat > .env << EOF
BOT_TOKEN=8603041416:AAHMAVuUXQ0agNns9ZJW5VjngeOzwS0IC0M
EOF

# 8. 创建 systemd 服务文件
echo -e "${YELLOW}🔧 步骤 8/8: 创建系统服务...${NC}"
cat > /etc/systemd/system/alphaspeak.service << EOF
[Unit]
Description=AlphaSpeak English Learning Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/alphaspeak
Environment="BOT_TOKEN=8603041416:AAHMAVuUXQ0agNns9ZJW5VjngeOzwS0IC0M"
ExecStart=/opt/alphaspeak/venv/bin/python bot.py
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

# 检查状态
sleep 2
echo ""
echo -e "${YELLOW}📊 服务状态：${NC}"
systemctl status alphaspeak --no-pager -l

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ 部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}📱 测试机器人：${NC}"
echo "   在 Telegram 中搜索你的机器人，发送 /start"
echo ""
echo -e "${YELLOW}🔧 常用命令：${NC}"
echo "   查看日志：journalctl -u alphaspeak -f"
echo "   重启服务：systemctl restart alphaspeak"
echo "   停止服务：systemctl stop alphaspeak"
echo "   查看状态：systemctl status alphaspeak"
echo ""
echo -e "${YELLOW}⚠️  如果机器人没响应，请检查：${NC}"
echo "   1. 阿里云安全组 - 出方向允许所有（Polling 模式不需要开放端口）"
echo "   2. 服务器能访问外网：curl -I https://api.telegram.org"
echo "   3. BOT_TOKEN 是否正确"
echo ""
