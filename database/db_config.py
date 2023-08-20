import motor.motor_asyncio

from config.config import get_config

# Connect to MongoDB
client = motor.motor_asyncio.AsyncIOMotorClient(get_config().mongo_connection)
db = client.get_database(get_config().db_name)
db_name = get_config().db_name
qa_collection_name = get_config().qa_collection
users_collection_name = get_config().users_collection
