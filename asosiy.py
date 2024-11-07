import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
from telegram.constants import ParseMode
import json

TOKEN = "644883206:AAEbI1MEJbxXeIjK46uOLOE8MQoWEEqX8ck"
ADMIN_ID = 179500319

group_ids = set()

async def load_groups():
    global group_ids
    try:
        with open('groups.json', 'r') as f:
            group_ids = set(json.load(f))
    except FileNotFoundError:
        group_ids = set()

async def save_groups():
    with open('groups.json', 'w') as f:
        json.dump(list(group_ids), f)

async def start(update: Update, context: CallbackContext):
    user_name = update.message.from_user.username
    welcome_message = f"Assalomu alaykum, {user_name}!"
    await update.message.reply_text(welcome_message)

async def delete_links(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        return
    if update.message.entities:
        for entity in update.message.entities:
            if entity.type == "url":
                await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
                break

async def post(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("Sizda bu buyruqni bajarish huquqi yo'q.")
        return
    post_text = " ".join(context.args)
    if not post_text:
        await update.message.reply_text("Iltimos, yuboriladigan matnni kiriting.")
        return
    for chat_id in group_ids:
        await context.bot.send_message(chat_id=chat_id, text=post_text, parse_mode=ParseMode.MARKDOWN)

async def track_group(update: Update, context: CallbackContext):
    if update.message:
        chat = update.message.chat
        if chat and chat.type in ["group", "supergroup"]:
            if chat.id not in group_ids:
                group_ids.add(chat.id)
                await save_groups()

async def stats(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("Sizda bu buyruqni bajarish huquqi yo'q.")
        return
    group_count = len(group_ids)
    total_members = 0
    for chat_id in group_ids:
        try:
            members_count = await context.bot.get_chat_members_count(chat_id)
            total_members += members_count
        except Exception as e:
            print(f"Guruh {chat_id} uchun a'zolar soni olinayotganda xato yuz berdi: {e}")
    await update.message.reply_text(
        f"Guruhlar soni: {group_count}\nBotdagi umumiy a'zolar soni: {total_members}"
    )

async def main():
    await load_groups()

    # ApplicationBuilder bilan to'g'ri ishga tushirish
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, delete_links))
    application.add_handler(CommandHandler("post", post))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, track_group))
    application.add_handler(CommandHandler("stats", stats))

    # Pollingni boshlash
    await application.run_polling()

# Asynchronous kodni ishlatish uchun to'g'ri event loopni boshqarish
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
