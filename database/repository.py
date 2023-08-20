import motor.motor_asyncio

from database.db_config import client


## Generic MongoDB repository to share across multiple repositories

def get_mongo_repository():
    return MongoRepository(client)


class MongoRepository:
    def __init__(self, client: motor.motor_asyncio.AsyncIOMotorClient):
        self.client = client

    async def test_connection(self) -> bool:
        try:
            await self.client.admin.command("ping")
            return True
        except Exception as e:
            print(f"An error occurred while checking the connection: {e}")
            print("The application will continue to run without database support.")
            return False
