from pydantic import BaseModel


class QuestionAnswerSchema(BaseModel):
    question: str
    answer: str
    context: str = None
    is_correct: bool = None
    username: str = None

    class Config:
        schema_extra = {
            "example": {
                "question": "What is the capital of France?",
                "answer": "The capital of France is Paris, a major European city...",
                "context": "TBD",
                "is_correct": True
            }
        }
