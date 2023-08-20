from database.db_config import db, client, qa_collection
from database.repository import MongoRepository


def get_qa_repository():
    return QuestionAnswerRepository(client, db, qa_collection)


class QuestionAnswerRepository(MongoRepository):
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
