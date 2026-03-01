#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌟 AlphaSpeak - 美语陪练阿尔法 🌟
简化版 - 使用 Polling 模式（无需 webhook，适合阿里云部署）
"""

import os
import json
import random
import logging
from datetime import datetime
from typing import Dict, List

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, filters

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============= 🔑 机器人配置 =============
BOT_TOKEN = os.getenv("BOT_TOKEN", "8603041416:AAHMAVuUXQ0agNns9ZJW5VjngeOzwS0IC0M")

# ============= 🎨 Alpha 人设 =============
ALPHA_PERSONA = {
    "name": "Alpha",
    "title": "你的美语小伙伴",
    "personality": "阳光开朗的美语少年，像邻居家的大哥哥",
    "emojis": ["🌟", "✨", "🎉", "😎", "💪", "🔥", "📚", "🎤", "💫", "🚀"],
    "kaomoji": ["(ง •̀_•́)ง", "(✧ω✧)", "(｡•̀ᴗ-)✧", "ヾ (•ω•`)o", "٩ (๑>◡<๑)۶"],
}

# ============= 👑 称呼选项 =============
NICKNAME_OPTIONS = {
    "1": {"label": "富公", "emoji": "💰"},
    "2": {"label": "富婆", "emoji": "💎"},
    "3": {"label": "小主人", "emoji": "👑"},
    "4": {"label": "少主", "emoji": "🌟"},
    "5": {"label": "主公", "emoji": "⚔️"},
    "6": {"label": "可爱多", "emoji": "🍦"},
    "7": {"label": "灭霸", "emoji": "🧤"},
}

# ============= 🎭 开场白 =============
GREETINGS = [
    "哟！你来啦！我是你的美语小伙伴 Alpha！🎉 今天也是和我一起征服英语的一天呢~",
    "早啊小懒虫！☀️ Alpha 已经等你好久啦！准备好被英语轰炸了吗😎",
    "哈喽哈喽！(✧ω✧) 今天想学点什么？商务、区块链还是 Web3？",
    "嘿！我的学习搭档！💪 今天也是元气满满的一天呢~",
    "哇！见到你真开心！ヾ (•ω•`)o 今天我们来学点酷酷的单词吧！",
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
        "paradigm": {
            "definition": "范式，模式",
            "example": "This technology represents a new paradigm in business.",
            "etymology": "希腊语 'para' (旁边) + 'deigma' (例子)",
            "chinese_mnemonic": "拆解：'para'(旁边) + 'dig'(挖) + 'm'(山) → 在旁边挖出新模式的山！",
            "pronunciation": "ˈpær.ə.daɪm",
        }
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
        "decentralized": {
            "definition": "去中心化的",
            "example": "Bitcoin is a decentralized cryptocurrency.",
            "etymology": "前缀 'de' (去除) + 'central' (中心) + 后缀 'ized'",
            "chinese_mnemonic": "联想：'弟散他力' → 弟弟把权力分散给大家！",
            "pronunciation": "ˌdiːˈsen.trəl.aɪzd",
        }
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
        "interoperability": {
            "definition": "互操作性",
            "example": "Web3 aims for interoperability between different blockchain networks.",
            "etymology": "前缀 'inter' (相互) + 'operate' (操作) + 后缀 'ability' (能力)",
            "chinese_mnemonic": "拆解：'因特'(互联网) + 'operate'(操作) + 'ability'(能力)",
            "pronunciation": "ɪn.təˌrɒp.ər.əˈbɪl.ə.ti",
        }
    }
}

# ============= 💾 用户数据 =============
USER_DATA = {}

def get_user_data(user_id: int) -> Dict:
    if user_id not in USER_DATA:
        USER_DATA[user_id] = {
            "nickname": None,
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
    user = get_user_data(user_id)
    nickname_code = user.get("nickname")
    if nickname_code and nickname_code in NICKNAME_OPTIONS:
        return NICKNAME_OPTIONS[nickname_code]["label"]
    return None

def set_nickname(user_id: int, nickname_code: str):
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
    """处理 /start 命令"""
    user_id = update.effective_user.id
    user = get_user_data(user_id)
    
    if user.get("nickname"):
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

async def daily_vocabulary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /daily 命令"""
    user_id = update.effective_user.id
    user = get_user_data(user_id)
    
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
    """处理 /quiz 命令"""
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

async def nickname_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /nickname 命令"""
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

# ============= 🚀 主函数 =============

def main():
    """主函数 - 使用 Polling 模式"""
    logger.info("🌟 Alpha bot is starting... (Polling Mode)")
    
    # 创建应用
    application = Application.builder().token(BOT_TOKEN).build()
    
    # 添加处理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("daily", daily_vocabulary))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CommandHandler("streak", streak))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("nickname", nickname_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(CallbackQueryHandler(set_nickname_handler))
    
    # 启动机器人（Polling 模式）
    logger.info("✅ Alpha bot initialized! Waiting for messages...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
