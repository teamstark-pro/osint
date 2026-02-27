import os

class Config:
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    MONGO_URI = os.getenv("MONGO_URI") 
    OWNER_ID = int(os.getenv("OWNER_ID", "0"))
    
    # Force Subscribe Channels (Usernames or IDs separated by space)
    # Example in .env: FORCE_SUB_CHANNELS="@mychannel1 @mychannel2"
    FORCE_SUB_CHANNELS = os.getenv("FORCE_SUB_CHANNELS", "").split()

    FOOTER = "\n\n━━━━━━━━━━━━━━━━━━\n🤖 bot by internaldarksoul.t.me"
