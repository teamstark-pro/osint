import logging
import os
from threading import Thread
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler
from bot.config import Config
from bot import handlers

# 1. Setup Flask for Render Health Checks
server = Flask('')

@server.route('/')
def home():
    return "Bot is running!"

def run_server():
    # Render provides a PORT environment variable. If not found, use 10000.
    port = int(os.environ.get("PORT", 10000))
    server.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_server)
    t.start()

# 2. Setup Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    # Start the web server in the background
    print("🌐 Starting health check server...")
    keep_alive()

    # 1. Build the Application
    print("🚀 Starting Bot...")
    application = ApplicationBuilder().token(Config.TOKEN).build()

    # 2. Add Handlers
    application.add_handler(CommandHandler("start", handlers.cmd_start))
    application.add_handler(CommandHandler("broadcast", handlers.broadcast_cmd))
    application.add_handler(CommandHandler("tg", handlers.cmd_tg))
    application.add_handler(CommandHandler("num", handlers.cmd_num))
    application.add_handler(CommandHandler("pic", handlers.cmd_pic))
    application.add_handler(CommandHandler("vnum", handlers.cmd_vnum))
    application.add_handler(CommandHandler("aadhar", handlers.cmd_aadhar))
    application.add_handler(CommandHandler("upi", handlers.cmd_upi))
    application.add_handler(CommandHandler("stats", handlers.cmd_stats))

    # 3. Run Forever (Polling)
    print("✅ Bot is polling...")
    application.run_polling()

if __name__ == '__main__':
    main()
