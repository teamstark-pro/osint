import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode, ChatType
from telegram.ext import ContextTypes
from telegram.error import BadRequest, Forbidden

from bot.config import Config
from bot.database import db
from bot import api_handlers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Helper: Check Force Subscribe ---
async def check_fsub(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    if user_id == Config.OWNER_ID: return True
    if not Config.FORCE_SUB_CHANNELS: return True

    missing_channels = []
    for channel in Config.FORCE_SUB_CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ["left", "kicked"]:
                if str(channel).startswith("@"):
                    link = f"[https://t.me/](https://t.me/){str(channel).replace('@', '')}"
                else:
                    try:
                        chat_info = await context.bot.get_chat(channel)
                        link = chat_info.invite_link or chat_info.username
                    except:
                        link = "[https://t.me/](https://t.me/)"
                missing_channels.append(link)
        except BadRequest:
            continue

    if missing_channels:
        keyboard = [[InlineKeyboardButton(f"Join Channel {i+1}", url=link)] for i, link in enumerate(missing_channels)]
        await update.message.reply_text(
            "⚠️ **Access Denied!**\nJoin our channels to use this bot.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
        return False
    return True

# --- Middleware: Check Group ---
async def check_chat_auth(update: Update) -> bool:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type

    if user_id == Config.OWNER_ID:
        if chat_type == ChatType.PRIVATE: await db.add_user(user_id)
        else: await db.add_group(chat_id)
        return True

    if chat_type == ChatType.PRIVATE:
        await update.message.reply_text(f"⚠️ **I am not active in DMs!**\nUse me here: {Config.INVITE_LINK}")
        return False

    if chat_id in Config.OFFICIAL_GROUPS:
        await db.add_group(chat_id)
        await db.add_user(user_id)
        return True

    try:
        await update.message.reply_text(f"⚠️ **Not Active Here!**\nUse me here: {Config.INVITE_LINK}")
        await update.message.chat.leave()
    except:
        pass
    return False

async def validate_request(update, context):
    if not await check_chat_auth(update): return False
    if not await check_fsub(update, context): return False
    return True

# --- Generic Sender (Text or File) ---
async def send_response(update, response_tuple):
    text_resp, file_resp = response_tuple
    msg = update.message
    
    try:
        if file_resp:
            # Send as File if it exists
            await msg.reply_document(
                document=file_resp, 
                caption=text_resp, # Warning caption
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            # Send as Text
            await msg.reply_text(text_resp, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await msg.reply_text(f"❌ Error: {e}")

# --- Commands ---

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await validate_request(update, context): return
    await update.message.reply_text(f"👋 Online.\n/tg, /num, /pic, /vnum, /aadhar, /upi")

async def cmd_tg(update, context):
    if not await validate_request(update, context): return
    if not context.args: return await update.message.reply_text("Usage: `/tg <id>`", parse_mode="Markdown")
    m = await update.message.reply_text("🔄 Fetching...")
    await m.delete()
    await send_response(update, await api_handlers.handle_tg(context.args[0]))

async def cmd_num(update, context):
    if not await validate_request(update, context): return
    if not context.args: return await update.message.reply_text("Usage: `/num <number>`", parse_mode="Markdown")
    m = await update.message.reply_text("🔄 Fetching...")
    await m.delete()
    await send_response(update, await api_handlers.handle_num(context.args[0]))

async def cmd_pic(update, context):
    if not await validate_request(update, context): return
    if not context.args: return await update.message.reply_text("Usage: `/pic <number>`", parse_mode="Markdown")
    m = await update.message.reply_text("🔄 Fetching...")
    await m.delete()
    await send_response(update, await api_handlers.handle_pic(context.args[0]))

async def cmd_vnum(update, context):
    if not await validate_request(update, context): return
    if not context.args: return await update.message.reply_text("Usage: `/vnum <number>`", parse_mode="Markdown")
    m = await update.message.reply_text("🔄 Fetching...")
    await m.delete()
    await send_response(update, await api_handlers.handle_vnum(context.args[0]))

async def cmd_aadhar(update, context):
    if not await validate_request(update, context): return
    if not context.args: return await update.message.reply_text("Usage: `/aadhar <uid>`", parse_mode="Markdown")
    m = await update.message.reply_text("🔄 Fetching...")
    await m.delete()
    await send_response(update, await api_handlers.handle_aadhar(context.args[0]))

async def cmd_upi(update, context):
    if not await validate_request(update, context): return
    if not context.args: return await update.message.reply_text("Usage: `/upi <id>`", parse_mode="Markdown")
    m = await update.message.reply_text("🔄 Fetching...")
    await m.delete()
    await send_response(update, await api_handlers.handle_upi(context.args[0]))

async def broadcast_cmd(update, context):
    if update.effective_user.id != Config.OWNER_ID: return
    reply = update.message.reply_to_message
    if not reply: return await update.message.reply_text("Reply to msg.")
    
    users = await db.get_all_users()
    groups = await db.get_all_groups()
    targets = set(users + groups)
    
    sent = 0
    status = await update.message.reply_text(f"🚀 Broadcasting to {len(targets)}...")
    for t in targets:
        try:
            await reply.copy(chat_id=t)
            sent += 1
        except: pass
    await status.edit_text(f"✅ Sent to {sent} chats.")
