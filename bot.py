import json
from telegram import Update, ChatJoinRequest
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ChatJoinRequestHandler,
    ContextTypes,
    filters
)

# === CONFIG ===
BOT_TOKEN = "7602943902:AAEkDWmYPfkNgaGTfjZk8o5tYXvFIS6icq8"   # <<== PUT your bot token here!
OWNER_ID = 727463982           # <<== Your Telegram ID

WELCOME_IMAGE = "banner.jpg"   # Local banner image file

WELCOME_CAPTION = """
🌟 *FOLLOW ME ON ALL PLATFORMS ❤️🥰*

👑 *TELEGRAM CHANNELS:*
➡️ [Channel 1](https://t.me/+iHAVF9tRyXhiN2Nl)
➡️ [Channel 2](https://t.me/JuvelCricketLifes)
➡️ [Channel 3](https://t.me/+sxLhMLRw1VkwNDVl)

🎬 *YOUTUBE CHANNELS:*
▶️ [Juvel Cricket Lifes](https://youtube.com/@juvelcricketlifes?si=tSwlCkQtxtzswllp)
▶️ [Juvel Cricket](https://youtube.com/@juvelcricket?si=7xkgRxHAxHu4VIof)
▶️ [Casino Paradoxin](https://youtube.com/@casinoparadoxin?si=Dwg0nqGhC7oqHPPE)

📸 *INSTAGRAM:*
✨ [Juvel Cricket Lifes](https://www.instagram.com/juvelcricketlifes)
✨ [Juvel Bhai Real](https://www.instagram.com/juvelbhaireal)

🔥 Stay connected & enjoy!
"""

# === STATE ===
accepting_requests = False

# === UTILS ===
def load_users():
    try:
        with open("approved_users.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_users(users):
    with open("approved_users.json", "w") as f:
        json.dump(users, f)

def load_pending():
    try:
        with open("pending_requests.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_pending(pending):
    with open("pending_requests.json", "w") as f:
        json.dump(pending, f)

# === HANDLERS ===

async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global accepting_requests
    request: ChatJoinRequest = update.chat_join_request
    user_id = request.from_user.id
    chat_id = request.chat.id

    if accepting_requests:
        await request.approve()
        approved_users = load_users()
        if user_id not in approved_users:
            approved_users.append(user_id)
            save_users(approved_users)

        try:
            await context.bot.send_photo(
                chat_id=user_id,
                photo=open(WELCOME_IMAGE, "rb"),
                caption=WELCOME_CAPTION,
                parse_mode=ParseMode.MARKDOWN
            )
            print(f"✅ Approved & welcomed {user_id}")
        except Exception as e:
            print(f"❌ Failed to send welcome to {user_id}: {e}")

    else:
        pending = load_pending()
        new_entry = {"user_id": user_id, "chat_id": chat_id}
        if new_entry not in pending:
            pending.append(new_entry)
            save_pending(pending)
        print(f"⏸️ Stored pending join request for {user_id}")

async def turn_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global accepting_requests
    if update.effective_user.id == OWNER_ID:
        accepting_requests = True
        await update.message.reply_text("✅ Auto-approve is ON.\nChecking stored pending requests...")

        pending = load_pending()
        approved_users = load_users()

        for entry in pending:
            user_id = entry["user_id"]
            chat_id = entry["chat_id"]

            try:
                await context.bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)

                if user_id not in approved_users:
                    approved_users.append(user_id)

                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=open(WELCOME_IMAGE, "rb"),
                    caption=WELCOME_CAPTION,
                    parse_mode=ParseMode.MARKDOWN
                )
                print(f"✅ Approved stored & welcomed {user_id}")

            except Exception as e:
                print(f"❌ Could not approve/send to {user_id}: {e}")

        save_users(approved_users)
        save_pending([])

    else:
        await update.message.reply_text("🚫 You’re not authorized.")

async def turn_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global accepting_requests
    if update.effective_user.id == OWNER_ID:
        accepting_requests = False
        await update.message.reply_text("🛑 Auto-approve is OFF.")
    else:
        await update.message.reply_text("🚫 You’re not authorized.")

async def bro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == OWNER_ID:
        if not context.args:
            await update.message.reply_text("⚠️ Use `/bro Your message`")
            return

        message = ' '.join(context.args)
        approved_users = load_users()
        success = 0
        failed = 0

        for user_id in approved_users:
            try:
                await context.bot.send_message(chat_id=user_id, text=message)
                success += 1
            except Exception as e:
                print(f"❌ Failed for {user_id}: {e}")
                failed += 1

        await update.message.reply_text(
            f"📢 Text broadcast done!\n✅ Sent: {success}\n❌ Failed: {failed}"
        )
    else:
        await update.message.reply_text("🚫 You’re not authorized.")

async def brophoto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == OWNER_ID:
        if not update.message.photo:
            await update.message.reply_text("⚠️ You must attach a photo with this command.")
            return

        if not update.message.caption or not update.message.caption.startswith('/brophoto'):
            await update.message.reply_text("⚠️ Use `/brophoto Your caption` in the *caption*, with the photo attached.")
            return

        caption = update.message.caption.replace('/brophoto', '', 1).strip()
        file_id = update.message.photo[-1].file_id

        approved_users = load_users()
        success = 0
        failed = 0

        for user_id in approved_users:
            try:
                await context.bot.send_photo(chat_id=user_id, photo=file_id, caption=caption)
                success += 1
            except Exception as e:
                print(f"❌ Failed for {user_id}: {e}")
                failed += 1

        await update.message.reply_text(
            f"📸 Photo broadcast done!\n✅ Sent: {success}\n❌ Failed: {failed}"
        )
    else:
        await update.message.reply_text("🚫 You’re not authorized.")

async def brovideo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == OWNER_ID:
        if not update.message.video:
            await update.message.reply_text("⚠️ You must attach a video with this command.")
            return

        if not update.message.caption or not update.message.caption.startswith('/brovideo'):
            await update.message.reply_text("⚠️ Use `/brovideo Your caption` in the *caption*, with the video attached.")
            return

        caption = update.message.caption.replace('/brovideo', '', 1).strip()
        file_id = update.message.video.file_id

        approved_users = load_users()
        success = 0
        failed = 0

        for user_id in approved_users:
            try:
                await context.bot.send_video(chat_id=user_id, video=file_id, caption=caption)
                success += 1
            except Exception as e:
                print(f"❌ Failed for {user_id}: {e}")
                failed += 1

        await update.message.reply_text(
            f"🎥 Video broadcast done!\n✅ Sent: {success}\n❌ Failed: {failed}"
        )
    else:
        await update.message.reply_text("🚫 You’re not authorized.")

# === MAIN ===

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(ChatJoinRequestHandler(handle_join_request))
    app.add_handler(CommandHandler("on", turn_on))
    app.add_handler(CommandHandler("off", turn_off))
    app.add_handler(CommandHandler("bro", bro))
    app.add_handler(MessageHandler(filters.PHOTO, brophoto))
    app.add_handler(MessageHandler(filters.VIDEO, brovideo))

    print("🚀 Bot is running with FULL AURA! Ctrl+C to stop.")
    await app.run_polling()

# === ENTRY POINT ===

if __name__ == "__main__":
    import sys
    import asyncio
    import nest_asyncio

    if sys.platform.startswith('win') and sys.version_info >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())
