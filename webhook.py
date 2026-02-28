#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌟 AlphaSpeak - 美语陪练阿尔法 🌟
带 GitHub 自动部署功能的版本
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
BOT_TOKEN = os.getenv("BOT_TOKEN", "8603041416:AAHMAVuUXQ0agNns9ZJW5VjngeOzwS0IC0M")
TTS_ENABLED = os.getenv("TTS_ENABLED", "true").lower() == "true"
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "alphaspeak2026")

# Flask 应用
app = Flask(__name__)

# ============= 🎨 Alpha 人设配置 =============
ALPHA_PERSONA = {
    "name": "Alpha",
    "title": "你的美语小伙伴",
    "personality": "阳光开朗的美语少年，像邻居家的大哥哥",
    "emojis": ["🌟", "✨", "🎉", "😎", "💪", "🔥", "📚", "🎤", "💫", "🚀"],
    "kaomoji": ["(ง •̀_•́)ง", "(✧ω✧)", "(｡•̀ᴗ-)✧", "ヾ (•ω•`)o", "٩ (๑>◡<๑)۶"],
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
    "噔噔噔~ Alpha 闪亮登场！ 今天也要一起学习进步哦！",
]

# ============= 📚 词汇库（简化版，完整代码见原文件） =============
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
            "level": "CET-4",
            "daily_streak": 0,
            "last_practice": None,
            "total_words_learned": 0,
            "mastered_words": [],
            "weak_words": [],
            "achievements": [],
        }
    return USER_DATA[user_id]

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
/help - 帮助指南 ❓

准备好了吗？输入 /daily 开始今天的英语冒险吧！{get_random_kaomoji()}
    """
    await update.message.reply_text(message)

async def daily_vocabulary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    vocab = generate_daily_vocabulary()
    word = vocab["word"]
    data = vocab["data"]
    theme = vocab["theme"]
    
    user = get_user_data(update.effective_user.id)
    user["total_words_learned"] += 1
    if word not in user["mastered_words"]:
        user["mastered_words"].append(word)
    
    message = f"""
{get_random_emoji()} **今日词汇：{word.upper()}** {get_random_emoji()}
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
    
    await update.message.reply_text(f"🤔 '{data['definition']}' 对应哪个单词？", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data.startswith("quiz_"):
        parts = data.split("_")
        correct = parts[1]
        selected = parts[2]
        
        if selected == correct:
            await query.edit_message_text(f"✅ 答对了！{get_random_kaomoji()}")
        else:
            await query.edit_message_text(f"❌ 正确答案是：{correct}\n\n加油！💪")

async def streak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user_data(update.effective_user.id)
    await update.message.reply_text(f"🔥 **连续学习**：{user['daily_streak']} 天\n\n继续加油！{get_random_kaomoji()}")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user_data(update.effective_user.id)
    await update.message.reply_text(f"""
📊 **学习统计**
📚 已学：{user['total_words_learned']} 词
🔥 连续：{user['daily_streak']} 天
🏆 成就：{len(user['achievements'])} 个
    """)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
🆘 **帮助指南**
/daily - 每日词汇
/quiz - 小测验
/streak - 连续天数
/stats - 学习统计
/help - 帮助
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
    """
    GitHub Webhook - 自动部署
    当 GitHub 有 push 事件时，自动拉取最新代码并重启服务
    """
    try:
        # 验证签名
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
        
        # 解析 payload
        data = request.get_json()
        ref = data.get('ref', '')
        
        # 只处理 main 分支的推送
        if ref != 'refs/heads/main':
            logger.info(f"Ignoring non-main branch push: {ref}")
            return 'OK', 200
        
        logger.info("GitHub webhook received! Starting auto-deploy...")
        
        # 执行部署脚本
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

@app.route('/deploy', methods=['POST'])
def manual_deploy():
    """手动触发部署（可选）"""
    try:
        deploy_script = """
        cd /opt/alphaspeak && \
        git pull origin main && \
        pip install -r requirements.txt && \
        systemctl restart alphaspeak
        """
        result = subprocess.run(deploy_script, shell=True, capture_output=True, text=True)
        return jsonify({
            "status": "success" if result.returncode == 0 else "failed",
            "output": result.stdout,
            "error": result.stderr
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

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
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    logger.info("Alpha bot initialized! 🌟")

if __name__ == "__main__":
    post_init()
    port = int(os.getenv('PORT', 8080))
    logger.info(f"Starting Alpha bot on port {port}...")
    app.run(host='0.0.0.0', port=port)
