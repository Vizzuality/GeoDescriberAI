import motor

from database.db_config import client, db_name, qa_collection_name
from database.repository import MongoRepository


def get_qa_repository():
    return QuestionAnswerRepository(client, db_name, qa_collection_name)


class QuestionAnswerRepository(MongoRepository):
    def __init__(self, client: motor.motor_asyncio.AsyncIOMotorClient, database_name: str, collection_name: str):
        super().__init__(client)
        self.db = client.get_database(database_name)
        self.collection = self.db.get_collection(collection_name)

    async def save_question_answer(self, question: str, answer: str, context: str = None, is_correct: bool = None,
                                   user_id: str = None):
        document = {
            "question": question,
            "answer": answer,
            "context": context,
            "is_correct": is_correct,
            "user_id": user_id
        }
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)
