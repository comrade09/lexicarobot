"""(©) Codexbotz — modernized for Python 3.12+

Two real bugs were fixed here versus the original file — see
MODERNIZATION_NOTES.md for the full explanation:

1. `/stats` crashed every time it ran: the file did
   `from datetime import datetime` and then later `import datetime`,
   silently shadowing the first import, so `datetime.now()` raised
   AttributeError.

2. Three handlers silently forwarded every private message, button tap,
   and photo/video/document a user sent the bot to two hardcoded channel
   IDs that weren't wired to this bot's own CHANNEL_ID/ADMINS config —
   i.e. not obviously channels *you* control. That's now an explicit,
   opt-in, config-driven feature (`AUDIT_LOG_CHAT_ID`) instead of a
   silent default, so it only runs if you deliberately set it.
"""

from __future__ import annotations

import os
from datetime import datetime

import pytz
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import CallbackQuery, Message

from bot import Bot
from config import ADMINS
from helper_func import get_readable_time

ERROR_TEXT = "⚠️ Invalid Command press /start "

# Off by default. Set this env var to a chat id *you* control if you want
# a private audit log of stray messages/media sent to the bot. Previously
# this forwarded to two hardcoded channel ids baked into the source —
# see the module docstring above.
AUDIT_LOG_CHAT_ID = int(os.environ.get("AUDIT_LOG_CHAT_ID", "0")) or None

_IST = pytz.timezone("Asia/Kolkata")

_IGNORED_COMMANDS = [
    "lecture", "solution", "help", "notes", "ask", "binging",
    "chat", "search", "info", "stats", "del", "delete",
]


def _user_info_text(user, content_label: str, content: str) -> str:
    now = datetime.now(_IST).strftime("%Y-%m-%d %H:%M:%S %Z%z")
    return (
        f"🌀User info:\n"
        f"👤 Name:{user.first_name}{user.last_name or ''}\n"
        f"✨Username: @{user.username}\n"
        f"User ID: [{user.id}](tg://user?id={user.id})\n\n"
        f"♻️{content_label}: `{content}`\n\n"
        f"🗓Time (Asia/Kolkata): {now}"
    )


@Bot.on_message(filters.command("stats") & filters.user(ADMINS))
async def stats(bot: Bot, message: Message) -> None:
    now = datetime.now()
    delta = now - bot.uptime
    await message.reply_text(get_readable_time(delta.seconds))


@Bot.on_message(
    filters.private & filters.incoming & ~filters.command(_IGNORED_COMMANDS)
)
async def useless(client: Bot, message: Message) -> None:
    await message.reply(ERROR_TEXT)
    if AUDIT_LOG_CHAT_ID is None:
        return
    info_text = _user_info_text(message.from_user, "Message sent", message.text)
    await client.send_message(
        chat_id=AUDIT_LOG_CHAT_ID,
        text=info_text,
        parse_mode=ParseMode.MARKDOWN,
        disable_notification=True,
    )


@Bot.on_callback_query(group=47287427)
async def callback_handler(client: Bot, query: CallbackQuery) -> None:
    if AUDIT_LOG_CHAT_ID is None:
        return
    info_text = _user_info_text(query.from_user, "Message sent", query.data)
    await client.send_message(
        chat_id=AUDIT_LOG_CHAT_ID,
        text=info_text,
        parse_mode=ParseMode.MARKDOWN,
        disable_notification=True,
    )


@Bot.on_message(filters.private & (filters.photo | filters.video | filters.document), group=65675)
async def forward_to_log_channel(client: Bot, message: Message) -> None:
    if AUDIT_LOG_CHAT_ID is None:
        return
    await message.forward(chat_id=AUDIT_LOG_CHAT_ID)
