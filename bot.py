#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌟 AlphaSpeak - 美语陪练阿尔法 🌟
完整改造版本：阳光美语少年 Alpha

改造需求：
- 机器人名称：Alpha（阿尔法）
- 人设：阳光开朗的美语少年，像邻居家的大哥哥
- 语气：活泼有趣、emoji 颜文字、谐音梗、故事化教学
- 功能：称呼选择、英语水平选择、语音功能、智能复习、定时问候
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
    MessageHandler, ContextTypes, filters, JobQueue
)

# ============= 🔑 配置 =============
BOT_TOKEN = os.getenv("BOT_TOKEN", "8603041416:AAHMAVuUXQ0agNns9ZJW5VjngeOzwS0IC0M")
VOICE_ENABLED = os.getenv("VOICE_ENABLED", "true").lower() == "true"
TIMEZONE = "Asia/Shanghai"  # 北京时间

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
    "1": {"label": "富公", "emoji": "💰", "style": "霸气老板风"},
    "2": {"label": "富婆", "emoji": "💎", "style": "霸气老板娘风"},
    "3": {"label": "小主人", "emoji": "👑", "style": "温柔可爱风"},
    "4": {"label": "少主", "emoji": "🌟", "style": "古风尊贵风"},
    "5": {"label": "主公", "emoji": "⚔️", "style": "三国谋士风"},
    "6": {"label": "可爱多", "emoji": "🍦", "style": "甜蜜软萌风"},
    "7": {"label": "灭霸", "emoji": "🧤", "style": "漫威霸气风"},
}

# ============= 📊 英语水平选项 =============
ENGLISH_LEVELS = {
    "1": {"label": "新手", "emoji": "🌱", "desc": "零基础或刚入门，从简单词汇开始"},
    "2": {"label": "初级", "emoji": "🌿", "desc": "掌握基础词汇，能进行简单日常对话"},
    "3": {"label": "中级", "emoji": "🌳", "desc": "词汇量较好，能理解复杂句型和文章"},
    "4": {"label": "高级", "emoji": "🌲", "desc": "英语流利，需要精进表达和地道用法"},
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

# ============= 🌅 早安问候语 =============
MORNING_GREETINGS = [
    "早安呀！今天又是元气满满的一天呢~ ☀️",
    "早上好！阳光和你都在，就是美好的一天！✨",
    "早安！新的一天，新的开始，Alpha 陪你一起加油！💪",
    "早啊！昨晚睡得好吗？今天也要好好学习哦~ 📚",
    "Morning！今天的你也是闪闪发光的呢！🌟",
]

# ============= 🌙 晚安问候语 =============
NIGHT_GREETINGS = [
    "晚安啦！今天辛苦啦~ 好好休息哦！🌙",
    "晚安！今天也是进步的一天呢，为你骄傲！💫",
    "睡个好觉！明天继续和 Alpha 一起学英语~ 😴",
    "晚安！今天的努力，明天的收获！🌟",
    "Good night！做个好梦，梦里也有英语单词哦~ (开玩笑的啦！) 😄",
]

# ============= 📚 词汇库（按难度分级） =============
VOCABULARY_DB = {
    # ============ 新手级 ============
    "beginner": {
        "hello": {
            "definition": "你好，问候语",
            "example": "Hello! How are you today?",
            "example_cn": "你好！今天怎么样？",
            "etymology": "来自古英语 'hāl'，意为'健康'",
            "chinese_mnemonic": "谐音：'哈喽' → 打招呼的声音！",
            "pronunciation": "həˈləʊ",
            "story": "hello 是世界上最常用的问候语之一。据说最早是电话发明者贝尔推广开来的，以前人们见面说'good day'，有了电话后就说'hello'啦！",
            "voice_text": "Hello. /həˈləʊ/. Hello! How are you today?",
            "level": 1,
        },
        "thank": {
            "definition": "感谢，谢谢",
            "example": "Thank you for your help!",
            "example_cn": "谢谢你的帮助！",
            "etymology": "来自古英语 'thanc'，意为'感激'",
            "chinese_mnemonic": "谐音：'三克' → 感谢你给了三克金子！",
            "pronunciation": "θæŋk",
            "story": "thank 这个词源自古英语，意思是'感激'。英语里有个词组'thank goodness'，就是'谢天谢地'的意思~",
            "voice_text": "Thank. /θæŋk/. Thank you for your help!",
            "level": 1,
        },
        "learn": {
            "definition": "学习，学会",
            "example": "I want to learn English.",
            "example_cn": "我想学英语。",
            "etymology": "来自古英语 'leornian'，意为'获取知识'",
            "chinese_mnemonic": "谐音：'冷' → 学习学到发冷！",
            "pronunciation": "lɜːn",
            "story": "learn 这个词和'lore'(知识) 是同源词。有趣的是，learner 是'学习者'，但 learning 既可以指'学习'也可以指'学问'！",
            "voice_text": "Learn. /lɜːn/. I want to learn English.",
            "level": 1,
        },
    },
    # ============ 初级 ============
    "elementary": {
        "awesome": {
            "definition": "很棒的，令人惊叹的",
            "example": "That movie was awesome!",
            "example_cn": "那部电影太棒了！",
            "etymology": "来自 'awe'(敬畏) + 'some'(有些)",
            "chinese_mnemonic": "谐音：'哦~三亩' → 哇哦，三亩地都是我的，太 awesome 了！",
            "pronunciation": "ˈɔːsəm",
            "story": "awesome 原本是指'让人心生敬畏的'，比如看到大峡谷会说'awesome'。现在口语里就是'太牛了'的意思！比'good'厉害多了~",
            "voice_text": "Awesome. /ˈɔːsəm/. That movie was awesome!",
            "level": 2,
        },
        "practice": {
            "definition": "练习，实践",
            "example": "Practice makes perfect!",
            "example_cn": "熟能生巧！",
            "etymology": "希腊语 'praktikos'，意为'实践的'",
            "chinese_mnemonic": "谐音：'扑来克提死' → 扑来练习到死！",
            "pronunciation": "ˈpræktɪs",
            "story": "practice 是个万能词！既是名词也是动词。英语里有句名言'Practice makes perfect'，就是'熟能生巧'的意思。记住：多练习才能完美！",
            "voice_text": "Practice. /ˈpræktɪs/. Practice makes perfect!",
            "level": 2,
        },
        "improve": {
            "definition": "改进，提高",
            "example": "I want to improve my English.",
            "example_cn": "我想提高我的英语。",
            "etymology": "来自 'im'(进入) + 'prove'(证明)",
            "chinese_mnemonic": "谐音：'因扑入五' → 因为扑进去学习，英语提高了！",
            "pronunciation": "ɪmˈpruːv",
            "story": "improve 的 prove 不是'证明'的意思，而是来自古法语'利润'。所以 improve 最初是'获利'的意思，后来引申为'变得更好'~",
            "voice_text": "Improve. /ɪmˈpruːv/. I want to improve my English.",
            "level": 2,
        },
    },
    # ============ 中级 ============
    "intermediate": {
        "leverage": {
            "definition": "利用（资源、优势等）",
            "example": "We can leverage our existing customer base to launch new products.",
            "example_cn": "我们可以利用现有的客户群来推出新产品。",
            "etymology": "来自拉丁语 'levare' (举起)，原意是用杠杆撬动重物",
            "chinese_mnemonic": "联想：'leave' + 'rage' → 留下愤怒的力量来撬动成功！",
            "pronunciation": "ˈliː.vər.ɪdʒ",
            "story": "想象一下，阿基米德说过'给我一个支点，我能撬动地球'。leverage 就是这个'撬动'的力量！在商业里，就是用现有的资源去撬动更大的成功~",
            "voice_text": "Leverage. /ˈliː.vər.ɪdʒ/. We can leverage our existing customer base.",
            "level": 3,
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
            "level": 3,
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
            "level": 3,
        },
    },
    # ============ 高级 ============
    "advanced": {
        "consensus": {
            "definition": "共识，一致意见",
            "example": "The committee reached a consensus after hours of discussion.",
            "example_cn": "委员会经过数小时讨论后达成了共识。",
            "etymology": "拉丁语 'con' (一起) + 'sentire' (感觉)",
            "chinese_mnemonic": "谐音：'肯死死' → 肯定要死死地达成共识！",
            "pronunciation": "kənˈsen.səs",
            "story": "consensus 就是'大家一致同意'的意思。在区块链里，所有节点要达成一致才能确认交易，就像一群人投票决定去哪吃饭，大家都同意才行！",
            "voice_text": "Consensus. /kənˈsen.səs/. The committee reached a consensus.",
            "level": 4,
        },
        "immutable": {
            "definition": "不可变的，永恒的",
            "example": "Blockchain records are immutable once added to the chain.",
            "example_cn": "区块链记录一旦添加到链上就不可更改。",
            "etymology": "拉丁语 'in' (不) + 'mutare' (改变)",
            "chinese_mnemonic": "联想：'一木土' → 一块木头埋在土里，永远不变！",
            "pronunciation": "ɪmjuː.tə.bəl",
            "story": "immutable 就是'永远不变'的意思。区块链的神奇之处就在于，一旦数据写进去，就像刻在石头上一样，永远改不了！这就是为什么它这么安全~",
            "voice_text": "Immutable. /ɪmjuː.tə.bəl/. Blockchain records are immutable.",
            "level": 4,
        },
        "tokenomics": {
            "definition": "代币经济学",
            "example": "Good tokenomics is crucial for a successful crypto project.",
            "example_cn": "好的代币经济学对成功的加密项目至关重要。",
            "etymology": "token + economics",
            "chinese_mnemonic": "谐音：'偷啃我米克斯' → 偷啃我的米 (代币) 还要学经济！",
            "pronunciation": "ˌtəʊ.kəˈnɒm.ɪks",
            "story": "tokenomics 是 token 和 economics 的组合词，就是研究代币怎么发行、怎么分配、怎么增值的学问。一个好的项目，tokenomics 设计得好，大家都有钱赚！",
            "voice_text": "Tokenomics. /ˌtəʊ.kəˈnɒm.ɪks/. Good tokenomics is crucial for success.",
            "level": 4,
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
            "level": 4,
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
            "morning_greeting_enabled": True,
            "night_greeting_enabled": True,
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
    """获取用户英语水平，返回 (label, emoji, level_num)"""
    user = get_user_data(user_id)
    code = user.get("english_level")
    if code and code in ENGLISH_LEVELS:
        return ENGLISH_LEVELS[code]["label"], ENGLISH_LEVELS[code]["emoji"], int(code)
    return None, None, 0

def set_level(user_id: int, code: str):
    """设置用户英语水平"""
    user = get_user_data(user_id)
    user["english_level"] = code
    user["english_level_label"] = ENGLISH_LEVELS[code]["label"]
    save_user_data(user_id, user)

def get_vocabulary_by_level(level: int) -> Dict:
    """根据英语水平获取词汇"""
    if level <= 1:
        theme = "beginner"
    elif level == 2:
        theme = "elementary"
    elif level == 3:
        theme = "intermediate"
    else:
        theme = "advanced"
    
    if theme in VOCABULARY_DB:
        words = list(VOCABULARY_DB[theme].keys())
        word = random.choice(words)
        return {"word": word, "theme": theme, "data": VOCABULARY_DB[theme][word]}
    else:
        # 默认返回中级词汇
        return generate_daily_vocabulary()

def generate_daily_vocabulary(level: int = None) -> Dict:
    """生成每日词汇（兼容旧版）"""
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
async def send_voice_with_text(update: Update, text: str, voice_text: str = None):
    """发送语音 + 文字（同步发送）"""
    if not VOICE_ENABLED:
        await update.message.reply_text(text)
        return
    
    try:
        # 实际部署时集成 TTS API（如 ElevenLabs、Azure TTS）
        # 简化版：发送文字提示，语音功能可扩展
        voice_hint = f"🎙️ *【Alpha 语音】* \n\n_{voice_text or text}_"
        await update.message.reply_text(text, parse_mode="Markdown")
        # await update.message.reply_voice(voice_file)  # 实际 TTS 集成时启用
    except Exception as e:
        logger.warning(f"语音发送失败：{e}")
        await update.message.reply_text(text)

# ============= 🌅🌙 定时问候任务 =============
async def morning_greeting(context: ContextTypes.DEFAULT_TYPE):
    """早安问候任务"""
    logger.info("执行早安问候任务...")
    
    for user_id, user in USER_DATA.items():
        if not user.get("morning_greeting_enabled", True):
            continue
        if not user.get("nickname"):
            continue
        
        nickname, emoji = get_nickname(user_id)
        greeting = random.choice(MORNING_GREETINGS)
        
        message = f"""
{emoji} **{nickname}，早安！** {get_random_emoji()}

{greeting}

📖 **Alpha 的小分享**：
你知道吗？英语里 "Good morning" 原本是指 "好的早晨"，但现在就是早安的意思~
就像中文说 "早上好"，都是希望对方有个美好的一天！

💬 **{nickname} 今天有什么计划呀？**
跟 Alpha 分享一下吧~ (✧ω✧)
        """
        
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.warning(f"发送早安问候失败 (user {user_id}): {e}")

async def night_greeting(context: ContextTypes.DEFAULT_TYPE):
    """晚安问候任务"""
    logger.info("执行晚安问候任务...")
    
    for user_id, user in USER_DATA.items():
        if not user.get("night_greeting_enabled", True):
            continue
        if not user.get("nickname"):
            continue
        
        nickname, emoji = get_nickname(user_id)
        greeting = random.choice(NIGHT_GREETINGS)
        
        message = f"""
{emoji} **{nickname}，晚安！** {get_random_emoji()}

{greeting}

📖 **睡前小知识**：
英语里 "Good night" 只能用于告别，不能用于问候哦~
就像中文的 "晚安"，只有睡觉前才说！

💬 **{nickname} 今天过得怎么样？**
有什么开心或想吐槽的事吗？Alpha 在听~ (´▽`ʃ♡ƪ)
        """
        
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.warning(f"发送晚安问候失败 (user {user_id}): {e}")

# ============= 🤖 命令处理 =============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令 - 显示称呼和英语水平选择"""
    user_id = update.effective_user.id
    user = get_user_data(user_id)
    
    # 检查是否已经设置过称呼和水平
    if user.get("nickname") and user.get("english_level"):
        nickname, emoji = get_nickname(user_id)
        level, level_emoji, _ = get_level(user_id)
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
/settings - 个人设置 ⚙️
/review - 智能复习 🔄
/mistakes - 查看错题本 📝
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
            keyboard.append([InlineKeyboardButton(f"{info['emoji']} {info['label']} ({info['style']})", callback_data=f"nickname_{code}")])
        
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
                level, level_emoji, _ = get_level(user_id)
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

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /settings 命令 - 重新选择称呼和英语水平"""
    user_id = update.effective_user.id
    user = get_user_data(user_id)
    
    current_nickname, nick_emoji = get_nickname(user_id)
    current_level, level_emoji, _ = get_level(user_id)
    
    keyboard = [
        [InlineKeyboardButton("👑 修改称呼", callback_data="settings_nickname")],
        [InlineKeyboardButton("📊 修改英语水平", callback_data="settings_level")],
        [InlineKeyboardButton("🔙 返回", callback_data="settings_back")],
    ]
    
    message = f"""
⚙️ **个人设置** {get_random_emoji()}

👤 **当前称呼**：{nick_emoji} {current_nickname or '未设置'}
📖 **英语水平**：{level_emoji} {current_level or '未设置'}

请选择要修改的设置~
    """
    
    await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理设置回调"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    
    if data == "settings_nickname":
        keyboard = []
        for code, info in NICKNAME_OPTIONS.items():
            keyboard.append([InlineKeyboardButton(f"{info['emoji']} {info['label']}", callback_data=f"nickname_{code}")])
        await query.edit_message_text("👑 **选择新称呼**\n\n请选择一个你喜欢的称呼~", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "settings_level":
        keyboard = []
        for code, info in ENGLISH_LEVELS.items():
            keyboard.append([InlineKeyboardButton(f"{info['emoji']} {info['label']}", callback_data=f"level_{code}")])
        await query.edit_message_text("📊 **选择英语水平**\n\n请选择你的英语水平~", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "settings_back":
        await settings_command(update, context)

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
    level, level_emoji, level_num = get_level(user_id)
    
    # 根据水平获取词汇
    vocab = get_vocabulary_by_level(level_num)
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
    
    # 发送文字 + 语音（同步）
    await send_voice_with_text(update, message, data.get("voice_text", f"{word}. {data['example']}"))

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /quiz 命令 - 小测验"""
    user_id = update.effective_user.id
    user = get_user_data(user_id)
    
    if not user.get("nickname"):
        await update.message.reply_text("🤔 先完成设置吧！输入 /start 开始~")
        return
    
    _, _, level_num = get_level(user_id)
    vocab = get_vocabulary_by_level(level_num)
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
    
    elif data.startswith("nickname_"):
        await nickname_handler(update, context)
    
    elif data.startswith("level_"):
        await level_handler(update, context)
    
    elif data.startswith("step_"):
        await query.answer("请继续选择下方选项~")
    
    elif data.startswith("settings_"):
        await settings_callback(update, context)

async def review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /review 命令 - 智能复习"""
    user_id = update.effective_user.id
    user = get_user_data(user_id)
    
    if not user.get("nickname"):
        await update.message.reply_text("🤔 先完成设置吧！输入 /start 开始~")
        return
    
    nickname, nick_emoji = get_nickname(user_id)
    
    if user["mastered_words"]:
        review_words = random.sample(user["mastered_words"], min(3, len(user["mastered_words"])))
        message = f"""
{nick_emoji} **{nickname}，复习时间到**！ {get_random_emoji()}

📚 **今日复习单词**：
"""
        for word in review_words:
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
    level, level_emoji, _ = get_level(user_id)
    
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

**⚙️ 个人设置**：
/settings - 个人设置（称呼 + 英语水平）
/nickname - 修改称呼
/level - 修改英语水平

**📊 学习统计**：
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
    logger.info(f"🕐 时区：{TIMEZONE}")
    
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
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(CommandHandler("nickname", nickname_command))
    application.add_handler(CommandHandler("level", level_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # 设置定时任务（早安 8 点，晚安 20 点，北京时间）
    job_queue = application.job_queue
    
    # 早安问候 - 每天 8:00 (UTC+8)
    job_queue.run_daily(morning_greeting, time=datetime.strptime("00:00", "%H:%M").time(), name="morning_greeting")
    logger.info("⏰ 早安问候任务已设置（每天 8:00 北京时间）")
    
    # 晚安问候 - 每天 20:00 (UTC+8)
    job_queue.run_daily(night_greeting, time=datetime.strptime("12:00", "%H:%M").time(), name="night_greeting")
    logger.info("⏰ 晚安问候任务已设置（每天 20:00 北京时间）")
    
    # 启动机器人
    logger.info("✅ Alpha bot initialized! Waiting for messages...")
    logger.info(f"🎨 人设：{ALPHA_PERSONA['name']} - {ALPHA_PERSONA['personality']}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
