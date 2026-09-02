"""
(©) CodeXBotz — modernized for Python 3.12+

Central bot configuration, loaded once from environment variables into a
frozen, type-hinted `Settings` object. Import `settings` anywhere you need
a config value, e.g.:

    from config import settings
    await client.send_message(settings.owner_id, "hi")

`LOGGER` is kept as a module-level function, and the old ALL_CAPS names
(`CHANNEL_ID`, `ADMINS`, ...) are still exported, so every existing plugin
that does `from config import CHANNEL_ID, ADMINS` keeps working untouched.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from logging.handlers import RotatingFileHandler
from pathlib import Path


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def _env_int(name: str, default: str = "0") -> int:
    return int(_env(name, default))


def _env_bool(name: str, default: bool = False) -> bool:
    return _env(name, str(default)) == "True"


def _env_id_list(name: str) -> list[int]:
    raw = _env(name)
    if not raw:
        return []
    try:
        return [int(x) for x in raw.split()]
    except ValueError as exc:
        raise ValueError(f"{name} must contain only whitespace-separated integers") from exc


@dataclass(frozen=True, slots=True)
class Settings:
    """Immutable snapshot of the bot's runtime configuration."""

    # --- Telegram / Pyrogram credentials -----------------------------
    tg_bot_token: str = field(default_factory=lambda: _env("TG_BOT_TOKEN"))
    app_id: int = field(default_factory=lambda: _env_int("APP_ID"))
    api_hash: str = field(default_factory=lambda: _env("API_HASH"))
    bot_username: str = field(default_factory=lambda: _env("BOT_USERNM"))
    bot_workers: int = field(default_factory=lambda: _env_int("TG_BOT_WORKERS", "4"))

    # --- Storage / channels -----------------------------------------
    channel_id: int = field(default_factory=lambda: _env_int("CHANNEL_ID"))
    force_sub_channel: int = field(default_factory=lambda: _env_int("FORCE_SUB_CHANNEL", "0"))

    # --- Owner / admins ------------------------------------------------
    owner_id: int = field(default_factory=lambda: _env_int("OWNER_ID"))
    admins: list[int] = field(default_factory=lambda: _env_id_list("ADMINS"))

    # --- Web server --------------------------------------------------
    port: int = field(default_factory=lambda: _env_int("PORT", "8080"))

    # --- Database ------------------------------------------------------
    db_uri: str = field(default_factory=lambda: _env("DATABASE_URL"))
    db_name: str = field(default_factory=lambda: _env("DATABASE_NAME", "filesharexbot"))

    # --- Extra services --------------------------------------------------
    gemini_api_key: str = field(default_factory=lambda: _env("GEMINI"))

    # --- Copy / behaviour --------------------------------------------------
    start_msg: str = field(
        default_factory=lambda: _env(
            "START_MESSAGE",
            "Hello {first}\n\nI can store private files in Specified Channel "
            "and other users can access it from special link.",
        )
    )
    force_msg: str = field(
        default_factory=lambda: _env(
            "FORCE_SUB_MESSAGE",
            "Hello {first}\n\n<b>You need to join in my Channel/Group to use me\n\n"
            "Kindly Please join Channel</b>",
        )
    )
    custom_caption: str | None = field(default_factory=lambda: _env("CUSTOM_CAPTION") or None)
    protect_content: bool = field(default_factory=lambda: _env_bool("PROTECT_CONTENT"))
    disable_channel_button: bool = field(default_factory=lambda: _env_bool("DISABLE_CHANNEL_BUTTON"))

    bot_stats_text: str = "<b>BOT UPTIME</b>\n{uptime}"
    user_reply_text: str = "❌Don't send me messages directly I'm only File Share bot!"

    log_file_name: str = "filesharingbot.txt"

    def __post_init__(self) -> None:
        # Legacy behaviour: owner and the hard-coded maintainer id are always admins.
        for extra_admin in (self.owner_id, 1250450587):
            if extra_admin not in self.admins:
                self.admins.append(extra_admin)


settings = Settings()

# ---------------------------------------------------------------------------
# Backwards-compatible module-level names, so `from config import CHANNEL_ID`
# style imports used throughout the older plugins keep working untouched.
# ---------------------------------------------------------------------------
TG_BOT_TOKEN = settings.tg_bot_token
GEMINI = settings.gemini_api_key
BOT_USERNM = settings.bot_username
APP_ID = settings.app_id
API_HASH = settings.api_hash
CHANNEL_ID = settings.channel_id
OWNER_ID = settings.owner_id
PORT = settings.port
DB_URI = settings.db_uri
DB_NAME = settings.db_name
FORCE_SUB_CHANNEL = settings.force_sub_channel
TG_BOT_WORKERS = settings.bot_workers
START_MSG = settings.start_msg
ADMINS = settings.admins
FORCE_MSG = settings.force_msg
CUSTOM_CAPTION = settings.custom_caption
PROTECT_CONTENT = settings.protect_content
DISABLE_CHANNEL_BUTTON = settings.disable_channel_button
BOT_STATS_TEXT = settings.bot_stats_text
USER_REPLY_TEXT = settings.user_reply_text
LOG_FILE_NAME = settings.log_file_name


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
        handlers=[
            RotatingFileHandler(
                Path(settings.log_file_name),
                maxBytes=50_000_000,
                backupCount=10,
            ),
            logging.StreamHandler(),
        ],
    )
    logging.getLogger("pyrogram").setLevel(logging.WARNING)


_configure_logging()


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
