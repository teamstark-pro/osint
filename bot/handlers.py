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
    """
    Checks if the user has joined all required channels.
    Returns True if passed, False if failed (and sends join buttons).
    """
    user_id = update.effective_user.id
    
    # Owner always bypasses
    if user_id == Config.OWNER_ID:
        return True

    # If no channels configured, pass
    if not Config.FORCE_SUB_CHANNELS:
        return True

    missing_channels = []
    
    for channel in Config.FORCE_SUB_CHANNELS:
        try:
            # Check member status
            # chat_id can be integer ID or @username
            member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
            
            # Statuses that mean the user is NOT in the channel
            if member.status in ["left", "kicked"]:
                # Generate Link
                if str(channel).startswith("@"):
                    link = f"https://t.me/{str(channel).replace('@', '')}"
                else:
                    # Try to get invite link if it's a private channel ID
                    try:
                        chat_info = await context.bot.get_chat(channel)
                        link = chat_info.invite_link or chat_info.username
                    except Exception:
                        link = "https://t.me/" # Fallback
                
                missing_channels.append(link)

        except BadRequest as e:
            logger.error(f"FSUB Error for {channel}: {e}. Make sure Bot is Admin in that channel.")
            continue
        except Exception as e:
            logger.error(f"Unexpected FSUB Error: {e}")
            continue

    if missing_channels:
        # Create Buttons for missing channels
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
    Logs users and groups to DB.
    """
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type

    # 1. Private Chat (DM) -> Always allow & Log User
    if chat_type == ChatType.PRIVATE:
        await db.add_user(user_id)
        return True

    # 2. Official Group or Owner -> Allow & Log Group
    if chat_id in Config.OFFICIAL_GROUPS or user_id == Config.OWNER_ID:
        await db.add_group(chat_id)
        return True

    # 3. Unauthorized Group -> Warn & Leave
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
    """Runs both Chat Auth and Force Sub checks."""
    if not await check_chat_auth(update):
        return False
    if not await check_fsub(update, context):
        return False
    return True

# --- Command Handlers ---

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        # If response is a file (too long)
        try:
            await update.message.reply_document(
                document=file_resp, 
                caption=text_resp[:1000], # Caption limit
                parse_mode=ParseMode.MARKDOWN
            )
            await msg.delete()
        except Exception as e:
            await msg.edit_text(f"❌ Error sending file: {e}")
    else:
        # Normal text response
        await msg.edit_text(text_resp, parse_mode=ParseMode.MARKDOWN)

async def cmd_pic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await validate_request(update, context): return
    
    args = context.args
    if not args:
        return await update.message.reply_text("Usage: `/pic <number>`", parse_mode=ParseMode.MARKDOWN)
    
    msg = await update.message.reply_text("🔄 Fetching Pic info...")
    response = await api_handlers.handle_pic(args[0])
    
    # NO Parse Mode here (Raw text) as requested
    await msg.edit_text(response)

async def cmd_vnum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await validate_request(update, context): return
    
    args = context.args
    if not args:
        return await update.message.reply_text("Usage: `/vnum <vehicle_no>`", parse_mode=ParseMode.MARKDOWN)
    
    msg = await update.message.reply_text("🔄 Fetching Vehicle info...")
    response = await api_handlers.handle_vnum(args[0])
    
    # Standard text response
    await msg.edit_text(response)

# --- Broadcast (Owner Only) ---
async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Security check: Only Owner
    if update.effective_user.id != Config.OWNER_ID:
        return

    reply = update.message.reply_to_message
    if not reply:
        await update.message.reply_text("⚠️ Reply to a message to broadcast it.")
        return

    # Fetch targets
    users = await db.get_all_users()
    groups = await db.get_all_groups()
    all_targets = set(users + groups) # Use set to avoid duplicates
    
    total = len(all_targets)
    sent = 0
    blocked = 0
    
    status_msg = await update.message.reply_text(f"🚀 Broadcasting to {total} chats...")

    for chat_id in all_targets:
        try:
            await reply.copy(chat_id=chat_id)
            sent += 1
        except Forbidden:
            # User blocked bot
            blocked += 1
            # Optional: Remove user from DB here if desired
        except Exception as e:
            logger.error(f"Broadcast fail for {chat_id}: {e}")
            
    await status_msg.edit_text(
        f"✅ **Broadcast Complete**\n\n"
        f"📩 Sent: {sent}\n"
        f"🚫 Blocked/Failed: {blocked}\n"
        f"📊 Total: {total}"
    )
