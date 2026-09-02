"""(©) Codexbotz — modernized for Python 3.12+"""

from __future__ import annotations

import asyncio
import base64
import re
from typing import TYPE_CHECKING

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant

from config import ADMINS, FORCE_SUB_CHANNEL

if TYPE_CHECKING:
    from pyrogram import Client
    from pyrogram.types import Message

_LINK_PATTERN = re.compile(r"https://t\.me/(?:c/)?(.*)/(\d+)")
_MEMBER_STATUSES = frozenset(
    {ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER}
)


async def is_subscribed(_filter, client: Client, update: Message) -> bool:
    if not FORCE_SUB_CHANNEL:
        return True

    user_id = update.from_user.id
    if user_id in ADMINS:
        return True

    try:
        member = await client.get_chat_member(chat_id=FORCE_SUB_CHANNEL, user_id=user_id)
    except UserNotParticipant:
        return False

    return member.status in _MEMBER_STATUSES


async def encode(string: str) -> str:
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    return base64_bytes.decode("ascii").strip("=")


async def decode(base64_string: str) -> str:
    # Links generated before this commit have a trailing `=`, so strip and
    # re-pad to handle both old and new links.
    base64_string = base64_string.strip("=")
    padded = base64_string + "=" * (-len(base64_string) % 4)
    string_bytes = base64.urlsafe_b64decode(padded.encode("ascii"))
    return string_bytes.decode("ascii")


async def get_messages(client: Client, message_ids: list[int]) -> list[Message]:
    messages: list[Message] = []
    batch_size = 200

    for start in range(0, len(message_ids), batch_size):
        batch = message_ids[start : start + batch_size]
        try:
            msgs = await client.get_messages(chat_id=client.db_channel.id, message_ids=batch)
        except FloodWait as e:
            await asyncio.sleep(e.x)
            msgs = await client.get_messages(chat_id=client.db_channel.id, message_ids=batch)
        except Exception:
            continue
        messages.extend(msgs)

    return messages


async def get_message_id(client: Client, message: Message) -> int:
    if message.forward_from_chat:
        if message.forward_from_chat.id == client.db_channel.id:
            return message.forward_from_message_id
        return 0

    if message.forward_sender_name:
        return 0

    if not message.text:
        return 0

    match = _LINK_PATTERN.match(message.text)
    if not match:
        return 0

    channel_id, msg_id = match.group(1), int(match.group(2))

    if channel_id.isdigit():
        if f"-100{channel_id}" == str(client.db_channel.id):
            return msg_id
    elif channel_id == client.db_channel.username:
        return msg_id

    return 0


def get_readable_time(seconds: int) -> str:
    """Render a duration in seconds as e.g. '1days, 02h:03m:04s'."""
    if seconds == 0:
        return ""

    periods = [(60, "s"), (60, "m"), (24, "h"), (24, "days")]
    parts: list[str] = []
    remaining = seconds

    for divisor, suffix in periods:
        if remaining == 0:
            break
        remaining, displayed = divmod(remaining, divisor)
        parts.append(f"{displayed}{suffix}")

    if len(parts) == 4:
        days = parts.pop()
        parts.reverse()
        return f"{days}, " + ":".join(parts)

    parts.reverse()
    return ":".join(parts)


subscribed = filters.create(is_subscribed)
