import logging
from telegram.ext import ApplicationBuilder, CommandHandler
from bot.config import Config
from bot import handlers

# Setup Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    # 1. Build the Application
    print("🚀 Starting Bot...")
    application = ApplicationBuilder().token(Config.TOKEN).build()

    # 2. Add Handlers (Same as before)
    application.add_handler(CommandHandler("start", handlers.cmd_start))
    application.add_handler(CommandHandler("broadcast", handlers.broadcast_cmd))
    application.add_handler(CommandHandler("tg", handlers.cmd_tg))
    application.add_handler(CommandHandler("num", handlers.cmd_num))
    application.add_handler(CommandHandler("pic", handlers.cmd_pic))
    application.add_handler(CommandHandler("vnum", handlers.cmd_vnum))
    application.add_handler(CommandHandler("aadhar", handlers.cmd_aadhar))
    application.add_handler(CommandHandler("upi", handlers.cmd_upi))

    # 3. Run Forever (Polling)
    print("✅ Bot is polling...")
    application.run_polling()

if __name__ == '__main__':
    main()
