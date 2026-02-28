#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌟 AlphaSpeak - 美语陪练阿尔法 🌟
English Learning Bot with Alpha Persona
阳光开朗的美语少年伙伴，像邻居家的大哥哥一样亲切~
"""

import os
import json
import random
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List
import hashlib
import hmac

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
    "噔噔噔噔~ Alpha 闪亮登场！🌟 今天也要一起学习进步哦！",
]

CONTINUE_GREETINGS = [
    "欢迎回来！(｡•̀ᴗ-)✧ 今天继续我们的英语冒险吧！",
    "又见面啦！٩ (๑>◡<๑)۶ 今天也要加油学习哦！",
    "嘿！学习小达人！💪 今天想挑战什么？",
    "Alpha 想你啦~ (✧ω✧) 快来继续学习吧！",
]

# ============= 📚 增强版词汇库 =============
VOCABULARY_DB = {
    "business": {
        "leverage": {
            "definition": "利用（资源、优势等）",
            "example": "We can leverage our existing customer base to launch new products.",
            "etymology": "来自拉丁语 'levare' (举起)，原意是用杠杆撬动重物，现在引申为'利用优势'",
            "chinese_mnemonic": "联想：'leave' + 'rage' → 留下愤怒的力量来撬动成功！",
            "pronunciation": "ˈliː.vər.ɪdʒ",
            "story": "想象一下，阿基米德说过'给我一个支点，我能撬动地球'。leverage 就是这个'撬动'的力量！在商界，就是用现有的资源去撬动更大的成功~",
            "fun_fact": "在华尔街，leverage 也指'杠杆交易'，就是用借来的钱赚钱，刺激吧？",
            "difficulty": "intermediate"
        },
        "synergy": {
            "definition": "协同效应，合力",
            "example": "The merger created synergy between the two companies.",
            "etymology": "希腊语 'syn' (一起) + 'ergon' (工作) = 一起工作产生的额外效果",
            "chinese_mnemonic": "谐音：'新能量' → 新的合作产生新能量！",
            "pronunciation": "ˈsɪn.ə.dʒi",
            "story": "synergy 就像 1+1>2 的魔法！两个人合作，产生的效果比各自为战强很多。就像复联里的超级英雄们，单打独斗已经很厉害了，但组队就是无敌！",
            "fun_fact": "迪士尼收购皮克斯、漫威、卢卡斯影业，就是在创造 synergy 哦~",
            "difficulty": "advanced"
        },
        "paradigm": {
            "definition": "范式，模式",
            "example": "This technology represents a new paradigm in business.",
            "etymology": "希腊语 'para' (旁边) + 'deigma' (例子) = 旁边的例子作为参考模式",
            "chinese_mnemonic": "拆解：'para'(旁边) + 'dig'(挖) + 'm'(山) → 在旁边挖出新模式的山！",
            "pronunciation": "ˈpær.ə.daɪm",
            "story": "paradigm 就像一个'模板'或'样板'。当有人说'paradigm shift'(范式转变)，就是指整个游戏规则都变了！比如从功能机到智能机，就是 paradigm shift！",
            "fun_fact": "iPhone 的发布被称作手机行业的 paradigm shift，彻底改变了我们用手机的方式！",
            "difficulty": "advanced"
        }
    },
    "blockchain": {
        "consensus": {
            "definition": "共识机制",
            "example": "Proof of Stake is a consensus mechanism used by many blockchains.",
            "etymology": "拉丁语 'con' (一起) + 'sentire' (感觉) = 大家感觉一致",
            "chinese_mnemonic": "谐音：'肯死死' → 肯定要死死地达成共识！",
            "pronunciation": "kənˈsen.səs",
            "story": "consensus 就是一群人达成一致意见的过程。想象一下，你们班要决定去哪里春游，最后大家都同意去同一个地方，这就是 consensus！",
            "fun_fact": "比特币用的是 Proof of Work 共识机制，简单说就是'谁干活多谁说了算'，很公平吧？",
            "difficulty": "intermediate"
        },
        "immutable": {
            "definition": "不可变的",
            "example": "Blockchain records are immutable once added to the chain.",
            "etymology": "拉丁语 'in' (不) + 'mutare' (改变) = 不能改变",
            "chinese_mnemonic": "联想：'一木土' → 一块木头埋在土里，永远不变！",
            "pronunciation": "ɪˈmjuː.tə.bəl",
            "story": "immutable 就像刻在石头上的字，一旦刻上去就改不了了。区块链的魅力就在于此——数据一旦写入，就永远无法篡改！",
            "fun_fact": "比特币从 2009 年到现在，从来没有被成功篡改过，immutable 不是吹的！",
            "difficulty": "advanced"
        },
        "decentralized": {
            "definition": "去中心化的",
            "example": "Bitcoin is a decentralized cryptocurrency.",
            "etymology": "前缀 'de' (去除) + 'central' (中心) + 后缀 'ized' (使...化)",
            "chinese_mnemonic": "联想：'弟散他力' → 弟弟把权力分散给大家！",
            "pronunciation": "ˌdiːˈsen.trəl.aɪzd",
            "story": "decentralized 就是'没有老大'的意思。传统的银行有央行管着，但比特币没有中央机构，每个人都是节点，大家一起维护，酷吧？",
            "fun_fact": "比特币网络有上万个节点分布在全球，就算一半节点挂了，网络照样运行，这就是去中心化的力量！",
            "difficulty": "intermediate"
        }
    },
    "web3": {
        "interoperability": {
            "definition": "互操作性",
            "example": "Web3 aims for interoperability between different blockchain networks.",
            "etymology": "前缀 'inter' (相互) + 'operate' (操作) + 后缀 'ability' (能力)",
            "chinese_mnemonic": "拆解：'因特'(互联网) + 'operate'(操作) + 'ability'(能力) → 互联网操作能力！",
            "pronunciation": "ɪn.təˌrɒp.ər.əˈbɪl.ə.ti",
            "story": "interoperability 就是'互相能听懂对方说话'的能力。比如微信和 QQ 如果能互相发消息，就是有了 interoperability。Web3 的目标就是让不同的区块链能互相沟通！",
            "fun_fact": "现在的区块链就像一个个孤岛，interoperability 就是要在它们之间建桥，让资产和信息能自由流动！",
            "difficulty": "advanced"
        },
        "tokenomics": {
            "definition": "代币经济学",
            "example": "Good tokenomics is crucial for a successful crypto project.",
            "etymology": "token + economics = 代币的经济体系",
            "chinese_mnemonic": "谐音：'偷啃我米克斯' → 偷啃我的米 (代币) 还要学经济！",
            "pronunciation": "ˌtəʊ.kəˈnɒm.ɪks",
            "story": "tokenomics 就是一个代币的'经济设计'。比如总共发多少币？怎么分配？通胀还是通缩？好的 tokenomics 能让项目长久，差的可能很快就归零...",
            "fun_fact": "比特币的 tokenomics 设计得很精妙：总量 2100 万枚，每 4 年减半，这就是为什么它被称为'数字黄金'！",
            "difficulty": "intermediate"
        },
        "metaverse": {
            "definition": "元宇宙",
            "example": "Many companies are investing in the metaverse.",
            "etymology": "前缀 'meta' (超越) + 'universe' (宇宙) = 超越现实的宇宙",
            "chinese_mnemonic": "联想：'妹她佛斯' → 妹妹在虚拟世界里当佛祖！",
            "pronunciation": "ˈmet.ə.vɜːs",
            "story": "metaverse 就是一个虚拟的平行宇宙，你可以在里面工作、娱乐、社交。想象一下《头号玩家》里的'Oasis'，那就是 metaverse 的雏形！",
            "fun_fact": "Roblox、Decentraland、Sandbox 都是早期的 metaverse 尝试，有人在里面买虚拟土地赚了几百万美元！",
            "difficulty": "beginner"
        }
    }
}

# ============= 🏆 成就徽章系统 =============
ACHIEVEMENTS = {
    "first_blood": {"name": "首战告捷", "icon": "🎯", "desc": "第一次完成每日练习"},
    "week_streak": {"name": "坚持一周", "icon": "🔥", "desc": "连续学习 7 天"},
    "month_streak": {"name": "月度达人", "icon": "💎", "desc": "连续学习 30 天"},
    "vocab_master": {"name": "词汇大师", "icon": "📚", "desc": "学习 100 个单词"},
    "quiz_king": {"name": "测验之王", "icon": "👑", "desc": "连续答对 10 道题"},
    "pun_master": {"name": "谐音梗大王", "icon": "🎭", "desc": "收藏 10 个谐音梗"},
}

# ============= ❄️ 冷知识数据库 =============
COLD_FACTS = [
    "你知道吗？'goodbye' 其实是 'God be with ye' 的缩写，意思是'愿上帝与你同在'~",
    "英语里最长的单词是'pneumonoultramicroscopicsilicovolcanoconiosis'，一种肺病，共 45 个字母！",
    "'set' 是英语里意思最多的单词，有 430 多种不同的含义！",
    "莎士比亚发明了超过 1700 个英语单词，包括'eyeball'、'fashionable'、'lonely'等！",
    "英语是唯一一种月份名称和星期名称都来自罗马神话的语言！",
    "'queue' 是唯一一个去掉后面 4 个字母发音还是一样的单词！",
    "在英语中，'almost' 是唯一一个字母按字母表顺序排列的长单词！",
    "你知道吗？'nice' 在中世纪的意思是'愚蠢的'，后来才变成'好的'！",
]

# ============= 💾 用户数据存储 =============
USER_DATA = {}

def get_user_data(user_id: int) -> Dict:
    """获取用户数据"""
    if user_id not in USER_DATA:
        USER_DATA[user_id] = {
            "level": "CET-4",
            "daily_streak": 0,
            "last_practice": None,
            "total_words_learned": 0,
            "mastered_words": [],
            "weak_words": [],
            "favorites": [],
            "achievements": [],
            "mistakes": [],  # 错题本
            "learning_preference": "mixed",  # mixed/business/blockchain/web3
            "voice_enabled": True,
            "created_at": datetime.now().isoformat(),
        }
    return USER_DATA[user_id]

def save_user_data(user_id: int, data: Dict):
    """保存用户数据"""
    USER_DATA[user_id] = data

def check_streak(user_id: int) -> tuple:
    """检查学习连续天数"""
    user = get_user_data(user_id)
    last = user.get("last_practice")
    
    if not last:
        return 0, False
    
    last_date = datetime.fromisoformat(last).date()
    today = datetime.now().date()
    diff = (today - last_date).days
    
    if diff == 0:
        return user["daily_streak"], True  # 今天已经学过
    elif diff == 1:
        return user["daily_streak"], False  # 可以继续
    else:
        return 0, False  # 断了

def update_streak(user_id: int):
    """更新连续学习天数"""
    user = get_user_data(user_id)
    streak, practiced = check_streak(user_id)
    
    if not practiced:
        user["daily_streak"] = streak + 1
    
    user["last_practice"] = datetime.now().isoformat()
    save_user_data(user_id, user)
    
    return user["daily_streak"]

def check_achievements(user_id: int) -> List:
    """检查并解锁成就"""
    user = get_user_data(user_id)
    new_achievements = []
    
    # 连续学习成就
    if user["daily_streak"] >= 7 and "week_streak" not in user["achievements"]:
        user["achievements"].append("week_streak")
        new_achievements.append(ACHIEVEMENTS["week_streak"])
    
    if user["daily_streak"] >= 30 and "month_streak" not in user["achievements"]:
        user["achievements"].append("month_streak")
        new_achievements.append(ACHIEVEMENTS["month_streak"])
    
    # 词汇学习成就
    if user["total_words_learned"] >= 100 and "vocab_master" not in user["achievements"]:
        user["achievements"].append("vocab_master")
        new_achievements.append(ACHIEVEMENTS["vocab_master"])
    
    save_user_data(user_id, user)
    return new_achievements

# ============= 🎤 TTS 语音生成 =============
def generate_tts_audio(text: str, user_id: int) -> str:
    """
    生成 TTS 语音（简化版，实际部署时调用 TTS API）
    返回语音文件的 URL 或路径
    """
    if not TTS_ENABLED:
        return None
    
    # 这里可以集成实际的 TTS 服务
    # 如：ElevenLabs, Google TTS, Azure TTS 等
    # 简化版本：返回一个标记，前端可以处理
    audio_hash = hashlib.md5(text.encode()).hexdigest()[:8]
    return f"audio_{user_id}_{audio_hash}.mp3"

# ============= 🎲 随机工具函数 =============
def get_random_greeting(is_returning: bool = False) -> str:
    """获取随机问候语"""
    if is_returning:
        return random.choice(CONTINUE_GREETINGS)
    return random.choice(GREETINGS)

def get_random_fact() -> str:
    """获取随机冷知识"""
    return random.choice(COLD_FACTS)

def get_random_emoji() -> str:
    """获取随机 emoji"""
    return random.choice(ALPHA_PERSONA["emojis"])

def get_random_kaomoji() -> str:
    """获取随机颜文字"""
    return random.choice(ALPHA_PERSONA["kaomoji"])

# ============= 🤖 Alpha 的命令处理函数 =============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    user_id = update.effective_user.id
    user = get_user_data(user_id)
    
    greeting = get_random_greeting()
    
    welcome_message = f"""
{greeting}

🎯 **关于 Alpha**：
我是你的美语小伙伴 Alpha，一个阳光开朗的美语少年~
我会用最接地气的方式帮你学好英语！

📚 **专为你定制**：
• 水平：{user['level']}
• 主题：商务/区块链/Web3
• 时间：每天 30 分钟
• 风格：幽默有趣 + 词源故事 + 谐音梗

🎮 **可用命令**：
/daily - 每日词汇练习 📖
/quiz - 单词小测验 🎯
/review - 智能复习 🔄
/mistakes - 查看错题本 📝
/streak - 连续学习天数 🔥
/stats - 学习数据统计 📊
/fav - 收藏单词 ⭐
/speak - 口语练习 🎤
/help - 帮助指南 ❓

💡 **小贴士**：
我会讲单词的历史故事，还有超好记的谐音梗哦~
准备好了吗？输入 /daily 开始今天的英语冒险吧！{get_random_kaomoji()}
    """
    
    await update.message.reply_text(welcome_message)

async def daily_vocabulary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /daily 命令 - 每日词汇练习"""
    user_id = update.effective_user.id
    user = get_user_data(user_id)
    
    # 检查是否已练习
    streak, practiced = check_streak(user_id)
    if practiced:
        messages = [
            f"🎉 哇！你今天已经学过啦！真是勤奋呢~ (✧ω✧)",
            f"💪 今天的学习任务已完成！要不要挑战一下/quiz？",
            f"✨ 太棒啦！今天就到这里吧，明天继续哦~",
        ]
        await update.message.reply_text(random.choice(messages))
        return
    
    # 生成词汇
    vocab = generate_daily_vocabulary()
    word = vocab["word"]
    data = vocab["data"]
    theme = vocab["theme"]
    
    # 更新用户数据
    user["total_words_learned"] += 1
    if word not in user["mastered_words"]:
        user["mastered_words"].append(word)
    save_user_data(user_id, user)
    
    # 更新 streak
    new_streak = update_streak(user_id)
    
    # 检查成就
    new_achievements = check_achievements(user_id)
    
    # 构建消息
    message = f"""
{get_random_emoji()} **今日词汇：{word.upper()}** {get_random_emoji()}
📍 **主题**：{theme.title()}

🎙️ *【Alpha 发音】: /{data['pronunciation']}/*

📝 **定义**：{data['definition']}
💬 **例句**：{data['example']}

🏛️ **词源故事**：
{data['story']}

🧠 **中文记忆法**：
{data['chinese_mnemonic']}

💡 **冷知识**：
{data.get('fun_fact', '学无止境，每天进步一点点！')}

🔥 **连续学习**：{new_streak} 天

🎯 **小挑战**：用这个单词造个句子发给我吧！
我会帮你纠正语法，还会给你发音建议哦~ {get_random_kaomoji()}
    """
    
    # 发送消息
    await update.message.reply_text(message)
    
    # 发送成就通知
    for achievement in new_achievements:
        achievement_msg = f"""
🏆 **解锁新成就！** 🏆
{achievement['icon']} {achievement['name']}
{achievement['desc']}

太厉害了！继续加油！(ง •̀_•́)ง
        """
        await update.message.reply_text(achievement_msg)
    
    # 随机发送冷知识
    if random.random() < 0.3:  # 30% 概率
        fact = get_random_fact()
        await update.message.reply_text(f"\n❄️ **英语冷知识**：{fact}\n")

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /quiz 命令 - 小测验"""
    vocab = generate_daily_vocabulary()
    word = vocab["word"]
    data = vocab["data"]
    
    # 创建选项
    all_words = []
    for theme_words in VOCABULARY_DB.values():
        all_words.extend(list(theme_words.keys()))
    
    wrong_options = random.sample([w for w in all_words if w != word], 3)
    options = [word] + wrong_options
    random.shuffle(options)
    
    question = f"""
{get_random_emoji()} **单词小测验** {get_random_emoji()}

🤔 '{data['definition']}' 对应哪个英文单词？

答对有惊喜哦~ (✧ω✧)
    """
    
    keyboard = []
    for i, option in enumerate(options):
        keyboard.append([InlineKeyboardButton(f"{chr(65+i)}. {option}", callback_data=f"quiz_{word}_{option}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(question, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理按钮回调"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data.startswith("quiz_"):
        parts = data.split("_")
        correct_word = parts[1]
        selected_word = parts[2]
        
        if selected_word == correct_word:
            responses = [
                "✅ 恭喜！答对了！🎉 你真是太棒了！(ง •̀_•́)ง",
                "✅ 太厉害了！这都能答对！✧ω✧",
                "✅ 正确！Alpha 为你骄傲！🌟",
                "✅ 哇塞！完全正确！继续保持！💪",
            ]
            response = random.choice(responses)
        else:
            responses = [
                f"❌ 差一点点！正确答案是：{correct_word}\n\n别灰心，继续加油！💪",
                f"❌ 哎呀，不对哦~ 正确答案是：{correct_word}\n\n下次一定行！(｡•̀ᴗ-)✧",
                f"❌ 嗯...不太对呢。正确答案：{correct_word}\n\n学习就是不断尝试的过程！📚",
            ]
            response = random.choice(responses)
            
            # 记录错题
            user_id = update.effective_user.id
            user = get_user_data(user_id)
            if correct_word not in user["weak_words"]:
                user["weak_words"].append(correct_word)
                save_user_data(user_id, user)
        
        await query.edit_message_text(response)

async def review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /review 命令 - 智能复习"""
    user_id = update.effective_user.id
    user = get_user_data(user_id)
    
    if not user["weak_words"]:
        await update.message.reply_text(f"🎉 太棒了！你还没有需要复习的薄弱词汇！\n\n继续保持哦~ {get_random_kaomoji()}")
        return
    
    # 从薄弱词汇中随机选择一个
    review_word = random.choice(user["weak_words"])
    
    # 查找单词详情
    word_data = None
    for theme_words in VOCABULARY_DB.values():
        if review_word in theme_words:
            word_data = theme_words[review_word]
            break
    
    if word_data:
        message = f"""
🔄 **智能复习时间** 🔄

📝 **复习单词**：{review_word.upper()}

📖 **定义**：{word_data['definition']}
💬 **例句**：{word_data['example']}

🧠 **记忆法**：{word_data['chinese_mnemonic']}

💪 再记一次，这次一定能记住！{get_random_kaomoji()}
        """
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("复习功能正在升级中，敬请期待~")

async def mistakes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /mistakes 命令 - 查看错题本"""
    user_id = update.effective_user.id
    user = get_user_data(user_id)
    
    if not user["weak_words"]:
        await update.message.reply_text(f"🎉 太棒了！你的错题本是空的！\n\n说明你学习很认真哦~ {get_random_kaomoji()}")
        return
    
    message = f"""
📝 **你的错题本** 📝

共有 {len(user['weak_words'])} 个需要复习的单词：

"""
    for i, word in enumerate(user["weak_words"][:10], 1):  # 只显示前 10 个
        message += f"{i}. {word}\n"
    
    if len(user["weak_words"]) > 10:
        message += f"... 还有 {len(user['weak_words']) - 10} 个"
    
    message += f"\n\n💡 使用 /review 命令开始复习吧！{get_random_kaomoji()}"
    
    await update.message.reply_text(message)

async def streak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /streak 命令 - 查看连续学习天数"""
    user_id = update.effective_user.id
    user = get_user_data(user_id)
    
    streak_count = user["daily_streak"]
    
    if streak_count == 0:
        message = f"""
🔥 **学习连续天数**：0 天

还没有开始学习哦~
今天就来开启你的学习之旅吧！{get_random_kaomoji()}
        """
    elif streak_count < 7:
        message = f"""
🔥 **学习连续天数**：{streak_count} 天

继续加油！再坚持 {7 - streak_count} 天就能解锁【坚持一周】成就啦！💪
        """
    elif streak_count < 30:
        message = f"""
🔥 **学习连续天数**：{streak_count} 天 🔥

太厉害了！已经解锁【坚持一周】成就！
再坚持 {30 - streak_count} 天就能解锁【月度达人】成就！💎
        """
    else:
        message = f"""
🔥 **学习连续天数**：{streak_count} 天 🔥🔥

学习大神！请收下我的膝盖！(✧ω✧)
你已经解锁了【坚持一周】和【月度达人】成就！
继续创造记录吧！🚀
        """
    
    await update.message.reply_text(message)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /stats 命令 - 学习数据统计"""
    user_id = update.effective_user.id
    user = get_user_data(user_id)
    
    message = f"""
📊 **学习数据统计** 📊

📚 **已学单词**：{user['total_words_learned']} 个
🔥 **连续学习**：{user['daily_streak']} 天
⭐ **收藏单词**：{len(user['favorites'])} 个
📝 **薄弱词汇**：{len(user['weak_words'])} 个
🏆 **解锁成就**：{len(user['achievements'])} 个

"""
    
    if user["achievements"]:
        message += "**已解锁成就**：\n"
        for ach_id in user["achievements"]:
            ach = ACHIEVEMENTS.get(ach_id, {})
            message += f"{ach.get('icon', '⭐')} {ach.get('name', '未知')}\n"
    
    message += f"\n继续加油，Alpha 一直陪着你！{get_random_kaomoji()}"
    
    await update.message.reply_text(message)

async def speak_practice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /speak 命令 - 口语练习"""
    scenarios = [
        {
            "title": "Web3 大会",
            "scenario": "You're at a Web3 conference and someone asks you: 'What do you think about the future of decentralized finance?'",
            "tips": ["decentralized (去中心化的)", "leverage (利用)", "paradigm (范式)"]
        },
        {
            "title": "商务会议",
            "scenario": "You're in a business meeting and need to explain: 'How can our company leverage blockchain technology?'",
            "tips": ["leverage (利用)", "synergy (协同效应)", "immutable (不可变的)"]
        },
        {
            "title": "投资人路演",
            "scenario": "You're pitching to investors: 'Why should you invest in our metaverse project?'",
            "tips": ["metaverse (元宇宙)", "tokenomics (代币经济学)", "interoperability (互操作性)"]
        }
    ]
    
    scenario = random.choice(scenarios)
    
    message = f"""
🎤 **口语练习时间**！🎤

📍 **场景**：{scenario['title']}

💬 **情境**：
{scenario['scenario']}

💡 **提示词汇**：
{', '.join(scenario['tips'])}

🎯 **要求**：
用英语回答，至少使用 2 个提示词汇。

🎙️ Alpha 会帮你：
✅ 纠正语法错误
✅ 改善发音建议
✅ 提供更地道的表达

开始吧！直接回复你的英语回答~ {get_random_kaomoji()}
    """
    
    await update.message.reply_text(message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /help 命令"""
    help_text = f"""
🆘 **Alpha 的帮助指南** 🆘

**📚 学习功能**：
• /daily - 每日词汇学习（含词源故事 + 谐音梗）
• /quiz - 单词小测验
• /review - 智能复习（基于遗忘曲线）
• /speak - 口语场景练习

**📊 进度追踪**：
• /streak - 连续学习天数
• /stats - 学习数据统计
• /mistakes - 查看错题本

**⭐ 个人功能**：
• /fav - 收藏单词到个人词库
• /achievements - 查看已解锁成就

**🎯 学习特色**：
✨ 美式发音指导
✨ 词源历史故事
✨ 中文谐音记忆
✨ 商务/区块链/Web3 主题
✨ 幽默有趣的互动

**💡 学习建议**：
1. 每天固定时间学习 30 分钟
2. 多用新学的单词造句
3. 不怕犯错，大胆开口说
4. 定期复习薄弱词汇

有任何问题随时找 Alpha！{get_random_kaomoji()}
    """
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理普通消息（用于口语练习回复等）"""
    user_id = update.effective_user.id
    text = update.message.text
    
    # 简单的回复逻辑（可以扩展为 AI 对话）
    responses = [
        f"说得不错哦！继续保持~ {get_random_kaomoji()}",
        "嗯嗯，我听懂了！要不要试试用今天学的单词？",
        "很好的尝试！语法基本正确，发音可以再练习一下~",
        f"太棒了！你的英语进步很快呢！{get_random_emoji()}",
    ]
    
    await update.message.reply_text(random.choice(responses))

# ============= 🌐 Webhook 处理 =============
@app.route('/webhook', methods=['POST'])
def webhook():
    """Telegram Webhook 处理"""
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        asyncio.run(application.process_update(update))
        return 'ok', 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return 'error', 500

@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({"status": "ok", "bot": "Alpha"}), 200

# ============= 🚀 应用初始化 =============
application = None

def post_init():
    """初始化应用"""
    global application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # 添加命令处理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("daily", daily_vocabulary))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CommandHandler("review", review))
    application.add_handler(CommandHandler("mistakes", mistakes))
    application.add_handler(CommandHandler("streak", streak))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("speak", speak_practice))
    application.add_handler(CommandHandler("help", help_command))
    
    # 添加回调处理器
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # 添加普通消息处理器
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Alpha bot initialized! 🌟")

if __name__ == "__main__":
    post_init()
    port = int(os.getenv('PORT', 8080))
    logger.info(f"Starting Alpha bot on port {port}...")
    app.run(host='0.0.0.0', port=port)