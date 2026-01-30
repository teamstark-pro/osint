from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler
from bot.config import Config
from bot import handlers

app = FastAPI()

# Initialize Bot Application
ptb_app = Application.builder().token(Config.TOKEN).build()

# Add Handlers
ptb_app.add_handler(CommandHandler("broadcast", handlers.broadcast))
ptb_app.add_handler(CommandHandler("tg", handlers.cmd_tg))
ptb_app.add_handler(CommandHandler("num", handlers.cmd_num))
ptb_app.add_handler(CommandHandler("pic", handlers.cmd_pic))
ptb_app.add_handler(CommandHandler("vnum", handlers.cmd_vnum))

@app.post("/")
async def process_update(request: Request):
    data = await request.json()
    update = Update.de_json(data, ptb_app.bot)
    await ptb_app.initialize()
    await ptb_app.process_update(update)
    return {"status": "ok"}

@app.get("/")
def health_check():
    return {"status": "Bot is running"}
