import os
import re

from langdetect import DetectorFactory, LangDetectException, detect_langs
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters


URL_PATTERN = re.compile(r"(?:https?://|www\.)\S+", re.IGNORECASE)
MENTION_PATTERN = re.compile(r"(?<!\w)@[A-Za-z0-9_]{3,}")
WORD_PATTERN = re.compile(r"\b[\w']+\b", re.UNICODE)
MIN_LANGUAGE_WORDS = 4
MIN_LANGUAGE_LETTERS = 20
MIN_LANGUAGE_CONFIDENCE = 0.85

DetectorFactory.seed = 0


def contains_blocked_content(text: str | None) -> bool:
    if not text:
        return False
    return bool(URL_PATTERN.search(text) or MENTION_PATTERN.search(text))


def is_unsupported_language(text: str | None) -> bool:
    if not text:
        return False

    words = WORD_PATTERN.findall(text)
    if len(words) < MIN_LANGUAGE_WORDS:
        return False
    if sum(character.isalpha() for character in text) < MIN_LANGUAGE_LETTERS:
        return False

    try:
        detections = detect_langs(text)
    except LangDetectException:
        return False

    if not detections or detections[0].prob < MIN_LANGUAGE_CONFIDENCE:
        return False
    return detections[0].lang not in {"id", "en"}


async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    if not message or not user or not chat:
        return False

    admins = await context.bot.get_chat_administrators(chat.id)
    return any(admin.user.id == user.id for admin in admins)


async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    chat = update.effective_chat

    if not message or not chat or not message.new_chat_members:
        return

    for member in message.new_chat_members:
        welcome_message = (
            f"Selamat datang, {member.full_name}! "
            "Jangan lupa baca rules di deskripsi 😊"
        )
        await context.bot.send_message(chat_id=chat.id, text=welcome_message)


async def filter_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    chat = update.effective_chat

    if not message or not chat:
        return

    if await is_admin(update, context):
        return

    text = message.text or message.caption
    if message.forward_origin is None and not (
        contains_blocked_content(text) or is_unsupported_language(text)
    ):
        return

    await message.delete()
    await context.bot.send_message(
        chat_id=chat.id,
        text="Pesan forward, link, mention, atau bahasa selain Indonesia dan Inggris dihapus!",
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_message:
        await update.effective_message.reply_text("Halo! Saya siap membantu. 😊")


def build_application():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable is required")

    application = ApplicationBuilder().token(token).build()
    application.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome)
    )
    application.add_handler(
        MessageHandler(
            filters.ALL & filters.ChatType.GROUPS,
            filter_messages,
        ),
        group=1,
    )
    application.add_handler(CommandHandler("start", start))
    return application


def main() -> None:
    application = build_application()
    application.run_polling()


if __name__ == "__main__":
    main()
