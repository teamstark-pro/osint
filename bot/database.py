from motor.motor_asyncio import AsyncIOMotorClient
from bot.config import Config

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(Config.MONGO_URI)
        self.db = self.client['telegram_bot_db']
        self.users = self.db['users']
        self.groups = self.db['groups']

    async def add_user(self, user_id):
        await self.users.update_one({'_id': user_id}, {'$set': {'active': True}}, upsert=True)

    async def add_group(self, chat_id):
        await self.groups.update_one({'_id': chat_id}, {'$set': {'active': True}}, upsert=True)

    async def get_all_users(self):
        return [doc['_id'] async for doc in self.users.find()]

    async def get_all_groups(self):
        return [doc['_id'] async for doc in self.groups.find()]

db = Database()
