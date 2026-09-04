"""(©) Codexbotz — modernized for Python 3.12+"""

from __future__ import annotations

import asyncio

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot import Bot
from config import ADMINS, CHANNEL_ID, DISABLE_CHANNEL_BUTTON
from helper_func import encode

_RESERVED_COMMANDS = [
    "start", "users", "broadcast", "batch", "genlink", "stats",
    "lecture", "solution", "help", "books", "notes", "ask", "cancel", "index",
]


def _share_button(link: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔁 Share URL", url=f"https://telegram.me/share/url?url={link}")]]
    )


async def _build_share_link(client: Client, message_id: int) -> str:
    converted_id = message_id * abs(client.db_channel.id)
    base64_string = await encode(f"get-{converted_id}")
    return f"https://t.me/{client.username}?start={base64_string}"


@Bot.on_message(
    filters.private & filters.user(ADMINS) & ~filters.command(_RESERVED_COMMANDS)
)
async def channel_post(client: Client, message: Message) -> None:
    reply_text = await message.reply_text("Please Wait...!", quote=True)
    try:
        post_message = await message.copy(chat_id=client.db_channel.id, disable_notification=True)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        post_message = await message.copy(chat_id=client.db_channel.id, disable_notification=True)
    except Exception as e:
        print(e)
        await reply_text.edit_text("Something went Wrong..!")
        return

    link = await _build_share_link(client, post_message.id)
    reply_markup = _share_button(link)

    await reply_text.edit(
        f"<b>Here is your link</b>\n\n{link}",
        reply_markup=reply_markup,
        disable_web_page_preview=True,
    )

    if not DISABLE_CHANNEL_BUTTON:
        await post_message.edit_reply_markup(reply_markup)


@Bot.on_message(filters.channel & filters.incoming & filters.chat(CHANNEL_ID))
async def new_post(client: Client, message: Message) -> None:
    if DISABLE_CHANNEL_BUTTON:
        return

    link = await _build_share_link(client, message.id)
    reply_markup = _share_button(link)

    try:
        await message.edit_reply_markup(reply_markup)
    except Exception as e:
        print(e)
