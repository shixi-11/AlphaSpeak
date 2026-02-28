#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
English Learning Bot for Telegram
Focus: Business, Blockchain, Web3 vocabulary and speaking practice
Level: CET-4 equivalent
Style: Humorous, Chinese-friendly explanations with etymology and wordplay
"""

import os
import json
import random
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 机器人配置
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is required")

# 学习主题词汇库
VOCABULARY_DB = {
    "business": {
        "leverage": {
            "definition": "利用（资源、优势等）",
            "example": "We can leverage our existing customer base to launch new products.",
            "etymology": "来自拉丁语 'levare' (举起)，原意是用杠杆撬动重物，现在引申为'利用优势'",
            "chinese_mnemonic": "联想：'leave' + 'rage' → 留下愤怒的力量来撬动成功！",
            "pronunciation": "ˈliː.vər.ɪdʒ"
        },
        "synergy": {
            "definition": "协同效应，合力",
            "example": "The merger created synergy between the two companies.",
            "etymology": "希腊语 'syn' (一起) + 'ergon' (工作) = 一起工作产生的额外效果",
            "chinese_mnemonic": "谐音：'新能量' → 新的合作产生新能量！",
            "pronunciation": "ˈsɪn.ə.dʒi"
        },
        "paradigm": {
            "definition": "范式，模式",
            "example": "This technology represents a new paradigm in business.",
            "etymology": "希腊语 'para' (旁边) + 'deigma' (例子) = 旁边的例子作为参考模式",
            "chinese_mnemonic": "拆解：'para'(旁边) + 'dig'(挖) + 'm'(山) → 在旁边挖出新模式的山！",
            "pronunciation": "ˈpær.ə.daɪm"
        }
    },
    "blockchain": {
        "consensus": {
            "definition": "共识机制",
            "example": "Proof of Stake is a consensus mechanism used by many blockchains.",
            "etymology": "拉丁语 'con' (一起) + 'sentire' (感觉) = 大家感觉一致",
            "chinese_mnemonic": "谐音：'肯死死' → 肯定要死死地达成共识！",
            "pronunciation": "kənˈsen.səs"
        },
        "immutable": {
            "definition": "不可变的",
            "example": "Blockchain records are immutable once added to the chain.",
            "etymology": "拉丁语 'in' (不) + 'mutare' (改变) = 不能改变",
            "chinese_mnemonic": "拆解：'im'(不) + 'mutable'(可变) → 不可变，像石头一样硬！",
            "pronunciation": "ɪˈmjuː.tə.bəl"
        },
        "decentralized": {
            "definition": "去中心化的",
            "example": "Bitcoin is a decentralized cryptocurrency.",
            "etymology": "前缀 'de' (去除) + 'central' (中心) + 后缀 'ized' (使...化)",
            "chinese_mnemonic": "联想：'弟散他力' → 弟弟把权力分散给大家！",
            "pronunciation": "ˌdiːˈsen.trəl.aɪzd"
        }
    },
    "web3": {
        "interoperability": {
            "definition": "互操作性",
            "example": "Web3 aims for interoperability between different blockchain networks.",
            "etymology": "前缀 'inter' (相互) + 'operate' (操作) + 后缀 'ability' (能力)",
            "chinese_mnemonic": "拆解：'因特'(互联网) + 'operate'(操作) + 'ability'(能力) → 互联网操作能力！",
            "pronunciation": "ɪn.təˌrɒp.ər.əˈbɪl.ə.ti"
        },
        "tokenomics": {
            "definition": "代币经济学",
            "example": "Good tokenomics is crucial for a successful crypto project.",
            "etymology": "token + economics = 代币的经济体系",
            "chinese_mnemonic": "谐音：'偷啃我米克斯' → 偷啃我的米(代币)还要学经济！",
            "pronunciation": "ˌtəʊ.kəˈnɒm.ɪks"
        },
        "metaverse": {
            "definition": "元宇宙",
            "example": "Many companies are investing in the metaverse.",
            "etymology": "前缀 'meta' (超越) + 'universe' (宇宙) = 超越现实的宇宙",
            "chinese_mnemonic": "联想：'妹她佛斯' → 妹妹在虚拟世界里当佛祖！",
            "pronunciation": "ˈmet.ə.vɜːs"
        }
    }
}

# 用户学习进度数据库（简化版，实际部署时使用SQLite或PostgreSQL）
USER_PROGRESS = {}

def get_user_progress(user_id: int) -> Dict:
    """获取用户学习进度"""
    if user_id not in USER_PROGRESS:
        USER_PROGRESS[user_id] = {
            "level": "CET-4",
            "daily_streak": 0,
            "last_practice": None,
            "mastered_words": [],
            "weak_areas": [],
            "total_words_learned": 0,
            "practice_time_today": 0
        }
    return USER_PROGRESS[user_id]

def save_user_progress(user_id: int, progress: Dict):
    """保存用户学习进度"""
    USER_PROGRESS[user_id] = progress

def generate_daily_vocabulary(theme: str = None) -> Dict:
    """生成每日词汇练习"""
    if theme is None:
        themes = list(VOCABULARY_DB.keys())
        theme = random.choice(themes)
    
    words = list(VOCABULARY_DB[theme].keys())
    selected_word = random.choice(words)
    word_data = VOCABULARY_DB[theme][selected_word]
    
    return {
        "word": selected_word,
        "theme": theme,
        "data": word_data
    }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    welcome_message = """
🌟 欢迎使用美式英语训练营！我是您的英语教练 Coach AI 🌟

🎯 **专为您定制的学习计划**：
• 水平：大学四级
• 主题：商务/区块链/Web3
• 时间：每天30分钟
• 风格：幽默有趣 + 词源解析 + 中文谐音梗

📚 **可用命令**：
/daily - 获取今日词汇练习
/quiz - 开始小测验
/speak - 口语练习
/progress - 查看学习进度
/help - 查看帮助

💡 **小贴士**：我会用最接地气的中文帮您理解美式英语，还会讲单词的历史故事哦！

准备好了吗？输入 /daily 开始今天的英语冒险吧！🚀
    """
    await update.message.reply_text(welcome_message)

async def daily_vocabulary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /daily 命令 - 每日词汇练习"""
    user_id = update.effective_user.id
    progress = get_user_progress(user_id)
    
    # 检查是否已经练习过今天的内容
    today = datetime.now().date()
    if progress["last_practice"] == str(today):
        await update.message.reply_text("🎉 您今天已经完成练习啦！明天再来学习新内容吧～")
        return
    
    vocab = generate_daily_vocabulary()
    word = vocab["word"]
    data = vocab["data"]
    theme = vocab["theme"]
    
    # 构建详细的词汇解析消息
    message = f"""
🔥 **今日词汇：{word.upper()}** 🔥
📍 **主题**：{theme.title()}

🔤 **发音**：/{data['pronunciation']}/
📝 **定义**：{data['definition']}
💬 **例句**：{data['example']}

🏛️ **词源故事**：
{data['etymology']}

🧠 **中文记忆法**：
{data['chinese_mnemonic']}

🎯 **小练习**：试着用这个单词造个句子吧！
我会帮您纠正语法和发音哦～
    """
    
    # 更新用户进度
    progress["last_practice"] = str(today)
    progress["total_words_learned"] += 1
    save_user_progress(user_id, progress)
    
    await update.message.reply_text(message)

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /quiz 命令 - 小测验"""
    vocab = generate_daily_vocabulary()
    word = vocab["word"]
    data = vocab["data"]
    
    # 创建选择题选项
    all_words = []
    for theme_words in VOCABULARY_DB.values():
        all_words.extend(list(theme_words.keys()))
    
    # 随机选择3个干扰项
    wrong_options = random.sample([w for w in all_words if w != word], 3)
    options = [word] + wrong_options
    random.shuffle(options)
    
    question = f"🤔 **单词测验**：\n\n'{data['definition']}' 对应哪个英文单词？"
    
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
            response = "✅ 恭喜！答对了！🎉\n\n您真是太棒了！"
        else:
            response = f"❌ 差一点点！正确答案是：{correct_word}\n\n别灰心，继续加油！💪"
        
        await query.edit_message_text(response)

async def speak_practice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /speak 命令 - 口语练习"""
    message = """
🎤 **口语练习时间**！🎤

我会给您一个商务/区块链/Web3相关的场景，您需要用英语回答。

**今日场景**：
You're at a Web3 conference and someone asks you: 
"What do you think about the future of decentralized finance?"

💡 **提示**：可以使用我们学过的词汇，比如：
• decentralized (去中心化的)
• leverage (利用)
• paradigm (范式)

请用英语回复，我会帮您：
✅ 纠正语法错误
✅ 改善发音建议  
✅ 提供更地道的表达

开始吧！直接回复您的英语回答 👇
    """
    await update.message.reply_text(message)

async def progress_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /progress 命令 - 查看学习进度"""
    user_id = update.effective_user.id
    progress = get_user_progress(user_id)
    
    message = f"""
📊 **您的学习进度报告** 📊

🎯 **当前水平**：{progress['level']}
🔥 **连续学习天数**：{progress['daily_streak']} 天
📚 **已掌握词汇**：{progress['total_words_learned']} 个
⏰ **今日练习时间**：{progress['practice_time_today']} 分钟

{'🏆 **学习达人**！' if progress['daily_streak'] >= 7 else '💪 **继续加油**！'}

记住：每天30分钟，坚持就是胜利！
    """
    await update.message.reply_text(message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /help 命令"""
    help_text = """
🆘 **帮助指南** 🆘

**主要功能**：
• /daily - 每日词汇学习（含词源+谐音梗）
• /quiz - 单词小测验
• /speak - 口语场景练习
• /progress - 查看学习进度

**学习特色**：
✨ **美式发音**：纯正美语发音指导
✨ **词源解析**：每个单词的历史故事
✨ **中文谐音**：用中文帮您记忆
✨ **商务主题**：专注商务/区块链/Web3
✨ **幽默风格**：让学习变得有趣

**学习建议**：
1. 每天固定时间练习30分钟
2. 多用新学的单词造句
3. 不怕犯错，大胆开口说
4. 定期查看进度，保持动力

有任何问题随时告诉我！😊
    """
    await update.message.reply_text(help_text)

def main():
    """主函数"""
    # 创建应用
    application = Application.builder().token(BOT_TOKEN).build()
    
    # 添加处理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("daily", daily_vocabulary))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CommandHandler("speak", speak_practice))
    application.add_handler(CommandHandler("progress", progress_check))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # 启动机器人
    logger.info("English Learning Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
