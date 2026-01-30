from telegram import Update
from telegram.ext import ContextTypes
from bot.config import Config
from bot.database import db
from bot import api_handlers

# --- Middleware: Check Group ---
async def check_chat(update: Update):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    # Allow if private chat (User) or Official Group or Owner
    if update.effective_chat.type == "private":
        await db.add_user(user_id)
        return True
        
    if chat_id in Config.OFFICIAL_GROUPS or user_id == Config.OWNER_ID:
        await db.add_group(chat_id)
        return True
        
    # If unauthorized group
    await update.message.reply_text(
        f"⚠️ **Core Active Only in Official Groups**\n\nUse me here: {Config.INVITE_LINK}",
        disable_web_page_preview=True
    )
    try:
        await update.message.chat.leave()
    except:
        pass
    return False

# --- Broadcast (Owner Only) ---
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Config.OWNER_ID:
        return

    reply = update.message.reply_to_message
    if not reply:
        await update.message.reply_text("Reply to a message to broadcast.")
        return

    users = await db.get_all_users()
    groups = await db.get_all_groups()
    
    count = 0
    await update.message.reply_text(f"🚀 Started broadcasting to {len(users)} users and {len(groups)} groups...")

    all_targets = users + groups
    for target in all_targets:
        try:
            await reply.forward(chat_id=target)
            count += 1
        except Exception:
            pass # Skip blocked users/kicked groups
            
    await update.message.reply_text(f"✅ Broadcast complete. Sent to {count} chats.")

# --- Command Handlers ---

async def cmd_tg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_chat(update): return
    args = context.args
    if not args: return await update.message.reply_text("Usage: `/tg <uid>`", parse_mode="Markdown")
    
    msg = await update.message.reply_text("🔄 Fetching...")
    response = await api_handlers.handle_tg(args[0])
    await msg.edit_text(response, parse_mode="Markdown")

async def cmd_num(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_chat(update): return
    args = context.args
    if not args: return await update.message.reply_text("Usage: `/num <number>`", parse_mode="Markdown")
    
    msg = await update.message.reply_text("🔄 Fetching details...")
    text_resp, file_resp = await api_handlers.handle_num(args[0])
    
    if file_resp:
        await update.message.reply_document(document=file_resp, caption=text_resp, parse_mode="Markdown")
        await msg.delete()
    else:
        await msg.edit_text(text_resp, parse_mode="Markdown")

async def cmd_pic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_chat(update): return
    args = context.args
    if not args: return await update.message.reply_text("Usage: `/pic <number>`", parse_mode="Markdown")
    
    msg = await update.message.reply_text("🔄 Fetching...")
    response = await api_handlers.handle_pic(args[0])
    # Note: explicitly NOT using parse_mode here as requested (no monospace enforcement)
    await msg.edit_text(response)

async def cmd_vnum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_chat(update): return
    args = context.args
    if not args: return await update.message.reply_text("Usage: `/vnum <vehicle_no>`", parse_mode="Markdown")
    
    msg = await update.message.reply_text("🔄 Fetching...")
    response = await api_handlers.handle_vnum(args[0])
    await msg.edit_text(response)
