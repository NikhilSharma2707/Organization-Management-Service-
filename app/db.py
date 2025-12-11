from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

client = AsyncIOMotorClient(settings.MONGO_URI)
master_db = client[settings.MASTER_DB]
# dynamic collections will be created in master_db or other db(s)
