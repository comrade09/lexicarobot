"""(©) Codexbotz — modernized for Python 3.12+"""

from __future__ import annotations

import sys
from datetime import datetime
from collections import defaultdict

import pyromod.listen  # noqa: F401  (patches Client with .listen())
from aiohttp import web
from pyrogram import Client
from pyrogram.enums import ParseMode

from config import (
    API_HASH,
    APP_ID,
    CHANNEL_ID,
    FORCE_SUB_CHANNEL,
    LOGGER,
    PORT,
    TG_BOT_TOKEN,
    TG_BOT_WORKERS,
)
from plugins.stream import web_server

BANNER = r"""
░█████╗░░█████╗░██████╗░███████╗██╗░░██╗██████╗░░█████╗░████████╗███████╗
██╔══██╗██╔══██╗██╔══██╗██╔════╝╚██╗██╔╝██╔══██╗██╔══██╗╚══██╔══╝╚════██║
██║░░╚═╝██║░░██║██║░░██║█████╗░░░╚███╔╝░██████╦╝██║░░██║░░░██║░░░░░███╔═╝
██║░░██╗██║░░██║██║░░██║██╔══╝░░░██╔██╗░██╔══██╗██║░░██║░░░██║░░░██╔══╝░░
╚█████╔╝╚█████╔╝██████╔╝███████╗██╔╝╚██╗██████╦╝╚█████╔╝░░░██║░░░███████╗
░╚════╝░░╚════╝░╚═════╝░╚══════╝╚═╝░░╚═╝╚═════╝░░╚════╝░░░░╚═╝░░░╚══════╝
"""


class Bot(Client):
    def __init__(self) -> None:
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN,
        )
        
        # --- PYROMOD KEYERROR FIX ---
        # A defaultdict automatically creates an empty list if Pyromod looks for a missing key.
        # This completely prevents the KeyError without needing to import Pyromod internals!
        self.listeners = defaultdict(list)
        # ----------------------------

        self.LOGGER = LOGGER
        self.uptime: datetime | None = None
        self.username: str | None = None
        self.invitelink: str | None = None

    async def start(self) -> None:
        await super().start()

        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        if FORCE_SUB_CHANNEL:
            await self._resolve_force_sub_link()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info(
            "%s\nBot Running..!\n\nCreated by https://t.me/CodeXBotz", BANNER
        )
        self.username = usr_bot_me.username

        await self._start_web_server()

    async def _resolve_force_sub_link(self) -> None:
        try:
            chat = await self.get_chat(FORCE_SUB_CHANNEL)
            link = chat.invite_link or await self.export_chat_invite_link(FORCE_SUB_CHANNEL)
            self.invitelink = link
        except Exception as exc:
            self.LOGGER(__name__).warning(exc)
            sys.exit(1)

    async def _start_web_server(self) -> None:
        app_runner = web.AppRunner(await web_server(self))
        await app_runner.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app_runner, bind_address, PORT).start()
        self.LOGGER(__name__).info("Streaming Web Server running on port %s", PORT)

    async def stop(self, *args) -> None:
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")


if __name__ == "__main__":
    Bot().run()
