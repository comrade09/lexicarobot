"""(©) Codexbotz — modernized for Python 3.12+"""

from __future__ import annotations

import asyncio

import humanize
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot import Bot
from config import (
    ADMINS,
    CUSTOM_CAPTION,
    DISABLE_CHANNEL_BUTTON,
    FORCE_MSG,
    PROTECT_CONTENT,
)
from database.database import add_user, del_user, full_userbase, present_user
from formatting import bold, join_lines
from helper_func import decode, encode, get_messages, subscribed

FILE_AUTO_DELETE_SECONDS = 600
FILE_AUTO_DELETE_HUMAN = humanize.naturaldelta(FILE_AUTO_DELETE_SECONDS)

WELCOME_TEXT = 'Hey! {first} I am Physicsaholics Bot <a href="https://i.ibb.co/vCJrx4PN/x.jpg">.</a>'
WAIT_MSG = "<b>Processing ...</b>"
REPLY_ERROR = "<code>Use this command as a reply to any telegram message without any spaces.</code>"


def _greeting_kwargs(message: Message) -> dict:
    user = message.from_user
    return {
        "first": user.first_name,
        "last": user.last_name,
        "username": None if not user.username else f"@{user.username}",
        "mention": user.mention,
        "id": user.id,
    }


def _resolve_requested_ids(argument: list[str], db_channel_id: int) -> list[int] | None:
    """Turn a decoded `get-<id>[-<id>]` payload into the real DB-channel message ids."""
    match len(argument):
        case 3:
            try:
                start = int(int(argument[1]) / abs(db_channel_id))
                end = int(int(argument[2]) / abs(db_channel_id))
            except (ValueError, ZeroDivisionError):
                return None
            if start <= end:
                return list(range(start, end + 1))
            return list(range(start, end - 1, -1))
        case 2:
            try:
                return [int(int(argument[1]) / abs(db_channel_id))]
            except (ValueError, ZeroDivisionError):
                return None
        case _:
            return None


@Bot.on_message(filters.command("start") & filters.private & subscribed)
async def start_command(client: Client, message: Message) -> None:
    user_id = message.from_user.id
    if not await present_user(user_id):
        try:
            await add_user(user_id)
        except Exception:
            pass

    text = message.text
    if len(text) <= 7:
        await _send_welcome(message)
        return

    try:
        base64_string = text.split(" ", 1)[1]
    except IndexError:
        return

    string = await decode(base64_string)
    argument = string.split("-")
    ids = _resolve_requested_ids(argument, client.db_channel.id)
    if ids is None:
        return

    await _deliver_files(client, message, ids)


async def _send_welcome(message: Message) -> None:
    reply_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text="Menu", callback_data="help_cb")],
            [
                InlineKeyboardButton(text="Support ✨", url="https://t.me/voltaic_network"),
                InlineKeyboardButton(text="Updates 📡 ", url="https://t.me/voltaic_network"),
            ],
        ]
    )
    await message.reply_text(
        text=WELCOME_TEXT.format(**_greeting_kwargs(message)),
        reply_markup=reply_markup,
        disable_web_page_preview=False,
        quote=True,
    )


async def _deliver_files(client: Client, message: Message, ids: list[int]) -> None:
    temp_msg = await message.reply("Please Wait...")
    try:
        messages = await get_messages(client, ids)
    except Exception:
        await message.reply_text("Something Went Wrong..!")
        return
    await temp_msg.delete()

    sent_messages: list[Message] = []
    for msg in messages:
        if CUSTOM_CAPTION and msg.document:
            caption = CUSTOM_CAPTION.format(
                previouscaption="" if not msg.caption else msg.caption.html,
                filename=msg.document.file_name,
            )
        else:
            caption = "" if not msg.caption else msg.caption.html

        reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

        try:
            sent = await msg.copy(
                chat_id=message.from_user.id,
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
                protect_content=PROTECT_CONTENT,
            )
            sent_messages.append(sent)
        except FloodWait as e:
            await asyncio.sleep(e.x)
            sent = await msg.copy(
                chat_id=message.from_user.id,
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
                protect_content=PROTECT_CONTENT,
            )
            sent_messages.append(sent)
        except Exception:
            pass

    status = await client.send_message(
        chat_id=message.from_user.id,
        text=join_lines(
            f" {bold('DONE ✅')}",
            f"These files will auto-delete in {FILE_AUTO_DELETE_HUMAN} to save space.",
        ),
    )

    asyncio.create_task(delete_files(sent_messages, status))


async def delete_files(messages: list[Message], status_message: Message) -> None:
    """
    Wait FILE_AUTO_DELETE_SECONDS, then delete every message that was sent
    to the user and update the status message to say so.

    (This function previously didn't exist — it was called but never
    defined, so the auto-delete this bot has always advertised silently
    did nothing. See MODERNIZATION_NOTES.md.)
    """
    await asyncio.sleep(FILE_AUTO_DELETE_SECONDS)
    for msg in messages:
        try:
            await msg.delete()
        except Exception:
            pass
    try:
        await status_message.edit(
            f"<b>Your files have been auto-deleted</b> after {FILE_AUTO_DELETE_HUMAN}. "
            "Use the link again to resend them."
        )
    except Exception:
        pass


@Bot.on_message(filters.command("start") & filters.private)
async def not_joined(client: Client, message: Message) -> None:
    buttons = [[InlineKeyboardButton("Join Channel", url=client.invitelink)]]
    try:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Try Again",
                    url=f"https://t.me/{client.username}?start={message.command[1]}",
                )
            ]
        )
    except IndexError:
        pass

    await message.reply(
        text=FORCE_MSG.format(**_greeting_kwargs(message)),
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True,
        disable_web_page_preview=True,
    )


@Bot.on_message(filters.command("users") & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message) -> None:
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await full_userbase()
    await msg.edit(f"{len(users)} users are using this bot ")


@Bot.on_message(filters.private & filters.command("broadcast") & filters.user(ADMINS))
async def send_text(client: Bot, message: Message) -> None:
    if not message.reply_to_message:
        msg = await message.reply(REPLY_ERROR)
        await asyncio.sleep(8)
        await msg.delete()
        return

    query = await full_userbase()
    broadcast_msg = message.reply_to_message
    total = successful = blocked = deleted = unsuccessful = 0

    pls_wait = await message.reply("<i>Broadcasting Message.. This will Take Some Time</i>")
    for chat_id in query:
        try:
            await broadcast_msg.copy(chat_id)
            successful += 1
        except FloodWait as e:
            await asyncio.sleep(e.x)
            await broadcast_msg.copy(chat_id)
            successful += 1
        except UserIsBlocked:
            await del_user(chat_id)
            blocked += 1
        except InputUserDeactivated:
            await del_user(chat_id)
            deleted += 1
        except Exception:
            unsuccessful += 1
        total += 1

    status = f"""<b><u>Broadcast Completed</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""

    await pls_wait.edit(status)
