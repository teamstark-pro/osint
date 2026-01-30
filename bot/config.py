import os

class Config:
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    # Add your MongoDB URI from Atlas
    MONGO_URI = os.getenv("MONGO_URI") 
    # Owner ID (Integer)
    OWNER_ID = int(os.getenv("OWNER_ID", "0"))
    # List of allowed group IDs (separated by space in .env)
    OFFICIAL_GROUPS = set(map(int, os.getenv("OFFICIAL_GROUPS", "").split()))
    INVITE_LINK = os.getenv("INVITE_LINK", "https://t.me/your_group_link")
    
    # Credit Footer
    FOOTER = "\n\n━━━━━━━━━━━━━━━━━━\n🤖 bot by internal_dark_soul.t.me and frappeash.t.me"
