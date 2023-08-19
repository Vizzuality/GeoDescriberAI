import os

import motor.motor_asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
MONGO_CONNECTION = os.getenv("MONGO_CONNECTION")

# Connect to MongoDB
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_CONNECTION)
db = client.get_database(os.getenv("MONG0_DATABASE"))
collection = db.get_collection(os.getenv("MONGO_COLLECTION"))
