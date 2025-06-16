from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from apscheduler.schedulers.background import BackgroundScheduler
from telegram.ext import MessageHandler
from telegram.ext import filters
import random
from telegram.ext import ConversationHandler
from report import generate_report
from weekly_report import generate_weekly_report
FEEDBACK = range(1)
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
import sqlite3
print("бот запущено")
HR_PASSWORD = "4567"  
HR_ACCESS = {}  


USERNAME, MOOD, COMMENT = range(3)
POSITIVE = ['energetic', 'calm', 'super', 'wonderful', 'cool', 'awesome', 'high', 'good', 'everything is super', 'everything is wonderful']
NEGATIVE = ['anxious', 'depressed', 'bad', 'not very good', 'it is difficult for me', 'it is hard for me', 'I am stressed', 'I am tired']
NEUTRAL = ['okay', 'ok', 'so so']
THANK_YOU_KEYWORDS = ['Thank you', 'Bye', 'have a good day']
NO_COMMENT_KEYWORDS = ['no', 'do not want', 'no need']


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Let's collect your daily feedback. What is your name? If you want, you can write a nickname and remain anonymous.")
    return USERNAME

async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['username'] = update.message.text
    await update.message.reply_text("How are you feeling today??")
    return MOOD

from nlp_units import classify_comment
async def get_mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    mood, confidence = classify_comment(user_text)
    context.user_data['mood'] = mood

    if mood == 'Позитивно':
        await update.message.reply_text("Glad to hear it! Would you like to leave a comment?")
    elif mood == 'Негативно':
        await update.message.reply_text("I'm sorry to hear that. Would you like to leave a comment to contact HR?")
    else:
        await update.message.reply_text("Understood. Perhaps you would like to leave a comment.?")

    return COMMENT

from datetime import datetime 
async def get_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    comment = update.message.text
    username = context.user_data.get('username', 'anon')
    mood = context.user_data.get('mood', 'не визначено')

    if comment.lower() in ['no', 'do not want', 'no thanks']:
        await update.message.reply_text("Thanks anyway!")
        return ConversationHandler.END

    if comment.lower() in ['yes', 'sure', 'ok']:
        await update.message.reply_text("What would you like to share?")
        return COMMENT  
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO feedback (username, mood, comment, timestamp) VALUES (?, ?, ?, ?)",
              (username, mood, comment, datetime.now()))
    conn.commit()
    conn.close()

    await update.message.reply_text("Thanks! Your feedback has been saved.")
    return ConversationHandler.END 

async def respond_to_keywords(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower()

    bye_keywords = ['thanks', 'bye']

    if any(word in text for word in bye_keywords):
        await update.message.reply_text("See you soon! Have a nice day!!")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Скасовано.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END





#WEEKLY

WEEKLY_USERNAME, WEEKLY_FEEDBACK, TEAM_CONFLICT, SUPPORT, SUPPORT_DETAIL, WEEKLY_COMMENT, WEEKLY_COMMENT_TEXT = range(7)

async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Let's start our weekly poll. What is your name?")
    return WEEKLY_USERNAME

async def get_weekly_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['username'] = update.message.text.strip()
    await update.message.reply_text("How was your week??")
    return WEEKLY_FEEDBACK

async def get_weekly_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['weekly_feedback'] = update.message.text.strip()
    await update.message.reply_text("Were there any conflicts within the team? (yes/no)")
    return TEAM_CONFLICT

async def get_conflict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['conflict'] = update.message.text.lower().strip()
    await update.message.reply_text("Do you need any support? (yes/no)")
    return SUPPORT

async def get_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower().strip()
    context.user_data['support'] = text
    if text == 'так':
        await update.message.reply_text("Write down the way you feel, and I'll pass it on to HR.")
        return SUPPORT_DETAIL
    else:
        await update.message.reply_text("Would you like to add anything else? (comment)")
        return WEEKLY_COMMENT

async def get_support_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):   
    context.user_data['support_detail'] = update.message.text.strip()
    await update.message.reply_text("Thank you. Would you like to add anything else? (comment)")
    return WEEKLY_COMMENT

async def get_weekly_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.lower().strip()
    if user_input in ["no", "do not want", "no thanks"]:
        context.user_data["comment"] = ""
        await update.message.reply_text("Great, see you then!")
        await save_weekly_data(context)
        return ConversationHandler.END
    else:
        await update.message.reply_text("Please write your comment:")
        return WEEKLY_COMMENT_TEXT

async def save_weekly_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    context.user_data["comment"] = text
    await save_weekly_data(context)
    await update.message.reply_text("Thank you, see you soon!")
    return ConversationHandler.END

async def save_weekly_data(context):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute('''
        INSERT INTO weekly_feedback (username, weekly_feedback, conflict, support, support_detail, comment)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        context.user_data.get("username", "anon"),
        context.user_data.get("weekly_feedback", ""),
        context.user_data.get("conflict", ""),
        context.user_data.get("support", ""),
        context.user_data.get("support_detail", ""),
        context.user_data.get("comment", "")
    ))
    conn.commit()
    conn.close()


# HR dashboard

async def request_hr_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Enter your password to access the HR report:")
    return "CHECK_PASSWORD"
    
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler 
async def check_hr_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == HR_PASSWORD:
        user_id = update.effective_user.id
        HR_ACCESS[user_id] = True

        keyboard = [
            [InlineKeyboardButton("Daily report", callback_data="daily_report")],
            [InlineKeyboardButton("Weekly report", callback_data="weekly_report")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Access granted. Select report type:", reply_markup=reply_markup)
        return ConversationHandler.END
    else:
        await update.message.reply_text("Невірний пароль. Спробуй ще раз або натисни /cancel.")
        return "CHECK_PASSWORD"
    
async def handle_report_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if not HR_ACCESS.get(user_id):
        await query.edit_message_text("У вас немає доступу до звітів.")
        return

    if query.data == "daily_report":
        await query.edit_message_text("Надсилаю щоденний звіт...")
        await send_daily_report(query, context)
    elif query.data == "weekly_report":
        await query.edit_message_text("Надсилаю щотижневий звіт...")
        await report(query, context)  

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT conflict FROM weekly_feedback")
    conflict_data = [row[0].lower() for row in c.fetchall()]
    yes_conflicts = conflict_data.count("так")
    no_conflicts = conflict_data.count("ні")

    c.execute("SELECT support FROM weekly_feedback")
    support_data = [row[0].lower() for row in c.fetchall()]
    yes_support = support_data.count("так")
    no_support = support_data.count("ні")

    c.execute("SELECT username, support_detail, comment FROM weekly_feedback")
    raw_comments = c.fetchall()
    conn.close()

    report_text = (
        "Щотижневий звіт:\n\n"
        "Конфлікти:\n"
        f"- Так: {yes_conflicts}\n"
        f"- Ні: {no_conflicts}\n\n"
        "Запити на підтримку:\n"
        f"- Так: {yes_support}\n"
        f"- Ні: {no_support}\n\n"
        "Коментарі:"
    )

    seen = set()
    for user, detail, comment in raw_comments:
        key = (user, detail.strip(), comment.strip())
        if key in seen or (not detail and not comment):
            continue
        seen.add(key)

        report_text += f"\n\n— {user}:"
        if detail:
            report_text += f"\n  Підтримка: {detail}"
        if comment:
            report_text += f"\n  Коментар: {comment}"

    await update.message.reply_text(report_text)

async def send_daily_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT mood FROM daily_feedback")
    mood_data = [row[0] for row in c.fetchall()]
    
    mood_counts = {
        "енергійно": mood_data.count("енергійно"),
        "спокійно": mood_data.count("спокійно"),
        "втомлено": mood_data.count("втомлено"),
        "напружено": mood_data.count("напружено")
    }

    c.execute("SELECT username, comment FROM daily_feedback WHERE comment != ''")
    comments = c.fetchall()

    conn.close()
    report_text = (
        "Daily feedback:\n\n"
        "Moods:\n"
        f"- Енергійно: {mood_counts['енергійно']}\n"
        f"- Спокійно: {mood_counts['спокійно']}\n"
        f"- Втомлено: {mood_counts['втомлено']}\n"
        f"- Напружено: {mood_counts['напружено']}\n\n"
        "Comments:"
    )

    for username, comment in comments:
        report_text += f"\n— {username}:\n{comment}"

    await update.message.reply_text(report_text, parse_mode='Markdown')


from dotenv import load_dotenv
import os
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_username)],
            MOOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_mood)],
            COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_comment)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )


    weekly_handler = ConversationHandler(
    entry_points=[CommandHandler("weekly", weekly)],
    states={
        WEEKLY_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_weekly_username)],
        WEEKLY_FEEDBACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_weekly_feedback)],
        TEAM_CONFLICT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_conflict)],
        SUPPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_support)],
        SUPPORT_DETAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_support_detail)],
        WEEKLY_COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_weekly_comment)],
        WEEKLY_COMMENT_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_weekly_comment)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

    hr_handler = ConversationHandler(
        entry_points=[CommandHandler("report", request_hr_password)],
        states={
     "CHECK_PASSWORD": [MessageHandler(filters.TEXT & ~filters.COMMAND, check_hr_password)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
    app.add_handler(conv_handler)
    app.add_handler(weekly_handler)
    app.add_handler(hr_handler)
    app.add_handler(CommandHandler("report", report))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'(?i)^(привіт|добр(ий|а)? (день|вечір|ранок))'), start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, respond_to_keywords))
    app.add_handler(CallbackQueryHandler(handle_report_choice)) 
    app.add_handler(CommandHandler("daily_pdf", generate_report))
    app.add_handler(CommandHandler("weekly_pdf", generate_weekly_report))
    app.run_polling()


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
