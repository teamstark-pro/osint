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
    
    # Owner always bypasses
    if user_id == Config.OWNER_ID:
        return True

    if not Config.FORCE_SUB_CHANNELS:
        return True

    missing_channels = []
    
    for channel in Config.FORCE_SUB_CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ["left", "kicked"]:
                if str(channel).startswith("@"):
                    link = f"https://t.me/{str(channel).replace('@', '')}"
                else:
                    try:
                        chat_info = await context.bot.get_chat(channel)
                        link = chat_info.invite_link or chat_info.username
                    except Exception:
                        link = "https://t.me/"
                missing_channels.append(link)

        except BadRequest as e:
            logger.error(f"FSUB Error for {channel}: {e}")
            continue
        except Exception as e:
            logger.error(f"Unexpected FSUB Error: {e}")
            continue

    if missing_channels:
        keyboard = []
        for i, link in enumerate(missing_channels):
            btn_text = f"Join Channel {i+1}" if len(missing_channels) > 1 else "Join Channel"
            keyboard.append([InlineKeyboardButton(btn_text, url=link)])
        
        await update.message.reply_text(
            "⚠️ **Access Denied!**\n\n"
            "You must join our update channels to use this bot.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
        return False
        
    return True

# --- Middleware: Check Group & Authorization ---
async def check_chat_auth(update: Update) -> bool:
    """
    Verifies if the bot is allowed to run in this chat.
    BLOCKS Private DMs for normal users.
    """
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type

    # 1. ALLOW Owner (Anywhere: DM or Groups)
    if user_id == Config.OWNER_ID:
        # Still log them if it's a DM, or log the group if it's a group
        if chat_type == ChatType.PRIVATE:
            await db.add_user(user_id)
        else:
            await db.add_group(chat_id)
        return True

    # 2. BLOCK Private DMs for everyone else
    if chat_type == ChatType.PRIVATE:
        await update.message.reply_text(
            f"⚠️ **I am not active in DMs!**\n\nUse me in the official group: {Config.INVITE_LINK}",
            disable_web_page_preview=True
        )
        return False

    # 3. ALLOW Official Groups
    if chat_id in Config.OFFICIAL_GROUPS:
        await db.add_group(chat_id)
        await db.add_user(user_id) # Log user even in group
        return True

    # 4. BLOCK Unauthorized Groups
    try:
        await update.message.reply_text(
            f"⚠️ **I am not active here!**\n\nUse me in the official group: {Config.INVITE_LINK}",
            disable_web_page_preview=True
        )
        await update.message.chat.leave()
    except Exception as e:
        logger.warning(f"Could not leave chat {chat_id}: {e}")
        
    return False

# --- Combined Validator ---
async def validate_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if not await check_chat_auth(update):
        return False
    if not await check_fsub(update, context):
        return False
    return True

# --- Command Handlers ---

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Only reply to start if it passes the check (Owner or Official Group)
    if not await validate_request(update, context): return
    await update.message.reply_text(
        f"👋 Welcome! I am online.\n\nUse /tg, /num, /pic, or /vnum to search.{Config.FOOTER}"
    )

async def cmd_tg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await validate_request(update, context): return
    args = context.args
    if not args:
        return await update.message.reply_text("Usage: `/tg <uid>`", parse_mode=ParseMode.MARKDOWN)
    
    msg = await update.message.reply_text("🔄 Fetching TG info...")
    response = await api_handlers.handle_tg(args[0])
    await msg.edit_text(response, parse_mode=ParseMode.MARKDOWN)

async def cmd_num(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await validate_request(update, context): return
    args = context.args
    if not args:
        return await update.message.reply_text("Usage: `/num <number>`", parse_mode=ParseMode.MARKDOWN)
    
    msg = await update.message.reply_text("🔄 Fetching Number details...")
    text_resp, file_resp = await api_handlers.handle_num(args[0])
    
    if file_resp:
        try:
            await update.message.reply_document(
                document=file_resp, 
                caption=text_resp[:1000], 
                parse_mode=ParseMode.MARKDOWN
            )
            await msg.delete()
        except Exception as e:
            await msg.edit_text(f"❌ Error sending file: {e}")
    else:
        await msg.edit_text(text_resp, parse_mode=ParseMode.MARKDOWN)

async def cmd_pic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await validate_request(update, context): return
    args = context.args
    if not args:
        return await update.message.reply_text("Usage: `/pic <number>`", parse_mode=ParseMode.MARKDOWN)
    
    msg = await update.message.reply_text("🔄 Fetching Pic info...")
    response = await api_handlers.handle_pic(args[0])
    await msg.edit_text(response)

async def cmd_vnum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await validate_request(update, context): return
    args = context.args
    if not args:
        return await update.message.reply_text("Usage: `/vnum <vehicle_no>`", parse_mode=ParseMode.MARKDOWN)
    
    msg = await update.message.reply_text("🔄 Fetching Vehicle info...")
    response = await api_handlers.handle_vnum(args[0])
    await msg.edit_text(response)

async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.OWNER_ID: return
    reply = update.message.reply_to_message
    if not reply:
        await update.message.reply_text("⚠️ Reply to a message to broadcast it.")
        return

    users = await db.get_all_users()
    groups = await db.get_all_groups()
    all_targets = set(users + groups)
    
    total = len(all_targets)
    sent = 0
    blocked = 0
    
    status_msg = await update.message.reply_text(f"🚀 Broadcasting to {total} chats...")

    for chat_id in all_targets:
        try:
            await reply.copy(chat_id=chat_id)
            sent += 1
        except Forbidden:
            blocked += 1
        except Exception as e:
            logger.error(f"Broadcast fail for {chat_id}: {e}")
            
    await status_msg.edit_text(
        f"✅ **Broadcast Complete**\n\n"
        f"📩 Sent: {sent}\n"
        f"🚫 Blocked/Failed: {blocked}\n"
        f"📊 Total: {total}"
    )
