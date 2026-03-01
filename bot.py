#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌟 AlphaSpeak - 美语陪练阿尔法 🌟
改造版本：阳光美语少年 Alpha，带语音功能 + 称呼选择 + 英语水平选择

改造需求：
- 机器人名称：Alpha（阿尔法）
- 人设：阳光开朗的美语少年，像邻居家的大哥哥
- 语气：活泼有趣、emoji 颜文字、谐音梗、故事化教学
- 功能：称呼选择、英语水平选择、语音功能、智能复习
"""

import os
import json
import random
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, ContextTypes, filters
)

# ============= 🔑 配置 =============
BOT_TOKEN = os.getenv("BOT_TOKEN", "8603041416:AAHMAVuUXQ0agNns9ZJW5VjngeOzwS0IC0M")
VOICE_ENABLED = os.getenv("VOICE_ENABLED", "true").lower() == "true"

# 日志配置
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============= 🎨 Alpha 人设配置 =============
ALPHA_PERSONA = {
    "name": "Alpha",
    "title": "你的美语小伙伴",
    "personality": "阳光开朗的美语少年，像邻居家的大哥哥",
    "age": "18 岁",
    "voice_style": "阳光灿烂的少年音，元气满满、温暖治愈、略带俏皮",
    "emojis": ["🌟", "✨", "🎉", "😎", "💪", "🔥", "📚", "🎤", "💫", "🚀", "🎯", "🏆", "💡", "🎵", "🌈"],
    "kaomoji": [
        "(ง •̀_•́)ง", "(✧ω✧)", "(｡•̀ᴗ-)✧", "ヾ (•ω•`)o", "٩ (๑>◡<๑)۶",
        "(~￣▽￣)~", "o (￣▽￣) d", "(´▽`ʃ♡ƪ)", "(*´▽`*)", "ヾ (≧▽≦*)o"
    ],
}

# ============= 👑 称呼选项 =============
NICKNAME_OPTIONS = {
    "1": {"label": "富公", "emoji": "💰", "desc": "尊贵的富公大人"},
    "2": {"label": "富婆", "emoji": "💎", "desc": "优雅的富婆大人"},
    "3": {"label": "小主人", "emoji": "👑", "desc": "我最亲爱的小主人"},
    "4": {"label": "少主", "emoji": "🌟", "desc": "英气逼人的少主"},
    "5": {"label": "主公", "emoji": "⚔️", "desc": "威风凛凛的主公"},
    "6": {"label": "可爱多", "emoji": "🍦", "desc": "甜度满分的小可爱"},
    "7": {"label": "灭霸", "emoji": "🧤", "desc": "掌控全局的灭霸大人"},
}

# ============= 📊 英语水平选项 =============
ENGLISH_LEVELS = {
    "1": {"label": "新手", "emoji": "🌱", "desc": "刚开始学英语，从基础开始"},
    "2": {"label": "初级", "emoji": "🌿", "desc": "有一点基础，继续加油"},
    "3": {"label": "中级", "emoji": "🌳", "desc": "日常交流没问题"},
    "4": {"label": "高级", "emoji": "🌲", "desc": "英语大佬，挑战高阶内容"},
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
    "嗨~ 我的学习小伙伴！(｡•̀ᴗ-)✧ 今天也是变强的一天呢！",
    "哇哦~ 你终于来啦！Alpha 都想你想念了！(´▽`ʃ♡ƪ)",
]

# ============= 📚 词汇库（商务/区块链/Web3） =============
VOCABULARY_DB = {
    "business": {
        "leverage": {
            "definition": "利用（资源、优势等）",
            "example": "We can leverage our existing customer base to launch new products.",
            "example_cn": "我们可以利用现有的客户群来推出新产品。",
            "etymology": "来自拉丁语 'levare' (举起)，原意是用杠杆撬动重物",
            "chinese_mnemonic": "联想：'leave' + 'rage' → 留下愤怒的力量来撬动成功！",
            "pronunciation": "ˈliː.vər.ɪdʒ",
            "story": "想象一下，阿基米德说过'给我一个支点，我能撬动地球'。leverage 就是这个'撬动'的力量！在商业里，就是用现有的资源去撬动更大的成功~",
            "voice_text": "Leverage. /ˈliː.vər.ɪdʒ/. We can leverage our existing customer base.",
        },
        "synergy": {
            "definition": "协同效应，合力",
            "example": "The merger created synergy between the two companies.",
            "example_cn": "这次合并为两家公司创造了协同效应。",
            "etymology": "希腊语 'syn' (一起) + 'ergon' (工作)",
            "chinese_mnemonic": "谐音：'新能量' → 新的合作产生新能量！",
            "pronunciation": "ˈsɪn.ə.dʒi",
            "story": "synergy 就像 1+1>2 的魔法！两个人合作，产生的效果比各自为战强很多。就像复仇者联盟，每个人都很强，但合在一起就是无敌的！",
            "voice_text": "Synergy. /ˈsɪn.ə.dʒi/. The merger created synergy between the two companies.",
        },
        "paradigm": {
            "definition": "范式，模式",
            "example": "This technology represents a new paradigm in business.",
            "example_cn": "这项技术代表了商业的新范式。",
            "etymology": "希腊语 'para' (旁边) + 'deigma' (例子)",
            "chinese_mnemonic": "拆解：'para'(旁边) + 'dig'(挖) + 'm'(山) → 在旁边挖出新模式的山！",
            "pronunciation": "ˈpær.ə.daɪm",
            "story": "paradigm 就是'模式'、'典范'的意思。当有人说'paradigm shift'，就是指'范式转变'，彻底改变游戏规则的那种！",
            "voice_text": "Paradigm. /ˈpær.ə.daɪm/. This technology represents a new paradigm.",
        },
    },
    "blockchain": {
        "consensus": {
            "definition": "共识机制",
            "example": "Proof of Stake is a consensus mechanism used by many blockchains.",
            "example_cn": "权益证明是许多区块链使用的共识机制。",
            "etymology": "拉丁语 'con' (一起) + 'sentire' (感觉)",
            "chinese_mnemonic": "谐音：'肯死死' → 肯定要死死地达成共识！",
            "pronunciation": "kənˈsen.səs",
            "story": "consensus 就是'大家一致同意'的意思。在区块链里，所有节点要达成一致才能确认交易，就像一群人投票决定去哪吃饭，大家都同意才行！",
            "voice_text": "Consensus. /kənˈsen.səs/. Proof of Stake is a consensus mechanism.",
        },
        "immutable": {
            "definition": "不可变的",
            "example": "Blockchain records are immutable once added to the chain.",
            "example_cn": "区块链记录一旦添加到链上就不可更改。",
            "etymology": "拉丁语 'in' (不) + 'mutare' (改变)",
            "chinese_mnemonic": "联想：'一木土' → 一块木头埋在土里，永远不变！",
            "pronunciation": "ɪmjuː.tə.bəl",
            "story": "immutable 就是'永远不变'的意思。区块链的神奇之处就在于，一旦数据写进去，就像刻在石头上一样，永远改不了！这就是为什么它这么安全~",
            "voice_text": "Immutable. /ɪmjuː.tə.bəl/. Blockchain records are immutable.",
        },
        "decentralized": {
            "definition": "去中心化的",
            "example": "Bitcoin is a decentralized cryptocurrency.",
            "example_cn": "比特币是一种去中心化的加密货币。",
            "etymology": "前缀 'de' (去除) + 'central' (中心) + 后缀 'ized' (使...化)",
            "chinese_mnemonic": "联想：'弟散他力' → 弟弟把权力分散给大家！",
            "pronunciation": "ˌdiːˈsen.trəl.aɪzd",
            "story": "decentralized 就是'没有中心'的意思。传统的银行有一个中心，但比特币没有，所有人都平等参与，就像没有国王的王国，每个人都是自己的主人！",
            "voice_text": "Decentralized. /ˌdiːˈsen.trəl.aɪzd/. Bitcoin is a decentralized cryptocurrency.",
        },
    },
    "web3": {
        "tokenomics": {
            "definition": "代币经济学",
            "example": "Good tokenomics is crucial for a successful crypto project.",
            "example_cn": "好的代币经济学对成功的加密项目至关重要。",
            "etymology": "token + economics",
            "chinese_mnemonic": "谐音：'偷啃我米克斯' → 偷啃我的米 (代币) 还要学经济！",
            "pronunciation": "ˌtəʊ.kəˈnɒm.ɪks",
            "story": "tokenomics 是 token 和 economics 的组合词，就是研究代币怎么发行、怎么分配、怎么增值的学问。一个好的项目，tokenomics 设计得好，大家都有钱赚！",
            "voice_text": "Tokenomics. /ˌtəʊ.kəˈnɒm.ɪks/. Good tokenomics is crucial for success.",
        },
        "metaverse": {
            "definition": "元宇宙",
            "example": "Many companies are investing in the metaverse.",
            "example_cn": "许多公司正在投资元宇宙。",
            "etymology": "前缀 'meta' (超越) + 'universe' (宇宙)",
            "chinese_mnemonic": "联想：'妹她佛斯' → 妹妹在虚拟世界里当佛祖！",
            "pronunciation": "ˈmet.ə.vɜːs",
            "story": "metaverse 就是'超越现实的宇宙'。想象一下，你可以在虚拟世界里工作、娱乐、社交，甚至买房子！就像《头号玩家》里的绿洲，那就是元宇宙！",
            "voice_text": "Metaverse. /ˈmet.ə.vɜːs/. Many companies are investing in the metaverse.",
        },
        "interoperability": {
            "definition": "互操作性",
            "example": "Web3 aims for interoperability between different blockchain networks.",
            "example_cn": "Web3 旨在实现不同区块链网络之间的互操作性。",
            "etymology": "前缀 'inter' (相互) + 'operate' (操作) + 后缀 'ability' (能力)",
            "chinese_mnemonic": "拆解：'因特'(互联网) + 'operate'(操作) + 'ability'(能力) → 互联网操作能力！",
            "pronunciation": "ɪn.təˌrɒp.ər.əˈbɪl.ə.ti",
            "story": "interoperability 就是'互相能沟通'的能力。就像你说中文，我说英文，我们互相听不懂。但如果有个翻译，我们就能交流了。区块链之间也需要这种'翻译'能力！",
            "voice_text": "Interoperability. /ɪn.təˌrɒp.ər.əˈbɪl.ə.ti/. Web3 aims for interoperability.",
        },
    },
}

# ============= 💾 用户数据结构 =============
USER_DATA = {}

def get_user_data(user_id: int) -> Dict:
    """获取用户数据"""
    if user_id not in USER_DATA:
        USER_DATA[user_id] = {
            "nickname": None,
            "nickname_label": None,
            "english_level": None,
            "english_level_label": None,
            "daily_streak": 0,
            "last_practice": None,
            "total_words_learned": 0,
            "mastered_words": [],
            "weak_words": [],
            "favorite_words": [],
            "mistakes": [],
            "achievements": [],
            "voice_enabled": True,
            "learning_preference": {
                "favorite_themes": [],
                "preferred_time": None,
            },
            "created_at": datetime.now().isoformat(),
        }
    return USER_DATA[user_id]

def save_user_data(user_id: int, data: Dict):
    """保存用户数据"""
    USER_DATA[user_id] = data

def get_nickname(user_id: int) -> tuple:
    """获取用户称呼，返回 (label, emoji)"""
    user = get_user_data(user_id)
    code = user.get("nickname")
    if code and code in NICKNAME_OPTIONS:
        return NICKNAME_OPTIONS[code]["label"], NICKNAME_OPTIONS[code]["emoji"]
    return None, None

def set_nickname(user_id: int, code: str):
    """设置用户称呼"""
    user = get_user_data(user_id)
    user["nickname"] = code
    user["nickname_label"] = NICKNAME_OPTIONS[code]["label"]
    save_user_data(user_id, user)

def get_level(user_id: int) -> tuple:
    """获取用户英语水平，返回 (label, emoji)"""
    user = get_user_data(user_id)
    code = user.get("english_level")
    if code and code in ENGLISH_LEVELS:
        return ENGLISH_LEVELS[code]["label"], ENGLISH_LEVELS[code]["emoji"]
    return None, None

def set_level(user_id: int, code: str):
    """设置用户英语水平"""
    user = get_user_data(user_id)
    user["english_level"] = code
    user["english_level_label"] = ENGLISH_LEVELS[code]["label"]
    save_user_data(user_id, user)

def generate_daily_vocabulary(level: str = None) -> Dict:
    """生成每日词汇"""
    themes = list(VOCABULARY_DB.keys())
    theme = random.choice(themes)
    words = list(VOCABULARY_DB[theme].keys())
    word = random.choice(words)
    return {"word": word, "theme": theme, "data": VOCABULARY_DB[theme][word]}

def get_random_greeting() -> str:
    """获取随机开场白"""
    return random.choice(GREETINGS)

def get_random_emoji() -> str:
    """获取随机 emoji"""
    return random.choice(ALPHA_PERSONA["emojis"])

def get_random_kaomoji() -> str:
    """获取随机颜文字"""
    return random.choice(ALPHA_PERSONA["kaomoji"])

# ============= 🎙️ 语音功能 =============
async def send_voice_message(update: Update, text: str, filename: str = "voice"):
    """发送语音消息（简化版，实际部署时集成 TTS API）"""
    if not VOICE_ENABLED:
        return
    
    try:
        # 这里集成 TTS API（如 ElevenLabs、Azure TTS 等）
        # 简化版：发送文字提示，实际部署时替换为真实语音
        voice_hint = f"🎙️ *【Alpha 语音】* \n\n_{text}_"
        await update.message.reply_text(voice_hint, parse_mode="Markdown")
    except Exception as e:
        logger.warning(f"语音发送失败：{e}")

# ============= 🤖 命令处理 =============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令 - 显示称呼和英语水平选择"""
    user_id = update.effective_user.id
    user = get_user_data(user_id)
    
    # 检查是否已经设置过称呼和水平
    if user.get("nickname") and user.get("english_level"):
        nickname, emoji = get_nickname(user_id)
        level, level_emoji = get_level(user_id)
        greeting = get_random_greeting()
        
        message = f"""
{greeting}

{emoji} **{nickname}**，欢迎回来！{emoji}

📊 **你的学习档案**：
• 英语水平：{level_emoji} {level}
• 已学单词：{user['total_words_learned']} 个
• 连续学习：{user['daily_streak']} 天

🎯 **关于 Alpha**：
我是你的美语小伙伴 Alpha，一个阳光开朗的美语少年~
我会用最有趣的方式帮你学好英语！

📚 **可用命令**：
/daily - 每日词汇练习 📖
/quiz - 单词小测验 🎯
/review - 智能复习 🔄
/mistakes - 查看错题本 📝
/level - 修改英语水平 📊
/nickname - 修改称呼 👤
/stats - 学习数据统计 📈
/streak - 连续学习天数 🔥
/help - 帮助指南 ❓

准备好了吗？输入 /daily 开始今天的英语冒险吧！{get_random_kaomoji()}
        """
        await update.message.reply_text(message)
    else:
        # 未设置，显示选择界面
        keyboard = []
        
        # 称呼选择
        keyboard.append([InlineKeyboardButton("👑 第一步：选择称呼", callback_data="step_nickname")])
        for code, info in NICKNAME_OPTIONS.items():
            keyboard.append([InlineKeyboardButton(f"{info['emoji']} {info['label']}", callback_data=f"nickname_{code}")])
        
        keyboard.append([InlineKeyboardButton("━━━━━━━━━━", callback_data="separator")])
        
        # 英语水平选择
        keyboard.append([InlineKeyboardButton("📊 第二步：选择英语水平", callback_data="step_level")])
        for code, info in ENGLISH_LEVELS.items():
            keyboard.append([InlineKeyboardButton(f"{info['emoji']} {info['label']}", callback_data=f"level_{code}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_message = f"""
🌟 **欢迎来到 Alpha 的美语训练营**！ 🌟

我是 Alpha，你的阳光美语小伙伴~ (✧ω✧)

在开始学习之前，让我更了解你吧！

👇 **请先选择你喜欢的称呼** 👇
我会用这个称呼叫你哦~ 💕

然后选择你的英语水平，我会根据你的水平调整教学内容！
        """
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def nickname_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理称呼选择回调"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data.startswith("nickname_"):
        code = data.split("_")[1]
        user_id = update.effective_user.id
        
        if code in NICKNAME_OPTIONS:
            set_nickname(user_id, code)
            nickname = NICKNAME_OPTIONS[code]["label"]
            emoji = NICKNAME_OPTIONS[code]["emoji"]
            
            user = get_user_data(user_id)
            if user.get("english_level"):
                level, level_emoji = get_level(user_id)
                success_message = f"""
{emoji} 太好啦！以后我就叫你 **{nickname}** 啦！{emoji}

从现在开始，你就是我的专属 {nickname} 了~ (✧ω✧)

📊 你的英语水平：{level_emoji} {level}

准备好开始今天的英语学习了吗？
输入 /daily 获取今日词汇吧！📚

或者输入 /help 查看所有功能哦~
                """
            else:
                success_message = f"""
{emoji} 太好啦！以后我就叫你 **{nickname}** 啦！{emoji}

从现在开始，你就是我的专属 {nickname} 了~ (✧ω✧)

👇 **接下来请选择你的英语水平** 👇
这会影响我教学内容的难度哦！
                """
            await query.edit_message_text(success_message)

async def level_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理英语水平选择回调"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data.startswith("level_"):
        code = data.split("_")[1]
        user_id = update.effective_user.id
        
        if code in ENGLISH_LEVELS:
            set_level(user_id, code)
            level = ENGLISH_LEVELS[code]["label"]
            emoji = ENGLISH_LEVELS[code]["emoji"]
            
            nickname, nick_emoji = get_nickname(user_id)
            if nickname:
                success_message = f"""
{emoji} 收到！你的英语水平是 **{level}**！{emoji}

{nick_emoji} **{nickname}**，现在一切都设置好啦！(✧ω✧)

🎯 **Alpha 会为你**：
• 根据{level}水平调整词汇难度
• 用有趣的方式讲解单词
• 记录你的学习进度
• 在你需要时给予鼓励

准备好开始今天的英语学习了吗？
输入 /daily 获取今日词汇吧！📚

或者输入 /help 查看所有功能哦~ {get_random_kaomoji()}
            """
            else:
                success_message = f"""
{emoji} 收到！你的英语水平是 **{level}**！{emoji}

👇 **接下来请选择你喜欢的称呼** 👇
这会影响我以后怎么叫你哦~
                """
            await query.edit_message_text(success_message)

async def nickname_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /nickname 命令 - 重新选择称呼"""
    user_id = update.effective_user.id
    
    keyboard = []
    for code, info in NICKNAME_OPTIONS.items():
        keyboard.append([InlineKeyboardButton(f"{info['emoji']} {info['label']}", callback_data=f"nickname_{code}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    current_nickname, _ = get_nickname(user_id)
    message = f"""
👤 **修改称呼**

{get_random_emoji()} 当前称呼：{current_nickname if current_nickname else '未设置'}

请选择一个新的称呼吧~
    """
    
    await update.message.reply_text(message, reply_markup=reply_markup)

async def level_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /level 命令 - 重新选择英语水平"""
    user_id = update.effective_user.id
    
    keyboard = []
    for code, info in ENGLISH_LEVELS.items():
        keyboard.append([InlineKeyboardButton(f"{info['emoji']} {info['label']}", callback_data=f"level_{code}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    current_level, _ = get_level(user_id)
    message = f"""
📊 **修改英语水平**

{get_random_emoji()} 当前水平：{current_level if current_level else '未设置'}

请选择一个新的水平，我会调整教学内容难度~
    """
    
    await update.message.reply_text(message, reply_markup=reply_markup)

async def daily_vocabulary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /daily 命令 - 每日词汇练习"""
    user_id = update.effective_user.id
    user = get_user_data(user_id)
    
    # 检查是否设置基本信息
    if not user.get("nickname") or not user.get("english_level"):
        await update.message.reply_text("🤔 先完成设置吧！输入 /start 开始~")
        return
    
    nickname, nick_emoji = get_nickname(user_id)
    level, level_emoji = get_level(user_id)
    
    vocab = generate_daily_vocabulary()
    word = vocab["word"]
    data = vocab["data"]
    theme = vocab["theme"]
    
    user["total_words_learned"] += 1
    if word not in user["mastered_words"]:
        user["mastered_words"].append(word)
    
    message = f"""
{nick_emoji} **{nickname}，今日词汇：{word.upper()}** {get_random_emoji()}
📍 **主题**：{theme.title()} | **难度**：{level_emoji} {level}

🎙️ *【Alpha 发音】: /{data['pronunciation']}/*

📝 **定义**：{data['definition']}
💬 **例句**：{data['example']}
🇨🇳 **翻译**：{data['example_cn']}

🏛️ **词源故事**：
{data.get('story', data['etymology'])}

🧠 **中文记忆法**：
{data['chinese_mnemonic']}

🎯 **小挑战**：用这个单词造个句子吧！{get_random_kaomoji()}
    """
    await update.message.reply_text(message)
    
    # 发送语音（如果开启）
    if VOICE_ENABLED and user.get("voice_enabled", True):
        await send_voice_message(update, data.get("voice_text", f"{word}. {data['example']}"))

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /quiz 命令 - 小测验"""
    user_id = update.effective_user.id
    user = get_user_data(user_id)
    
    if not user.get("nickname"):
        await update.message.reply_text("🤔 先完成设置吧！输入 /start 开始~")
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
    
    nickname, _ = get_nickname(user_id)
    await update.message.reply_text(
        f"🤔 {nickname}，'{data['definition']}' 对应哪个单词？", 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理按钮回调"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    nickname, _ = get_nickname(user_id)
    nickname = nickname or "小伙伴"
    
    if data.startswith("quiz_"):
        parts = data.split("_")
        correct = parts[1]
        selected = parts[2]
        
        if selected == correct:
            await query.edit_message_text(f"✅ {nickname} 太棒了！答对了！{get_random_kaomoji()}")
        else:
            # 记录错题
            user = get_user_data(user_id)
            if correct not in user["mistakes"]:
                user["mistakes"].append(correct)
            await query.edit_message_text(f"❌ {nickname}，正确答案是：{correct}\n\n已加入错题本，记得复习哦！💪")
    
    elif data.startswith("step_"):
        await query.answer("请继续选择下方选项~")

async def review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /review 命令 - 智能复习"""
    user_id = update.effective_user.id
    user = get_user_data(user_id)
    
    if not user.get("nickname"):
        await update.message.reply_text("🤔 先完成设置吧！输入 /start 开始~")
        return
    
    nickname, nick_emoji = get_nickname(user_id)
    
    # 获取需要复习的单词（简化版：随机选择已学单词）
    if user["mastered_words"]:
        review_words = random.sample(user["mastered_words"], min(3, len(user["mastered_words"])))
        message = f"""
{nick_emoji} **{nickname}，复习时间到**！ {get_random_emoji()}

📚 **今日复习单词**：
"""
        for word in review_words:
            # 查找单词信息
            for theme, words in VOCABULARY_DB.items():
                if word in words:
                    data = words[word]
                    message += f"\n• **{word}**: {data['definition']}"
                    break
        
        message += f"\n\n{get_random_kaomoji()} 还记得这些单词的意思吗？"
        await update.message.reply_text(message)
    else:
        await update.message.reply_text(f"{nick_emoji} {nickname}，你还没有学过单词哦~ 先输入 /daily 学习吧！📚")

async def mistakes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /mistakes 命令 - 错题本"""
    user_id = update.effective_user.id
    user = get_user_data(user_id)
    
    if not user.get("nickname"):
        await update.message.reply_text("🤔 先完成设置吧！输入 /start 开始~")
        return
    
    nickname, nick_emoji = get_nickname(user_id)
    
    if user["mistakes"]:
        message = f"""
{nick_emoji} **{nickname} 的错题本** 📝

{get_random_emoji()} 这些单词需要多复习哦：

"""
        for word in user["mistakes"][:10]:
            message += f"• {word}\n"
        
        message += f"\n{get_random_kaomoji()} 加油！多复习几次就能记住啦！"
        await update.message.reply_text(message)
    else:
        await update.message.reply_text(f"{nick_emoji} {nickname} 太棒了！错题本是空的！继续保持！🏆")

async def streak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /streak 命令"""
    user_id = update.effective_user.id
    user = get_user_data(user_id)
    nickname, nick_emoji = get_nickname(user_id)
    nickname = nickname or "小伙伴"
    
    message = f"🔥 **{nickname}，连续学习**：{user['daily_streak']} 天\n\n"
    if user['daily_streak'] >= 7:
        message += f"🏆 太厉害了！已经坚持一周了！{get_random_kaomoji()}"
    elif user['daily_streak'] >= 3:
        message += f"💪 继续加油！离一周目标不远了！{get_random_kaomoji()}"
    else:
        message += f"✨ 新的开始！坚持就是胜利！{get_random_kaomoji()}"
    
    await update.message.reply_text(message)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /stats 命令"""
    user_id = update.effective_user.id
    user = get_user_data(user_id)
    nickname, nick_emoji = get_nickname(user_id)
    level, level_emoji = get_level(user_id)
    
    nickname = nickname or "小伙伴"
    level = level or "未设置"
    
    await update.message.reply_text(f"""
📊 **{nickname} 的学习统计** {get_random_emoji()}

📚 已学单词：{user['total_words_learned']} 个
🔥 连续学习：{user['daily_streak']} 天
📝 错题本：{len(user['mistakes'])} 个
🏆 成就：{len(user['achievements'])} 个
📖 英语水平：{level_emoji} {level}

{get_random_kaomoji()} 继续加油，你越来越棒了！
    """)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /help 命令"""
    nickname, _ = get_nickname(update.effective_user.id)
    nickname = nickname or "小伙伴"
    
    await update.message.reply_text(f"""
🆘 **{nickname} 的帮助指南** {get_random_emoji()}

**📚 学习功能**：
/daily - 每日词汇（含词源 + 谐音梗）
/quiz - 单词小测验
/review - 智能复习
/mistakes - 查看错题本

**📊 个人设置**：
/nickname - 修改称呼
/level - 修改英语水平
/stats - 学习统计
/streak - 连续天数

**💡 学习建议**：
1. 每天学习 30 分钟
2. 多用新单词造句
3. 定期复习错题
4. 不怕犯错，大胆说

**🎙️ 语音功能**：
Alpha 会用标准美音朗读单词和例句
帮助你练习听力和发音！

有任何问题随时找 Alpha！{get_random_kaomoji()}
    """)

# ============= 🚀 主函数 =============

def main():
    """主函数"""
    logger.info("🌟 Alpha bot is starting... (Polling Mode)")
    logger.info(f"🎙️ 语音功能：{'开启' if VOICE_ENABLED else '关闭'}")
    
    # 创建应用
    application = Application.builder().token(BOT_TOKEN).build()
    
    # 添加处理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("daily", daily_vocabulary))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CommandHandler("review", review))
    application.add_handler(CommandHandler("mistakes", mistakes))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("streak", streak))
    application.add_handler(CommandHandler("nickname", nickname_command))
    application.add_handler(CommandHandler("level", level_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(CallbackQueryHandler(nickname_handler))
    application.add_handler(CallbackQueryHandler(level_handler))
    
    # 启动机器人
    logger.info("✅ Alpha bot initialized! Waiting for messages...")
    logger.info(f"🎨 人设：{ALPHA_PERSONA['name']} - {ALPHA_PERSONA['personality']}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
