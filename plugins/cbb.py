"""(©) Codexbotz — modernized for Python 3.12+"""

from __future__ import annotations

from pyrogram.enums import ParseMode
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot import Bot
from database.database import full_userbase
from formatting import join_lines, link

CLOSE_BUTTON = InlineKeyboardMarkup([[InlineKeyboardButton("close", callback_data="close")]])
BACK_BUTTON = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="start_cb")]])


@Bot.on_callback_query(group=278)
async def features(client: Bot, query: CallbackQuery) -> None:
    if query.data != "features":
        return

    text = join_lines(
        f"🌱 I am developed by {link('Voltaic Network', 'https://t.me/Voltaic_Network')}",
        "📡 Hosted on Heroku",
    )
    await query.message.edit_text(
        text=text,
        disable_web_page_preview=True,
        reply_markup=CLOSE_BUTTON,
    )


@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery) -> None:
    match query.data:
        case "about":
            user_first_name = query.from_user.first_name
            users = await full_userbase()
            text = f"""
🪐**Hey there! `{user_first_name}`**

🌀**Current Users** : {len(users)} Users

☘️I'm here to make your Learning fun and easy!

Any issues or need help related to me? Come visit us in Support Chat @linklockernet

This Bot Is  Licensed Under The GNU (General Public License v3.0)
"""
            await query.message.edit_text(
                text=text,
                disable_web_page_preview=True,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=BACK_BUTTON,
            )

        case "close":
            await query.message.delete()
            try:
                await query.message.reply_to_message.delete()
            except Exception:
                pass
