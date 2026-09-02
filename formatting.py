"""
formatting.py — modern Telegram formatting helpers, Python 3.12+

This bot talks to Telegram in HTML parse mode (see `bot.py`,
`self.set_parse_mode(ParseMode.HTML)`), so every helper here produces
Telegram's HTML-flavoured formatting: <b>, <i>, <u>, <s>, <spoiler>,
<code>, <pre>, <blockquote>, <blockquote expandable>, <tg-emoji>, <a>.

Import what you need in any plugin:

    from formatting import bold, spoiler, quote, code_block, link

    await message.reply(
        f"{bold('Result:')} {spoiler('the answer is 42')}\n"
        f"{quote('This part can be quoted separately.')}"
    )

Everything here is a pure string function — no Pyrogram objects required —
so it's easy to unit test and safe to reuse across every plugin file.
"""

from __future__ import annotations

from html import escape as _escape
from typing import Final

__all__ = [
    "bold",
    "italic",
    "underline",
    "strike",
    "spoiler",
    "code",
    "code_block",
    "quote",
    "expandable_quote",
    "link",
    "mention",
    "custom_emoji",
    "escape_html",
    "join_lines",
]


def escape_html(text: str) -> str:
    """Escape user-supplied text so it can't break HTML formatting or inject tags."""
    return _escape(str(text), quote=False)


def bold(text: str) -> str:
    return f"<b>{escape_html(text)}</b>"


def italic(text: str) -> str:
    return f"<i>{escape_html(text)}</i>"


def underline(text: str) -> str:
    return f"<u>{escape_html(text)}</u>"


def strike(text: str) -> str:
    return f"<s>{escape_html(text)}</s>"


def spoiler(text: str) -> str:
    """Telegram 'tap to reveal' spoiler formatting."""
    return f'<span class="tg-spoiler">{escape_html(text)}</span>'


def code(text: str) -> str:
    """Inline monospace code."""
    return f"<code>{escape_html(text)}</code>"


def code_block(text: str, language: str | None = None) -> str:
    """Multi-line code block, optionally with syntax highlighting language."""
    lang_attr = f' class="language-{escape_html(language)}"' if language else ""
    return f"<pre><code{lang_attr}>{escape_html(text)}</code></pre>"


def quote(text: str) -> str:
    """A collapsed-by-default blockquote (Bot API 7.x+)."""
    return f"<blockquote>{escape_html(text)}</blockquote>"


def expandable_quote(text: str) -> str:
    """A blockquote that starts collapsed with a 'show more' toggle."""
    return f"<blockquote expandable>{escape_html(text)}</blockquote>"


def link(text: str, url: str) -> str:
    return f'<a href="{escape_html(url)}">{escape_html(text)}</a>'


def mention(text: str, user_id: int) -> str:
    """Mention a user by id even if they have no @username."""
    return f'<a href="tg://user?id={user_id}">{escape_html(text)}</a>'


def custom_emoji(placeholder: str, emoji_id: int) -> str:
    """
    Render a premium custom emoji. `placeholder` should be a regular emoji
    that is shown as alt text on clients that don't support custom emoji.
    """
    return f'<tg-emoji emoji-id="{emoji_id}">{escape_html(placeholder)}</tg-emoji>'


_LINE_SEP: Final = "\n"


def join_lines(*parts: str) -> str:
    """Join already-formatted fragments into one message body, one per line."""
    return _LINE_SEP.join(parts)
