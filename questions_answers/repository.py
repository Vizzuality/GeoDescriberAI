from database.db_config import collection, db, client


def get_repository():
    return MongoRepository(client, db, collection)


class MongoRepository:
    def __init__(self, mongo_client, mongo_db, mongo_collection):
        self.client = mongo_client
        self.db = mongo_db
        self.collection = mongo_collection

    async def save_question_answer(self, question: str, answer: str, context: str = None, is_correct: bool = None):
        document = {
            "question": question,
            "answer": answer,
            "context": context,
            "is_correct": is_correct
        }
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)

    async def test_connection(self):
        try:
            await self.db.command("serverStatus")
            return True
        except Exception as e:
            print("Error connecting to MongoDB:", e)
            print("Q&A won't be saved to database.")
