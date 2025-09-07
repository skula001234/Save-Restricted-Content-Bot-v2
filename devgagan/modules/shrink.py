 
# ---------------------------------------------------
# File Name: shrink.py
# Description: A Pyrogram bot for downloading files from Telegram channels or groups 
#              and uploading them back to Telegram.
# Author: Gagan
# GitHub: https://github.com/devgaganin/
# Telegram: https://t.me/team_spy_pro
# YouTube: https://youtube.com/@dev_gagan
# Created: 2025-01-11
# Last Modified: 2025-01-11
# Version: 2.0.5
# License: MIT License
# ---------------------------------------------------

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
import random
import requests
import string
import aiohttp
from devgagan import app
from devgagan.core.func import *
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB, WEBSITE_URL, AD_API, LOG_GROUP  
 
 
tclient = AsyncIOMotorClient(MONGO_DB)
tdb = tclient["telegram_bot"]
token = tdb["tokens"]
 
 
async def create_ttl_index():
    await token.create_index("expires_at", expireAfterSeconds=0)
 
 
 
Param = {}
 
 
async def generate_random_param(length=8):
    """Generate a random parameter."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
 
 
async def get_shortened_url(deep_link):
    api_url = f"https://{WEBSITE_URL}/api?api={AD_API}&url={deep_link}"
 
     
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            if response.status == 200:
                data = await response.json()   
                if data.get("status") == "success":
                    return data.get("shortenedUrl")
    return None
 
 
async def is_user_verified(user_id):
    """Check if a user has an active session."""
    session = await token.find_one({"user_id": user_id})
    return session is not None
 
 
@app.on_message(filters.command("start"))
async def token_handler(client, message):
    """Handle the /token command."""
    join = await subscribe(client, message)
    if join == 1:
        return
    chat_id = "save_restricted_content_bots"
    msg = await app.get_messages(chat_id, 796)
    user_id = message.chat.id
    if len(message.command) <= 1:
        image_url = "https://i.postimg.cc/v8q8kGyz/startimg-1.jpg"
        join_button = InlineKeyboardButton("𝐉𝐨𝐢𝐧 𝐌𝐚𝐢𝐧 𝐂𝐡𝐚𝐧𝐧𝐞𝐥", url="https://t.me/team_spy_pro")
        premium = InlineKeyboardButton("help", callback_data="helper")   
        keyboard = InlineKeyboardMarkup([
            [join_button],   
            [premium]    
        ])
         
        await message.reply_photo(
            msg.photo.file_id,
            caption=(
                "Hi 👋 Welcome, Wanna intro...?\n\n"
                "➭ Sᴀᴠᴇ ᴘᴏꜱᴛꜱ ғʀᴏᴍ ᴄʜᴀɴɴᴇʟꜱ ᴀɴᴅ ɢʀᴏᴜᴘꜱ ᴡʜᴇʀᴇ ғᴏʀᴡᴀʀᴅɪɴɢ ɪꜱ ʀᴇꜱᴛʀɪᴄᴛᴇᴅ\n"
                "➭ Eᴀꜱɪʟʏ ғᴇᴛᴄʜ ᴍᴇꜱꜱᴀɢᴇꜱ ғʀᴏᴍ ᴘᴜʙʟɪᴄ ᴄʜᴀɴɴᴇʟꜱ ʙʏ ꜱᴇɴᴅɪɴɢ ᴛʜᴇɪʀ ᴘᴏꜱᴛ ʟɪɴᴋꜱ\n"
                "➭ Fᴏʀ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀɴɴᴇʟꜱ, ᴜꜱᴇ /login ᴛᴏ ᴀᴄᴄᴇꜱꜱ ᴄᴏɴᴛᴇɴᴛ ꜱᴇᴄᴜʀᴇʟʏ\n\n"
                "📑 Fᴏʀ ᴍᴏʀᴇ ɪɴꜱᴛʀᴜᴄᴛɪᴏɴꜱ ꜱᴇɴᴅ /help"
            ),
            reply_markup=keyboard
        )
        return  
 
    param = message.command[1] if len(message.command) > 1 else None
    freecheck = await chk_user(message, user_id)
    if freecheck != 1:
        await message.reply("You are a premium user no need of token 😉")
        return
 
     
    if param:
        if user_id in Param and Param[user_id] == param:
             
            await token.insert_one({
                "user_id": user_id,
                "param": param,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=3),
            })
            del Param[user_id]   
            await message.reply("✅ You have been verified successfully! Enjoy your session for next 3 hours.")
            return
        else:
            await message.reply("❌ Invalid or expired verification link. Please generate a new token.")
            return
 
@app.on_message(filters.command("token"))
async def smart_handler(client, message):
    user_id = message.chat.id
     
    freecheck = await chk_user(message, user_id)
    if freecheck != 1:
        await message.reply("You are a premium user no need of token 😉")
        return
    if await is_user_verified(user_id):
        await message.reply("✅ Your free session is already active enjoy!")
    else:
         
        param = await generate_random_param()
        Param[user_id] = param   
 
         
        deep_link = f"https://t.me/{client.me.username}?start={param}"
 
         
        shortened_url = await get_shortened_url(deep_link)
        if not shortened_url:
            await message.reply("❌ Failed to generate the token link. Please try again.")
            return
 
         
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Verify the token now...", url=shortened_url)]]
        )
        await message.reply("Click the button below to verify your free access token: \n\n> What will you get ? \n1. No time bound upto 3 hours \n2. Batch command limit will be FreeLimit + 20 \n3. All functions unlocked", reply_markup=button)


@app.on_callback_query(filters.regex("helper"))
async def see_plan(client, callback_query):
    plan_text = (
        "> 📝 Bot Commands Overview:"
        "> 1. /add userID - Add user to premium (Owner only)\n2. /rem userID - Remove user from premium (Owner only)\n3. /transfer userID - Transfer premium to another user\n4. /login - Log into the bot for private channel access\n5. /batch - Bulk extraction for posts (After login)\n6. /logout - Logout from the bot\n7. /stats - Get bot statistics\n8. /plan - Check premium plans\n9. /speedtest - Test the server speed\n10. /terms - Terms and conditions\n11. /cancel - Cancel ongoing batch process\n12. /myplan - Get details about your plans\n13. /session - Generate Pyrogram V2 session\n14. /settings - Personalize bot settings"
        "Powered by Team SPY"
    )

    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🏷️ back ", callback_data="home")],
            [InlineKeyboardButton("💬 Contact Now", url="https://t.me/")],
        ]
    )
    await callback_query.message.edit_text(plan_text, reply_markup=buttons)


@app.on_callback_query(filters.regex("home"))
async def see_plan(client, callback_query):
    plan_text = (
        "Hi 👋 Welcome, Wanna intro...?\n\n"
                "➭ Sᴀᴠᴇ ᴘᴏꜱᴛꜱ ғʀᴏᴍ ᴄʜᴀɴɴᴇʟꜱ ᴀɴᴅ ɢʀᴏᴜᴘꜱ ᴡʜᴇʀᴇ ғᴏʀᴡᴀʀᴅɪɴɢ ɪꜱ ʀᴇꜱᴛʀɪᴄᴛᴇᴅ\n"
                "➭ Eᴀꜱɪʟʏ ғᴇᴛᴄʜ ᴍᴇꜱꜱᴀɢᴇꜱ ғʀᴏᴍ ᴘᴜʙʟɪᴄ ᴄʜᴀɴɴᴇʟꜱ ʙʏ ꜱᴇɴᴅɪɴɢ ᴛʜᴇɪʀ ᴘᴏꜱᴛ ʟɪɴᴋꜱ\n"
                "➭ Fᴏʀ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀɴɴᴇʟꜱ, ᴜꜱᴇ /login ᴛᴏ ᴀᴄᴄᴇꜱꜱ ᴄᴏɴᴛᴇɴᴛ ꜱᴇᴄᴜʀᴇʟʏ\n\n"
                "📑 Fᴏʀ ᴍᴏʀᴇ ɪɴꜱᴛʀᴜᴄᴛɪᴏɴꜱ ꜱᴇɴᴅ /help"
    )

    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🏷️ back ", callback_data="home")],
            [InlineKeyboardButton("💬 Contact Now", url="https://t.me/")],
        ]
    )
    await callback_query.message.edit_text(plan_text, reply_markup=buttons)
