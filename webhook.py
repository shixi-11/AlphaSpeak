#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌟 AlphaSpeak - 美语陪练阿尔法 🌟
带称呼选择功能的版本
"""

import os
import json
import random
import logging
import asyncio
import subprocess
import hashlib
import hmac
from datetime import datetime
from typing import Dict, List

from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 机器人配置
BOT_TOKEN = os.getenv("BOT_TOKEN")
TTS_ENABLED = os.getenv("TTS_ENABLED", "true").lower() == "true"
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")

# Flask 应用
app = Flask(__name__)

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is required")

if not GITHUB_WEBHOOK_SECRET:
    raise RuntimeError("GITHUB_WEBHOOK_SECRET environment variable is required")


# ============= 🎨 Alpha 人设配置 =============
ALPHA_PERSONA = {
    "name": "Alpha",
    "title": "你的美语小伙伴",
    "personality": "阳光开朗的美语少年，像邻居家的大哥哥",
    "emojis": ["🌟", "✨", "🎉", "😎", "💪", "🔥", "📚", "🎤", "💫", "🚀"],
    "kaomoji": ["(ง •̀_•́)ง", "(✧ω✧)", "(｡•̀ᴗ-)✧", "ヾ (•ω•`)o", "٩ (๑>◡<๑)۶"],
}

# ============= 👑 称呼选项配置 =============
NICKNAME_OPTIONS = {
    "1": {"label": "富公", "emoji": "💰"},
    "2": {"label": "富婆", "emoji": "💎"},
    "3": {"label": "小主人", "emoji": "👑"},
    "4": {"label": "少主", "emoji": "🌟"},
    "5": {"label": "主公", "emoji": "⚔️"},
    "6": {"label": "可爱多", "emoji": "🍦"},
    "7": {"label": "灭霸", "emoji": "🧤"},
}

# ============= 🎭 多样化开场白 =============
GREETINGS = [
    "哟！你来啦！我是你的美语小伙伴 Alpha！🎉 今天也是和我一起征服英语的一天呢~",
    "早啊小懒虫！☀️ Alpha 已经等你好久啦！准备好被英语轰炸了吗😎",
    "哈喽哈喽！(✧ω✧) 今天想学点什么？商务、区块链还是 Web3？",
    "嘿！我的学习搭档！💪 今天也是元气满满的一天呢~",
    "哇！见到你真开心！ヾ (•ω•`)o 今天我们来学点酷酷的单词吧！",
    "哟吼！Alpha 的美语小课堂开课啦！🎤 今天也要加油哦！",
    "Hello hello~ 你的专属美语教练 Alpha 已上线！✨ 准备好了吗？",
    "噔噔噔~ Alpha 闪亮登场！今天也要一起学习进步哦！",
]

# ============= 📚 词汇库 =============
VOCABULARY_DB = {
    "business": {
        "leverage": {
            "definition": "利用（资源、优势等）",
            "example": "We can leverage our existing customer base to launch new products.",
            "etymology": "来自拉丁语 'levare' (举起)，原意是用杠杆撬动重物",
            "chinese_mnemonic": "联想：'leave' + 'rage' → 留下愤怒的力量来撬动成功！",
            "pronunciation": "ˈliː.vər.ɪdʒ",
            "story": "想象一下，阿基米德说过'给我一个支点，我能撬动地球'。leverage 就是这个'撬动'的力量！",
        },
        "synergy": {
            "definition": "协同效应，合力",
            "example": "The merger created synergy between the two companies.",
            "etymology": "希腊语 'syn' (一起) + 'ergon' (工作)",
            "chinese_mnemonic": "谐音：'新能量' → 新的合作产生新能量！",
            "pronunciation": "ˈsɪn.ə.dʒi",
            "story": "synergy 就像 1+1>2 的魔法！两个人合作，产生的效果比各自为战强很多。",
        },
    },
    "blockchain": {
        "consensus": {
            "definition": "共识机制",
            "example": "Proof of Stake is a consensus mechanism used by many blockchains.",
            "etymology": "拉丁语 'con' (一起) + 'sentire' (感觉)",
            "chinese_mnemonic": "谐音：'肯死死' → 肯定要死死地达成共识！",
            "pronunciation": "kənˈsen.səs",
        },
        "immutable": {
            "definition": "不可变的",
            "example": "Blockchain records are immutable once added to the chain.",
            "etymology": "拉丁语 'in' (不) + 'mutare' (改变)",
            "chinese_mnemonic": "联想：'一木土' → 一块木头埋在土里，永远不变！",
            "pronunciation": "ɪmjuː.tə.bəl",
        },
    },
    "web3": {
        "tokenomics": {
            "definition": "代币经济学",
            "example": "Good tokenomics is crucial for a successful crypto project.",
            "etymology": "token + economics",
            "chinese_mnemonic": "谐音：'偷啃我米克斯' → 偷啃我的米 (代币) 还要学经济！",
            "pronunciation": "ˌtəʊ.kəˈnɒm.ɪks",
        },
        "metaverse": {
            "definition": "元宇宙",
            "example": "Many companies are investing in the metaverse.",
            "etymology": "前缀 'meta' (超越) + 'universe' (宇宙)",
            "chinese_mnemonic": "联想：'妹她佛斯' → 妹妹在虚拟世界里当佛祖！",
            "pronunciation": "ˈmet.ə.vɜːs",
        },
    }
}

# ============= 💾 用户数据 =============
USER_DATA = {}

def get_user_data(user_id: int) -> Dict:
    if user_id not in USER_DATA:
        USER_DATA[user_id] = {
            "nickname": None,  # 用户选择的称呼
            "level": "CET-4",
            "daily_streak": 0,
            "last_practice": None,
            "total_words_learned": 0,
            "mastered_words": [],
            "weak_words": [],
            "achievements": [],
        }
    return USER_DATA[user_id]

def save_user_data(user_id: int, data: Dict):
    USER_DATA[user_id] = data

def get_nickname(user_id: int) -> str:
    """获取用户称呼"""
    user = get_user_data(user_id)
    nickname_code = user.get("nickname")
    if nickname_code and nickname_code in NICKNAME_OPTIONS:
        return NICKNAME_OPTIONS[nickname_code]["label"]
    return None

def set_nickname(user_id: int, nickname_code: str):
    """设置用户称呼"""
    user = get_user_data(user_id)
    user["nickname"] = nickname_code
    save_user_data(user_id, user)

def generate_daily_vocabulary():
    themes = list(VOCABULARY_DB.keys())
    theme = random.choice(themes)
    words = list(VOCABULARY_DB[theme].keys())
    word = random.choice(words)
    return {"word": word, "theme": theme, "data": VOCABULARY_DB[theme][word]}

def get_random_greeting():
    return random.choice(GREETINGS)

def get_random_emoji():
    return random.choice(ALPHA_PERSONA["emojis"])

def get_random_kaomoji():
    return random.choice(ALPHA_PERSONA["kaomoji"])

# ============= 🤖 命令处理 =============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令 - 显示称呼选择"""
    user_id = update.effective_user.id
    user = get_user_data(user_id)
    
    # 检查是否已经设置过称呼
    if user.get("nickname"):
        # 已设置，显示正常欢迎消息
        nickname = get_nickname(user_id)
        greeting = get_random_greeting()
        
        message = f"""
{greeting}

🎯 **关于 Alpha**：
我是你的美语小伙伴 Alpha，一个阳光开朗的美语少年~

📚 **可用命令**：
/daily - 每日词汇练习 📖
/quiz - 单词小测验 🎯
/streak - 连续学习天数 🔥
/stats - 学习数据统计 📊
/nickname - 修改称呼 👤
/help - 帮助指南 ❓

准备好了吗？输入 /daily 开始今天的英语冒险吧！{get_random_kaomoji()}
        """
        await update.message.reply_text(message)
    else:
        # 未设置，显示称呼选择
        keyboard = []
        for code, info in NICKNAME_OPTIONS.items():
            keyboard.append([InlineKeyboardButton(f"{info['emoji']} {info['label']}", callback_data=f"nickname_{code}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_message = f"""
🌟 欢迎来到 Alpha 的美语训练营！🌟

我是 Alpha，你的阳光美语小伙伴~ (✧ω✧)

在开始学习之前，让我知道怎么称呼你吧！
选一个你喜欢的称呼，以后我就这么叫你啦~ 💕

👇 **请选择你喜欢的称呼** 👇
        """
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def set_nickname_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理称呼选择回调"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data.startswith("nickname_"):
        nickname_code = data.split("_")[1]
        user_id = update.effective_user.id
        
        if nickname_code in NICKNAME_OPTIONS:
            set_nickname(user_id, nickname_code)
            nickname = NICKNAME_OPTIONS[nickname_code]["label"]
            emoji = NICKNAME_OPTIONS[nickname_code]["emoji"]
            
            success_message = f"""
{emoji} 太好啦！以后我就叫你 **{nickname}** 啦！{emoji}

从现在开始，你就是我的专属 {nickname} 了~ (✧ω✧)

准备好开始今天的英语学习了吗？
输入 /daily 获取今日词汇吧！📚

或者输入 /help 查看所有功能哦~
            """
            await query.edit_message_text(success_message)

async def nickname_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /nickname 命令 - 重新选择称呼"""
    user_id = update.effective_user.id
    
    keyboard = []
    for code, info in NICKNAME_OPTIONS.items():
        keyboard.append([InlineKeyboardButton(f"{info['emoji']} {info['label']}", callback_data=f"nickname_{code}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    current_nickname = get_nickname(user_id)
    message = f"""
👤 **修改称呼**

{get_random_emoji()} 当前称呼：{current_nickname if current_nickname else '未设置'}

请选择一个新的称呼吧~
    """
    
    await update.message.reply_text(message, reply_markup=reply_markup)

async def daily_vocabulary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /daily 命令 - 每日词汇练习"""
    user_id = update.effective_user.id
    user = get_user_data(user_id)
    
    # 检查是否设置称呼
    if not user.get("nickname"):
        await update.message.reply_text("🤔 先选择一个称呼吧！输入 /start 开始~")
        return
    
    nickname = get_nickname(user_id)
    
    vocab = generate_daily_vocabulary()
    word = vocab["word"]
    data = vocab["data"]
    theme = vocab["theme"]
    
    user["total_words_learned"] += 1
    if word not in user["mastered_words"]:
        user["mastered_words"].append(word)
    
    message = f"""
{get_random_emoji()} **{nickname}，今日词汇：{word.upper()}** {get_random_emoji()}
📍 **主题**：{theme.title()}

🎙️ *【Alpha 发音】: /{data['pronunciation']}/*

📝 **定义**：{data['definition']}
💬 **例句**：{data['example']}

🏛️ **词源故事**：
{data.get('story', data['etymology'])}

🧠 **中文记忆法**：
{data['chinese_mnemonic']}

🎯 **小挑战**：用这个单词造个句子吧！{get_random_kaomoji()}
    """
    await update.message.reply_text(message)

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /quiz 命令 - 小测验"""
    user_id = update.effective_user.id
    user = get_user_data(user_id)
    
    if not user.get("nickname"):
        await update.message.reply_text("🤔 先选择一个称呼吧！输入 /start 开始~")
        return
    
    vocab = generate_daily_vocabulary()
    word = vocab["word"]
    data = vocab["data"]
    
    all_words = []
    for theme_words in VOCABULARY_DB.values():
        all_words.extend(list(theme_words.keys()))
    
    wrong_options = random.sample([w for w in all_words if w != word], 3)
    options = [word] + wrong_options
    random.shuffle(options)
    
    keyboard = []
    for i, option in enumerate(options):
        keyboard.append([InlineKeyboardButton(f"{chr(65+i)}. {option}", callback_data=f"quiz_{word}_{option}")])
    
    nickname = get_nickname(user_id)
    await update.message.reply_text(f"🤔 {nickname}，'{data['definition']}' 对应哪个单词？", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理按钮回调"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    nickname = get_nickname(user_id)
    
    if data.startswith("quiz_"):
        parts = data.split("_")
        correct = parts[1]
        selected = parts[2]
        
        if selected == correct:
            await query.edit_message_text(f"✅ {nickname} 太棒了！答对了！{get_random_kaomoji()}")
        else:
            await query.edit_message_text(f"❌ {nickname}，正确答案是：{correct}\n\n加油！💪")

async def streak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /streak 命令"""
    user = get_user_data(update.effective_user.id)
    nickname = get_nickname(update.effective_user.id) or "小伙伴"
    await update.message.reply_text(f"🔥 **{nickname}，连续学习**：{user['daily_streak']} 天\n\n继续加油！{get_random_kaomoji()}")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /stats 命令"""
    user = get_user_data(update.effective_user.id)
    nickname = get_nickname(update.effective_user.id) or "小伙伴"
    await update.message.reply_text(f"""
📊 **{nickname} 的学习统计**
📚 已学：{user['total_words_learned']} 词
🔥 连续：{user['daily_streak']} 天
🏆 成就：{len(user['achievements'])} 个
    """)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /help 命令"""
    nickname = get_nickname(update.effective_user.id) or "小伙伴"
    await update.message.reply_text(f"""
🆘 **{nickname} 的帮助指南**

**📚 学习功能**：
/daily - 每日词汇
/quiz - 小测验
/streak - 连续天数
/stats - 学习统计
/nickname - 修改称呼

**💡 学习建议**：
1. 每天学习 30 分钟
2. 多用新单词造句
3. 不怕犯错，大胆说

有任何问题随时找 Alpha！{get_random_kaomoji()}
    """)

# ============= 🌐 Webhook 处理 =============

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    """Telegram Webhook"""
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        asyncio.run(application.process_update(update))
        return 'ok', 200
    except Exception as e:
        logger.error(f"Telegram webhook error: {e}")
        return 'error', 500

@app.route('/github-webhook', methods=['POST'])
def github_webhook():
    """GitHub Webhook - 自动部署"""
    try:
        signature = request.headers.get('X-Hub-Signature-256', '')
        payload = request.get_data()
        
        expected_signature = 'sha256=' + hmac.new(
            GITHUB_WEBHOOK_SECRET.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            logger.warning("GitHub webhook signature mismatch!")
            return 'Unauthorized', 401
        
        data = request.get_json()
        ref = data.get('ref', '')
        
        if ref != 'refs/heads/main':
            logger.info(f"Ignoring non-main branch push: {ref}")
            return 'OK', 200
        
        logger.info("GitHub webhook received! Starting auto-deploy...")
        
        deploy_script = """
        cd /opt/alphaspeak && \
        git pull origin main && \
        pip install -r requirements.txt && \
        systemctl restart alphaspeak
        """
        
        result = subprocess.run(deploy_script, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Auto-deploy successful!")
            return 'Deployed', 200
        else:
            logger.error(f"Deploy failed: {result.stderr}")
            return 'Deploy failed', 500
            
    except Exception as e:
        logger.error(f"GitHub webhook error: {e}")
        return 'Error', 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "bot": "Alpha"}), 200

# ============= 🚀 应用初始化 =============
application = None

def post_init():
    global application
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("daily", daily_vocabulary))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CommandHandler("streak", streak))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("nickname", nickname_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(CallbackQueryHandler(set_nickname_handler))
    
    logger.info("Alpha bot initialized with nickname feature! 🌟")

if __name__ == "__main__":
    post_init()
    port = int(os.getenv('PORT', 8080))
    logger.info(f"Starting Alpha bot on port {port}...")
    app.run(host='0.0.0.0', port=port)
