import motor

from database.db_config import client, db_name, users_collection_name
from database.repository import MongoRepository
from users.model import User


def get_user_repository():
    return UserRepository(client, db_name, users_collection_name)


class UserRepository(MongoRepository):
    def __init__(self, client: motor.motor_asyncio.AsyncIOMotorClient, database_name: str, collection_name: str):
        super().__init__(client)
        self.db = client.get_database(database_name)
        self.collection = self.db.get_collection(collection_name)

    def create_user(self, user: User):
        return self.collection.insert_one(user.dict())

    def get_user_by_credentials(self, username: str, password: str):
        return self.collection.find_one({"username": username, "password": password})

    def find_user_by_username(self, username: str):
        return self.collection.find_one({"username": username})

    def update_user(self, username: str, user: User):
        return self.collection.update_one({"username": username}, {"$set": user.dict()})

    def delete_user(self, username: str):
        return self.collection.delete_one({"username": username})
