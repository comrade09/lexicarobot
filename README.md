# Physicsaholics File-Sharing Bot

A Telegram file-sharing bot (Pyrogram-based, forked from
[CodeXBotz/File-Sharing-Bot](https://github.com/CodeXBotz/File-Sharing-Bot)): store posts
in a private database channel and hand out shareable links that deliver them back to any
user who opens the link.

Requires **Python 3.12+** (see `runtime.txt` / `Dockerfile`).

## Deploy on Koyeb

[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy?type=git&repository=github.com/CodeXBotz/File-Sharing-Bot&branch=koyeb&name=filesharingbot)

## Local setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in the values below
python3 main.py
```

## Required environment variables

| Variable | Description |
|---|---|
| `TG_BOT_TOKEN` | Bot token from [@BotFather](https://t.me/BotFather) |
| `APP_ID` | From [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | From [my.telegram.org](https://my.telegram.org) |
| `OWNER_ID` | Your numeric Telegram user ID |
| `DATABASE_URL` | MongoDB connection string |
| `CHANNEL_ID` | ID of your private database channel (add the bot as admin there) |

## Optional environment variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_NAME` | `filesharexbot` | MongoDB database name |
| `FORCE_SUB_CHANNEL` | `0` | Channel/group ID users must join before using the bot; `0` disables it |
| `START_MESSAGE` / `FORCE_SUB_MESSAGE` | see `config.py` | HTML-formatted bot copy |
| `ADMINS` | — | Space-separated admin user IDs |
| `CUSTOM_CAPTION` | — | Caption template applied to shared documents |
| `PROTECT_CONTENT` | `False` | Prevent forwarding/saving of shared content |
| `DISABLE_CHANNEL_BUTTON` | `False` | Disable the share button on the DB channel copy |
| `TG_BOT_WORKERS` | `4` | Pyrogram worker thread count |
| `GEMINI` | — | API key for the AI-reply feature in `plugins/custom_filters.py` |
| `AUDIT_LOG_CHAT_ID` | — | A chat ID **you control** to receive a log of stray private messages/media. Off by default — see `MODERNIZATION_NOTES.md` for why this replaced a previously hardcoded value. |

Never commit a real `.env` file — see `.gitignore`.

## Project status

This codebase is partway through a modernization pass (Python 3.8 → 3.12+ syntax, type
hints, a couple of real bugs fixed along the way). See `MODERNIZATION_NOTES.md` for exactly
what's changed, what hasn't been touched yet, and two things worth reading before you deploy:
a message-formatting bug that silently broke a feature, and a privacy issue in the original
logging code.
