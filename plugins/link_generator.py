"""(©) Codexbotz — modernized for Python 3.12+"""

from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot import Bot
from config import ADMINS
from helper_func import encode, get_message_id

_ASK_FILTERS = filters.forwarded | (filters.text & ~filters.forwarded)
_NOT_FROM_DB_CHANNEL = (
    "❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel"
)


def _share_button(link: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔁 Share URL", url=f"https://telegram.me/share/url?url={link}")]]
    )


async def _ask_for_db_message(client: Client, message: Message, prompt: str) -> tuple[Message, int] | None:
    """Repeatedly ask the admin for a DB-channel forward/link until a valid one arrives."""
    while True:
        try:
            reply = await client.ask(
                text=prompt,
                chat_id=message.from_user.id,
                filters=_ASK_FILTERS,
                timeout=60,
            )
        except Exception:
            return None

        msg_id = await get_message_id(client, reply)
        if msg_id:
            return reply, msg_id

        await reply.reply(_NOT_FROM_DB_CHANNEL, quote=True)


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command("batch"))
async def batch(client: Client, message: Message) -> None:
    first = await _ask_for_db_message(
        client, message, "Forward the First Message from DB Channel (with Quotes)..\n\nor Send the DB Channel Post Link"
    )
    if first is None:
        return
    _first_message, f_msg_id = first

    second = await _ask_for_db_message(
        client, message, "Forward the Last Message from DB Channel (with Quotes)..\nor Send the DB Channel Post link"
    )
    if second is None:
        return
    second_message, s_msg_id = second

    string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    await second_message.reply_text(
        f"<b>Here is your link</b>\n\n{link}", quote=True, reply_markup=_share_button(link)
    )


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command("genlink"))
async def link_generator(client: Client, message: Message) -> None:
    result = await _ask_for_db_message(
        client, message, "Forward Message from the DB Channel (with Quotes)..\nor Send the DB Channel Post link"
    )
    if result is None:
        return
    channel_message, msg_id = result

    base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
    link = f"https://t.me/{client.username}?start={base64_string}"

    await channel_message.reply_text(
        f"<b>Here is your link</b>\n\n{link}", quote=True, reply_markup=_share_button(link)
    )
